// Split group 2a: story sorting, triage normalization, and shared preview primitives.
// Depends on 00-common.js (state, copy, phrase, options, storage keys).

function uniqueValues(values) {
  return Array.from(new Set((Array.isArray(values) ? values : [values])
    .flatMap((value) => Array.isArray(value) ? value : [value])
    .map((value) => String(value ?? "").trim())
    .filter(Boolean)));
}

function normalizeStorySort(value) {
  const normalized = String(value || "").trim().toLowerCase() || "attention";
  return storySortOptions.includes(normalized) ? normalized : "attention";
}

function normalizeStoryFilter(value) {
  const normalized = String(value || "").trim().toLowerCase() || "all";
  if (normalized === "all" || normalized === "conflicted") {
    return normalized;
  }
  return storyStatusOptions.includes(normalized) ? normalized : "all";
}

function normalizeStoryWorkspaceMode(value) {
  const normalized = String(value || "").trim().toLowerCase() || "board";
  return storyWorkspaceModeOptions.includes(normalized) ? normalized : "board";
}

function normalizeStoryDetailView(value) {
  const normalized = String(value || "").trim().toLowerCase() || "overview";
  return storyDetailViewOptions.includes(normalized) ? normalized : "overview";
}

function normalizeStoryInspectorKind(value) {
  return String(value || "").trim().toLowerCase() === "json" ? "json" : "markdown";
}

function normalizeTriageFilter(value) {
  const normalized = String(value || "").trim().toLowerCase() || "open";
  return triageFilterOptions.includes(normalized) ? normalized : "open";
}

function storyViewPresetLabel(viewKey) {
  const labels = {
    desk: copy("Ops Desk", "运营台"),
    fresh: copy("Fresh Radar", "新近雷达"),
    conflicts: copy("Conflict Queue", "冲突队列"),
    archive: copy("Archive Review", "归档回看"),
    custom: copy("Custom", "自定义"),
  };
  return labels[String(viewKey || "").trim().toLowerCase()] || labels.custom;
}

function storyViewPresetDescription(viewKey) {
  const descriptions = {
    desk: copy(
      "Default operating lane for active story review.",
      "默认的日常运营视角，先看当前应处理的故事。"
    ),
    fresh: copy(
      "Pull the latest story updates to the top.",
      "把最新更新的故事优先提到最前。"
    ),
    conflicts: copy(
      "Narrow to contradiction-heavy stories first.",
      "直接聚焦冲突较多的故事。"
    ),
    archive: copy(
      "Review recently archived stories without reopening the whole queue.",
      "查看最近归档的故事，而不用重新打开整个队列。"
    ),
    custom: copy(
      "You are using a manual filter or sort combination.",
      "当前使用的是手动组合的筛选与排序。"
    ),
  };
  return descriptions[String(viewKey || "").trim().toLowerCase()] || descriptions.custom;
}

function getStoryViewPreset(viewKey) {
  const normalized = String(viewKey || "").trim().toLowerCase();
  const presets = {
    desk: { key: "desk", filter: "all", sort: "attention" },
    fresh: { key: "fresh", filter: "all", sort: "recent" },
    conflicts: { key: "conflicts", filter: "conflicted", sort: "conflict" },
    archive: { key: "archive", filter: "archived", sort: "recent" },
  };
  return presets[normalized] || null;
}

function detectStoryViewPreset({ filter = "all", sort = "attention", search = "" } = {}) {
  if (String(search || "").trim()) {
    return "custom";
  }
  const normalizedFilter = normalizeStoryFilter(filter);
  const normalizedSort = normalizeStorySort(sort);
  const matchedPreset = storyViewPresetOptions.find((viewKey) => {
    const preset = getStoryViewPreset(viewKey);
    return preset && preset.filter === normalizedFilter && preset.sort === normalizedSort;
  });
  return matchedPreset || "custom";
}

function storySortLabel(sortKey) {
  const normalized = normalizeStorySort(sortKey);
  const labels = {
    attention: copy("Attention Order", "优先级排序"),
    recent: copy("Most Recent", "最近更新"),
    evidence: copy("Most Evidence", "证据最多"),
    conflict: copy("Conflict Load", "冲突强度"),
    score: copy("Highest Score", "最高分数"),
  };
  return labels[normalized] || labels.attention;
}

function storySortSummary(sortKey) {
  const normalized = normalizeStorySort(sortKey);
  const summaries = {
    attention: copy(
      "Default lane: unresolved conflicts, fresh updates, and active stories float to the top first.",
      "默认把未解决冲突、最近更新且仍在活跃队列里的故事放在最前面。"
    ),
    recent: copy(
      "Use when recency matters more than story depth.",
      "当时效比故事深度更重要时，用这个排序。"
    ),
    evidence: copy(
      "Use when you want the densest evidence packs first.",
      "当你想先看证据最密集的故事时，用这个排序。"
    ),
    conflict: copy(
      "Use when contradiction triage is the current priority.",
      "当处理冲突信号是当前优先级时，用这个排序。"
    ),
    score: copy(
      "Use when ranked signal quality should lead the queue.",
      "当你想按综合分数先看高质量信号时，用这个排序。"
    ),
  };
  return summaries[normalized] || summaries.attention;
}

function parseDateValue(value) {
  const stamp = Date.parse(String(value || "").trim());
  return Number.isFinite(stamp) ? stamp : 0;
}

function formatCompactDateTime(value) {
  const stamp = parseDateValue(value);
  if (!stamp) {
    return "-";
  }
  const formatter = new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
  return formatter.format(new Date(stamp));
}

function getStoryUpdatedAt(story) {
  return parseDateValue((story && (story.updated_at || story.generated_at)) || "");
}

function getStoryContradictionCount(story) {
  return Array.isArray(story?.contradictions) ? story.contradictions.length : 0;
}

function getStoryAttentionScore(story) {
  const status = String(story?.status || "active").trim().toLowerCase() || "active";
  const contradictionCount = getStoryContradictionCount(story);
  const itemCount = Math.max(0, Number(story?.item_count || 0));
  const sourceCount = Math.max(0, Number(story?.source_count || 0));
  const score = Number(story?.score || 0);
  const confidence = Number(story?.confidence || 0);
  const updatedAt = getStoryUpdatedAt(story);
  const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
  const freshness = Math.max(0, 48 - Math.min(48, ageHours));
  const statusWeights = {
    active: 40,
    monitoring: 26,
    resolved: 10,
    archived: -24,
  };
  return (
    contradictionCount * 70 +
    itemCount * 8 +
    sourceCount * 4 +
    score * 0.4 +
    confidence * 18 +
    freshness +
    (statusWeights[status] ?? 16)
  );
}

function compareNumberDesc(leftValue, rightValue) {
  if (leftValue === rightValue) {
    return 0;
  }
  return leftValue < rightValue ? 1 : -1;
}

