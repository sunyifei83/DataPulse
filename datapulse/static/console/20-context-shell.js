// Split group 2b: workspace context, URL state, shell descriptors, and context lens helpers.
// Depends on prior fragments and 00-common.js.

function safeLocalStorageGet(key) {
  try {
    return window.localStorage.getItem(key);
  } catch (error) {
    return null;
  }
}

function safeLocalStorageSet(key, value) {
  try {
    window.localStorage.setItem(key, value);
  } catch (error) {
    console.warn("localStorage write skipped", error);
  }
}

function safeLocalStorageRemove(key) {
  try {
    window.localStorage.removeItem(key);
  } catch (error) {
    console.warn("localStorage remove skipped", error);
  }
}

function loadCreateWatchDraft() {
  const raw = safeLocalStorageGet(createWatchStorageKey);
  if (!raw) {
    return defaultCreateWatchDraft();
  }
  try {
    return normalizeCreateWatchDraft(JSON.parse(raw));
  } catch (error) {
    safeLocalStorageRemove(createWatchStorageKey);
    return defaultCreateWatchDraft();
  }
}

function persistCreateWatchDraft() {
  const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
  const hasSignal = createWatchFormFields.some((field) => String(draft[field] || "").trim());
  if (!hasSignal) {
    safeLocalStorageRemove(createWatchStorageKey);
    return;
  }
  safeLocalStorageSet(createWatchStorageKey, JSON.stringify(draft));
}

function persistStoryWorkspacePrefs() {
  safeLocalStorageSet(storyFilterStorageKey, normalizeStoryFilter(state.storyFilter));
  safeLocalStorageSet(storySortStorageKey, normalizeStorySort(state.storySort));
  safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
}

function loadCommandPaletteQuery() {
  return String(safeLocalStorageGet(commandPaletteQueryStorageKey) || "").trim();
}

function persistCommandPaletteQuery() {
  const query = String(state.commandPalette.query || "").trim();
  if (!query) {
    safeLocalStorageRemove(commandPaletteQueryStorageKey);
    return;
  }
  safeLocalStorageSet(commandPaletteQueryStorageKey, query);
}

function loadCommandPaletteRecent() {
  const raw = safeLocalStorageGet(commandPaletteRecentStorageKey);
  if (!raw) {
    return [];
  }
  try {
    return uniqueValues(JSON.parse(raw)).slice(0, 8);
  } catch (error) {
    safeLocalStorageRemove(commandPaletteRecentStorageKey);
    return [];
  }
}

function persistCommandPaletteRecent() {
  const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
  if (!recentIds.length) {
    safeLocalStorageRemove(commandPaletteRecentStorageKey);
    return;
  }
  safeLocalStorageSet(commandPaletteRecentStorageKey, JSON.stringify(recentIds));
}

function noteCommandPaletteRecent(entryId) {
  const normalized = String(entryId || "").trim();
  if (!normalized) {
    return;
  }
  state.commandPalette.recentIds = [normalized, ...uniqueValues(state.commandPalette.recentIds || []).filter((id) => id !== normalized)].slice(0, 8);
  persistCommandPaletteRecent();
}

function normalizeContextLinkHistoryEntry(entry) {
  const url = String(entry?.url || "").trim();
  if (!url) {
    return null;
  }
  const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
  const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
  const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
  return { url, summary, sectionId, timestamp };
}

function loadContextLinkHistory() {
  const raw = safeLocalStorageGet(contextLinkHistoryStorageKey);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return (Array.isArray(parsed) ? parsed : [])
      .map((entry) => normalizeContextLinkHistoryEntry(entry))
      .filter(Boolean)
      .slice(0, 6);
  } catch (error) {
    safeLocalStorageRemove(contextLinkHistoryStorageKey);
    return [];
  }
}

function persistContextLinkHistory() {
  const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
    .map((entry) => normalizeContextLinkHistoryEntry(entry))
    .filter(Boolean)
    .slice(0, 6);
  if (!entries.length) {
    safeLocalStorageRemove(contextLinkHistoryStorageKey);
    return;
  }
  safeLocalStorageSet(contextLinkHistoryStorageKey, JSON.stringify(entries));
}

function noteContextLinkHistory(entry) {
  const normalized = normalizeContextLinkHistoryEntry(entry);
  if (!normalized) {
    return;
  }
  state.contextLinkHistory = [
    normalized,
    ...(Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
      .map((candidate) => normalizeContextLinkHistoryEntry(candidate))
      .filter((candidate) => candidate && candidate.url !== normalized.url),
  ].slice(0, 6);
  persistContextLinkHistory();
  renderCommandPalette();
}

function clearContextLinkHistory({ toast = true } = {}) {
  state.contextLinkHistory = [];
  persistContextLinkHistory();
  renderCommandPalette();
  renderTopbarContext();
  if (toast) {
    showToast(copy("Shared context history cleared", "已清空分享上下文历史"), "success");
  }
}

function normalizeContextSavedViewEntry(entry) {
  const url = String(entry?.url || "").trim();
  const rawName = String(entry?.name || "").trim();
  if (!(url && rawName)) {
    return null;
  }
  const name = clampLabel(rawName, 72);
  const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
  const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
  const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
  const pinned = Boolean(entry?.pinned);
  const isDefault = Boolean(entry?.isDefault);
  return { name, url, summary, sectionId, timestamp, pinned, isDefault };
}

function loadContextSavedViews() {
  const raw = safeLocalStorageGet(contextSavedViewsStorageKey);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return (Array.isArray(parsed) ? parsed : [])
      .map((entry) => normalizeContextSavedViewEntry(entry))
      .filter(Boolean)
      .slice(0, 8);
  } catch (error) {
    safeLocalStorageRemove(contextSavedViewsStorageKey);
    return [];
  }
}

function persistContextSavedViews() {
  const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .filter(Boolean)
    .slice(0, 8);
  if (!entries.length) {
    safeLocalStorageRemove(contextSavedViewsStorageKey);
    return;
  }
  safeLocalStorageSet(contextSavedViewsStorageKey, JSON.stringify(entries));
}

function upsertContextSavedView(entry) {
  const normalized = normalizeContextSavedViewEntry(entry);
  if (!normalized) {
    return false;
  }
  const hasPinnedOverride = Object.prototype.hasOwnProperty.call(entry || {}, "pinned");
  const hasDefaultOverride = Object.prototype.hasOwnProperty.call(entry || {}, "isDefault");
  const existing = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((candidate) => normalizeContextSavedViewEntry(candidate))
    .filter(Boolean);
  const existingIndex = existing.findIndex((candidate) => candidate.name.toLowerCase() === normalized.name.toLowerCase());
  const existingPinned = existingIndex >= 0 ? Boolean(existing[existingIndex]?.pinned) : false;
  const existingDefault = existingIndex >= 0 ? Boolean(existing[existingIndex]?.isDefault) : false;
  const resolvedEntry = {
    ...normalized,
    pinned: hasPinnedOverride ? Boolean(entry.pinned) : existingPinned,
    isDefault: hasDefaultOverride ? Boolean(entry.isDefault) : existingDefault,
  };
  const next = existingIndex >= 0
    ? existing.map((candidate, index) => (index === existingIndex ? resolvedEntry : candidate))
    : [resolvedEntry, ...existing].slice(0, 8);
  state.contextSavedViews = next;
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  return existingIndex >= 0;
}

function findContextSavedViewIndexByName(viewName) {
  const normalizedName = String(viewName || "").trim().toLowerCase();
  if (!normalizedName) {
    return -1;
  }
  return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
}

function findContextSavedViewIndexByUrl(viewUrl) {
  const normalizedUrl = String(viewUrl || "").trim();
  if (!normalizedUrl) {
    return -1;
  }
  return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .findIndex((entry) => entry && entry.url === normalizedUrl);
}

function buildUniqueContextSavedViewName(baseName) {
  const trimmedBase = clampLabel(String(baseName || "").trim(), 72) || copy("Saved View", "保存视图");
  const normalizedExisting = new Set(
    (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
      .map((entry) => normalizeContextSavedViewEntry(entry))
      .filter(Boolean)
      .map((entry) => entry.name.toLowerCase())
  );
  if (!normalizedExisting.has(trimmedBase.toLowerCase())) {
    return trimmedBase;
  }
  let counter = 2;
  while (counter < 100) {
    const candidate = clampLabel(`${trimmedBase} ${counter}`, 72);
    if (!normalizedExisting.has(candidate.toLowerCase())) {
      return candidate;
    }
    counter += 1;
  }
  return clampLabel(`${trimmedBase} copy`, 72);
}

function saveCurrentContextView(rawName = "") {
  const base = buildCurrentContextLinkRecord();
  if (!base) {
    return;
  }
  const preferredName = String(rawName || "").trim() || base.summary;
  const wasOverwrite = upsertContextSavedView({
    name: preferredName,
    ...base,
    timestamp: new Date().toISOString(),
  });
  const input = $("context-save-name");
  if (input) {
    input.value = "";
  }
  showToast(
    wasOverwrite
      ? copy("Saved view updated", "已更新保存视图")
      : copy("Saved view added", "已保存当前视图"),
    "success",
  );
}

function saveAndPinCurrentContextView() {
  const current = buildCurrentContextLinkRecord();
  if (!current) {
    return;
  }
  const existingIndex = findContextSavedViewIndexByUrl(current.url);
  if (existingIndex >= 0) {
    const existing = normalizeContextSavedViewEntry(state.contextSavedViews[existingIndex]);
    if (existing?.pinned) {
      showToast(copy("Current view is already pinned", "当前视图已固定到坞站"), "success");
      return;
    }
    if (countPinnedContextSavedViews() >= 4) {
      showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
      return;
    }
    upsertContextSavedView({
      ...existing,
      ...current,
      name: existing.name,
      pinned: true,
      isDefault: existing.isDefault,
      timestamp: new Date().toISOString(),
    });
    showToast(copy("Current view saved to the top dock", "已将当前视图固定到顶部坞站"), "success");
    return;
  }
  if (countPinnedContextSavedViews() >= 4) {
    showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
    return;
  }
  upsertContextSavedView({
    name: buildUniqueContextSavedViewName(current.summary),
    ...current,
    pinned: true,
    timestamp: new Date().toISOString(),
  });
  showToast(copy("Current view saved and pinned", "已保存并固定当前视图"), "success");
}

function startContextDockRename(viewName) {
  const index = findContextSavedViewIndexByName(viewName);
  if (index < 0) {
    return;
  }
  const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!entry || !entry.pinned) {
    return;
  }
  state.contextDockEditingName = entry.name;
  renderTopbarContext();
  window.setTimeout(() => {
    const input = $("context-dock-rename-input");
    input?.focus();
    input?.select();
  }, 10);
}

function cancelContextDockRename() {
  if (!String(state.contextDockEditingName || "").trim()) {
    return;
  }
  state.contextDockEditingName = "";
  renderTopbarContext();
}

function renameContextSavedView(viewName, rawNextName) {
  const index = findContextSavedViewIndexByName(viewName);
  if (index < 0) {
    return;
  }
  const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!current) {
    return;
  }
  const nextName = clampLabel(String(rawNextName || "").trim(), 72);
  if (!nextName) {
    showToast(copy("Provide a name before saving the view label.", "保存视图标签前请先填写名称。"), "error");
    return;
  }
  const duplicateIndex = findContextSavedViewIndexByName(nextName);
  if (duplicateIndex >= 0 && duplicateIndex !== index) {
    showToast(copy("A saved view with that name already exists.", "已有同名保存视图。"), "error");
    return;
  }
  state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {
    const normalized = normalizeContextSavedViewEntry(candidate);
    if (!normalized) {
      return candidate;
    }
    if (candidateIndex !== index) {
      return normalized;
    }
    return {
      ...normalized,
      name: nextName,
      timestamp: new Date().toISOString(),
    };
  });
  state.contextDockEditingName = "";
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  showToast(
    state.language === "zh" ? `已重命名视图：${nextName}` : `Saved view renamed: ${nextName}`,
    "success",
  );
}

