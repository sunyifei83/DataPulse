#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime
from typing import Any

from datapulse.reader import DataPulseReader


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "")) if os.getenv(name) is not None else default
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "")) if os.getenv(name) is not None else default
    except (TypeError, ValueError):
        return default


HIGH_CONF_THRESHOLD = _env_float("DATAPULSE_XHS_HIGH_CONFIDENCE", 0.80)
MEDIUM_CONF_THRESHOLD = _env_float("DATAPULSE_XHS_MEDIUM_CONFIDENCE", 0.65)
HIGH_SCORE_THRESHOLD = _env_int("DATAPULSE_XHS_HIGH_SCORE", 70)
MEDIUM_SCORE_THRESHOLD = _env_int("DATAPULSE_XHS_MEDIUM_SCORE", 50)


def classify_tier(confidence: float, score: int) -> tuple[str, str]:
    """Return (tier, rationale) by combining confidence + score."""
    if confidence >= HIGH_CONF_THRESHOLD and score >= HIGH_SCORE_THRESHOLD:
        return (
            "高置信",
            f"confidence >= {HIGH_CONF_THRESHOLD:.2f} 且 score >= {HIGH_SCORE_THRESHOLD}",
        )
    if confidence >= MEDIUM_CONF_THRESHOLD and score >= MEDIUM_SCORE_THRESHOLD:
        return (
            "中置信",
            f"confidence >= {MEDIUM_CONF_THRESHOLD:.2f} 且 score >= {MEDIUM_SCORE_THRESHOLD}",
        )
    return "低置信", f"未达到高/中置信阈值"


def fmt_snippet(text: str, max_chars: int = 200) -> str:
    txt = (text or "").replace("\n", " ").strip()
    if len(txt) <= max_chars:
        return txt
    return txt[: max_chars - 1] + "…"


def get_engagement(item: Any) -> dict[str, int]:
    metrics = {}
    raw_metrics = getattr(item, "extra", {}).get("engagement")
    if isinstance(raw_metrics, dict):
        for key, value in raw_metrics.items():
            try:
                metrics[key] = int(value)
            except (TypeError, ValueError):
                continue
    return metrics


def engagement_weight(item: Any) -> int:
    return sum(get_engagement(item).values())


def _to_json_record(item: Any, search_query: str) -> dict[str, Any]:
    return {
        "index": item.quality_rank or 0,
        "title": item.title,
        "url": item.url,
        "source_name": item.source_name,
        "source_type": item.source_type.value if getattr(item, "source_type", None) else "",
        "parser": item.parser,
        "confidence": item.confidence,
        "score": item.score,
        "confidence_factors": item.confidence_factors,
        "tags": item.tags,
        "sample": fmt_snippet(item.content or "", 400),
        "engagement": get_engagement(item),
        "search": {
            "provider": item.extra.get("search_provider", ""),
            "mode": item.extra.get("search_mode", ""),
            "sources": item.extra.get("search_sources", []),
            "source_count": item.extra.get("search_source_count", 0),
            "cross_validation": item.extra.get("search_cross_validation", {}),
            "audit": item.extra.get("search_audit", {}),
        },
        "score_breakdown": item.extra.get("score_breakdown", {}),
        "metadata": {
            "search_query": search_query,
            "fetched_at": item.fetched_at,
            "quality_rank": item.quality_rank,
            "confidence_factors": item.confidence_factors,
            "tier": item.extra.get("xhs_tier"),
            "tier_rationale": item.extra.get("xhs_tier_rationale"),
        },
    }


async def run_xhs_search(query: str, limit: int, min_confidence: float) -> list[Any]:
    reader = DataPulseReader()
    return await reader.search(
        query,
        platform="xhs",
        limit=limit,
        fetch_content=True,
        min_confidence=min_confidence,
        provider="multi",
        mode="multi",
    )


