// Split group 2d: shared governance summaries, action histories, and operator guidance surfaces.
// Depends on prior fragments and 00-common.js.

function metricCard(label, value, tone = "") {
  return `<div class="metric"><div class="metric-label">${label}</div><div class="metric-value ${tone}">${value}</div></div>`;
}

function formatRate(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return `${Math.round(Number(value) * 100)}%`;
}

function skeletonCard(lines = 3) {
  return `
    <div class="card skeleton">
      <div class="stack">
        ${Array.from({ length: lines }).map((_, index) => `
          <div class="skeleton-block ${index === 0 ? "short" : index === lines - 1 ? "long" : "medium"}"></div>
        `).join("")}
      </div>
    </div>
  `;
}

function renderActionHistory() {
  const root = $("console-action-history");
  if (!root) {
    return;
  }
  if (!state.actionLog.length) {
    root.innerHTML = `<div class="empty">${copy("No reversible action yet. Create, tune, or triage something and it will show up here.", "当前还没有可回退的操作。创建、调整或分诊后，会在这里显示。")}</div>`;
    return;
  }
  root.innerHTML = state.actionLog.slice(0, 6).map((entry) => `
    <div class="action-log-item">
      <div class="card-top">
        <div>
          <div class="mono">${escapeHtml(entry.kind || "action")}</div>
          <div>${escapeHtml(entry.label || "")}</div>
        </div>
        <span class="chip ${entry.status === "error" ? "hot" : entry.status === "ready" ? "ok" : ""}">${escapeHtml(localizeWord(entry.status || "done"))}</span>
      </div>
      <div class="panel-sub">${escapeHtml(entry.detail || "")}</div>
      <div class="actions">
        ${
          entry.undo
            ? `<button class="btn-secondary" type="button" data-action-undo="${entry.id}">${escapeHtml(entry.undoLabel || copy("Undo", "撤销"))}</button>`
            : ""
        }
      </div>
    </div>
  `).join("");
  root.querySelectorAll("[data-action-undo]").forEach((button) => {
    button.addEventListener("click", async () => {
      const item = state.actionLog.find((entry) => entry.id === button.dataset.actionUndo);
      if (!item || !item.undo) {
        return;
      }
      button.disabled = true;
      try {
        await item.undo();
        state.actionLog = state.actionLog.filter((entry) => entry.id !== item.id);
        renderActionHistory();
      } catch (error) {
        reportError(error, "Undo action");
      } finally {
        button.disabled = false;
      }
    });
  });
}

