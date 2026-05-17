# ModelBus Bundle Drift Guard (DP-side)

Date: 2026-05-16
Owner: DataPulse
Status: Draft for review
Repo: `~/DataPulse` @ `6ada88b`
Upstream pin: `sunyifei83/ModelBusProject @ cb89464cb` (declared by MB sync 2026-05-14..16)

---

## 1. Problem (anchored facts)

DataPulse consumes ModelBus (MB) governance state via JSON bundle. Two structural gaps were discovered on 2026-05-16:

### 1.1 Local bundle is non-conformant with MB current emit shape — **all 4 payloads drifted**

DP local snapshot was generated `2026-04-02T03:05:09Z` (~44 days stale). Drift per payload, anchored to MB current `scripts/ci/build_consumer_bundle.py` + `docs/schemas/`:

**`bundle_manifest.json`** — MB schema `docs/schemas/modelbus.consumer_bundle_manifest.v1.json` (blob `84dc243`) declares 9 top-level required fields and 7 required artifacts. DP local:
- Top-level: 5/9 required. Missing: `source_profile`, `runtime`, `surfaces`, `governance`.
- Artifacts: 3/7 required. Missing: `bundle_readme`, `bundle_manifest` (self-ref), `alias_catalog`, `smoke_manifest`.

**`surface_admission.json`** — MB `build_consumer_bundle.py:207` emits 7 fields. DP local: 5/7. Missing: `source_profile`, `source_release_status`.

**`bridge_config.json`** — MB `build_consumer_bundle.py:158` emits 15 fields. DP local: 10/15. Missing: `accepted_protocols`, `accepted_modelbus_semantics`, `release_window`, `mode_by_surface`, `capability_packages_by_surface`.

**`release_status.json`** — MB schema `docs/schemas/modelbus.release_status.v1.json` exists. Field-level drift quantification deferred to implementation step 0 (read schema, diff against DP payload).

All drift to date is **missing-fields-only** (no rename, no type narrow, no field removal). DP reader.py functionally still works because it consumes only narrow subsets — but the snapshot is provably non-conformant with MB current spec.

### 1.2 DP parser does not enforce MB schema

`datapulse/reader.py` validates only the `schema` string field equals `modelbus.consumer_bundle_manifest.v1` and that 3 hardcoded artifact paths exist. No JSON Schema validation. → Drift is silent. The bundle visibly violates v1 but parses without error.

### 1.3 Upstream ownership model

Per MB's runbook `docs/integrations/datapulse-release-bundle-runbook.md`:
- MB owns bundle production (`scripts/local/verify_assured_release.sh` → `consumer_bundles/datapulse/`).
- MB invokes DP with `DATAPULSE_MODELBUS_BUNDLE_DIR=<fresh_bundle_dir>` at release time.
- DP's local `config/modelbus/datapulse/` is a **fallback / diagnostic snapshot**, not the primary source of truth.
- "Local snapshot" only feeds: dev runs, console smoke, DP CI when `DATAPULSE_MODELBUS_BUNDLE_DIR` is unset.

So 1.1's drift does not break MB-led release windows, but it **does** affect every other code path that resolves the canonical bundle dir. The snapshot's job is "diagnostic + fallback" — for that job it must be conformant.

---

## 2. Goals

- G1. DP's local snapshot conforms to current MB v1 schema.
- G2. Schema drift becomes loud (parser-enforced), not silent.
- G3. Bundle staleness is observable in CI before it crosses thresholds.
- G4. Future MB v1→v2 migration is detected at the consumer earliest, not by surprise.

## 3. Non-goals

- Live HTTP consumer of `/v1/governance/*` endpoints. No freshness requirement justifies the dependency.
- Replacing MB's bundle generator. DP does not produce bundles.
- Implementing v2 schema support. No v2 exists; design for additive v1 changes only.
- Ecosystem contract-testing infrastructure (Pact Broker, Confluent SR). 1×1 same-owner relationship makes this over-engineering.