function compareStoriesByWorkspaceOrder(left, right, sortKey) {
  const normalized = normalizeStorySort(sortKey);
  const leftUpdated = getStoryUpdatedAt(left);
  const rightUpdated = getStoryUpdatedAt(right);
  const leftAttention = getStoryAttentionScore(left);
  const rightAttention = getStoryAttentionScore(right);
  const leftConflicts = getStoryContradictionCount(left);
  const rightConflicts = getStoryContradictionCount(right);
  const leftItems = Math.max(0, Number(left?.item_count || 0));
  const rightItems = Math.max(0, Number(right?.item_count || 0));
  const leftSources = Math.max(0, Number(left?.source_count || 0));
  const rightSources = Math.max(0, Number(right?.source_count || 0));
  const leftScore = Number(left?.score || 0);
  const rightScore = Number(right?.score || 0);
  const leftConfidence = Number(left?.confidence || 0);
  const rightConfidence = Number(right?.confidence || 0);
  const chain = normalized === "recent"
    ? [
        compareNumberDesc(leftUpdated, rightUpdated),
        compareNumberDesc(leftAttention, rightAttention),
        compareNumberDesc(leftItems, rightItems),
      ]
    : normalized === "evidence"
      ? [
          compareNumberDesc(leftItems, rightItems),
          compareNumberDesc(leftSources, rightSources),
          compareNumberDesc(leftAttention, rightAttention),
          compareNumberDesc(leftUpdated, rightUpdated),
        ]
      : normalized === "conflict"
        ? [
            compareNumberDesc(leftConflicts, rightConflicts),
            compareNumberDesc(leftAttention, rightAttention),
            compareNumberDesc(leftUpdated, rightUpdated),
          ]
        : normalized === "score"
          ? [
              compareNumberDesc(leftScore, rightScore),
              compareNumberDesc(leftConfidence, rightConfidence),
              compareNumberDesc(leftAttention, rightAttention),
              compareNumberDesc(leftUpdated, rightUpdated),
            ]
          : [
              compareNumberDesc(leftAttention, rightAttention),
              compareNumberDesc(leftConflicts, rightConflicts),
              compareNumberDesc(leftUpdated, rightUpdated),
              compareNumberDesc(leftItems, rightItems),
            ];
  for (const result of chain) {
    if (result) {
      return result;
    }
  }
  return String(left?.title || left?.id || "").localeCompare(String(right?.title || right?.id || ""));
}

function describeStoryPriority(story) {
  const contradictionCount = getStoryContradictionCount(story);
  const itemCount = Math.max(0, Number(story?.item_count || 0));
  const status = String(story?.status || "active").trim().toLowerCase() || "active";
  const updatedAt = getStoryUpdatedAt(story);
  const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
  if (status === "archived") {
    return { tone: "", label: copy("cold lane", "冷队列") };
  }
  if (contradictionCount > 0) {
    return {
      tone: "hot",
      label: phrase("conflict x{count}", "冲突 x{count}", { count: contradictionCount }),
    };
  }
  if (ageHours <= 12) {
    return { tone: "ok", label: copy("fresh update", "新近更新") };
  }
  if (itemCount >= 4) {
    return { tone: "ok", label: copy("deep evidence", "证据较多") };
  }
  if (status === "monitoring") {
    return { tone: "", label: copy("watching", "持续监控") };
  }
  if (status === "resolved") {
    return { tone: "", label: copy("resolved lane", "已解决") };
  }
  return { tone: "ok", label: copy("active lane", "活跃队列") };
}

function renderDatalist(identifier, values) {
  const root = $(identifier);
  if (!root) {
    return;
  }
  root.innerHTML = uniqueValues(values).slice(0, 32).map((value) => `<option value="${escapeHtml(value)}"></option>`).join("");
}

function collectWatchValues(fieldName) {
  return [
    ...state.watches.map((watch) => watch ? watch[fieldName] : ""),
    ...Object.values(state.watchDetails || {}).map((watch) => watch ? watch[fieldName] : ""),
  ];
}

function collectWatchArrayValues(fieldName) {
  return [
    ...state.watches.flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
    ...Object.values(state.watchDetails || {}).flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
  ];
}

function collectAlertRuleValues(fieldName) {
  return Object.values(state.watchDetails || {}).flatMap((watch) => {
    return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).flatMap((rule) => {
      const raw = rule ? rule[fieldName] : "";
      return Array.isArray(raw) ? raw : [raw];
    });
  });
}

function collectRouteNames() {
  return state.routes.map((route) => route && (route.name || route.route_name || route.id || ""));
}

function renderFormSuggestionLists() {
  const suggestionPatch = state.createWatchSuggestions?.autofill_patch || {};
  renderDatalist("mission-name-options-list", [
    state.createWatchDraft?.name,
    ...createWatchPresets.map((preset) => preset.values.name),
    ...collectWatchValues("name"),
  ]);
  renderDatalist("query-options-list", [
    state.createWatchDraft?.query,
    ...createWatchPresets.map((preset) => preset.values.query),
    ...collectWatchValues("query"),
  ]);
  renderDatalist("schedule-options-list", [
    state.createWatchDraft?.schedule,
    suggestionPatch.schedule,
    state.createWatchSuggestions?.recommended_schedule,
    ...scheduleLaneOptions.map((option) => option.value),
    ...collectWatchValues("schedule"),
  ]);
  renderDatalist("platform-options-list", [
    state.createWatchDraft?.platform,
    suggestionPatch.platform,
    state.createWatchSuggestions?.recommended_platform,
    ...platformLaneOptions.map((option) => option.value),
    ...collectWatchArrayValues("platforms"),
  ]);
  renderDatalist("domain-options-list", [
    state.createWatchDraft?.domain,
    suggestionPatch.domain,
    state.createWatchSuggestions?.recommended_domain,
    ...collectWatchArrayValues("sites"),
    ...collectAlertRuleValues("domains"),
  ]);
  renderDatalist("route-options-list", [
    state.createWatchDraft?.route,
    suggestionPatch.route,
    state.createWatchSuggestions?.recommended_route,
    ...collectRouteNames(),
    ...collectAlertRuleValues("routes"),
  ]);
  renderDatalist("keyword-options-list", [
    state.createWatchDraft?.keyword,
    suggestionPatch.keyword,
    state.createWatchSuggestions?.recommended_keyword,
    ...createWatchPresets.map((preset) => preset.values.keyword),
    ...collectAlertRuleValues("keyword_any"),
  ]);
  renderDatalist("score-options-list", [
    state.createWatchDraft?.min_score,
    suggestionPatch.min_score,
    ...scoreSuggestionOptions,
    ...collectAlertRuleValues("min_score").filter((value) => Number(value || 0) > 0),
  ]);
  renderDatalist("confidence-options-list", [
    state.createWatchDraft?.min_confidence,
    suggestionPatch.min_confidence,
    ...confidenceSuggestionOptions,
    ...collectAlertRuleValues("min_confidence").filter((value) => Number(value || 0) > 0),
  ]);
}