function pushActionEntry(entry) {
  state.actionLog = [{
    id: `action-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    timestamp: new Date().toISOString(),
    status: "ready",
    ...entry,
  }, ...state.actionLog].slice(0, 8);
  renderActionHistory();
}

function updateActionEntry(entryId, patch = {}) {
  if (!entryId) {
    return;
  }
  let changed = false;
  state.actionLog = state.actionLog.map((entry) => {
    if (entry.id !== entryId) {
      return entry;
    }
    changed = true;
    return {
      ...entry,
      ...patch,
    };
  });
  if (changed) {
    renderActionHistory();
  }
}

function buildAlertRules({ route = "", keyword = "", domain = "", domains = null, minScore = 0, minConfidence = 0 }) {
  const cleanedRoute = String(route || "").trim();
  const cleanedKeyword = String(keyword || "").trim();
  const domainList = Array.isArray(domains)
    ? parseListField(domains.join(", "))
    : parseListField(domain);
  const scoreValue = Math.max(0, Number(minScore || 0));
  const confidenceValue = Math.max(0, Number(minConfidence || 0));
  if (!(cleanedRoute || cleanedKeyword || domainList.length || scoreValue > 0 || confidenceValue > 0)) {
    return [];
  }
  const alertRule = {
    name: "console-threshold",
    min_score: scoreValue,
    min_confidence: confidenceValue,
    channels: ["json"],
  };
  if (cleanedRoute) alertRule.routes = [cleanedRoute];
  if (cleanedKeyword) alertRule.keyword_any = [cleanedKeyword];
  if (domainList.length) alertRule.domains = domainList;
  return [alertRule];
}

function renderLifecycleGuideCard({ title = "", summary = "", steps = [], actions = [], tone = "ok" } = {}) {
  const stepsHtml = steps.map((step, index) => `
    <div class="guide-card">
      <div class="guide-step">${String(index + 1).padStart(2, "0")}</div>
      <div class="mono">${escapeHtml(step.title || "")}</div>
      <div class="panel-sub">${escapeHtml(step.copy || "")}</div>
    </div>
  `).join("");
  const actionsHtml = actions.length
    ? `<div class="actions" style="margin-top:14px;">${actions.map((action) => `
        <button
          class="${action.primary ? "btn-primary" : "btn-secondary"}"
          type="button"
          ${action.section ? `data-empty-jump="${escapeHtml(action.section)}"` : ""}
          ${action.focus ? `data-empty-focus="${escapeHtml(action.focus)}"` : ""}
          ${action.field ? `data-empty-field="${escapeHtml(action.field)}"` : ""}
          ${action.watch ? `data-empty-watch="${escapeHtml(action.watch)}"` : ""}
          ${action.runWatch ? `data-empty-run-watch="${escapeHtml(action.runWatch)}"` : ""}
          ${action.toggleWatch ? `data-watch-toggle="${escapeHtml(action.toggleWatch)}"` : ""}
          ${action.watchEnabled ? `data-watch-enabled="${escapeHtml(action.watchEnabled)}"` : ""}
        >${escapeHtml(action.label || "")}</button>
      `).join("")}</div>`
    : "";
  return `
    <details class="guide-disclosure">
      <summary>
        <div>
          <div class="guide-disclosure-kicker">${copy("lifecycle guide", "生命周期引导")}</div>
          <div class="guide-disclosure-title">${escapeHtml(title)}</div>
        </div>
        <span class="chip ${tone}">${copy("browser-first", "浏览器优先")}</span>
        <svg class="guide-disclosure-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
          <path d="M4 6 L8 10 L12 6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </summary>
      <div class="guide-disclosure-body">
        <div class="panel-sub">${escapeHtml(summary)}</div>
        <div class="guide-grid">${stepsHtml}</div>
        ${actionsHtml}
      </div>
    </details>
  `;
}

function getWatchRecord(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return null;
  }
  return state.watchDetails[normalized] || state.watches.find((watch) => watch.id === normalized) || null;
}

async function triggerWatchRun(identifier) {
  const normalized = String(identifier || "").trim();
  if (!normalized) {
    return;
  }
  const watch = getWatchRecord(normalized);
  if (watch && watch.enabled === false) {
    setStageFeedback("monitor", {
      kind: "blocked",
      title: copy("Mission is paused and cannot run yet", "任务已暂停，当前无法执行"),
      copy: copy("Enable the selected mission first, then rerun it from the monitoring lane.", "请先在监测阶段重新启用该任务，再发起执行。"),
      actionHierarchy: {
        primary: {
          label: copy("Enable Mission", "启用任务"),
          attrs: { "data-watch-toggle": normalized, "data-watch-enabled": "0" },
        },
        secondary: [
          {
            label: copy("Open Mission Board", "打开任务列表"),
            attrs: { "data-empty-jump": "section-board" },
          },
        ],
      },
    });
    showToast(copy("Mission is paused. Enable it before running.", "任务已停用，请先启用后再执行。"), "error");
    return;
  }
  const watchLabel = String((watch && (watch.name || watch.id)) || normalized).trim() || normalized;
  const actionId = `mission-run-${normalized}-${Date.now()}`;
  pushActionEntry({
    id: actionId,
    status: "pending",
    kind: copy("mission run", "任务执行"),
    label: state.language === "zh" ? `执行中：${watchLabel}` : `Running: ${watchLabel}`,
    detail: copy("Fetching sources and waiting for mission results.", "正在抓取来源并等待任务结果返回。"),
  });
  showToast(
    state.language === "zh" ? `任务开始执行：${watchLabel}` : `Mission started: ${watchLabel}`,
    "info",
  );
  try {
    const payload = await api(`/api/watches/${normalized}/run`, { method: "POST" });
    const run = payload && typeof payload === "object" && payload.run && typeof payload.run === "object" ? payload.run : {};
    const items = Array.isArray(payload?.items) ? payload.items : [];
    const alertEvents = Array.isArray(payload?.alert_events) ? payload.alert_events : [];
    const itemCount = items.length || Number(run.item_count || 0);
    const alertCount = alertEvents.length;
    const outcomeDetail = itemCount > 0
      ? state.language === "zh"
        ? `执行完成，返回 ${itemCount} 条结果${alertCount ? `，触发 ${alertCount} 条告警` : ""}。`
        : `Run finished with ${itemCount} result(s)${alertCount ? ` and ${alertCount} alert event(s)` : ""}.`
      : state.language === "zh"
        ? "执行完成，但没有返回结果。可调整查询词、平台或阈值后重试。"
        : "Run finished with no results. Adjust the query, platform, or thresholds and try again.";
    updateActionEntry(actionId, {
      status: "ready",
      label: state.language === "zh" ? `任务完成：${watchLabel}` : `Mission completed: ${watchLabel}`,
      detail: outcomeDetail,
    });
    await refreshBoard();
    setStageFeedback("monitor", itemCount > 0
      ? {
          kind: "completion",
          title: state.language === "zh"
            ? `任务已完成并返回 ${itemCount} 条结果`
            : `Mission completed with ${itemCount} result(s)`,
          copy: alertCount > 0
            ? copy(
                "Monitoring already produced usable results and alert activity. Review the evidence lane or inspect Cockpit for the full outcome.",
                "监测阶段已经产出可用结果并触发了告警活动；下一步可以进入审阅工作线，或回到驾驶舱查看完整结果。"
              )
            : copy(
                "Monitoring produced usable results. Review the evidence lane next or inspect Cockpit for the full outcome.",
                "监测阶段已经产出可用结果；下一步可以进入审阅工作线，或回到驾驶舱查看完整结果。"
              ),
          facts: [
            { label: copy("Results", "结果数"), value: String(itemCount) },
            { label: copy("Alerts", "告警数"), value: String(alertCount) },
          ],
          actionHierarchy: {
            primary: {
              label: copy("Open Triage", "打开分诊"),
              attrs: { "data-empty-jump": "section-triage" },
            },
            secondary: [
              {
                label: copy("Open Cockpit", "打开任务详情"),
                attrs: { "data-empty-jump": "section-cockpit" },
              },
            ],
          },
        }
      : {
          kind: "no_result",
          title: copy("Mission completed with no results", "任务执行完成，但没有结果"),
          copy: copy(
            "The mission finished, but the current query, platform, or thresholds did not return usable evidence. Adjust the draft, then rerun it.",
            "任务已经执行完成，但当前查询词、平台或阈值没有返回可用证据。请调整草稿后再重跑。"
          ),
          facts: [
            { label: copy("Mission", "任务"), value: watchLabel },
            { label: copy("Alerts", "告警数"), value: String(alertCount) },
          ],
          actionHierarchy: {
            primary: {
              label: copy("Edit Mission Draft", "编辑任务草稿"),
              attrs: { "data-empty-focus": "mission", "data-empty-field": "query" },
            },
            secondary: [
              {
                label: copy("Open Cockpit", "打开任务详情"),
                attrs: { "data-empty-jump": "section-cockpit" },
              },
            ],
          },
        });
    showToast(
      itemCount > 0
        ? (state.language === "zh" ? `任务完成：${itemCount} 条结果` : `Mission completed: ${itemCount} result(s)`)
        : copy("Mission completed with no results.", "任务执行完成，但没有结果。"),
      itemCount > 0 ? "success" : "info",
    );
    return payload;
  } catch (error) {
    const message = error && error.message ? error.message : String(error || "Unknown error");
    updateActionEntry(actionId, {
      status: "error",
      label: state.language === "zh" ? `任务失败：${watchLabel}` : `Mission failed: ${watchLabel}`,
      detail: message,
    });
    setStageFeedback("monitor", {
      kind: "blocked",
      title: state.language === "zh" ? `任务执行失败：${watchLabel}` : `Mission failed: ${watchLabel}`,
      copy: message,
      actionHierarchy: {
        primary: {
          label: copy("Open Cockpit", "打开任务详情"),
          attrs: { "data-empty-jump": "section-cockpit" },
        },
        secondary: [
          {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        ],
      },
    });
    throw error;
  }
}

async function handleWatchToggle(button) {
  const identifier = String(button?.dataset?.watchToggle || "").trim();
  if (!identifier) {
    return;
  }
  const isEnabled = String(button.dataset.watchEnabled || "1") === "1";
  const previousWatch = state.watches.find((watch) => watch.id === identifier);
  const previousDetail = state.watchDetails[identifier] ? { ...state.watchDetails[identifier] } : null;
  button.disabled = true;
  if (previousWatch) {
    previousWatch.enabled = !isEnabled;
  }
  if (state.watchDetails[identifier]) {
    state.watchDetails[identifier].enabled = !isEnabled;
  }
  renderWatches();
  renderWatchDetail();
  try {
    await api(`/api/watches/${identifier}/${isEnabled ? "disable" : "enable"}`, { method: "POST" });
    pushActionEntry({
      kind: "mission state",
      label: `${isEnabled ? "Disabled" : "Enabled"} ${previousWatch && previousWatch.name ? previousWatch.name : identifier}`,
      detail: `${identifier} switched to ${isEnabled ? "disabled" : "enabled"}.`,
      undoLabel: isEnabled ? "Re-enable" : "Disable again",
      undo: async () => {
        await api(`/api/watches/${identifier}/${isEnabled ? "enable" : "disable"}`, { method: "POST" });
        await refreshBoard();
        showToast(`Mission ${isEnabled ? "re-enabled" : "disabled"}: ${identifier}`, "success");
      },
    });
    await refreshBoard();
    setStageFeedback("monitor", isEnabled
      ? {
          kind: "warning",
          title: state.language === "zh" ? `任务已暂停：${identifier}` : `Mission paused: ${identifier}`,
          copy: copy(
            "The mission now stays out of monitoring until it is enabled again.",
            "这条任务会从监测阶段暂停，直到再次被启用。"
          ),
          actionHierarchy: {
            primary: {
              label: copy("Enable Mission", "启用任务"),
              attrs: { "data-watch-toggle": identifier, "data-watch-enabled": "0" },
            },
            secondary: [
              {
                label: copy("Open Mission Board", "打开任务列表"),
                attrs: { "data-empty-jump": "section-board" },
              },
            ],
          },
        }
      : {
          kind: "completion",
          title: state.language === "zh" ? `任务已启用：${identifier}` : `Mission enabled: ${identifier}`,
          copy: copy(
            "The mission is back in the monitoring lane and can be run immediately.",
            "这条任务已经重新回到监测阶段，现在可以立即执行。"
          ),
          actionHierarchy: {
            primary: {
              label: copy("Run Mission", "执行任务"),
              attrs: { "data-empty-run-watch": identifier },
            },
            secondary: [
              {
                label: copy("Open Cockpit", "打开任务详情"),
                attrs: { "data-empty-jump": "section-cockpit" },
              },
            ],
          },
        });
  } catch (error) {
    if (previousWatch) {
      previousWatch.enabled = isEnabled;
    }
    if (previousDetail) {
      state.watchDetails[identifier] = previousDetail;
    }
    renderWatches();
    renderWatchDetail();
    reportError(error, `${isEnabled ? "Disable" : "Enable"} mission`);
  } finally {
    button.disabled = false;
  }
}

function bindWatchToggleButtons(root) {
  if (!root) {
    return;
  }
  root.querySelectorAll("[data-watch-toggle]").forEach((button) => {
    button.addEventListener("click", async () => {
      await handleWatchToggle(button);
    });
  });
}

function wireLifecycleGuideActions(root) {
  if (!root) {
    return;
  }
  root.querySelectorAll("[data-empty-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      const requestedMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode || "");
      if (requestedMode) {
        applyStoryWorkspaceMode(requestedMode, { persist: true, syncUrl: true });
      }
      const section = String(button.dataset.emptyJump || "").trim();
      if (section) {
        jumpToSection(section);
      }
    });
  });
  root.querySelectorAll("[data-empty-focus]").forEach((button) => {
    button.addEventListener("click", () => {
      const focus = String(button.dataset.emptyFocus || "").trim();
      const field = String(button.dataset.emptyField || "").trim();
      if (focus === "mission") {
        focusCreateWatchDeck(field || "name");
      } else if (focus === "story") {
        focusStoryDeck(field || "title");
      } else if (focus === "route") {
        focusRouteDeck(field || "name");
      }
    });
  });
  root.querySelectorAll("[data-empty-reset]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = String(button.dataset.emptyReset || "").trim();
      if (target === "mission") {
        const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
        state.createWatchAdvancedOpen = null;
        setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
        focusCreateWatchDeck("name");
        showToast(
          wasEditing
            ? copy("Mission edit cancelled", "已取消任务编辑")
            : copy("Mission deck draft cleared", "已清空任务草稿"),
          "success",
        );
      } else if (target === "route") {
        const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
        state.routeAdvancedOpen = null;
        setRouteDraft(defaultRouteDraft(), "");
        focusRouteDeck("name");
        showToast(
          wasEditing
            ? copy("Route edit cancelled", "已取消路由编辑")
            : copy("Route deck draft cleared", "已清空路由草稿"),
          "success",
        );
      }
    });
  });
  root.querySelectorAll("[data-empty-watch]").forEach((button) => {
    button.addEventListener("click", async () => {
      const identifier = String(button.dataset.emptyWatch || "").trim();
      if (!identifier) {
        return;
      }
      button.disabled = true;
      try {
        await loadWatch(identifier);
      } catch (error) {
        reportError(error, copy("Open mission", "打开任务"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelectorAll("[data-empty-run-watch]").forEach((button) => {
    button.addEventListener("click", async () => {
      const identifier = String(button.dataset.emptyRunWatch || "").trim();
      if (!identifier) {
        return;
      }
      button.disabled = true;
      try {
        await triggerWatchRun(identifier);
      } catch (error) {
        reportError(error, copy("Run mission", "执行任务"));
      } finally {
        button.disabled = false;
      }
    });
  });
  bindWatchToggleButtons(root);
}

function getGovernanceSignals() {
  const scorecard = state.ops?.governance_scorecard;
  return scorecard && typeof scorecard.signals === "object" ? scorecard.signals : {};
}

function getGovernanceSignal(signalId) {
  const signal = getGovernanceSignals()[signalId];
  return signal && typeof signal === "object" ? signal : {};
}

function getAiSurfacePrecheck(surfaceId) {
  const payload = state.aiSurfacePrechecks?.[surfaceId];
  return payload && typeof payload === "object" ? payload : {};
}

function getAiSurfaceProjection(surfaceId) {
  const payload = state.aiSurfaceProjections?.[surfaceId];
  return payload && typeof payload === "object" ? payload : null;
}

function summarizeAiSurfaceProjection(surfaceId, projection) {
  if (!projection || typeof projection !== "object") {
    return copy("No selected subject is loaded for this surface yet.", "这个 surface 还没有加载选中的对象。");
  }
  const runtime = projection.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {};
  const output = projection.output && typeof projection.output === "object" ? projection.output : null;
  const payload = output && output.payload && typeof output.payload === "object" ? output.payload : {};
  if (surfaceId === "mission_suggest" && payload.summary) {
    return String(payload.summary);
  }
  if (surfaceId === "triage_assist") {
    const candidateCount = payload.candidate_count ?? payload.returned_count;
    if (candidateCount !== undefined) {
      return state.language === "zh"
        ? `重复解释候选数：${candidateCount}。`
        : `Duplicate explain candidates: ${candidateCount}.`;
    }
  }
  if (surfaceId === "claim_draft") {
    if (payload.summary) {
      return String(payload.summary);
    }
    const claimCount = Array.isArray(payload.claim_cards) ? payload.claim_cards.length : 0;
    return state.language === "zh"
      ? `待审核主张卡：${claimCount} 条。`
      : `Claim cards ready for review: ${claimCount}.`;
  }
  if (runtime.status) {
    return state.language === "zh"
      ? `运行状态：${localizeWord(runtime.status)}。`
      : `Runtime status: ${runtime.status}.`;
  }
  return copy("Governed projection loaded.", "治理投影已加载。");
}

function getStoryEvidenceIds(story) {
  return uniqueValues([
    story?.primary_item_id,
    ...(Array.isArray(story?.primary_evidence) ? story.primary_evidence.map((row) => row.item_id) : []),
    ...(Array.isArray(story?.secondary_evidence) ? story.secondary_evidence.map((row) => row.item_id) : []),
  ]);
}

function getStoriesForEvidenceItem(itemId) {
  const normalizedId = String(itemId || "").trim();
  if (!normalizedId) {
    return [];
  }
  return state.stories.filter((story) => getStoryEvidenceIds(story).includes(normalizedId));
}

function getStoryDeliveryStatus(story) {
  const governance = story && typeof story.governance === "object" ? story.governance : {};
  const deliveryRisk = governance && typeof governance.delivery_risk === "object" ? governance.delivery_risk : {};
  const rawStatus = String(deliveryRisk.status || "").trim().toLowerCase();
  if (rawStatus === "ready") {
    return { key: "ready", label: copy("Ready", "已就绪"), tone: "ok" };
  }
  if (rawStatus === "blocked") {
    return { key: "blocked", label: copy("Blocked", "已阻塞"), tone: "hot" };
  }
  if (rawStatus) {
    return { key: rawStatus, label: localizeWord(rawStatus), tone: rawStatus === "watch" ? "hot" : "" };
  }
  return { key: "pending", label: copy("Not assessed", "未评估"), tone: "" };
}

function signalToneFromStatus(status = "") {
  const normalized = String(status || "").trim().toLowerCase();
  if (["ok", "ready", "healthy", "clear", "completed", "delivered"].includes(normalized)) {
    return "ok";
  }
  if (["watch", "warning", "blocked", "error", "fail", "failed", "degraded", "no_result"].includes(normalized)) {
    return "hot";
  }
  return "";
}

function traceStageStatusLabel(status = "") {
  const normalized = String(status || "").trim().toLowerCase() || "pending";
  const labels = {
    ready: copy("ready", "已就绪"),
    ok: copy("ok", "正常"),
    watch: copy("watch", "关注"),
    warning: copy("warning", "警告"),
    blocked: copy("blocked", "阻塞"),
    no_result: copy("no result", "无结果"),
    pending: copy("pending", "待推进"),
    delivered: copy("delivered", "已送达"),
  };
  return labels[normalized] || localizeWord(normalized);
}

function buildStageLinkedTrace() {
  const watch = getSelectedWatchForContext() || state.watches[0] || null;
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  const recentRuns = Array.isArray(watch?.runs) ? watch.runs : [];
  const latestRun = recentRuns[0] || null;
  const recentAlerts = Array.isArray(watch?.recent_alerts) ? watch.recent_alerts : [];
  const resultStats = watch?.result_stats || {};
  const storedResults = Number(resultStats.stored_result_count || resultStats.returned_result_count || 0);
  const selectedTriage = state.triage.find((item) => String(item.id || "").trim() === String(state.selectedTriageId || "").trim()) || null;
  const selectedStory = getStoryRecord(state.selectedStoryId);
  const selectedReport = getSelectedReportRecord();
  const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
  const routeSummary = state.ops?.route_summary || {};
  const routeTimeline = Array.isArray(state.ops?.route_timeline) ? state.ops.route_timeline : [];
  const storySignal = getGovernanceSignal("story_conversion");
  const triageSignal = getGovernanceSignal("triage_throughput");
  const readyStories = Number(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0);
  const openQueue = Number(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0);
  const contradictionCount = Array.isArray(selectedStory?.contradictions) ? selectedStory.contradictions.length : 0;
  const selectedStoryEvidenceCount = Number(selectedStory?.item_count || 0);

  const startStage = watch
    ? {
        id: "start",
        status: "ready",
        title: String(watch.name || watch.id || copy("Mission anchor", "任务锚点")),
        summary: copy(
          "The current trace is anchored to the selected mission and its latest workflow trigger.",
          "当前 trace 以选中的任务及其最近一次流程触发为锚点。"
        ),
        facts: [
          { label: copy("Subject", "主体"), value: String(watch.id || watch.name || "") },
          { label: copy("Trigger", "触发方式"), value: localizeWord(latestRun?.trigger || watch.schedule_label || watch.schedule || "manual") },
          { label: copy("Started", "开始时间"), value: formatCompactDateTime(latestRun?.started_at || watch.last_run_at || "") },
        ],
      }
    : {
        id: "start",
        status: draft.name.trim() && draft.query.trim() ? "ready" : "blocked",
        title: draft.name.trim() || copy("Mission draft", "任务草稿"),
        summary: draft.name.trim() && draft.query.trim()
          ? copy(
              "The mission draft already names the subject and query that will seed the workflow.",
              "这份任务草稿已经具备会启动流程的主体名称和查询词。"
            )
          : copy(
              "The lifecycle has not started yet because the mission draft is still missing required input.",
              "这条生命周期尚未启动，因为任务草稿仍缺少必填输入。"
            ),
        facts: [
          { label: copy("Name", "名称"), value: draft.name || copy("unset", "未设置") },
          { label: copy("Query", "查询词"), value: clampLabel(draft.query || copy("unset", "未设置"), 28) },
          { label: copy("Route", "路由"), value: draft.route || copy("not attached", "未绑定") },
        ],
      };

  let monitorStage = null;
  if (latestRun && String(latestRun.status || "").trim().toLowerCase() === "error") {
    monitorStage = {
      id: "monitor",
      status: "blocked",
      title: copy("Run failed before output stabilized", "执行在输出稳定前失败"),
      summary: latestRun.error || copy("The latest run failed and still needs operator retry guidance.", "最近一次执行失败，仍需要操作者根据重试建议处理。"),
      facts: [
        { label: copy("Run", "执行"), value: String(latestRun.id || "-") },
        { label: copy("Status", "状态"), value: localizeWord(latestRun.status || "error") },
        { label: copy("Results", "结果"), value: String(latestRun.item_count || 0) },
      ],
    };
  } else if (watch && (latestRun || watch.last_run_at) && (storedResults > 0 || Number(latestRun?.item_count || 0) > 0)) {
    monitorStage = {
      id: "monitor",
      status: "ready",
      title: copy("Run output is inspectable", "执行输出已可检查"),
      summary: copy(
        "Monitoring now exposes a concrete run outcome and stored result count without forcing operators into raw logs.",
        "监测阶段现在直接暴露明确的执行结果和存储结果数，不需要操作者回到原始日志里重建上下文。"
      ),
      facts: [
        { label: copy("Outcome", "结果"), value: localizeWord(latestRun?.status || watch.last_run_status || "success") },
        { label: copy("Stored results", "已存储结果"), value: String(storedResults || latestRun?.item_count || 0) },
        { label: copy("Finished", "结束时间"), value: formatCompactDateTime(latestRun?.finished_at || watch.last_run_at || "") },
      ],
    };
  } else if (watch && (latestRun || watch.last_run_at)) {
    monitorStage = {
      id: "monitor",
      status: "no_result",
      title: copy("Mission completed with no results", "任务执行完成但没有结果"),
      summary: copy(
        "The latest run finished, but it did not leave behind any stored result for review.",
        "最近一次执行已经结束，但没有留下可供审阅的存储结果。"
      ),
      facts: [
        { label: copy("Outcome", "结果"), value: localizeWord(latestRun?.status || watch.last_run_status || "success") },
        { label: copy("Stored results", "已存储结果"), value: "0" },
        { label: copy("Finished", "结束时间"), value: formatCompactDateTime(latestRun?.finished_at || watch.last_run_at || "") },
      ],
    };
  } else if (watch) {
    monitorStage = {
      id: "monitor",
      status: watch.enabled ? "pending" : "blocked",
      title: watch.enabled
        ? copy("Mission has not run yet", "任务尚未开始执行")
        : copy("Mission is paused before monitoring", "任务在监测前已暂停"),
      summary: watch.enabled
        ? copy("One run is still required before output, review, or delivery facts can appear.", "还需要先执行一次，输出、审阅和交付事实才会开始出现。")
        : copy("Enable the mission first so monitoring facts can start moving again.", "请先启用任务，再让监测事实重新流动起来。"),
      facts: [
        { label: copy("Mission", "任务"), value: String(watch.name || watch.id || "") },
        { label: copy("Status", "状态"), value: watch.enabled ? copy("ready to run", "待执行") : copy("paused", "已暂停") },
        { label: copy("Schedule", "频率"), value: String(watch.schedule_label || watch.schedule || "manual") },
      ],
    };
  } else {
    monitorStage = {
      id: "monitor",
      status: "pending",
      title: copy("Monitoring starts after mission creation", "创建任务后才会进入监测"),
      summary: copy("Create or select one mission before run output can be traced.", "先创建或选中一条任务，执行输出才有可追踪的起点。"),
      facts: [
        { label: copy("Mission", "任务"), value: copy("not selected", "未选择") },
        { label: copy("Stored results", "已存储结果"), value: "0" },
        { label: copy("Run state", "执行状态"), value: copy("not started", "未开始") },
      ],
    };
  }

  let reviewStage = null;
  if (selectedQuality) {
    const qualityStatus = String(selectedQuality.status || "draft").trim().toLowerCase();
    reviewStage = {
      id: "review",
      status: selectedQuality.can_export ? "ready" : (qualityStatus === "review_required" ? "watch" : qualityStatus || "blocked"),
      title: selectedReport?.title || copy("Report quality guardrails", "报告质量门禁"),
      summary: selectedQuality.can_export
        ? copy("Review has already produced an export-ready report quality snapshot.", "审阅阶段已经产出可导出的报告质量快照。")
        : copy("Review is still holding on report guardrails before this output should be treated as ready.", "在把当前输出视为就绪之前，审阅阶段仍然被报告质量门禁卡住。"),
      facts: [
        { label: copy("Quality", "质量"), value: localizeWord(selectedQuality.status || "draft") },
        { label: copy("Score", "分数"), value: Number(selectedQuality.score || 0).toFixed(2) },
        { label: copy("Action", "动作"), value: formatReportOperatorAction(selectedQuality.operator_action || "") },
      ],
    };
  } else if (selectedStory) {
    const deliveryStatus = getStoryDeliveryStatus(selectedStory);
    reviewStage = {
      id: "review",
      status: contradictionCount ? "blocked" : (selectedStoryEvidenceCount ? "ready" : "watch"),
      title: String(selectedStory.title || selectedStory.id || copy("Story review", "故事审阅")),
      summary: contradictionCount
        ? copy("Review already promoted signal into a story, but contradiction markers still need resolution.", "审阅阶段已经把信号提升成故事，但冲突标记仍然需要先处理。")
        : copy("Review has already linked evidence to a persisted story object.", "审阅阶段已经把证据连接到持久化故事对象。"),
      facts: [
        { label: copy("Story", "故事"), value: localizeWord(selectedStory.status || "active") },
        { label: copy("Evidence", "证据"), value: String(selectedStoryEvidenceCount) },
        { label: copy("Contradictions", "冲突"), value: String(contradictionCount) },
      ],
    };
  } else if (selectedTriage) {
    const linkedStories = getStoriesForEvidenceItem(selectedTriage.id);
    reviewStage = {
      id: "review",
      status: linkedStories.length || String(selectedTriage.review_state || "").trim().toLowerCase() === "verified" ? "ready" : "watch",
      title: String(selectedTriage.title || selectedTriage.id || copy("Selected evidence", "当前证据")),
      summary: linkedStories.length
        ? copy("Review has already linked the selected evidence to downstream story work.", "审阅阶段已经把当前证据连接到下游故事工作。")
        : copy("The selected evidence is in review, but it still needs a verify-or-promote decision.", "当前证据已经进入审阅，但仍需要一个核验或提升决定。"),
      facts: [
        { label: copy("Disposition", "处置"), value: localizeWord(selectedTriage.review_state || "new") },
        { label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) },
        { label: copy("Open queue", "开放队列"), value: String(openQueue) },
      ],
    };
  } else {
    reviewStage = {
      id: "review",
      status: openQueue > 0 || readyStories > 0 ? "watch" : "pending",
      title: copy("Review lane status", "审阅阶段状态"),
      summary: openQueue > 0
        ? copy("Review still owns open queue pressure before the flow can move cleanly toward delivery.", "在流程顺畅进入交付之前，审阅阶段仍然背着开放队列压力。")
        : copy("No active review object is selected right now, but the review lane remains the next promotion owner.", "当前没有选中激活中的审阅对象，但审阅阶段仍然是下一个负责提升的所有者。"),
      facts: [
        { label: copy("Open queue", "开放队列"), value: String(openQueue) },
        { label: copy("Acted on", "已处理"), value: String(state.overview?.triage_acted_on_count ?? triageSignal.acted_on_items ?? 0) },
        { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
      ],
    };
  }

  let deliverStage = null;
  if ((routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0) {
    deliverStage = {
      id: "deliver",
      status: "blocked",
      title: copy("Delivery stopped on route health", "交付因路由健康问题停止"),
      summary: copy("Route health is currently the explicit stop reason before this flow can be trusted downstream again.", "路由健康当前是这条流程无法继续被下游信任的明确停止原因。"),
      facts: [
        { label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) },
        { label: copy("Missing", "缺失"), value: String(routeSummary.missing || 0) },
        { label: copy("Routes", "路由"), value: String(routeSummary.total || state.routes.length || 0) },
      ],
    };
  } else if (routeTimeline.length || recentAlerts.length || state.deliveryDispatchRecords.length) {
    const latestRouteEvent = routeTimeline[0] || null;
    const latestAlert = recentAlerts[0] || null;
    deliverStage = {
      id: "deliver",
      status: latestRouteEvent && String(latestRouteEvent.status || "").trim().toLowerCase() === "failed" ? "blocked" : "delivered",
      title: String(latestRouteEvent?.route || latestAlert?.rule_name || copy("Delivery outcome recorded", "已记录交付结果")),
      summary: String(
        latestRouteEvent?.summary
        || latestRouteEvent?.error
        || latestAlert?.summary
        || copy("A route-backed delivery outcome is already recorded for the current flow.", "当前流程已经记录了带路由的交付结果。")
      ),
      facts: [
        { label: copy("Route", "路由"), value: String(latestRouteEvent?.route || "-") },
        { label: copy("Outcome", "结果"), value: localizeWord(latestRouteEvent?.status || "delivered") },
        { label: copy("Last event", "最近事件"), value: formatCompactDateTime(latestRouteEvent?.created_at || latestAlert?.created_at || "") },
      ],
    };
  } else if (readyStories > 0 && state.routes.length) {
    deliverStage = {
      id: "deliver",
      status: "watch",
      title: copy("Ready output is waiting for dispatch", "就绪输出正在等待分发"),
      summary: copy("Review has already produced ready output, but there is still no recorded delivery outcome for it.", "审阅阶段已经产出就绪输出，但当前还没有对应的交付结果记录。"),
      facts: [
        { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
        { label: copy("Routes", "路由"), value: String(state.routes.length || 0) },
        { label: copy("Dispatch records", "dispatch 记录"), value: String(state.deliveryDispatchRecords.length || 0) },
      ],
    };
  } else if (selectedStory || selectedTriage || openQueue > 0) {
    deliverStage = {
      id: "deliver",
      status: "blocked",
      title: copy("Flow stopped before delivery", "流程在交付前停止"),
      summary: readyStories > 0
        ? copy("A delivery target still needs an explicit dispatch outcome.", "当前仍需要一个明确的 dispatch 结果，才能完成交付。")
        : copy("The flow has not produced a delivery-ready object yet, so the stop reason still lives upstream in review.", "当前流程还没有产出可交付对象，所以停止原因仍然位于上游审阅阶段。"),
      facts: [
        { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
        { label: copy("Open queue", "开放队列"), value: String(openQueue) },
        { label: copy("Routes", "路由"), value: String(state.routes.length || 0) },
      ],
    };
  } else {
    deliverStage = {
      id: "deliver",
      status: "pending",
      title: copy("Delivery path is not active yet", "交付路径尚未激活"),
      summary: copy("Create a route or produce review-ready output before the delivery stage can record an outcome.", "先创建路由或产出可交付的审阅结果，交付阶段才会开始记录结果。"),
      facts: [
        { label: copy("Routes", "路由"), value: String(state.routes.length || 0) },
        { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
        { label: copy("Dispatch records", "dispatch 记录"), value: String(state.deliveryDispatchRecords.length || 0) },
      ],
    };
  }

  return {
    title: copy("Stage-Linked Output Trace", "阶段联动输出 Trace"),
    summary: copy(
      "Follow one visible path from mission start through monitor, review, and route-backed delivery without reconstructing the story from logs.",
      "沿着一条可见路径，从任务启动一路看到监测、审阅和带路由的交付结果，而不必回到日志里重建流程。"
    ),
    stages: [startStage, monitorStage, reviewStage, deliverStage],
  };
}

function renderStageLinkedTraceCard(trace = buildStageLinkedTrace()) {
  const stages = Array.isArray(trace?.stages) ? trace.stages : [];
  return `
    <div class="card workflow-trace-card" data-stage-trace="workflow">
      <div class="card-top">
        <div>
          <div class="mono">${copy("output trace", "输出追踪")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(trace?.title || copy("Stage-Linked Output Trace", "阶段联动输出 Trace"))}</h3>
        </div>
        <span class="chip ok">${copy("Start -> Monitor -> Review -> Deliver", "Start -> Monitor -> Review -> Deliver")}</span>
      </div>
      <div class="panel-sub">${escapeHtml(trace?.summary || "")}</div>
      <div class="trace-stage-grid">
        ${stages.map((stage) => {
          const tone = signalToneFromStatus(stage?.status || "");
          return `
            <div class="trace-stage ${tone}" data-trace-stage="${escapeHtml(stage?.id || "")}" data-trace-status="${escapeHtml(String(stage?.status || ""))}">
              <div class="trace-stage-head">
                <div class="trace-stage-kicker">${escapeHtml(localizeWord(stage?.id || ""))}</div>
                <span class="chip ${tone}">${escapeHtml(traceStageStatusLabel(stage?.status || ""))}</span>
              </div>
              <div class="trace-stage-title">${escapeHtml(stage?.title || "")}</div>
              <div class="trace-stage-copy">${escapeHtml(stage?.summary || "")}</div>
              ${renderSectionSummaryFacts(stage?.facts || [])}
            </div>
          `;
        }).join("")}
      </div>
    </div>
  `;
}

function buildSharedSignalTaxonomy() {
  const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
  const selectedStory = getStoryRecord(state.selectedStoryId);
  const selectedReport = getSelectedReportRecord();
  const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
  const routeSummary = state.ops?.route_summary || {};
  const routeTimeline = Array.isArray(state.ops?.route_timeline) ? state.ops.route_timeline : [];
  const overflowEvidence = state.consoleOverflowEvidence || defaultConsoleOverflowEvidence();
  const aiPrechecks = Object.values(state.aiSurfacePrechecks || {}).filter((value) => value && typeof value === "object");
  const aiTrustRisk = aiPrechecks.find((precheck) => {
    const normalized = String(precheck.mode_status || "").trim().toLowerCase();
    return ["rejected", "invalid"].includes(normalized);
  }) || aiPrechecks.find((precheck) => {
    const normalized = String(precheck.mode_status || "").trim().toLowerCase();
    return ["admitted", "fallback_used"].includes(normalized);
  }) || null;
  const contradictionCount = Array.isArray(selectedStory?.contradictions) ? selectedStory.contradictions.length : 0;
  const readyStories = Number(state.overview?.story_ready_count ?? getGovernanceSignal("story_conversion").ready_story_count ?? 0);
  const qualitySignal = selectedQuality
    ? {
        id: "quality",
        classLabel: copy("Quality", "质量"),
        status: selectedQuality.can_export ? "ready" : String(selectedQuality.status || "blocked").trim().toLowerCase(),
        title: selectedQuality.can_export ? copy("Report guardrails are green", "报告门禁已通过") : copy("Report guardrails still need review", "报告门禁仍待处理"),
        summary: selectedQuality.can_export
          ? copy("Review quality is owned by the report guardrails surface and currently allows export.", "审阅质量由报告门禁 surface 持有，当前已经允许导出。")
          : copy("Quality remains owned by the report guardrails surface until the blocking checks are resolved.", "在阻断检查被解决之前，质量说明仍由报告门禁 surface 持有。"),
        owner: copy("Report quality guardrails", "报告质量门禁"),
        meaning: copy("Review readiness, contradiction handling, and export guardrail state.", "审阅就绪度、冲突处理和导出门禁状态。"),
        facts: [
          { label: copy("Report", "报告"), value: String(selectedReport?.title || selectedReport?.id || "") },
          { label: copy("Status", "状态"), value: localizeWord(selectedQuality.status || "draft") },
          { label: copy("Score", "分数"), value: Number(selectedQuality.score || 0).toFixed(2) },
        ],
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
        },
      }
    : selectedStory
      ? {
          id: "quality",
          classLabel: copy("Quality", "质量"),
          status: contradictionCount ? "blocked" : (Number(selectedStory.item_count || 0) > 0 ? "ready" : "watch"),
          title: contradictionCount ? copy("Story contradictions still own quality risk", "故事冲突仍然决定质量风险") : copy("Story evidence is currently grounded", "故事证据当前已经成形"),
          summary: contradictionCount
            ? copy("Quality is owned by story contradiction markers until the narrative is no longer mixed.", "在叙事不再混杂之前，质量解释由故事冲突标记持有。")
            : copy("Quality is owned by the story evidence surface because the narrative is already attached to reviewed signal.", "质量解释由故事证据 surface 持有，因为当前叙事已经绑定到已审阅信号。"),
          owner: contradictionCount ? copy("Story contradiction markers", "故事冲突标记") : copy("Story evidence context", "故事证据上下文"),
          meaning: copy("Review readiness, contradiction handling, and narrative grounding.", "审阅就绪度、冲突处理和叙事锚定情况。"),
          facts: [
            { label: copy("Story", "故事"), value: localizeWord(selectedStory.status || "active") },
            { label: copy("Evidence", "证据"), value: String(selectedStory.item_count || 0) },
            { label: copy("Contradictions", "冲突"), value: String(contradictionCount) },
          ],
          actionHierarchy: {
            primary: {
              label: copy("Open Story Workspace", "打开故事工作台"),
              attrs: { "data-empty-jump": "section-story" },
            },
          },
        }
      : {
          id: "quality",
          classLabel: copy("Quality", "质量"),
          status: Number(state.overview?.triage_open_count || 0) > 0 ? "watch" : "pending",
          title: copy("Review lane still owns the next quality decision", "审阅阶段仍然持有下一个质量决策"),
          summary: copy("Without a selected story or report, quality stays owned by the active review lane and its promotion decisions.", "在没有选中故事或报告时，质量解释仍由当前审阅工作线及其提升决策持有。"),
          owner: copy("Triage and promotion surfaces", "分诊与提升 surface"),
          meaning: copy("Review readiness, contradiction handling, and export guardrail state.", "审阅就绪度、冲突处理和导出门禁状态。"),
          facts: [
            { label: copy("Open queue", "开放队列"), value: String(state.overview?.triage_open_count || 0) },
            { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
            { label: copy("Reports", "报告"), value: String(state.reports.length || 0) },
          ],
          actionHierarchy: {
            primary: {
              label: copy("Open Review Lane", "打开审阅工作线"),
              attrs: { "data-empty-jump": "section-triage" },
            },
          },
        };

  const deliverySignal = {
    id: "delivery",
    classLabel: copy("Delivery", "交付"),
    status: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
      ? "blocked"
      : (routeTimeline.length || state.deliveryDispatchRecords.length || readyStories > 0 ? "ready" : "watch"),
    title: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
      ? copy("Route health is blocking delivery", "路由健康正在阻塞交付")
      : (routeTimeline.length || state.deliveryDispatchRecords.length)
        ? copy("Route-backed delivery is visible", "带路由的交付结果已经可见")
        : copy("Delivery lane is waiting for a route-backed outcome", "交付工作线正在等待带路由的结果"),
    summary: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
      ? copy("Delivery is owned by route health remediation until degraded or missing routes are cleared.", "在降级或缺失的路由被清理前，交付解释由路由健康修复 surface 持有。")
      : copy("Delivery is owned by route health, package audit, and dispatch history inside the delivery lane.", "交付解释由交付工作线里的路由健康、输出包审计和 dispatch 历史持有。"),
    owner: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
      ? copy("Route health remediation", "路由健康修复")
      : copy("Delivery workspace and dispatch record", "交付工作台与 dispatch 记录"),
    meaning: copy("Route health, package readiness, dispatch outcome, and downstream delivery quality.", "路由健康、输出包就绪度、dispatch 结果和下游交付质量。"),
    facts: [
      { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
      { label: copy("Degraded routes", "降级路由"), value: String(routeSummary.degraded || 0) },
      { label: copy("Last route", "最近路由"), value: String(routeTimeline[0]?.route || "-") },
    ],
    actionHierarchy: {
      primary: {
        label: copy("Open Delivery Lane", "打开交付工作线"),
        attrs: { "data-empty-jump": "section-ops" },
      },
    },
  };

  const overflowSignal = {
    id: "overflow",
    classLabel: copy("Overflow", "溢出"),
    status: Number(overflowEvidence.residual_surface_count || 0) > 0
      ? "watch"
      : (Number(overflowEvidence.surface_count || 0) > 0 ? "ready" : "pending"),
    title: Number(overflowEvidence.residual_surface_count || 0) > 0
      ? copy("Residual text overflow hotspots remain", "仍然存在残余文本溢出热点")
      : copy("Console overflow evidence is within baseline", "控制台溢出证据处于基线内"),
    summary: Number(overflowEvidence.residual_surface_count || 0) > 0
      ? copy("Overflow is owned by the console overflow evidence card until the surviving hotspots are understood.", "在残余热点被理解之前，溢出解释由 console overflow evidence 卡片持有。")
      : copy("Overflow remains owned by the evidence card even when there is no current operator action.", "即使当前没有操作动作，溢出解释仍由 evidence 卡片持有。"),
    owner: copy("console-overflow-evidence-card", "console-overflow-evidence-card"),
    meaning: copy("Residual console text overflow pressure after the current fit and truncation baseline.", "当前 fit 与截断基线之后仍残留的控制台文本溢出压力。"),
    facts: [
      { label: copy("Survivors", "残余样本"), value: String(overflowEvidence.survivor_count || 0) },
      { label: copy("Hotspots", "热点"), value: String(overflowEvidence.residual_surface_count || 0) },
      { label: copy("Sampled", "采样"), value: overflowEvidence.updated_at ? formatCompactDateTime(overflowEvidence.updated_at) : copy("not yet", "尚未") },
    ],
    actionHierarchy: Number(overflowEvidence.residual_surface_count || 0) > 0
      ? {
          primary: {
            label: copy("Inspect Overflow Evidence", "查看溢出证据"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        }
      : null,
    noActionOutcome: copy("No operator action: keep the overflow evidence visible as a residual hotspot baseline.", "无需操作：把溢出证据继续保留为残余热点基线。"),
  };

  const trustSignal = selectedWatch && (selectedWatch.retry_advice || selectedWatch.last_failure)
    ? {
        id: "trust",
        classLabel: copy("Trust", "可信度"),
        status: "watch",
        title: copy("Mission trust is currently owned by retry guidance", "当前任务可信度由重试建议持有"),
        summary: copy("The nearest trust explainer is still the mission retry guidance because the latest failure remains visible.", "当前最近的可信度解释器仍然是任务重试建议，因为最近失败事实依然可见。"),
        owner: copy("Retry guidance", "重试建议"),
        meaning: copy("Whether the current mission, route, or assisted surface is trustworthy enough to continue.", "当前任务、路由或辅助 surface 是否足够可信，可以继续推进。"),
        facts: [
          { label: copy("Mission", "任务"), value: String(selectedWatch.name || selectedWatch.id || "") },
          { label: copy("Retry", "重试"), value: String(selectedWatch.retry_advice?.retry_command || "-") },
          { label: copy("Last failure", "最近失败"), value: String(selectedWatch.last_failure?.error || selectedWatch.retry_advice?.failure_class || "-") },
        ],
        actionHierarchy: {
          primary: {
            label: copy("Open Cockpit Guidance", "打开任务详情指引"),
            attrs: { "data-empty-jump": "section-cockpit" },
          },
        },
      }
    : aiTrustRisk
      ? {
          id: "trust",
          classLabel: copy("Trust", "可信度"),
          status: String(aiTrustRisk.mode_status || "watch").trim().toLowerCase() || "watch",
          title: copy("Governed assist trust needs a surface check", "治理辅助可信度需要 surface 检查"),
          summary: copy("The nearest trust explainer is currently an AI surface precheck or runtime fact guard.", "当前最近的可信度解释器是 AI surface 的预检或运行事实门禁。"),
          owner: copy("AI surface precheck", "AI surface 预检"),
          meaning: copy("Whether the current mission, route, or assisted surface is trustworthy enough to continue.", "当前任务、路由或辅助 surface 是否足够可信，可以继续推进。"),
          facts: [
            { label: copy("Surface", "surface"), value: String(aiTrustRisk.alias || aiTrustRisk.contract_id || "-") },
            { label: copy("Mode status", "模式状态"), value: localizeWord(aiTrustRisk.mode_status || "pending") },
            { label: copy("Fallback", "回退"), value: localizeWord(aiTrustRisk.manual_fallback || "-") },
          ],
          actionHierarchy: {
            primary: {
              label: copy("Open Delivery Lane", "打开交付工作线"),
              attrs: { "data-empty-jump": "section-ops" },
            },
          },
        }
      : {
          id: "trust",
          classLabel: copy("Trust", "可信度"),
          status: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0 ? "watch" : "ready",
          title: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
            ? copy("Route trust still needs remediation", "路由可信度仍需修复")
            : copy("Trust posture is currently stable", "当前可信度姿态稳定"),
          summary: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
            ? copy("Trust is currently owned by route health remediation because delivery posture is degraded.", "由于交付姿态降级，当前可信度解释由路由健康修复 surface 持有。")
            : copy("No nearer trust explainer is currently raising risk, so operators can continue with the active workflow.", "当前没有更近的可信度解释器在持续抬高风险，所以操作者可以继续当前工作流。"),
          owner: copy("Route health remediation", "路由健康修复"),
          meaning: copy("Whether the current mission, route, or assisted surface is trustworthy enough to continue.", "当前任务、路由或辅助 surface 是否足够可信，可以继续推进。"),
          facts: [
            { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
            { label: copy("Degraded routes", "降级路由"), value: String(routeSummary.degraded || 0) },
            { label: copy("Missing routes", "缺失路由"), value: String(routeSummary.missing || 0) },
          ],
          actionHierarchy: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
            ? {
                primary: {
                  label: copy("Inspect Route Health", "查看路由健康"),
                  attrs: { "data-empty-jump": "section-ops" },
                },
              }
            : null,
          noActionOutcome: copy("No operator action: trust posture is currently clear enough to continue.", "无需操作：当前可信度姿态已足够清晰，可以继续推进。"),
        };

  return [qualitySignal, deliverySignal, overflowSignal, trustSignal];
}

function renderSharedSignalTaxonomyCard(signals = buildSharedSignalTaxonomy()) {
  const rows = Array.isArray(signals) ? signals : [];
  const activeSignal = rows.find((signal) => signal.id === state.sharedSignalFocus) || rows[0] || null;
  if (activeSignal && state.sharedSignalFocus !== activeSignal.id) {
    state.sharedSignalFocus = activeSignal.id;
  }
  return `
    <div class="card shared-signal-taxonomy-card" data-shared-signal-taxonomy="true">
      <div class="card-top">
        <div>
          <div class="mono">${copy("shared signal taxonomy", "共享信号 taxonomy")}</div>
          <h3 class="card-title" style="margin-top:10px;">${copy("Shared Signal Taxonomy", "共享信号分类")}</h3>
        </div>
        <span class="chip">${copy("owner-backed", "解释有归属")}</span>
      </div>
      <div class="panel-sub">${copy(
        "Every shared signal below names its owner, meaning, and next action instead of behaving like a decorative badge.",
        "下面每个共享信号都会明确说明 owner、含义和下一步，而不是只做装饰性 badge。"
      )}</div>
      <div class="shared-signal-row ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Shared signal classes", "共享信号分类切换"))}">
        ${rows.map((signal) => {
          const tone = signalToneFromStatus(signal?.status || "");
          const active = signal?.id === activeSignal?.id;
          return `
            <button
              class="ui-segment-button shared-signal-button ${tone} ${active ? "active" : ""}"
              type="button"
              data-shared-signal-button="${escapeHtml(signal?.id || "")}"
              aria-pressed="${active ? "true" : "false"}"
              aria-expanded="${String(active)}"
            >${escapeHtml(signal?.classLabel || signal?.id || "")} · ${escapeHtml(traceStageStatusLabel(signal?.status || ""))}</button>
          `;
        }).join("")}
      </div>
      ${activeSignal ? `
        <div class="shared-signal-detail ${signalToneFromStatus(activeSignal.status || "")}" data-shared-signal-panel="${escapeHtml(activeSignal.id || "")}">
          <div class="shared-signal-detail-head">
            <div>
              <div class="section-summary-kicker">${escapeHtml(activeSignal.classLabel || activeSignal.id || "")}</div>
              <div class="section-summary-title">${escapeHtml(activeSignal.title || "")}</div>
            </div>
            <span class="chip ${signalToneFromStatus(activeSignal.status || "")}">${escapeHtml(traceStageStatusLabel(activeSignal.status || ""))}</span>
          </div>
          <div class="section-summary-copy">${escapeHtml(activeSignal.summary || "")}</div>
          <div class="meta">
            <span data-shared-signal-owner>${copy("Owner", "归属")}: ${escapeHtml(activeSignal.owner || "-")}</span>
            <span>${copy("Meaning", "含义")}: ${escapeHtml(activeSignal.meaning || "-")}</span>
          </div>
          ${renderSectionSummaryFacts(activeSignal.facts || [])}
          ${activeSignal.actionHierarchy ? renderCardActionHierarchy(activeSignal.actionHierarchy) : `<div class="panel-sub" data-shared-signal-noop="true">${escapeHtml(activeSignal.noActionOutcome || copy("No operator action.", "当前无需操作。"))}</div>`}
        </div>
      ` : ""}
    </div>
  `;
}

function renderLifecycleContinuityCard({ title = "", summary = "", stages = [], actions = [], tone = "ok" } = {}) {
  const stagesHtml = stages.map((stage) => `
    <div class="continuity-stage ${escapeHtml(stage.tone || "")}">
      <div class="continuity-stage-kicker">${escapeHtml(stage.kicker || "")}</div>
      <div class="continuity-stage-title">${escapeHtml(stage.title || "")}</div>
      <div class="continuity-stage-copy">${escapeHtml(stage.copy || "")}</div>
      <div class="continuity-fact-list">
        ${(stage.facts || []).map((fact) => {
          const hasValue = ![null, undefined].includes(fact.value) && String(fact.value).trim() !== "";
          return `
            <div class="continuity-fact">
              <span>${escapeHtml(fact.label || "")}</span>
              <strong>${escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}</strong>
            </div>
          `;
        }).join("")}
      </div>
    </div>
  `).join("");
  const actionsHtml = actions.length
    ? `<div class="actions" style="margin-top:14px;">${actions.map((action) => `
        <button
          class="${action.primary ? "btn-primary" : "btn-secondary"}"
          type="button"
          ${action.section ? `data-empty-jump="${escapeHtml(action.section)}"` : ""}
          ${action.focus ? `data-empty-focus="${escapeHtml(action.focus)}"` : ""}
          ${action.field ? `data-empty-field="${escapeHtml(action.field)}"` : ""}
          ${action.watch ? `data-empty-watch="${escapeHtml(action.watch)}"` : ""}
          ${action.runWatch ? `data-empty-run-watch="${escapeHtml(action.runWatch)}"` : ""}
          ${action.toggleWatch ? `data-watch-toggle="${escapeHtml(action.toggleWatch)}"` : ""}
          ${action.watchEnabled ? `data-watch-enabled="${escapeHtml(action.watchEnabled)}"` : ""}
        >${escapeHtml(action.label || "")}</button>
      `).join("")}</div>`
    : "";
  return `
    <div class="card">
      <div class="card-top">
        <div>
          <div class="mono">${copy("lifecycle continuity", "生命周期衔接")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(title)}</h3>
        </div>
        <span class="chip ${tone}">${copy("cross-stage", "跨阶段")}</span>
      </div>
      <div class="panel-sub">${escapeHtml(summary)}</div>
      <div class="continuity-lane" style="margin-top:14px;">${stagesHtml}</div>
      ${actionsHtml}
    </div>
  `;
}

function sectionSummaryRootId(sectionId) {
  const map = {
    "section-intake": "intake-section-summary",
    "section-board": "board-section-summary",
    "section-cockpit": "cockpit-section-summary",
    "section-triage": "triage-section-summary",
    "section-story": "story-section-summary",
    "section-ops": "ops-section-summary",
  };
  return map[normalizeSectionId(sectionId)] || "";
}

function stageFeedbackIdForSection(sectionId) {
  const normalizedSectionId = normalizeSectionId(sectionId);
  const map = {
    "section-intake": "start",
    "section-board": "monitor",
    "section-cockpit": "monitor",
    "section-triage": "review",
    "section-story": "review",
    "section-claims": "review",
    "section-report-studio": "review",
    "section-ops": "deliver",
  };
  return map[normalizedSectionId] || normalizedSectionId;
}

function getStageFeedback(stageOrSectionId) {
  const stageId = stageFeedbackIdForSection(stageOrSectionId);
  return state.stageFeedback?.[stageId] || null;
}

function refreshStageFeedbackSurfaces(stageId) {
  const normalizedStageId = stageFeedbackIdForSection(stageId);
  if (normalizedStageId === "start") {
    renderCreateWatchDeck();
    return;
  }
  if (normalizedStageId === "monitor") {
    renderWatches();
    renderWatchDetail();
    return;
  }
  if (normalizedStageId === "review") {
    renderTriage();
    renderStories();
    return;
  }
  if (normalizedStageId === "deliver") {
    renderStatus();
  }
}

function setStageFeedback(stageOrSectionId, payload = null) {
  const stageId = stageFeedbackIdForSection(stageOrSectionId);
  if (!stageId || !state.stageFeedback) {
    return;
  }
  state.stageFeedback[stageId] = payload
    ? {
        stageId,
        kind: String(payload.kind || "info").trim().toLowerCase() || "info",
        title: String(payload.title || "").trim(),
        copy: String(payload.copy || "").trim(),
        tone: String(payload.tone || "").trim(),
        facts: Array.isArray(payload.facts) ? payload.facts : [],
        actionHierarchy: payload.actionHierarchy && typeof payload.actionHierarchy === "object"
          ? payload.actionHierarchy
          : null,
      }
    : null;
  refreshStageFeedbackSurfaces(stageId);
}

function stageFeedbackKindLabel(kind = "") {
  const labels = {
    completion: copy("completion", "完成状态"),
    warning: copy("warning", "警告"),
    blocked: copy("blocked", "阻塞状态"),
    no_result: copy("no result", "无结果"),
    info: copy("stage note", "阶段说明"),
  };
  return labels[String(kind || "").trim().toLowerCase()] || copy("stage note", "阶段说明");
}

function renderStageFeedbackCard(feedback = {}, sectionId = "") {
  if (!feedback || !(feedback.title || feedback.copy)) {
    return "";
  }
  const stageId = stageFeedbackIdForSection(feedback.stageId || sectionId);
  const kind = String(feedback.kind || "info").trim().toLowerCase() || "info";
  const tone = String(feedback.tone || "").trim()
    || (kind === "completion" ? "ok" : ["warning", "blocked"].includes(kind) ? "hot" : "");
  return `
    <div class="section-summary-feedback ${escapeHtml(tone)}" data-stage-feedback-stage="${escapeHtml(stageId)}" data-stage-feedback-kind="${escapeHtml(kind)}">
      <div class="section-summary-feedback-head">
        <div>
          <div class="section-summary-kicker">${escapeHtml(stageFeedbackKindLabel(kind))}</div>
          <div class="section-summary-title">${escapeHtml(feedback.title || copy("Stage feedback", "阶段反馈"))}</div>
        </div>
        <span class="chip ${escapeHtml(tone)}">${escapeHtml(stageFeedbackKindLabel(kind))}</span>
      </div>
      <div class="section-summary-feedback-copy">${escapeHtml(feedback.copy || "")}</div>
      ${renderSectionSummaryFacts(feedback.facts)}
      ${feedback.actionHierarchy ? renderCardActionHierarchy(feedback.actionHierarchy) : ""}
    </div>
  `;
}

function renderSectionSummaryFacts(facts = []) {
  const rows = Array.isArray(facts) ? facts.filter(Boolean) : [];
  if (!rows.length) {
    return "";
  }
  return `
    <div class="continuity-fact-list">
      ${rows.map((fact) => {
        const hasValue = ![null, undefined].includes(fact.value) && String(fact.value).trim() !== "";
        return `
          <div class="continuity-fact">
            <span>${escapeHtml(fact.label || "")}</span>
            <strong>${escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}</strong>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderSectionSummarySignal(kind, signal = {}) {
  const normalizedKind = String(kind || "").trim().toLowerCase();
  const kindLabels = {
    objective: copy("current objective", "当前目标"),
    success: copy("success signal", "成功信号"),
    blocker: copy("blocker or next prerequisite", "阻塞点或下一个前提"),
  };
  const hasExplicitTone = Object.prototype.hasOwnProperty.call(signal || {}, "tone");
  const tone = hasExplicitTone
    ? String(signal.tone || "").trim()
    : (normalizedKind === "success" ? "ok" : normalizedKind === "blocker" ? "hot" : "");
  return `
    <div class="section-summary-signal ${escapeHtml(tone)}" data-section-summary-kind="${escapeHtml(normalizedKind)}">
      <div class="section-summary-kicker">${escapeHtml(kindLabels[normalizedKind] || normalizedKind)}</div>
      <div class="section-summary-title">${escapeHtml(signal.title || copy("No signal yet", "当前没有信号"))}</div>
      <div class="section-summary-copy">${escapeHtml(signal.copy || "")}</div>
      ${renderSectionSummaryFacts(signal.facts)}
    </div>
  `;
}

function renderSectionSummaryFrame({ sectionId = "", title = "", summary = "", objective = {}, success = {}, blocker = {} } = {}) {
  const normalizedSectionId = normalizeSectionId(sectionId);
  const feedback = getStageFeedback(normalizedSectionId);
  return `
    <div class="card section-summary-card" data-section-summary="${escapeHtml(normalizedSectionId)}">
      <div class="card-top">
        <div>
          <div class="mono">${copy("section summary", "区块摘要")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(title || activeSectionLabel(normalizedSectionId))}</h3>
        </div>
        <span class="chip">${escapeHtml(activeSectionLabel(normalizedSectionId))}</span>
      </div>
      <div class="panel-sub">${escapeHtml(summary)}</div>
      ${feedback ? renderStageFeedbackCard(feedback, normalizedSectionId) : ""}
      <div class="section-summary-grid">
        ${renderSectionSummarySignal("objective", objective)}
        ${renderSectionSummarySignal("success", success)}
        ${renderSectionSummarySignal("blocker", blocker)}
      </div>
    </div>
  `;
}

function setSectionSummary(sectionId, payload = {}) {
  const rootId = sectionSummaryRootId(sectionId);
  const root = rootId ? $(rootId) : null;
  if (!root) {
    return;
  }
  root.innerHTML = renderSectionSummaryFrame({
    sectionId,
    ...payload,
  });
  wireLifecycleGuideActions(root);
  scheduleCanvasTextFit(root);
}

function operatorGuidanceLaneLabel(lane = "") {
  const labels = {
    mission: copy("mission lane", "任务工作线"),
    triage: copy("triage lane", "分诊工作线"),
    story: copy("story lane", "故事工作线"),
    route: copy("route lane", "路由工作线"),
  };
  return labels[String(lane || "").trim().toLowerCase()] || copy("operator guidance", "操作指引");
}

function operatorGuidanceColumnMeta(kind = "") {
  const normalizedKind = String(kind || "").trim().toLowerCase();
  const labels = {
    reasons: {
      title: copy("Action reasons", "动作原因"),
      subtitle: copy("What is driving the current guidance right now.", "当前这条指引背后的驱动事实。"),
    },
    next_steps: {
      title: copy("Next steps", "下一步"),
      subtitle: copy("What the operator should do next from this lane.", "操作者在这条工作线里的下一步动作。"),
    },
    sources: {
      title: copy("Explanation owners", "解释归属"),
      subtitle: copy("Which runtime or static source owns this copy.", "哪些运行时或静态来源拥有这部分解释。"),
    },
  };
  return labels[normalizedKind] || {
    title: copy("Guidance", "指引"),
    subtitle: copy("Shared operator wording for this lane.", "当前工作线的共享操作文案。"),
  };
}

function normalizeOperatorGuidanceItems(items = []) {
  return Array.isArray(items)
    ? items.filter((item) => item && (item.title || item.copy || (Array.isArray(item.facts) && item.facts.length)))
    : [];
}

function renderOperatorGuidanceItem(item = {}, kind = "") {
  const tone = String(item.tone || "").trim();
  const owner = item.owner
    ? `<span class="chip">${escapeHtml(item.owner)}</span>`
    : "";
  return `
    <div class="operator-guidance-item ${escapeHtml(tone)}" data-guidance-kind="${escapeHtml(kind)}" data-guidance-item="${escapeHtml(String(item.title || kind || "guidance").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-"))}">
      <div class="operator-guidance-item-head">
        <div class="operator-guidance-item-title">${escapeHtml(item.title || copy("Guidance item", "指引条目"))}</div>
        ${owner}
      </div>
      <div class="operator-guidance-item-copy">${escapeHtml(item.copy || "")}</div>
      ${renderSectionSummaryFacts(item.facts)}
    </div>
  `;
}

function renderOperatorGuidanceColumn(kind, items = []) {
  const rows = normalizeOperatorGuidanceItems(items);
  if (!rows.length) {
    return "";
  }
  const meta = operatorGuidanceColumnMeta(kind);
  return `
    <div class="operator-guidance-column" data-guidance-column="${escapeHtml(kind)}">
      <div class="operator-guidance-column-head">
        <div class="mono">${escapeHtml(meta.title)}</div>
        <div class="panel-sub">${escapeHtml(meta.subtitle)}</div>
      </div>
      <div class="operator-guidance-list">
        ${rows.map((item) => renderOperatorGuidanceItem(item, kind)).join("")}
      </div>
    </div>
  `;
}

function renderOperatorGuidanceSurface({
  surfaceId = "",
  lane = "",
  title = "",
  summary = "",
  reasons = [],
  nextSteps = [],
  sources = [],
  actionHierarchy = null,
} = {}) {
  const normalizedLane = String(lane || "").trim().toLowerCase() || "generic";
  return `
    <div
      class="card operator-guidance-surface"
      ${surfaceId ? `id="${escapeHtml(surfaceId)}"` : ""}
      data-operator-guidance-surface="${escapeHtml(normalizedLane)}"
    >
      <div class="card-top">
        <div>
          <div class="mono">${copy("operator guidance", "操作指引")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(title || operatorGuidanceLaneLabel(normalizedLane))}</h3>
        </div>
        <span class="chip">${escapeHtml(operatorGuidanceLaneLabel(normalizedLane))}</span>
      </div>
      <div class="panel-sub">${escapeHtml(summary)}</div>
      <div class="operator-guidance-grid">
        ${renderOperatorGuidanceColumn("reasons", reasons)}
        ${renderOperatorGuidanceColumn("next_steps", nextSteps)}
        ${renderOperatorGuidanceColumn("sources", sources)}
      </div>
      ${actionHierarchy ? renderCardActionHierarchy(actionHierarchy) : ""}
    </div>
  `;
}

function renderIntakeSectionSummary(preview = buildCreateWatchPreview(state.createWatchDraft || defaultCreateWatchDraft())) {
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  const routeName = normalizeRouteName(draft.route);
  const routeRecord = routeName ? getRouteRecordByName(routeName) : null;
  const hardBlocker = !draft.name.trim()
    ? {
        title: copy("Mission name is still missing", "任务名称仍未填写"),
        copy: copy("Add a short operator-facing name before the draft can create or update a mission.", "先补一个面向操作者的短名称，任务草稿才能创建或更新。"),
        facts: [
          { label: copy("Query", "查询词"), value: clampLabel(draft.query, 24) },
          { label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") },
        ],
      }
    : !draft.query.trim()
      ? {
          title: copy("Mission query is still missing", "任务查询词仍未填写"),
          copy: copy("Add the signal or topic to track before the draft can become a valid mission.", "先补上要追踪的主题或信号，草稿才能成为有效任务。"),
          facts: [
            { label: copy("Name", "名称"), value: clampLabel(draft.name, 24) },
            { label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") },
          ],
        }
      : routeName && !routeRecord
        ? {
            title: copy("Named route is not available", "命名路由当前不可用"),
            copy: copy("The draft references a route that is not present in the current route inventory.", "当前草稿引用了一个不在现有路由库存中的命名路由。"),
            facts: [
              { label: copy("Route", "路由"), value: routeName },
              { label: copy("Known routes", "现有路由"), value: String(state.routes.length || 0) },
            ],
          }
        : {
            title: copy("Next prerequisite is optional delivery wiring", "下一个前提是决定是否接入交付"),
            copy: copy("The draft is already valid. Only add a named route when this mission should notify downstream systems.", "当前草稿已经有效；只有在这个任务需要通知下游系统时，才需要继续补命名路由。"),
            tone: "",
            facts: [
              { label: copy("Route", "路由"), value: routeName || copy("not attached", "未绑定") },
              { label: copy("Cadence", "频率"), value: draft.schedule || "manual" },
            ],
          };
  const successSignal = preview.requiredReady
    ? {
        title: copy("Draft can already map to a valid mission", "当前草稿已经能映射成有效任务"),
        copy: copy("The required mission fields are present, so this draft can create or update a watch without leaving the intake lane.", "必填任务字段已经齐全，所以这份草稿可以直接在录入区创建或更新任务。"),
        tone: "ok",
        facts: [
          { label: copy("Name", "名称"), value: clampLabel(draft.name, 24) },
          { label: copy("Query", "查询词"), value: clampLabel(draft.query, 28) },
          { label: copy("Readiness", "就绪度"), value: `${preview.readiness}%` },
        ],
      }
    : (state.createWatchPresetId || String(state.createWatchEditingId || "").trim())
      ? {
          title: copy("Reusable mission source is already loaded", "可复用的任务来源已经载入"),
          copy: copy("A preset or existing mission is already shaping this draft, so the operator does not need to rebuild everything from scratch.", "当前草稿已经带着预设或已有任务来源，操作者不需要从零重建。"),
          facts: [
            { label: copy("Preset", "预设"), value: state.createWatchPresetId || copy("editing existing", "编辑已有任务") },
            { label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") },
          ],
        }
      : {
          title: copy("Mission intake deck is live", "任务录入面板已就绪"),
          copy: copy("The intake lane is ready for the next mission draft even before a reusable source or complete payload exists.", "即使还没有复用来源或完整载荷，录入工作线也已经可以承接下一条任务草稿。"),
          facts: [
            { label: copy("Routes", "路由数"), value: String(state.routes.length || 0) },
            { label: copy("Presets", "预设数"), value: String(createWatchPresets.length || 0) },
          ],
        };
  setSectionSummary("section-intake", {
    title: copy("Mission Intake Readiness", "任务录入就绪度"),
    summary: copy(
      "Keep one concise intake frame visible so operators know what mission or route-aware watch they are preparing to launch.",
      "保持一个简洁的录入摘要框，让操作者始终知道自己正在准备哪条任务或路由感知型 watch。"
    ),
    objective: {
      title: preview.draft.name.trim() || preview.draft.query.trim() || copy("Prepare the next watch mission", "准备下一条监控任务"),
      copy: copy(
        "Mission Intake is currently shaping the next watch payload, including optional alert route and threshold fields.",
        "任务录入区当前正在整理下一条 watch 载荷，其中也包括可选的告警路由和阈值字段。"
      ),
      facts: [
        { label: copy("Schedule", "频率"), value: preview.scheduleLabel },
        { label: copy("Scope", "范围"), value: preview.filtersLabel },
        { label: copy("Route", "路由"), value: preview.routeLabel },
      ],
    },
    success: successSignal,
    blocker: hardBlocker,
  });
}

function renderBoardSectionSummary(filteredWatches = [], searchValue = "") {
  const selectedWatch = state.watches.find((watch) => watch.id === state.selectedWatchId) || null;
  const dueCount = filteredWatches.filter((watch) => watch.is_due).length;
  const blockerSignal = !state.watches.length
    ? {
        title: copy("Mission board is still empty", "任务列表当前为空"),
        copy: copy("Create one watch from Mission Intake before the board can provide a mission set for inspection.", "先从任务录入区创建一条任务，任务列表才能提供可检查的任务集合。"),
        facts: [
          { label: copy("Loaded missions", "已加载任务"), value: "0" },
          { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) },
        ],
      }
    : !filteredWatches.length
      ? {
          title: copy("Current mission search returned zero matches", "当前任务搜索没有命中"),
          copy: copy("The board has missions, but the active search has removed the next mission context needed for inspection.", "当前任务列表里其实有任务，但激活中的搜索把下一条可检查的任务上下文筛掉了。"),
          facts: [
            { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) },
            { label: copy("Total missions", "任务总数"), value: String(state.watches.length || 0) },
          ],
        }
      : !selectedWatch
        ? {
            title: copy("Select one mission for cockpit inspection", "先选择一条任务进入驾驶舱"),
            copy: copy("The board already has candidate missions, but cockpit inspection still needs one active mission context.", "当前任务列表里已经有候选任务，但驾驶舱检查仍然需要一个激活中的任务上下文。"),
            tone: "",
            facts: [
              { label: copy("Shown", "显示"), value: String(filteredWatches.length) },
              { label: copy("Due now", "当前待执行"), value: String(dueCount) },
            ],
          }
        : {
            title: copy("Next prerequisite is cockpit inspection", "下一个前提是进入驾驶舱检查"),
            copy: copy("The board is populated. Open the selected mission in Cockpit when the operator needs detailed run or delivery facts.", "当前任务列表已经有内容；当操作者需要查看更细的执行或交付事实时，下一步就进入驾驶舱。"),
            tone: "",
            facts: [
              { label: copy("Selected", "当前任务"), value: clampLabel(selectedWatch.name || selectedWatch.id, 24) },
              { label: copy("Due now", "当前待执行"), value: String(dueCount) },
            ],
          };
  const successSignal = filteredWatches.length
    ? {
        title: copy("Mission board already has reviewable missions", "任务列表里已经有可继续推进的任务"),
        copy: copy("The board can already hand one or more missions into Cockpit without sending the operator back to Intake first.", "当前任务列表已经可以把一条或多条任务直接交给驾驶舱，不需要先退回录入区。"),
        tone: "ok",
        facts: [
          { label: copy("Shown", "显示"), value: String(filteredWatches.length) },
          { label: copy("Total", "总数"), value: String(state.watches.length || 0) },
          { label: copy("Due", "待执行"), value: String(dueCount) },
        ],
      }
    : {
        title: copy("Mission board shell is ready", "任务列表工作面已经就绪"),
        copy: copy("Search and board controls are live even when the current slice does not expose a reviewable mission set yet.", "即使当前切片里还没有可审阅的任务集合，搜索和列表控制也已经可用。"),
        facts: [
          { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) },
          { label: copy("Total", "总数"), value: String(state.watches.length || 0) },
        ],
      };
  setSectionSummary("section-board", {
    title: copy("Mission Board Snapshot", "任务列表摘要"),
    summary: copy(
      "Frame the current mission set first so operators can see whether the board already contains the next inspectable mission context.",
      "先框定当前正在审阅的任务集合，让操作者快速看清任务列表里是否已经存在下一条可检查任务。"
    ),
    objective: {
      title: selectedWatch
        ? phrase("Review {mission}", "审阅 {mission}", { mission: clampLabel(selectedWatch.name || selectedWatch.id, 18) })
        : (searchValue.trim()
          ? phrase("Review search: {query}", "审阅搜索：{query}", { query: clampLabel(searchValue, 18) })
          : copy("Review the current mission set", "审阅当前任务集合")),
      copy: copy(
        "Mission Board is defining which mission set is under review before the operator commits to Cockpit or Triage.",
        "任务列表当前正在界定哪一组任务处于审阅范围，然后操作者才会继续进入驾驶舱或分诊。"
      ),
      facts: [
        { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") },
        { label: copy("Selected", "当前任务"), value: selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 24) : copy("none", "无") },
        { label: copy("Due now", "当前待执行"), value: String(dueCount) },
      ],
    },
    success: successSignal,
    blocker: blockerSignal,
  });
}

function renderCockpitSectionSummary(watch = null, {
  recentRuns = [],
  recentResults = [],
  retryAdvice = null,
  lastFailure = null,
  deliveryStats = {},
} = {}) {
  const routeSummary = state.ops?.route_summary || {};
  const hasInspectableState = Boolean((Array.isArray(recentRuns) && recentRuns.length) || (Array.isArray(recentResults) && recentResults.length) || Number(watch?.alert_rule_count || 0) > 0);
  const blockerSignal = !watch
    ? {
        title: copy("No mission is selected for cockpit inspection", "当前没有选中任务进入驾驶舱"),
        copy: copy("Cockpit needs one selected mission before it can project current runs, results, or retry guidance.", "驾驶舱需要先有一条被选中的任务，才能投射当前执行、结果和重试建议。"),
        facts: [
          { label: copy("Board missions", "任务数"), value: String(state.watches.length || 0) },
        ],
      }
    : (retryAdvice || lastFailure || String(watch.last_run_status || "").trim().toLowerCase() === "error")
      ? {
          title: copy("Latest run is asking for remediation", "最近一次执行正在请求修复"),
          copy: copy(
            retryAdvice?.summary || lastFailure?.error || "The latest mission run failed and needs operator action before trust is restored.",
            retryAdvice?.summary || lastFailure?.error || "最近一次任务执行失败，在恢复可信度之前需要操作者介入。"
          ),
          facts: [
            { label: copy("Last run", "最近执行"), value: localizeWord(watch.last_run_status || "error") },
            { label: copy("Retry", "重试"), value: retryAdvice?.retry_command || copy("open retry advice", "查看重试建议") },
            { label: copy("Alerts", "告警"), value: String(deliveryStats.recent_alert_count || 0) },
          ],
        }
      : !(Array.isArray(recentRuns) && recentRuns.length)
        ? {
            title: copy("Run this mission once before deeper inspection", "先执行一次任务，再进入更深检查"),
            copy: copy("Cockpit already has the selected mission context, but one run is still missing before results and delivery facts become inspectable.", "驾驶舱已经拿到当前任务上下文，但还缺少至少一次执行，结果流和交付事实才能真正可检查。"),
            tone: "",
            facts: [
              { label: copy("Mission", "任务"), value: clampLabel(watch.name || watch.id, 24) },
              { label: copy("Alert rules", "告警规则"), value: String(watch.alert_rule_count || 0) },
            ],
          }
        : {
            title: copy("Next prerequisite is deciding the next operator action", "下一个前提是决定当前操作者动作"),
            copy: copy("The mission is already live in Cockpit. Decide whether the next move belongs in Triage, retry, or downstream delivery handling.", "当前任务已经在驾驶舱内处于可检查状态；下一步只需判断该进入分诊、重试，还是继续处理下游交付。"),
            tone: "",
            facts: [
              { label: copy("Recent results", "最近结果"), value: String(recentResults.length || 0) },
              { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
            ],
          };
  const successSignal = watch && hasInspectableState
    ? {
        title: copy("Selected mission is already inspectable", "当前选中任务已经可检查"),
        copy: copy("Runs, result stream, or alert settings already provide enough runtime facts to inspect the mission without leaving Cockpit.", "执行记录、结果流或告警设置已经提供了足够的运行事实，可以直接在驾驶舱里检查任务。"),
        tone: "ok",
        facts: [
          { label: copy("Runs", "执行次数"), value: String(recentRuns.length || 0) },
          { label: copy("Results", "结果数"), value: String(recentResults.length || 0) },
          { label: copy("Alert rules", "告警规则"), value: String(watch.alert_rule_count || 0) },
        ],
      }
    : {
        title: copy("Cockpit shell is ready for mission detail", "驾驶舱工作面已经可以承接任务详情"),
        copy: copy("Mission detail, retry guidance, and delivery handoff surfaces are already mounted in this lane.", "任务详情、重试建议和交付交接面板已经全部挂载到当前工作线里。"),
        facts: [
          { label: copy("Mission", "任务"), value: watch ? clampLabel(watch.name || watch.id, 24) : copy("not selected", "未选择") },
          { label: copy("Routes", "路由"), value: String(state.routes.length || 0) },
        ],
      };
  setSectionSummary("section-cockpit", {
    title: copy("Mission Cockpit Snapshot", "任务驾驶舱摘要"),
    summary: copy(
      "Show what the selected mission is doing now, whether it is already inspectable, and what currently blocks trust or the next operator move.",
      "直接展示当前选中任务此刻正在做什么、是否已经可检查，以及当前阻碍可信度或下一步动作的因素。"
    ),
    objective: {
      title: watch
        ? phrase("Inspect {mission} now", "当前检查 {mission}", { mission: clampLabel(watch.name || watch.id, 18) })
        : copy("Select a mission to inspect", "先选择一条任务开始检查"),
      copy: copy(
        "Cockpit keeps the active mission, runtime detail, and delivery handoff in one surface instead of scattering them across the shell.",
        "驾驶舱会把当前任务、运行细节和交付交接维持在同一个面板里，而不是让它们散落在整个 shell 里。"
      ),
      facts: [
        { label: copy("Mission", "任务"), value: watch ? clampLabel(watch.name || watch.id, 24) : copy("none", "无") },
        { label: copy("Status", "状态"), value: watch ? localizeWord(watch.last_run_status || "idle") : copy("idle", "空闲") },
        { label: copy("Last run", "最近执行"), value: watch ? formatCompactDateTime(watch.last_run_at || "") : copy("n/a", "暂无") },
      ],
    },
    success: successSignal,
    blocker: blockerSignal,
  });
}

function renderTriageSectionSummary({
  stats = {},
  filteredItems = [],
  selectedItem = null,
  evidenceFocusCount = 0,
  activeFilter = "open",
  searchValue = "",
} = {}) {
  const linkedStories = selectedItem ? getStoriesForEvidenceItem(selectedItem.id) : [];
  const noteCount = selectedItem && Array.isArray(selectedItem.review_notes) ? selectedItem.review_notes.length : 0;
  const blockerSignal = !state.triage.length
    ? {
        title: copy("Triage queue is still empty", "分诊队列当前为空"),
        copy: copy("The review lane needs inbox evidence from at least one mission run before operators can verify or promote anything.", "审阅工作线需要至少一次任务执行产生的收件箱证据，操作者才能开始核验或提升内容。"),
        facts: [
          { label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) },
        ],
      }
    : !filteredItems.length
      ? {
          title: copy("Active queue slice hides every item", "当前队列切片把所有条目都隐藏了"),
          copy: copy("The queue exists, but the current filter or search has removed the next evidence context needed for review.", "队列本身有内容，但当前筛选或搜索把下一条可审阅证据上下文筛掉了。"),
          facts: [
            { label: copy("Filter", "筛选"), value: localizeWord(activeFilter) },
            { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) },
          ],
        }
      : !selectedItem
        ? {
            title: copy("Pick one evidence item to continue review", "先选中一条证据再继续审阅"),
            copy: copy("The queue already has a reviewable slice, but the current workspace still needs one active evidence selection.", "当前队列里已经有可审阅切片，但当前工作区还需要一个激活中的证据选择。"),
            tone: "",
            facts: [
              { label: copy("Shown", "显示"), value: String(filteredItems.length) },
              { label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) },
            ],
          }
        : (Number(stats.open_count || 0) > filteredItems.length && String(selectedItem.review_state || "new").trim().toLowerCase() === "new")
          ? {
              title: copy("Backlog pressure is still ahead of this review", "当前审阅前方仍有积压压力"),
              copy: copy("The selected item is loaded, but open backlog pressure still suggests more queue work remains before this lane feels clear.", "当前条目已经载入，但开放队列的积压仍然说明这条工作线还没有真正清空。"),
              facts: [
                { label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) },
                { label: copy("Selected state", "当前状态"), value: localizeWord(selectedItem.review_state || "new") },
              ],
            }
          : {
              title: copy("Next prerequisite is verification or story handoff", "下一个前提是完成核验或故事交接"),
              copy: copy("The queue slice is visible. Decide whether the selected evidence should be verified, escalated, or promoted into a story next.", "当前队列切片已经可见；下一步只需要判断这条证据该被核验、升级，还是提升成故事。"),
              tone: "",
              facts: [
                { label: copy("Stories", "关联故事"), value: String(linkedStories.length) },
                { label: copy("Notes", "备注"), value: String(noteCount) },
              ],
            };
  const successSignal = filteredItems.length
    ? {
        title: copy("Current queue slice is moving toward a decision", "当前队列切片正在朝着决策推进"),
        copy: copy(
          selectedItem && linkedStories.length
            ? "The selected evidence is already linked to one or more stories, so review can continue as story handoff instead of starting over."
            : selectedItem && noteCount
              ? "Reviewer notes are already attached to the selected evidence, which keeps reasoning visible while the queue advances."
              : "The queue already contains evidence that can be reviewed, verified, or promoted without leaving the current lane.",
          selectedItem && linkedStories.length
            ? "当前选中的证据已经关联到一个或多个故事，因此后续审阅可以直接沿着故事交接继续，而不必重新开始。"
            : selectedItem && noteCount
              ? "当前选中的证据已经带有审核备注，可以在队列继续推进时保留分析推理。"
              : "当前队列里已经有可审阅、可核验或可提升的证据，不需要离开这条工作线。"
        ),
        tone: "ok",
        facts: [
          { label: copy("Shown", "显示"), value: String(filteredItems.length) },
          { label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) },
          { label: copy("Evidence focus", "证据聚焦"), value: String(evidenceFocusCount || 0) },
        ],
      }
    : {
        title: copy("Triage controls are already mounted", "分诊控制已经挂载完成"),
        copy: copy("Filter, search, and batch controls are ready even when the current queue slice is empty.", "即使当前队列切片为空，筛选、搜索和批量控制也都已经可用。"),
        facts: [
          { label: copy("Filter", "筛选"), value: localizeWord(activeFilter) },
          { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") },
        ],
      };
  setSectionSummary("section-triage", {
    title: copy("Triage Queue Snapshot", "分诊队列摘要"),
    summary: copy(
      "Keep the current inbox slice explicit so operators can see which evidence lane is under review, what is already advancing, and what is still blocking movement.",
      "明确显示当前收件箱切片，让操作者快速看清哪条证据工作线正在被审阅、哪些部分已经推进、哪些因素仍在阻塞。"
    ),
    objective: {
      title: selectedItem
        ? phrase("Review {item}", "审阅 {item}", { item: clampLabel(selectedItem.title || selectedItem.id, 18) })
        : phrase("Review {queue} queue", "审阅 {queue} 队列", { queue: localizeWord(activeFilter) }),
      copy: copy(
        "Triage is currently framing which inbox slice requires review before the operator decides on verification, duplicate handling, or story promotion.",
        "分诊区当前正在界定哪一段收件箱切片需要审阅，然后操作者才会决定是否进行核验、去重或故事提升。"
      ),
      facts: [
        { label: copy("Queue", "队列"), value: localizeWord(activeFilter) },
        { label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") },
        { label: copy("Selected", "当前条目"), value: selectedItem ? clampLabel(selectedItem.title || selectedItem.id, 24) : copy("none", "无") },
      ],
    },
    success: successSignal,
    blocker: blockerSignal,
  });
}

function renderStorySectionSummary({
  filteredStories = [],
  activeStoryView = "all",
  storySort = "attention",
  storySearchValue = "",
} = {}) {
  const selectedStory = getStoryRecord(state.selectedStoryId);
  const deliveryStatus = selectedStory ? getStoryDeliveryStatus(selectedStory) : null;
  const contradictionCount = selectedStory ? (selectedStory.contradictions || []).length : 0;
  const evidenceCount = selectedStory ? Number(selectedStory.item_count || 0) : 0;
  const timelineCount = selectedStory ? (selectedStory.timeline || []).length : 0;
  const blockerSignal = !state.stories.length
    ? {
        title: copy("No persisted story snapshot exists yet", "当前还没有持久化故事快照"),
        copy: copy("Promote one triage item or seed a manual brief before the story lane can advance narrative work.", "先提升一条分诊证据或写下一条手工简报，故事工作线才能开始推进叙事工作。"),
        facts: [
          { label: copy("Stories", "故事数"), value: "0" },
          { label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) },
        ],
      }
    : !filteredStories.length
      ? {
          title: copy("Active story view returned zero matches", "当前故事视图没有返回任何匹配"),
          copy: copy("The story lane has persisted stories, but the active view or search is hiding the next narrative context.", "故事工作线里其实已经有持久化故事，但当前视图或搜索把下一段叙事上下文隐藏掉了。"),
          facts: [
            { label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) },
            { label: copy("Search", "搜索"), value: clampLabel(storySearchValue, 24) },
          ],
        }
      : !selectedStory
        ? {
            title: copy("Select one story to keep advancing", "先选中一条故事再继续推进"),
            copy: copy("The story lane is populated, but the workspace still needs one active story selection for evidence or editor detail.", "故事工作线已经有内容，但工作区仍然需要一条激活中的故事选择，才能展示证据或编辑细节。"),
            tone: "",
            facts: [
              { label: copy("Shown", "显示"), value: String(filteredStories.length) },
              { label: copy("Sort", "排序"), value: storySortLabel(storySort) },
            ],
          }
        : contradictionCount
          ? {
              title: copy("Resolve contradiction markers before export", "导出前先处理冲突标记"),
              copy: copy("This story is already selected, but contradiction markers still block confident promotion or export.", "当前故事已经选中，但冲突标记仍然会阻塞可信的提升或导出。"),
              facts: [
                { label: copy("Conflicts", "冲突数"), value: String(contradictionCount) },
                { label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") },
              ],
            }
          : !evidenceCount
            ? {
                title: copy("Story still needs evidence context", "当前故事仍然缺少证据上下文"),
                copy: copy("A story object exists, but evidence count is still empty, so narrative promotion is not yet grounded enough.", "当前已经存在故事对象，但证据数仍然为空，所以叙事提升还不够扎实。"),
                facts: [
                  { label: copy("Evidence", "证据"), value: "0" },
                  { label: copy("Timeline", "时间线"), value: String(timelineCount) },
                ],
              }
            : deliveryStatus?.key === "blocked"
              ? {
                  title: copy("Delivery gate is blocked for this story", "这条故事的交付门禁当前被阻塞"),
                  copy: copy("Evidence is present, but the delivery gate still reports a blocked state that needs operator review.", "当前故事已经有证据，但交付门禁仍然报告为阻塞状态，需要操作者复核。"),
                  facts: [
                    { label: copy("Delivery", "交付"), value: deliveryStatus.label },
                    { label: copy("Evidence", "证据"), value: String(evidenceCount) },
                  ],
                }
              : {
                  title: copy("Next prerequisite is export or downstream handoff", "下一个前提是导出或下游交接"),
                  copy: copy("The selected story is already grounded enough for the operator to choose between more editing and downstream handoff.", "当前选中的故事已经足够扎实，操作者只需要决定是继续编辑，还是直接进入下游交接。"),
                  tone: "",
                  facts: [
                    { label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") },
                    { label: copy("Timeline", "时间线"), value: String(timelineCount) },
                  ],
                };
  const successSignal = selectedStory && evidenceCount
    ? {
        title: copy("Selected story already carries enough context to move", "当前选中的故事已经带着足够上下文继续推进"),
        copy: copy("Evidence, timeline, or delivery-readiness facts already make this story actionable inside the current workspace.", "证据、时间线或交付就绪度事实已经让这条故事在当前工作区里具备可操作性。"),
        tone: "ok",
        facts: [
          { label: copy("Evidence", "证据"), value: String(evidenceCount) },
          { label: copy("Timeline", "时间线"), value: String(timelineCount) },
          { label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") },
        ],
      }
    : (filteredStories.length
      ? {
          title: copy("Story board already has narrative candidates", "故事看板里已经有叙事候选项"),
          copy: copy("The story lane is populated, so operators can keep advancing narrative work without re-entering triage first.", "故事工作线已经有内容，操作者可以继续推进叙事工作，而不必先重新回到分诊。"),
          tone: "ok",
          facts: [
            { label: copy("Shown", "显示"), value: String(filteredStories.length) },
            { label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) },
            { label: copy("Sort", "排序"), value: storySortLabel(storySort) },
          ],
        }
      : {
          title: copy("Story workspace controls are ready", "故事工作台控制已经就绪"),
          copy: copy("View presets, search, and editor mode are already mounted even when the active slice is empty.", "即使当前切片为空，视图预设、搜索和编辑模式也已经全部挂载完成。"),
          facts: [
            { label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) },
            { label: copy("Search", "搜索"), value: clampLabel(storySearchValue, 24) || copy("none", "无") },
          ],
        });
  setSectionSummary("section-story", {
    title: copy("Story Workspace Snapshot", "故事工作台摘要"),
    summary: copy(
      "Keep the current story objective, one success signal, and one blocker signal visible so narrative work stays grounded before export or delivery.",
      "把当前故事目标、一条成功信号和一条阻塞信号持续保持可见，让叙事工作在导出或交付前始终有事实锚点。"
    ),
    objective: {
      title: selectedStory
        ? phrase("Advance {story}", "推进 {story}", { story: clampLabel(selectedStory.title || selectedStory.id, 18) })
        : phrase("Review {view} stories", "审阅 {view} 故事", { view: storyViewPresetLabel(activeStoryView) }),
      copy: copy(
        "Story Workspace is defining which story or evidence package is currently being advanced in board or editor mode.",
        "故事工作台当前正在界定哪条故事或证据包正在被推进，不管它处于看板模式还是编辑模式。"
      ),
      facts: [
        { label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) },
        { label: copy("Mode", "模式"), value: state.storyWorkspaceMode === "editor" ? copy("Editor", "编辑") : copy("Board", "看板") },
        { label: copy("Selected", "当前故事"), value: selectedStory ? clampLabel(selectedStory.title || selectedStory.id, 24) : copy("none", "无") },
      ],
    },
    success: successSignal,
    blocker: blockerSignal,
  });
}

function renderOpsSectionSummary() {
  const ops = state.ops || {};
  const status = ops.daemon || state.status || {};
  const collectorSummary = ops.collector_summary || {};
  const routeSummary = ops.route_summary || {};
  const routeTimeline = Array.isArray(ops.route_timeline) ? ops.route_timeline : [];
  const recentFailures = Array.isArray(ops.recent_failures) ? ops.recent_failures : [];
  const activeRoute = normalizeRouteName(state.contextRouteName);
  const activeRouteHealth = activeRoute ? getRouteHealthRow(activeRoute) : null;
  const blockerSignal = (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
    ? {
        title: copy("Route health requires remediation", "路由健康当前需要修复"),
        copy: copy("Degraded or missing routes are currently the dominant blocker in the delivery lane.", "降级或缺失的路由当前是交付工作线上的主要阻塞因素。"),
        facts: [
          { label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) },
          { label: copy("Missing", "缺失"), value: String(routeSummary.missing || 0) },
          { label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") },
        ],
      }
    : (collectorSummary.error || 0) > 0 || (collectorSummary.warn || 0) > 0
      ? {
          title: copy("Collector health is degrading the lane", "采集器健康正在拖慢这条工作线"),
          copy: copy("Collector warnings or errors are currently the main operational blocker before delivery can be trusted again.", "在重新信任交付之前，采集器警告或错误是当前最主要的运行阻塞因素。"),
          facts: [
            { label: copy("Collector warn", "采集器警告"), value: String(collectorSummary.warn || 0) },
            { label: copy("Collector error", "采集器错误"), value: String(collectorSummary.error || 0) },
          ],
        }
      : recentFailures.length
        ? {
            title: copy("Recent failures still need review", "最近失败记录仍需复核"),
            copy: copy("The delivery lane has recent runtime failures that should be acknowledged before operators treat it as stable.", "当前交付工作线里还有最近的运行失败，在认定它稳定之前仍应先复核。"),
            facts: [
              { label: copy("Recent failures", "最近失败"), value: String(recentFailures.length) },
              { label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") },
            ],
          }
        : !routeTimeline.length
          ? {
              title: copy("Trigger one routed delivery to seed live ops evidence", "先触发一次路由交付，沉淀实时运维证据"),
              copy: copy("The ops lane is mounted, but it still needs at least one delivery event before route posture is fully observable.", "当前运维工作线已经挂载完成，但还需要至少一次交付事件，路由姿态才能完全可观测。"),
              tone: "",
              facts: [
                { label: copy("Routes", "路由数"), value: String(state.routes.length || 0) },
                { label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") },
              ],
            }
          : {
              title: copy("Next operational risk is route coverage drift", "下一个运行风险是路由覆盖漂移"),
              copy: copy("No hard blocker is active right now, but operators should keep route usage and delivery posture in view.", "当前没有硬阻塞，但操作者仍应继续关注路由使用情况和整体交付姿态。"),
              tone: "",
              facts: [
                { label: copy("Healthy", "健康"), value: String(routeSummary.healthy || 0) },
                { label: copy("Idle", "空闲"), value: String(routeSummary.idle || 0) },
              ],
            };
  const successSignal = String(status.state || "").trim().toLowerCase() !== "error" && (((routeSummary.healthy || 0) > 0) || activeRouteHealth?.status === "healthy")
    ? {
        title: copy("Delivery lane is healthy enough to trust", "交付工作线当前健康到可被信任"),
        copy: copy("Daemon state, route health, and recent delivery observations already show a live lane that operators can supervise with confidence.", "守护进程状态、路由健康和最近交付观察已经共同表明，这是一条可以被稳定监督的工作线。"),
        tone: "ok",
        facts: [
          { label: copy("Daemon", "守护进程"), value: localizeWord(status.state || "running") },
          { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
          { label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") },
        ],
      }
    : {
        title: copy("Ops surfaces are already mounted", "运维工作面已经全部挂载"),
        copy: copy("Daemon, route health, and delivery diagnostics are already available in one surface even before the lane turns fully healthy.", "即使当前工作线还没有完全转绿，守护进程、路由健康和交付诊断也已经都汇集到同一个面板里。"),
        facts: [
          { label: copy("Routes", "路由数"), value: String(state.routes.length || 0) },
          { label: copy("Alerts", "告警数"), value: String(state.alerts.length || 0) },
          { label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") },
        ],
      };
  setSectionSummary("section-ops", {
    title: copy("Ops Snapshot Summary", "运维快照摘要"),
    summary: copy(
      "Keep route or delivery posture visible in one summary frame so operators can see what is healthy, what is blocked, and which route or lane they are supervising.",
      "把当前路由或交付姿态收进一个摘要框，让操作者快速看到什么是健康的、什么被阻塞，以及自己正在监督哪条路由或工作线。"
    ),
    objective: {
      title: activeRoute
        ? phrase("Supervise {route}", "监督 {route}", { route: clampLabel(activeRoute, 18) })
        : copy("Supervise current delivery posture", "监督当前交付姿态"),
      copy: copy(
        "Ops Snapshot is currently framing which route or delivery lane the operator is supervising across daemon, alert, and route facts.",
        "运维快照当前正在界定操作者正监督哪条路由或交付工作线，并把守护进程、告警和路由事实压到同一视图里。"
      ),
      facts: [
        { label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") },
        { label: copy("Daemon", "守护进程"), value: localizeWord(status.state || "idle") },
        { label: copy("Routes", "路由数"), value: String(state.routes.length || 0) },
      ],
    },
    success: successSignal,
    blocker: blockerSignal,
  });
}

function makeSurfaceAction(label, attrs = {}, extra = {}) {
  return { label, attrs, ...extra };
}

function renderCardActionControl(action, tone = "secondary") {
  if (!action || !action.label) {
    return "";
  }
  const className = tone === "primary" ? "btn-primary" : tone === "danger" ? "btn-danger" : "btn-secondary";
  const attrList = Object.entries(action.attrs || {})
    .filter(([, value]) => value !== null && value !== undefined && value !== false && value !== "")
    .map(([key, value]) => (value === true ? key : `${key}="${escapeHtml(String(value))}"`));
  if (action.href) {
    attrList.push(`href="${escapeHtml(String(action.href))}"`);
    if (action.target) {
      attrList.push(`target="${escapeHtml(String(action.target))}"`);
    }
    if (action.rel) {
      attrList.push(`rel="${escapeHtml(String(action.rel))}"`);
    }
    return `<a class="${className}" data-action-tone="${tone}" ${attrList.join(" ")}>${escapeHtml(action.label)}</a>`;
  }
  if (action.disabled) {
    attrList.push("disabled");
  }
  return `<button class="${className}" type="button" data-action-tone="${tone}" ${attrList.join(" ")}>${escapeHtml(action.label)}</button>`;
}

function renderCardActionHierarchy({ primary = null, secondary = [], danger = [] } = {}) {
  const sections = [];
  if (primary) {
    sections.push(`
      <div class="actions action-primary-row" data-card-action-primary>
        ${renderCardActionControl(primary, "primary")}
      </div>
    `);
  }
  const secondaryActions = secondary.filter(Boolean);
  if (secondaryActions.length) {
    sections.push(`
      <div class="actions action-secondary-row" data-card-action-secondary>
        ${secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}
      </div>
    `);
  }
  const dangerActions = danger.filter(Boolean);
  if (dangerActions.length) {
    sections.push(`
      <div class="actions action-danger-row" data-card-action-danger>
        ${dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}
      </div>
    `);
  }
  if (secondaryActions.length || dangerActions.length) {
    sections.push(`
      <details class="action-sheet" data-card-action-sheet>
        <summary class="action-sheet-toggle">${copy("More Actions", "更多操作")}</summary>
        <div class="action-sheet-panel">
          ${secondaryActions.length
            ? `<div class="actions action-secondary-row" data-card-action-sheet-secondary>
                ${secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}
              </div>`
            : ""}
          ${dangerActions.length
            ? `<div class="actions action-danger-row" data-card-action-sheet-danger>
                ${dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}
              </div>`
            : ""}
        </div>
      </details>
    `);
  }
  return sections.length ? `<div class="action-hierarchy">${sections.join("")}</div>` : "";
}
