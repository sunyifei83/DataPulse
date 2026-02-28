"""Collector exports."""

from .arxiv import ArxivCollector
from .base import BaseCollector, ParseResult
from .bilibili import BilibiliCollector
from .generic import GenericCollector
from .hackernews import HackerNewsCollector
from .jina import JinaCollector
from .reddit import RedditCollector
from .rss import RssCollector
from .telegram import TelegramCollector
from .twitter import TwitterCollector
from .wechat import WeChatCollector
from .xhs import XiaohongshuCollector
from .youtube import YouTubeCollector

try:
    from .browser import BrowserCollector
except ImportError:
    BrowserCollector = None  # type: ignore[assignment,misc]

__all__ = [
    "BaseCollector",
    "ParseResult",
    "ArxivCollector",
    "TwitterCollector",
    "RedditCollector",
    "YouTubeCollector",
    "BilibiliCollector",
    "RssCollector",
    "TelegramCollector",
    "WeChatCollector",
    "XiaohongshuCollector",
    "HackerNewsCollector",
    "GenericCollector",
    "JinaCollector",
    "BrowserCollector",
]