function deleteContextSavedView(entryIndex, { toast = true } = {}) {
  const index = Number(entryIndex);
  const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!current) {
    return;
  }
  if (String(state.contextDockEditingName || "").trim().toLowerCase() === String(current.name || "").trim().toLowerCase()) {
    state.contextDockEditingName = "";
  }
  state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .filter((_, candidateIndex) => candidateIndex !== index);
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  if (toast) {
    showToast(
      state.language === "zh" ? `已删除保存视图：${current.name}` : `Saved view removed: ${current.name}`,
      "success",
    );
  }
}

function clearContextSavedViews({ toast = true } = {}) {
  state.contextSavedViews = [];
  state.contextDockEditingName = "";
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  if (toast) {
    showToast(copy("Saved views cleared", "已清空保存视图"), "success");
  }
}

function getDefaultContextSavedView() {
  return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .find((entry) => entry && entry.isDefault) || null;
}

function clearDefaultContextSavedView({ toast = true } = {}) {
  const currentDefault = getDefaultContextSavedView();
  if (!currentDefault) {
    return;
  }
  state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate) => {
    const normalized = normalizeContextSavedViewEntry(candidate);
    return normalized ? { ...normalized, isDefault: false } : candidate;
  });
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  if (toast) {
    showToast(copy("Default landing view cleared", "已清除默认落地视图"), "success");
  }
}

function setDefaultContextSavedView(entryIndex) {
  const index = Number(entryIndex);
  const target = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!target) {
    return;
  }
  const shouldUnset = Boolean(target.isDefault);
  state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {
    const normalized = normalizeContextSavedViewEntry(candidate);
    if (!normalized) {
      return candidate;
    }
    return {
      ...normalized,
      isDefault: shouldUnset ? false : candidateIndex === index,
    };
  });
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  showToast(
    shouldUnset
      ? copy("Default landing view cleared", "已清除默认落地视图")
      : copy("Default landing view updated", "已更新默认落地视图"),
    "success",
  );
}

function hasExplicitWorkspaceUrlContext() {
  return Boolean(
    readWatchUrlState().hasWatchContext ||
    readTriageUrlState().hasTriageContext ||
    readStoryUrlState().hasStoryContext ||
    String(window.location.hash || "").trim()
  );
}

function countPinnedContextSavedViews() {
  return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .filter((entry) => entry && entry.pinned)
    .length;
}

function getPinnedContextSavedViewIndexes() {
  return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry, index) => {
      const normalized = normalizeContextSavedViewEntry(entry);
      return normalized && normalized.pinned ? index : -1;
    })
    .filter((index) => index >= 0);
}

function toggleContextSavedViewPinned(entryIndex) {
  const index = Number(entryIndex);
  const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!entry) {
    return;
  }
  if (!entry.pinned && countPinnedContextSavedViews() >= 4) {
    showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
    return;
  }
  if (entry.pinned && String(state.contextDockEditingName || "").trim().toLowerCase() === String(entry.name || "").trim().toLowerCase()) {
    state.contextDockEditingName = "";
  }
  state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {
    const normalized = normalizeContextSavedViewEntry(candidate);
    if (!normalized) {
      return candidate;
    }
    if (candidateIndex !== index) {
      return normalized;
    }
    return {
      ...normalized,
      pinned: !normalized.pinned,
      timestamp: new Date().toISOString(),
    };
  });
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  showToast(
    entry.pinned
      ? copy("Saved view removed from the top dock", "已从顶部坞站取消固定")
      : copy("Saved view pinned to the top dock", "已固定到顶部坞站"),
    "success",
  );
}

function moveContextSavedViewInDock(entryIndex, direction = "left") {
  const index = Number(entryIndex);
  const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
  if (!entry || !entry.pinned) {
    return;
  }
  const pinnedIndexes = getPinnedContextSavedViewIndexes();
  const currentPosition = pinnedIndexes.indexOf(index);
  if (currentPosition < 0) {
    return;
  }
  const offset = direction === "right" ? 1 : -1;
  const nextPosition = currentPosition + offset;
  if (nextPosition < 0 || nextPosition >= pinnedIndexes.length) {
    return;
  }
  const swapIndex = pinnedIndexes[nextPosition];
  const reordered = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((candidate) => normalizeContextSavedViewEntry(candidate))
    .filter(Boolean);
  [reordered[index], reordered[swapIndex]] = [reordered[swapIndex], reordered[index]];
  state.contextSavedViews = reordered;
  persistContextSavedViews();
  renderCommandPalette();
  renderTopbarContext();
  showToast(
    direction === "right"
      ? copy("Pinned view moved right", "已将固定视图右移")
      : copy("Pinned view moved left", "已将固定视图左移"),
    "success",
  );
}

function resetWorkspaceContext({ jump = true, toast = true } = {}) {
  setContextLensOpen(false);
  closeStoryInspector({ restoreFocus: false });
  state.watchSearch = "";
  state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
  state.watchResultFilters = {};
  setContextRouteName("", "");

  state.triageFilter = "open";
  state.triageSearch = "";
  state.triagePinnedIds = [];
  state.selectedTriageIds = [];
  state.selectedTriageId = "";
  state.triageUrlFocusPending = false;

  state.storySearch = "";
  state.storyWorkspaceMode = "board";
  state.storyDetailView = "overview";
  state.storyFilter = "all";
  state.storySort = "attention";
  state.selectedStoryIds = [];
  state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
  state.storyUrlFocusPending = false;
  persistStoryWorkspacePrefs();

  state.selectedClaimId = state.claimCards[0] ? state.claimCards[0].id : "";
  state.selectedReportId = state.reports[0] ? state.reports[0].id : "";
  const defaultSections = getReportSectionsForReport(state.selectedReportId);
  state.selectedReportSectionId = defaultSections[0] ? defaultSections[0].id : "";

  state.commandPalette.query = "";
  persistCommandPaletteQuery();
  closeCommandPalette();

  state.watchUrlFocusPending = false;
  renderWatches();
  renderWatchDetail();
  renderTriage();
  renderStories();
  renderClaimsWorkspace();
  renderReportStudio();
  renderCommandPalette();
  if (jump) {
    jumpToSection("section-intake");
  }
  if (toast) {
    showToast(copy("Workspace context reset", "当前工作上下文已重置"), "success");
  }
}

function applyStoryViewPreset(viewKey, { jump = false, toast = false } = {}) {
  const preset = getStoryViewPreset(viewKey);
  if (!preset) {
    return;
  }
  state.storySearch = "";
  state.storyFilter = preset.filter;
  state.storySort = preset.sort;
  persistStoryWorkspacePrefs();
  renderStories();
  if (jump) {
    jumpToSection("section-story");
  }
  if (toast) {
    showToast(
      state.language === "zh"
        ? `故事视图已切换：${storyViewPresetLabel(preset.key)}`
        : `Story view switched: ${storyViewPresetLabel(preset.key)}`,
      "success",
    );
  }
}

function renderStoryViewJumpStrip() {
  const root = $("story-view-jumps");
  if (!root) {
    return;
  }
  const activeStoryView = detectStoryViewPreset({
    filter: state.storyFilter,
    sort: state.storySort,
    search: state.storySearch,
  });
  root.innerHTML = `
    <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Story view shortcuts", "故事视图快捷切换"))}">
      ${storyViewPresetOptions.map((option) => `
        <button class="ui-segment-button ${activeStoryView === option ? "active" : ""}" type="button" data-story-view-shortcut="${escapeHtml(option)}" aria-pressed="${activeStoryView === option ? "true" : "false"}">
          ${escapeHtml(storyViewPresetLabel(option))}
        </button>
      `).join("")}
    </div>
    ${activeStoryView === "custom" ? `<span class="chip hot">${storyViewPresetLabel("custom")}</span>` : ""}
  `;
  root.querySelectorAll("[data-story-view-shortcut]").forEach((button) => {
    button.addEventListener("click", () => {
      applyStoryViewPreset(String(button.dataset.storyViewShortcut || "").trim(), { jump: true });
    });
  });
}

function readWatchUrlState() {
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const search = String(params.get(watchUrlSearchParam) || "").trim();
  const watchId = String(params.get(watchUrlIdParam) || "").trim();
  const hasWatchContext = Boolean(search || watchId || url.hash === "#section-board" || url.hash === "#section-cockpit");
  return { hasWatchContext, search, watchId };
}

function applyWatchUrlStateFromLocation() {
  const urlState = readWatchUrlState();
  if (!urlState.hasWatchContext) {
    return;
  }
  state.watchSearch = urlState.search;
  if (urlState.watchId) {
    state.selectedWatchId = urlState.watchId;
  }
  state.watchUrlFocusPending = true;
}

function syncWatchUrlState({ defaultWatchId = "" } = {}) {
  if (state.loading.board) {
    return;
  }
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const search = String(state.watchSearch || "").trim();
  const watchId = String(state.selectedWatchId || "").trim();

  if (search) {
    params.set(watchUrlSearchParam, search);
  } else {
    params.delete(watchUrlSearchParam);
  }

  if (watchId) {
    params.set(watchUrlIdParam, watchId);
  } else {
    params.delete(watchUrlIdParam);
  }

  const nextSearch = params.toString();
  const nextUrl = `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash || ""}`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (nextUrl !== currentUrl) {
    window.history.replaceState(window.history.state, "", nextUrl);
  }
}

function flushWatchUrlFocus() {
  if (!state.watchUrlFocusPending) {
    return;
  }
  state.watchUrlFocusPending = false;
  window.setTimeout(() => {
    jumpToSection(window.location.hash === "#section-board" ? "section-board" : "section-cockpit", { updateHash: false });
  }, 0);
}

function readTriageUrlState() {
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const filter = String(params.get(triageUrlFilterParam) || "").trim().toLowerCase();
  const search = String(params.get(triageUrlSearchParam) || "").trim();
  const itemId = String(params.get(triageUrlIdParam) || "").trim();
  const hasTriageContext = Boolean(filter || search || itemId || url.hash === "#section-triage");
  return {
    hasTriageContext,
    filter: normalizeTriageFilter(filter || state.triageFilter),
    search,
    itemId,
  };
}

function applyTriageUrlStateFromLocation() {
  const urlState = readTriageUrlState();
  if (!urlState.hasTriageContext) {
    return;
  }
  state.triageFilter = urlState.filter;
  state.triageSearch = urlState.search;
  if (urlState.itemId) {
    state.selectedTriageId = urlState.itemId;
  }
  state.triageUrlFocusPending = true;
}

function syncTriageUrlState({ defaultItemId = "" } = {}) {
  if (state.loading.board) {
    return;
  }
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const filter = normalizeTriageFilter(state.triageFilter);
  const search = String(state.triageSearch || "").trim();
  const itemId = String(state.selectedTriageId || "").trim();

  if (filter !== "open") {
    params.set(triageUrlFilterParam, filter);
  } else {
    params.delete(triageUrlFilterParam);
  }

  if (search) {
    params.set(triageUrlSearchParam, search);
  } else {
    params.delete(triageUrlSearchParam);
  }

  if (itemId) {
    params.set(triageUrlIdParam, itemId);
  } else {
    params.delete(triageUrlIdParam);
  }

  const nextSearch = params.toString();
  const nextUrl = `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash || ""}`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (nextUrl !== currentUrl) {
    window.history.replaceState(window.history.state, "", nextUrl);
  }
}

function flushTriageUrlFocus() {
  if (!state.triageUrlFocusPending) {
    return;
  }
  state.triageUrlFocusPending = false;
  window.setTimeout(() => {
    jumpToSection("section-triage", { updateHash: false });
  }, 0);
}

function applyStoryWorkspaceMode(mode, { persist = true, syncUrl = false, defaultStoryId = "" } = {}) {
  state.storyWorkspaceMode = normalizeStoryWorkspaceMode(mode);
  if (document.body) {
    document.body.dataset.storyWorkspaceMode = state.storyWorkspaceMode;
  }
  const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
  if (storyWorkspaceModeSwitch) {
    storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {
      const buttonMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode);
      const isActive = buttonMode === state.storyWorkspaceMode;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }
  if (persist) {
    safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
  }
  if (syncUrl) {
    syncStoryUrlState({ defaultStoryId });
  }
}