function defaultCreateWatchDraft() {
  return {
    name: "",
    schedule: "",
    query: "",
    platform: "",
    domain: "",
    provider: "",
    route: "",
    keyword: "",
    min_score: "",
    min_confidence: "",
  };
}

function draftHasAdvancedSignal(payload = {}) {
  const draft = normalizeCreateWatchDraft(payload || defaultCreateWatchDraft());
  const providerSignal = draft.provider.trim() && draft.provider.trim().toLowerCase() !== "auto";
  return Boolean(
    draft.schedule.trim() ||
    draft.platform.trim() ||
    draft.domain.trim() ||
    providerSignal ||
    draft.route.trim() ||
    draft.keyword.trim() ||
    draft.min_score.trim() ||
    draft.min_confidence.trim()
  );
}

function normalizeCreateWatchDraft(payload = {}) {
  const draft = defaultCreateWatchDraft();
  createWatchFormFields.forEach((field) => {
    draft[field] = String(payload[field] ?? "");
  });
  return draft;
}

function isCreateWatchAdvancedOpen(draftInput) {
  const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
  if (typeof state.createWatchAdvancedOpen === "boolean") {
    return state.createWatchAdvancedOpen;
  }
  return Boolean(String(state.createWatchEditingId || "").trim() || draftHasAdvancedSignal(draft));
}

function summarizeCreateWatchAdvanced(draftInput) {
  const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
  const chips = [];
  if (draft.schedule.trim()) {
    chips.push(scheduleModeLabel(draft.schedule));
  }
  const platformList = parseListField(draft.platform);
  const siteList = parseListField(draft.domain);
  const providerMode = (draft.provider || "").trim().toLowerCase();
  if (platformList.length) {
    const platformText = platformList.join(", ");
    chips.push(phrase("platforms: {value}", "平台：{value}", { value: platformText }));
  }
  if (siteList.length) {
    const siteText = siteList.join(", ");
    chips.push(phrase("sites: {value}", "站点：{value}", { value: siteText }));
  }
  if (providerMode && providerMode !== "auto") {
    chips.push(phrase("provider: {value}", "采集模式：{value}", { value: providerMode }));
  }
  if (platformList.length >= 2 || providerMode === "multi") {
    chips.push(copy("multi-source parallel + cross-verify", "多源并行 + 交叉印证"));
  }
  if (draft.route.trim()) {
    chips.push(phrase("route: {value}", "路由：{value}", { value: draft.route.trim() }));
  }
  if (draft.keyword.trim()) {
    chips.push(phrase("keyword: {value}", "关键词：{value}", { value: draft.keyword.trim() }));
  }
  if (draft.min_score.trim()) {
    chips.push(phrase("score >= {value}", "分数 >= {value}", { value: draft.min_score.trim() }));
  }
  if (draft.min_confidence.trim()) {
    chips.push(phrase("confidence >= {value}", "置信度 >= {value}", { value: draft.min_confidence.trim() }));
  }
  if (!chips.length) {
    chips.push(copy("No scope or alert gate yet", "当前还没有范围或告警门槛"));
  }
  return chips.slice(0, 6);
}

function defaultRouteDraft() {
  return {
    name: "",
    channel: "webhook",
    description: "",
    webhook_url: "",
    authorization: "",
    headers_json: "",
    feishu_webhook: "",
    telegram_bot_token: "",
    telegram_chat_id: "",
    timeout_seconds: "",
  };
}

function normalizeRouteDraft(payload = {}) {
  const draft = defaultRouteDraft();
  routeFormFields.forEach((field) => {
    if (field === "channel") {
      return;
    }
    draft[field] = String(payload[field] ?? draft[field] ?? "");
  });
  const channel = String(payload.channel ?? draft.channel ?? "webhook").trim().toLowerCase();
  draft.channel = routeChannelOptions.some((option) => option.value === channel) ? channel : "webhook";
  return draft;
}

function routeChannelLabel(channel) {
  const normalized = String(channel || "").trim().toLowerCase();
  const option = routeChannelOptions.find((candidate) => candidate.value === normalized);
  if (!option) {
    return normalized || copy("unknown", "未知");
  }
  return copy(option.label, option.zhLabel || option.label);
}

function routeDraftHasAdvancedSignal(payload = {}) {
  const draft = normalizeRouteDraft(payload || defaultRouteDraft());
  return Boolean(
    draft.description.trim() ||
    draft.authorization.trim() ||
    draft.headers_json.trim() ||
    draft.timeout_seconds.trim()
  );
}

function isRouteAdvancedOpen(draftInput) {
  const draft = normalizeRouteDraft(draftInput || defaultRouteDraft());
  if (typeof state.routeAdvancedOpen === "boolean") {
    return state.routeAdvancedOpen;
  }
  return Boolean(String(state.routeEditingId || "").trim() || routeDraftHasAdvancedSignal(draft));
}

function normalizeRouteName(value) {
  return String(value || "").trim().toLowerCase();
}

function normalizeRouteRuleNames(rule) {
  if (!rule) {
    return [];
  }
  const raw = Array.isArray(rule.routes) ? rule.routes : [rule.route];
  return uniqueValues(raw).map((value) => normalizeRouteName(value)).filter(Boolean);
}

function watchUsesRoute(watch, routeName) {
  const normalized = normalizeRouteName(routeName);
  if (!normalized) {
    return false;
  }
  return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).some((rule) => {
    return normalizeRouteRuleNames(rule).includes(normalized);
  });
}

function getRouteUsageRows(routeName) {
  const rows = [
    ...state.watches,
    ...Object.values(state.watchDetails || {}),
  ];
  const seen = new Set();
  return rows.filter((watch) => {
    const identifier = String(watch?.id || "").trim();
    if (!identifier || seen.has(identifier)) {
      return false;
    }
    seen.add(identifier);
    return watchUsesRoute(watch, routeName);
  });
}

function getRouteUsageCount(routeName) {
  return getRouteUsageRows(routeName).length;
}

function getRouteUsageNames(routeName) {
  return getRouteUsageRows(routeName).map((watch) => String(watch.name || watch.id || "").trim()).filter(Boolean);
}

function getRouteHealthRow(routeName) {
  const normalized = normalizeRouteName(routeName);
  if (!normalized) {
    return null;
  }
  return state.routeHealth.find((route) => normalizeRouteName(route?.name) === normalized) || null;
}

function summarizeUrlHost(rawUrl) {
  const value = String(rawUrl || "").trim();
  if (!value) {
    return "";
  }
  try {
    const parsed = new URL(value);
    const path = parsed.pathname && parsed.pathname !== "/" ? parsed.pathname.slice(0, 18) : "";
    return `${parsed.host}${path}`;
  } catch {
    return value;
  }
}

