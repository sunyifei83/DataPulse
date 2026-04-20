// Split group 2z: top-level boot wiring and document listeners.
// Keep this fragment last so all helpers are declared before boot executes.

applyWatchUrlStateFromLocation();
applyTriageUrlStateFromLocation();
state.storyWorkspaceMode = normalizeStoryWorkspaceMode(safeLocalStorageGet(storyWorkspaceModeStorageKey) || state.storyWorkspaceMode);
state.storyFilter = normalizeStoryFilter(safeLocalStorageGet(storyFilterStorageKey) || state.storyFilter);
state.storySort = normalizeStorySort(safeLocalStorageGet(storySortStorageKey) || state.storySort);
applyStoryUrlStateFromLocation();
applyStoryWorkspaceMode(state.storyWorkspaceMode, { persist: false });
state.commandPalette.query = loadCommandPaletteQuery();
state.commandPalette.recentIds = loadCommandPaletteRecent();
state.contextLinkHistory = loadContextLinkHistory();
state.contextSavedViews = loadContextSavedViews();
state.contextDefaultBootPending = !hasExplicitWorkspaceUrlContext();
state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);
state.activeWorkspaceMode = workspaceModeForSection(state.activeSectionId);
state.language = detectInitialLanguage();
window.alert = (message) => showToast(String(message || ""), "error");
state.createWatchDraft = loadCreateWatchDraft();
bindCreateWatchDeck();
bindRouteDeck();
bindStoryDeck();
bindContextObjectRail();
bindHeroStageMotion();
bindSectionJumps();
bindSectionTracking();
bindContextLens();
bindStoryInspector();
bindLanguageSwitch();
bindCommandPalette();
bindResponsiveInteractionContract();
applyLanguageChrome();
renderActionHistory();
renderCommandPalette();
$("palette-open")?.addEventListener("click", () => {
  if (state.commandPalette.open) {
    closeCommandPalette();
  } else {
    openCommandPalette();
  }
});
$("context-reset")?.addEventListener("click", () => {
  resetWorkspaceContext();
});

$("refresh-all").addEventListener("click", async () => {
  const button = $("refresh-all");
  button.disabled = true;
  try {
    await refreshBoard();
    showToast(copy("Console refreshed", "控制台已刷新"), "success");
  } catch (error) {
    reportError(error, copy("Refresh console", "刷新控制台"));
  } finally {
    button.disabled = false;
  }
});
$("run-due").addEventListener("click", async () => {
  const button = $("run-due");
  button.disabled = true;
  try {
    await api("/api/watches/run-due", { method: "POST", payload: { limit: 0 } });
    await refreshBoard();
    showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
  } catch (error) {
    reportError(error, copy("Run due missions", "执行到点任务"));
  } finally {
    button.disabled = false;
  }
});

