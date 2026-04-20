// Split group 2c: intake deck rendering, language chrome, command palette, and shared operator actions.
// Depends on prior fragments and 00-common.js.

function applyLanguageChrome() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.body.dataset.lang = state.language;
  document.title = state.language === "zh" ? "DataPulse 情报控制台" : initial.title;
  setText("topbar-title", copy("DataPulse Operations Console", "DataPulse 情报控制台"));
  setText("nav-intake", copy("Start", "开始"));
  setText("nav-missions", copy("Monitor", "监测"));
  setText("nav-review", copy("Review", "审阅"));
  setText("nav-delivery", copy("Deliver", "交付"));
  setText("context-lens-title", copy("Workspace Context", "工作上下文"));
  setText("context-lens-copy", copy("See the current rail, active filters, and save or share the current workspace state.", "查看当前主轨、正在生效的筛选条件，并保存或分享当前工作区状态。"));
  setText("context-lens-close", copy("Close", "关闭"));
  setText("context-save-title", copy("Save Current View", "保存当前视图"));
  setText("context-save-submit", copy("Save View", "保存视图"));
  setPlaceholder("context-save-name", copy("Ops desk / Escalations", "运营台 / 升级队列"));
  setText("context-utilities-title", copy("Workspace Utilities", "工作区工具"));
  setText("context-open-section", copy("Open Current Surface", "打开当前区块"));
  setText("context-copy-link", copy("Copy Link", "复制链接"));
  document.querySelectorAll("[data-context-section='section-triage']").forEach((button) => {
    button.textContent = copy("Open Triage", "打开分诊");
  });
  document.querySelectorAll("[data-context-section='section-story']").forEach((button) => {
    button.textContent = copy("Open Story", "打开故事");
  });
  setText("palette-open", copy("Command Palette", "快速命令"));
  setText("context-reset", copy("Reset Context", "重置上下文"));
  setText("hero-eyebrow", copy("Guided Analyst Workflow", "引导式工作流"));
  setHTML("hero-title", state.language === "zh" ? "运行任务<br>审阅信号<br>沉淀故事" : "Run Missions, Review Signal, Publish Stories");
  setText("hero-copy", copy(
    "Start with one mission draft, run it from the board, triage the inbox, promote verified evidence into a story, then wire a route when delivery should turn on.",
    "先创建一个任务草稿，再从列表执行、进入分诊、把已核验信号提升为故事，最后在需要交付时接上路由。"
  ));
  setText("refresh-all", copy("Refresh Console", "刷新控制台"));
  setText("run-due", copy("Run Due Missions", "运行待执行任务"));
  setText("jump-watch-board", copy("Open Mission Board", "查看任务列表"));
  setText("guide-step-1-title", copy("Draft Mission", "创建任务"));
  setText("guide-step-1-copy", copy("Use a preset, clone an existing watch, or enter just Name + Query to create the first watch.", "可以使用预设、复制已有任务，或者只填名称和查询词先把第一个任务建起来。"));
  setText("guide-step-2-title", copy("Run And Inspect", "执行并查看"));
  setText("guide-step-2-copy", copy("Mission Board and Cockpit run the watch, show results, and expose alert rules before review work starts.", "任务列表和任务详情负责执行任务、查看结果，并在进入审阅前暴露告警规则。"));
  setText("guide-step-3-title", copy("Triage And Promote", "分诊并提升"));
  setText("guide-step-3-copy", copy("Triage reviews inbox items, captures analyst notes, and promotes verified evidence into story drafts.", "分诊队列负责审阅收件箱条目、记录分析师备注，并把已核验的证据提升为故事草稿。"));
  setText("guide-step-4-title", copy("Set Route And Watch Delivery", "配置路由并观察交付"));
  setText("guide-step-4-copy", copy("Route Manager creates reusable sinks; mission alert rules attach them when stories are ready to notify downstream.", "路由管理先创建可复用的交付目标；当故事准备好触发下游通知时，再从任务告警规则里把它接上。"));
  setText("guide-kicker", copy("Operator Guidance", "操作提示"));
  setText("guide-panel-title", copy("Workflow Stages", "工作流阶段"));
  setText("guide-chip", copy("Start -> Monitor -> Review -> Deliver", "开始 -> 监测 -> 审阅 -> 交付"));
  setText("guide-panel-copy", copy("Create or clone a mission here. Monitoring owns runs and results, Review owns triage and stories, and advanced claim or report workspaces stay nested until they are needed.", "先在这里创建或复制任务；监测阶段负责运行和结果，审阅阶段负责分诊和故事，而主张与报告工作区会等到真正需要时再进入。"));
  setText("shortcut-focus", copy("/ focus draft", "/ 聚焦任务草稿"));
  setText("shortcut-preset", copy("1-4 load preset", "1-4 套用预设"));
  setText("shortcut-submit", copy("Cmd/Ctrl+Enter deploy", "Cmd/Ctrl+Enter 提交"));
  setText("jump-cockpit", copy("Cockpit", "任务详情"));
  setText("jump-triage", copy("Triage", "分诊"));
  setText("jump-story", copy("Stories", "故事"));
  setText("jump-ops", copy("Delivery", "交付"));
  setText("deploy-title", copy("Deploy Mission", "创建监测任务"));
  setText("deploy-copy", copy("Create one watch, add optional scope, then decide whether alert routing is needed.", "先定义监测任务，再按需补充范围和通知条件。"));
  setText("preset-title", copy("Mission Modes", "任务预设"));
  setText("preset-copy", copy("Start from an archetype when the workflow is familiar, then only adjust the fields that matter.", "如果任务模式比较固定，可以直接套用预设，再修改关键字段。"));
  setText("deck-step-1-title", copy("Required Mission Input", "基础信息"));
  setText("deck-step-1-copy", copy("Name and query define the watch. Everything else can be layered on later.", "名称和查询词决定这个任务监测什么，其余设置都可以后补。"));
  setText("label-name", copy("Name", "名称"));
  setText("label-query", copy("Query", "查询词"));
  setText("hint-name", copy("Use a short operator-facing label.", "建议填写一个便于识别的简短名称。"));
  setText("hint-query", copy("Describe the signal you want tracked.", "描述你希望持续跟踪的主题、事件或对象。"));
  setText("deck-step-2-title", copy("Scope And Cadence", "范围与频率"));
  setText("deck-step-2-copy", copy("Pick multiple platforms and sites to run them in parallel; 2+ platforms or provider=multi unlocks cross-source corroboration.", "勾选多个平台和站点即可并行采集；≥2 个平台或采集模式=multi 时会启用跨源印证加权。"));
  setText("label-schedule", copy("Schedule", "调度频率"));
  setText("label-platform", copy("Platforms", "平台（可多选）"));
  setText("label-domain", copy("Sites / Domains", "站点/域名（可多值）"));
  setText("label-provider", copy("Provider Mode", "采集模式"));
  setText("hint-schedule", copy("Manual is fine for first exploration.", "初次探索时，用手动执行就够了。"));
  setText("hint-platform", copy("Toggle chips or type a comma-separated list. Leave empty for broad discovery.", "点击芯片多选，或手动输入逗号分隔列表；留空代表全平台广泛探索。"));
  setText("hint-domain", copy("Comma-separated sites act as both search scope and alert domain guard.", "支持逗号分隔的多站点；同时作为采集范围和告警域名约束。"));
  setText("hint-provider", copy("auto = smart. multi = parallel multi-source fusion with corroboration boost.", "auto=智能选择；jina=单源；multi=多源并行融合并提升印证信号。"));
  setText("schedule-lanes-title", copy("Schedule Lanes", "常用频率"));
  setText("platform-lanes-title", copy("Platform Lanes (multi-select)", "常用平台（可多选）"));
  setText("provider-lanes-title", copy("Provider Mode", "采集模式"));
  setText("deck-step-3-title", copy("Optional Alert Gate", "通知条件（可选）"));
  setText("deck-step-3-copy", copy("Attach delivery only when the mission is ready to trigger downstream action.", "只有当这个任务需要自动通知外部时，再补充告警条件。"));
  setText("label-route", copy("Alert Route", "告警路由"));
  setText("label-keyword", copy("Alert Keyword", "告警关键词"));
  setText("label-score", copy("Min Score", "最低分数"));
  setText("label-confidence", copy("Min Confidence", "最低置信度"));
  setText("hint-route", copy("Choose a named route when the watch should notify someone.", "如果需要自动通知，就选择一个命名路由。"));
  setText("hint-keyword", copy("Use a high-signal term to reduce noise.", "用高信号关键词减少无关结果。"));
  setText("hint-score", copy("Use when you only want stronger ranked hits.", "只想保留高分结果时再设置。"));
  setText("hint-confidence", copy("Use when analyst quality matters more than coverage.", "当质量比覆盖更重要时再设置。"));
  setText("route-snap-title", copy("Route Snap", "常用路由"));
  setText("create-watch-submit", copy("Create Watch", "创建任务"));
  setText("create-watch-clear", copy("Reset Draft", "清空草稿"));
  setText("clone-title", copy("Clone Existing Mission", "从已有任务复制"));
  setText("clone-copy", copy("Fork an existing watch when the current mission is only a variation in route, threshold, or query wording.", "如果当前任务只是查询词、阈值或路由的小改动，直接复制已有任务会更快。"));
  setText("actions-title", copy("Recent Actions", "最近变更"));
  setText("actions-copy", copy("Every reversible mutation stays here briefly so you can undo false starts without losing flow.", "最近的可撤销操作会暂时保留在这里，方便你快速回退。"));
  setText("board-title", copy("Mission Board", "任务看板"));
  setText("board-copy", copy("Run missions, open the cockpit, and keep review handoff facts attached to the active board lane.", "在一个列表里完成执行任务、打开详情，并把审阅交接事实保持在当前任务工作线附近。"));
  setText("alert-stream-title", copy("Alert Stream", "告警动态"));
  setText("alert-stream-copy", copy("Read recent alert events beside route editing and health instead of treating them as a detached feed.", "把最近告警事件放在路由编辑和健康状态旁边查看，而不是再把它当成一条脱离上下文的独立信息流。"));
  setText("alert-stream-mode", copy("Events read-only", "事件只读"));
  setText("route-manager-title", copy("Route Manager", "路由管理"));
  setText("route-manager-copy", copy("Create named delivery sinks once, then attach them from Mission Intake or the Cockpit alert editor without retyping webhook or chat details.", "把命名交付路由先配置一次，后续在新建任务或任务详情的告警编辑器里直接绑定，不必重复填写 webhook 或会话信息。"));
  setText("route-manager-mode", copy("Editable", "可编辑"));
  setText("ops-title", copy("Ops Snapshot", "运行状态"));
  setText("ops-copy", copy("Watch alerting missions, story readiness, route delivery, and recent failures in one delivery slice.", "把触发告警的任务、故事就绪度、路由投递和近期失败集中到一个交付视图。"));
  setText("ai-surface-title", copy("AI Assistance Surfaces", "AI 辅助面"));
  setText("ai-surface-copy", copy("Inspect the same governed AI projection facts that CLI and MCP expose, without creating browser-only AI state.", "查看与 CLI 和 MCP 同源的 AI 投影治理事实，不在浏览器里制造私有 AI 状态。"));
  setText("ai-surface-mode", copy("Read-only", "只读"));
  setText("cockpit-title", copy("Mission Cockpit", "任务详情"));
  setText("cockpit-copy", copy("Open one mission to inspect runs, review continuity, follow-up actions, and route-backed delivery without losing the cockpit context.", "打开单个任务后，可以在不离开任务详情的前提下查看执行记录、审阅连续性、后续动作和路由交付。"));
  setText("distribution-title", copy("Distribution Health", "分发健康"));
  setText("distribution-copy", copy("See whether named delivery routes are healthy and which upstream work is feeding them before they go silent.", "提前发现命名路由是否健康，以及哪些上游工作正在给它们供流，避免进入静默失败。"));
  setText("distribution-mode", copy("Read-only", "只读"));
  setText("delivery-workspace-title", copy("Delivery Workspace", "交付工作区"));
  setText("delivery-workspace-copy", copy("Subscribe to persisted outputs, inspect one report package, and dispatch it through named routes without leaving the shell.", "在不离开当前 shell 的前提下完成持久化订阅、报告输出包审计和命名路由 dispatch。"));
  setText("delivery-workspace-mode", copy("Editable", "可编辑"));
  setText("review-advanced-kicker", copy("Secondary Review Tools", "二级审阅工具"));
  setText("review-advanced-title", copy("Claim & Report Tools", "主张与报告工具"));
  setText("review-advanced-copy", copy("Open claim composition and report assembly only when review needs structured output beyond triage and story editing.", "只有当审阅需要超出分诊和故事编辑的结构化输出时，再打开主张装配和报告编排。"));
  setText("review-advanced-chip", copy("On demand · Claim Composer · Report Studio", "按需打开 · 主张装配 · 报告工作台"));
  setText("delivery-advanced-kicker", copy("Secondary Delivery Tools", "二级交付工具"));
  setText("delivery-advanced-title", copy("AI & Route Health", "AI 与路由健康"));
  setText("delivery-advanced-copy", copy("Open AI projection inspection and route-health drill-down only when delivery needs diagnosis beyond dispatch posture and history.", "只有当交付需要超出分发姿态和历史的诊断时，再打开 AI 投影检查和路由健康钻取。"));
  setText("delivery-advanced-chip", copy("On demand · AI Assistance · Distribution Health", "按需打开 · AI 辅助 · 分发健康"));
  setText("triage-title", copy("Triage Queue", "分诊队列"));
  setText("triage-copy", copy("Review open items with one selected evidence workbench, keep analyst reasoning visible, and hand verified signal into stories without leaving the queue.", "通过一个选中证据工作台完成审阅，持续看到分析师推理，并在不离开队列的前提下把已核验信号交接给故事。"));
  setText("story-title", copy("Story Workspace", "故事工作台"));
  setText("story-copy", copy("Inspect promoted stories, evidence stacks, contradictions, and delivery readiness before the narrative leaves the browser.", "查看已提升的故事、证据堆栈、冲突点和交付就绪度，并在叙事离开浏览器前完成整理。"));
  setText("claims-title", copy("Claim Composer", "主张装配"));
  setText("claims-copy", copy("Compose source-bound claims and attach them to report sections without leaving the review lane.", "在不离开审阅主轨的前提下，编排带来源绑定的主张并把它挂进报告章节。"));
  setText("report-studio-title", copy("Report Studio", "报告工作台"));
  setText("report-studio-copy", copy("Inspect report sections, quality guardrails, and export sheets over persisted report objects.", "围绕持久化报告对象查看章节结构、质量门禁和导出查看。"));
  setText("story-mode-switch-label", copy("Workspace mode", "工作区模式"));
  setText("story-mode-board-button", copy("Board", "看板"));
  setText("story-mode-editor-button", copy("Editor", "编辑"));
  setText("story-intake-title", copy("Story Intake", "故事录入"));
  setText("story-intake-copy", copy("Capture a manual brief when a story should exist before clustering catches up, then refine it inside the workspace.", "当某个故事需要先落下来、而聚类还没跟上时，可以先手工补录，再在工作台里继续完善。"));
  setText("story-intake-mode", copy("Editable", "可编辑"));
  setText("story-inspector-kicker", copy("Story Inspector", "故事查看"));
  setText("story-inspector-title", copy("Story Export Sheet", "故事导出查看"));
  setText("story-inspector-copy", copy("Review exported markdown or the persisted story JSON without pushing raw output into the main workspace column.", "把 Markdown 导出和持久化故事 JSON 放进 sheet 查看，避免主工作台被原始输出打断。"));
  setText("story-inspector-close", copy("Close", "关闭"));
  setText("footer-note", copy("The browser is the operating surface. CLI and MCP remain first-class control planes.", "浏览器是主要操作界面；CLI 和 MCP 仍保持一等能力。"));
  setPlaceholder("command-palette-input", copy("Search actions, missions, stories, or routes", "搜索操作、任务、故事或路由"));
  setPlaceholder("input-name", copy("Launch Ops", "新品发布监测"));
  setPlaceholder("input-query", copy("OpenAI launch", "OpenAI 发布"));
  setPlaceholder("input-schedule", copy("@hourly / interval:15m", "@hourly / interval:15m"));
  setPlaceholder("input-platform", copy("twitter, reddit, hackernews", "twitter, reddit, hackernews"));
  setPlaceholder("input-domain", copy("openai.com, techcrunch.com", "openai.com, techcrunch.com"));
  setPlaceholder("input-route", copy("ops-webhook", "ops-webhook"));
  setPlaceholder("input-keyword", copy("launch", "发布"));
  setPlaceholder("input-score", copy("70", "70"));
  setPlaceholder("input-confidence", copy("0.8", "0.8"));
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.classList.toggle("active", String(button.dataset.lang || "") === state.language);
  });
  renderWorkspaceModeChrome();
  renderTopbarContext();
}