function summarizeRouteDestination(route) {
  const channel = normalizeRouteName(route?.channel);
  if (channel === "webhook") {
    return route?.webhook_url
      ? summarizeUrlHost(route.webhook_url)
      : copy("Webhook URL missing", "Webhook URL 未配置");
  }
  if (channel === "feishu") {
    return route?.feishu_webhook
      ? summarizeUrlHost(route.feishu_webhook)
      : copy("Feishu webhook missing", "飞书 webhook 未配置");
  }
  if (channel === "telegram") {
    return route?.telegram_chat_id
      ? phrase("chat {value}", "会话 {value}", { value: route.telegram_chat_id })
      : copy("Telegram chat missing", "Telegram 会话未配置");
  }
  if (channel === "markdown") {
    return copy("Append to alert markdown log", "追加到告警 Markdown 日志");
  }
  return copy("Route target not configured", "路由目标未配置");
}

function createRouteDraftFromRoute(route) {
  const rawHeaders = route && typeof route.headers === "object" && !Array.isArray(route.headers)
    ? { ...route.headers }
    : {};
  let authorization = "";
  if (typeof route?.authorization === "string" && route.authorization !== "***") {
    authorization = route.authorization;
  }
  if (!authorization && typeof rawHeaders.Authorization === "string" && rawHeaders.Authorization !== "***") {
    authorization = rawHeaders.Authorization;
  }
  delete rawHeaders.Authorization;
  return normalizeRouteDraft({
    name: String(route?.name || ""),
    channel: String(route?.channel || "webhook"),
    description: String(route?.description || ""),
    webhook_url: String(route?.webhook_url || ""),
    authorization,
    headers_json: Object.keys(rawHeaders).length ? JSON.stringify(rawHeaders, null, 2) : "",
    feishu_webhook: String(route?.feishu_webhook || ""),
    telegram_bot_token: "",
    telegram_chat_id: String(route?.telegram_chat_id || ""),
    timeout_seconds: route?.timeout_seconds != null ? String(route.timeout_seconds) : "",
  });
}

function collectRouteDraft(form) {
  if (!form) {
    return normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
  }
  const next = defaultRouteDraft();
  routeFormFields.forEach((fieldName) => {
    const field = form.elements.namedItem(fieldName);
    next[fieldName] = field ? String(field.value ?? "") : "";
  });
  return normalizeRouteDraft(next);
}

function setRouteDraft(nextDraft, editingId = state.routeEditingId) {
  state.routeDraft = normalizeRouteDraft(nextDraft || defaultRouteDraft());
  state.routeEditingId = String(editingId || "").trim();
  const deliveryFeedback = state.stageFeedback?.deliver;
  if (deliveryFeedback && ["blocked", "warning", "no_result"].includes(String(deliveryFeedback.kind || "").trim().toLowerCase())) {
    state.stageFeedback.deliver = null;
  }
  renderRouteDeck();
}

function focusRouteDeck(fieldName = "name") {
  jumpToSection("section-ops");
  window.setTimeout(() => {
    $("route-manager-shell")?.scrollIntoView({ block: "start", behavior: "smooth" });
    const form = $("route-form");
    const field = form?.elements?.namedItem(fieldName);
    if (field && typeof field.focus === "function") {
      field.focus();
    }
  }, 140);
}

async function editRouteInDeck(identifier) {
  const normalized = normalizeRouteName(identifier);
  if (!normalized) {
    return;
  }
  const route = state.routes.find((item) => normalizeRouteName(item?.name) === normalized);
  if (!route) {
    throw new Error(copy("Alert route not found in current board state.", "当前看板中没有找到该告警路由。"));
  }
  setContextRouteName(normalized, "section-ops");
  state.routeAdvancedOpen = true;
  setRouteDraft(createRouteDraftFromRoute(route), normalized);
  focusRouteDeck(route.channel === "markdown" ? "description" : "name");
}

async function applyRouteToMissionDraft(identifier) {
  const normalized = normalizeRouteName(identifier);
  if (!normalized) {
    return;
  }
  state.createWatchAdvancedOpen = true;
  updateCreateWatchDraft({ route: normalized });
  focusCreateWatchDeck("route");
  showToast(
    state.language === "zh"
      ? `已把路由载入任务草稿：${normalized}`
      : `Route loaded into mission deck: ${normalized}`,
    "success",
  );
}

function parseRouteHeaders(rawValue) {
  const text = String(rawValue || "").trim();
  if (!text) {
    return null;
  }
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new Error(copy("Custom headers must be valid JSON.", "自定义请求头必须是合法 JSON。"));
  }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error(copy("Custom headers must be a JSON object.", "自定义请求头必须是 JSON 对象。"));
  }
  return Object.fromEntries(
    Object.entries(parsed)
      .map(([key, value]) => [String(key || "").trim(), String(value ?? "").trim()])
      .filter(([key]) => Boolean(key)),
  );
}

function defaultStoryDraft() {
  return {
    title: "",
    summary: "",
    status: "active",
  };
}

function normalizeStoryDraft(payload = {}) {
  return {
    title: String(payload.title ?? "").trimStart(),
    summary: String(payload.summary ?? ""),
    status: storyStatusOptions.includes(String(payload.status || "").trim().toLowerCase())
      ? String(payload.status || "").trim().toLowerCase()
      : "active",
  };
}

function collectStoryDraft(form) {
  if (!form) {
    return normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
  }
  return normalizeStoryDraft({
    title: String(form.elements.namedItem("title")?.value || ""),
    summary: String(form.elements.namedItem("summary")?.value || ""),
    status: String(form.elements.namedItem("status")?.value || "active"),
  });
}

function setStoryDraft(nextDraft) {
  state.storyDraft = normalizeStoryDraft(nextDraft || defaultStoryDraft());
  const reviewFeedback = state.stageFeedback?.review;
  if (reviewFeedback && ["blocked", "warning", "no_result"].includes(String(reviewFeedback.kind || "").trim().toLowerCase())) {
    state.stageFeedback.review = null;
  }
  renderStoryCreateDeck();
}

function focusStoryDeck(fieldName = "title") {
  jumpToSection("section-story");
  window.setTimeout(() => {
    $("story-intake-shell")?.scrollIntoView({ block: "start", behavior: "smooth" });
    const form = $("story-create-form");
    const field = form?.elements?.namedItem(fieldName);
    if (field && typeof field.focus === "function") {
      field.focus();
    }
  }, 140);
}

function getStoryRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  return state.storyDetails[normalized] || state.stories.find((story) => story.id === normalized) || null;
}

function removeStoryFromState(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return;
  }
  state.stories = state.stories.filter((story) => story.id !== normalized);
  delete state.storyDetails[normalized];
  delete state.storyGraph[normalized];
  delete state.storyMarkdown[normalized];
  if (state.selectedStoryId === normalized) {
    state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
  }
}

function parseDelimitedInput(value) {
  return uniqueValues(
    String(value || "")
      .split(",")
      .flatMap((value) => value.split(String.fromCharCode(10)).map((value) => value.replace(String.fromCharCode(13), "")))
  );
}