function readStoryUrlState() {
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const view = String(params.get(storyUrlViewParam) || "").trim().toLowerCase();
  const filter = String(params.get(storyUrlFilterParam) || "").trim().toLowerCase();
  const sort = String(params.get(storyUrlSortParam) || "").trim().toLowerCase();
  const search = String(params.get(storyUrlSearchParam) || "").trim();
  const storyId = String(params.get(storyUrlIdParam) || "").trim();
  const storyWorkspaceMode = String(params.get(storyUrlModeParam) || "").trim().toLowerCase();
  const preset = getStoryViewPreset(view);
  const resolvedFilter = filter
    ? normalizeStoryFilter(filter)
    : (preset ? normalizeStoryFilter(preset.filter) : normalizeStoryFilter(state.storyFilter));
  const resolvedSort = sort
    ? normalizeStorySort(sort)
    : (preset ? normalizeStorySort(preset.sort) : normalizeStorySort(state.storySort));
  const resolvedStoryWorkspaceMode = normalizeStoryWorkspaceMode(storyWorkspaceMode);
  const hasStoryContext = Boolean(view || filter || sort || search || storyId || url.hash === "#section-story");
  return {
    hasStoryContext,
    filter: resolvedFilter,
    sort: resolvedSort,
    search,
    storyId,
    storyWorkspaceMode: resolvedStoryWorkspaceMode,
  };
}

function applyStoryUrlStateFromLocation() {
  const urlState = readStoryUrlState();
  if (!urlState.hasStoryContext) {
    return;
  }
  state.storyFilter = urlState.filter;
  state.storySort = urlState.sort;
  state.storySearch = urlState.search;
  state.storyWorkspaceMode = urlState.storyWorkspaceMode;
  if (urlState.storyId) {
    state.selectedStoryId = urlState.storyId;
  }
  state.storyUrlFocusPending = true;
}

function syncStoryUrlState({ defaultStoryId = "" } = {}) {
  if (state.loading.board) {
    return;
  }
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const filter = normalizeStoryFilter(state.storyFilter);
  const sort = normalizeStorySort(state.storySort);
  const search = String(state.storySearch || "").trim();
  const storyId = String(state.selectedStoryId || "").trim();
  const activeView = detectStoryViewPreset({ filter, sort, search });

  if (!search && activeView !== "custom" && activeView !== "desk") {
    params.set(storyUrlViewParam, activeView);
  } else {
    params.delete(storyUrlViewParam);
  }

  if (activeView === "custom") {
    if (filter !== "all") {
      params.set(storyUrlFilterParam, filter);
    } else {
      params.delete(storyUrlFilterParam);
    }
    if (sort !== "attention") {
      params.set(storyUrlSortParam, sort);
    } else {
      params.delete(storyUrlSortParam);
    }
  } else {
    params.delete(storyUrlFilterParam);
    params.delete(storyUrlSortParam);
  }

  if (search) {
    params.set(storyUrlSearchParam, search);
  } else {
    params.delete(storyUrlSearchParam);
  }

  if (storyId) {
    params.set(storyUrlIdParam, storyId);
  } else {
    params.delete(storyUrlIdParam);
  }
  if (state.storyWorkspaceMode === "editor") {
    params.set(storyUrlModeParam, state.storyWorkspaceMode);
  } else {
    params.delete(storyUrlModeParam);
  }

  const nextSearch = params.toString();
  const nextUrl = `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${url.hash || ""}`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (nextUrl !== currentUrl) {
    window.history.replaceState(window.history.state, "", nextUrl);
  }
}

function flushStoryUrlFocus() {
  if (!state.storyUrlFocusPending) {
    return;
  }
  state.storyUrlFocusPending = false;
  window.setTimeout(() => {
    jumpToSection("section-story", { updateHash: false });
  }, 0);
}

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

function detectInitialLanguage() {
  const stored = String(safeLocalStorageGet(languageStorageKey) || "").trim().toLowerCase();
  if (stored === "zh" || stored === "en") {
    return stored;
  }
  const browserLanguage = String(window.navigator.language || "").trim().toLowerCase();
  return browserLanguage.startsWith("zh") ? "zh" : "en";
}

function normalizeSectionId(value) {
  const normalized = String(value || "").trim().replace(/^#/, "");
  return [
    "section-intake",
    "section-board",
    "section-cockpit",
    "section-triage",
    "section-story",
    "section-claims",
    "section-report-studio",
    "section-ops",
  ].includes(normalized)
    ? normalized
    : "section-intake";
}

state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);

function setText(id, value) {
  const node = $(id);
  if (node) {
    node.textContent = value;
    if (node instanceof HTMLElement && node.hasAttribute("data-fit-text")) {
      delete node.dataset.fitTextOriginal;
      delete node.dataset.fitApplied;
    }
  }
}

function setHTML(id, value) {
  const node = $(id);
  if (node) {
    node.innerHTML = value;
  }
}

function setPlaceholder(id, value) {
  const node = $(id);
  if (node) {
    node.placeholder = value;
  }
}

function activeSectionLabel(sectionId) {
  const labels = {
    "section-intake": copy("Mission Intake", "任务录入"),
    "section-board": copy("Mission Board", "任务列表"),
    "section-cockpit": copy("Cockpit", "任务详情"),
    "section-triage": copy("Triage", "分诊"),
    "section-story": copy("Stories", "故事"),
    "section-claims": copy("Claim Composer", "主张装配"),
    "section-report-studio": copy("Report Studio", "报告工作台"),
    "section-ops": copy("Ops Snapshot", "运行状态"),
  };
  return labels[normalizeSectionId(sectionId)] || labels["section-intake"];
}

function normalizeWorkspaceMode(value) {
  const normalized = String(value || "").trim().toLowerCase();
  return Object.prototype.hasOwnProperty.call(workspaceModeSectionMap, normalized) ? normalized : "intake";
}

function workspaceModeForSection(sectionId) {
  const normalizedSection = normalizeSectionId(sectionId);
  if (workspaceModeSectionMap.missions.includes(normalizedSection)) {
    return "missions";
  }
  if (workspaceModeSectionMap.review.includes(normalizedSection)) {
    return "review";
  }
  if (workspaceModeSectionMap.delivery.includes(normalizedSection)) {
    return "delivery";
  }
  return "intake";
}

function workspaceModeDescriptor(modeId) {
  const normalized = normalizeWorkspaceMode(modeId);
  const descriptors = {
    intake: {
      id: "intake",
      label: copy("Start", "开始"),
      kicker: copy("Start", "开始"),
      summary: copy(
        "Keep mission intake as the clean starting surface so the first decision stays focused on what to monitor next.",
        "把任务录入单独作为起始界面，确保进入控制台后的第一个判断仍然只是下一步要监测什么。"
      ),
      modules: [
        {
          sectionId: "section-intake",
          title: copy("Mission Intake", "任务录入"),
          summary: copy(
            "Start from one mission draft and keep the first move narrow: define the watch, then hand it into monitoring.",
            "从一个任务草稿开始，把第一步收窄成定义监测对象，然后再交给监测阶段。"
          ),
          output: copy("Readiness state and current checklist", "就绪状态和当前清单"),
          nextAction: copy("Create one mission", "创建一个任务"),
          cta: copy("Open Start Surface", "打开开始视图"),
        },
      ],
      advancedActions: [],
      landingSection: "section-intake",
      footnote: copy("Keep this stage narrow: readiness first, downstream detail later.", "这个阶段只保留最小必要范围：先确认就绪，再进入下游细节。"),
      topbarSubtitle: copy("Workflow stages | Start -> Monitor -> Review -> Deliver", "工作流阶段 | 开始 -> 监测 -> 审阅 -> 交付"),
    },
    missions: {
      id: "missions",
      label: copy("Monitor", "监测"),
      kicker: copy("Monitor", "监测"),
      summary: copy(
        "Keep mission selection and cockpit inspection in one monitoring lane so run posture, recent evidence, and handoff facts stay together.",
        "把任务选择和任务详情收进同一条监测工作线，让执行姿态、近期证据和交接事实保持连贯。"
      ),
      modules: [
        {
          sectionId: "section-board",
          title: copy("Mission Board", "任务列表"),
          summary: copy(
            "Choose the current mission, confirm readiness, and keep due or degraded watches visible without diving into every detail at once.",
            "先选定当前任务，确认就绪度，并把待执行或降级任务保持可见，而不是一开始就展开全部细节。"
          ),
          output: copy("Mission posture, due state, and latest lane status", "任务姿态、待执行状态和最近工作线状态"),
          nextAction: copy("Select one mission", "选中一个任务"),
          cta: copy("Open Mission Board", "打开任务列表"),
        },
        {
          sectionId: "section-cockpit",
          title: copy("Mission Cockpit", "任务详情"),
          summary: copy(
            "Inspect one mission's run history, results, and route handoff facts once it becomes the current work object.",
            "当某个任务成为当前工作对象后，在这里查看它的执行历史、结果和路由交接事实。"
          ),
          output: copy("Latest run outcome and stored results", "最新运行结果和已存储结果"),
          nextAction: copy("Inspect the selected mission", "查看当前任务详情"),
          cta: copy("Open Cockpit", "打开任务详情"),
        },
      ],
      advancedActions: [],
      landingSection: "section-board",
      footnote: copy("Stay on the current mission until the run outcome and next handoff are obvious.", "围绕当前任务工作，直到运行结果和下一步交接都清晰为止。"),
      topbarSubtitle: copy("Monitor | Mission Board -> Cockpit", "监测 | 任务列表 -> 任务详情"),
    },
    review: {
      id: "review",
      label: copy("Review", "审阅"),
      kicker: copy("Review", "审阅"),
      summary: copy(
        "Keep triage and story work first-rank so evidence review can progress before claim composition and report assembly are needed.",
        "把分诊和故事工作保持在第一层级，让证据审阅先完成，再按需进入主张装配和报告编排。"
      ),
      modules: [
        {
          sectionId: "section-triage",
          title: copy("Triage Queue", "分诊队列"),
          summary: copy(
            "Review the inbox and keep the selected evidence workbench visible before promoting anything downstream.",
            "先处理收件队列，并让选中的证据工作台保持可见，再决定是否向下游提升。"
          ),
          output: copy("Queue state and selected evidence", "队列状态和当前证据"),
          nextAction: copy("Verify or promote evidence", "核验或提升证据"),
          cta: copy("Open Triage", "打开分诊"),
        },
        {
          sectionId: "section-story",
          title: copy("Story Workspace", "故事工作台"),
          summary: copy(
            "Keep the promoted story, contradictions, and delivery readiness in one place before editorial packaging begins.",
            "在进入编辑包装前，把已提升故事、冲突点和交付就绪度收进同一个工作台。"
          ),
          output: copy("Promoted story candidate and readiness state", "已提升故事候选和就绪状态"),
          nextAction: copy("Refine the current story", "完善当前故事"),
          cta: copy("Open Story Workspace", "打开故事工作台"),
        },
      ],
      advancedActions: [
        {
          sectionId: "section-claims",
          label: copy("Open Claim Composer", "打开主张装配"),
        },
        {
          sectionId: "section-report-studio",
          label: copy("Open Report Studio", "打开报告工作台"),
        },
      ],
      landingSection: "section-triage",
      footnote: copy("Claims and reports remain available, but they should not compete with the current evidence object by default.", "主张和报告仍然可用，但默认不再与当前证据对象争夺第一层级注意力。"),
      topbarSubtitle: copy("Review | Triage -> Stories -> Advanced Review", "审阅 | 分诊 -> 故事 -> 高级审阅"),
    },
    delivery: {
      id: "delivery",
      label: copy("Deliver", "交付"),
      kicker: copy("Deliver", "交付"),
      summary: copy(
        "Keep route posture, dispatch state, and delivery history first-rank so downstream status stays visible without exposing every diagnostic surface by default.",
        "把路由姿态、分发状态和交付历史保留在第一层级，让下游状态保持可见，而不是默认把所有诊断面板都展开。"
      ),
      modules: [
        {
          sectionId: "section-ops",
          title: copy("Delivery Lane", "交付工作线"),
          summary: copy(
            "Watch route posture, recent alert flow, and dispatch history in one owned delivery surface before opening diagnostics.",
            "先在一个交付面板里查看路由姿态、近期告警流和分发历史，再按需打开诊断视图。"
          ),
          output: copy("Dispatch posture and delivery history", "分发姿态和交付历史"),
          nextAction: copy("Inspect routes or dispatch output", "查看路由或分发输出"),
          cta: copy("Open Delivery Lane", "打开交付工作线"),
        },
      ],
      advancedActions: [
        {
          shellId: "delivery-advanced-shell",
          label: copy("Open AI & Route Health", "打开 AI 与路由健康"),
        },
      ],
      landingSection: "section-ops",
      footnote: copy("Keep delivery diagnostics available on demand instead of leaving them in the default scan path.", "让交付诊断面按需可见，而不是继续留在默认扫描路径上。"),
      topbarSubtitle: copy("Deliver | Route posture -> Dispatch -> History", "交付 | 路由姿态 -> 分发 -> 历史"),
    },
  };
  return descriptors[normalized] || descriptors.intake;
}