state.language = detectInitialLanguage();

function showToast(message, tone = "info") {
  const rack = $("toast-rack");
  if (!rack) {
    return;
  }
  const toast = document.createElement("div");
  toast.className = `toast ${tone}`;
  toast.innerHTML = `
    <div class="mono">${copy("mission signal", "任务信号")} / ${localizeWord(tone)}</div>
    <div style="margin-top:6px;">${escapeHtml(message)}</div>
  `;
  rack.appendChild(toast);
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "opacity .18s ease, transform .18s ease";
    window.setTimeout(() => toast.remove(), 220);
  }, 2800);
}

window.alert = (message) => showToast(String(message || ""), "error");

function reportError(error, prefix = "") {
  console.error(error);
  const message = error && error.message ? error.message : String(error || "Unknown error");
  showToast(prefix ? `${prefix}: ${message}` : message, "error");
}

function focusCreateWatchDeck(fieldName = "query") {
  const form = $("create-watch-form");
  if (!form) {
    return;
  }
  jumpToSection("section-intake");
  window.setTimeout(() => {
    form.scrollIntoView({ block: "nearest", behavior: "smooth" });
    const field = form.elements.namedItem(fieldName);
    if (field && typeof field.focus === "function") {
      field.focus();
      if (typeof field.select === "function") {
        field.select();
      }
    }
  }, 140);
}