function getClaimCardLabel(claim) {
  if (!claim || typeof claim !== "object") {
    return "";
  }
  return String(claim.statement || claim.title || claim.id || "").trim();
}

function getClaimCardRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  return state.claimCards.find((claim) => String(claim.id || "").trim() === normalized) || null;
}

function getReportRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  const compositionReport = state.reportCompositions[normalized]?.report;
  if (compositionReport && typeof compositionReport === "object") {
    return compositionReport;
  }
  return state.reports.find((report) => String(report.id || "").trim() === normalized) || null;
}

function getReportSectionsForReport(reportId) {
  const normalized = String(reportId || "").trim();
  if (!normalized) {
    return [];
  }
  return state.reportSections
    .filter((section) => String(section.report_id || "").trim() === normalized)
    .sort((left, right) => {
      const leftPosition = Number(left.position || 0);
      const rightPosition = Number(right.position || 0);
      if (leftPosition !== rightPosition) {
        return leftPosition - rightPosition;
      }
      return String(left.title || left.id || "").localeCompare(String(right.title || right.id || ""));
    });
}

function getReportComposition(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  const payload = state.reportCompositions[normalized];
  return payload && typeof payload === "object" ? payload : null;
}

function getSelectedClaimCard() {
  return getClaimCardRecord(state.selectedClaimId);
}

function getSelectedReportRecord() {
  return getReportRecord(state.selectedReportId);
}

function getSelectedReportSectionRecord() {
  const selectedReport = getSelectedReportRecord();
  if (!selectedReport) {
    return null;
  }
  const sections = getReportSectionsForReport(selectedReport.id);
  return sections.find((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim()) || null;
}

function getReportClaimIds(reportId) {
  const composition = getReportComposition(reportId);
  if (composition && Array.isArray(composition.claim_cards)) {
    return uniqueValues(composition.claim_cards.map((claim) => String(claim.id || "").trim()));
  }
  const report = getReportRecord(reportId);
  return uniqueValues(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []);
}

function getCitationBundleRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  return state.citationBundles.find((bundle) => String(bundle.id || "").trim() === normalized) || null;
}

function reportStatusTone(status) {
  const normalized = String(status || "").trim().toLowerCase();
  if (["ready", "ok", "pass", "clear", "success", "approved"].includes(normalized)) {
    return "ok";
  }
  if (["blocked", "error", "fail", "failed", "review_required", "warning", "warn", "conflicted"].includes(normalized)) {
    return "hot";
  }
  return "";
}

function formatReportCheckLabel(key) {
  const normalized = String(key || "").trim().toLowerCase();
  const labels = {
    claim_source: copy("Claim source binding", "主张来源绑定"),
    section_coverage: copy("Section coverage", "章节覆盖"),
    contradictions: copy("Contradictions", "冲突"),
    export_gates: copy("Export gates", "导出门禁"),
    fact_consistency: copy("Fact consistency", "事实一致性"),
    coverage: copy("Coverage", "覆盖度"),
  };
  return labels[normalized] || String(key || "").replace(/_/g, " ").trim();
}

function formatReportOperatorAction(action) {
  const normalized = String(action || "").trim().toLowerCase();
  const labels = {
    allow_export: copy("Allow export", "允许导出"),
    review_before_export: copy("Review before export", "导出前复核"),
    hold_export: copy("Hold export", "暂停导出"),
    approve: copy("Approve", "批准"),
  };
  return labels[normalized] || String(action || "").replace(/_/g, " ").trim();
}

function syncReportSelectionState() {
  const availableReports = Array.isArray(state.reports) ? state.reports : [];
  if (!availableReports.some((report) => String(report.id || "").trim() === String(state.selectedReportId || "").trim())) {
    state.selectedReportId = availableReports[0] ? String(availableReports[0].id || "") : "";
  }
  const sections = getReportSectionsForReport(state.selectedReportId);
  if (!sections.some((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim())) {
    state.selectedReportSectionId = sections[0] ? String(sections[0].id || "") : "";
  }
  const availableClaims = Array.isArray(state.claimCards) ? state.claimCards : [];
  if (!availableClaims.some((claim) => String(claim.id || "").trim() === String(state.selectedClaimId || "").trim())) {
    const reportClaimIds = getReportClaimIds(state.selectedReportId);
    const matchingClaim = availableClaims.find((claim) => reportClaimIds.includes(String(claim.id || "").trim()));
    state.selectedClaimId = matchingClaim
      ? String(matchingClaim.id || "")
      : (availableClaims[0] ? String(availableClaims[0].id || "") : "");
  }
}

async function loadReportComposition(identifier, { includeMarkdown = false, render = true, force = false } = {}) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return;
  }
  if (force || !state.reportCompositions[normalized]) {
    state.reportCompositions[normalized] = await api(`/api/reports/${normalized}/compose`);
  }
  if (includeMarkdown && (force || !state.reportMarkdown[normalized])) {
    state.reportMarkdown[normalized] = await apiText(`/api/reports/${normalized}/export?output_format=markdown`);
  }
  if (render) {
    renderClaimsWorkspace();
    renderReportStudio();
    renderTopbarContext();
  }
}

async function selectReport(identifier, { sectionId = "" } = {}) {
  state.selectedReportId = String(identifier || "").trim();
  if (sectionId) {
    state.selectedReportSectionId = String(sectionId || "").trim();
  }
  syncReportSelectionState();
  renderClaimsWorkspace();
  renderReportStudio();
  renderTopbarContext();
  if (state.selectedReportId) {
    await loadReportComposition(state.selectedReportId);
  }
}

async function previewReportMarkdown(identifier) {
  await inspectReportArtifact("markdown", identifier);
}

function formatDeliverySubjectKind(value) {
  const normalized = String(value || "").trim().toLowerCase();
  const labels = {
    profile: copy("Profile", "配置"),
    watch_mission: copy("Mission", "任务"),
    story: copy("Story", "故事"),
    report: copy("Report", "报告"),
  };
  return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
}

function formatDeliveryOutputKind(value) {
  const normalized = String(value || "").trim().toLowerCase();
  const labels = {
    alert_event: copy("Alert Event", "告警事件"),
    feed_json: copy("JSON Feed", "JSON 订阅"),
    feed_rss: copy("RSS Feed", "RSS 订阅"),
    feed_atom: copy("Atom Feed", "Atom 订阅"),
    story_json: copy("Story JSON", "故事 JSON"),
    story_markdown: copy("Story Markdown", "故事 Markdown"),
    report_brief: copy("Report Brief", "报告摘要"),
    report_full: copy("Report Full", "完整报告"),
    report_sources: copy("Report Sources", "报告来源"),
    report_watch_pack: copy("Report Watch Pack", "报告监控包"),
  };
  return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
}

