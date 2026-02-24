"""Collector exports."""

from .base import BaseCollector, ParseResult
from .twitter import TwitterCollector
from .reddit import RedditCollector
from .youtube import YouTubeCollector
from .bilibili import BilibiliCollector
from .rss import RssCollector
from .telegram import TelegramCollector
from .wechat import WeChatCollector
from .xhs import XiaohongshuCollector
from .generic import GenericCollector
from .jina import JinaCollector

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
]