function workspaceModeHasPopulation(modeId) {
  const normalizedMode = normalizeWorkspaceMode(modeId);
  if (normalizedMode === "intake") {
    return hasIntakePopulation();
  }
  if (normalizedMode === "missions") {
    return Boolean(state.watches.length || getSelectedWatchForContext());
  }
  if (normalizedMode === "review") {
    return Boolean(
      state.triage.length
      || state.stories.length
      || state.claimCards.length
      || state.reports.length
      || state.selectedTriageId
      || state.selectedStoryId
    );
  }
  return Boolean(
    state.routes.length
    || state.alerts.length
    || state.deliverySubscriptions.length
    || state.deliveryDispatchRecords.length
    || normalizeRouteName(state.contextRouteName)
  );
}

function workspaceModeCurrentObjectLabel(activeSectionId) {
  if (activeSectionId === "section-intake") {
    if (hasIntakePopulation()) {
      const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
      if (selectedWatch) {
        return clampLabel(selectedWatch?.name || selectedWatch?.id || copy("Live mission focus", "实时任务聚焦"), 42);
      }
    }
    const draftName = String(state.createWatchDraft?.name || "").trim();
    const draftQuery = String(state.createWatchDraft?.query || "").trim();
    return clampLabel(draftName || draftQuery || copy("Mission draft not started", "任务草稿尚未开始"), 42);
  }
  if (activeSectionId === "section-board" || activeSectionId === "section-cockpit") {
    const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
    return clampLabel(selectedWatch?.name || selectedWatch?.id || copy("No mission selected", "未选择任务"), 42);
  }
  if (activeSectionId === "section-triage") {
    const triageFocus = state.triage.find((item) => item.id === state.selectedTriageId);
    return clampLabel(triageFocus?.title || triageFocus?.id || copy("No evidence selected", "未选择证据"), 42);
  }
  if (activeSectionId === "section-story") {
    const selectedStory = getStoryRecord(state.selectedStoryId);
    return clampLabel(selectedStory?.title || selectedStory?.id || copy("No story selected", "未选择故事"), 42);
  }
  if (activeSectionId === "section-claims") {
    const selectedClaim = getSelectedClaimCard();
    const selectedReport = getSelectedReportRecord();
    return clampLabel(
      getClaimCardLabel(selectedClaim) || selectedReport?.title || selectedReport?.id || copy("No claim target selected", "未选择主张目标"),
      42,
    );
  }
  if (activeSectionId === "section-report-studio") {
    const selectedReport = getSelectedReportRecord();
    return clampLabel(selectedReport?.title || selectedReport?.id || copy("No report selected", "未选择报告"), 42);
  }
  const selectedSubscription = getSelectedDeliverySubscription();
  const routeName = normalizeRouteName(state.contextRouteName) || selectedSubscription?.route_names?.[0] || state.routes[0]?.name || "";
  return clampLabel(
    summarizeDeliverySubject(selectedSubscription) || routeName || copy("No delivery object selected", "未选择交付对象"),
    42,
  );
}

function workspaceModeOwnedOutputLabel(modeId, activeSectionId) {
  if (modeId === "intake") {
    if (hasIntakePopulation()) {
      return phrase(
        "{missions} live missions | {queue} open triage",
        "{missions} 条实时任务 | {queue} 条待分诊",
        {
          missions: Number(state.overview?.enabled_watches ?? state.watches.filter((watch) => watch.enabled !== false).length ?? 0),
          queue: Number(state.overview?.triage_open_count ?? state.triageStats?.open_count ?? 0),
        },
      );
    }
    const hasRequiredInput = Boolean(String(state.createWatchDraft?.name || "").trim() && String(state.createWatchDraft?.query || "").trim());
    return hasRequiredInput
      ? copy("Mission draft ready to create", "任务草稿已具备创建条件")
      : copy("Waiting for Name + Query", "等待填写名称和查询词");
  }
  if (modeId === "missions") {
    const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
    const resultStats = selectedWatch?.result_stats || state.watchDetails[state.selectedWatchId]?.result_stats || null;
    if (!selectedWatch) {
      return copy("Select one mission to inspect its latest run", "选中一个任务后才能查看它的最新运行结果");
    }
    return phrase(
      "{status} | {count} stored results",
      "{status} | {count} 条已存储结果",
      {
        status: localizeWord(selectedWatch.last_run_status || "waiting"),
        count: Number(resultStats?.stored_result_count || resultStats?.returned_result_count || 0),
      },
    );
  }
  if (modeId === "review") {
    if (activeSectionId === "section-story" || activeSectionId === "section-claims" || activeSectionId === "section-report-studio") {
      const selectedStory = getStoryRecord(state.selectedStoryId);
      const selectedReport = getSelectedReportRecord();
      const quality = getReportComposition(selectedReport?.id || "")?.quality || null;
      if (activeSectionId === "section-story" && selectedStory) {
        return phrase(
          "{status} | {count} evidence items",
          "{status} | {count} 条证据",
          {
            status: localizeWord(selectedStory.status || "active"),
            count: Number(selectedStory.item_count || 0),
          },
        );
      }
      if (selectedReport) {
        return phrase(
          "{status} | {count} sections",
          "{status} | {count} 个章节",
          {
            status: localizeWord(quality?.status || selectedReport.status || "draft"),
            count: getReportSectionsForReport(selectedReport.id).length,
          },
        );
      }
    }
    return phrase(
      "{count} open items in triage",
      "分诊中有 {count} 条待处理项",
      { count: Number(state.triageStats?.open_count || 0) },
    );
  }
  const routeSummary = state.ops?.route_summary || {};
  return phrase(
    "{healthy} healthy routes | {alerts} alerts",
    "{healthy} 条健康路由 | {alerts} 条告警",
    {
      healthy: Number(routeSummary.healthy || 0),
      alerts: Number(state.alerts.length || 0),
    },
  );
}

function workspaceModeNextActionLabel(modeId, activeSectionId) {
  if (modeId === "intake") {
    if (hasIntakePopulation()) {
      const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
      return selectedWatch
        ? copy("Open Cockpit for the current mission", "打开当前任务详情")
        : copy("Open the mission board", "打开任务列表");
    }
    const hasRequiredInput = Boolean(String(state.createWatchDraft?.name || "").trim() && String(state.createWatchDraft?.query || "").trim());
    return hasRequiredInput
      ? copy("Create the mission", "创建任务")
      : copy("Fill the required mission input", "补全任务必填信息");
  }
  if (modeId === "missions") {
    return state.selectedWatchId
      ? copy("Open Cockpit or run the mission", "打开任务详情或立即执行任务")
      : copy("Select one mission from the board", "先从列表选中一个任务");
  }
  if (modeId === "review") {
    if (activeSectionId === "section-claims" || activeSectionId === "section-report-studio") {
      return getSelectedReportRecord()
        ? copy("Refresh composition or attach claims", "刷新编排或挂接主张")
        : copy("Choose a report target first", "先选择一个报告目标");
    }
    return state.selectedStoryId
      ? copy("Refine the story and confirm readiness", "完善故事并确认交付就绪度")
      : (state.selectedTriageId
          ? copy("Verify or promote the selected evidence", "核验或提升当前证据")
          : copy("Pick one evidence item from triage", "先从分诊队列选中一条证据"));
  }
  return state.routes.length
    ? copy("Inspect route posture or dispatch current output", "查看路由姿态或分发当前输出")
    : copy("Create a named route", "创建一个命名路由");
}

function workspaceModeContinuityFacts(modeId, activeSectionId, ownedOutput) {
  const normalizedMode = normalizeWorkspaceMode(modeId);
  const facts = [
    { label: copy("Surface", "视图"), value: activeSectionLabel(activeSectionId) },
    { label: copy("Owned output", "阶段产出"), value: ownedOutput },
  ];
  if (normalizedMode === "intake") {
    facts.push(
      { label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? 0) },
      { label: copy("Routes", "路由数"), value: String(state.overview?.route_count ?? state.routes.length ?? 0) },
    );
    return facts;
  }
  if (normalizedMode === "missions") {
    facts.push(
      { label: copy("Due now", "当前待执行"), value: String(state.overview?.due_watches ?? 0) },
      { label: copy("Open queue", "待分诊"), value: String(state.overview?.triage_open_count ?? state.triageStats?.open_count ?? 0) },
    );
    return facts;
  }
  if (normalizedMode === "review") {
    facts.push(
      { label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? 0) },
      { label: copy("Reports", "报告"), value: String(state.reports.length || 0) },
    );
    return facts;
  }
  facts.push(
    { label: copy("Healthy routes", "健康路由"), value: String(state.ops?.route_summary?.healthy ?? 0) },
    { label: copy("Alerts", "告警数"), value: String(state.alerts.length || 0) },
  );
  return facts;
}

function workspaceModeActionHierarchy(modeId, activeSectionId) {
  const normalizedMode = normalizeWorkspaceMode(modeId);
  if (normalizedMode === "intake") {
    if (!hasIntakePopulation()) {
      const hasRequiredInput = Boolean(String(state.createWatchDraft?.name || "").trim() && String(state.createWatchDraft?.query || "").trim());
      return {
        primary: hasRequiredInput
          ? { label: copy("Create Mission", "创建任务"), attrs: { "data-empty-focus": "mission", "data-empty-field": "name" } }
          : { label: copy("Focus Mission Draft", "聚焦任务草稿"), attrs: { "data-empty-focus": "mission", "data-empty-field": "name" } },
        secondary: [],
      };
    }
    const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
    return {
      primary: selectedWatch
        ? { label: copy("Open Cockpit", "打开任务详情"), attrs: { "data-empty-jump": "section-cockpit" } }
        : { label: copy("Open Mission Board", "打开任务列表"), attrs: { "data-empty-jump": "section-board" } },
      secondary: [
        { label: copy("Open Triage", "打开分诊"), attrs: { "data-empty-jump": "section-triage" } },
        { label: copy("Focus Mission Draft", "聚焦任务草稿"), attrs: { "data-empty-focus": "mission", "data-empty-field": "name" } },
      ],
    };
  }
  if (normalizedMode === "missions") {
    const selectedWatch = getSelectedWatchForContext() || null;
    return {
      primary: selectedWatch
        ? (
            activeSectionId === "section-cockpit" && selectedWatch.enabled !== false
              ? { label: copy("Run Mission", "执行任务"), attrs: { "data-empty-run-watch": selectedWatch.id } }
              : activeSectionId === "section-cockpit" && selectedWatch.enabled === false
                ? { label: copy("Enable Mission", "启用任务"), attrs: { "data-watch-toggle": selectedWatch.id, "data-watch-enabled": "0" } }
                : { label: copy("Open Cockpit", "打开任务详情"), attrs: { "data-empty-jump": "section-cockpit" } }
          )
        : { label: copy("Open Mission Board", "打开任务列表"), attrs: { "data-empty-jump": "section-board" } },
      secondary: [
        { label: copy("Open Triage", "打开分诊"), attrs: { "data-empty-jump": "section-triage" } },
      ],
    };
  }
  if (normalizedMode === "review") {
    const selectedStory = getStoryRecord(state.selectedStoryId);
    return {
      primary: selectedStory
        ? {
            label: copy("Open Story Editor", "打开故事编辑"),
            attrs: { "data-empty-jump": "section-story", "data-story-workspace-mode": "editor" },
          }
        : { label: copy("Open Triage", "打开分诊"), attrs: { "data-empty-jump": "section-triage" } },
      secondary: [
        { label: copy("Open Story Workspace", "打开故事工作台"), attrs: { "data-empty-jump": "section-story" } },
        { label: copy("Open Report Studio", "打开报告工作台"), attrs: { "data-empty-jump": "section-report-studio" } },
      ],
    };
  }
  if (!state.routes.length) {
    return {
      primary: { label: copy("Focus Route Draft", "聚焦路由草稿"), attrs: { "data-empty-focus": "route", "data-empty-field": "name" } },
      secondary: [],
    };
  }
  return {
    primary: { label: copy("Open Delivery Lane", "打开交付工作线"), attrs: { "data-empty-jump": "section-ops" } },
    secondary: [
      { label: copy("Focus Route Draft", "聚焦路由草稿"), attrs: { "data-empty-focus": "route", "data-empty-field": "name" } },
    ],
  };
}

