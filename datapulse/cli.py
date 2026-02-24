"""DataPulse command line entry."""

from __future__ import annotations

import argparse
import asyncio

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


def main() -> None:
    parser = argparse.ArgumentParser(description="DataPulse Intelligence Hub")
    parser.add_argument("inputs", nargs="*", help="URLs or commands")
    parser.add_argument("--batch", nargs="+", help="Process a batch of URLs")
    parser.add_argument(
        "--login",
        choices=supported_platforms(),
        help="Capture browser login state for platform (xhs, wechat)",
    )
    parser.add_argument("--list", action="store_true", help="List inbox")
    parser.add_argument("--clear", action="store_true", help="Clear inbox")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Filter by confidence")
    parser.add_argument("--limit", type=int, default=20, help="List limit")
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
        path = reader.inbox.path
        if path.exists():
            path.write_text("[]", encoding="utf-8")
            print(f"✅ Cleared inbox: {path}")
        else:
            print("ℹ️ Inbox already empty")
        return

    targets = []
    if args.batch:
        targets.extend(args.batch)
    else:
        targets.extend([x for x in args.inputs if "://" in x or x.startswith("www.")])

    if not targets:
        print("Usage:\n  datapulse <url> [urls...]\n  datapulse --batch <url1> <url2>\n  datapulse --list\n")
        return

    async def run() -> None:
        results = await reader.read_batch(targets, min_confidence=args.min_confidence)
        if not results:
            print("⚠️ No result above confidence threshold")
            return
        for idx, item in enumerate(results, 1):
            print(f"\n{idx}. [{item.source_type.value}] {item.title}")
            print(f"   confidence: {item.confidence:.3f}")
            print(f"   url: {item.url}")
            print(f"   sample: {(item.content or '')[:140].replace('\n', ' ')}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