function defaultDeliveryDraft() {
  const selectedReport = getSelectedReportRecord();
  const firstReport = Array.isArray(state.reports) && state.reports.length ? state.reports[0] : null;
  const report = selectedReport || firstReport;
  const firstRoute = Array.isArray(state.routes) && state.routes.length
    ? normalizeRouteName(state.routes[0]?.name)
    : "";
  return {
    subject_kind: report ? "report" : "profile",
    subject_ref: report ? String(report.id || "").trim() : "default",
    output_kind: report ? "report_full" : "feed_json",
    delivery_mode: firstRoute ? "push" : "pull",
    status: "active",
    route_names: firstRoute ? [firstRoute] : [],
    cursor_or_since: "",
  };
}

function getDeliverySubjectRefOptions(subjectKind) {
  const normalized = String(subjectKind || "").trim().toLowerCase();
  if (normalized === "profile") {
    return [{
      value: "default",
      label: copy("Default profile", "默认配置"),
      detail: copy("Use the canonical feed subscription target.", "使用默认的订阅配置目标。"),
    }];
  }
  if (normalized === "watch_mission") {
    return (Array.isArray(state.watches) ? state.watches : []).map((watch) => ({
      value: String(watch.id || "").trim(),
      label: String(watch.name || watch.id || "").trim(),
      detail: String(watch.query || "").trim(),
    }));
  }
  if (normalized === "story") {
    return (Array.isArray(state.stories) ? state.stories : []).map((story) => ({
      value: String(story.id || "").trim(),
      label: String(story.title || story.id || "").trim(),
      detail: String(story.summary || "").trim(),
    }));
  }
  if (normalized === "report") {
    return (Array.isArray(state.reports) ? state.reports : []).map((report) => ({
      value: String(report.id || "").trim(),
      label: String(report.title || report.id || "").trim(),
      detail: String(report.summary || "").trim(),
    }));
  }
  return [];
}

function getDeliveryOutputOptions(subjectKind) {
  const normalized = String(subjectKind || "").trim().toLowerCase();
  return (deliveryOutputOptionsBySubject[normalized] || []).map((value) => ({
    value,
    label: formatDeliveryOutputKind(value),
  }));
}

function normalizeDeliveryDraft(draft) {
  const source = draft && typeof draft === "object" ? draft : defaultDeliveryDraft();
  const subjectKind = deliverySubjectOptions.includes(String(source.subject_kind || "").trim().toLowerCase())
    ? String(source.subject_kind || "").trim().toLowerCase()
    : defaultDeliveryDraft().subject_kind;
  const subjectOptions = getDeliverySubjectRefOptions(subjectKind);
  const outputOptions = getDeliveryOutputOptions(subjectKind);
  const subjectRef = subjectOptions.some((option) => option.value === String(source.subject_ref || "").trim())
    ? String(source.subject_ref || "").trim()
    : (subjectOptions[0]?.value || "");
  const outputKind = outputOptions.some((option) => option.value === String(source.output_kind || "").trim())
    ? String(source.output_kind || "").trim()
    : (outputOptions[0]?.value || "");
  const deliveryMode = deliveryModeOptions.includes(String(source.delivery_mode || "").trim().toLowerCase())
    ? String(source.delivery_mode || "").trim().toLowerCase()
    : "pull";
  const status = deliveryStatusOptions.includes(String(source.status || "").trim().toLowerCase())
    ? String(source.status || "").trim().toLowerCase()
    : "active";
  const routeNames = uniqueValues((Array.isArray(source.route_names) ? source.route_names : parseDelimitedInput(source.route_names))
    .map((value) => normalizeRouteName(value))
    .filter(Boolean));
  return {
    subject_kind: subjectKind,
    subject_ref: subjectRef,
    output_kind: outputKind,
    delivery_mode: deliveryMode,
    status,
    route_names: routeNames,
    cursor_or_since: String(source.cursor_or_since || "").trim(),
  };
}

function collectDeliveryDraft(form) {
  const formData = new FormData(form);
  return normalizeDeliveryDraft({
    subject_kind: formData.get("subject_kind"),
    subject_ref: formData.get("subject_ref"),
    output_kind: formData.get("output_kind"),
    delivery_mode: formData.get("delivery_mode"),
    status: formData.get("status"),
    route_names: parseDelimitedInput(formData.get("route_names")),
    cursor_or_since: formData.get("cursor_or_since"),
  });
}

function syncDeliveryDraft() {
  state.deliveryDraft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
}

function defaultDigestProfileDraft() {
  const profile = state.digestConsole?.profile?.profile && typeof state.digestConsole.profile.profile === "object"
    ? state.digestConsole.profile.profile
    : {};
  const target = profile.default_delivery_target && typeof profile.default_delivery_target === "object"
    ? profile.default_delivery_target
    : {};
  const firstRoute = Array.isArray(state.routes) && state.routes.length
    ? normalizeRouteName(state.routes[0]?.name)
    : "";
  return {
    language: String(profile.language || "en").trim() || "en",
    timezone: String(profile.timezone || "UTC").trim() || "UTC",
    frequency: String(profile.frequency || "@daily").trim() || "@daily",
    default_delivery_target: {
      kind: "route",
      ref: normalizeRouteName(target.ref || firstRoute),
    },
  };
}

function normalizeDigestProfileDraft(draft) {
  const source = draft && typeof draft === "object" ? draft : defaultDigestProfileDraft();
  const target = source.default_delivery_target && typeof source.default_delivery_target === "object"
    ? source.default_delivery_target
    : {};
  return {
    language: String(source.language || "en").trim() || "en",
    timezone: String(source.timezone || "UTC").trim() || "UTC",
    frequency: String(source.frequency || "@daily").trim() || "@daily",
    default_delivery_target: {
      kind: "route",
      ref: normalizeRouteName(target.ref || ""),
    },
  };
}

function syncDigestProfileDraft() {
  state.digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
}

function collectDigestProfileDraft(form) {
  const formData = new FormData(form);
  return normalizeDigestProfileDraft({
    language: formData.get("language"),
    timezone: formData.get("timezone"),
    frequency: formData.get("frequency"),
    default_delivery_target: {
      kind: "route",
      ref: formData.get("default_delivery_target_ref"),
    },
  });
}

function summarizePathTail(value, depth = 2) {
  const parts = String(value || "").split("/").filter(Boolean);
  if (!parts.length) {
    return "";
  }
  return parts.slice(-Math.max(1, depth)).join("/");
}

function getDeliverySubscriptionRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  return (Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [])
    .find((row) => String(row.id || "").trim() === normalized) || null;
}

function getSelectedDeliverySubscription() {
  return getDeliverySubscriptionRecord(state.selectedDeliverySubscriptionId);
}

function syncDeliverySelectionState() {
  const rows = Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [];
  if (!rows.some((row) => String(row.id || "").trim() === String(state.selectedDeliverySubscriptionId || "").trim())) {
    state.selectedDeliverySubscriptionId = rows[0] ? String(rows[0].id || "").trim() : "";
  }
  const selected = getSelectedDeliverySubscription();
  if (!selected) {
    return;
  }
  const subscriptionId = String(selected.id || "").trim();
  const reportProfiles = String(selected.subject_kind || "").trim().toLowerCase() === "report"
    ? state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selected.subject_ref || "").trim())
    : [];
  const currentProfileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
  if (!reportProfiles.some((profile) => String(profile.id || "").trim() === currentProfileId)) {
    state.deliveryPackageProfileIds[subscriptionId] = reportProfiles[0] ? String(reportProfiles[0].id || "").trim() : "";
  }
}

