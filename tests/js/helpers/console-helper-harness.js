const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const CONSOLE_HELPER_FILES = [
  path.join("datapulse", "static", "console", "00-common.js"),
  path.join("datapulse", "static", "console", "10-story-primitives.js"),
  path.join("datapulse", "static", "console", "30-intake-command-surface.js"),
];

function createStorage() {
  const values = new Map();
  return {
    getItem(key) {
      return values.has(String(key)) ? values.get(String(key)) : null;
    },
    setItem(key, value) {
      values.set(String(key), String(value));
    },
    removeItem(key) {
      values.delete(String(key));
    },
    clear() {
      values.clear();
    },
  };
}

function createElementStub(tagName = "div") {
  return {
    tagName: String(tagName).toUpperCase(),
    style: {},
    dataset: {},
    classList: {
      add() {},
      remove() {},
      toggle() {
        return false;
      },
      contains() {
        return false;
      },
    },
    appendChild() {},
    removeChild() {},
    remove() {},
    setAttribute() {},
    getAttribute() {
      return null;
    },
    addEventListener() {},
    removeEventListener() {},
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
    scrollIntoView() {},
    focus() {},
    select() {},
    getContext() {
      return {
        font: "",
        measureText(value) {
          return { width: String(value ?? "").length * 8 };
        },
      };
    },
  };
}

function createDocumentStub() {
  const body = createElementStub("body");
  return {
    body,
    documentElement: { lang: "en" },
    activeElement: null,
    getElementById() {
      return null;
    },
    createElement(tagName) {
      return createElementStub(tagName);
    },
    addEventListener() {},
    removeEventListener() {},
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
  };
}

function createConsoleVmContext() {
  const document = createDocumentStub();
  const localStorage = createStorage();
  const sessionStorage = createStorage();
  const location = new URL("https://example.test/console");
  const window = {
    __DP_INITIAL__: {},
    location,
    history: {
      state: null,
      replaceState() {},
      pushState() {},
    },
    navigator: {
      language: "en-US",
      clipboard: {
        writeText: async () => {},
      },
    },
    localStorage,
    sessionStorage,
    alert() {},
    addEventListener() {},
    removeEventListener() {},
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    requestAnimationFrame(callback) {
      return setTimeout(() => callback(0), 0);
    },
    cancelAnimationFrame(handle) {
      clearTimeout(handle);
    },
    matchMedia() {
      return {
        matches: false,
        addEventListener() {},
        removeEventListener() {},
      };
    },
  };
  const context = vm.createContext({
    window,
    document,
    navigator: window.navigator,
    localStorage,
    sessionStorage,
    console,
    fetch: async () => {
      throw new Error("Unexpected fetch in console helper unit tests.");
    },
    URL,
    URLSearchParams,
    Intl,
    Date,
    Math,
    JSON,
    Map,
    Set,
    WeakMap,
    WeakSet,
    Array,
    Object,
    String,
    Number,
    Boolean,
    RegExp,
    Error,
    TypeError,
    Promise,
    AbortController,
    detectInitialLanguage: () => "en",
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    requestAnimationFrame: window.requestAnimationFrame,
    cancelAnimationFrame: window.cancelAnimationFrame,
    performance: { now: () => 0 },
    HTMLElement: class HTMLElementStub {},
    Node: class NodeStub {},
  });
  context.globalThis = context;
  context.window.window = context.window;
  context.window.document = document;
  context.window.console = console;
  context.window.performance = context.performance;
  return context;
}

function readConsoleHelperSource(repoRoot) {
  return CONSOLE_HELPER_FILES.map((relativePath) => {
    const absolutePath = path.join(repoRoot, relativePath);
    return fs.readFileSync(absolutePath, "utf8");
  }).join("\n\n");
}

function loadConsoleHelpers() {
  const repoRoot = path.resolve(__dirname, "..", "..", "..");
  const helperSource = readConsoleHelperSource(repoRoot);
  const wrappedSource = [
    "(function loadDataPulseConsoleHelpers() {",
    helperSource,
    "return {",
    "  parseListField,",
    "  formatListField,",
    "  toggleListValue,",
    "  normalizeTriageFilter,",
    "  normalizeStorySort,",
    "  normalizeStoryFilter,",
    "  normalizeStoryWorkspaceMode,",
    "  normalizeStoryDetailView,",
    "  draftHasAdvancedSignal,",
    "  buildCreateWatchPreview,",
    "  summarizeCreateWatchAdvanced,",
    "  state,",
    "  __meta: { loadedFiles: " + JSON.stringify(CONSOLE_HELPER_FILES) + " },",
    "};",
    "})()",
  ].join("\n");
  return vm.runInContext(wrappedSource, createConsoleVmContext(), {
    filename: "tests/js/helpers/console-helper-harness.js",
  });
}

module.exports = {
  CONSOLE_HELPER_FILES,
  loadConsoleHelpers,
};