function scheduleModeLabel(value) {
  const schedule = String(value || "").trim();
  if (!schedule || schedule === "manual") {
    return copy("manual dispatch", "手动执行");
  }
  if (schedule.startsWith("interval:")) {
    return state.language === "zh"
      ? `频率 ${schedule.replace("interval:", "")}`
      : `cadence ${schedule.replace("interval:", "")}`;
  }
  if (schedule.startsWith("@")) {
    return state.language === "zh" ? `Cron 别名 ${schedule}` : `cron alias ${schedule}`;
  }
  return schedule;
}

function buildCreateWatchPreview(draftInput) {
  const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
  const requiredReady = Boolean(draft.name.trim() && draft.query.trim());
  const platformList = parseListField(draft.platform);
  const siteList = parseListField(draft.domain);
  const providerMode = (draft.provider || "").trim().toLowerCase();
  const crossVerify = platformList.length >= 2 || providerMode === "multi";
  const alertArmed = Boolean(
    draft.route.trim() ||
    draft.keyword.trim() ||
    siteList.length ||
    Number(draft.min_score || 0) > 0 ||
    Number(draft.min_confidence || 0) > 0,
  );
  const readiness = Math.min(
    100,
    (draft.name.trim() ? 34 : 0) +
    (draft.query.trim() ? 34 : 0) +
    (draft.schedule.trim() ? 8 : 0) +
    (platformList.length ? 8 : 0) +
    ((draft.route.trim() || draft.keyword.trim() || siteList.length) ? 8 : 0) +
    ((draft.min_score.trim() || draft.min_confidence.trim()) ? 8 : 0),
  );
  const platformLabel = platformList.length
    ? platformList.join(", ")
    : copy("cross-platform", "跨平台");
  const filterParts = [];
  if (platformList.length) filterParts.push(platformList.join(", "));
  if (siteList.length) filterParts.push(siteList.join(", "));
  if (draft.keyword.trim()) filterParts.push(draft.keyword.trim());
  return {
    draft,
    requiredReady,
    alertArmed,
    readiness,
    platformList,
    siteList,
    providerMode: providerMode || "auto",
    crossVerify,
    summary: draft.query.trim()
      ? phrase(
          "Track {query} with {schedule} across {platform} surfaces.",
          "围绕 {query} 以 {schedule} 跟踪 {platform} 信号。",
          {
            query: draft.query.trim(),
            schedule: scheduleModeLabel(draft.schedule),
            platform: platformLabel,
          },
        )
      : copy("Add a query to project the mission into the live preview lane.", "填入查询词后，任务会立即投射到实时预览区。"),
    scoreLabel: draft.min_score.trim() ? copy(`score >= ${draft.min_score.trim()}`, `分数 >= ${draft.min_score.trim()}`) : copy("score gate unset", "未设置分数门槛"),
    confidenceLabel: draft.min_confidence.trim() ? copy(`confidence >= ${draft.min_confidence.trim()}`, `置信度 >= ${draft.min_confidence.trim()}`) : copy("confidence gate unset", "未设置置信度门槛"),
    filtersLabel: filterParts.length ? filterParts.join(" / ") : copy("no scope filter", "未设置范围过滤"),
    routeLabel: draft.route.trim() || copy("route not attached", "未绑定路由"),
    scheduleLabel: scheduleModeLabel(draft.schedule),
    crossVerifyLabel: crossVerify
      ? copy("multi-source parallel + cross-verify enabled", "已启用多源并行 + 交叉印证")
      : copy("single-source sweep", "单源采集"),
  };
}

function syncCreateWatchForm() {
  const form = $("create-watch-form");
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  if (!form) {
    return;
  }
  createWatchFormFields.forEach((fieldName) => {
    const field = form.elements.namedItem(fieldName);
    if (!field || field.value === draft[fieldName]) {
      return;
    }
    field.value = draft[fieldName];
  });
}

function collectCreateWatchDraft(form) {
  if (!form) {
    return defaultCreateWatchDraft();
  }
  const next = defaultCreateWatchDraft();
  createWatchFormFields.forEach((fieldName) => {
    const field = form.elements.namedItem(fieldName);
    next[fieldName] = field ? String(field.value ?? "") : "";
  });
  return normalizeCreateWatchDraft(next);
}

function setCreateWatchDraft(nextDraft, presetId = "", editingId = state.createWatchEditingId) {
  state.createWatchDraft = normalizeCreateWatchDraft(nextDraft || defaultCreateWatchDraft());
  state.createWatchPresetId = presetId;
  state.createWatchEditingId = String(editingId || "").trim();
  const startFeedback = state.stageFeedback?.start;
  if (startFeedback && ["blocked", "warning", "no_result"].includes(String(startFeedback.kind || "").trim().toLowerCase())) {
    state.stageFeedback.start = null;
  }
  syncCreateWatchForm();
  persistCreateWatchDraft();
  renderCreateWatchDeck();
  queueCreateWatchSuggestions();
  setContextRouteFromWatch();
}

function updateCreateWatchDraft(patch = {}, presetId = "") {
  setCreateWatchDraft({
    ...normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft()),
    ...patch,
  }, presetId);
}

async function refreshCreateWatchSuggestions(force = false) {
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  if (!force && !(draft.name.trim() || draft.query.trim() || draft.keyword.trim())) {
    state.createWatchSuggestions = null;
    renderCreateWatchDeck();
    return;
  }
  state.loading.suggestions = true;
  renderCreateWatchDeck();
  try {
    state.createWatchSuggestions = await api("/api/console/deck/suggestions", {
      method: "POST",
      payload: draft,
    });
  } catch (error) {
    state.createWatchSuggestions = null;
    reportError(error, "Load mission suggestions");
  } finally {
    state.loading.suggestions = false;
    renderCreateWatchDeck();
  }
}

function queueCreateWatchSuggestions(force = false) {
  if (state.createWatchSuggestionTimer) {
    window.clearTimeout(state.createWatchSuggestionTimer);
  }
  state.createWatchSuggestionTimer = window.setTimeout(() => {
    refreshCreateWatchSuggestions(force).catch((error) => reportError(error, "Load mission suggestions"));
  }, force ? 20 : 220);
}

