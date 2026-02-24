"""Core data models for DataPulse."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import hashlib


class SourceType(str, Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    BILIBILI = "bilibili"
    TELEGRAM = "telegram"
    WECHAT = "wechat"
    XHS = "xhs"
    RSS = "rss"
    GENERIC = "generic"
    MANUAL = "manual"


class MediaType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"


@dataclass
class DataPulseItem:
    source_type: SourceType
    source_name: str
    title: str
    content: str
    url: str

    parser: str = ""
    id: str = ""
    fetched_at: str = ""
    media_type: MediaType = MediaType.TEXT

    score: int = 0
    confidence: float = 0.0
    confidence_factors: list[str] = field(default_factory=list)
    quality_rank: int = 0

    tags: list[str] = field(default_factory=list)
    language: str = "unknown"

    category: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    processed: bool = False
    digest_date: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = hashlib.md5(f"{self.url}:{self.title}".encode("utf-8")).hexdigest()[:12]
        if not self.fetched_at:
            self.fetched_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_type"] = self.source_type.value
        payload["media_type"] = self.media_type.value
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DataPulseItem":
        if isinstance(data.get("source_type"), str):
            data["source_type"] = SourceType(data["source_type"])
        if isinstance(data.get("media_type"), str):
            data["media_type"] = MediaType(data["media_type"])

        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid})