function syncAdvancedSurfaceShells() {
  const activeSectionId = normalizeSectionId(state.activeSectionId);
  const reviewShell = $("review-advanced-shell");
  if (reviewShell instanceof HTMLDetailsElement) {
    if (reviewAdvancedSectionIds.includes(activeSectionId)) {
      reviewShell.open = true;
    } else if (state.activeWorkspaceMode !== "review") {
      reviewShell.open = false;
    }
  }
  const deliveryShell = $("delivery-advanced-shell");
  if (deliveryShell instanceof HTMLDetailsElement && state.activeWorkspaceMode !== "delivery") {
    deliveryShell.open = false;
  }
}

function openAdvancedSurfaceShell(shellId) {
  const shell = $(shellId);
  if (!(shell instanceof HTMLElement)) {
    return;
  }
  if (shell instanceof HTMLDetailsElement) {
    shell.open = true;
  }
  shell.scrollIntoView({ block: "start", behavior: "smooth" });
}

function renderWorkspaceModeShell() {
  const root = $("workspace-mode-shell");
  if (!root) {
    return;
  }
  const activeSectionId = normalizeSectionId(state.activeSectionId);
  const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode);
  const currentObject = workspaceModeCurrentObjectLabel(activeSectionId);
  const ownedOutput = workspaceModeOwnedOutputLabel(modeDescriptor.id, activeSectionId);
  const nextAction = workspaceModeNextActionLabel(modeDescriptor.id, activeSectionId);
  const hasPopulation = workspaceModeHasPopulation(modeDescriptor.id);
  const continuityFacts = workspaceModeContinuityFacts(modeDescriptor.id, activeSectionId, ownedOutput);
  const actionHierarchy = workspaceModeActionHierarchy(modeDescriptor.id, activeSectionId);
  const compactObjectFacts = continuityFacts.map((fact) => {
    const hasValue = ![null, undefined].includes(fact?.value) && String(fact.value).trim() !== "";
    return `
      <div class="continuity-fact workspace-mode-module">
        <span>${escapeHtml(fact?.label || "")}</span>
        <strong>${escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}</strong>
      </div>
    `;
  }).join("");
  const compactObjectActions = actionHierarchy?.primary ? renderCardActionHierarchy({ primary: actionHierarchy.primary }) : "";
  const cards = Array.isArray(modeDescriptor.modules) ? modeDescriptor.modules : [];
  const advancedActions = Array.isArray(modeDescriptor.advancedActions) ? modeDescriptor.advancedActions : [];
  const traceCard = renderStageLinkedTraceCard();
  const sharedSignalCard = renderSharedSignalTaxonomyCard();
  const advancedActionMarkup = advancedActions.length
    ? `
      <div class="actions workspace-mode-actions">
        ${advancedActions.map((action) => action.sectionId
          ? `<button class="btn-secondary" type="button" data-workspace-jump="${escapeHtml(action.sectionId)}">${escapeHtml(action.label)}</button>`
          : `<button class="btn-secondary" type="button" data-workspace-advanced-open="${escapeHtml(action.shellId || "")}">${escapeHtml(action.label)}</button>`
        ).join("")}
      </div>
    `
    : "";

  root.hidden = false;
  root.dataset.workspaceChrome = hasPopulation ? "compact" : "default";
  root.innerHTML = `
    <div class="workspace-mode-head">
      <div class="workspace-mode-summary">
        <div class="workspace-mode-kicker">${escapeHtml(modeDescriptor.kicker)}</div>
        <div class="workspace-mode-title">${escapeHtml(modeDescriptor.label)}</div>
        <div class="workspace-mode-copy">${escapeHtml(modeDescriptor.summary)}</div>
      </div>
      ${
        hasPopulation
          ? `
            <div class="workspace-mode-object-anchor" data-workspace-object-anchor="true">
              <div class="workspace-mode-object-head">
                <div>
                  <div class="workspace-mode-object-kicker">${copy("Current object", "当前对象")}</div>
                  <div class="workspace-mode-object-title">${escapeHtml(currentObject)}</div>
                </div>
                <span class="chip ok">${escapeHtml(activeSectionLabel(activeSectionId))}</span>
              </div>
              <div class="workspace-mode-object-copy">${escapeHtml(nextAction)}</div>
              <div class="workspace-mode-modules continuity-fact-list">${compactObjectFacts}</div>
              ${compactObjectActions}
            </div>
          `
          : `
            <div class="workspace-mode-meta">
              <span class="chip">${copy("Current surface", "当前视图")}: ${escapeHtml(activeSectionLabel(activeSectionId))}</span>
              <span class="chip ok">${copy("Current object", "当前对象")}: ${escapeHtml(currentObject)}</span>
              <span class="chip">${copy("Owned output", "阶段产出")}: ${escapeHtml(ownedOutput)}</span>
              <span class="chip hot">${copy("Next action", "下一步动作")}: ${escapeHtml(nextAction)}</span>
            </div>
          `
      }
    </div>
    <div class="workspace-mode-insight-grid">
      ${traceCard}
      ${sharedSignalCard}
    </div>
    <div class="workspace-mode-grid">
      ${cards.map((card) => {
        const sectionId = normalizeSectionId(card.sectionId || modeDescriptor.landingSection);
        const active = sectionId === activeSectionId;
        return `
          <button class="workspace-mode-card ${active ? "active" : ""}" type="button" data-workspace-jump="${sectionId}">
            <div class="workspace-mode-card-head">
              <div>
                <div class="workspace-mode-kicker">${escapeHtml(modeDescriptor.label)}</div>
                <div class="workspace-mode-title">${escapeHtml(card.title || activeSectionLabel(sectionId))}</div>
              </div>
              <span class="chip ${active ? "ok" : ""}">${active ? copy("Current", "当前") : copy("Open", "打开")}</span>
            </div>
            <div class="workspace-mode-copy">${escapeHtml(card.summary || "")}</div>
            <div class="workspace-mode-modules">
              <span class="workspace-mode-module">${copy("Owned output", "阶段产出")} · ${escapeHtml(card.output || "")}</span>
              <span class="workspace-mode-module">${copy("Next action", "下一步动作")} · ${escapeHtml(card.nextAction || "")}</span>
            </div>
            <div class="workspace-mode-foot">
              <span>${copy("Surface", "视图")} · ${escapeHtml(activeSectionLabel(sectionId))}</span>
              <span>${escapeHtml(card.cta || copy("Open surface", "打开视图"))}</span>
            </div>
          </button>
        `;
      }).join("")}
    </div>
    <div class="workspace-mode-foot">
      <span>${escapeHtml(modeDescriptor.footnote)}</span>
      ${advancedActionMarkup}
    </div>
  `;
  root.querySelectorAll("[data-workspace-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      jumpToSection(String(button.dataset.workspaceJump || "").trim());
    });
  });
  root.querySelectorAll("[data-workspace-advanced-open]").forEach((button) => {
    button.addEventListener("click", () => {
      openAdvancedSurfaceShell(String(button.dataset.workspaceAdvancedOpen || "").trim());
    });
  });
  root.querySelectorAll("[data-shared-signal-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const signalId = String(button.dataset.sharedSignalButton || "").trim();
      if (!signalId) {
        return;
      }
      state.sharedSignalFocus = signalId;
      renderWorkspaceModeShell();
    });
  });
  wireLifecycleGuideActions(root);
  scheduleCanvasTextFit(root);
}

function renderWorkspaceModeChrome() {
  const activeSectionId = normalizeSectionId(state.activeSectionId);
  state.activeSectionId = activeSectionId;
  state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
  const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode);
  document.querySelectorAll("[data-workspace-group]").forEach((group) => {
    const groupMode = normalizeWorkspaceMode(group.dataset.workspaceGroup || "");
    group.hidden = groupMode !== modeDescriptor.id;
  });
  document.querySelectorAll(".topbar-nav [data-jump-target]").forEach((button) => {
    const buttonMode = normalizeWorkspaceMode(button.dataset.workspaceMode || workspaceModeForSection(button.dataset.jumpTarget || ""));
    const active = buttonMode === modeDescriptor.id;
    button.hidden = false;
    button.classList.toggle("active", active);
    button.setAttribute("aria-current", active ? "page" : "false");
  });
  setText("topbar-subtitle", modeDescriptor.topbarSubtitle);
  syncAdvancedSurfaceShells();
  renderWorkspaceModeShell();
}

state.activeWorkspaceMode = workspaceModeForSection(state.activeSectionId);

function contextLensEmptyValue() {
  return copy("Not set", "未设置");
}