function renderCreateWatchDeck() {
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  const editingId = String(state.createWatchEditingId || "").trim();
  const editing = Boolean(editingId);
  const advancedOpen = isCreateWatchAdvancedOpen(draft);
  const preview = buildCreateWatchPreview(draft);
  renderIntakeSectionSummary(preview);
  renderFormSuggestionLists();
  const presetPanel = $("create-watch-preset-panel");
  const presetRoot = $("create-watch-presets");
  const scheduleRoot = $("create-watch-schedule-picks");
  const platformRoot = $("create-watch-platform-picks");
  const providerRoot = $("create-watch-provider-picks");
  const crossVerifyHintRoot = $("create-watch-cross-verify-hint");
  const routeRoot = $("create-watch-route-picks");
  const advancedTitle = $("deck-advanced-title");
  const advancedCopy = $("deck-advanced-copy");
  const advancedToggle = $("create-watch-advanced-toggle");
  const advancedSummary = $("create-watch-advanced-summary");
  const advancedPanel = $("create-watch-advanced-panel");
  const clonePanel = $("create-watch-clone-panel");
  const cloneRoot = $("create-watch-clones");
  const previewRoot = $("create-watch-preview");
  const suggestionRoot = $("create-watch-suggestions");
  const feedbackRoot = $("create-watch-feedback");
  const stageHudRoot = $("stage-hud");
  const submitButton = $("create-watch-submit");
  const clearButton = $("create-watch-clear");
  const deployTitle = $("deploy-title");
  const deployCopy = $("deploy-copy");

  if (deployTitle) {
    deployTitle.textContent = editing ? copy("Edit Mission", "编辑监测任务") : copy("Deploy Mission", "创建监测任务");
  }
  if (deployCopy) {
    deployCopy.textContent = editing
      ? copy("Update one existing watch in place using the same mission deck.", "沿用同一套任务草稿面板，直接原位修改已有任务。")
      : copy("Create one watch, add optional scope, then decide whether alert routing is needed.", "先定义监测任务，再按需补充范围和通知条件。");
  }
  if (advancedTitle) {
    advancedTitle.textContent = editing ? copy("Refine Scope Carefully", "精细调整范围") : copy("Keep It Simple First", "先从简单输入开始");
  }
  if (advancedCopy) {
    advancedCopy.textContent = advancedOpen
      ? copy("Only fill the extra controls you actually need. Empty fields keep the mission broad and easier to operate.", "只填写真正需要的额外条件；留空代表任务保持更宽、更易操作。")
      : copy("Most missions only need Name and Query. Open advanced settings only when you need scope or alert delivery.", "大多数任务只需要名称和查询词；只有在要限定范围或接入告警时，再展开高级设置。");
  }
  if (advancedToggle) {
    advancedToggle.textContent = advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置");
    advancedToggle.setAttribute("aria-expanded", String(advancedOpen));
  }
  if (advancedSummary) {
    advancedSummary.innerHTML = summarizeCreateWatchAdvanced(draft).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");
  }
  if (advancedPanel) {
    advancedPanel.classList.toggle("collapsed", !advancedOpen);
    advancedPanel.setAttribute("aria-hidden", String(!advancedOpen));
  }
  if (presetPanel) {
    presetPanel.hidden = editing;
  }
  if (clonePanel) {
    clonePanel.hidden = editing;
  }

  if (submitButton) {
    submitButton.textContent = editing ? copy("Save Changes", "保存修改") : copy("Create Watch", "创建任务");
  }
  if (clearButton) {
    clearButton.textContent = editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿");
  }

  if (presetRoot) {
    presetRoot.innerHTML = `
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Mission presets", "任务预设"))}">
        ${createWatchPresets.map((preset, index) => `
          <button
            class="ui-segment-button ${state.createWatchPresetId === preset.id ? "active" : ""}"
            type="button"
            data-create-watch-preset="${preset.id}"
            title="${escapeHtml(copy(preset.description, preset.zhDescription || preset.description))}"
            aria-pressed="${state.createWatchPresetId === preset.id ? "true" : "false"}"
          >${index + 1}. ${escapeHtml(copy(preset.label, preset.zhLabel || preset.label))}</button>
        `).join("")}
      </div>
    `;
  }

  if (scheduleRoot) {
    scheduleRoot.innerHTML = `
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Mission schedule lanes", "任务频率选择"))}">
        ${scheduleLaneOptions.map((option) => `
          <button
            class="ui-segment-button ${draft.schedule.trim() === option.value ? "active" : ""}"
            type="button"
            data-create-watch-schedule="${option.value}"
            aria-pressed="${draft.schedule.trim() === option.value ? "true" : "false"}"
          >${escapeHtml(option.value === "manual" ? copy("manual", "手动") : option.label)}</button>
        `).join("")}
      </div>
    `;
  }

  if (platformRoot) {
    const activePlatformSet = new Set(preview.platformList);
    platformRoot.innerHTML = `
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Mission platform lanes", "任务平台选择"))}">
        ${platformLaneOptions.map((option) => `
          <button
            class="ui-segment-button ${activePlatformSet.has(option.value) ? "active" : ""}"
            type="button"
            data-create-watch-platform="${option.value}"
            aria-pressed="${activePlatformSet.has(option.value) ? "true" : "false"}"
          >${escapeHtml(option.label)}</button>
        `).join("")}
      </div>
    `;
  }

  if (providerRoot) {
    const providerMode = preview.providerMode || "auto";
    providerRoot.innerHTML = `
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Search provider mode", "采集提供者模式"))}">
        ${providerLaneOptions.map((option) => `
          <button
            class="ui-segment-button ${providerMode === option.value ? "active" : ""}"
            type="button"
            data-create-watch-provider="${option.value}"
            aria-pressed="${providerMode === option.value ? "true" : "false"}"
          >${escapeHtml(copy(option.enLabel, option.zhLabel))}</button>
        `).join("")}
      </div>
    `;
  }

  if (crossVerifyHintRoot) {
    crossVerifyHintRoot.textContent = preview.crossVerify
      ? copy(
          "Multi-source parallel is on. Platforms run concurrently and items confirmed by 2+ sources get corroboration priority.",
          "多源并行已开启：各平台并行采集，被 2 个及以上来源印证的信号会被优先提升。"
        )
      : copy(
          "Pick 2+ platforms or switch provider to multi to enable cross-source corroboration.",
          "选择 2 个及以上平台，或将采集模式切到 multi，即可启用跨源印证。"
        );
  }

  if (routeRoot) {
    const routeButtons = state.routes.length
      ? `
          <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Mission route snaps", "任务路由选择"))}">
            ${state.routes.slice(0, 6).map((route) => `
              <button
                class="ui-segment-button ${draft.route.trim() === String(route.name || "").trim() ? "active" : ""}"
                type="button"
                data-create-watch-route="${escapeHtml(route.name || "")}"
                aria-pressed="${draft.route.trim() === String(route.name || "").trim() ? "true" : "false"}"
              >${escapeHtml(route.name || "unnamed-route")}</button>
            `).join("")}
          </div>
        `
      : `<span class="chip">${copy("No named routes", "暂无命名路由")}</span>`;
    routeRoot.innerHTML = routeButtons;
  }

  if (cloneRoot) {
    const cloneButtons = state.watches.length
      ? state.watches.slice(0, 6).map((watch) => `
          <button class="btn-secondary" type="button" data-create-watch-clone="${escapeHtml(watch.id)}">${copy("Clone", "复制")} · ${escapeHtml(watch.name || watch.id)}</button>
        `).join("")
      : `<span class="chip">${copy("No mission to clone", "暂无可克隆任务")}</span>`;
    cloneRoot.innerHTML = cloneButtons;
  }

  if (previewRoot) {
    previewRoot.className = `card mission-preview ${preview.requiredReady ? "ready" : ""}`;
    previewRoot.innerHTML = `
      <div class="card-top">
        <div>
          <div class="mono">${copy("mission brief", "任务概览")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(draft.name.trim() || copy("Unnamed Mission", "未命名任务"))}</h3>
        </div>
        <span class="chip ${preview.requiredReady ? "ok" : "hot"}">${preview.requiredReady ? copy("ready", "就绪") : copy("needs query/name", "缺少名称或查询词")}</span>
      </div>
      <div class="panel-sub">${escapeHtml(preview.summary)}</div>
      <div class="preview-meter">
        <div class="preview-meter-fill" style="width:${preview.readiness}%;"></div>
      </div>
      <div class="meta">
        <span>${copy("mode", "模式")}=${editing ? copy("edit existing", "编辑已有任务") : copy("create new", "新建任务")}</span>
        <span>${copy("readiness", "就绪度")}=${preview.readiness}%</span>
        <span>${copy("alert", "告警")}=${preview.alertArmed ? copy("armed", "已启用") : copy("passive", "未启用")}</span>
        <span>${copy("schedule", "频率")}=${escapeHtml(preview.scheduleLabel)}</span>
        <span>${copy("collection", "采集")}=${escapeHtml(preview.crossVerifyLabel)}</span>
        <span>${copy("provider", "模式")}=${escapeHtml(preview.providerMode)}</span>
      </div>
      <div class="preview-grid">
        <div class="preview-line">
          <div class="preview-label">${copy("Scope", "范围")}</div>
          <div class="preview-value">${escapeHtml(preview.filtersLabel)}</div>
        </div>
        <div class="preview-line">
          <div class="preview-label">${copy("Route", "路由")}</div>
          <div class="preview-value">${escapeHtml(preview.routeLabel)}</div>
        </div>
        <div class="preview-line">
          <div class="preview-label">${copy("Score Gate", "分数门槛")}</div>
          <div class="preview-value">${escapeHtml(preview.scoreLabel)}</div>
        </div>
        <div class="preview-line">
          <div class="preview-label">${copy("Confidence Gate", "置信度门槛")}</div>
          <div class="preview-value">${escapeHtml(preview.confidenceLabel)}</div>
        </div>
      </div>
    `;
  }

  if (suggestionRoot) {
    if (state.loading.suggestions) {
      suggestionRoot.innerHTML = `
        <div class="mono">${copy("mission suggestions", "任务建议")}</div>
        <div class="panel-sub">${copy("Deriving route, cadence, and duplicate signals from the current repository state.", "正在基于当前仓库状态推导路由、频率和重复信号。")}</div>
        <div class="stack" style="margin-top:12px;">${skeletonCard(4)}</div>
        ${buildMissionGuidanceSurface(preview)}
      `;
    } else if (!state.createWatchSuggestions) {
      suggestionRoot.innerHTML = `
        <div class="mono">${copy("mission suggestions", "任务建议")}</div>
        <div class="panel-sub">${copy("Start typing a mission draft and the deck will derive cadence, route, and duplicate pressure from current watches and stories.", "开始输入任务草稿后，系统会根据现有任务和故事自动推导频率、路由与重复风险。")}</div>
        ${buildMissionGuidanceSurface(preview)}
      `;
    } else {
      const suggestions = state.createWatchSuggestions;
      const warningBlock = Array.isArray(suggestions.warnings) && suggestions.warnings.length
        ? `<div class="suggestion-list">${suggestions.warnings.map((item) => `<div class="mini-item">${escapeHtml(item)}</div>`).join("")}</div>`
        : `<div class="panel-sub">${copy("No active conflict or delivery warning for this draft.", "当前草稿没有冲突或交付告警。")}</div>`;
      const similarWatches = Array.isArray(suggestions.similar_watches) ? suggestions.similar_watches : [];
      const relatedStories = Array.isArray(suggestions.related_stories) ? suggestions.related_stories : [];
      suggestionRoot.innerHTML = `
        <div class="card-top">
          <div>
            <div class="mono">${copy("mission suggestions", "任务建议")}</div>
            <div class="panel-sub" style="margin-top:8px;">${escapeHtml(suggestions.summary || "")}</div>
          </div>
          <button class="btn-secondary" id="apply-all-suggestions" type="button">${copy("Apply All", "全部应用")}</button>
        </div>
        <div class="suggestion-grid">
          <div class="preview-grid">
            <div class="preview-line">
              <div class="preview-label">${copy("Cadence", "频率")}</div>
              <div class="preview-value">${escapeHtml(suggestions.recommended_schedule || "-")}</div>
              <div class="panel-sub">${escapeHtml(suggestions.schedule_reason || "")}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${copy("Platform", "平台")}</div>
              <div class="preview-value">${escapeHtml(suggestions.recommended_platform || "-")}</div>
              <div class="panel-sub">${escapeHtml(suggestions.platform_reason || "")}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${copy("Route", "路由")}</div>
              <div class="preview-value">${escapeHtml(suggestions.recommended_route || "-")}</div>
              <div class="panel-sub">${escapeHtml(suggestions.route_reason || "")}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${copy("Scope Hints", "范围提示")}</div>
              <div class="preview-value">${escapeHtml(suggestions.recommended_keyword || "-")} / ${escapeHtml(suggestions.recommended_domain || "-")}</div>
              <div class="panel-sub">${escapeHtml(suggestions.keyword_reason || suggestions.domain_reason || "")}</div>
            </div>
          </div>
          <div class="actions">
            <button class="btn-secondary" type="button" data-suggestion-apply="schedule">${copy("Use", "采用")} · ${escapeHtml(suggestions.recommended_schedule || "schedule")}</button>
            <button class="btn-secondary" type="button" data-suggestion-apply="platform">${copy("Use", "采用")} · ${escapeHtml(suggestions.recommended_platform || "platform")}</button>
            <button class="btn-secondary" type="button" data-suggestion-apply="route">${copy("Use", "采用")} · ${escapeHtml(suggestions.recommended_route || "route")}</button>
            <button class="btn-secondary" type="button" data-suggestion-apply="keyword">${copy("Use", "采用")} · ${escapeHtml(suggestions.recommended_keyword || "keyword")}</button>
            <button class="btn-secondary" type="button" data-suggestion-apply="thresholds">${copy("Use score/confidence", "采用分数/置信度")}</button>
          </div>
          <div class="stack">
            <div class="mono">${copy("Warnings", "提醒")}</div>
            ${warningBlock}
          </div>
          <div class="preview-grid">
            <div class="stack">
              <div class="mono">${copy("Similar Missions", "相似任务")}</div>
              ${similarWatches.length ? similarWatches.map((item) => `<div class="mini-item">${escapeHtml(item.name)} | ${copy("similarity", "相似度")}=${Number(item.similarity || 0).toFixed(2)} | ${escapeHtml(item.schedule || copy("manual", "手动"))}</div>`).join("") : `<div class="panel-sub">${copy("No mission conflict found.", "未发现任务冲突。")}</div>`}
            </div>
            <div class="stack">
              <div class="mono">${copy("Related Stories", "相关故事")}</div>
              ${relatedStories.length ? relatedStories.map((item) => `<div class="mini-item">${escapeHtml(item.title)} | ${copy("similarity", "相似度")}=${Number(item.similarity || 0).toFixed(2)} | ${copy("items", "条目")}=${item.item_count || 0}</div>`).join("") : `<div class="panel-sub">${copy("No story cluster overlap found.", "未发现故事簇重叠。")}</div>`}
            </div>
          </div>
        </div>
        ${buildMissionGuidanceSurface(preview, suggestions)}
      `;
      suggestionRoot.querySelector("#apply-all-suggestions")?.addEventListener("click", () => {
        const patch = suggestions.autofill_patch || {};
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft(patch);
        showToast(copy("Applied suggested mission defaults", "已应用建议的任务默认值"), "success");
      });
      suggestionRoot.querySelectorAll("[data-suggestion-apply]").forEach((button) => {
        button.addEventListener("click", () => {
          const patch = suggestions.autofill_patch || {};
          const field = String(button.dataset.suggestionApply || "").trim();
          if (field === "thresholds") {
            state.createWatchAdvancedOpen = true;
            updateCreateWatchDraft({
              min_score: String(patch.min_score || ""),
              min_confidence: String(patch.min_confidence || ""),
            });
            return;
          }
          if (!field || !(field in patch)) {
            return;
          }
          if (["schedule", "platform", "route", "keyword", "domain", "min_score", "min_confidence"].includes(field)) {
            state.createWatchAdvancedOpen = true;
          }
          updateCreateWatchDraft({ [field]: String(patch[field] || "") });
        });
      });
    }
    wireLifecycleGuideActions(suggestionRoot);
    scheduleCanvasTextFit(suggestionRoot);
  }

  if (feedbackRoot) {
    if (editing) {
      feedbackRoot.textContent = preview.requiredReady
        ? copy(
            `Editing ${editingId}. Use Cmd/Ctrl+Enter to save${preview.alertArmed ? " with alert gating." : "."}`,
            `正在编辑 ${editingId}。使用 Cmd/Ctrl+Enter 保存${preview.alertArmed ? "，并带上告警门槛。" : "。"}`,
          )
        : copy(
            `Editing ${editingId}. Name and Query are still required before saving.`,
            `正在编辑 ${editingId}。保存前仍需填写名称和查询词。`,
          );
    } else {
      feedbackRoot.textContent = preview.requiredReady
        ? copy(
            `Deck armed. Use Cmd/Ctrl+Enter to dispatch${preview.alertArmed ? " with alert gating." : "."}`,
            `草稿已就绪。使用 Cmd/Ctrl+Enter 提交${preview.alertArmed ? "，并带上告警门槛。" : "。"}`,
          )
        : copy("Required fields: Name and Query. Use / to focus the mission deck.", "必填字段：名称和查询词。按 / 可快速聚焦任务草稿。");
    }
  }

  if (stageHudRoot) {
    stageHudRoot.innerHTML = `
      <div class="card-top">
        <div>
          <div class="mono">${copy("Live Mission Projection", "实时任务投影")}</div>
          <div class="stage-hud-title">${escapeHtml(draft.name.trim() || draft.query.trim() || copy("Awaiting Mission Draft", "等待任务草稿"))}</div>
        </div>
        <span class="chip ${preview.requiredReady ? "ok" : ""}">${preview.requiredReady ? copy("synced", "已同步") : copy("draft", "草稿")}</span>
      </div>
      <div class="stage-hud-summary">${escapeHtml(preview.summary)}</div>
      <div class="stage-hud-meta">
        <span class="chip">${escapeHtml(preview.scheduleLabel)}</span>
        <span class="chip">${escapeHtml(preview.filtersLabel)}</span>
        <span class="chip ${preview.alertArmed ? "hot" : ""}">${preview.alertArmed ? copy("alert armed", "告警已启用") : copy("passive watch", "仅监测")}</span>
      </div>
    `;
  }
  renderActionHistory();
}

