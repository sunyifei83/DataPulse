#!/usr/bin/env python3
"""Sync DataPulse local markdown docs and token inventory into Notion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

NOTION_VERSION = "2022-06-28"
DEFAULT_PARENT_PAGE_ID = "3166986288aa812a8a3ef977f79cd4e9"
DEFAULT_DOC_DIR = Path(
    "/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian"
    "/Documents/SunYifei/01-项目开发/DataPulse"
)
DEFAULT_TOKEN_STORE = Path(
    "/Users/sunyifei/Library/Mobile Documents/iCloud~md~obsidian"
    "/Documents/SunYifei/信息资产/ob-digital-asset-facts/Secrets/API Token Store.md"
)
DOC_TITLE_PAGE = "DataPulse 文档（同步版）"
TOKEN_TITLE_PAGE = "DataPulse API Token 台账"
SUMMARY_PAGE_TITLE = "DataPulse 文档变更摘要"

BASE_REQUIRED_TOKENS = [
    "JINA_API_KEY",
    "TAVILY_API_KEY",
    "FIRECRAWL_API_KEY",
    "GROQ_API_KEY",
    "DATAPULSE_LLM_API_KEY",
    "TG_API_ID",
    "TG_API_HASH",
]

TOKEN_NAME_RE = re.compile(
    r"[A-Z0-9_]*(?:API_KEY|TOKEN|BOT_TOKEN|CLIENT_SECRET|CLIENT_ID|APP_SECRET|APP_ID|HASH|ID)"
)
INVOCATION_RE = re.compile(
    r"(?:get_secret|has_secret|os\.getenv|getenv)\(\s*['\"]([A-Z0-9_]+)['\"]\s*\)",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^\s*###\s+([A-Za-z0-9_]+)$")
SOURCE_RE = re.compile(r"^\s*-\s*Source\s*:.*`([^`]+)`")
VALUE_RE = re.compile(r"^\s*-\s*Value[^:]*:\s*`?([^`]+)`?$")
TABLE_RE = re.compile(r"^\s*\|\s*([A-Za-z0-9_]+)\s*\|\s*([^|]+?)\s*(?:\|.*)?$")
INLINE_KV_RE = re.compile(r"^\s*[-*]\s*([A-Za-z0-9_]+)\s*[:：]\s*`?([^`]+)`?")

REQUEST_INTERVAL_SECONDS = 0.35
REQUEST_TIMEOUT_SECONDS = 60
REQUEST_MAX_RETRIES = 6
REQUEST_BACKOFF_BASE_SECONDS = 1.0

_last_request_ts = 0.0


@dataclass(frozen=True)
class SyncState:
    page_id_by_path: dict[str, str]
    sha_by_path: dict[str, str]
    summary_sha: str = ""
    token_summary_sha: str = ""


@dataclass(frozen=True)
class DocumentRecord:
    path: str
    title: str
    source_sha: str
    cleaned_text: str
    cleaned_sha: str
    line_dedupe_count: int
    block_dedupe_count: int


def notion_request(
    token: str,
    method: str,
    path: str,
    json_payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    max_retries: int | None = None,
) -> Any:
    global _last_request_ts
    if max_retries is None:
        max_retries = REQUEST_MAX_RETRIES

    url = f"https://api.notion.com/v1/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    attempt = 0
    while True:
        now = time.monotonic()
        elapsed = now - _last_request_ts
        if elapsed < REQUEST_INTERVAL_SECONDS:
            time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)
        _last_request_ts = time.monotonic()

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=json_payload,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise RuntimeError(f"{method} {path} failed after retries: {exc}") from exc
            backoff = REQUEST_BACKOFF_BASE_SECONDS * (2**attempt) + random.uniform(0, 0.5)
            attempt += 1
            time.sleep(min(backoff, 30))
            continue

        if response.status_code == 429:
            if attempt >= max_retries:
                raise RuntimeError(f"{method} {path} failed {response.status_code}: {response.text}")
            retry_after = response.headers.get("Retry-After")
            delay = REQUEST_BACKOFF_BASE_SECONDS * (2**attempt)
            try:
                if retry_after:
                    delay = max(delay, float(retry_after))
            except ValueError:
                pass
            attempt += 1
            time.sleep(min(delay + random.uniform(0, 0.5), 30))
            continue

        if response.status_code >= 500:
            if attempt >= max_retries:
                raise RuntimeError(f"{method} {path} failed {response.status_code}: {response.text}")
            backoff = REQUEST_BACKOFF_BASE_SECONDS * (2**attempt) + random.uniform(0, 0.5)
            attempt += 1
            time.sleep(min(backoff, 30))
            continue

        if response.status_code == 401:
            raise RuntimeError(f"{method} {path} failed {response.status_code}: token invalid/unauthorized")
        if response.status_code >= 400:
            raise RuntimeError(f"{method} {path} failed {response.status_code}: {response.text}")
        if response.text:
            return response.json()
        return {}


def hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def split_text_blocks(text: str, chunk_size: int = 1800) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] or [""]


def clean_markdown_with_stats(text: str, *, dedupe_lines: bool = True) -> tuple[str, dict[str, int]]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]

    normalized: list[str] = []
    blank = 0
    for line in lines:
        if not line:
            blank += 1
            if blank > 2:
                continue
        else:
            blank = 0
        normalized.append(line)

    line_dedupe_count = 0
    if dedupe_lines:
        deduped: list[str] = []
        prev: str | None = None
        for line in normalized:
            if line == prev:
                line_dedupe_count += 1
                continue
            deduped.append(line)
            prev = line
        normalized = deduped

    block_dedupe_count = 0
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in normalized:
        if line:
            current.append(line)
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    # 去掉重复块（连续重复或非连续重复，按块文本去重）
    seen: set[str] = set()
    deduped_blocks: list[list[str]] = []
    for block in blocks:
        key = "\n".join(block).strip()
        if not key:
            continue
        if key in seen:
            block_dedupe_count += 1
            continue
        seen.add(key)
        deduped_blocks.append(block)

    flattened: list[str] = []
    for i, block in enumerate(deduped_blocks):
        if i > 0:
            flattened.append("")
        flattened.extend(block)

    cleaned = "\n".join(flattened).strip() + "\n"
    return cleaned, {
        "line_dedupe_count": line_dedupe_count,
        "block_dedupe_count": block_dedupe_count,
    }


def clean_markdown(text: str, *, dedupe_lines: bool = True) -> str:
    return clean_markdown_with_stats(text, dedupe_lines=dedupe_lines)[0]


def build_text_block(text: str, *, rich: bool = False) -> list[dict[str, Any]]:
    blocks = []
    for chunk in split_text_blocks(text):
        if rich:
            blocks.append(
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "plain text",
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                    },
                }
            )
        else:
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                    },
                }
            )
    return blocks


def notion_list_children(token: str, page_id: str) -> list[dict[str, Any]]:
    cursor = None
    blocks: list[dict[str, Any]] = []
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = notion_request(token, "GET", f"blocks/{page_id}/children", params=params)
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return blocks


def notion_find_child_pages(token: str, parent_page_id: str) -> dict[str, str]:
    return {
        item["title"]: item["id"]
        for item in notion_find_child_pages_with_ids(token, parent_page_id)
    }


def notion_find_child_pages_with_ids(token: str, parent_page_id: str) -> list[dict[str, str]]:
    cursor = None
    pages: list[dict[str, str]] = []
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        data = notion_request(token, "GET", f"blocks/{parent_page_id}/children", params=params)
        for item in data.get("results", []):
            if item.get("type") == "child_page":
                pages.append(
                    {
                        "id": item["id"],
                        "title": item.get("child_page", {}).get("title", ""),
                        "created_time": item.get("created_time", ""),
                        "last_edited_time": item.get("last_edited_time", ""),
                    }
                )
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages


def notion_archive_block(token: str, block_id: str) -> None:
    notion_request(token, "PATCH", f"blocks/{block_id}", {"archived": True})


def notion_archive_page(token: str, page_id: str) -> None:
    notion_request(token, "PATCH", f"pages/{page_id}", {"archived": True})


def notion_clear_children(token: str, page_id: str) -> None:
    for block in notion_list_children(token, page_id):
        notion_request(token, "PATCH", f"blocks/{block['id']}", {"archived": True})


def notion_append_children(token: str, page_id: str, blocks: list[dict[str, Any]]) -> None:
    if not blocks:
        return
    for i in range(0, len(blocks), 100):
        notion_request(token, "PATCH", f"blocks/{page_id}/children", {"children": blocks[i : i + 100]})


def notion_replace_children(token: str, page_id: str, blocks: list[dict[str, Any]]) -> None:
    notion_clear_children(token, page_id)
    notion_append_children(token, page_id, blocks)


def notion_upsert_page(token: str, parent_page_id: str, title: str) -> str:
    existing = notion_find_child_pages(token, parent_page_id)
    if title in existing:
        return existing[title]
    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}],
            },
        },
    }
    data = notion_request(token, "POST", "pages", payload)
    return data["id"]


def notion_upsert_pages_in_bulk(token: str, parent_page_id: str, titles: list[str]) -> dict[str, str]:
    title_map = notion_find_child_pages(token, parent_page_id)
    for title in titles:
        if title in title_map:
            continue
        payload = {
            "parent": {"page_id": parent_page_id},
            "properties": {
                "title": {
                    "title": [{"type": "text", "text": {"content": title}}],
                },
            },
        }
        data = notion_request(token, "POST", "pages", payload)
        title_map[title] = data["id"]
    return title_map


def parse_md_docs(doc_dir: Path) -> list[Path]:
    return [p for p in sorted(doc_dir.rglob("*.md")) if p.is_file()]


def document_page_title(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = rel.parts
    if len(parts) <= 1:
        return rel.name
    return " / ".join(parts)


def collect_document_records(doc_dir: Path, *, dedupe_lines: bool) -> list[DocumentRecord]:
    records: list[DocumentRecord] = []
    for path in parse_md_docs(doc_dir):
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        cleaned_text, stats = clean_markdown_with_stats(raw, dedupe_lines=dedupe_lines)
        records.append(
            DocumentRecord(
                path=path.as_posix(),
                title=document_page_title(path, doc_dir),
                source_sha=hash_text(raw),
                cleaned_text=cleaned_text,
                cleaned_sha=hash_text(cleaned_text),
                line_dedupe_count=stats["line_dedupe_count"],
                block_dedupe_count=stats["block_dedupe_count"],
            )
        )
    return records


def parse_table_kv(line: str) -> tuple[str, str] | None:
    m = TABLE_RE.match(line)
    if not m:
        return None
    key = m.group(1).upper().strip()
    value = m.group(2).strip()
    if key in {"KEY", "VALUE", ""}:
        return None
    return key, value


def parse_inline_kv(line: str) -> tuple[str, str] | None:
    m = INLINE_KV_RE.match(line)
    if not m:
        return None
    key = m.group(1).upper().strip()
    value = m.group(2).strip()
    if not key:
        return None
    return key, value


def collect_required_tokens(repo_root: Path) -> list[str]:
    required: set[str] = set()
    for path in sorted(repo_root.rglob("*.py")):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in INVOCATION_RE.finditer(content):
            key = match.group(1).upper()
            if TOKEN_NAME_RE.fullmatch(key):
                required.add(key)
    return sorted(required)


def parse_token_inventory(token_store: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    sections: dict[str, dict[str, Any]] = {}
    source_file_by_key: dict[str, str] = {}
    if not token_store.exists():
        return sections, source_file_by_key

    current_key: str | None = None
    current_source = None

    for raw in token_store.read_text(encoding="utf-8", errors="ignore").splitlines():
        heading_match = HEADING_RE.match(raw)
        if heading_match:
            current_key = heading_match.group(1).strip().upper()
            current_source = None
            sections.setdefault(current_key, {"source": "", "value": ""})
            continue

        if not current_key:
            table_kv = parse_table_kv(raw)
            if table_kv:
                key, value = table_kv
                if not TOKEN_NAME_RE.fullmatch(key):
                    continue
                current_source = None
                sections.setdefault(key, {"source": "", "value": ""})
                sections[key]["value"] = value
                continue

            inline_kv = parse_inline_kv(raw)
            if inline_kv:
                key, value = inline_kv
                if not TOKEN_NAME_RE.fullmatch(key):
                    continue
                current_key = key
                current_source = None
                sections.setdefault(key, {"source": "", "value": ""})
                sections[key]["value"] = value
                continue
            continue

        source_match = SOURCE_RE.match(raw)
        if source_match:
            current_source = source_match.group(1).strip()
            sections[current_key]["source"] = current_source
            continue

        value_match = VALUE_RE.match(raw)
        if value_match:
            value = value_match.group(1).strip()
            if value:
                sections[current_key]["value"] = value
                if current_source:
                    source_file_by_key[current_key] = (token_store.parent / current_source).as_posix()

    for key, source in source_file_by_key.items():
        src = Path(source).expanduser()
        if not src.is_absolute():
            src = token_store.parent / source
        if not src.is_file():
            continue
        for line in src.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" in line:
                name, value = line.split("=", 1)
                if name.strip().upper() == key:
                    sections[key]["value"] = value.strip().strip('"').strip("'")
                    break

    return sections, source_file_by_key


def mask_secret(raw: str) -> str:
    value = (raw or "").strip()
    if len(value) <= 8:
        return "*" * max(len(value), 4)
    return f"{value[:4]}****{value[-4:]}"


def build_doc_blocks(
    source_paths: list[str],
    title: str,
    sha: str,
    content: str,
    *,
    merged: bool,
) -> list[dict[str, Any]]:
    lines = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"归档文档：{title}"},
                    }
                ],
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "合并模式：是" if merged else "合并模式：否"},
                    }
                ],
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "来源文件（按路径）："},
                    }
                ],
            },
        },
        {
            "object": "block",
            "type": "code",
            "code": {
                "language": "plain text",
                "rich_text": [{"type": "text", "text": {"content": "\n".join(source_paths)}}],
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"内容签名：{sha}"}}],
            },
        },
        {"object": "block", "type": "divider", "divider": {}},
    ]
    return lines + build_text_block(content, rich=True)


def build_token_blocks(
    token_map: dict[str, dict[str, Any]],
    required_tokens: list[str],
    *,
    mask_values: bool = True,
) -> tuple[list[dict[str, Any]], str]:
    present = [k for k in required_tokens if token_map.get(k, {}).get("value")]
    missing = [k for k in required_tokens if k not in present]

    rows = [
        f"已对齐 API Token（{len(present)}/{len(required_tokens)}）：",
        *[f"- {k}" for k in sorted(present)],
        "",
        "缺失 API Token：",
        *["- " + k for k in sorted(missing)],
    ]

    if not missing:
        rows.append("- 无")

    rows.append("")
    rows.append("库存明细：")
    for key in sorted(set(required_tokens) | set(token_map.keys())):
        item = token_map.get(key, {})
        value = item.get("value", "")
        src = item.get("source", "")
        if value:
            display = mask_secret(value) if mask_values else value
            suffix = "（来源：掩码）" if mask_values else "（来源：本地文档）"
            rows.append(f"{key}: {display} {suffix if src else '（来源：本地文档）'}")
        else:
            rows.append(f"{key}: <未入库>")

    text = "\n".join(rows)
    return [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "仓内 API Token 需求与库存"}}],
            },
        },
    ] + build_text_block(text, rich=True), text


def build_change_summary_blocks(summary: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    lines = [
        "DataPulse 文档同步变更摘要",
        f"同步时间：{summary['timestamp']}",
        f"扫描文档数：{summary['total_docs']}",
        f"已更新/新增：{summary['updated_docs']}；未变化：{summary['unchanged_docs']}",
        f"新增文档：{summary['added_docs']}；删除文档：{summary['removed_docs']}",
        f"清洗去重：行去重 {summary['line_dedupe_count']} 处，段落去重 {summary['block_dedupe_count']} 处",
        f"重复内容合并：{summary['merged_groups']} 组，{summary['merged_docs']} 份被合并",
        f"孤立文档页清理：{summary['cleanup_orphan_doc_pages']} 个",
        f"重复标题页清理：{summary['cleanup_duplicate_doc_pages']} 个",
    ]

    if summary["updated_paths"]:
        lines.append("")
        lines.append("变更文档：")
        lines.extend(f"- {path}" for path in summary["updated_paths"])

    if summary["merged_pages"]:
        lines.append("")
        lines.append("参与合并的页面：")
        lines.extend(f"- {name}" for name in summary["merged_pages"])

    if summary["removed_paths"]:
        lines.append("")
        lines.append("失效文档：")
        lines.extend(f"- {path}" for path in summary["removed_paths"])

    if summary["errors"]:
        lines.append("")
        lines.append("同步异常：")
        lines.extend(f"- {message}" for message in summary["errors"])

    summary_text = "\n".join(lines).strip() + "\n"
    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "DataPulse 文档同步变更摘要"}}],
            },
        },
        {
            "object": "block",
            "type": "code",
            "code": {
                "language": "plain text",
                "rich_text": [{"type": "text", "text": {"content": summary_text}}],
            },
        },
    ]
    return blocks, summary_text


def load_state(path: Path) -> SyncState:
    if not path.exists():
        return SyncState(page_id_by_path={}, sha_by_path={})
    data = json.loads(path.read_text(encoding="utf-8"))
    return SyncState(
        page_id_by_path=data.get("page_id_by_path", data.get("page_id_by_title", {})),
        sha_by_path=data.get("sha_by_path", {}),
        summary_sha=data.get("summary_sha", ""),
        token_summary_sha=data.get("token_summary_sha", ""),
    )


def save_state(path: Path, state: SyncState) -> None:
    path.write_text(
        json.dumps(
            {
                "page_id_by_path": state.page_id_by_path,
                "sha_by_path": state.sha_by_path,
                "summary_sha": state.summary_sha,
                "token_summary_sha": state.token_summary_sha,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    global REQUEST_INTERVAL_SECONDS, REQUEST_MAX_RETRIES

    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-page-id", default=DEFAULT_PARENT_PAGE_ID)
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOC_DIR))
    parser.add_argument("--token-store", default=str(DEFAULT_TOKEN_STORE))
    parser.add_argument("--state-file", default=".datapulse_notion_sync_state.json")
    parser.add_argument("--requests-per-second", default=2.5, type=float)
    parser.add_argument("--max-retries", default=REQUEST_MAX_RETRIES, type=int)
    parser.add_argument("--force-update", action="store_true")
    parser.add_argument("--no-dedupe-lines", action="store_true")
    parser.add_argument("--skip-token-page", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    parser.add_argument("--cleanup-dry-run", action="store_true")
    parser.add_argument("--cleanup-orphan-doc-pages", action="store_true")
    parser.add_argument("--cleanup-duplicate-doc-pages", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    token_store = Path(args.token_store)
    state = load_state(Path(args.state_file))
    prev_state_sha_by_path = dict(state.sha_by_path)

    dedupe_lines = not args.no_dedupe_lines
    documents = collect_document_records(docs_dir, dedupe_lines=dedupe_lines)

    repo_root = Path(__file__).resolve().parents[1]
    required_tokens = sorted(set(BASE_REQUIRED_TOKENS) | set(collect_required_tokens(repo_root)))
    token_map, _ = parse_token_inventory(token_store)

    current_paths = {doc.path for doc in documents}
    removed_paths = sorted(set(prev_state_sha_by_path.keys()) - current_paths)
    added_paths = sorted(current_paths - set(prev_state_sha_by_path.keys()))

    changed_paths = [
        doc.path
        for doc in documents
        if args.force_update or state.sha_by_path.get(doc.path) != doc.cleaned_sha
    ]

    total_line_dedupe = sum(doc.line_dedupe_count for doc in documents)
    total_block_dedupe = sum(doc.block_dedupe_count for doc in documents)

    print(f"扫描文档：{len(documents)} 个")
    print(f"识别需求 token：{len(required_tokens)} 个")
    print(f"已入库 token：{len([k for k in required_tokens if token_map.get(k, {}).get('value')])} 个")

    cleanup_dry_run_only = args.cleanup_dry_run or (
        args.dry_run and (args.cleanup_orphan_doc_pages or args.cleanup_duplicate_doc_pages)
    )
    if args.dry_run and not cleanup_dry_run_only:
        print("dry run enabled: skip network writes")
        print(f"[dry-run] 将更新 {len(changed_paths)} 个文档页")
        for path in sorted(changed_paths):
            print(f"- {Path(path).relative_to(docs_dir)}")
        return 0
    if args.dry_run and cleanup_dry_run_only:
        print("dry run enabled: skip network writes")
        print(f"[dry-run] 将更新 {len(changed_paths)} 个文档页")
        for path in sorted(changed_paths):
            print(f"- {Path(path).relative_to(docs_dir)}")

    if args.requests_per_second <= 0:
        raise SystemExit("--requests-per-second 必须大于 0")
    REQUEST_INTERVAL_SECONDS = 1.0 / args.requests_per_second
    REQUEST_MAX_RETRIES = max(0, args.max_retries)

    token = os.getenv("NOTION_TOKEN", "").strip()
    if not token:
        raise SystemExit("Missing NOTION_TOKEN")

    summary_payload: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_docs": len(documents),
        "updated_docs": 0,
        "unchanged_docs": 0,
        "added_docs": len(added_paths),
        "removed_docs": len(removed_paths),
        "line_dedupe_count": total_line_dedupe,
        "block_dedupe_count": total_block_dedupe,
        "merged_groups": 0,
        "merged_docs": 0,
        "cleanup_orphan_doc_pages": 0,
        "cleanup_duplicate_doc_pages": 0,
        "updated_paths": [],
        "merged_pages": [],
        "removed_paths": [Path(p).relative_to(docs_dir).as_posix() for p in removed_paths],
        "errors": [],
        "notion_parent_page_id": args.parent_page_id,
    }

    container_pages = notion_find_child_pages(token, args.parent_page_id)
    if DOC_TITLE_PAGE not in container_pages:
        container_pages[DOC_TITLE_PAGE] = notion_upsert_page(token, args.parent_page_id, DOC_TITLE_PAGE)
    doc_container_id = container_pages[DOC_TITLE_PAGE]

    if TOKEN_TITLE_PAGE not in container_pages:
        container_pages[TOKEN_TITLE_PAGE] = notion_upsert_page(token, args.parent_page_id, TOKEN_TITLE_PAGE)
    token_container_id = container_pages[TOKEN_TITLE_PAGE]

    if SUMMARY_PAGE_TITLE not in container_pages:
        container_pages[SUMMARY_PAGE_TITLE] = notion_upsert_page(token, args.parent_page_id, SUMMARY_PAGE_TITLE)
    summary_page_id = container_pages[SUMMARY_PAGE_TITLE]

    grouped: defaultdict[str, list[DocumentRecord]] = defaultdict(list)
    for doc in documents:
        grouped[doc.cleaned_sha].append(doc)

    merged_groups = [group for group in grouped.values() if len(group) > 1]
    summary_payload["merged_groups"] = len(merged_groups)
    summary_payload["merged_docs"] = sum(len(group) - 1 for group in merged_groups)

    if merged_groups:
        print(f"内容去重：发现 {summary_payload['merged_groups']} 组重复内容，{summary_payload['merged_docs']} 份待合并")

    titles = [
        sorted(group, key=lambda r: r.path)[0].title
        for group in grouped.values()
    ]
    titles_set = set(titles)

    records_by_title: dict[str, list[DocumentRecord]] = defaultdict(list)
    for rec in documents:
        records_by_title[rec.title].append(rec)

    child_pages = notion_find_child_pages_with_ids(token, doc_container_id)
    pages_by_title: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in child_pages:
        pages_by_title[item["title"]].append(item)

    existing_docs: dict[str, str] = {}
    cleanup_duplicate_targets: list[tuple[str, str]] = []
    cleanup_orphan_targets: list[tuple[str, str]] = []
    for title in titles_set:
        candidates = pages_by_title.get(title, [])
        if not candidates:
            existing_docs[title] = notion_upsert_page(token, doc_container_id, title)
            continue

        candidate_ids = [item["id"] for item in candidates]
        preferred = None
        for rec in records_by_title[title]:
            current_id = state.page_id_by_path.get(rec.path)
            if current_id and current_id in candidate_ids:
                preferred = current_id
                break
        if not preferred:
            preferred = candidate_ids[0]
        existing_docs[title] = preferred

        if args.cleanup_duplicate_doc_pages:
            for item in candidates:
                if item["id"] != preferred:
                    if cleanup_dry_run_only:
                        cleanup_duplicate_targets.append((title, item["id"]))
                    else:
                        notion_archive_page(token, item["id"])
                    summary_payload["cleanup_duplicate_doc_pages"] += 1

    if args.cleanup_orphan_doc_pages:
        for item in child_pages:
            if item["title"] not in titles_set:
                if cleanup_dry_run_only:
                    cleanup_orphan_targets.append((item["title"], item["id"]))
                else:
                    notion_archive_page(token, item["id"])
                summary_payload["cleanup_orphan_doc_pages"] += 1

    for rec in documents:
        state.page_id_by_path[rec.path] = existing_docs[rec.title]

    if cleanup_dry_run_only:
        print("cleanup dry-run enabled: skip cleanup writes")
        if cleanup_duplicate_targets:
            print("[dry-run] 将归档重复标题页：")
            for title, page_id in cleanup_duplicate_targets:
                print(f"- {title}: {page_id}")
        if cleanup_orphan_targets:
            print("[dry-run] 将归档孤立页：")
            for title, page_id in cleanup_orphan_targets:
                print(f"- {title}: {page_id}")
        if not cleanup_duplicate_targets and not cleanup_orphan_targets:
            print("[dry-run] 无需清理重复或孤立文档页")
        if args.emit_json:
            emit = {
                "status": "ok",
                "cleanup_plan": {
                    "duplicate_targets": cleanup_duplicate_targets,
                    "orphan_targets": cleanup_orphan_targets,
                },
                "summary": summary_payload,
            }
            print(json.dumps(emit, ensure_ascii=False, indent=2))
        return 0

    for group in sorted(grouped.values(), key=lambda g: sorted(r.path for r in g)[0]):
        group = sorted(group, key=lambda rec: rec.path)
        representative = group[0]
        title = representative.title
        merged = len(group) > 1

        page_id = state.page_id_by_path.get(representative.path) or existing_docs[title]

        for rec in group:
            state.page_id_by_path[rec.path] = page_id

        group_changed = args.force_update or any(
            args.force_update or state.sha_by_path.get(rec.path) != rec.cleaned_sha
            for rec in group
        )

        if group_changed:
            summary_payload["updated_docs"] += len(group)
            summary_payload["updated_paths"].append(Path(representative.path).relative_to(docs_dir).as_posix())
            if merged:
                summary_payload["merged_pages"].append(title)

            blocks = build_doc_blocks(
                source_paths=[Path(rec.path).relative_to(docs_dir).as_posix() for rec in group],
                title=title,
                sha=representative.cleaned_sha,
                content=representative.cleaned_text,
                merged=merged,
            )
            notion_replace_children(token, page_id, blocks)
            for rec in group:
                state.sha_by_path[rec.path] = rec.cleaned_sha

    summary_payload["unchanged_docs"] = max(0, len(documents) - len(changed_paths))

    # token台账 idempotent
    if not args.skip_token_page:
        token_blocks, token_text = build_token_blocks(token_map, required_tokens, mask_values=False)
        token_summary_sha = hash_text(token_text)
        if args.force_update or token_summary_sha != state.token_summary_sha:
            notion_replace_children(token, token_container_id, token_blocks)
            state = SyncState(
                page_id_by_path=state.page_id_by_path,
                sha_by_path=state.sha_by_path,
                summary_sha=state.summary_sha,
                token_summary_sha=token_summary_sha,
            )

    # 保留快照（去重后的签名）与变更摘要
    summary_blocks, summary_text = build_change_summary_blocks(summary_payload)
    new_summary_sha = hash_text(summary_text)
    if args.force_update or new_summary_sha != state.summary_sha:
        notion_replace_children(token, summary_page_id, summary_blocks)
        state = SyncState(
            page_id_by_path=state.page_id_by_path,
            sha_by_path=state.sha_by_path,
            summary_sha=new_summary_sha,
            token_summary_sha=state.token_summary_sha,
        )

    # 清理本地不存在文件的哈希和 page 映射（保留 Notion 页面）
    for stale in sorted(set(state.sha_by_path.keys()) - set(doc.path for doc in documents)):
        state.sha_by_path.pop(stale, None)
        state.page_id_by_path.pop(stale, None)

    save_state(Path(args.state_file), state)

    if args.emit_json:
        emit = {
            "status": "ok",
            "summary": summary_payload,
            "state": {
                "path_count": len(state.sha_by_path),
                "summary_sha": state.summary_sha,
                "token_summary_sha": state.token_summary_sha,
            },
        }
        print(json.dumps(emit, ensure_ascii=False, indent=2))

    print(f"同步完成：文档更新 {summary_payload['updated_docs']} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