function buildTopbarContextDescriptor() {
  const activeSectionId = normalizeSectionId(state.activeSectionId);
  state.activeSectionId = activeSectionId;
  state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
  const descriptor = {
    modeId: state.activeWorkspaceMode,
    modeLabel: workspaceModeDescriptor(state.activeWorkspaceMode).label,
    sectionId: activeSectionId,
    sectionLabel: activeSectionLabel(activeSectionId),
    detail: "",
    rows: [],
  };
  const pushRow = (label, value, { mono = false, muted = false } = {}) => {
    const hasValue = ![null, undefined].includes(value) && String(value).trim() !== "";
    descriptor.rows.push({
      label,
      value: hasValue ? String(value).trim() : contextLensEmptyValue(),
      className: [
        mono ? "mono" : "",
        !hasValue || muted ? "muted" : "",
      ].filter(Boolean).join(" "),
    });
  };
  pushRow(copy("Rail", "主轨"), descriptor.modeLabel);

  if (activeSectionId === "section-intake") {
    const draftName = String(state.createWatchDraft?.name || "").trim();
    const draftQuery = String(state.createWatchDraft?.query || "").trim();
    descriptor.detail = draftName || draftQuery
      ? clampLabel(draftName || draftQuery, 28)
      : copy("mission intake", "任务录入");
    pushRow(copy("Mode", "模式"), String(state.createWatchEditingId || "").trim() ? copy("Editing mission", "编辑任务") : copy("New mission", "新建任务"));
    pushRow(copy("Name", "名称"), clampLabel(draftName, 52));
    pushRow(copy("Query", "查询词"), clampLabel(draftQuery, 72), { mono: true });
    pushRow(copy("Schedule", "频率"), String(state.createWatchDraft?.schedule || "").trim() || "manual", { mono: true });
  } else if (activeSectionId === "section-board" || activeSectionId === "section-cockpit") {
    const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
    const watchLabel = selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 28) : "";
    const watchSearch = String(state.watchSearch || "").trim();
    descriptor.detail = watchSearch
      ? phrase("q={query}", "搜索={query}", { query: clampLabel(watchSearch, 20) })
      : (watchLabel || copy("mission focus", "任务聚焦"));
    pushRow(copy("Mission", "任务"), selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 52) : "");
    pushRow(copy("Search", "搜索"), clampLabel(watchSearch, 52), { mono: true });
    pushRow(copy("Schedule", "频率"), String(selectedWatch?.schedule_label || selectedWatch?.schedule || "").trim(), { mono: true });
    pushRow(copy("Alerts", "告警"), selectedWatch ? String(selectedWatch.alert_rule_count || (Array.isArray(selectedWatch.alert_rules) ? selectedWatch.alert_rules.length : 0) || 0) : "", { mono: true });
  } else if (activeSectionId === "section-triage") {
    const triageFocus = state.triage.find((item) => item.id === state.selectedTriageId);
    const triageSearch = String(state.triageSearch || "").trim();
    if (state.triagePinnedIds.length) {
      descriptor.detail = phrase("evidence x{count}", "证据 x{count}", { count: state.triagePinnedIds.length });
    } else if (triageSearch) {
      descriptor.detail = phrase("{filter} | {query}", "{filter} | {query}", {
        filter: localizeWord(state.triageFilter || "open"),
        query: clampLabel(triageSearch, 18),
      });
    } else {
      descriptor.detail = triageFocus
        ? clampLabel(triageFocus.title || triageFocus.id, 28)
        : localizeWord(state.triageFilter || "open");
    }
    pushRow(copy("Queue", "队列"), localizeWord(state.triageFilter || "open"));
    pushRow(copy("Search", "搜索"), clampLabel(triageSearch, 52), { mono: true });
    pushRow(copy("Selected", "当前条目"), triageFocus ? clampLabel(triageFocus.title || triageFocus.id, 52) : "");
    pushRow(copy("Evidence focus", "证据聚焦"), state.triagePinnedIds.length ? phrase("{count} linked items", "{count} 个关联条目", { count: state.triagePinnedIds.length }) : "");
    pushRow(copy("Batch", "批量"), state.selectedTriageIds.length ? phrase("{count} selected", "{count} 个已选", { count: state.selectedTriageIds.length }) : "");
  } else if (activeSectionId === "section-story") {
    const activeStoryView = detectStoryViewPreset({
      filter: state.storyFilter,
      sort: state.storySort,
      search: state.storySearch,
    });
    const selectedStory = getStoryRecord(state.selectedStoryId);
    const storySearch = String(state.storySearch || "").trim();
    descriptor.detail = storySearch
      ? phrase("{view} | {query}", "{view} | {query}", {
        view: storyViewPresetLabel(activeStoryView),
        query: clampLabel(storySearch, 18),
      })
      : (selectedStory
          ? phrase("{view} | {title}", "{view} | {title}", {
              view: storyViewPresetLabel(activeStoryView),
              title: clampLabel(selectedStory.title || selectedStory.id, 18),
            })
          : storyViewPresetLabel(activeStoryView));
    pushRow(copy("View", "视图"), storyViewPresetLabel(activeStoryView));
    pushRow(
      copy("Workspace Mode", "工作区模式"),
      state.storyWorkspaceMode === "editor" ? copy("Editor", "编辑") : copy("Board", "看板"),
    );
    pushRow(copy("Sort", "排序"), storySortLabel(state.storySort));
    pushRow(copy("Search", "搜索"), clampLabel(storySearch, 52), { mono: true });
    pushRow(copy("Selected", "当前故事"), selectedStory ? clampLabel(selectedStory.title || selectedStory.id, 52) : "");
    pushRow(copy("Batch", "批量"), state.selectedStoryIds.length ? phrase("{count} selected", "{count} 个已选", { count: state.selectedStoryIds.length }) : "");
  } else if (activeSectionId === "section-claims") {
    const selectedReport = getSelectedReportRecord();
    const selectedSection = getSelectedReportSectionRecord();
    const selectedClaim = getSelectedClaimCard();
    const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
    descriptor.detail = selectedClaim
      ? clampLabel(getClaimCardLabel(selectedClaim), 28)
      : (selectedReport
          ? phrase("report={title}", "报告={title}", { title: clampLabel(selectedReport.title || selectedReport.id, 18) })
          : copy("claim composition", "主张装配"));
    pushRow(copy("Report", "报告"), selectedReport ? clampLabel(selectedReport.title || selectedReport.id, 52) : "");
    pushRow(copy("Section", "章节"), selectedSection ? clampLabel(selectedSection.title || selectedSection.id, 52) : "");
    pushRow(copy("Claim", "主张"), selectedClaim ? clampLabel(getClaimCardLabel(selectedClaim), 72) : "");
    pushRow(copy("Quality", "质量"), selectedQuality ? `${localizeWord(selectedQuality.status || "draft")} / ${Number(selectedQuality.score || 0).toFixed(2)}` : "");
  } else if (activeSectionId === "section-report-studio") {
    const selectedReport = getSelectedReportRecord();
    const selectedComposition = getReportComposition(selectedReport?.id || "");
    const selectedQuality = selectedComposition?.quality || null;
    const reportSections = getReportSectionsForReport(selectedReport?.id || "");
    const reportClaimIds = getReportClaimIds(selectedReport?.id || "");
    descriptor.detail = selectedReport
      ? clampLabel(selectedReport.title || selectedReport.id, 28)
      : copy("report studio", "报告工作台");
    pushRow(copy("Report", "报告"), selectedReport ? clampLabel(selectedReport.title || selectedReport.id, 52) : "");
    pushRow(copy("Audience", "受众"), selectedReport ? clampLabel(selectedReport.audience || "", 52) : "");
    pushRow(copy("Sections", "章节"), selectedReport ? String(reportSections.length) : "", { mono: true });
    pushRow(copy("Claims", "主张"), selectedReport ? String(reportClaimIds.length) : "", { mono: true });
    pushRow(copy("Quality", "质量"), selectedQuality ? `${localizeWord(selectedQuality.status || "draft")} / ${Number(selectedQuality.score || 0).toFixed(2)}` : "");
  } else if (activeSectionId === "section-ops") {
    const daemonState = String(state.status?.state || "").trim();
    const routeSummary = state.ops?.route_summary || {};
    descriptor.detail = copy("health and delivery", "健康与交付");
    pushRow(copy("Daemon", "守护进程"), daemonState ? localizeWord(daemonState) : "");
    pushRow(copy("Routes", "路由"), String(state.routes.length || 0), { mono: true });
    pushRow(copy("Healthy", "健康"), String(routeSummary.healthy || 0), { mono: true });
    pushRow(copy("Alerts", "告警"), String(state.alerts.length || 0), { mono: true });
  }

  descriptor.summary = descriptor.detail
    ? `${descriptor.modeLabel} / ${descriptor.sectionLabel} | ${descriptor.detail}`
    : `${descriptor.modeLabel} / ${descriptor.sectionLabel}`;
  return descriptor;
}

function buildCurrentContextLinkRecord(descriptor = buildTopbarContextDescriptor()) {
  const url = new URL(window.location.href);
  url.hash = descriptor.sectionId ? `#${descriptor.sectionId}` : "";
  return normalizeContextLinkHistoryEntry({
    url: `${url.pathname}${url.search}${url.hash}`,
    summary: descriptor.summary,
    sectionId: descriptor.sectionId,
    timestamp: new Date().toISOString(),
  });
}

function renderContextViewDock() {
  const root = $("context-view-dock");
  if (!root) {
    return;
  }
  const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry, index) => ({ entry: normalizeContextSavedViewEntry(entry), index }))
    .filter(({ entry }) => entry && entry.pinned)
    .slice(0, 4);
  if (!entries.length) {
    root.hidden = true;
    root.innerHTML = "";
    return;
  }
  root.hidden = false;
  root.innerHTML = `
    <div class="context-dock-strip">
      ${entries.map(({ entry, index }) => `
        <button
          class="btn-secondary context-dock-pill"
          type="button"
          data-context-dock-open="${index}"
          data-fit-text="context-dock-pill"
          data-fit-fallback="18"
        >${escapeHtml(entry.name)}</button>
      `).join("")}
      <button class="btn-secondary context-dock-manage" type="button" data-context-dock-manage>${copy("Manage Views", "管理视图")}</button>
    </div>
  `;
  root.querySelectorAll("[data-context-dock-open]").forEach((button) => {
    button.addEventListener("click", () => {
      state.contextLensRestoreFocusId = "context-summary";
      restoreContextSavedViewEntry(Number(button.dataset.contextDockOpen || -1));
    });
  });
  root.querySelector("[data-context-dock-manage]")?.addEventListener("click", () => {
    state.contextLensRestoreFocusId = "context-summary";
    setContextLensOpen(true);
  });
  scheduleCanvasTextFit(root);
}

function renderContextSavedViews() {
  const root = $("context-lens-saved");
  if (!root) {
    return;
  }
  const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .filter(Boolean)
    .slice(0, 8);
  const pinnedIndexes = entries
    .map((entry, index) => (entry.pinned ? index : -1))
    .filter((index) => index >= 0);
  root.innerHTML = `
    <div class="context-lens-history-head">
      <div class="context-lens-history-title">${copy("Saved Views", "已保存视图")}</div>
      ${entries.length ? `<button class="btn-secondary" type="button" data-context-saved-clear>${copy("Clear", "清空")}</button>` : ""}
    </div>
    ${entries.length
      ? `<div class="context-lens-history-list">
          ${entries.map((entry, index) => {
            const pinnedPosition = pinnedIndexes.indexOf(index);
            const canMoveLeft = pinnedPosition > 0;
            const canMoveRight = pinnedPosition >= 0 && pinnedPosition < pinnedIndexes.length - 1;
            return `
            <div class="context-history-item">
              <div class="context-history-summary">${escapeHtml(entry.name)}</div>
              <div class="context-history-meta">
                <span>${escapeHtml(activeSectionLabel(entry.sectionId))}</span>
                <span>${escapeHtml(formatCompactDateTime(entry.timestamp))}</span>
                ${entry.isDefault ? `<span class="chip ok">${copy("Default", "默认")}</span>` : ""}
                ${entry.pinned ? `<span class="chip">${copy("Pinned", "已固定")}</span>` : ""}
              </div>
              <div class="panel-sub">${escapeHtml(entry.summary)}</div>
              <div class="context-history-url">${escapeHtml(clampLabel(entry.url, 96))}</div>
              <div class="context-history-actions">
                <button class="btn-secondary" type="button" data-context-saved-open="${index}">${copy("Open", "打开")}</button>
                <button class="btn-secondary" type="button" data-context-saved-copy="${index}">${copy("Copy", "复制")}</button>
                <button class="btn-secondary" type="button" data-context-saved-pin="${index}">${entry.pinned ? copy("Unpin", "取消固定") : copy("Pin", "固定")}</button>
                ${entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-left="${index}" ${canMoveLeft ? "" : "disabled"}>${copy("Move Left", "左移")}</button>` : ""}
                ${entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-right="${index}" ${canMoveRight ? "" : "disabled"}>${copy("Move Right", "右移")}</button>` : ""}
                <button class="btn-secondary" type="button" data-context-saved-default="${index}">${entry.isDefault ? copy("Clear Default", "取消默认") : copy("Set Default", "设为默认")}</button>
                <button class="btn-secondary" type="button" data-context-saved-delete="${index}">${copy("Delete", "删除")}</button>
              </div>
            </div>
          `;
          }).join("")}
        </div>`
      : `<div class="empty">${copy("No saved view yet. Name one above and it will stay here.", "还没有保存视图。给上面的当前视图起个名字，它就会保留在这里。")}</div>`}
  `;
  root.querySelector("[data-context-saved-clear]")?.addEventListener("click", () => {
    clearContextSavedViews();
  });
  root.querySelectorAll("[data-context-saved-open]").forEach((button) => {
    button.addEventListener("click", () => {
      restoreContextSavedViewEntry(Number(button.dataset.contextSavedOpen || -1));
    });
  });
  root.querySelectorAll("[data-context-saved-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      await copyContextSavedViewEntry(Number(button.dataset.contextSavedCopy || -1));
    });
  });
  root.querySelectorAll("[data-context-saved-pin]").forEach((button) => {
    button.addEventListener("click", () => {
      toggleContextSavedViewPinned(Number(button.dataset.contextSavedPin || -1));
    });
  });
  root.querySelectorAll("[data-context-saved-move-left]").forEach((button) => {
    button.addEventListener("click", () => {
      moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveLeft || -1), "left");
    });
  });
  root.querySelectorAll("[data-context-saved-move-right]").forEach((button) => {
    button.addEventListener("click", () => {
      moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveRight || -1), "right");
    });
  });
  root.querySelectorAll("[data-context-saved-default]").forEach((button) => {
    button.addEventListener("click", () => {
      setDefaultContextSavedView(Number(button.dataset.contextSavedDefault || -1));
    });
  });
  root.querySelectorAll("[data-context-saved-delete]").forEach((button) => {
    button.addEventListener("click", () => {
      deleteContextSavedView(Number(button.dataset.contextSavedDelete || -1));
    });
  });
}