function createWatchDraftFromMissionDetail(detail, { copyName = false } = {}) {
  const firstRule = Array.isArray(detail.alert_rules) && detail.alert_rules.length ? detail.alert_rules[0] : {};
  const platformList = Array.isArray(detail.platforms) ? detail.platforms : [];
  const detailSites = Array.isArray(detail.sites) ? detail.sites : [];
  const ruleDomains = Array.isArray(firstRule.domains) ? firstRule.domains : [];
  const domainList = detailSites.length ? detailSites : ruleDomains;
  const providerValue = String(detail.provider || "").trim().toLowerCase();
  return {
    name: copyName && detail.name ? `${detail.name} copy` : (detail.name || ""),
    schedule: detail.schedule || "",
    query: detail.query || "",
    platform: formatListField(platformList),
    domain: formatListField(domainList),
    provider: ["auto", "jina", "multi"].includes(providerValue) ? providerValue : "",
    route: Array.isArray(firstRule.routes) && firstRule.routes.length ? firstRule.routes[0] : "",
    keyword: Array.isArray(firstRule.keyword_any) && firstRule.keyword_any.length ? firstRule.keyword_any[0] : "",
    min_score: firstRule.min_score ? String(firstRule.min_score) : "",
    min_confidence: firstRule.min_confidence ? String(firstRule.min_confidence) : "",
  };
}

async function editMissionInCreateWatch(identifier) {
  if (!identifier) {
    return;
  }
  const detail = state.watchDetails[identifier] || await api(`/api/watches/${identifier}`);
  state.watchDetails[identifier] = detail;
  state.createWatchAdvancedOpen = true;
  setCreateWatchDraft(createWatchDraftFromMissionDetail(detail), "", detail.id || identifier);
  showToast(
    state.language === "zh"
      ? `已载入任务编辑：${detail.name || identifier}`
      : `Editing mission: ${detail.name || identifier}`,
    "success",
  );
  focusCreateWatchDeck("name");
}

async function cloneMissionIntoCreateWatch(identifier) {
  if (!identifier) {
    return;
  }
  const detail = state.watchDetails[identifier] || await api(`/api/watches/${identifier}`);
  state.watchDetails[identifier] = detail;
  state.createWatchAdvancedOpen = true;
  setCreateWatchDraft(createWatchDraftFromMissionDetail(detail, { copyName: true }), "", "");
  showToast(
    state.language === "zh"
      ? `已从 ${detail.name || identifier} 克隆任务草稿`
      : `Mission deck cloned from ${detail.name || identifier}`,
    "success",
  );
  focusCreateWatchDeck("name");
}