$("create-watch-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const formElement = event.target;
  const submitButton = formElement.querySelector("button[type='submit']");
  const draft = collectCreateWatchDraft(formElement);
  state.createWatchDraft = draft;
  persistCreateWatchDraft();
  renderCreateWatchDeck();
  if (!(draft.name.trim() && draft.query.trim())) {
    const missingField = draft.name.trim() ? "query" : "name";
    setStageFeedback("start", {
      kind: "blocked",
      title: String(state.createWatchEditingId || "").trim()
        ? copy("Mission edit is still blocked by required fields", "任务修改仍被必填字段阻塞")
        : copy("Mission draft is still blocked by required fields", "任务草稿仍被必填字段阻塞"),
      copy: draft.name.trim()
        ? copy("Add the query before this draft can move into monitoring.", "补上查询词后，这份草稿才能进入监测阶段。")
        : copy("Add a mission name before this draft can move into monitoring.", "补上任务名称后，这份草稿才能进入监测阶段。"),
      actionHierarchy: {
        primary: {
          label: copy("Complete Mission Draft", "继续补全任务草稿"),
          attrs: { "data-empty-focus": "mission", "data-empty-field": missingField },
        },
        secondary: [
          {
            label: copy("Open Mission Board", "打开任务列表"),
            attrs: { "data-empty-jump": "section-board" },
          },
        ],
      },
    });
    showToast(
      String(state.createWatchEditingId || "").trim()
        ? copy("Provide both Name and Query before saving changes.", "保存修改前请同时填写名称和查询词。")
        : copy("Provide both Name and Query before creating a watch.", "创建任务前请同时填写名称和查询词。"),
      "error",
    );
    focusCreateWatchDeck(draft.name.trim() ? "query" : "name");
    return;
  }
  const platformsList = parseListField(draft.platform);
  const sitesList = parseListField(draft.domain);
  const providerValue = (draft.provider || "").trim().toLowerCase();
  const providerMode = ["auto", "jina", "multi"].includes(providerValue) ? providerValue : "auto";
  const alertRules = buildAlertRules({
    route: draft.route.trim(),
    keyword: draft.keyword.trim(),
    domains: sitesList,
    minScore: Number(draft.min_score || 0),
    minConfidence: Number(draft.min_confidence || 0),
  });
  const payload = {
    name: draft.name.trim(),
    query: draft.query.trim(),
    schedule: draft.schedule.trim() || "manual",
    platforms: platformsList.length ? platformsList : null,
    sites: sitesList.length ? sitesList : null,
    provider: providerMode,
    alert_rules: alertRules.length ? alertRules : null,
  };
  const editingId = String(state.createWatchEditingId || "").trim();
  if (submitButton) {
    submitButton.disabled = true;
  }
  if (editingId) {
    try {
      const updated = await api(`/api/watches/${editingId}`, {
        method: "PUT",
        payload,
      });
      state.selectedWatchId = updated.id || editingId;
      state.watchDetails[state.selectedWatchId] = updated;
      state.createWatchAdvancedOpen = null;
      setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
      formElement.reset();
      pushActionEntry({
        kind: copy("mission update", "任务修改"),
        label: state.language === "zh" ? `已更新任务：${payload.name}` : `Updated ${payload.name}`,
        detail: state.language === "zh" ? `任务 ID：${editingId}` : `Mission id: ${editingId}`,
      });
      await refreshBoard();
      setStageFeedback("start", {
        kind: "completion",
        title: state.language === "zh" ? `任务已更新：${payload.name}` : `Mission updated: ${payload.name}`,
        copy: copy(
          "The updated mission now lives in the monitoring lane. Inspect its board posture or open Cockpit to verify the next run.",
          "更新后的任务已经进入监测阶段；下一步可以查看任务列表姿态，或直接打开驾驶舱确认下一次执行。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Mission Board", "打开任务列表"),
            attrs: { "data-empty-jump": "section-board" },
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
        state.language === "zh" ? `任务已更新：${payload.name}` : `Mission updated: ${payload.name}`,
        "success",
      );
    } catch (error) {
      reportError(error, copy("Update watch", "更新任务"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
    return;
  }
  const optimisticId = `draft-${Date.now()}`;
  const optimisticWatch = {
    id: optimisticId,
    name: payload.name,
    query: payload.query,
    enabled: true,
    platforms: payload.platforms || [],
    sites: payload.sites || [],
    provider: payload.provider || "auto",
    schedule: payload.schedule,
    schedule_label: payload.schedule,
    is_due: false,
    next_run_at: "",
    alert_rule_count: Array.isArray(payload.alert_rules) ? payload.alert_rules.length : 0,
    alert_rules: payload.alert_rules || [],
    last_run_at: "",
    last_run_status: "pending",
  };
  state.watches = [optimisticWatch, ...state.watches];
  state.selectedWatchId = optimisticId;
  state.watchDetails[optimisticId] = optimisticWatch;
  renderWatches();
  renderWatchDetail();
  try {
    const created = await api("/api/watches", { method: "POST", payload });
    state.createWatchAdvancedOpen = null;
    setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
    formElement.reset();
    pushActionEntry({
      kind: copy("mission create", "任务创建"),
      label: state.language === "zh" ? `已创建任务：${payload.name}` : `Created ${payload.name}`,
      detail: copy("The new mission can be removed from the recent action log if this was a false start.", "如果这是误创建，可以在最近操作中直接删除。"),
      undoLabel: copy("Delete mission", "删除任务"),
      undo: async () => {
        await api(`/api/watches/${created.id}`, { method: "DELETE" });
        await refreshBoard();
        showToast(
          state.language === "zh" ? `已删除任务：${created.name || created.id}` : `Mission deleted: ${created.name || created.id}`,
          "success",
        );
      },
    });
    await refreshBoard();
    setStageFeedback("start", {
      kind: "completion",
      title: state.language === "zh" ? `任务已创建：${payload.name}` : `Watch created: ${payload.name}`,
      copy: copy(
        "The new mission now owns a slot in monitoring. Select it on the board or open Cockpit to inspect the first run.",
        "新任务现在已经进入监测阶段；下一步可以在任务列表中选中它，或直接打开驾驶舱查看第一次执行。"
      ),
      actionHierarchy: {
        primary: {
          label: copy("Open Mission Board", "打开任务列表"),
          attrs: { "data-empty-jump": "section-board" },
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
      state.language === "zh" ? `任务已创建：${payload.name}` : `Watch created: ${payload.name}`,
      "success",
    );
  } catch (error) {
    state.watches = state.watches.filter((watch) => watch.id !== optimisticId);
    delete state.watchDetails[optimisticId];
    if (state.selectedWatchId === optimisticId) {
      state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
    }
    renderWatches();
    renderWatchDetail();
    reportError(error, copy("Create watch", "创建任务"));
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
});

state.consoleOverflowEvidence = defaultConsoleOverflowEvidence();
window.getConsoleOverflowEvidence = getConsoleOverflowEvidence;

hydrateBoardForSection(state.activeSectionId).catch((error) => {
  reportError(error, copy("Console boot failed", "控制台启动失败"));
});

document.addEventListener("keydown", (event) => {
  const target = event.target;
  const tagName = target && target.tagName ? String(target.tagName).toLowerCase() : "";
  const key = String(event.key || "").toLowerCase();
  if ((event.metaKey || event.ctrlKey) && key === "k") {
    event.preventDefault();
    if (state.commandPalette.open) {
      closeCommandPalette();
    } else {
      openCommandPalette();
    }
    return;
  }
  if (key === "escape" && state.commandPalette.open) {
    event.preventDefault();
    closeCommandPalette();
    return;
  }
  if (key === "escape" && state.contextLensOpen) {
    event.preventDefault();
    setContextLensOpen(false);
    return;
  }
  if (state.commandPalette.open) {
    return;
  }
  if (event.metaKey || event.ctrlKey || event.altKey) {
    return;
  }
  if (["input", "textarea", "select", "button"].includes(tagName)) {
    return;
  }
  if (key === "/") {
    event.preventDefault();
    focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
    return;
  }
  if (["1", "2", "3", "4"].includes(key)) {
    const preset = createWatchPresets[Number(key) - 1];
    if (preset) {
      event.preventDefault();
      state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
      setCreateWatchDraft(preset.values, preset.id, "");
      showToast(
        state.language === "zh"
          ? `${preset.zhLabel || preset.label} 已载入任务草稿`
          : `${preset.label} loaded into the mission deck`,
        "success",
      );
    }
    return;
  }
  const visibleItems = getVisibleTriageItems();
  if (!visibleItems.length) {
    return;
  }
  const selectedId = state.selectedTriageId || visibleItems[0].id;
  const hasBatchSelection = state.selectedTriageIds.length > 0;
  if (key === "j") {
    event.preventDefault();
    moveTriageSelection(1);
  } else if (key === "k") {
    event.preventDefault();
    moveTriageSelection(-1);
  } else if (key === "v") {
    event.preventDefault();
    (hasBatchSelection ? runTriageBatchStateUpdate("verified") : runTriageStateUpdate(selectedId, "verified")).catch((error) => reportError(error, copy("Verify triage item", "核验分诊条目")));
  } else if (key === "t") {
    event.preventDefault();
    (hasBatchSelection ? runTriageBatchStateUpdate("triaged") : runTriageStateUpdate(selectedId, "triaged")).catch((error) => reportError(error, copy("Triage item", "分诊条目")));
  } else if (key === "e") {
    event.preventDefault();
    (hasBatchSelection ? runTriageBatchStateUpdate("escalated") : runTriageStateUpdate(selectedId, "escalated")).catch((error) => reportError(error, copy("Escalate triage item", "升级分诊条目")));
  } else if (key === "i") {
    event.preventDefault();
    (hasBatchSelection ? runTriageBatchStateUpdate("ignored") : runTriageStateUpdate(selectedId, "ignored")).catch((error) => reportError(error, copy("Ignore triage item", "忽略分诊条目")));
  } else if (key === "s") {
    event.preventDefault();
    (hasBatchSelection ? createStoryFromTriageItems(state.selectedTriageIds) : createStoryFromTriageItems([selectedId])).catch((error) => reportError(error, copy("Create story from triage", "从分诊生成故事")));
  } else if (key === "d") {
    event.preventDefault();
    runTriageExplain(selectedId).catch((error) => reportError(error, copy("Explain duplicates", "查看重复解释")));
  } else if (key === "n") {
    event.preventDefault();
    focusTriageNoteComposer(selectedId);
  }
});
