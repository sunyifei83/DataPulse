"""Collector/router layer for DataPulse."""

from __future__ import annotations

import logging

from datapulse.core.utils import resolve_platform_hint
from datapulse.collectors import (
    BaseCollector,
    ParseResult,
    TwitterCollector,
    YouTubeCollector,
    RedditCollector,
    BilibiliCollector,
    TelegramCollector,
    WeChatCollector,
    XiaohongshuCollector,
    RssCollector,
    GenericCollector,
    JinaCollector,
)

logger = logging.getLogger("datapulse.router")


class ParsePipeline:
    def __init__(self, extra_parsers: list[BaseCollector] | None = None):
        configured = extra_parsers or []
        self.parsers: list[BaseCollector] = []
        self.parsers.extend(configured)
        self.parsers.extend([
            TwitterCollector(),
            YouTubeCollector(),
            RedditCollector(),
            BilibiliCollector(),
            TelegramCollector(),
            WeChatCollector(),
            XiaohongshuCollector(),
            RssCollector(),
            GenericCollector(),
            JinaCollector(),
        ])

    def register_parser(self, parser: BaseCollector, priority: bool = False) -> None:
        if priority:
            self.parsers.insert(0, parser)
        else:
            self.parsers.append(parser)

    @property
    def available_parsers(self) -> list[str]:
        return [p.name for p in self.parsers]

    def route(self, url: str) -> tuple[ParseResult, BaseCollector]:
        hint = resolve_platform_hint(url)
        prioritized: list[BaseCollector] = []
        fallback: list[BaseCollector] = []
        for parser in self.parsers:
            if parser.name == hint or parser.source_type.value == hint:
                prioritized.append(parser)
            else:
                fallback.append(parser)

        for parser in prioritized + fallback:
            try:
                if not parser.can_handle(url):
                    continue
                logger.info("Routing with %s for %s", parser.name, url)
                result = parser.parse(url)
                if result.success:
                    return result, parser

                logger.warning("%s failed for %s: %s", parser.name, url, result.error)
            except Exception as exc:
                logger.warning("%s raised for %s: %s", parser.name, url, exc)
                result = ParseResult.failure(url, str(exc))

        return ParseResult.failure(url, f"No parser produced successful result for {url}"), self.parsers[-1]
