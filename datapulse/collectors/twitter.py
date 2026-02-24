"""Twitter/X collector with FxTwitter primary and Nitter fallback."""

from __future__ import annotations

import json
import logging
import os
import random
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

from datapulse.core.models import SourceType, MediaType
from datapulse.core.utils import generate_excerpt, clean_text
from .base import BaseCollector, ParseResult

logger = logging.getLogger("datapulse.parsers.twitter")


_DEFAULT_NITTER = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
    "https://nitter.1d4.us",
    "https://nitter.kavin.rocks",
]
NITTER_INSTANCES = (
    os.getenv("NITTER_INSTANCES").split(",") if os.getenv("NITTER_INSTANCES") else _DEFAULT_NITTER
)


class TwitterCollector(BaseCollector):
    name = "twitter"
    source_type = SourceType.TWITTER
    reliability = 0.92

    max_nitter_retries = 3
    max_nitter_response_bytes = 3_000_000
    _nitter_allowed_content_types = ("text/html", "application/xhtml+xml")
    _profile_reserved_paths = {"home", "explore", "search", "messages", "notifications", "settings", "i"}

    def can_handle(self, url: str) -> bool:
        parsed = urlparse(url)
        return (parsed.hostname or "").replace("www.", "") in {"x.com", "twitter.com", "mobile.twitter.com", "mobile.x.com"}

    def parse(self, url: str) -> ParseResult:
        tweet_info = self._extract_tweet_info(url)
        if tweet_info:
            username, tweet_id = tweet_info
            result = self._parse_fxtwitter(url, username, tweet_id)
            if result.success:
                return result

            logger.warning("FxTwitter failed for %s, fallback to nitter: %s", url, result.error)
            path = f"{username}/status/{tweet_id}"
            nitter_result = self._parse_nitter_fallback(url, path)
            if nitter_result.success:
                return nitter_result

            return ParseResult.failure(
                url,
                f"FxTwitter error: {result.error}; Nitter error: {nitter_result.error}",
            )

        # profile URL
        profile = self._extract_profile_username(url)
        if profile:
            result = self._parse_profile(url, profile)
            return result

        return ParseResult.failure(
            url,
            "Twitter/X URL format not recognized. Expected status URL or public profile.",
        )

    def _parse_fxtwitter(self, original_url: str, username: str, tweet_id: str) -> ParseResult:
        api_base = os.getenv("FXTWITTER_API_URL", "https://api.fxtwitter.com").rstrip("/")
        api_url = f"{api_base}/{username}/status/{tweet_id}"

        last_error = ""
        for _ in range(2):
            try:
                req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode())
                if data.get("code") != 200:
                    return ParseResult.failure(original_url, f"FxTwitter code {data.get('code')}: {data.get('message', 'unknown')}")

                tweet = data.get("tweet") or {}
                screen_name = data.get("user", {}).get("screen_name", username)
                author = data.get("user", {}).get("name", username)
                created_at = tweet.get("created_at", "")
                stats = tweet.get("stats") or {}

                likes = stats.get("likes", 0)
                retweets = stats.get("retweets", 0)
                views = stats.get("views", 0)
                quotes = []

                if tweet.get("is_article"):
                    blocks = tweet.get("article", {}).get("content", {}).get("blocks", [])
                    article_title = tweet.get("article", {}).get("title", "")
                    title = f"📝 {article_title}" if article_title else f"X Article by @{screen_name}"
                    body = "\n\n".join(b.get("text", "") for b in blocks)
                else:
                    title = f"Tweet by @{screen_name}"
                    if created_at:
                        title += f" ({created_at})"
                    body = tweet.get("text", "")

                if tweet.get("note_tweet"):
                    body += "\n\n[Note Tweet]"
                    quotes.append("note")

                quote = tweet.get("quote")
                if quote:
                    quotes.append("quote")
                    body += f"\n\n[Quoted Tweet] {quote.get('text', '')}"

                media = tweet.get("media", {})
                media_items = media.get("all", []) or []
                if media_items:
                    body += "\n\n## Media\n"
                    for index, item in enumerate(media_items, 1):
                        media_type = item.get("type", "unknown")
                        media_url = item.get("url", "")
                        if media_type == "photo":
                            body += f"{index}. {media_url}\n"
                        elif media_url:
                            body += f"{index}. {media_type}: {media_url}\n"

                content = clean_text(f"{body}  \n\n👍 {likes}  🔁 {retweets}  👁️ {views}")
                excerpt = generate_excerpt(content)

                return ParseResult(
                    url=original_url,
                    title=title[:180],
                    content=content,
                    author=f"@{screen_name}",
                    excerpt=excerpt,
                    tags=["twitter", "x"],
                    source_type=self.source_type,
                    media_type=(MediaType.IMAGE.value if media_items else MediaType.TEXT.value),
                    confidence_flags=["fxtwitter", "engagement"],
                    extra={
                        "tweet_id": tweet_id,
                        "screen_name": screen_name,
                        "likes": likes,
                        "retweets": retweets,
                        "views": views,
                        "is_article": bool(tweet.get("is_article")),
                        "features": quotes,
                    },
                )
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.reason}"
                return ParseResult.failure(original_url, last_error)
            except urllib.error.URLError as exc:
                last_error = f"Network error: {exc}"
                time.sleep(1)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                break
        return ParseResult.failure(original_url, last_error or "FxTwitter request failed")

    def _parse_profile(self, original_url: str, profile: str) -> ParseResult:
        api_url = f"https://api.fxtwitter.com/{profile}"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
            if data.get("code") != 200:
                return ParseResult.failure(original_url, f"Profile API error: {data.get('message', '')}")

            user = data.get("user") or {}
            name = user.get("name", "")
            description = user.get("description", "")
            followers = user.get("followers", 0)
            following = user.get("following", 0)

            sections = [
                f"# X Profile: @{profile}",
                f"Name: {name}",
                f"Followers: {followers}  Following: {following}",
                "",
                f"Bio: {description}",
                f"Source: {user.get('url', original_url)}",
            ]
            content = "\n".join(sections)
            return ParseResult(
                url=original_url,
                title=f"X Profile: @{profile}",
                content=clean_text(content),
                author=f"@{profile}",
                source_type=self.source_type,
                tags=["twitter", "profile"],
                confidence_flags=["fxtwitter", "profile"],
                extra={"followers": followers, "following": following},
            )
        except Exception as exc:  # noqa: BLE001
            return ParseResult.failure(original_url, str(exc))

    def _parse_nitter_fallback(self, original_url: str, tweet_path: str) -> ParseResult:
        chosen = random.sample(list(NITTER_INSTANCES), min(self.max_nitter_retries, len(NITTER_INSTANCES)))
        last_error = ""
        for instance in chosen:
            url = f"{instance}/{tweet_path}"
            try:
                return self._parse_nitter_page(original_url, url)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
        return ParseResult.failure(original_url, last_error or "Nitter unavailable")

    def _parse_nitter_page(self, original_url: str, nitter_url: str) -> ParseResult:
        with requests.get(
            nitter_url,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
            timeout=20,
            stream=True,
        ) as resp:
            resp.raise_for_status()
            safe, reason = __import__("datapulse.core.utils", fromlist=["validate_external_url"]).validate_external_url(resp.url)
            if not safe:
                raise ValueError(f"Blocked redirect target: {reason}")

            content_type = (resp.headers.get("Content-Type") or "").lower()
            if content_type and not any(ct in content_type for ct in self._nitter_allowed_content_types):
                raise ValueError(f"Unsupported content type: {content_type}")

            body = bytearray()
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                body.extend(chunk)
                if len(body) > self.max_nitter_response_bytes:
                    raise ValueError("Nitter payload too large")

            html = body.decode(resp.encoding or resp.apparent_encoding or "utf-8", errors="replace")

        soup = BeautifulSoup(html, "lxml")
        tweet_div = soup.find("div", class_="tweet-content") or soup.find("div", class_="main-tweet")
        if not tweet_div:
            return ParseResult.failure(original_url, "Nitter parse: tweet body missing")

        text = clean_text(tweet_div.get_text("\n", strip=True))
        if not text:
            return ParseResult.failure(original_url, "Nitter parse: empty text")

        author_tag = soup.find("a", class_="fullname") or soup.find("span", class_="username")
        author = author_tag.get_text(strip=True) if author_tag else ""
        return ParseResult(
            url=original_url,
            title=f"Tweet by {author}" if author else "Tweet",
            content=text,
            author=author,
            excerpt=generate_excerpt(text),
            source_type=self.source_type,
            tags=["twitter", "nitter"],
            confidence_flags=["nitter-fallback"],
            extra={"nitter_url": nitter_url},
        )

    @staticmethod
    def _extract_tweet_info(url: str) -> tuple[str, str] | None:
        match = re.search(r"(?:x|twitter)\.com/([a-zA-Z0-9_]{1,15})/status/(\d+)", url)
        if not match:
            return None
        return match.group(1), match.group(2)

    def _extract_profile_username(self, url: str) -> str | None:
        parsed = urlparse(url)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) != 1:
            return None
        username = parts[0]
        if username in self._profile_reserved_paths:
            return None
        return username if re.fullmatch(r"[a-zA-Z0-9_]{1,15}", username) else None