function renderContextLinkHistory() {
  const root = $("context-lens-history");
  if (!root) {
    return;
  }
  const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
    .map((entry) => normalizeContextLinkHistoryEntry(entry))
    .filter(Boolean)
    .slice(0, 6);
  root.innerHTML = `
    <div class="context-lens-history-head">
      <div class="context-lens-history-title">${copy("Recently Shared", "最近分享")}</div>
      ${entries.length ? `<button class="btn-secondary" type="button" data-context-history-clear>${copy("Clear", "清空")}</button>` : ""}
    </div>
    ${entries.length
      ? `<div class="context-lens-history-list">
          ${entries.map((entry, index) => `
            <div class="context-history-item">
              <div class="context-history-summary">${escapeHtml(entry.summary)}</div>
              <div class="context-history-meta">
                <span>${escapeHtml(activeSectionLabel(entry.sectionId))}</span>
                <span>${escapeHtml(formatCompactDateTime(entry.timestamp))}</span>
              </div>
              <div class="context-history-url">${escapeHtml(clampLabel(entry.url, 96))}</div>
              <div class="context-history-actions">
                <button class="btn-secondary" type="button" data-context-history-open="${index}">${copy("Open", "打开")}</button>
                <button class="btn-secondary" type="button" data-context-history-copy="${index}">${copy("Copy", "复制")}</button>
              </div>
            </div>
          `).join("")}
        </div>`
      : `<div class="empty">${copy("No shared context yet. Copy a deep link and it will appear here.", "还没有分享上下文。复制一次深链后，这里就会出现。")}</div>`}
  `;
  root.querySelector("[data-context-history-clear]")?.addEventListener("click", () => {
    clearContextLinkHistory();
  });
  root.querySelectorAll("[data-context-history-open]").forEach((button) => {
    button.addEventListener("click", () => {
      restoreContextLinkHistoryEntry(Number(button.dataset.contextHistoryOpen || -1));
    });
  });
  root.querySelectorAll("[data-context-history-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      await copyContextLinkHistoryEntry(Number(button.dataset.contextHistoryCopy || -1));
    });
  });
}

function syncContextLensChrome() {
  const summary = $("context-summary");
  const lens = $("context-lens");
  const backdrop = $("context-lens-backdrop");
  const lensOpen = Boolean(state.contextLensOpen);
  if (summary) {
    summary.setAttribute("aria-expanded", lensOpen ? "true" : "false");
  }
  if (document.body) {
    document.body.dataset.contextLensOpen = lensOpen ? "true" : "false";
  }
  if (backdrop) {
    backdrop.hidden = !lensOpen;
    backdrop.classList.toggle("open", lensOpen);
  }
  if (lens) {
    lens.hidden = !lensOpen;
    lens.setAttribute("aria-hidden", lensOpen ? "false" : "true");
  }
}

function renderContextLens(descriptor = buildTopbarContextDescriptor()) {
  const body = $("context-lens-body");
  if (!body) {
    return;
  }
  renderContextObjectRail();
  body.innerHTML = descriptor.rows.length
    ? descriptor.rows.map((row) => `
        <div class="context-lens-row">
          <div class="context-lens-label">${escapeHtml(row.label)}</div>
          <div class="context-lens-value ${escapeHtml(row.className || "")}">${escapeHtml(row.value)}</div>
        </div>
      `).join("")
    : `<div class="empty">${copy("No active workspace context.", "当前没有工作上下文。")}</div>`;
  renderContextSavedViews();
  renderContextLinkHistory();
}