function bindCreateWatchDeck() {
  const form = $("create-watch-form");
  const presetRoot = $("create-watch-presets");
  const scheduleRoot = $("create-watch-schedule-picks");
  const platformRoot = $("create-watch-platform-picks");
  const providerRoot = $("create-watch-provider-picks");
  const routeRoot = $("create-watch-route-picks");
  const cloneRoot = $("create-watch-clones");
  const clearButton = $("create-watch-clear");
  const advancedToggle = $("create-watch-advanced-toggle");
  if (!form) {
    return;
  }

  syncCreateWatchForm();
  renderCreateWatchDeck();

  form.addEventListener("input", () => {
    state.createWatchPresetId = "";
    state.createWatchDraft = collectCreateWatchDraft(form);
    persistCreateWatchDraft();
    renderCreateWatchDeck();
    queueCreateWatchSuggestions();
  });

  form.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && String(event.key || "").toLowerCase() === "enter") {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  advancedToggle?.addEventListener("click", () => {
    state.createWatchAdvancedOpen = !isCreateWatchAdvancedOpen(state.createWatchDraft || defaultCreateWatchDraft());
    renderCreateWatchDeck();
  });

  presetRoot?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-create-watch-preset]");
    if (!button) {
      return;
    }
    const preset = createWatchPresets.find((candidate) => candidate.id === button.dataset.createWatchPreset);
    if (!preset) {
      return;
    }
    state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
    setCreateWatchDraft(preset.values, preset.id, "");
    showToast(
      state.language === "zh"
        ? `${preset.zhLabel || preset.label} 已载入任务草稿`
        : `${preset.label} loaded into the mission deck`,
      "success",
    );
    focusCreateWatchDeck("query");
  });

  scheduleRoot?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-create-watch-schedule]");
    if (!button) {
      return;
    }
    state.createWatchAdvancedOpen = true;
    updateCreateWatchDraft({ schedule: String(button.dataset.createWatchSchedule || "") });
  });

  platformRoot?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-create-watch-platform]");
    if (!button) {
      return;
    }
    state.createWatchAdvancedOpen = true;
    const currentDraft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
    const nextPlatform = toggleListValue(currentDraft.platform, String(button.dataset.createWatchPlatform || ""));
    updateCreateWatchDraft({ platform: nextPlatform });
  });

  providerRoot?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-create-watch-provider]");
    if (!button) {
      return;
    }
    state.createWatchAdvancedOpen = true;
    const value = String(button.dataset.createWatchProvider || "").trim().toLowerCase();
    const next = ["auto", "jina", "multi"].includes(value) ? value : "auto";
    updateCreateWatchDraft({ provider: next });
  });

  routeRoot?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-create-watch-route]");
    if (!button) {
      return;
    }
    state.createWatchAdvancedOpen = true;
    updateCreateWatchDraft({ route: String(button.dataset.createWatchRoute || "") });
  });

  cloneRoot?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-create-watch-clone]");
    if (!button) {
      return;
    }
    button.disabled = true;
    try {
      await cloneMissionIntoCreateWatch(String(button.dataset.createWatchClone || ""));
    } catch (error) {
      reportError(error, copy("Clone mission", "克隆任务"));
    } finally {
      button.disabled = false;
    }
  });

  clearButton?.addEventListener("click", () => {
    const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
    state.createWatchAdvancedOpen = null;
    setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
    showToast(
      wasEditing
        ? copy("Mission edit cancelled", "已取消任务编辑")
        : copy("Mission deck draft cleared", "已清空任务草稿"),
      "success",
    );
    focusCreateWatchDeck("name");
  });
}

function bindRouteDeck() {
  if (!state.routeDraft) {
    state.routeDraft = defaultRouteDraft();
  }
  renderRouteDeck();
}

function bindStoryDeck() {
  if (!state.storyDraft) {
    state.storyDraft = defaultStoryDraft();
  }
  renderStoryCreateDeck();
  const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
  if (storyWorkspaceModeSwitch) {
    storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        const nextMode = String(button.dataset.storyWorkspaceMode || "").trim().toLowerCase();
        applyStoryWorkspaceMode(nextMode, { persist: true, syncUrl: true });
      });
    });
  }
}

function bindHeroStageMotion() {
  const hero = $("hero-main");
  const stage = hero?.querySelector(".hero-stage");
  const visual = hero?.querySelector(".hero-visual");
  const globe = hero?.querySelector(".stage-globe");
  const leftRing = hero?.querySelector(".stage-ring-left");
  const rightRing = hero?.querySelector(".stage-ring-right");
  const leftConsole = hero?.querySelector(".stage-console-left");
  const rightConsole = hero?.querySelector(".stage-console-right");
  if (!hero || !stage || !visual || !globe || !leftRing || !rightRing || !leftConsole || !rightConsole) {
    return;
  }

  const reset = () => {
    stage.style.transform = "";
    visual.style.transform = "";
    globe.style.transform = "translateX(-50%)";
    leftRing.style.transform = "";
    rightRing.style.transform = "";
    leftConsole.style.transform = "";
    rightConsole.style.transform = "";
  };

  hero.addEventListener("pointermove", (event) => {
    const rect = hero.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) - 0.5;
    const y = ((event.clientY - rect.top) / rect.height) - 0.5;
    stage.style.transform = `perspective(1200px) rotateX(${-y * 6}deg) rotateY(${x * 7}deg)`;
    visual.style.transform = `scale(1.05) translate(${x * -16}px, ${y * -12}px)`;
    globe.style.transform = `translate(calc(-50% + ${x * 20}px), ${y * 12}px)`;
    leftRing.style.transform = `translateX(${x * -10}px)`;
    rightRing.style.transform = `translateX(${x * 10}px)`;
    leftConsole.style.transform = `translate(${x * -8}px, ${y * 6}px)`;
    rightConsole.style.transform = `translate(${x * 8}px, ${y * 6}px)`;
  });

  hero.addEventListener("pointerleave", reset);
  reset();
}

function rerenderLanguageSensitiveViews() {
  applyLanguageChrome();
  renderOverview();
  renderWatches();
  renderWatchDetail();
  renderAlerts();
  renderRoutes();
  renderRouteHealth();
  renderStatus();
  renderTriage();
  renderStories();
  renderCreateWatchDeck();
  renderCommandPalette();
}

function setLanguage(nextLanguage) {
  const normalized = String(nextLanguage || "").trim().toLowerCase() === "zh" ? "zh" : "en";
  state.language = normalized;
  safeLocalStorageSet(languageStorageKey, normalized);
  rerenderLanguageSensitiveViews();
}

function bindLanguageSwitch() {
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextLanguage = String(button.dataset.lang || "").trim();
      if (!nextLanguage || nextLanguage === state.language) {
        return;
      }
      setLanguage(nextLanguage);
    });
  });
}

function bindSectionJumps() {
  document.querySelectorAll("[data-jump-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = String(button.dataset.jumpTarget || "").trim();
      jumpToSection(targetId);
    });
  });
}

function bindSectionTracking() {
  const sectionIds = [
    "section-intake",
    "section-board",
    "section-cockpit",
    "section-triage",
    "section-story",
    "section-claims",
    "section-report-studio",
    "section-ops",
  ];
  const sections = sectionIds
    .map((sectionId) => document.getElementById(sectionId))
    .filter(Boolean);
  if (!sections.length) {
    return;
  }
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => right.intersectionRatio - left.intersectionRatio);
      if (!visible.length) {
        return;
      }
      const nextSectionId = normalizeSectionId(visible[0].target.id);
      if (nextSectionId === state.activeSectionId) {
        return;
      }
      state.activeSectionId = nextSectionId;
      renderWorkspaceModeChrome();
      renderTopbarContext();
      hydrateBoardForSection(nextSectionId).catch((error) => {
        reportError(error, copy("Load workspace stage", "加载工作阶段"));
      });
    }, {
      root: null,
      rootMargin: "-18% 0px -56% 0px",
      threshold: [0.18, 0.35, 0.55],
    });
    sections.forEach((section) => observer.observe(section));
  }
  window.addEventListener("hashchange", () => {
    state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);
    renderWorkspaceModeChrome();
    renderTopbarContext();
    hydrateBoardForSection(state.activeSectionId).catch((error) => {
      reportError(error, copy("Load workspace stage", "加载工作阶段"));
    });
  });
}