## 4. Design

Four layers, P0 → P2.

### Layer 1 — Re-pull conformant snapshot (P0, one-shot operator action)

Not code. Operator coordination with MB owner.

Steps (executed by operator, on MB host):

```
# On MB host (~/ModelBusProject)
bash scripts/local/verify_assured_release.sh \
  --out out_tmp_datapulse_drift_fix_20260516/assured_deploy \
  --release-level assured \
  --consumer-bundle-batch-manifest docs/examples/consumer-bundle-batch.release-attachment.json

# Copy produced bundle into DP repo
cp out_tmp_datapulse_drift_fix_20260516/assured_deploy/consumer_bundles/datapulse/* \
   ~/DataPulse/config/modelbus/datapulse/
```

Acceptance: DP's `bundle_manifest.json` `generated_at_utc` ≥ 2026-05-16T00:00:00Z and the 9 required top-level fields all present.

If MB owner unavailable on the same window as Layer 2, Layer 2 lands first in warn-only mode (see §4.2 rollout).

### Layer 2 — Schema validation in reader (P0, ~120 LoC across 2a + 2b)

Q1 resolution: of the 4 schema strings DP reader.py checks, only 2 have authoritative JSON Schema documents published by MB. The other 2 exist only as payload tags emitted by MB's `build_consumer_bundle.py`. Layer 2 splits accordingly.

#### Layer 2a — Mirror MB-authoritative schemas

For schemas with published `.v1.json` files:

```
config/modelbus/schemas/upstream/
  modelbus.consumer_bundle_manifest.v1.json     # mirror of MB blob 84dc243
  modelbus.release_status.v1.json               # mirror of MB blob 78aa95a
  README.md                                     # pin sha, pull date, policy
```

Each mirror is the verbatim MB schema content. `README.md` records source blob SHAs and the date pulled.

#### Layer 2b — DP-authored consumer contract for un-published schemas

For schemas emitted by MB code without a published spec (`consumer_surface_admission.v1`, `consumer_bridge_config.v1`), DP authors a minimum-shape contract reflecting **what DP actually depends on**, not the full MB emit shape:

```
config/modelbus/schemas/consumer-contract/
  modelbus.consumer_surface_admission.v1.json   # DP-authored, only DP-consumed fields required
  modelbus.consumer_bridge_config.v1.json       # DP-authored, same approach
  README.md                                     # explains: consumer-driven contract per Pact CDC pattern;
                                                #           swap to MB-authoritative when MB publishes
```

The DP-authored schemas mark only DP-consumed fields as `required`, leaving the rest of the MB emit shape as `additionalProperties: true`. This is the classic consumer-driven contract pattern: DP locks in what it depends on, MB free to add fields. When MB publishes authoritative schemas, the DP contract becomes a verifiable subset of the MB spec (BDCT alignment check).

#### Reader integration (shared between 2a + 2b)

`datapulse/reader.py` changes:

- New helper `_validate_against_schema(payload, schema_name) -> list[str]`:
  - Tries `config/modelbus/schemas/upstream/<schema_name>.json` first, falls back to `consumer-contract/<schema_name>.json`.
  - If `jsonschema` library installed → runs strict validation, returns list of field-path errors with the source ("upstream" / "consumer-contract") in the message prefix.
  - If library missing → returns empty list and logs once at warn level. Library is optional dep, not hard dep.
- Integrated at the 4 existing schema-string check sites (`reader.py:1054`, `1103`, `1107`, `1111`):
  - After string check passes, call `_validate_against_schema`.
  - Aggregate errors into existing `errors` list. Existing fail-closed path picks them up.
- New optional extra in `pyproject.toml`: `[project.optional-dependencies] governance = ["jsonschema>=4.0"]`. CI installs it; runtime users may opt out.

Rollout sub-stages within Layer 2:

- **2a-warn**: Mirrors + DP-authored contracts committed, validation runs in warn-only mode (errors logged, not added to fail-closed `errors` list). Run until the admission gate `scripts/check_modelbus_admission.sh` exits 0 (≥N clean validations since last warn — N=10 default). Time-based soak (originally ≥7 days) was deprecated as a subjective threshold; see §11.
- **2-fail**: Flip to fail-closed mode for both source types.

`datapulse/reader.py` changes:

- New helper `_validate_against_mirror(payload, schema_name) -> list[str]`:
  - Loads `config/modelbus/schemas/<schema_name>.json` lazily.
  - If `jsonschema` library installed → runs strict validation, returns list of field-path errors.
  - If library missing → returns empty list and logs once at warn level. **Library is optional dep, not hard dep.**
- Integrated at the 4 existing schema-string check sites (around `reader.py:1054–1112`):
  - After string check passes, call `_validate_against_mirror`.
  - Aggregate errors into existing `errors` list. Existing fail-closed path picks them up.
- New optional extra in `pyproject.toml`: `[project.optional-dependencies] governance = ["jsonschema>=4.0"]`. CI installs it; runtime users may opt out.

Rollout sub-stages within Layer 2:

- **2a**: Mirror committed, validation runs in warn-only mode (errors logged, not added to fail-closed `errors` list). Run until the admission gate `scripts/check_modelbus_admission.sh` exits 0 (≥N clean validations since last warn — N=10 default). Time-based soak (originally ≥7 days) was deprecated as a subjective threshold; see §11.
- **2b**: Flip to fail-closed mode.

### Layer 3 — Weekly drift CI (P1, ~60 LoC YAML)

New workflow `.github/workflows/modelbus-bundle-drift.yml`:

Triggers:
- `schedule: '0 14 * * MON'` (weekly Monday 14:00 UTC)
- `pull_request: paths: ['config/modelbus/**', 'datapulse/reader.py']`
- `workflow_dispatch`

Steps:

1. Fetch live MB schemas via `gh api repos/sunyifei83/ModelBusProject/contents/docs/schemas/<schema>.json`.
2. For each mirrored schema, run `diff <local> <upstream>`.
   - If diff is purely additive (new optional properties only) → warn, post comment on PR / open issue weekly.
   - If diff is non-additive (required field added, type narrowed, property removed) → **fail**.
   - Detection logic: shell out to a small Python helper `scripts/modelbus_schema_diff.py` using `jsonschema` semantics, not raw text diff.
3. Inspect DP's `bundle_manifest.json`:
   - `generated_at_utc` > 60 days old → warn.
   - `generated_at_utc` > 90 days old → fail.