function getContextLensFocusableElements() {
  const shell = $("context-lens-shell");
  if (!shell) {
    return [];
  }
  return Array.from(shell.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
    .filter((element) => !element.hasAttribute("hidden") && element.getAttribute("aria-hidden") !== "true");
}

function setContextLensOpen(nextOpen) {
  state.contextLensOpen = Boolean(nextOpen);
  const shell = $("context-lens-shell");
  syncContextLensChrome();
  if (state.contextLensOpen) {
    renderContextLens();
    window.setTimeout(() => {
      shell?.focus();
    }, 10);
    return;
  }
  window.setTimeout(() => {
    $(state.contextLensRestoreFocusId || "context-summary")?.focus();
  }, 0);
}

function toggleContextLens() {
  setContextLensOpen(!state.contextLensOpen);
}

function applyWorkspaceUrlStateFromLocation({ jump = true } = {}) {
  state.watchSearch = "";
  state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
  state.watchResultFilters = {};
  state.watchUrlFocusPending = false;

  state.triageFilter = "open";
  state.triageSearch = "";
  state.triagePinnedIds = [];
  state.selectedTriageIds = [];
  state.selectedTriageId = "";
  state.triageUrlFocusPending = false;

  state.storySearch = "";
  state.storyWorkspaceMode = "board";
  state.storyFilter = "all";
  state.storySort = "attention";
  state.selectedStoryIds = [];
  state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
  state.storyUrlFocusPending = false;

  applyWatchUrlStateFromLocation();
  applyTriageUrlStateFromLocation();
  applyStoryUrlStateFromLocation();
  state.storyWorkspaceMode = normalizeStoryWorkspaceMode(state.storyWorkspaceMode);
  applyStoryWorkspaceMode(state.storyWorkspaceMode, { persist: false });
  setContextRouteFromWatch();
  persistStoryWorkspacePrefs();
  state.activeSectionId = normalizeSectionId(window.location.hash || "section-intake");
  renderWatches();
  renderWatchDetail();
  renderTriage();
  renderStories();
  renderClaimsWorkspace();
  renderReportStudio();
  renderWorkspaceModeChrome();
  renderTopbarContext();
  const hasFocusedSection = state.watchUrlFocusPending || state.triageUrlFocusPending || state.storyUrlFocusPending;
  if (state.watchUrlFocusPending) {
    flushWatchUrlFocus();
  }
  if (state.triageUrlFocusPending) {
    flushTriageUrlFocus();
  }
  if (state.storyUrlFocusPending) {
    flushStoryUrlFocus();
  }
  if (jump && !hasFocusedSection) {
    window.setTimeout(() => {
      jumpToSection(state.activeSectionId, { updateHash: false });
    }, 0);
  }
}

async function copyContextLinkRecord(entry, { toastMessage = "" } = {}) {
  const normalized = normalizeContextLinkHistoryEntry(entry);
  if (!normalized) {
    return;
  }
  const href = new URL(normalized.url, window.location.origin).href;
  try {
    if (window.navigator.clipboard?.writeText) {
      await window.navigator.clipboard.writeText(href);
    } else {
      const helper = document.createElement("textarea");
      helper.value = href;
      helper.setAttribute("readonly", "readonly");
      helper.style.position = "absolute";
      helper.style.left = "-9999px";
      document.body.appendChild(helper);
      helper.select();
      document.execCommand("copy");
      document.body.removeChild(helper);
    }
    noteContextLinkHistory({
      ...normalized,
      timestamp: new Date().toISOString(),
    });
    renderTopbarContext();
    showToast(toastMessage || copy("Context link copied", "已复制当前上下文链接"), "success");
  } catch (error) {
    reportError(error, copy("Copy context link", "复制上下文链接"));
  }
}

async function copyCurrentContextLink() {
  await copyContextLinkRecord(buildCurrentContextLinkRecord());
}

async function copyContextSavedViewEntry(entryIndex) {
  const entry = normalizeContextSavedViewEntry(state.contextSavedViews[Number(entryIndex)]);
  if (!entry) {
    return;
  }
  await copyContextLinkRecord(entry, {
    toastMessage: copy("Saved view link copied", "已复制保存视图链接"),
  });
}

async function copyContextLinkHistoryEntry(entryIndex) {
  const entry = state.contextLinkHistory[Number(entryIndex)];
  if (!entry) {
    return;
  }
  await copyContextLinkRecord(entry, {
    toastMessage: copy("Shared context link copied", "已复制分享上下文链接"),
  });
}

function restoreContextLinkRecord(entry, toastMessage, { noteHistory = true, closeLens = true, showToastMessage = true } = {}) {
  const normalized = normalizeContextLinkHistoryEntry(entry);
  if (!normalized) {
    return;
  }
  const target = new URL(normalized.url, window.location.origin);
  if (target.pathname !== window.location.pathname) {
    window.location.assign(target.href);
    return;
  }
  window.history.replaceState(
    window.history.state,
    "",
    `${target.pathname}${target.search}${target.hash}`,
  );
  if (noteHistory) {
    noteContextLinkHistory({
      ...normalized,
      timestamp: new Date().toISOString(),
    });
  }
  if (closeLens) {
    setContextLensOpen(false);
  }
  applyWorkspaceUrlStateFromLocation({ jump: true });
  if (showToastMessage && toastMessage) {
    showToast(toastMessage, "success");
  }
}

function restoreContextLinkHistoryEntry(entryIndex) {
  const entry = state.contextLinkHistory[Number(entryIndex)];
  if (!entry) {
    return;
  }
  restoreContextLinkRecord(entry, copy("Shared context restored", "已恢复分享上下文"));
}

function restoreContextSavedViewEntry(entryIndex) {
  const entry = state.contextSavedViews[Number(entryIndex)];
  if (!entry) {
    return;
  }
  restoreContextLinkRecord(entry, copy("Saved view restored", "已恢复保存视图"));
}

function restoreContextSavedViewByName(viewName) {
  const normalizedName = String(viewName || "").trim().toLowerCase();
  if (!normalizedName) {
    return;
  }
  const index = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
    .map((entry) => normalizeContextSavedViewEntry(entry))
    .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
  if (index >= 0) {
    restoreContextSavedViewEntry(index);
  }
}

function applyDefaultSavedViewOnBoot() {
  if (!state.contextDefaultBootPending) {
    return;
  }
  state.contextDefaultBootPending = false;
  const defaultEntry = getDefaultContextSavedView();
  if (!defaultEntry) {
    return;
  }
  restoreContextLinkRecord(defaultEntry, "", {
    noteHistory: false,
    closeLens: false,
    showToastMessage: false,
  });
}

function hasIntakePopulation() {
  return (
    (Array.isArray(state.watches) && state.watches.length > 0) ||
    (Array.isArray(state.triage) && state.triage.length > 0) ||
    (Array.isArray(state.stories) && state.stories.length > 0) ||
    (Array.isArray(state.alerts) && state.alerts.length > 0) ||
    (Array.isArray(state.routes) && state.routes.length > 0) ||
    Boolean(
      state.overview && [
        "enabled_watches",
        "due_watches",
        "triage_open_count",
        "story_ready_count",
        "alerting_mission_count",
        "story_count",
        "alert_count",
        "route_count"
      ].some((key) => Number(state.overview?.[key] || 0) > 0)
    )
  );
}

function renderIntakeLiveDesk() {
  const onboardingHero = $("intake-hero-onboarding");
  const liveHero = $("intake-hero-live");
  const onboardingSide = $("intake-side-onboarding");
  const liveSide = $("intake-side-live");
  if (!onboardingHero || !liveHero || !onboardingSide || !liveSide) {
    return;
  }

  const hasPopulation = hasIntakePopulation();
  onboardingHero.hidden = hasPopulation;
  onboardingSide.hidden = hasPopulation;
  liveHero.hidden = !hasPopulation;
  liveSide.hidden = !hasPopulation;

  if (!hasPopulation) {
    return;
  }

  const overview = state.overview || {};
  const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
  const selectedName = String((selectedWatch && (selectedWatch.name || selectedWatch.id)) || "").trim() || copy("No mission selected", "未选择任务");
  const enabledCount = Number(overview.enabled_watches ?? 0);
  const dueCount = Number(overview.due_watches ?? 0);
  const openQueue = Number(overview.triage_open_count ?? 0);
  const readyStories = Number(overview.story_ready_count ?? 0);
  const alertingMissions = Number(overview.alerting_mission_count ?? 0);
  const heroActionHierarchy = {
    primary: selectedWatch
      ? (
          selectedWatch.enabled === false
            ? {
                label: copy("Enable Mission", "启用任务"),
                attrs: { "data-watch-toggle": selectedWatch.id, "data-watch-enabled": "0" },
              }
            : {
                label: copy("Open Cockpit", "打开任务详情"),
                attrs: { "data-empty-jump": "section-cockpit" },
              }
        )
      : {
          label: copy("Open Mission Board", "打开任务列表"),
          attrs: { "data-empty-jump": "section-board" },
        },
    secondary: [
      selectedWatch && selectedWatch.enabled !== false
        ? { label: copy("Run Mission", "立即执行任务"), attrs: { "data-empty-run-watch": selectedWatch.id } }
        : null,
      { label: copy("Open Triage", "打开分诊"), attrs: { "data-empty-jump": "section-triage" } },
      { label: copy("Focus Mission Draft", "聚焦任务草稿"), attrs: { "data-empty-focus": "mission", "data-empty-field": "name" } },
      { label: copy("Reset Draft", "清空草稿"), attrs: { "data-empty-reset": "mission" } },
    ].filter(Boolean),
  };
  const stageFacts = [
    { label: copy("Open queue", "待分诊"), value: String(openQueue) },
    { label: copy("Ready stories", "待交付故事"), value: String(readyStories) },
    { label: copy("Alerting missions", "告警中任务"), value: String(alertingMissions) },
  ];
  const guidanceFacts = [
    { label: copy("Enabled missions", "活跃任务"), value: String(enabledCount) },
    { label: copy("Due now", "当前待执行"), value: String(dueCount) },
    { label: copy("Routes", "路由数"), value: String(overview.route_count ?? state.routes.length ?? 0) },
  ];

  liveHero.innerHTML = `
    <div class="card live-object-anchor" data-intake-populated-hero="true">
      <div class="live-object-head">
        <div>
          <div class="live-object-kicker">${copy("Current object", "当前对象")}</div>
          <div class="live-object-title" data-intake-current-object>${escapeHtml(selectedName)}</div>
        </div>
        <span class="chip ${selectedWatch ? "ok" : "hot"}">${selectedWatch ? copy("Mission Focus", "任务聚焦") : copy("Population Present", "已有数据")}</span>
      </div>
      <div class="live-object-copy">${copy("The workspace is already populated, so stay on the current mission and use review or delivery counts as continuity instead of re-reading onboarding.", "当前工作区已经有实时对象，因此先围绕当前任务推进，并把审阅和交付计数作为连续性事实，而不是重新阅读引导文案。")}</div>
      ${renderSectionSummaryFacts(stageFacts)}
      ${renderCardActionHierarchy(heroActionHierarchy)}
    </div>
  `;

  liveSide.innerHTML = `
    <div class="card guide-compact-card" data-intake-guide-compact="true">
      <div class="card-top">
        <div>
          <div class="mono">${copy("Stage frame", "阶段框架")}</div>
          <h3 class="panel-title" style="margin-top:8px;">${copy("Monitor -> Review -> Deliver", "监测 -> 审阅 -> 交付")}</h3>
        </div>
        <span class="chip">${copy("compact guidance", "紧凑指引")}</span>
      </div>
      <div class="panel-sub">${copy("Keep one sentence of stage framing visible while the current mission, review queue, and route readiness carry the first scan path.", "保留一条阶段说明即可，让当前任务、分诊队列和路由就绪度承担第一扫描路径。")}</div>
      ${renderSectionSummaryFacts(guidanceFacts)}
    </div>
  `;

  wireLifecycleGuideActions(liveHero);
  wireLifecycleGuideActions(liveSide);
}

function renderTopbarContext() {
  const descriptor = buildTopbarContextDescriptor();
  setText("context-summary-kicker", descriptor.sectionLabel || descriptor.modeLabel);
  setText("context-summary-detail", descriptor.detail || descriptor.sectionLabel || descriptor.modeLabel);
  const summary = $("context-summary");
  if (summary) {
    summary.setAttribute("title", summary.textContent || descriptor.summary);
  }
  setPlaceholder("context-save-name", descriptor.summary);
  renderContextViewDock();
  renderContextLens(descriptor);
  syncContextLensChrome();
  renderIntakeLiveDesk();
  renderWorkspaceModeShell();
  scheduleCanvasTextFit($("context-shell"));
  scheduleCanvasTextFit($("context-lens"));
}

function normalizeContextObjectId(value) {
  return String(value || "").trim();
}

function setContextRouteName(value, section = "") {
  state.contextRouteName = normalizeContextObjectId(normalizeRouteName(value));
  state.contextRouteSection = String(section || "").trim();
}

function getRouteRecordByName(routeName) {
  const normalized = normalizeRouteName(routeName);
  if (!normalized) {
    return null;
  }
  return state.routes.find((route) => normalizeRouteName(route?.name) === normalized) || null;
}

function getSelectedWatchForContext() {
  const selectedWatchId = normalizeContextObjectId(state.selectedWatchId);
  if (!selectedWatchId) {
    return null;
  }
  return (
    state.watchDetails[selectedWatchId]
    || state.watches.find((watch) => watch.id === selectedWatchId)
    || null
  );
}

function collectWatchRouteCandidates(watch) {
  const watchRecord = watch || {};
  const rules = Array.isArray(watchRecord.alert_rules) ? watchRecord.alert_rules : [];
  const out = [];
  rules.forEach((rule) => {
    const routeNames = normalizeRouteRuleNames(rule);
    routeNames.forEach((routeName) => {
      if (routeName && !out.includes(routeName)) {
        out.push(routeName);
      }
    });
  });
  return out;
}

function setContextRouteFromWatch() {
  const selectedWatch = getSelectedWatchForContext();
  const draftRouteName = normalizeRouteName(state.createWatchDraft?.route);
  const routeCandidates = collectWatchRouteCandidates(selectedWatch);
  const contextRouteName = normalizeContextObjectId(state.contextRouteName);
  const activeSectionId = normalizeSectionId(state.activeSectionId);
  const activeRouteRecord = getRouteRecordByName(contextRouteName);

  if (draftRouteName) {
    setContextRouteName(draftRouteName, "section-ops");
    return;
  }

  if (contextRouteName && activeSectionId === "section-ops" && activeRouteRecord) {
    setContextRouteName(contextRouteName, "section-ops");
    return;
  }

  if (contextRouteName && routeCandidates.includes(contextRouteName)) {
    setContextRouteName(contextRouteName, state.contextRouteSection || "section-board");
    return;
  }

  if (routeCandidates.length) {
    setContextRouteName(routeCandidates[0], "section-board");
    return;
  }
  setContextRouteName("", "");
}

function buildContextObjectRailDescriptor() {
  const mission = getSelectedWatchForContext();
  const missionId = normalizeContextObjectId(mission?.id);
  const missionLabel = mission ? clampLabel(String(mission.name || mission.id || ""), 22) : contextLensEmptyValue();
  const missionRecentEvidence = Array.isArray(mission?.recent_results) && mission.recent_results.length
    ? mission.recent_results[0]
    : null;

  const selectedTriage = state.triage.find((item) => item.id === state.selectedTriageId) || null;
  const evidenceId = selectedTriage
    ? normalizeContextObjectId(selectedTriage.id)
    : normalizeContextObjectId(missionRecentEvidence?.id);
  const evidenceLabel = selectedTriage
    ? clampLabel(String(selectedTriage.title || selectedTriage.url || selectedTriage.id || ""), 24)
    : (missionRecentEvidence
      ? clampLabel(String(missionRecentEvidence.title || missionRecentEvidence.url || missionRecentEvidence.id || ""), 24)
      : contextLensEmptyValue());

  const selectedStory = getStoryRecord(state.selectedStoryId);
  const storyId = normalizeContextObjectId(selectedStory?.id);
  const storyLabel = selectedStory
    ? clampLabel(String(selectedStory.title || selectedStory.id || ""), 24)
    : contextLensEmptyValue();

  const selectedReport = getSelectedReportRecord();
  const reportId = normalizeContextObjectId(selectedReport?.id);
  const reportLabel = selectedReport
    ? clampLabel(String(selectedReport.title || selectedReport.id || ""), 24)
    : contextLensEmptyValue();

  const draftRouteName = normalizeRouteName(state.createWatchDraft?.route);
  const routeName = normalizeRouteName(state.contextRouteName) || draftRouteName || collectWatchRouteCandidates(mission)[0] || "";
  const routeRecord = getRouteRecordByName(routeName);

  return {
    steps: [
      {
        step: "mission",
        sectionId: "section-board",
        id: missionId,
        title: copy("Mission", "任务"),
        label: missionLabel,
      },
      {
        step: "evidence",
        sectionId: "section-triage",
        id: evidenceId,
        title: copy("Evidence", "证据"),
        label: evidenceLabel,
      },
      {
        step: "story",
        sectionId: "section-story",
        id: storyId,
        title: copy("Story", "故事"),
        label: storyLabel,
      },
      {
        step: "report",
        sectionId: "section-report-studio",
        id: reportId,
        title: copy("Report", "报告"),
        label: reportLabel,
      },
      {
        step: "route",
        sectionId: "section-ops",
        id: routeName,
        title: copy("Route", "路由"),
        label: routeRecord?.name || routeName || contextLensEmptyValue(),
      },
    ],
  };
}

function renderContextObjectRail(descriptor = buildContextObjectRailDescriptor()) {
  const root = $("context-object-rail");
  if (!root) {
    return;
  }
  const steps = Array.isArray(descriptor?.steps) ? descriptor.steps : [];
  root.innerHTML = steps
    .map((step) => `
      <button
        class="context-object-step"
        type="button"
        data-context-object-step="${step.step}"
        data-context-object-id="${escapeHtml(step.id || "")}"
        data-context-object-section="${step.sectionId}"
        title="${escapeHtml(`${step.title}: ${step.label || contextLensEmptyValue()}`)}"
      >
        <span class="context-object-step-title">${escapeHtml(step.title)}</span>
        <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">${escapeHtml(step.label || contextLensEmptyValue())}</span>
      </button>`)
    .join('<span class="context-object-divider">→</span>');
  scheduleCanvasTextFit(root);
}

async function activateContextObjectRailStep(stepName, objectId, sectionId) {
  const normalizedStep = String(stepName || "").trim().toLowerCase();
  const normalizedObjectId = normalizeContextObjectId(objectId);
  const normalizedSectionId = normalizeSectionId(sectionId);

  if (normalizedStep === "mission" && normalizedObjectId) {
    try {
      await loadWatch(normalizedObjectId);
    } catch (error) {
      reportError(error, copy("Open mission", "打开任务"));
    }
  } else if (normalizedStep === "evidence" && normalizedObjectId) {
    const triageItem = state.triage.find((item) => item.id === normalizedObjectId) || null;
    if (triageItem) {
      focusTriageEvidence([normalizedObjectId], { itemId: normalizedObjectId, jump: false, showToastMessage: false });
    }
  } else if (normalizedStep === "story" && normalizedObjectId) {
    try {
      await loadStory(normalizedObjectId);
    } catch (error) {
      reportError(error, copy("Open story", "打开故事"));
    }
  } else if (normalizedStep === "report" && normalizedObjectId) {
    try {
      await selectReport(normalizedObjectId);
    } catch (error) {
      reportError(error, copy("Open report", "打开报告"));
    }
  } else if (normalizedStep === "route" && normalizedObjectId) {
    try {
      await editRouteInDeck(normalizedObjectId);
      return;
    } catch (error) {
      reportError(error, copy("Open route", "打开路由"));
    }
  }

  if (normalizedSectionId) {
    jumpToSection(normalizedSectionId);
  }
}

function bindContextObjectRail() {
  const root = $("context-object-rail");
  if (!root) {
    return;
  }
  root.addEventListener("click", async (event) => {
    const step = event.target.closest("[data-context-object-step]");
    if (!step) {
      return;
    }
    await activateContextObjectRailStep(
      String(step.dataset.contextObjectStep || ""),
      String(step.dataset.contextObjectId || ""),
      String(step.dataset.contextObjectSection || ""),
    );
  });
}
