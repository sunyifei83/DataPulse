"""DataPulse command line entry."""

from __future__ import annotations

import argparse
import asyncio
import json

from datapulse.reader import DataPulseReader
from datapulse.tools.session import login_platform, supported_platforms


def _print_list(items, limit: int = 20):
    if not items:
        print("📦 Inbox is empty")
        return

    print(f"📦 {len(items)} item(s)\n")
    for idx, item in enumerate(items[:limit], 1):
        score = f"{item.confidence:.3f}"
        print(f"{idx:2d}. [{item.source_type.value}] {item.title[:55]} - {score}")
        print(f"    {item.url}")


def _print_sources(sources, include_inactive: bool = False, public_only: bool = True):
    for source in sources:
        status = "active" if source.get("is_active", True) else "inactive"
        visibility = "public" if source.get("is_public", True) else "private"
        print(f"{source.get('id')}: {source.get('name')} | {source.get('source_type')} | {status}/{visibility}")


def _print_packs(packs):
    for pack in packs:
        count = len(pack.get("source_ids", []))
        print(f"{pack.get('slug')}: {pack.get('name')} | {count} source(s)")


def _normalize_csv_ids(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="DataPulse Intelligence Hub")
    parser.add_argument("inputs", nargs="*", help="URLs or commands")
    parser.add_argument("--batch", nargs="+", help="Process a batch of URLs")
    parser.add_argument(
        "--login",
        choices=supported_platforms(),
        help="Capture browser login state for platform (xhs, wechat)",
    )
    parser.add_argument("--source-profile", default="default", help="Source profile for feed/subscription ops")
    parser.add_argument("--list-sources", action="store_true", help="List source catalog entries")
    parser.add_argument("--list-packs", action="store_true", help="List source packs")
    parser.add_argument("--include-inactive-sources", action="store_true", help="Include inactive sources")
    parser.add_argument("--public-sources-only", action="store_true", help="Only list public sources")
    parser.add_argument("--resolve-source", metavar="URL", help="Resolve source metadata for a URL")
    parser.add_argument("--source-subscribe", metavar="SOURCE_ID", help="Subscribe profile source")
    parser.add_argument("--source-unsubscribe", metavar="SOURCE_ID", help="Unsubscribe profile source")
    parser.add_argument("--install-pack", metavar="PACK_SLUG", help="Install source pack to profile")
    parser.add_argument("--source-ids", help="Comma separated source IDs for query_feed")
    parser.add_argument("--query-feed", action="store_true", help="Print JSON feed output")
    parser.add_argument("--query-rss", action="store_true", help="Print RSS feed output")
    parser.add_argument("--query-atom", action="store_true", help="Print Atom 1.0 feed output")
    parser.add_argument("--digest", action="store_true", help="Build curated digest")
    parser.add_argument("--top-n", type=int, default=3, help="Number of primary stories in digest")
    parser.add_argument("--secondary-n", type=int, default=7, help="Number of secondary stories in digest")
    parser.add_argument("--list", action="store_true", help="List inbox")
    parser.add_argument("--clear", action="store_true", help="Clear inbox")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Filter by confidence")
    parser.add_argument("--limit", type=int, default=20, help="List limit")
    # Jina search options
    parser.add_argument("--search", metavar="QUERY", help="Search the web via Jina")
    parser.add_argument("--site", action="append", metavar="DOMAIN", help="Restrict search to domain (repeatable)")
    parser.add_argument("--search-limit", type=int, default=5, help="Max search results (default 5)")
    parser.add_argument("--no-fetch", action="store_true", help="Skip full content fetch for search results")
    # Jina reader options
    parser.add_argument("--target-selector", metavar="CSS", help="CSS selector for targeted extraction")
    parser.add_argument("--no-cache", action="store_true", help="Bypass Jina cache")
    parser.add_argument("--with-alt", action="store_true", help="Enable AI image descriptions via Jina")
    args = parser.parse_args()

    reader = DataPulseReader()

    if args.list:
        _print_list(reader.list_memory(limit=args.limit, min_confidence=args.min_confidence), limit=args.limit)
        return

    if args.login:
        try:
            path = login_platform(args.login)
            print(f"✅ Saved {args.login} session: {path}")
        except KeyboardInterrupt:
            print("⚠️ Login cancelled.")
        except Exception as exc:
            print(f"❌ Login failed: {exc}")
        return

    if args.clear:
        inbox_path = reader.inbox.path
        if inbox_path.exists():
            inbox_path.write_text("[]", encoding="utf-8")
            print(f"✅ Cleared inbox: {inbox_path}")
        else:
            print("ℹ️ Inbox already empty")
        return

    if args.list_sources:
        public_only = True
        if args.include_inactive_sources:
            public_only = bool(args.public_sources_only)
        sources = reader.list_sources(
            include_inactive=args.include_inactive_sources,
            public_only=public_only,
        )
        if not sources:
            print("No source in catalog.")
        else:
            print(f"📚 Sources: {len(sources)}")
            _print_sources(sources)
        return

    if args.list_packs:
        packs = reader.list_packs(public_only=True)
        if not packs:
            print("No source pack in catalog.")
        else:
            print(f"📦 Source packs: {len(packs)}")
            _print_packs(packs)
        return

    if args.resolve_source:
        print(json.dumps(reader.resolve_source(args.resolve_source), ensure_ascii=False, indent=2))
        return

    if args.source_subscribe:
        ok = reader.subscribe_source(args.source_subscribe, profile=args.source_profile)
        print("✅ subscribed" if ok else "⚠️ already subscribed or invalid source")
        return

    if args.source_unsubscribe:
        ok = reader.unsubscribe_source(args.source_unsubscribe, profile=args.source_profile)
        print("✅ unsubscribed" if ok else "⚠️ source not found in subscription")
        return

    if args.install_pack:
        count = reader.install_pack(args.install_pack, profile=args.source_profile)
        print(f"✅ installed {count} source(s) from pack")
        return

    if args.query_feed:
        payload = reader.build_json_feed(
            profile=args.source_profile,
            source_ids=_normalize_csv_ids(args.source_ids),
            limit=args.limit,
            min_confidence=args.min_confidence,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.query_rss:
        print(
            reader.build_rss_feed(
                profile=args.source_profile,
                source_ids=_normalize_csv_ids(args.source_ids),
                limit=args.limit,
                min_confidence=args.min_confidence,
            )
        )
        return

    if args.query_atom:
        print(
            reader.build_atom_feed(
                profile=args.source_profile,
                source_ids=_normalize_csv_ids(args.source_ids),
                limit=args.limit,
                min_confidence=args.min_confidence,
            )
        )
        return

    if args.digest:
        payload = reader.build_digest(
            profile=args.source_profile,
            source_ids=_normalize_csv_ids(args.source_ids),
            top_n=args.top_n,
            secondary_n=args.secondary_n,
            min_confidence=args.min_confidence,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.search:
        async def run_search() -> None:
            results = await reader.search(
                args.search,
                sites=args.site or None,
                limit=args.search_limit,
                fetch_content=not args.no_fetch,
                min_confidence=args.min_confidence,
            )
            if not results:
                print("No search results above confidence threshold")
                return
            print(f"Found {len(results)} result(s) for: {args.search}\n")
            for idx, item in enumerate(results, 1):
                sample = (item.content or "")[:140].replace("\n", " ")
                print(f"{idx}. {item.title}")
                print(f"   confidence: {item.confidence:.3f}  score: {item.score}")
                print(f"   url: {item.url}")
                print(f"   sample: {sample}\n")

        asyncio.run(run_search())
        return

    # Apply Jina reader options if provided
    if args.target_selector or args.no_cache or args.with_alt:
        from datapulse.collectors.jina import JinaCollector

        jina_opts = {}
        if args.target_selector:
            jina_opts["target_selector"] = args.target_selector
        if args.no_cache:
            jina_opts["no_cache"] = True
        if args.with_alt:
            jina_opts["with_alt"] = True
        # Replace the Jina collector in the pipeline with the enhanced one
        enhanced_jina = JinaCollector(**jina_opts)
        for i, p in enumerate(reader.router.parsers):
            if getattr(p, "name", "") == "jina":
                reader.router.parsers[i] = enhanced_jina
                break

    targets = []
    if args.batch:
        targets.extend(args.batch)
    else:
        targets.extend([x for x in args.inputs if "://" in x or x.startswith("www.")])

    if not targets:
        print("Usage:\n  datapulse <url> [urls...]\n  datapulse --batch <url1> <url2>\n  datapulse --list\n  datapulse --search QUERY\n")
        return

    async def run() -> None:
        results = await reader.read_batch(targets, min_confidence=args.min_confidence)
        if not results:
            print("No result above confidence threshold")
            return
        for idx, item in enumerate(results, 1):
            sample = (item.content or "")[:140].replace("\n", " ")
            print(f"\n{idx}. [{item.source_type.value}] {item.title}")
            print(f"   confidence: {item.confidence:.3f}")
            print(f"   url: {item.url}")
            print(f"   sample: {sample}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