4. If MB has added `source_pin` field (see issue #9 follow-up): query MB main HEAD via `gh api`, compute commit distance; > 100 commits → warn.

Token: GitHub Actions' default `GITHUB_TOKEN` is scoped to the running repo only and **cannot** read content from another private repo even under the same owner. Layer 3 therefore needs either:
- A fine-grained PAT scoped to `sunyifei83/ModelBusProject` with `contents: read`, stored as `MB_REPO_READ_TOKEN` secret in DP repo, or
- A GitHub App with cross-repo install.

Recommend PAT for minimum complexity. Implementation step 0 of Layer 3: create the PAT, add as secret, document rotation policy in workflow comments.

### Layer 4 — Renovate auto-PR (P2, **deferred — see §11 tripwire**, ~20 LoC config)

New `renovate.json` (or add to existing if present) custom-manager block:

```json
{
  "customManagers": [
    {
      "customType": "regex",
      "fileMatch": ["^config/modelbus/schemas/.*\\.v1\\.json$"],
      "matchStrings": [
        "//\\s*pin:\\s*(?<currentDigest>[a-f0-9]{7,40})"
      ],
      "depNameTemplate": "sunyifei83/ModelBusProject",
      "datasourceTemplate": "github-tags",
      "versioningTemplate": "loose"
    }
  ]
}
```

Mirror schemas carry a `// pin: <sha>` line (committed alongside the JSON, possibly in the matching `.pin` sidecar file since JSON itself has no comments). When MB's commit SHA changes, Renovate opens a PR bumping the pin and rendering the diff.

Since MB has no releases/tags currently, `github-tags` datasource may not work; fallback is "git" datasource with branch=main tracking. Decide at implementation time after probing what Renovate supports for tagless tracking.

This layer is genuinely optional — Layer 3 already catches drift on a weekly cadence. Renovate adds developer-ergonomic PRs but is not load-bearing. **Deferred** for the 1×1 same-owner case (see §11 for tripwire criteria + an alternative PyPI-package distribution path that would supersede Renovate-style mirror auto-PR if it ever becomes worth adopting).

## 5. Data flow

```
                    ┌─────────────────────────────────┐
                    │ MB repo (sunyifei83/ModelBusProject)
                    │  docs/schemas/*.v1.json
                    │  scripts/local/verify_assured_release.sh
                    └────────────┬──────────────────────┘
                                 │ (1) operator runs release
                                 ▼
                    ┌─────────────────────────────────┐
                    │ MB-produced bundle
                    │  consumer_bundles/datapulse/*.json
                    └────────────┬──────────────────────┘
                                 │ (2) cp to DP
                                 ▼
   ┌───────────────────────────────────────────────────────────────┐
   │ DP repo                                                       │
   │  config/modelbus/                                             │
   │    datapulse/{bundle_manifest, surface_admission,             │
   │               release_status, bridge_config}.json   ← snapshot│
   │    schemas/upstream/*.v1.json          ← MB-authoritative mirror
   │    schemas/consumer-contract/*.v1.json ← DP-authored contract │
   │                                                               │
   │  datapulse/reader.py                                          │
   │    _load_modelbus_bundle_surface_admissions_from_dir()        │
   │      → string-equal check  (existing)                         │
   │      → _validate_against_mirror()                  ← NEW L2   │
   │      → fail-closed path                            (existing) │
   │                                                               │
   │  .github/workflows/modelbus-bundle-drift.yml       ← NEW L3   │
   │  renovate.json (custom-manager block)              ← NEW L4   │
   └───────────────────────────────────────────────────────────────┘
```

## 6. Error handling

- **Mirror schema not on disk**: reader logs warn once, validation is skipped (graceful degrade). Drift CI catches this.
- **jsonschema lib not installed**: same as above — warn once, skip. CI installs the extra, so production CI always validates.
- **Validation fails (Layer 2b)**: errors list grows with field-path messages, existing `admission_source = "modelbus_bundle_required"` fail-closed path activates. No new control flow.
- **Drift CI gh api failure**: retry 3× with backoff; on persistent failure → workflow warns (not fails) since MB may be in maintenance.
- **Renovate PR fails to merge cleanly**: Renovate's responsibility, not DP's; manual PR review absorbs it.

## 7. Testing

Add to `tests/test_reader.py`:

- `test_modelbus_schema_mirror_passes_for_conformant_bundle`: synthesize bundle matching MB v1 fully, expect no errors.
- `test_modelbus_schema_mirror_catches_missing_required_field`: drop `source_profile`, expect error mentioning the field path.
- `test_modelbus_schema_mirror_catches_artifact_subset`: include only 3 of 7 required artifacts, expect error.
- `test_modelbus_schema_mirror_skipped_when_lib_unavailable`: monkeypatch `jsonschema` import to fail, assert no exception raised and warning logged once.

New `tests/test_modelbus_schema_mirror_well_formed.py`:

- Walk `config/modelbus/schemas/*.json`; each must be valid JSON, parse with `jsonschema.Draft7Validator.check_schema` (or whatever draft MB uses; detect from `$schema`).

CI smoke for drift workflow itself: invoke via `workflow_dispatch` after first land to confirm gh api calls succeed.

## 8. Rollout

| Stage | Action | Acceptance |
|---|---|---|
| S0 | Spec approved | This doc reviewed by user |
| S1 | Land Layer 2 mirror + warn-only validation | reader.py logs validation summary on bundle load |
| S2 | Operator runs Layer 1 with MB | DP snapshot has 9/9 required fields and 7/7 artifacts |
| S3 | Flip Layer 2 to fail-closed (2a→2b) | `scripts/check_modelbus_admission.sh` exits 0 (≥N clean validations since last warn); validation errors gate `admission_source` fallback |
| S4 | Land Layer 3 drift CI | First weekly run posts a passing report |
| S5 (deferred) | Land Layer 4 Renovate **or** PyPI-package distribution | Tripwire triggered per §11 (≥2 schema changes/month *or* a new silent drift incident) |

S1 and S2 can happen in parallel (warn-only mode is safe even with non-conformant snapshot).

## 9. Open questions

- **Q1: ~~Schema name verification.~~ RESOLVED 2026-05-16.** All 4 DP-expected schema strings are real names MB emits.
- **Q5: ~~MB schema publication gap.~~ RESOLVED 2026-05-17** (MB commit `9d0a364`, issue #9 follow-up). MB published authoritative `modelbus.consumer_surface_admission.v1.json` and `modelbus.consumer_bridge_config.v1.json` at `docs/schemas/`. DP migrated both from `consumer-contract/` CDC stand-ins to `upstream/` mirrors in this PR. The MB authoritative schemas are strict (`additionalProperties: false`, 16 + 7 required fields respectively) — far stricter than DP's prior CDC stand-ins; DP's existing local bundle drifts against them and will surface warns until #51 (fresh bundle) lands.
- **Q2: ~~`source_pin` adoption.~~ RESOLVED 2026-05-17** (MB commit `9d0a364`). MB added an optional `source_pin: {mb_commit_sha, mb_short_sha}` field to `consumer_bundle_manifest.v1.json` (only-add, not in `required[]` — readers MUST graceful-ignore when missing). DP does not yet consume the field; doing so would let Layer 3's commit-distance check become precise instead of date-only. Tracked as a future small enhancement in reader.py, not blocking.
- **Q3: MB v2 timing.** MB has no v2 plans surfaced. Design assumes additive-only v1 evolution. When v2 emerges, an Expand-Contract migration spec is needed (out of scope here).
- **Q4: Renovate datasource for tagless tracking.** MB currently has no releases/tags. Need to verify Renovate can track main-branch SHAs for non-package files at implementation time.

## 10. References

- MB runbook: `sunyifei83/ModelBusProject:docs/integrations/datapulse-release-bundle-runbook.md`
- MB schema dir: `sunyifei83/ModelBusProject:docs/schemas/` (25 files)
- MB build lib (de facto schemas for un-published payloads): `sunyifei83/ModelBusProject:scripts/ci/build_consumer_bundle.py:158,207`
- MB consumer bundle helpers: `sunyifei83/ModelBusProject:scripts/ci/consumer_bundle_lib.py`
- DP reader code under change: `datapulse/reader.py:1034–1170`
- Industry pattern grounding (1×1 same-owner case):
  - PactFlow — Schemas Can Be Contracts (BDCT minimum impl)
  - Renovate custom-manager docs
  - Sourcemeta One — schema evolution rules
  - Confluent — backward-compat as default

## 11. Governance & evolution (post-merge addendum, 2026-05-17)

This section was added after PR #50 merged. It captures three corrections / extensions derived from a research pass on industry best practices (Linux kernel, Kubernetes, Rust, Chromium, GitHub Docs, Google SRE, Stripe, Confluent SR, Buf BSR, Conduktor, Renovate / Dependabot).

### 11.1 Audit trail anchor — PR commits view, not main history

Original framing (in the ob index "ModelBus 接入准备清单.md") asserted "10 commits 不 squash, preserve TDD red→green→review-fix 序列作为 governance audit trail." PR #50 was merged via squash per the repo's existing main convention (every prior PR appears as a single squash commit with `(#NN)` suffix; e.g. PR #49 → `1ef6ff3`).

Resolution: **the PR commits view is the authoritative audit trail.** GitHub guarantees PR-attached commit history is permanent and indexed by PR number, independent of the source branch's lifecycle (the feat branch has been deleted). [GitHub: about merge methods](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges) explicitly recommends squash + PR-link as a valid pattern for preserving development history while keeping main linear. Reverting `1a42555` to re-merge with `--merge` would add 2 noise commits to main without producing a contiguous 10-commit sequence anyway; force-pushing to rewrite main is destructive and disproportionate. Mature OSS practice is split (Linux welcomes merge commits; Kubernetes mandates squash; Rust enforces linear; Chromium uses main-first cherry-pick) — there is no universal "correct" merge strategy, so the right call is to align with the repo's prior convention.

**Operating policy going forward:** PRs in this repo are merged squash by default. Multi-commit governance / TDD trail intent is satisfied by referencing the PR commits view, not by mandating a particular merge mode.

### 11.2 Warn → fail admission — event-gated, not time-gated

Original §4.2 sub-stage 2a required "≥7 days warn-mode soak." This number had no industry citation — Kubernetes uses ~2 years for GA API deprecation ([k8s deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)); Stripe uses 6–12 months for API version retirement ([Stripe upgrades](https://docs.stripe.com/upgrades)); Google SRE gates rollouts on error budget, not fixed duration ([SRE error budget policy](https://sre.google/workbook/error-budget-policy/)). For a single-owner, low-traffic data pipeline, importing a multi-tenant-B2C-shaped soak window is over-engineering in the opposite direction: it gates on a subjective time threshold instead of an observable signal.

Resolution: **the soak gate is event-based, not time-based.** A small validation counter persists per-event state to `~/.datapulse/modelbus_validation_counter.json` (or via `DATAPULSE_MODELBUS_VALIDATION_COUNTER_PATH` for tests). Admission is granted when **N consecutive validation events have occurred without a warn** (default N=10, configurable via `--min-validations` flag). The check is invokable as `scripts/check_modelbus_admission.sh` and is the single source of truth for Task 7's "ready to flip" decision.

This aligns with the project principle "事实锚点优先 — 机械化 / 客观化优先于人工." Time-based soak is a subjective fallback; event-based admission is a mechanical check.

### 11.3 Layer 4 (auto-sync) — deferred + tripwire + PyPI alternative

Layer 4 in §4 is Renovate-based mirror auto-PR. Scope C research surfaced that the industry-standard long-term pattern for cross-repo schema distribution is publisher-side packaging (Confluent SR; Buf BSR; PyPI / npm versioned schema package + Renovate/Dependabot consumer pull) rather than mirror-with-auto-PR. ([Conduktor schema evolution best practices](https://www.conduktor.io/glossary/schema-evolution-best-practices/); [Buf BSR docs](https://buf.build/docs/bsr/).) However, for the 1×1 same-owner case with sub-monthly schema change cadence, both Renovate-style auto-PR and PyPI-package distribution exceed the cost/benefit threshold for now ([Microsoft ISE: Pact value emerges at ≥3 microservices / >50% annual team turnover](https://devblogs.microsoft.com/ise/pact-contract-testing-because-not-everything-needs-full-integration-tests/)).

Resolution: **Layer 4 is deferred.** Re-evaluate when **any** of the following tripwires fire:

- MB schema change frequency exceeds 2/month for a sustained period (>3 months)
- A second silent-drift incident occurs despite Layer 3 weekly workflow
- A third consumer of MB bundles appears (i.e., the 1×1 assumption breaks)

When the tripwire fires, prefer **PyPI-published schema package + Renovate consumer pull** over the mirror+auto-PR design originally drafted in §4 Layer 4. Rationale: it decouples schema lifecycle from git commit cadence, leverages first-class versioning (consumers pin a known version), and reuses standard Python dependency tooling instead of a bespoke Renovate custom-manager. The original §4 Layer 4 design remains documented as a fallback if private PyPI distribution proves operationally heavier than expected.