def print_human_report(
    query: str,
    items: list[Any],
    selected_index: int,
    searched_at: str,
    output_selected: bool,
) -> None:
    print(f"DataPulse xhs 复核报告")
    print(f"生成时间: {searched_at}")
    print(f"目标查询: {query}")
    if items:
        print(f"平台模式: xhs | provider=multi | mode=multi | first-item-confidence={items[0].confidence:.3f}")
    print(f"候选条目: {len(items)}")
    print("-" * 72)

    if not items:
        print("未检出符合阈值的结果。可尝试降低 --min-confidence。")
        return

    for idx, item in enumerate(items, 1):
        tier, tier_reason = classify_tier(item.confidence, int(item.score))
        item.extra["xhs_tier"] = tier
        item.extra["xhs_tier_rationale"] = tier_reason
        confidence_factors = ",".join(item.confidence_factors)
        score_breakdown = item.extra.get("score_breakdown", {})

        print(f"{idx:>2d}. [{tier}] {item.title}")
        print(f"    URL: {item.url}")
        print(
            f"    置信度: {item.confidence:.3f} | 评分: {item.score} | "
            f"解析器: {item.parser} | 来源: {item.source_name}"
        )
        print(f"    判定条件: {tier_reason}")
        print(f"    置信度因素: {confidence_factors or 'none'}")
        if score_breakdown:
            print(
                "    score_breakdown: "
                f"conf={score_breakdown.get('confidence')} "
                f"authority={score_breakdown.get('authority')} "
                f"corroboration={score_breakdown.get('corroboration')} "
                f"recency={score_breakdown.get('recency')} "
                f"cross_validation={score_breakdown.get('cross_validation', 0)} "
                f"source_diversity={score_breakdown.get('source_diversity', 0)}"
            )
        if item.extra.get("search_sources"):
            print(f"    search_sources: {','.join(item.extra['search_sources'])}")
        engagement = get_engagement(item)
        if engagement:
            print(f"    engagement: {engagement}")
        print(f"    摘要: {fmt_snippet(item.content or '', 220)}")
        if idx == selected_index:
            print("    >>> 推荐复核项 <<<")
        print("-" * 72)

    if output_selected:
        selected = items[selected_index - 1]
        print("\n复核项正文（截取前 1200 字）:")
        print(fmt_snippet(selected.content or "", 1200))
        print(f"正文长度: {len(selected.content or '')} 字符")
        print(f"交叉验证: {bool(selected.extra.get('search_cross_validation'))}")


async def run(args: argparse.Namespace) -> int:
    searched_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    items = await run_xhs_search(args.query, limit=args.limit, min_confidence=args.min_confidence)
    if not items:
        if args.json:
            payload = {
                "ok": False,
                "reason": "no_items",
                "query": args.query,
                "platform": "xhs",
                "provider": "multi",
                "mode": "multi",
                "searched_at": searched_at,
                "items": [],
                "selected_index": None,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=args.json_indent))
            return 1
        print_human_report(args.query, [], 0, searched_at, False)
        return 1

    if args.prefer_engagement:
        items = sorted(
            items,
            key=lambda item: (
                engagement_weight(item),
                item.score,
                item.confidence,
            ),
            reverse=True,
        )
    else:
        items = sorted(
            items,
            key=lambda item: (item.score, item.confidence),
            reverse=True,
        )

    selected_index = max(1, min(len(items), args.select))

    for idx, item in enumerate(items, 1):
        item.quality_rank = idx

    if args.json:
        payload = {
            "ok": True,
            "query": args.query,
            "platform": "xhs",
            "provider": "multi",
            "mode": "multi",
            "searched_at": searched_at,
            "select_rule": "engagement_desc_then_score_desc" if args.prefer_engagement else "score_desc",
            "items": [_to_json_record(item, args.query) for item in items],
            "selected_index": selected_index,
            "selected": _to_json_record(items[selected_index - 1], args.query),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=args.json_indent))
        return 0

    print_human_report(
        args.query,
        items,
        selected_index=selected_index,
        searched_at=searched_at,
        output_selected=not args.no_content_print,
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate readable xhs quality report for openclaw-related results.")
    parser.add_argument("--query", default="openclaw", help="Search query, default: openclaw")
    parser.add_argument("--limit", type=int, default=8, help="Number of search candidates")
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="最低置信过滤阈值",
    )
    parser.add_argument(
        "--select",
        type=int,
        default=1,
        help="指定复核条目序号（按复核排序）",
    )
    parser.add_argument(
        "--prefer-engagement",
        action="store_true",
        help="优先按 engagement 指标排序（无 engagement 时回退 score）",
    )
    parser.add_argument(
        "--no-content-print",
        action="store_true",
        help="不打印正文内容，仅打印摘要与评分摘要",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出机器可读 JSON",
    )
    parser.add_argument("--json-indent", type=int, default=2, help="JSON 缩进（默认 2）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exit_code = asyncio.run(run(args))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
