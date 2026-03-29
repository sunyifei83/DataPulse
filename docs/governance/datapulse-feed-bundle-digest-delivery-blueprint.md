# DataPulse Feed Bundle And Digest Delivery Hardening Blueprint

## Purpose

This document promotes the `follow-builders` capability extraction into repository-scoped blueprint truth.

The goal is not to recreate a second product or bypass the current `mission -> triage -> story -> report -> delivery` lifecycle. The goal is to close one narrow but high-leverage gap in the current repo:

`curated pack/profile -> replayable feed bundle -> deterministic digest payload -> prompt-governed rendering -> route-backed delivery`

That gap is where `follow-builders` is genuinely stronger than current DataPulse ergonomics.

## Current Repo Read

DataPulse already has more lifecycle and governance depth than `follow-builders`.

Current repo anchors:

- `datapulse/core/source_catalog.py`
- `datapulse/reader.py`
- `datapulse/core/alerts.py`
- `docs/source_feed_enhancement_plan.md`
- `docs/intelligence_lifecycle_contract.md`
- `docs/intelligence_delivery_contract.md`
- `docs/gui_intelligence_console_plan.md`

Current repo reality:

- packs and profile-scoped feed exports already exist through `list_packs`, `install_pack`, `query_feed`, `build_json_feed`, `build_rss_feed`, and `build_atom_feed`
- digest curation already exists through `build_digest` and `emit_digest_package`
- route-backed push delivery already exists through named routes, `AlertEvent`, report delivery packages, route health, and browser route management
- browser onboarding already exists as mission/story/route guidance inside the console shell

That changes the highest-leverage delta.

The next delta is not "add packs" or "add digest" again. The next delta is to make existing pack/feed/digest/delivery surfaces replayable, deterministic, prompt-governed, and first-run operable.

## What `follow-builders` Gets Right For This Repo

The useful extracted capability is not collector breadth. It is execution shape.

High-value capability to import:

1. curated source selection produces a stable feed artifact instead of immediately mixing fetch, prompt, and delivery
2. one deterministic payload packages content, config, prompts, stats, and errors before any LLM remix step
3. prompt files are explicit, local, and user-overridable
4. onboarding captures language, timezone, frequency, and delivery defaults as a real profile instead of scattered setup knowledge
5. Telegram delivery handles chunking and fallback instead of silently truncating or assuming one successful send

Repo implication:

- DataPulse should treat this wave as delivery ergonomics and determinism hardening over existing repo primitives, not as a fresh lifecycle branch

## Real Gap Versus Current DataPulse

The current repo already has `pack/feed/digest/delivery` components, but it still lacks five narrow contracts:

### 1. Replayable `feed_bundle`

The repo can query feeds and build digests, but it does not yet persist or export one explicit `feed_bundle` artifact that binds:

- `pack_id` or `profile`
- selected `source_ids`
- run window / since cursor
- selected content rows
- stats and errors

Repo implication:

- the bundle should become the replayable input between source selection and digest rendering

### 2. Deterministic `prepare_digest_payload`

`build_digest` and `emit_digest_package` already exist, but they do not yet freeze one route-ready deterministic payload boundary shaped like:

- `content`
- `config`
- `prompts`
- `stats`
- `errors`

Repo implication:

- rendering, LLM remix, and route delivery should consume this payload rather than re-querying network data or re-deriving config ad hoc

### 3. Prompt pack and override order

The repo has operator-visible prompt text for AI assistance surfaces, but digest rendering does not yet expose a repo-defined prompt-pack contract with local overrides.

Repo implication:

- the digest layer needs explicit default prompt files plus a local override path such as `~/.datapulse/prompts/*`

### 4. First-run digest profile and onboarding boundary

The browser shell teaches current flows, but the repo does not yet expose one shared first-run profile for:

- `language`
- `timezone`
- `frequency`
- default delivery target or route

Repo implication:

- CLI, MCP, and console should converge on the same onboarding/profile nouns instead of leaving digest defaults implicit

### 5. Delivery robustness for Telegram and large payloads

Current repo truth still includes a `3900`-character truncation path in report delivery and single-send assumptions in Telegram dispatch surfaces.

Repo implication:

- route-backed digest/report delivery must support chunking, fallback, and attempt diagnostics before wider promotion

## What This Wave Must Preserve

Invariants for this wave:

1. `WatchMission`, `Story`, `Report`, and named routes remain the canonical lifecycle and delivery nouns
2. `build_digest` and `emit_digest_package` remain valid repo anchors; the new payload layer should refine them, not replace them
3. feed bundle and digest payload contracts must stay deterministic and replayable
4. prompt overrides must be explicit and operator-visible, not hidden inside browser state or environment drift
5. onboarding must compile down to shared Reader-backed config/profile truth
6. route-backed push still requires attributable delivery facts and route health observations
7. browser projection must stay a thin surface over Reader/CLI/MCP semantics rather than inventing a GUI-only digest composer

## What Should Not Be Reopened In This Wave

This wave should not reopen:

- a second content lifecycle parallel to mission/triage/story/report
- a new source-catalog system beside current `pack/profile/subscription` surfaces
- direct source editing rules that bypass current pack governance
- hidden prompt state in the browser only
- delivery success semantics that ignore route observations or truncate content silently

## L19 Slice Map

| Slice | Outcome | Why it exists |
| --- | --- | --- |
| `L19.1` | Land this repo-scoped feed-bundle and digest-delivery hardening blueprint plus manual ignition map | Converts the external capability extraction into active repo truth and restores a concrete next manual slice after the completed `L18` wave |
| `L19.2` | Define the `feed_bundle` and `prepare_digest_payload` contract on top of current pack/feed/digest surfaces | Freezes the deterministic payload boundary before runtime exporters or UI work drift into ad hoc shapes |
| `L19.3` | Define prompt-pack override order and first-run digest profile/onboarding semantics across CLI, MCP, and console | Makes rendering style and user defaults explicit instead of scattering them across route setup and operator memory |
| `L19.4` | Add Reader / CLI / MCP feed-bundle export and deterministic digest payload emission | Lands the narrow runtime value while reusing current `build_digest` and `emit_digest_package` semantics |
| `L19.5` | Harden route-backed digest/report delivery with Telegram chunking, fallback, and diagnostics | Closes the most visible delivery robustness gap before broader push usage |
| `L19.6` | Project feed-bundle browse/run, digest profile onboarding, and delivery diagnostics into the browser console and smoke coverage | Preserves cross-surface parity and keeps the browser as a projection instead of a second control plane |

## Recommended Ignition Order After This Refresh

Recommended order after this refresh:

1. `L19.2`
2. `L19.3`
3. `L19.4`
4. `L19.5`
5. `L19.6`

This order keeps the next work narrow:

- first freeze the deterministic bundle and payload nouns
- then freeze prompt and onboarding boundaries
- then add the exporter/runtime path
- then harden route delivery
- then project the same nouns into the browser

## One-Line Direction

DataPulse should not copy `follow-builders` as a product. It should absorb the stronger execution shape: make current pack/feed/digest surfaces replayable through `feed_bundle`, make rendering deterministic through `prepare_digest_payload`, let prompts and first-run defaults be explicit, and harden route-backed Telegram delivery before broader digest push usage.
