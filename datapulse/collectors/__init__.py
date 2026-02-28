"""Collector exports."""

from .base import BaseCollector, ParseResult
from .bilibili import BilibiliCollector
from .generic import GenericCollector
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
    "TwitterCollector",
    "RedditCollector",
    "YouTubeCollector",
    "BilibiliCollector",
    "RssCollector",
    "TelegramCollector",
    "WeChatCollector",
    "XiaohongshuCollector",
    "GenericCollector",
    "JinaCollector",
    "BrowserCollector",
]