function summarizeDeliverySubject(subscription) {
  if (!subscription || typeof subscription !== "object") {
    return "";
  }
  const subjectKind = String(subscription.subject_kind || "").trim().toLowerCase();
  const subjectRef = String(subscription.subject_ref || "").trim();
  if (subjectKind === "report") {
    return getReportRecord(subjectRef)?.title || subjectRef;
  }
  if (subjectKind === "story") {
    return (Array.isArray(state.stories) ? state.stories : [])
      .find((story) => String(story.id || "").trim() === subjectRef)?.title || subjectRef;
  }
  if (subjectKind === "watch_mission") {
    return (Array.isArray(state.watches) ? state.watches : [])
      .find((watch) => String(watch.id || "").trim() === subjectRef)?.name || subjectRef;
  }
  return subjectRef || copy("Default profile", "默认配置");
}

function getDeliveryDispatchRowsForSubscription(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return [];
  }
  return (Array.isArray(state.deliveryDispatchRecords) ? state.deliveryDispatchRecords : [])
    .filter((row) => String(row.subscription_id || "").trim() === normalized);
}

async function loadDeliveryPackageAudit(identifier, { profileId = "", render = true } = {}) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  const query = profileId ? `?profile_id=${encodeURIComponent(profileId)}` : "";
  try {
    const payload = await api(`/api/delivery-subscriptions/${normalized}/package${query}`);
    state.deliveryPackageAudits[normalized] = payload;
    state.deliveryPackageErrors[normalized] = "";
    state.deliveryPackageProfileIds[normalized] = String(payload.profile_id || profileId || "").trim();
    if (render) {
      renderDeliveryWorkspace();
    }
    return payload;
  } catch (error) {
    state.deliveryPackageErrors[normalized] = error.message;
    if (render) {
      renderDeliveryWorkspace();
    }
    throw error;
  }
}

async function loadDigestConsole({ render = true, preserveDraft = true, force = false } = {}) {
  if (!force && state.digestConsole) {
    if (!preserveDraft || !state.digestProfileDraft) {
      state.digestProfileDraft = normalizeDigestProfileDraft(state.digestConsole?.profile?.profile || defaultDigestProfileDraft());
    }
    if (render) {
      renderDeliveryWorkspace();
    }
    return state.digestConsole;
  }
  const payload = await api("/api/digest/console?profile=default&limit=8");
  state.digestConsole = payload;
  if (!preserveDraft || !state.digestProfileDraft) {
    state.digestProfileDraft = normalizeDigestProfileDraft(payload?.profile?.profile || defaultDigestProfileDraft());
  }
  if (render) {
    renderDeliveryWorkspace();
  }
  return payload;
}

async function attachClaimToReport(claimId, reportId, sectionId = "", bundleId = "") {
  const normalizedClaimId = String(claimId || "").trim();
  const normalizedReportId = String(reportId || "").trim();
  const normalizedSectionId = String(sectionId || "").trim();
  const normalizedBundleId = String(bundleId || "").trim();
  if (!normalizedClaimId || !normalizedReportId) {
    return;
  }
  const report = getReportRecord(normalizedReportId) || await api(`/api/reports/${normalizedReportId}`);
  const nextReportClaimIds = uniqueValues([...(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []), normalizedClaimId]);
  const nextReportBundleIds = normalizedBundleId
    ? uniqueValues([...(Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []), normalizedBundleId])
    : (Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []);
  await api(`/api/reports/${normalizedReportId}`, {
    method: "PUT",
    payload: { claim_card_ids: nextReportClaimIds, citation_bundle_ids: nextReportBundleIds },
  });
  if (normalizedSectionId) {
    const section = getReportSectionsForReport(normalizedReportId).find((entry) => String(entry.id || "").trim() === normalizedSectionId)
      || await api(`/api/report-sections/${normalizedSectionId}`);
    const nextSectionClaimIds = uniqueValues([...(Array.isArray(section?.claim_card_ids) ? section.claim_card_ids : []), normalizedClaimId]);
    await api(`/api/report-sections/${normalizedSectionId}`, {
      method: "PUT",
      payload: { claim_card_ids: nextSectionClaimIds },
    });
  }
}

