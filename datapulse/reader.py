"""Main DataPulse reader API."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, cast

from datapulse.collectors.trending import TrendingCollector, build_trending_url
from datapulse.core.confidence import compute_confidence
from datapulse.core.jina_client import JinaSearchOptions
from datapulse.core.models import DataPulseItem, SourceType
from datapulse.core.router import ParsePipeline
from datapulse.core.scoring import rank_items
from datapulse.core.search_gateway import SearchGateway, SearchHit
from datapulse.core.source_catalog import SourceCatalog
from datapulse.core.storage import UnifiedInbox, output_record_md, save_markdown
from datapulse.core.utils import content_fingerprint, inbox_path_from_env, normalize_language

logger = logging.getLogger("datapulse.reader")

PLATFORM_SEARCH_SITES: dict[str, list[str]] = {
    "xhs": ["xiaohongshu.com", "xhslink.com"],
    "twitter": ["x.com", "twitter.com"],
    "reddit": ["reddit.com"],
    "hackernews": ["news.ycombinator.com"],
    "arxiv": ["arxiv.org"],
    "bilibili": ["bilibili.com"],
}


class DataPulseReader:
    """End-to-end URL reader used by CLI/MCP/Skill/Agent."""

    def __init__(self, inbox_path: str | None = None):
        self.router = ParsePipeline()
        self.inbox = UnifiedInbox(inbox_path or inbox_path_from_env())
        self.catalog = SourceCatalog()
        self._search_gateway = SearchGateway()
        self._jina_client = self._search_gateway._jina_client

    def _run_jina_search(
        self,
        query: str,
        *,
        sites: list[str] | None,
        limit: int = 5,
    ) -> tuple[list[SearchHit], dict[str, Any]]:
        """Run Jina search through the reader's injected client for testable behavior."""
        opts = JinaSearchOptions(sites=sites or [], limit=max(1, int(limit)))
        raw_hits = self._jina_client.search(query, options=opts)

        hits: list[SearchHit] = []
        for r in raw_hits:
            url = (r.url or "").strip()
            if not url:
                continue
            snippet = str(r.description or r.content or "").strip()
            hit = SearchHit(
                title=str(r.title or "").strip()[:300] or "Untitled",
                url=self._search_gateway._sanitize_url(url),
                snippet=snippet,
                provider="jina",
                source="jina",
                score=0.45,
                raw={"title": r.title, "description": r.description, "content": r.content},
                extra={"sources": ["jina"]},
            )
            hits.append(hit)

        search_audit = {
            "query": query,
            "mode": "single",
            "requested_provider": "jina",
            "provider_chain": ["jina"],
            "attempts": [
                {
                    "provider": "jina",
                    "status": "ok",
                    "count": len(hits),
                    "latency_ms": 0.0,
                    "retry_count": 0,
                    "attempts": 0,
                    "circuit_state_before": None,
                    "circuit_state_after": None,
                }
            ],
            "providers_selected": 1,
            "providers_with_hit": 1 if hits else 0,
            "source_count": 1 if hits else 0,
            "provider_count": 1,
            "sampled_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }
        return hits, search_audit

    async def read(self, url: str, *, min_confidence: float = 0.0) -> DataPulseItem:
        return await asyncio.to_thread(self._read_sync, url, min_confidence)

    def _read_sync(self, url: str, min_confidence: float = 0.0) -> DataPulseItem:
        result, parser = self.router.route(url)
        if not result.success:
            raise RuntimeError(result.error)

        item = self._to_item(result, parser.name)
        if item.confidence < min_confidence:
            raise RuntimeError(f"Confidence too low: {item.confidence:.3f}")

        if self.inbox.add(item):
            self.inbox.save()
        else:
            logger.info("Item already exists in inbox: %s", item.id)

        md_path = save_markdown(item)
        if md_path:
            logger.info("Saved markdown: %s", md_path)
        return item

    async def read_batch(
        self,
        urls: list[str],
        *,
        min_confidence: float = 0.0,
        return_all: bool = True,
    ) -> list[DataPulseItem]:
        # Normalize and deduplicate URLs
        seen: set[str] = set()
        unique_urls: list[str] = []
        for url in urls:
            normalized = url.strip().rstrip("/")
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_urls.append(url.strip())
        max_concurrency = int(os.getenv("DATAPULSE_BATCH_CONCURRENCY", "5"))
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _bounded_read(url: str) -> DataPulseItem:
            async with semaphore:
                return await self.read(url, min_confidence=min_confidence)

        tasks = [_bounded_read(url) for url in unique_urls]
        outputs: list[DataPulseItem] = []
        for item in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(item, BaseException):
                logger.warning("Batch entry failed: %s", item)
                if return_all:
                    continue
                raise item
            outputs.append(item)  # type: ignore[arg-type]

        # Highest confidence first
        outputs.sort(key=lambda it: it.confidence, reverse=True)
        return outputs

    async def search(
        self,
        query: str,
        *,
        sites: list[str] | None = None,
        platform: str | None = None,
        limit: int = 5,
        fetch_content: bool = True,
        min_confidence: float = 0.0,
        provider: str = "auto",
        mode: str = "single",
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
        freshness: str | None = None,
    ) -> list[DataPulseItem]:
        """Search the web via Jina/Tavily and return scored DataPulseItems."""
        effective_mode = "multi" if provider == "multi" else mode
        merged_sites = list(sites or [])
        if platform and platform in PLATFORM_SEARCH_SITES:
            for domain in PLATFORM_SEARCH_SITES[platform]:
                if domain not in merged_sites:
                    merged_sites.append(domain)

        # Keep gateway Jina client reference aligned for external test/mocking.
        self._search_gateway._jina_client = self._jina_client

        # Provider-level orchestration (single provider + fallback, or multi-source fusion).
        requested_time_range = time_range or freshness

        if provider in {"jina", "auto"}:
            search_hits, search_audit = self._run_jina_search(
                query,
                sites=merged_sites,
                limit=limit,
            )
            if not search_hits and provider == "auto":
                search_hits, search_audit = self._search_gateway.search(
                    query,
                    sites=merged_sites,
                    limit=limit,
                    provider="tavily",
                    mode=effective_mode,
                    deep=deep,
                    news=news,
                    time_range=requested_time_range,
                )
        else:
            search_hits, search_audit = self._search_gateway.search(
                query,
                sites=merged_sites,
                limit=limit,
                provider=provider,
                mode=effective_mode,
                deep=deep,
                news=news,
                time_range=requested_time_range,
            )

        if not search_hits:
            return []

        items: list[DataPulseItem] = []
        for sr in search_hits:
            item: DataPulseItem | None = None
            hit_sources = sr.extra.get("sources", [sr.provider])
            hit_sources = list(dict.fromkeys(hit_sources)) if hit_sources else [sr.provider]
            hit_source_count = len(hit_sources)
            cross_validation = sr.extra.get("cross_validation", {})
            cross_validated = bool(
                isinstance(cross_validation, dict)
                and cross_validation.get("is_cross_validated")
            )

            # Tag and confidence bias for multi-source supported snippets.
            parser_name = "jina_search" if sr.provider == "jina" else "tavily_search" if sr.provider == "tavily" else "search_result"
            extra_flags = ["search_result", parser_name]
            if hit_source_count >= 2:
                extra_flags.append("multi_source")
            if cross_validated:
                extra_flags.append("cross_validated")

            if fetch_content and sr.url:
                try:
                    result, parser = self.router.route(sr.url)
                    if result.success:
                        item = self._to_item(result, parser.name)
                except Exception:
                    logger.info("Full fetch failed for search result %s, using snippet", sr.url)

            if item is None:
                # Build item directly from search snippet
                content = sr.snippet
                lang = normalize_language(f"{sr.title} {content}")
                confidence, reasons = compute_confidence(
                    parser_name,
                    has_title=bool(sr.title),
                    content_length=len(content),
                    has_source=True,
                    has_author=False,
                    extra_flags=extra_flags,
                )
                snippet_source_type = SourceType.XHS if platform == "xhs" else SourceType.GENERIC
                snippet_tags = [parser_name, snippet_source_type.value]
                if platform == "xhs":
                    snippet_tags.append("xhs_search")
                snippet_tags.append(sr.provider)
                if hit_source_count >= 2:
                    snippet_tags.append("multi_source")
                if cross_validated:
                    snippet_tags.append("cross_validated")
                item = DataPulseItem(
                    source_type=snippet_source_type,
                    source_name=sr.source,
                    title=(sr.title or "Untitled").strip()[:300],
                    content=content,
                    url=sr.url,
                    parser=parser_name,
                    confidence=confidence,
                    confidence_factors=reasons,
                    language=lang,
                    tags=snippet_tags,
                    extra={
                        "search_query": query,
                        "search_provider": provider,
                        "search_mode": effective_mode,
                        "search_audit": search_audit,
                        "search_sources": hit_sources,
                        "search_source_count": hit_source_count,
                        "search_raw": sr.raw,
                        "search_consistency": cross_validation,
                        "search_cross_validation": cross_validation,
                        "search_description": "",
                    },
                    score=0,
                )

            # Ensure search metadata is present
            item.extra["search_query"] = query
            item.extra["search_provider"] = provider
            item.extra["search_mode"] = effective_mode
            item.extra["search_audit"] = search_audit
            item.extra["search_sources"] = hit_sources
            item.extra["search_source_count"] = hit_source_count
            item.extra["search_consistency"] = cross_validation
            item.extra["search_cross_validation"] = cross_validation
            item.extra["search_source_diversity"] = sr.extra.get("source_diversity", 0.0)
            if "jina_search" not in item.tags:
                item.tags.append("jina_search")
            if parser_name not in item.tags:
                item.tags.append(parser_name)
            if "search" not in item.tags:
                item.tags.append("search")
            if effective_mode == "multi" or hit_source_count >= 2:
                if "multi_source" not in item.tags:
                    item.tags.append("multi_source")
            if cross_validated and "cross_validated" not in item.tags:
                item.tags.append("cross_validated")

            if min_confidence and item.confidence < min_confidence:
                continue

            items.append(item)

        # Batch add to inbox + single save
        added_any = False
        for item in items:
            if self.inbox.add(item):
                added_any = True
        if added_any:
            self.inbox.save()

        # Score and rank
        authority_map = self.catalog.build_authority_map()
        ranked = rank_items(items, authority_map=authority_map)
        return ranked

    async def trending(
        self,
        location: str = "",
        top_n: int = 20,
        store: bool = False,
        validate: bool | None = None,
        validate_mode: str = "strict",
    ) -> dict[str, Any]:
        """Fetch trending topics from trends24.in.

        Returns structured data with the latest snapshot.
        store=True saves the snapshot as a DataPulseItem to inbox (opt-in).
        """
        collector = TrendingCollector()
        snapshots = await asyncio.to_thread(
            collector.fetch_snapshots, location, top_n
        )
        if not snapshots:
            return {
                "location": location or "worldwide",
                "snapshot_time": "",
                "trend_count": 0,
                "trends": [],
            }

        latest = snapshots[0]
        loc_slug = location.strip().lower() if location else "worldwide"
        from urllib.parse import quote
        trends_out = [
            {
                "rank": t.rank,
                "name": t.name,
                "volume": t.volume,
                "volume_raw": t.volume_raw,
                "twitter_search_url": f"https://x.com/search?q={quote(t.name)}",
            }
            for t in latest.trends
        ]

        result: dict[str, Any] = {
            "location": loc_slug,
            "snapshot_time": latest.timestamp_utc or latest.timestamp,
            "trend_count": len(latest.trends),
            "trends": trends_out,
        }

        if validate is None:
            validate = os.getenv("DATAPULSE_TRENDING_CROSS_VALIDATE", "0").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
        if validate and result["trends"]:
            result["trends"] = await self._validate_trending_topics(
                result["trends"],
                query_mode=validate_mode,
            )
            result["trend_count"] = len(result["trends"])

        if store:
            url = build_trending_url(location)
            parse_result = collector.parse(url)
            if parse_result.success:
                item = self._to_item(parse_result, collector.name)
                if self.inbox.add(item):
                    self.inbox.save()
                result["stored_item_id"] = item.id

        return result

    async def _validate_trending_topics(
        self,
        trends: list[dict[str, Any]],
        *,
        query_mode: str = "strict",
    ) -> list[dict[str, Any]]:
        concurrency = max(1, int(os.getenv("DATAPULSE_TRENDING_VALIDATE_CONCURRENCY", "4")))
        sem = asyncio.Semaphore(concurrency)

        async def _check(topic: str) -> dict[str, Any]:
            async with sem:
                def _sync_search() -> tuple[list[Any], dict[str, Any]]:
                    return self._search_gateway.search(
                        topic,
                        limit=3,
                        provider="tavily",
                        mode="single",
                        news=query_mode == "news",
                        time_range="day" if query_mode == "news" else None,
                    )

                hits, audit = await asyncio.to_thread(_sync_search)
                is_validated = False
                source_count = 0
                consistency: dict[str, Any] = {}
                search_provider = "tavily"
                validation_level = "unvalidated"

                if hits:
                    top_hit = hits[0]
                    providers = top_hit.extra.get("providers", [])
                    if not providers and isinstance(top_hit.extra.get("cross_validation"), dict):
                        providers = top_hit.extra["cross_validation"].get("providers", [])
                    source_count = len(set(providers or [top_hit.provider]))
                    consistency = top_hit.extra.get("cross_validation", {})
                    is_cross_validated = bool(
                        isinstance(consistency, dict)
                        and consistency.get("is_cross_validated", False)
                    )
                    if is_cross_validated:
                        search_provider = "multi"
                    if query_mode == "strict":
                        is_validated = is_cross_validated
                        validation_level = "strict_validated" if is_validated else "strict_rejected"
                    elif query_mode == "news":
                        is_validated = source_count >= 1
                        validation_level = "news_validated" if is_validated else "news_rejected"
                    else:
                        is_validated = source_count >= 1
                        validation_level = "lenient_validated" if is_validated else "lenient_rejected"
                return {
                    "search_consistency": consistency,
                    "search_source_count": source_count,
                    "is_validated": is_validated,
                    "validation_mode": query_mode,
                    "validation_level": validation_level,
                    "search_provider": search_provider,
                    "search_audit": audit,
                }

        check_tasks = [(_check(item["name"]), item) for item in trends if item.get("name")]
        if not check_tasks:
            return []

        check_results = await asyncio.gather(*[t[0] for t in check_tasks])

        validated_topics: list[dict[str, Any]] = []
        for report, (_, topic) in zip(check_results, check_tasks):
            merged = dict(topic)
            merged.update(report)
            if report.get("is_validated"):
                validated_topics.append(merged)
        return validated_topics

    def emit_digest_package(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        top_n: int = 3,
        secondary_n: int = 7,
        min_confidence: float = 0.0,
        since: str | None = None,
        output_format: str = "json",
    ) -> str:
        """Build read-only digest package for downstream automation (no side effects)."""
        payload = cast(dict[str, Any], self.build_digest(
            profile=profile,
            source_ids=source_ids,
            top_n=top_n,
            secondary_n=secondary_n,
            min_confidence=min_confidence,
            since=since,
        ))

        primary_payload = payload.get("primary")
        secondary_payload = payload.get("secondary")
        primary = primary_payload if isinstance(primary_payload, list) else []
        secondary = secondary_payload if isinstance(secondary_payload, list) else []
        all_items = [item for item in primary + secondary if isinstance(item, dict)]
        sources: dict[str, int] = {}
        timeline: list[dict[str, Any]] = []
        recommendations: list[str] = []
        todos: list[str] = []
        high_confidence_hits = 0

        for item in all_items:
            source_name = item.get("source_name") or "unknown"
            sources[source_name] = sources.get(source_name, 0) + 1
            timeline.append(
                {
                    "time": item.get("date_published", item.get("fetched_at", "")),
                    "title": item.get("title", ""),
                    "source": source_name,
                    "url": item.get("url", ""),
                }
            )
            if (item.get("score", 0) or 0) >= 60:
                recommendations.append(
                    f"优先复核高置信内容: {item.get('title', '')} ({source_name})"
                )
                high_confidence_hits += 1
            else:
                todos.append(f"需补充来源/验证: {item.get('title', '')} ({source_name})")

        package: dict[str, Any] = {
            "summary": {
                "title": f"DataPulse Digest Package | {profile}",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "high_confidence_count": high_confidence_hits,
                "item_count": len(all_items),
                "stats": payload.get("stats", {}),
            },
            "sources": [
                {"source_name": name, "count": count}
                for name, count in sorted(sources.items(), key=lambda kv: kv[0])
            ],
            "recommendations": recommendations,
            "timeline": sorted(timeline, key=lambda x: x.get("time", ""), reverse=True),
            "todos": todos,
            "digest_payload": payload,
        }

        if output_format.lower() == "md" or output_format.lower() == "markdown":
            lines = [
                "# DataPulse Digest Package",
                f"- **生成时间**: {package['summary']['generated_at']}",
                f"- **高置信条目**: {package['summary']['high_confidence_count']}",
                f"- **总条目**: {package['summary']['item_count']}",
                "",
                "## 摘要",
                package["summary"]["title"],
                "",
                "## 来源",
            ]
            for source in package["sources"]:
                lines.append(f"- {source['source_name']}: {source['count']}")
            lines.extend([
                "",
                "## 建议行动",
            ])
            for item in package["recommendations"]:
                lines.append(f"- {item}")
            lines.extend([
                "",
                "## 待办",
            ])
            for item in package["todos"]:
                lines.append(f"- {item}")
            lines.extend([
                "",
                "## 时序",
            ])
            for event in package["timeline"]:
                lines.append(f"- [{event.get('time','')}]{event.get('title','')}")
            return "\n".join(lines)

        return json.dumps(package, ensure_ascii=False, indent=2)

    def _to_item(self, parse_result, parser_name: str) -> DataPulseItem:
        source_type = parse_result.source_type or SourceType.GENERIC
        lang = normalize_language(f"{parse_result.title} {parse_result.content}")
        conf_flags: list[str] = list(getattr(parse_result, "confidence_flags", []))
        source_name = parse_result.author or source_type.value
        source_name = source_name or parser_name

        confidence, reasons = compute_confidence(
            parser_name,
            has_title=bool(parse_result.title.strip()),
            content_length=len(parse_result.content or ""),
            has_source=bool(source_name),
            has_author=bool(parse_result.author),
            media_hint=getattr(parse_result, "media_type", "text") or "text",
            extra_flags=conf_flags,
        )

        return DataPulseItem(
            source_type=source_type,
            source_name=source_name,
            title=(parse_result.title or "Untitled").strip()[:300],
            content=parse_result.content or "",
            url=parse_result.url,
            parser=parser_name,
            confidence=confidence,
            confidence_factors=reasons,
            quality_rank=0,
            language=lang,
            tags=list(dict.fromkeys([
                source_type.value,
                parser_name,
                *getattr(parse_result, "tags", []),
            ])),
            extra={
                "raw_excerpt": parse_result.excerpt,
                **getattr(parse_result, "extra", {}),
            },
            score=0,
        )

    def doctor(self) -> dict[str, list[dict[str, str | bool]]]:
        """Run health checks on all collectors, grouped by tier."""
        return self.router.doctor()

    def mark_processed(self, item_id: str, processed: bool = True) -> bool:
        ok = self.inbox.mark_processed(item_id, processed=processed)
        if ok:
            self.inbox.save()
        return ok

    def query_unprocessed(self, limit: int = 20, min_confidence: float = 0.0) -> list[DataPulseItem]:
        return self.inbox.query_unprocessed(limit=limit, min_confidence=min_confidence)

    def detect_platform(self, url: str) -> str:
        result, parser = self.router.route(url)
        if result.success:
            return parser.name
        return "generic"

    def list_memory(self, limit: int = 20, min_confidence: float = 0.0) -> list[DataPulseItem]:
        return self.inbox.query(limit=limit, min_confidence=min_confidence)

    def resolve_source(self, url: str) -> dict[str, Any]:
        return self.catalog.resolve_source(url)

    def list_sources(self, *, include_inactive: bool = False, public_only: bool = False) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.catalog.list_sources(include_inactive=include_inactive, public_only=public_only)]

    def list_packs(self, *, public_only: bool = False) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self.catalog.list_packs(public_only=public_only)]

    def list_subscriptions(self, profile: str = "default") -> list[str]:
        return self.catalog.list_subscriptions(profile=profile)

    def subscribe_source(self, source_id: str, *, profile: str = "default") -> bool:
        return self.catalog.subscribe(profile=profile, source_id=source_id)

    def unsubscribe_source(self, source_id: str, *, profile: str = "default") -> bool:
        return self.catalog.unsubscribe(profile=profile, source_id=source_id)

    def install_pack(self, slug: str, *, profile: str = "default") -> int:
        return self.catalog.install_pack(profile, slug=slug)

    def query_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> list[DataPulseItem]:
        all_items = self.inbox.all_items(min_confidence=min_confidence)
        filtered = self.catalog.filter_by_subscription(
            all_items,
            profile=profile,
            source_ids=source_ids,
        )
        if since:
            since_dt = None
            try:
                since_dt = datetime.fromisoformat(since)
            except Exception:
                since_dt = None
            if since_dt:
                valid: list[DataPulseItem] = []
                for item in filtered:
                    try:
                        ts = datetime.fromisoformat(item.fetched_at)
                    except Exception:
                        valid.append(item)
                        continue
                    if ts >= since_dt:
                        valid.append(item)
                filtered = valid

        ordered = sorted(filtered, key=lambda it: it.fetched_at, reverse=True)
        return ordered[: max(0, limit)]

    def build_json_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> dict[str, Any]:
        items = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )
        base = "https://datapulse.local"
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"DataPulse Feed ({profile})",
            "home_page_url": base,
            "feed_url": f"{base}/feed/{profile}.json",
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content_text": item.content,
                    "date_published": item.fetched_at,
                    "url": item.url,
                    "source_type": item.source_type.value,
                    "source_name": item.source_name,
                    "authors": [{"name": item.source_name}] if item.source_name else [],
                }
                for item in items
            ],
            "generated_at": now,
        }

    def build_rss_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> str:
        items = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )
        def _xml_escape(value: str) -> str:
            return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;"))

        rows = []
        for item in items:
            pub = item.fetched_at
            try:
                dt = datetime.fromisoformat(pub).strftime("%a, %d %b %Y %H:%M:%S GMT")
            except Exception:
                dt = pub
            rows.append(
                "<item>"
                f"<title>{_xml_escape(item.title)}</title>"
                f"<link>{_xml_escape(item.url)}</link>"
                f"<guid>{_xml_escape(item.id)}</guid>"
                f"<pubDate>{_xml_escape(dt)}</pubDate>"
                f"<description>{_xml_escape(item.content[:1800])}</description>"
                "</item>"
            )

        payload = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<rss version=\"2.0\"><channel>"
            "<title>DataPulse Feed</title>"
            "<description>Unified content feed</description>"
            "<link>https://datapulse.local</link>"
            + "".join(rows)
            + "</channel></rss>"
        )
        return payload


    def build_digest(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        top_n: int = 3,
        secondary_n: int = 7,
        min_confidence: float = 0.0,
        since: str | None = None,
        max_per_source: int = 2,
    ) -> dict[str, Any]:
        """Build a curated digest with primary and secondary stories."""
        # 1. Get candidates
        candidates = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=500,  # grab a large pool
            min_confidence=min_confidence,
            since=since,
        )
        candidates_total = len(candidates)

        if not candidates:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            return {
                "version": "1.0",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "digest_date": today,
                "stats": {
                    "candidates_total": 0,
                    "candidates_after_dedup": 0,
                    "sources_seen": 0,
                    "selected_primary": 0,
                    "selected_secondary": 0,
                },
                "primary": [],
                "secondary": [],
                "provenance": "No items available",
            }

        # 2. Score and rank
        authority_map = self.catalog.build_authority_map()
        ranked = rank_items(candidates, authority_map=authority_map)

        # 3. Fingerprint dedup (keep first = highest scored per fingerprint)
        seen_fps: set[str] = set()
        deduped: list[DataPulseItem] = []
        for item in ranked:
            fp = content_fingerprint(item.content)
            if fp not in seen_fps:
                seen_fps.add(fp)
                deduped.append(item)

        sources_seen = len({item.source_name for item in deduped})

        # 4. Diverse selection
        total_needed = top_n + secondary_n
        selected = self._select_diverse(
            deduped, total_needed, max_per_source=max_per_source,
        )

        primary = selected[:top_n]
        secondary = selected[top_n:top_n + secondary_n]

        today = datetime.utcnow().strftime("%Y-%m-%d")
        for item in primary + secondary:
            item.digest_date = today

        return {
            "version": "1.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "digest_date": today,
            "stats": {
                "candidates_total": candidates_total,
                "candidates_after_dedup": len(deduped),
                "sources_seen": sources_seen,
                "selected_primary": len(primary),
                "selected_secondary": len(secondary),
            },
            "primary": [item.to_dict() for item in primary],
            "secondary": [item.to_dict() for item in secondary],
            "provenance": f"Curated from {candidates_total} items across {sources_seen} sources",
        }

    @staticmethod
    def _select_diverse(
        items: list[DataPulseItem],
        n: int,
        *,
        max_per_source: int = 2,
    ) -> list[DataPulseItem]:
        """Greedy diverse selection: limits same-source items to max_per_source."""
        if not items:
            return []
        selected: list[DataPulseItem] = []
        source_counts: dict[str, int] = {}

        for item in items:
            if len(selected) >= n:
                break
            source = item.source_name
            count = source_counts.get(source, 0)
            if count >= max_per_source:
                continue
            source_counts[source] = count + 1
            selected.append(item)

        return selected

    def build_atom_feed(
        self,
        *,
        profile: str = "default",
        source_ids: list[str] | None = None,
        limit: int = 20,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> str:
        items = self.query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

        def _xml_escape(value: str) -> str:
            return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;"))

        now = datetime.utcnow().isoformat() + "Z"
        base = "https://datapulse.local"

        entries = []
        for item in items:
            updated = item.fetched_at
            if not updated.endswith("Z"):
                updated += "Z"
            entries.append(
                "<entry>"
                f"<title>{_xml_escape(item.title)}</title>"
                f'<link href="{_xml_escape(item.url)}" rel="alternate"/>'
                f"<id>urn:datapulse:{_xml_escape(item.id)}</id>"
                f"<updated>{_xml_escape(updated)}</updated>"
                f"<summary>{_xml_escape(item.content[:1800])}</summary>"
                f"<author><name>{_xml_escape(item.source_name)}</name></author>"
                "</entry>"
            )

        payload = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<feed xmlns="http://www.w3.org/2005/Atom">'
            f"<title>DataPulse Feed ({_xml_escape(profile)})</title>"
            f'<link href="{base}/feed/{profile}.atom" rel="self"/>'
            f"<id>urn:datapulse:feed:{_xml_escape(profile)}</id>"
            f"<updated>{now}</updated>"
            + "".join(entries)
            + "</feed>"
        )
        return payload


def _safe_markdown_document(item: DataPulseItem) -> str:
    return output_record_md(item)
