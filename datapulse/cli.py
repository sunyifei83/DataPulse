"""DataPulse command line entry."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import datapulse
from datapulse.core.config import SearchGatewayConfig
from datapulse.reader import DataPulseReader
from datapulse.tools.session import login_platform, supported_platforms

_GITHUB_RELEASES_API = "https://api.github.com/repos/sunyifei83/DataPulse/releases/latest"
_GITHUB_REPO = "https://github.com/sunyifei83/DataPulse"


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


_FIX_COMMANDS_BY_COLLECTOR = {
    "xhs": ["datapulse --login xhs"],
    "wechat": ["datapulse --login wechat"],
    "telegram": [
        'pip install -e ".[telegram]"',
        "export TG_API_ID=<your_tg_api_id>",
        "export TG_API_HASH=<your_tg_api_hash>",
    ],
    "jina": ["export JINA_API_KEY=<your_jina_api_key>"],
    "generic": ["pip install trafilatura"],
    "youtube": [
        "pip install -e \".[youtube]\"",
        "export GROQ_API_KEY=<your_groq_api_key>",
    ],
    "twitter": ["curl -I https://api.fxtwitter.com"],
}


def _search_gateway_defaults() -> dict[str, tuple[object, object, str]]:
    """Collect effective and default SearchGateway values for quick diagnostics."""

    effective = SearchGatewayConfig.load()
    default = SearchGatewayConfig()
    return {
        "DATAPULSE_SEARCH_TIMEOUT": (
            effective.timeout_seconds,
            default.timeout_seconds,
            "search timeout (seconds)",
        ),
        "DATAPULSE_SEARCH_RETRY_ATTEMPTS": (
            effective.retry_attempts,
            default.retry_attempts,
            "retry attempts",
        ),
        "DATAPULSE_SEARCH_RETRY_BASE_DELAY": (
            effective.retry_base_delay,
            default.retry_base_delay,
            "retry base delay (s)",
        ),
        "DATAPULSE_SEARCH_RETRY_MAX_DELAY_SECONDS": (
            effective.retry_max_delay,
            default.retry_max_delay,
            "retry max delay (s)",
        ),
        "DATAPULSE_SEARCH_RETRY_BACKOFF": (
            effective.retry_backoff_factor,
            default.retry_backoff_factor,
            "retry backoff factor",
        ),
        "DATAPULSE_SEARCH_RETRY_RESPECT_RETRY_AFTER": (
            effective.retry_respect_retry_after,
            default.retry_respect_retry_after,
            "respect Retry-After",
        ),
        "DATAPULSE_SEARCH_CB_FAILURE_THRESHOLD": (
            effective.breaker_failure_threshold,
            default.breaker_failure_threshold,
            "circuit breaker failure threshold",
        ),
        "DATAPULSE_SEARCH_CB_RECOVERY_TIMEOUT": (
            effective.breaker_recovery_timeout,
            default.breaker_recovery_timeout,
            "circuit breaker recovery timeout (s)",
        ),
        "DATAPULSE_SEARCH_CB_RATE_LIMIT_WEIGHT": (
            effective.breaker_rate_limit_weight,
            default.breaker_rate_limit_weight,
            "circuit breaker rate-limit weight",
        ),
        "DATAPULSE_SEARCH_PROVIDER_PRECEDENCE": (
            ",".join(effective.provider_preference),
            ",".join(default.provider_preference),
            "provider preference",
        ),
    }


def _format_env_value(value: str | None) -> str:
    if value is None:
        return ""
    text = value.strip()
    if not text:
        return "<empty>"
    if len(text) <= 28:
        return text
    return f"{text[:22]}..."


def _collect_fix_commands(collector_name: str, setup_hint: str) -> list[str]:
    commands: list[str] = []
    commands.extend(_FIX_COMMANDS_BY_COLLECTOR.get(collector_name, []))

    run_hints = re.findall(r"Run:\s*([^;\n]+)", setup_hint, flags=re.IGNORECASE)
    if run_hints:
        commands.extend([h.strip() for h in run_hints])

    for match in re.findall(r"Set\s+([A-Z0-9_]+(?:\s+and\s+[A-Z0-9_]+)*)", setup_hint, flags=re.IGNORECASE):
        for env_name in re.findall(r"[A-Z0-9_]+", match):
            if env_name:
                commands.append(f"export {env_name}=<{env_name.lower()}>")

    pip_hints = re.findall(r"pip\s+install\s+[^;\n]+", setup_hint, flags=re.IGNORECASE)
    if pip_hints:
        commands.extend([h.strip() for h in pip_hints])

    out: list[str] = []
    seen: set[str] = set()
    for cmd in commands:
        if cmd and cmd not in seen:
            seen.add(cmd)
            out.append(cmd)

    return out


def _print_doctor_report(report: dict[str, list[dict[str, str | bool]]]) -> None:
    tier_labels = {
        "tier_0": "Zero-config",
        "tier_1": "Network / Free",
        "tier_2": "Needs Setup",
    }

    for tier_key in ("tier_0", "tier_1", "tier_2"):
        entries = report.get(tier_key, [])
        if not entries:
            continue
        print(f"\n  {tier_labels[tier_key]} (tier {tier_key[-1]})")
        print(f"  {'─' * 50}")
        for e in entries:
            status = e.get("status", "ok")
            icon = "[OK]" if status == "ok" else "[WARN]" if status == "warn" else "[ERR]"
            name = e.get("name", "?")
            msg = e.get("message", "")
            hint = e.get("setup_hint", "")
            print(f"  {icon:6s} {name:<14s} {msg}")
            if hint:
                print(f"         Hint: {hint}")

            if status != "ok":
                commands = _collect_fix_commands(str(name), str(hint))
                if commands:
                    print("         建议执行：")
                    for cmd in commands:
                        print(f"           - {cmd}")

    print("\nSearchGateway runtime defaults:")
    for env_name, (value, default, desc) in _search_gateway_defaults().items():
        marker = "default" if value == default else "override"
        print(f"  - {env_name} = {value} ({desc}, {marker})")


def _print_config_check() -> None:
    print("=== DataPulse Config Check ===")
    print("\n1) Must-have environment variables")
    print("   - None (bootstrap is runnable without mandatory env variables)")

    print("\n2) Optional environment variables")

    # Search provider keys (at least one is enough for robust search)
    has_jina = bool(os.getenv("JINA_API_KEY", "").strip())
    has_tavily = bool(os.getenv("TAVILY_API_KEY", "").strip())
    if has_jina and has_tavily:
        print("   [OK] Search keys: JINA_API_KEY + TAVILY_API_KEY")
    elif has_jina or has_tavily:
        print("   [WARN] Search keys: only one search key is set")
    else:
        print("   [WARN] Search keys: neither JINA_API_KEY nor TAVILY_API_KEY set")
        print("         Recommended fix:")
        print("           - export JINA_API_KEY=<your_jina_api_key>")
        print("           - export TAVILY_API_KEY=<your_tavily_api_key>")

    # Telegram credentials
    has_tg_id = bool(os.getenv("TG_API_ID", "").strip())
    has_tg_hash = bool(os.getenv("TG_API_HASH", "").strip())
    if has_tg_id and has_tg_hash:
        print("   [OK] Telegram credentials: TG_API_ID + TG_API_HASH")
    else:
        print("   [WARN] Telegram credentials: TG_API_ID / TG_API_HASH")
        print("         Recommended fix:")
        print("           - export TG_API_ID=<your_tg_api_id>")
        print("           - export TG_API_HASH=<your_tg_api_hash>")

    # General optional keys (display current/placeholder for fast onboarding)
    optional_envs = [
        "FIRECRAWL_API_KEY",
        "GROQ_API_KEY",
        "NITTER_INSTANCES",
        "FXTWITTER_API_URL",
        "DATAPULSE_SESSION_DIR",
        "DATAPULSE_BATCH_CONCURRENCY",
        "DATAPULSE_MIN_CONFIDENCE",
        "DATAPULSE_LOG_LEVEL",
    ]

    for env_name in optional_envs:
        present = _format_env_value(os.getenv(env_name, ""))
        status = "[OK]" if present not in ("", "<empty>") else "[WARN]"
        print(f"   {status} {env_name}: {present or 'not set'}")

    print("\nSearchGateway tuning (effective / default):")
    for env_name, (value, default, desc) in _search_gateway_defaults().items():
        marker = "default" if value == default else "override"
        print(f"   - {env_name}: {value} ({desc}, {marker})")



def _normalize_csv_ids(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _version_tuple(version: str) -> tuple[int, ...]:
    cleaned = (version or "").lstrip("vV").strip()
    parts = [int(part) for part in re.findall(r"\d+", cleaned)]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _fetch_latest_release_tag() -> tuple[str | None, str | None]:
    try:
        request = Request(
            _GITHUB_RELEASES_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "datapulse-cli",
            },
        )
        with urlopen(request, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
            latest_tag = payload.get("tag_name")
            if isinstance(latest_tag, str):
                return latest_tag.strip(), None
            return None, "GitHub release API did not return tag_name"
    except (HTTPError, URLError, ValueError, TimeoutError, OSError) as exc:
        return None, str(exc)


def _print_version() -> None:
    print(f"DataPulse v{datapulse.__version__}")


def _print_update_status() -> None:
    current = datapulse.__version__
    latest_tag, error = _fetch_latest_release_tag()

    print(f"Current version: v{current}")
    if not latest_tag:
        print("Latest version: unavailable")
        if error:
            print(f"Update check failed: {error}")
        return

    latest = latest_tag.lstrip("vV")
    print(f"Latest version: v{latest}")
    if _version_tuple(latest) <= _version_tuple(current):
        print("✅ Already up to date")
        return

    print("🔔 Update available")
    print("   Recommended: datapulse --self-update")


def _run_self_update() -> None:
    current = datapulse.__version__
    latest_tag, error = _fetch_latest_release_tag()
    if not latest_tag:
        print("❌ Failed to check latest release before update")
        if error:
            print(f"   Detail: {error}")
        return

    latest = latest_tag.lstrip("vV")
    print(f"Current version: v{current}")
    print(f"Latest version: v{latest}")

    if _version_tuple(latest) <= _version_tuple(current):
        print("✅ Already up to date, no update needed")
        return

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        f"git+{_GITHUB_REPO}@{latest_tag}",
    ]
    print("🚀 Running update command:")
    print(f"   {' '.join(shlex.quote(part) for part in command)}")
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        print(f"❌ Update failed: {exc}")
    except subprocess.CalledProcessError as exc:
        print(f"❌ Update failed with exit code {exc.returncode}")
        print("   You may manually run:")
        print(f"   {sys.executable} -m pip install --upgrade 'git+{_GITHUB_REPO}@{latest_tag}'")
    else:
        print("✅ Update command completed. Please restart your CLI session.")


def _load_skill_manifest() -> dict[str, Any]:
    manifest_path = Path(__file__).resolve().parent.parent / "datapulse_skill" / "manifest.json"
    if not manifest_path.exists():
        return {}

    try:
        content = manifest_path.read_text(encoding="utf-8")
        payload: Any = json.loads(content)
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}
    return {}


def _collect_mcp_tool_contract() -> list[dict[str, Any]]:
    try:
        from datapulse import mcp_server

        app = mcp_server._LocalMCP("datapulse")
        mcp_server._register_tools(app)
        contract: list[dict[str, Any]] = []
        for item in sorted(app._tool_metadata(), key=lambda x: x["name"]):
            input_schema = item.get("inputSchema", {})
            props = input_schema.get("properties", {})
            required = set(input_schema.get("required", []) or [])
            args = sorted(props) if isinstance(props, dict) else []
            contract.append(
                {
                    "name": item.get("name"),
                    "description": item.get("description", ""),
                    "required_args": sorted(required),
                    "optional_args": [arg for arg in args if arg not in required],
                }
            )
        return contract
    except Exception:
        return []


def _print_skill_contract() -> None:
    manifest = _load_skill_manifest()
    mcp_tools = _collect_mcp_tool_contract()

    contract: dict[str, Any] = {
        "name": manifest.get("name", "DataPulse"),
        "description": manifest.get("description", "Cross-platform data intake and confidence-aware workflow."),
        "version": datapulse.__version__,
        "entry_points": {
            "cli": "datapulse",
            "mcp": "python3 -m datapulse.mcp_server",
            "skill": "datapulse_skill",
        },
        "agent_triggers": manifest.get("triggers", []),
        "capabilities": manifest.get("capabilities", []),
        "memory_path": manifest.get("memory_path"),
        "arguments": {
            "flags": [
                "--search / -s",
                "--trending / -T",
                "--batch / -b",
                "--entities",
                "--doctor",
                "--config-check",
                "--troubleshoot",
                "--skill-contract",
                "--check-update",
                "--self-update",
                "--version",
            ],
            "env": {
                "DATAPULSE_MIN_CONFIDENCE": "Global minimum confidence",
                "DATAPULSE_BATCH_CONCURRENCY": "Read concurrency override",
                "DATAPULSE_LOG_LEVEL": "Log verbosity",
            },
        },
        "mcp_tools": mcp_tools,
        "recommended_workflows": [
            "for ingestion of URLs: datapulse --batch",
            "for discovery: datapulse --search",
            "for source governance: --list-sources/--list-packs/--query-feed",
            "for health checks: --doctor / --troubleshoot",
        ],
    }

    print(json.dumps(contract, ensure_ascii=False, indent=2))


def _print_troubleshoot_report(
    report: dict[str, list[dict[str, str | bool]]],
    target: str | None = None,
) -> None:
    target_norm = (target or "").strip().lower()
    filtered: list[tuple[str, dict[str, str | bool]]] = []
    found_target = False

    for tier_key, entries in report.items():
        for entry in entries:
            name = str(entry.get("name", "")).strip()
            if target and name.lower() != target_norm:
                continue
            status = str(entry.get("status", "unknown"))
            if target and status:
                found_target = True
            if status != "ok":
                filtered.append((tier_key, entry))

    if target and not found_target:
        print(f"⚠️  No collector named '{target}' in doctor report")
        return

    print("🩺 DataPulse Troubleshoot")
    if not filtered:
        if target:
            print(f"✅ Collector '{target}' is healthy")
        else:
            print("✅ No failing collectors found in current environment")
        return

    for tier_key, entry in filtered:
        name = str(entry.get("name", "unknown"))
        status = str(entry.get("status", "warn"))
        msg = str(entry.get("message", "")).strip()
        hint = str(entry.get("setup_hint", "")).strip()

        print(f"- {name} [{tier_key}] ({status})")
        if msg:
            print(f"  message: {msg}")
        if hint:
            print(f"  hint: {hint}")
        commands = _collect_fix_commands(name, hint)
        if commands:
            print("  suggested commands:")
            for cmd in commands:
                print(f"    - {cmd}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DataPulse Intelligence Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nScenario snippets:\n"
            "A) Parse one URL:          datapulse <url>\n"
            "B) Parse URL batch:         datapulse --batch <url1> <url2>\n"
            "C) Web search:              datapulse --search <query> [--search-limit N]\n"
            "D) Trending topics:         datapulse --trending [us|uk|jp]\n"
            "E) Entity workflow:         datapulse <url> --entities --entity-mode fast\n"
            "Diagnostics: datapulse --config-check / --doctor / --troubleshoot / --skill-contract / --check-update / --self-update / --version"
        ),
    )
    parser.add_argument("inputs", nargs="*", help="URLs or commands")

    parsing_group = parser.add_argument_group("解析类")
    search_group = parser.add_argument_group("搜索类")
    management_group = parser.add_argument_group("管理类")
    diagnostic_group = parser.add_argument_group("诊断类")

    parsing_group.add_argument(
        "-b",
        "--batch",
        nargs="+",
        help="Process a batch of URLs",
    )
    parsing_group.add_argument(
        "--entities",
        action="store_true",
        help="Extract entities while reading URL inputs",
    )
    parsing_group.add_argument(
        "--entity-mode",
        default="fast",
        choices=["fast", "llm"],
        help="Entity extraction mode",
    )
    parsing_group.add_argument(
        "--entity-store",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Persist extracted entities to local entity store",
    )
    parsing_group.add_argument("--target-selector", metavar="CSS", help="CSS selector for targeted extraction")
    parsing_group.add_argument("--no-cache", action="store_true", help="Bypass Jina cache")
    parsing_group.add_argument("--with-alt", action="store_true", help="Enable AI image descriptions via Jina")
    parsing_group.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Filter by confidence",
    )
    parsing_group.add_argument("--list", "-l", action="store_true", help="List inbox")
    parsing_group.add_argument("--clear", action="store_true", help="Clear inbox")

    search_group.add_argument("-s", "--search", metavar="QUERY", help="Search the web")
    search_group.add_argument(
        "-S",
        "--site",
        action="append",
        metavar="DOMAIN",
        help="Restrict search to domain (repeatable)",
    )
    search_group.add_argument("--search-limit", type=int, default=5, help="Max search results (default 5)")
    search_group.add_argument("--no-fetch", action="store_true", help="Skip full content fetch for search results")
    search_group.add_argument(
        "--search-provider",
        default="auto",
        choices=["auto", "jina", "tavily", "multi"],
        help="Search provider: auto/jina/tavily/multi",
    )
    search_group.add_argument(
        "--search-mode",
        default="single",
        choices=["single", "multi"],
        help="Search mode: single (fallback) / multi (fused)",
    )
    search_group.add_argument("--search-deep", action="store_true", help="Enable deep search depth (Tavily)")
    search_group.add_argument("--search-news", action="store_true", help="Enable news-only retrieval (Tavily)")
    search_group.add_argument("--search-time-range", choices=["day", "week", "month", "year"], help="Time range filter (Tavily)")
    search_group.add_argument("--search-freshness", choices=["day", "week", "month", "year"], help="Alias for time range filter")
    search_group.add_argument(
        "--platform",
        choices=["xhs", "twitter", "reddit", "hackernews", "arxiv", "bilibili"],
        help="Restrict search to a specific platform",
    )
    search_group.add_argument(
        "-T",
        "--trending",
        nargs="?",
        const="",
        metavar="LOCATION",
        help="Show trending topics (default: worldwide). Locations: us, uk, jp, etc.",
    )
    search_group.add_argument("--trending-limit", type=int, default=20, help="Max trending topics (default 20)")
    search_group.add_argument("--trending-store", action="store_true", help="Save trending snapshot to inbox")
    search_group.add_argument("--trending-validate", action="store_true", help="Use cross-validated trending strategy")
    search_group.add_argument("--trending-validate-mode", default="strict", choices=["strict", "news", "lenient"], help="Trending validate mode")

    management_group.add_argument(
        "--source-profile",
        default="default",
        help="Source profile for feed/subscription ops",
    )
    management_group.add_argument("--source-ids", help="Comma separated source IDs for query_feed")
    management_group.add_argument("--list-sources", action="store_true", help="List source catalog entries")
    management_group.add_argument("--list-packs", action="store_true", help="List source packs")
    management_group.add_argument("--limit", type=int, default=20, help="List/feed/feed-like limit")
    management_group.add_argument("--include-inactive-sources", action="store_true", help="Include inactive sources")
    management_group.add_argument("--public-sources-only", action="store_true", help="Only list public sources")
    management_group.add_argument("--resolve-source", metavar="URL", help="Resolve source metadata for a URL")
    management_group.add_argument("--source-subscribe", metavar="SOURCE_ID", help="Subscribe profile source")
    management_group.add_argument("--source-unsubscribe", metavar="SOURCE_ID", help="Unsubscribe profile source")
    management_group.add_argument("--install-pack", metavar="PACK_SLUG", help="Install source pack to profile")
    management_group.add_argument("--query-feed", action="store_true", help="Print JSON feed output")
    management_group.add_argument("--query-rss", action="store_true", help="Print RSS feed output")
    management_group.add_argument("--query-atom", action="store_true", help="Print Atom 1.0 feed output")
    management_group.add_argument("--digest", action="store_true", help="Build curated digest")
    management_group.add_argument("--emit-digest-package", action="store_true", help="Export minimal office-ready digest package")
    management_group.add_argument("--emit-digest-format", default="json", choices=["json", "markdown", "md"], help="Digest package output format")
    management_group.add_argument("--top-n", type=int, default=3, help="Number of primary stories in digest")
    management_group.add_argument("--secondary-n", type=int, default=7, help="Number of secondary stories in digest")
    management_group.add_argument("--entity-query", help="Query entities from store by name")
    management_group.add_argument("--entity-type", help="Filter entity query by type")
    management_group.add_argument("--entity-limit", type=int, default=50, help="Limit for entity query")
    management_group.add_argument("--entity-min-sources", type=int, default=1, help="Minimum source count for entity query")
    management_group.add_argument("--entity-graph", help="Show related entities for one entity name")
    management_group.add_argument("--entity-stats", action="store_true", help="Show entity store stats")
    management_group.add_argument(
        "-i",
        "--login",
        choices=supported_platforms(),
        help="Capture browser login state for platform (xhs, wechat)",
    )

    diagnostic_group.add_argument("-d", "--doctor", action="store_true", help="Run health checks on all collectors")
    diagnostic_group.add_argument("--troubleshoot", nargs="?", const="", metavar="COLLECTOR", help="Show actionable fix suggestions; optionally specify one collector")
    diagnostic_group.add_argument(
        "--skill-contract",
        action="store_true",
        help="Print skill contract and tool descriptors for agent/agentic integrations",
    )
    diagnostic_group.add_argument(
        "--self-update",
        action="store_true",
        help="Upgrade DataPulse from GitHub repo",
    )
    diagnostic_group.add_argument(
        "--check-update",
        action="store_true",
        help="Check latest release tag on GitHub",
    )
    diagnostic_group.add_argument(
        "--version",
        action="store_true",
        help="Show DataPulse version",
    )
    diagnostic_group.add_argument(
        "-k",
        "--config-check",
        action="store_true",
        help="Check optional config completeness and show fix suggestions",
    )
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

    if args.doctor:
        report = reader.doctor()
        _print_doctor_report(report)
        return

    if args.troubleshoot is not None:
        report = reader.doctor()
        target = args.troubleshoot.strip() if isinstance(args.troubleshoot, str) else None
        target = target or None
        _print_troubleshoot_report(report, target=target)
        return

    if args.self_update:
        _run_self_update()
        return

    if args.skill_contract:
        _print_skill_contract()
        return

    if args.check_update:
        _print_update_status()
        return

    if args.version:
        _print_version()
        return

    if args.config_check:
        _print_config_check()
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

    if args.entity_stats:
        print(json.dumps(reader.entity_stats(), ensure_ascii=False, indent=2))
        return

    if args.entity_graph:
        print(json.dumps(reader.entity_graph(entity_name=args.entity_graph), ensure_ascii=False, indent=2))
        return

    if args.entity_query:
        query_payload = reader.query_entities(
            name=args.entity_query,
            entity_type=args.entity_type,
            limit=args.entity_limit,
            min_sources=args.entity_min_sources,
        )
        print(json.dumps(query_payload, ensure_ascii=False, indent=2))
        return

    if args.query_feed:
        feed_payload = reader.build_json_feed(
            profile=args.source_profile,
            source_ids=_normalize_csv_ids(args.source_ids),
            limit=args.limit,
            min_confidence=args.min_confidence,
        )
        print(json.dumps(feed_payload, ensure_ascii=False, indent=2))
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
        digest_payload = reader.build_digest(
            profile=args.source_profile,
            source_ids=_normalize_csv_ids(args.source_ids),
            top_n=args.top_n,
            secondary_n=args.secondary_n,
            min_confidence=args.min_confidence,
        )
        print(json.dumps(digest_payload, ensure_ascii=False, indent=2))
        return

    if args.emit_digest_package:
        package_payload = reader.emit_digest_package(
            profile=args.source_profile,
            source_ids=_normalize_csv_ids(args.source_ids),
            top_n=args.top_n,
            secondary_n=args.secondary_n,
            min_confidence=args.min_confidence,
            output_format=args.emit_digest_format,
        )
        print(package_payload)
        return

    if args.trending is not None:
        async def run_trending() -> None:
            result = await reader.trending(
                location=args.trending,
                top_n=args.trending_limit,
                store=args.trending_store,
                validate=args.trending_validate,
                validate_mode=args.trending_validate_mode,
            )
            if not result["trends"]:
                print("No trending data found")
                return
            loc = result["location"]
            print(f"Trending Topics on X ({loc}) — {result['snapshot_time']}\n")
            for t in result["trends"]:
                vol = f" ({t['volume']})" if t.get("volume") else ""
                print(f"  {t['rank']:2d}. {t['name']}{vol}")
            print(f"\nTotal: {result['trend_count']} topic(s)")
            if result.get("stored_item_id"):
                print(f"Stored as: {result['stored_item_id']}")

        asyncio.run(run_trending())
        return

    if args.search:
        async def run_search() -> None:
            results = await reader.search(
                args.search,
                sites=args.site or None,
                platform=args.platform,
                limit=args.search_limit,
                fetch_content=not args.no_fetch,
                extract_entities=args.entities,
                entity_mode=args.entity_mode,
                store_entities=args.entity_store,
                min_confidence=args.min_confidence,
                provider=args.search_provider,
                mode=args.search_mode,
                deep=args.search_deep,
                news=args.search_news,
                time_range=args.search_time_range,
                freshness=args.search_freshness,
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
        results = await reader.read_batch(
            targets,
            min_confidence=args.min_confidence,
            extract_entities=args.entities,
            entity_mode=args.entity_mode,
            store_entities=args.entity_store,
        )
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