async function submitStoryDeck(form) {
  const draft = collectStoryDraft(form);
  state.storyDraft = draft;
  if (!draft.title.trim()) {
    setStageFeedback("review", {
      kind: "blocked",
      title: copy("Story draft still needs a title", "故事草稿仍然缺少标题"),
      copy: copy("Add a story title before this brief can move into the review lane.", "补上故事标题后，这条简报才能进入审阅阶段。"),
      actionHierarchy: {
        primary: {
          label: copy("Complete Story Intake", "继续补全故事录入"),
          attrs: { "data-empty-focus": "story", "data-empty-field": "title" },
        },
        secondary: [
          {
            label: copy("Open Triage", "打开分诊"),
            attrs: { "data-empty-jump": "section-triage" },
          },
        ],
      },
    });
    showToast(copy("Provide a story title before creating a brief.", "创建故事前请先填写标题。"), "error");
    focusStoryDeck("title");
    return;
  }
  const submitButton = form?.querySelector("button[type='submit']");
  if (submitButton) {
    submitButton.disabled = true;
  }
  try {
    const created = await api("/api/stories", {
      method: "POST",
      payload: draft,
    });
    setStoryDraft(defaultStoryDraft());
    pushActionEntry({
      kind: copy("story create", "故事创建"),
      label: state.language === "zh" ? `已创建故事：${created.title}` : `Created story: ${created.title}`,
      detail: copy("The story is now part of the workspace and can be archived or refined in place.", "该故事已进入工作台，后续可以继续编辑或归档。"),
      undoLabel: copy("Delete story", "删除故事"),
      undo: async () => {
        await api(`/api/stories/${created.id}`, { method: "DELETE" });
        await refreshBoard();
        showToast(
          state.language === "zh" ? `已删除故事：${created.title}` : `Story deleted: ${created.title}`,
          "success",
        );
      },
    });
    await refreshBoard();
    state.selectedStoryId = created.id;
    state.storyDetails[created.id] = created;
    renderStories();
    setStageFeedback("review", {
      kind: "completion",
      title: state.language === "zh" ? `故事已创建：${created.title}` : `Story created: ${created.title}`,
      copy: copy(
        "The review lane now has a persisted story object. Refine it in the workspace or inspect delivery readiness next.",
        "审阅阶段现在已经拥有持久化故事对象；下一步可以继续在工作台里完善它，或检查交付就绪度。"
      ),
      actionHierarchy: {
        primary: {
          label: copy("Open Story Workspace", "打开故事工作台"),
          attrs: { "data-empty-jump": "section-story" },
        },
        secondary: [
          {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        ],
      },
    });
    showToast(
      state.language === "zh" ? `故事已创建：${created.title}` : `Story created: ${created.title}`,
      "success",
    );
  } catch (error) {
    reportError(error, copy("Create story", "创建故事"));
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}

async function setStoryStatusQuick(identifier, nextStatus) {
  const story = getStoryRecord(identifier);
  if (!story) {
    throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
  }
  const targetStatus = String(nextStatus || "").trim().toLowerCase();
  if (!targetStatus || targetStatus === String(story.status || "active").trim().toLowerCase()) {
    return;
  }
  const previousStory = {
    title: story.title || "",
    summary: story.summary || "",
    status: story.status || "active",
  };
  try {
    await api(`/api/stories/${story.id}`, {
      method: "PUT",
      payload: { status: targetStatus },
    });
    pushActionEntry({
      kind: copy("story state", "故事状态"),
      label: state.language === "zh"
        ? `已将故事切换为 ${localizeWord(targetStatus)}：${story.title}`
        : `Story moved to ${targetStatus}: ${story.title}`,
      detail: copy("Use undo to restore the previous workspace state.", "如需回退，可在最近操作里恢复。"),
      undoLabel: copy("Restore story", "恢复故事"),
      undo: async () => {
        await api(`/api/stories/${story.id}`, {
          method: "PUT",
          payload: previousStory,
        });
        await refreshBoard();
        showToast(
          state.language === "zh" ? `已恢复故事：${previousStory.title}` : `Story restored: ${previousStory.title}`,
          "success",
        );
      },
    });
    await refreshBoard();
    showToast(
      state.language === "zh"
        ? `故事状态已更新：${story.title}`
        : `Story status updated: ${story.title}`,
      "success",
    );
  } catch (error) {
    reportError(error, copy("Update story state", "更新故事状态"));
  }
}

async function deleteStoryFromWorkspace(identifier) {
  const story = getStoryRecord(identifier);
  if (!story) {
    throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
  }
  const confirmed = window.confirm(
    state.language === "zh"
      ? `确认删除故事 ${story.title}？这会把它从当前工作台移除。`
      : `Delete story ${story.title} from the workspace?`,
  );
  if (!confirmed) {
    return;
  }
  const snapshot = JSON.parse(JSON.stringify(story));
  try {
    await api(`/api/stories/${story.id}`, { method: "DELETE" });
    if (String(state.storyInspector?.storyId || "").trim() === String(story.id || "").trim()) {
      closeStoryInspector({ restoreFocus: false });
    }
    removeStoryFromState(story.id);
    pushActionEntry({
      kind: copy("story delete", "故事删除"),
      label: state.language === "zh" ? `已删除故事：${story.title}` : `Deleted story: ${story.title}`,
      detail: copy("The full story payload is kept in recent actions so you can restore it once.", "完整故事快照会暂存在最近操作中，方便你单次恢复。"),
      undoLabel: copy("Restore story", "恢复故事"),
      undo: async () => {
        await api("/api/stories", {
          method: "POST",
          payload: snapshot,
        });
        await refreshBoard();
        showToast(
          state.language === "zh" ? `已恢复故事：${snapshot.title}` : `Story restored: ${snapshot.title}`,
          "success",
        );
      },
    });
    await refreshBoard();
    showToast(
      state.language === "zh" ? `故事已删除：${story.title}` : `Story deleted: ${story.title}`,
      "success",
    );
  } catch (error) {
    reportError(error, copy("Delete story", "删除故事"));
  }
}

function isStorySelected(storyId) {
  return state.selectedStoryIds.includes(storyId);
}

function toggleStorySelection(storyId, checked = null) {
  if (!storyId) {
    return;
  }
  const next = new Set(state.selectedStoryIds);
  const shouldSelect = checked === null ? !next.has(storyId) : Boolean(checked);
  if (shouldSelect) {
    next.add(storyId);
    state.selectedStoryId = storyId;
  } else {
    next.delete(storyId);
  }
  state.selectedStoryIds = Array.from(next);
}

function selectVisibleStories(filteredStories) {
  const visibleIds = (Array.isArray(filteredStories) ? filteredStories : []).map((story) => story.id);
  state.selectedStoryIds = visibleIds;
  if (visibleIds.length && !visibleIds.includes(state.selectedStoryId)) {
    state.selectedStoryId = visibleIds[0];
  }
}

function clearStorySelection() {
  state.selectedStoryIds = [];
}

async function runStoryBatchStatusUpdate(storyIds, nextStatus) {
  const normalizedIds = uniqueValues(storyIds).filter((storyId) => state.stories.some((story) => story.id === storyId));
  if (!normalizedIds.length || !nextStatus || state.storyBulkBusy) {
    return;
  }
  state.storyBulkBusy = true;
  const previousStates = {};
  normalizedIds.forEach((storyId) => {
    const currentStory = getStoryRecord(storyId);
    previousStates[storyId] = currentStory ? String(currentStory.status || "active") : "active";
    if (currentStory && state.storyDetails[storyId]) {
      state.storyDetails[storyId] = {
        ...state.storyDetails[storyId],
        status: nextStatus,
      };
    }
  });
  renderStories();
  try {
    for (const storyId of normalizedIds) {
      await api(`/api/stories/${storyId}`, {
        method: "PUT",
        payload: { status: nextStatus },
      });
    }
    state.selectedStoryIds = [];
    pushActionEntry({
      kind: copy("story batch", "故事批处理"),
      label: state.language === "zh"
        ? `已批量将 ${normalizedIds.length} 条故事切换为 ${localizeWord(nextStatus)}`
        : `Moved ${normalizedIds.length} stories to ${nextStatus}`,
      detail: state.language === "zh"
        ? `涉及故事：${normalizedIds.join(", ")}`
        : `Stories: ${normalizedIds.join(", ")}`,
      undoLabel: copy("Restore stories", "恢复故事"),
      undo: async () => {
        for (const storyId of normalizedIds) {
          await api(`/api/stories/${storyId}`, {
            method: "PUT",
            payload: { status: previousStates[storyId] || "active" },
          });
        }
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已恢复 ${normalizedIds.length} 条故事`
            : `Restored ${normalizedIds.length} stories`,
          "success",
        );
      },
    });
    await refreshBoard();
    showToast(
      state.language === "zh"
        ? `已批量更新 ${normalizedIds.length} 条故事`
        : `Updated ${normalizedIds.length} stories`,
      "success",
    );
  } catch (error) {
    normalizedIds.forEach((storyId) => {
      if (state.storyDetails[storyId]) {
        state.storyDetails[storyId] = {
          ...state.storyDetails[storyId],
          status: previousStates[storyId] || "active",
        };
      }
    });
    renderStories();
    throw error;
  } finally {
    state.storyBulkBusy = false;
    renderStories();
  }
}
