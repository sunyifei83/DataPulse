"""Persistence for structured records and markdown output."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from .models import DataPulseItem
from .utils import content_hash, get_domain_tag


class UnifiedInbox:
    """Append-only JSON memory with bounded size and deduplication."""

    def __init__(self, path: str):
        self.path: Path = Path(path)
        self.items: list[DataPulseItem] = []
        self.max_items = int(os.getenv("DATAPULSE_MAX_INBOX", "500"))
        self.max_days = int(os.getenv("DATAPULSE_KEEP_DAYS", "30"))
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.items = []
            return

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self.items = []
            return

        loaded = []
        for row in data if isinstance(data, list) else []:
            try:
                loaded.append(DataPulseItem.from_dict(row))
            except (KeyError, TypeError, ValueError):
                continue
        self.items = loaded
        self._prune()

    def _prune(self) -> None:
        cutoff = datetime.utcnow() - timedelta(days=max(0, self.max_days))
        retained: list[DataPulseItem] = []
        for item in self.items:
            try:
                ts = datetime.fromisoformat(item.fetched_at)
            except Exception:
                retained.append(item)
                continue
            if ts >= cutoff:
                retained.append(item)

        # Deduplicate
        dedup: dict[str, DataPulseItem] = {}
        for item in retained:
            dedup[item.id] = item

        ordered = sorted(dedup.values(), key=lambda i: i.fetched_at, reverse=True)
        self.items = ordered[: self.max_items]

    def add(self, item: DataPulseItem) -> bool:
        if any(existing.id == item.id for existing in self.items):
            return False
        self.items.append(item)
        self.items.sort(key=lambda i: i.fetched_at, reverse=True)
        self.items = self.items[: self.max_items]
        return True

    def save(self) -> None:
        self._prune()
        payload = [item.to_dict() for item in self.items]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def query(self, limit: int = 20, min_confidence: float = 0.0) -> list[DataPulseItem]:
        filtered = [item for item in self.items if item.confidence >= min_confidence]
        return sorted(filtered, key=lambda i: i.confidence, reverse=True)[:limit]

    def all_items(self, min_confidence: float = 0.0) -> list[DataPulseItem]:
        return [item for item in self.items if item.confidence >= min_confidence]

    def mark_processed(self, item_id: str, processed: bool = True) -> bool:
        for item in self.items:
            if item.id == item_id:
                item.processed = processed
                return True
        return False

    def query_unprocessed(self, limit: int = 20, min_confidence: float = 0.0) -> list[DataPulseItem]:
        filtered = [
            item for item in self.items
            if not item.processed and item.confidence >= min_confidence
        ]
        return sorted(filtered, key=lambda i: i.confidence, reverse=True)[:limit]


def save_markdown(item: DataPulseItem, path: str | None = None) -> str | None:
    if not path:
        path = os.getenv("DATAPULSE_MARKDOWN_PATH", "").strip()

    if not path:
        vault = os.getenv("OBSIDIAN_VAULT", "").strip()
        if vault:
            path = str(Path(vault) / "01-收集箱" / "datapulse-inbox.md")
        else:
            output_dir = os.getenv("OUTPUT_DIR", "").strip()
            if not output_dir:
                return None
            path = str(Path(output_dir) / "datapulse-hub.md")

    if not path:
        return None

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    snippet = item.content[:1800].replace("\n", "\n")
    excerpt = item.confidence_factors or []

    with target.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{item.title}]({item.url})\n")
        f.write(f"- source: {item.source_name} / {item.source_type.value}\n")
        f.write(f"- fetched: {item.fetched_at[:16]}\n")
        f.write(f"- confidence: {item.confidence:.3f}\n")
        f.write(f"- tags: {', '.join(item.tags)}\n")
        f.write(f"- factors: {', '.join(excerpt)}\n")
        f.write(f"\n{snippet}\n")
        f.write("\n---\n")
    return str(target)


def output_record_md(item: DataPulseItem) -> str:
    """Build markdown document content for one record."""
    domain = get_domain_tag(item.url)
    lines: list[str] = [
        "---",
        f"id: {item.id}",
        f"source_type: {item.source_type.value}",
        f"source_name: {item.source_name}",
        f"title: {item.title}",
        f"url: {item.url}",
        f"fetched_at: {item.fetched_at}",
        f"parser: {item.parser}",
        f"language: {item.language}",
        f"confidence: {item.confidence}",
        f"domain: {domain}",
        f"content_hash: {content_hash(item.content)}",
        "---",
        "",
        f"# {item.title}",
        "",
        f"- Source: {item.source_name}",
        f"- URL: {item.url}",
        f"- Confidence: {item.confidence:.3f}",
        f"- Parser reliability hints: {', '.join(item.confidence_factors)}",
        "",
        item.content,
    ]
    return "\n".join(lines)