function buildCommandPaletteEntries() {
  const entries = [
    {
      id: "refresh",
      group: copy("system", "系统"),
      title: copy("Refresh Console", "刷新控制台"),
      subtitle: copy("Reload overview, missions, triage, stories, and ops.", "重新加载总览、任务、分诊、故事和运维视图。"),
      run: async () => {
        await refreshBoard();
        showToast(copy("Console refreshed", "控制台已刷新"), "success");
      },
    },
    {
      id: "run-due",
      group: copy("system", "系统"),
      title: copy("Run Due Missions", "执行到点任务"),
      subtitle: copy("Dispatch every mission currently due.", "立即执行当前所有到点任务。"),
      run: async () => {
        await api("/api/watches/run-due", { method: "POST", payload: { limit: 0 } });
        await refreshBoard();
        showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
      },
    },
    {
      id: "reset-context",
      group: copy("system", "系统"),
      title: copy("Reset Workspace Context", "重置工作上下文"),
      subtitle: copy("Clear mission, triage, story, and palette browsing context without touching drafts or saved data.", "清除任务、分诊、故事和命令面板的浏览上下文，但不影响草稿和已保存数据。"),
      run: async () => {
        resetWorkspaceContext();
      },
    },
    {
      id: "copy-context-link",
      group: copy("system", "系统"),
      title: copy("Copy Context Link", "复制当前上下文链接"),
      subtitle: copy("Copy the current deep link with section, filters, and focused records.", "复制包含当前区块、筛选条件和焦点记录的深链。"),
      run: async () => {
        await copyCurrentContextLink();
      },
    },
    {
      id: "save-current-view",
      group: copy("system", "系统"),
      title: copy("Save Current View", "保存当前视图"),
      subtitle: copy("Pin the current workspace context as a reusable saved view.", "把当前工作上下文固定成一个可复用的保存视图。"),
      run: async () => {
        saveCurrentContextView();
      },
    },
    {
      id: "save-pin-current-view",
      group: copy("system", "系统"),
      title: copy("Save + Pin Current View", "保存并固定当前视图"),
      subtitle: copy("Save the current workspace context and pin it into the top dock in one step.", "一步把当前工作上下文保存并固定到顶部坞站。"),
      run: async () => {
        saveAndPinCurrentContextView();
      },
    },
    ...(state.contextLinkHistory[0]
      ? [{
          id: "open-last-context-link",
          group: copy("system", "系统"),
          title: copy("Open Last Shared Context", "打开最近分享上下文"),
          subtitle: copy("Restore the most recently copied deep link without reloading the page.", "在不刷新页面的情况下恢复最近一次复制的深链。"),
          run: async () => {
            restoreContextLinkHistoryEntry(0);
          },
        }]
      : []),
    ...(state.contextLinkHistory.length
      ? [{
          id: "clear-context-link-history",
          group: copy("system", "系统"),
          title: copy("Clear Shared Context History", "清空分享上下文历史"),
          subtitle: copy("Remove recent shared deep links from the context lens.", "清空上下文透镜中的最近分享深链。"),
          run: async () => {
            clearContextLinkHistory();
          },
        }]
      : []),
    ...(state.contextSavedViews.length
      ? state.contextSavedViews
          .map((entry, index) => normalizeContextSavedViewEntry(entry))
          .filter(Boolean)
          .slice(0, 6)
          .map((entry, index) => ({
            id: `open-saved-context-${index}`,
            group: copy("system", "系统"),
            title: state.language === "zh"
              ? `打开保存视图：${entry.pinned ? "[已固定] " : ""}${entry.name}`
              : `Open Saved View: ${entry.pinned ? "[Pinned] " : ""}${entry.name}`,
            subtitle: entry.pinned
              ? phrase("Pinned | {summary}", "已固定 | {summary}", { summary: entry.summary })
              : entry.summary,
            run: async () => {
              restoreContextSavedViewEntry(index);
            },
          }))
      : []),
    ...(getDefaultContextSavedView()
      ? [{
          id: "open-default-saved-view",
          group: copy("system", "系统"),
          title: copy("Open Default Landing View", "打开默认落地视图"),
          subtitle: getDefaultContextSavedView()?.summary || copy("Restore the default saved workspace view.", "恢复默认保存工作视图。"),
          run: async () => {
            const entry = getDefaultContextSavedView();
            if (entry) {
              restoreContextSavedViewByName(entry.name);
            }
          },
        },
        {
          id: "clear-default-saved-view",
          group: copy("system", "系统"),
          title: copy("Clear Default Landing View", "清除默认落地视图"),
          subtitle: copy("Stop auto-opening a saved view when the console boots without a deep link.", "控制台在没有深链时启动时，不再自动打开保存视图。"),
          run: async () => {
            clearDefaultContextSavedView();
          },
        }]
      : []),
    ...(state.contextSavedViews.length
      ? [{
          id: "clear-saved-context-views",
          group: copy("system", "系统"),
          title: copy("Clear Saved Views", "清空保存视图"),
          subtitle: copy("Remove every named saved view from the context lens.", "移除上下文透镜里的全部命名保存视图。"),
          run: async () => {
            clearContextSavedViews();
          },
        }]
      : []),
    {
      id: "focus-deck",
      group: copy("deck", "草稿"),
      title: copy("Focus Mission Deck", "聚焦任务草稿"),
      subtitle: copy("Jump to the draft deck and focus the main field.", "跳转到任务草稿区并聚焦主输入框。"),
      run: async () => {
        focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
      },
    },
    {
      id: "clear-deck",
      group: copy("deck", "草稿"),
      title: copy("Reset Mission Deck", "清空任务草稿"),
      subtitle: copy("Clear the current draft and its stored local state.", "清空当前草稿及其本地缓存。"),
      run: async () => {
        const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
        state.createWatchAdvancedOpen = null;
        setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
        showToast(
          wasEditing
            ? copy("Mission edit cancelled", "已取消任务编辑")
            : copy("Mission deck draft cleared", "已清空任务草稿"),
          "success",
        );
      },
    },
    {
      id: "focus-route-deck",
      group: copy("routes", "路由"),
      title: copy("Focus Route Deck", "聚焦路由草稿"),
      subtitle: copy("Jump to the route manager and focus the route name field.", "跳转到路由管理区并聚焦路由名称。"),
      run: async () => {
        focusRouteDeck((state.routeDraft && state.routeDraft.name.trim()) ? "description" : "name");
      },
    },
    {
      id: "clear-route-deck",
      group: copy("routes", "路由"),
      title: copy("Reset Route Deck", "清空路由草稿"),
      subtitle: copy("Clear the current route draft or exit edit mode.", "清空当前路由草稿或退出编辑模式。"),
      run: async () => {
        const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
        state.routeAdvancedOpen = null;
        setRouteDraft(defaultRouteDraft(), "");
        showToast(
          wasEditing
            ? copy("Route edit cancelled", "已取消路由编辑")
            : copy("Route deck draft cleared", "已清空路由草稿"),
          "success",
        );
      },
    },
    {
      id: "focus-story-deck",
      group: copy("stories", "故事"),
      title: copy("Focus Story Intake", "聚焦故事录入"),
      subtitle: copy("Jump to the manual story deck and start a new brief.", "跳转到手工故事草稿区，直接开始新建简报。"),
      run: async () => {
        focusStoryDeck((state.storyDraft && state.storyDraft.title.trim()) ? "summary" : "title");
      },
    },
  ];
  storyViewPresetOptions.forEach((viewKey) => {
    entries.push({
      id: `story-view-${viewKey}`,
      group: copy("stories", "故事"),
      title: state.language === "zh"
        ? `切换故事视图：${storyViewPresetLabel(viewKey)}`
        : `Story View: ${storyViewPresetLabel(viewKey)}`,
      subtitle: storyViewPresetDescription(viewKey),
      run: async () => {
        applyStoryViewPreset(viewKey, { jump: true, toast: true });
      },
    });
  });
  if (state.actionLog.length && state.actionLog[0].undo) {
    const latestAction = state.actionLog[0];
    entries.unshift({
      id: `undo-${latestAction.id}`,
      group: copy("actions", "操作"),
      title: state.language === "zh" ? `撤销：${latestAction.label}` : `Undo: ${latestAction.label}`,
      subtitle: latestAction.detail || copy("Reverse the latest reversible action.", "撤销最近一次可回退操作。"),
      run: async () => {
        await latestAction.undo();
        state.actionLog = state.actionLog.filter((entry) => entry.id !== latestAction.id);
        renderActionHistory();
      },
    });
  }
  state.watches.slice(0, 6).forEach((watch) => {
    entries.push({
      id: `watch-open-${watch.id}`,
      group: copy("missions", "任务"),
      title: state.language === "zh" ? `打开任务：${watch.name}` : `Open Mission: ${watch.name}`,
      subtitle: `${watch.query || "-"} | ${watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}`,
      run: async () => {
        await loadWatch(watch.id);
      },
    });
    entries.push({
      id: `watch-edit-${watch.id}`,
      group: copy("missions", "任务"),
      title: state.language === "zh" ? `编辑任务：${watch.name}` : `Edit Mission: ${watch.name}`,
      subtitle: copy("Load this mission into the deck for in-place editing.", "把该任务载入草稿区，直接原位编辑。"),
      run: async () => {
        await editMissionInCreateWatch(watch.id);
      },
    });
    entries.push({
      id: `watch-clone-${watch.id}`,
      group: copy("missions", "任务"),
      title: state.language === "zh" ? `克隆任务：${watch.name}` : `Clone Mission: ${watch.name}`,
      subtitle: copy("Pull this mission into the deck as a draft fork.", "把这个任务拉进草稿区，作为分支任务继续编辑。"),
      run: async () => {
        await cloneMissionIntoCreateWatch(watch.id);
      },
    });
  });
  state.routes.slice(0, 6).forEach((route) => {
    entries.push({
      id: `route-edit-${route.name}`,
      group: copy("routes", "路由"),
      title: state.language === "zh" ? `编辑路由：${route.name}` : `Edit Route: ${route.name}`,
      subtitle: `${routeChannelLabel(route.channel)} | ${summarizeRouteDestination(route)}`,
      run: async () => {
        await editRouteInDeck(route.name);
      },
    });
    entries.push({
      id: `route-apply-${route.name}`,
      group: copy("routes", "路由"),
      title: state.language === "zh" ? `把路由用于任务：${route.name}` : `Use Route In Mission: ${route.name}`,
      subtitle: copy("Attach this named route to the mission intake deck.", "把这个命名路由直接带入任务草稿。"),
      run: async () => {
        await applyRouteToMissionDraft(route.name);
      },
    });
  });
  const visibleTriage = getVisibleTriageItems();
  const focusedTriageId = state.selectedTriageId || (visibleTriage[0] ? visibleTriage[0].id : "");
  const focusedTriage = focusedTriageId
    ? visibleTriage.find((item) => item.id === focusedTriageId) || state.triage.find((item) => item.id === focusedTriageId)
    : null;
  if (focusedTriage) {
    entries.push({
      id: `triage-story-${focusedTriage.id}`,
      group: copy("triage", "分诊"),
      title: state.language === "zh" ? `从分诊生成故事：${focusedTriage.title}` : `Create Story From Triage: ${focusedTriage.title}`,
      subtitle: copy("Promote the focused triage item into a story draft and jump to Story Workspace.", "把当前焦点分诊条目提升为故事草稿，并跳转到故事工作台。"),
      run: async () => {
        await createStoryFromTriageItems([focusedTriage.id]);
      },
    });
    entries.push({
      id: `triage-note-${focusedTriage.id}`,
      group: copy("triage", "分诊"),
      title: state.language === "zh" ? `聚焦备注：${focusedTriage.title}` : `Focus Note: ${focusedTriage.title}`,
      subtitle: copy("Jump back to the queue and place the cursor in the note composer.", "跳回分诊队列，并把光标放进备注输入框。"),
      run: async () => {
        focusTriageNoteComposer(focusedTriage.id);
      },
    });
  }
  state.stories.slice(0, 5).forEach((story) => {
    entries.push({
      id: `story-open-${story.id}`,
      group: copy("stories", "故事"),
      title: state.language === "zh" ? `打开故事：${story.title}` : `Open Story: ${story.title}`,
      subtitle: `${localizeWord(story.status || "active")} | ${copy("items", "条目")}=${story.item_count || 0}`,
      run: async () => {
        await loadStory(story.id);
      },
    });
  });
  return entries;
}

