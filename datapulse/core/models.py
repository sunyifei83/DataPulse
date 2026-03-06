"""Core data models for DataPulse."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .triage import normalize_review_state


class SourceType(str, Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    BILIBILI = "bilibili"
    TELEGRAM = "telegram"
    WECHAT = "wechat"
    XHS = "xhs"
    RSS = "rss"
    ARXIV = "arxiv"
    HACKERNEWS = "hackernews"
    TRENDING = "trending"
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
    review_state: str = "new"
    review_notes: list[dict[str, str]] = field(default_factory=list)
    review_actions: list[dict[str, str]] = field(default_factory=list)
    duplicate_of: Optional[str] = None
    digest_date: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = hashlib.md5(f"{self.url}:{self.title}".encode("utf-8")).hexdigest()[:12]
        if not self.fetched_at:
            self.fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.review_state = normalize_review_state(self.review_state, processed=self.processed)
        self.review_notes = [
            {str(k): str(v) for k, v in note.items()}
            for note in self.review_notes
            if isinstance(note, dict)
        ]
        self.review_actions = [
            {str(k): str(v) for k, v in action.items()}
            for action in self.review_actions
            if isinstance(action, dict)
        ]
        self.duplicate_of = str(self.duplicate_of or "").strip() or None

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
