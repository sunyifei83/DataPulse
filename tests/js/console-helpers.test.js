const { loadConsoleHelpers } = require("./helpers/console-helper-harness");

describe("console helper harness", () => {
  test("loads the helper fragments without bootstrap side effects", () => {
    const helpers = loadConsoleHelpers();

    expect(helpers.__meta.loadedFiles).toEqual([
      "datapulse/static/console/00-common.js",
      "datapulse/static/console/10-story-primitives.js",
      "datapulse/static/console/30-intake-command-surface.js",
    ]);
    expect(helpers.__meta.loadedFiles).not.toContain("datapulse/static/console/90-bootstrap.js");
    expect(helpers.state.activeSectionId).toBe("section-intake");
  });
});

describe("list field helpers", () => {
  test("parseListField normalizes, de-duplicates, and lowers comma-delimited values", () => {
    const { parseListField } = loadConsoleHelpers();

    expect(parseListField(" Twitter, reddit, TWITTER，Reddit，youtube ")).toEqual([
      "twitter",
      "reddit",
      "youtube",
    ]);
  });

  test("formatListField and toggleListValue preserve comma-separated output", () => {
    const { formatListField, toggleListValue } = loadConsoleHelpers();

    expect(formatListField(["twitter", "", "reddit"])).toBe("twitter, reddit");
    expect(toggleListValue("twitter, reddit", "reddit")).toBe("twitter");
    expect(toggleListValue("twitter", "youtube")).toBe("twitter, youtube");
  });
});

describe("story and triage normalization helpers", () => {
  test("normalizeStorySort, normalizeStoryFilter, normalizeStoryWorkspaceMode, normalizeStoryDetailView, and normalizeTriageFilter gate invalid values", () => {
    const {
      normalizeStorySort,
      normalizeStoryFilter,
      normalizeStoryWorkspaceMode,
      normalizeStoryDetailView,
      normalizeTriageFilter,
    } = loadConsoleHelpers();

    expect(normalizeStorySort("RECENT")).toBe("recent");
    expect(normalizeStorySort("unexpected")).toBe("attention");
    expect(normalizeStoryFilter("resolved")).toBe("resolved");
    expect(normalizeStoryFilter("CONFLICTED")).toBe("conflicted");
    expect(normalizeStoryFilter("unexpected")).toBe("all");
    expect(normalizeStoryWorkspaceMode("EDITOR")).toBe("editor");
    expect(normalizeStoryWorkspaceMode("unexpected")).toBe("board");
    expect(normalizeStoryDetailView("evidence")).toBe("evidence");
    expect(normalizeStoryDetailView("unexpected")).toBe("overview");
    expect(normalizeTriageFilter("VERIFIED")).toBe("verified");
    expect(normalizeTriageFilter("unexpected")).toBe("open");
  });
});

describe("create-watch preview helpers", () => {
  test("draftHasAdvancedSignal ignores default provider but detects real advanced scope", () => {
    const { draftHasAdvancedSignal } = loadConsoleHelpers();

    expect(draftHasAdvancedSignal({ provider: "auto" })).toBe(false);
    expect(draftHasAdvancedSignal({ keyword: "launch" })).toBe(true);
    expect(draftHasAdvancedSignal({ provider: "multi" })).toBe(true);
  });

  test("buildCreateWatchPreview summarizes readiness, filters, and cross-verify state", () => {
    const { buildCreateWatchPreview } = loadConsoleHelpers();

    const preview = buildCreateWatchPreview({
      name: "Launch Pulse",
      query: "OpenAI launch",
      schedule: "interval:15m",
      platform: "twitter, reddit",
      domain: "openai.com",
      provider: "multi",
      route: "ops-room",
      keyword: "launch",
      min_score: "70",
      min_confidence: "0.8",
    });

    expect(preview.requiredReady).toBe(true);
    expect(preview.alertArmed).toBe(true);
    expect(preview.readiness).toBe(100);
    expect(preview.platformList).toEqual(["twitter", "reddit"]);
    expect(preview.siteList).toEqual(["openai.com"]);
    expect(preview.providerMode).toBe("multi");
    expect(preview.crossVerify).toBe(true);
    expect(preview.summary).toContain("Track OpenAI launch");
    expect(preview.filtersLabel).toBe("twitter, reddit / openai.com / launch");
    expect(preview.routeLabel).toBe("ops-room");
    expect(preview.crossVerifyLabel).toContain("cross-verify");
  });

  test("summarizeCreateWatchAdvanced reports advanced chips and keeps the empty fallback honest", () => {
    const { summarizeCreateWatchAdvanced } = loadConsoleHelpers();

    expect(summarizeCreateWatchAdvanced({})).toEqual(["No scope or alert gate yet"]);

    expect(summarizeCreateWatchAdvanced({
      schedule: "@hourly",
      platform: "twitter, reddit",
      provider: "multi",
      route: "ops-room",
    })).toEqual([
      "cron alias @hourly",
      "platforms: twitter, reddit",
      "provider: multi",
      "multi-source parallel + cross-verify",
      "route: ops-room",
    ]);
  });
});