function getCommandPaletteEntriesForQuery() {
  const query = String(state.commandPalette.query || "").trim().toLowerCase();
  const filteredEntries = buildCommandPaletteEntries().filter((entry) => {
    if (!query) {
      return true;
    }
    return [entry.group, entry.title, entry.subtitle].some((value) => String(value || "").toLowerCase().includes(query));
  });
  if (query) {
    return filteredEntries;
  }
  const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
  if (!recentIds.length) {
    return filteredEntries;
  }
  const recentEntries = recentIds
    .map((entryId) => filteredEntries.find((entry) => entry.id === entryId))
    .filter(Boolean)
    .map((entry) => ({
      ...entry,
      group: copy("recent", "最近"),
      subtitle: entry.subtitle
        ? `${copy("from", "来自")} ${entry.group} | ${entry.subtitle}`
        : `${copy("from", "来自")} ${entry.group}`,
    }));
  const seen = new Set(recentEntries.map((entry) => entry.id));
  return [...recentEntries, ...filteredEntries.filter((entry) => !seen.has(entry.id))];
}

async function executePaletteEntry(entry) {
  if (!entry) {
    return;
  }
  closeCommandPalette();
  noteCommandPaletteRecent(entry.id);
  try {
    await entry.run();
  } catch (error) {
    reportError(error, "Palette action");
  }
}

function renderCommandPalette() {
  const backdrop = $("command-palette");
  const input = $("command-palette-input");
  const list = $("command-palette-list");
  if (!backdrop || !input || !list) {
    return;
  }
  backdrop.classList.toggle("open", state.commandPalette.open);
  if (!state.commandPalette.open) {
    return;
  }
  const entries = getCommandPaletteEntriesForQuery();
  if (state.commandPalette.selectedIndex >= entries.length) {
    state.commandPalette.selectedIndex = Math.max(entries.length - 1, 0);
  }
  list.innerHTML = entries.length
    ? entries.map((entry, index) => `
        <div class="palette-item ${index === state.commandPalette.selectedIndex ? "active" : ""}" data-palette-id="${entry.id}" data-palette-index="${index}">
          <div class="palette-kicker">${escapeHtml(entry.group)}</div>
          <div>${escapeHtml(entry.title)}</div>
          <div class="panel-sub">${escapeHtml(entry.subtitle || "")}</div>
        </div>
      `).join("")
    : `<div class="empty">${copy("No command matched the current search.", "当前搜索没有匹配到命令。")}</div>`;
  list.querySelectorAll("[data-palette-id]").forEach((item) => {
    item.addEventListener("mouseenter", () => {
      state.commandPalette.selectedIndex = Number(item.dataset.paletteIndex || 0);
      renderCommandPalette();
    });
    item.addEventListener("click", async () => {
      const entry = entries.find((candidate) => candidate.id === item.dataset.paletteId);
      await executePaletteEntry(entry);
    });
  });
  input.value = state.commandPalette.query;
}

function openCommandPalette() {
  setContextLensOpen(false);
  state.commandPalette.open = true;
  state.commandPalette.selectedIndex = 0;
  renderCommandPalette();
  window.setTimeout(() => $("command-palette-input")?.focus(), 10);
}

function closeCommandPalette() {
  state.commandPalette.open = false;
  state.commandPalette.selectedIndex = 0;
  renderCommandPalette();
}

function bindContextLens() {
  const summary = $("context-summary");
  const lens = $("context-lens");
  const backdrop = $("context-lens-backdrop");
  const dialog = $("context-lens-shell");
  const saveForm = $("context-save-form");
  const saveInput = $("context-save-name");
  if (!summary || !lens || !backdrop || !dialog) {
    return;
  }
  summary.addEventListener("click", (event) => {
    event.stopPropagation();
    state.contextLensRestoreFocusId = "context-summary";
    toggleContextLens();
  });
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) {
      setContextLensOpen(false);
    }
  });
  dialog.addEventListener("keydown", (event) => {
    if (String(event.key || "") !== "Tab" || !state.contextLensOpen) {
      return;
    }
    const focusable = getContextLensFocusableElements();
    if (!focusable.length) {
      event.preventDefault();
      dialog.focus();
      return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;
    if (event.shiftKey && (active === first || active === dialog)) {
      event.preventDefault();
      last.focus();
      return;
    }
    if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  });
  saveForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    saveCurrentContextView(saveInput?.value || "");
  });
  $("context-lens-close")?.addEventListener("click", () => {
    setContextLensOpen(false);
  });
  $("context-open-section")?.addEventListener("click", () => {
    setContextLensOpen(false);
    jumpToSection(state.activeSectionId);
  });
  $("context-copy-link")?.addEventListener("click", async () => {
    await copyCurrentContextLink();
    setContextLensOpen(false);
  });
  dialog.querySelectorAll("[data-context-section]").forEach((button) => {
    button.addEventListener("click", () => {
      const sectionId = String(button.dataset.contextSection || "").trim();
      setContextLensOpen(false);
      jumpToSection(sectionId);
    });
  });
}

function bindStoryInspector() {
  const backdrop = $("story-inspector-backdrop");
  const dialog = $("story-inspector-shell");
  if (!backdrop || !dialog) {
    return;
  }
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) {
      closeStoryInspector();
    }
  });
  dialog.addEventListener("keydown", (event) => {
    if (String(event.key || "") === "Escape" && state.storyInspector?.open) {
      event.preventDefault();
      closeStoryInspector();
      return;
    }
    if (String(event.key || "") !== "Tab" || !state.storyInspector?.open) {
      return;
    }
    const focusable = getStoryInspectorFocusableElements();
    if (!focusable.length) {
      event.preventDefault();
      dialog.focus();
      return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;
    if (event.shiftKey && (active === first || active === dialog)) {
      event.preventDefault();
      last.focus();
      return;
    }
    if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  });
  $("story-inspector-close")?.addEventListener("click", () => {
    closeStoryInspector();
  });
}

function bindCommandPalette() {
  const backdrop = $("command-palette");
  const input = $("command-palette-input");
  if (!backdrop || !input) {
    return;
  }
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) {
      closeCommandPalette();
    }
  });
  input.addEventListener("input", () => {
    state.commandPalette.query = input.value;
    state.commandPalette.selectedIndex = 0;
    persistCommandPaletteQuery();
    renderCommandPalette();
  });
  input.addEventListener("keydown", async (event) => {
    const list = getCommandPaletteEntriesForQuery();
    if (event.key === "ArrowDown") {
      event.preventDefault();
      state.commandPalette.selectedIndex = Math.min(state.commandPalette.selectedIndex + 1, Math.max(list.length - 1, 0));
      renderCommandPalette();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      state.commandPalette.selectedIndex = Math.max(state.commandPalette.selectedIndex - 1, 0);
      renderCommandPalette();
    } else if (event.key === "Enter") {
      event.preventDefault();
      const entry = list[state.commandPalette.selectedIndex];
      await executePaletteEntry(entry);
    } else if (event.key === "Escape") {
      event.preventDefault();
      closeCommandPalette();
    }
  });
}
