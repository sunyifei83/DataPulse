// Split group 2f: triage queue workbench, batch actions, and triage rendering.
// Depends on prior fragments and 00-common.js.

function renderDuplicateExplain(payload) {
  if (!payload) {
    return "";
  }
  const candidates = payload.candidates || [];
  const header = `
    <div class="meta">
      <span>${copy("suggested_primary", "建议主项")}=${payload.suggested_primary_id || "-"}</span>
      <span>${copy("matches", "匹配数")}=${payload.candidate_count || 0}</span>
      <span>${copy("shown", "显示数")}=${payload.returned_count || 0}</span>
    </div>
  `;
  if (!candidates.length) {
    return `<div class="card" style="margin-top:12px;">${header}<div class="panel-sub">${copy("No close duplicate candidate found.", "没有找到接近的重复候选项。")}</div></div>`;
  }
  return `
    <div class="card" style="margin-top:12px;">
      ${header}
      <div class="stack" style="margin-top:12px;">
        ${candidates.map((candidate) => `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${candidate.title}</h3>
                <div class="meta">
                  <span>${candidate.id}</span>
                  <span>${copy("similarity", "相似度")}=${Number(candidate.similarity || 0).toFixed(2)}</span>
                  <span>${copy("state", "状态")}=${localizeWord(candidate.review_state || "new")}</span>
                </div>
              </div>
              <span class="chip ${candidate.suggested_primary_id === candidate.id ? "ok" : ""}">${candidate.suggested_primary_id === candidate.id ? copy("keep", "保留") : copy("merge", "合并")}</span>
            </div>
            <div class="meta">
              <span>${copy("signals", "信号")}=${(candidate.signals || []).join(", ") || "-"}</span>
              <span>${copy("domain", "域名")}=${candidate.same_domain ? copy("same", "相同") : copy("mixed", "混合")}</span>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function renderReviewNotes(notes) {
  const entries = Array.isArray(notes) ? notes : [];
  if (!entries.length) {
    return `<div class="panel-sub">${copy("No review note recorded yet.", "当前还没有审核备注。")}</div>`;
  }
  return `
    <div class="stack" style="margin-top:12px;">
      ${entries.slice(-3).map((entry) => `
        <div class="mini-item">${escapeHtml(entry.author || "console")} | ${escapeHtml(entry.created_at || "-")}</div>
        <div class="panel-sub">${escapeHtml(entry.note || "")}</div>
      `).join("")}
    </div>
  `;
}

function renderTriageWorkbench(item, { filteredCount = 0, evidenceFocusCount = 0 } = {}) {
  if (!item) {
    return "";
  }
  const linkedStories = getStoriesForEvidenceItem(item.id);
  const nextHopActions = getTriageWorkbenchActionHierarchy(item, linkedStories);
  const triageSignal = getGovernanceSignal("triage_throughput");
  const storySignal = getGovernanceSignal("story_conversion");
  const noteCount = Array.isArray(item.review_notes) ? item.review_notes.length : 0;
  const itemMission = String(item?.extra?.watch_mission_name || item?.watch_mission_name || "").trim();
  const duplicateExplain = state.triageExplain[item.id];
  const triageGuidanceBlock = buildTriageGuidanceSurface(item, linkedStories, duplicateExplain, nextHopActions);
  return `
    <div class="card workbench-shell">
      <div class="card-top">
        <div>
          <div class="mono">${copy("Selected Evidence Workbench", "选中证据工作台")}</div>
          <h3 class="card-title" style="margin-top:10px;">${escapeHtml(item.title || item.id || copy("Selected evidence", "选中证据"))}</h3>
        </div>
        <span class="chip ${item.review_state === "escalated" ? "hot" : "ok"}">${localizeWord(item.review_state || "new")}</span>
      </div>
      <div class="panel-sub">${copy(
        "Keep queue context, reviewer notes, and story handoff in one focused surface while the list stays available for fast switching.",
        "把队列上下文、审核备注和故事交接集中在一个聚焦工作面里，同时保留列表用于快速切换。"
      )}</div>
      <div class="workbench-meta">
        <span class="chip">${copy("Queue", "队列")}: ${escapeHtml(localizeWord(state.triageFilter || "open"))}</span>
        <span class="chip">${copy("Shown", "显示")}: ${filteredCount}</span>
        <span class="chip">${copy("Score", "分数")}: ${item.score || 0}</span>
        <span class="chip">${copy("Confidence", "置信度")}: ${Number(item.confidence || 0).toFixed(2)}</span>
        ${itemMission ? `<span class="chip ok" data-fit-text="triage-mission-chip" data-fit-max-width="190" data-fit-fallback="28">${copy("Mission", "任务")}: ${escapeHtml(itemMission)}</span>` : ""}
        ${evidenceFocusCount ? `<span class="chip hot">${copy("Evidence Focus", "证据聚焦")}: ${evidenceFocusCount}</span>` : ""}
      </div>
      ${linkedStories.length
        ? `<div class="workbench-story-links">
            ${linkedStories.map((story) => `<span class="chip ok" data-fit-text="triage-story-chip" data-fit-max-width="176" data-fit-fallback="24">${escapeHtml(story.title || story.id)}</span>`).join("")}
          </div>`
        : ""}
      <div class="continuity-lane">
        <div class="continuity-stage ${itemMission ? "ok" : ""}">
          <div class="continuity-stage-kicker">${copy("From", "来自")}</div>
          <div class="continuity-stage-title">${copy("Mission Intake", "任务入口")}</div>
          <div class="continuity-stage-copy">${copy(
            "The queue keeps mission context close so evidence review does not require bouncing back to the board first.",
            "队列会把任务上下文保持在附近，避免为了回忆来源而先跳回任务列表。"
          )}</div>
          <div class="continuity-fact-list">
            <div class="continuity-fact"><span>${copy("Mission", "任务")}</span><strong>${escapeHtml(itemMission || copy("Shared queue", "共享队列"))}</strong></div>
            <div class="continuity-fact"><span>${copy("Open queue", "开放队列")}</span><strong>${String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0)}</strong></div>
            <div class="continuity-fact"><span>${copy("Enabled missions", "已启用任务")}</span><strong>${String(state.overview?.enabled_watches ?? 0)}</strong></div>
          </div>
        </div>
        <div class="continuity-stage ok">
          <div class="continuity-stage-kicker">${copy("Now", "当前")}</div>
          <div class="continuity-stage-title">${copy("Selected Evidence", "选中证据")}</div>
          <div class="continuity-stage-copy">${copy(
            "State transitions and reviewer notes stay attached to the selected evidence instead of being buried inside the full queue.",
            "状态切换和审核备注会直接附着在当前证据上，而不是继续埋在整条长队列里。"
          )}</div>
          <div class="continuity-fact-list">
            <div class="continuity-fact"><span>${copy("State", "状态")}</span><strong>${escapeHtml(localizeWord(item.review_state || "new"))}</strong></div>
            <div class="continuity-fact"><span>${copy("Notes", "备注")}</span><strong>${String(noteCount)}</strong></div>
            <div class="continuity-fact"><span>${copy("URL", "链接")}</span><strong>${escapeHtml(clampLabel(item.url || "-", 28))}</strong></div>
          </div>
        </div>
        <div class="continuity-stage ${linkedStories.length ? "ok" : ""}">
          <div class="continuity-stage-kicker">${copy("Next", "下一步")}</div>
          <div class="continuity-stage-title">${copy("Story Handoff", "故事交接")}</div>
          <div class="continuity-stage-copy">${copy(
            "Linked stories and conversion headroom stay visible so you can decide when this evidence should become narrative work.",
            "已关联故事和转化余量会继续可见，方便判断这条证据何时该进入叙事工作。"
          )}</div>
          <div class="continuity-fact-list">
            <div class="continuity-fact"><span>${copy("Linked stories", "已关联故事")}</span><strong>${String(linkedStories.length)}</strong></div>
            <div class="continuity-fact"><span>${copy("Eligible evidence", "可转故事证据")}</span><strong>${String(storySignal.eligible_item_count ?? 0)}</strong></div>
            <div class="continuity-fact"><span>${copy("Ready stories", "待交付故事")}</span><strong>${String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0)}</strong></div>
          </div>
        </div>
      </div>
      <div class="workbench-columns">
        <div class="card">
          <div class="mono">${copy("review notes", "审核备注")}</div>
          <div class="panel-sub">${copy("Capture reviewer rationale, route hints, and merge context without losing the selected evidence lane.", "在不丢失当前证据工作线的前提下，记录审核理由、路由提示和合并上下文。")}</div>
          ${renderReviewNotes(item.review_notes)}
          <form data-triage-note-form="${item.id}" style="margin-top:12px;">
            <label>${copy("note composer", "备注编辑")}<textarea name="note" rows="3" data-triage-note-input="${item.id}" placeholder="${copy("Capture reviewer rationale, routing hint, or merge context.", "记录审核理由、路由提示或合并上下文。")}">${escapeHtml(state.triageNoteDrafts[item.id] || "")}</textarea></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${copy("Save Note", "保存备注")}</button>
            </div>
          </form>
        </div>
        <div class="card">
          ${triageGuidanceBlock}
          ${duplicateExplain
            ? renderDuplicateExplain(duplicateExplain)
            : `<div class="panel-sub" style="margin-top:12px;">${copy("Duplicate explain stays here once loaded so the list can remain focused on switching items.", "加载后的重复解释会留在这里，列表本身只负责切换条目。")}</div>`}
        </div>
      </div>
    </div>
  `;
}

function getVisibleTriageItems() {
  const activeFilter = state.triageFilter || "open";
  const searchQuery = String(state.triageSearch || "").trim().toLowerCase();
  const pinnedIds = new Set(uniqueValues(state.triagePinnedIds));
  return state.triage.filter((item) => {
    if (pinnedIds.size && !pinnedIds.has(String(item.id || "").trim())) {
      return false;
    }
    const reviewState = String(item.review_state || "new").trim().toLowerCase() || "new";
    if (activeFilter === "all") {
      // pass
    } else if (activeFilter === "open") {
      if (["verified", "duplicate", "ignored"].includes(reviewState)) {
        return false;
      }
    } else if (reviewState !== activeFilter) {
      return false;
    }
    if (!searchQuery) {
      return true;
    }
    const noteText = Array.isArray(item.review_notes)
      ? item.review_notes.map((note) => String(note.note || "")).join(" ")
      : "";
    const haystack = [
      item.id,
      item.title,
      item.url,
      noteText,
    ].join(" ").toLowerCase();
    return haystack.includes(searchQuery);
  });
}

function isTriageItemSelected(itemId) {
  return state.selectedTriageIds.includes(itemId);
}

function toggleTriageSelection(itemId, checked = null) {
  if (!itemId) {
    return;
  }
  const next = new Set(state.selectedTriageIds);
  const shouldSelect = checked === null ? !next.has(itemId) : Boolean(checked);
  if (shouldSelect) {
    next.add(itemId);
    state.selectedTriageId = itemId;
  } else {
    next.delete(itemId);
  }
  state.selectedTriageIds = Array.from(next);
}

function selectVisibleTriageItems() {
  const visibleIds = getVisibleTriageItems().map((item) => item.id);
  state.selectedTriageIds = visibleIds;
  if (visibleIds.length && !visibleIds.includes(state.selectedTriageId)) {
    state.selectedTriageId = visibleIds[0];
  }
}

function clearTriageSelection() {
  state.selectedTriageIds = [];
}

function clearTriageEvidenceFocus() {
  state.triagePinnedIds = [];
  renderTriage();
  showToast(copy("Returned to the full triage queue.", "已返回完整分诊队列。"), "success");
}

function focusTriageEvidence(itemIds, { itemId = "", jump = true, showToastMessage = true } = {}) {
  const normalizedIds = uniqueValues(itemIds).filter((candidate) => state.triage.some((item) => item.id === candidate));
  if (!normalizedIds.length) {
    if (showToastMessage) {
      showToast(copy("No matching triage evidence is available for this story.", "当前没有可回查的分诊证据。"), "error");
    }
    return;
  }
  state.triagePinnedIds = normalizedIds;
  state.triageFilter = "all";
  state.triageSearch = "";
  state.selectedTriageId = itemId && normalizedIds.includes(itemId) ? itemId : normalizedIds[0];
  state.selectedTriageIds = [];
  renderTriage();
  if (jump) {
    jumpToSection("section-triage");
  }
  if (showToastMessage) {
    showToast(
      state.language === "zh"
        ? `已聚焦 ${normalizedIds.length} 条相关分诊证据`
        : `Focused ${normalizedIds.length} related triage item(s)`,
      "success",
    );
  }
}

async function postTriageState(itemId, nextState) {
  return api(`/api/triage/${itemId}/state`, {
    method: "POST",
    payload: { state: nextState, actor: "console" },
  });
}

async function deleteTriageItem(itemId) {
  return api(`/api/triage/${itemId}`, {
    method: "DELETE",
  });
}

async function runTriageExplain(itemId) {
  if (!itemId) {
    return;
  }
  state.selectedTriageId = itemId;
  state.triageExplain[itemId] = await api(`/api/triage/${itemId}/explain?limit=4`);
  renderTriage();
}

async function runTriageStateUpdate(itemId, nextState) {
  if (!itemId || !nextState) {
    return;
  }
  state.selectedTriageId = itemId;
  const currentItem = state.triage.find((item) => item.id === itemId);
  const previousState = currentItem ? String(currentItem.review_state || "new") : "new";
  if (currentItem) {
    currentItem.review_state = nextState;
  }
  renderTriage();
  try {
    await postTriageState(itemId, nextState);
    pushActionEntry({
      kind: copy("triage state", "分诊状态"),
      label: state.language === "zh" ? `已将 ${itemId} 标记为 ${localizeWord(nextState)}` : `Marked ${itemId} as ${nextState}`,
      detail: state.language === "zh" ? `之前状态为 ${localizeWord(previousState)}。` : `Previous state was ${previousState}.`,
      undoLabel: state.language === "zh" ? `恢复为 ${localizeWord(previousState)}` : `Restore ${previousState}`,
      undo: async () => {
        await postTriageState(itemId, previousState);
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已恢复分诊状态：${itemId} -> ${localizeWord(previousState)}`
            : `Triage state restored: ${itemId} -> ${previousState}`,
          "success",
        );
      },
    });
    await refreshBoard();
    setStageFeedback("review", {
      kind: "completion",
      title: state.language === "zh"
        ? `已将 ${itemId} 标记为 ${localizeWord(nextState)}`
        : `Marked ${itemId} as ${nextState}`,
      copy: copy(
        "The queue state is now persisted on the review lane. Continue in triage or hand the evidence into story work next.",
        "这条队列状态已经在审阅阶段持久化；下一步可以继续留在分诊，或把证据交给故事工作台。"
      ),
      actionHierarchy: {
        primary: {
          label: ["verified", "escalated"].includes(String(nextState || "").trim().toLowerCase())
            ? copy("Open Story Workspace", "打开故事工作台")
            : copy("Continue In Triage", "继续处理分诊"),
          attrs: ["verified", "escalated"].includes(String(nextState || "").trim().toLowerCase())
            ? { "data-empty-jump": "section-story" }
            : { "data-empty-jump": "section-triage" },
        },
        secondary: [
          {
            label: copy("Review Queue", "查看分诊队列"),
            attrs: { "data-empty-jump": "section-triage" },
          },
        ],
      },
    });
  } catch (error) {
    if (currentItem) {
      currentItem.review_state = previousState;
    }
    renderTriage();
    throw error;
  }
}

async function runTriageDelete(itemId) {
  if (!itemId) {
    return;
  }
  const currentItem = state.triage.find((item) => item.id === itemId);
  const itemLabel = currentItem && currentItem.title ? currentItem.title : itemId;
  const confirmed = window.confirm(
    state.language === "zh"
      ? `确认删除分诊条目：${itemLabel}？该操作会把条目从当前收件箱中移除。`
      : `Delete triage item "${itemLabel}" from the inbox?`,
  );
  if (!confirmed) {
    return;
  }
  await deleteTriageItem(itemId);
  state.selectedTriageIds = state.selectedTriageIds.filter((selectedId) => selectedId !== itemId);
  delete state.triageExplain[itemId];
  delete state.triageNoteDrafts[itemId];
  pushActionEntry({
    kind: copy("triage delete", "分诊删除"),
    label: state.language === "zh" ? `已删除：${itemLabel}` : `Deleted ${itemLabel}`,
    detail: state.language === "zh" ? `条目 ID：${itemId}` : `Item id: ${itemId}`,
  });
  await refreshBoard();
  showToast(
    state.language === "zh" ? `已删除分诊条目：${itemLabel}` : `Deleted triage item: ${itemLabel}`,
    "success",
  );
}

async function createStoryFromTriageItems(itemIds) {
  const normalizedIds = uniqueValues(itemIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
  if (!normalizedIds.length) {
    return;
  }
  const selectedItems = normalizedIds
    .map((itemId) => state.triage.find((item) => item.id === itemId))
    .filter(Boolean);
  const created = await api("/api/stories/from-triage", {
    method: "POST",
    payload: {
      item_ids: normalizedIds,
      status: "monitoring",
    },
  });
  state.storySearch = "";
  state.storyFilter = "all";
  state.storySort = "attention";
  persistStoryWorkspacePrefs();
  state.selectedStoryId = created.id;
  state.storyDetails[created.id] = created;
  state.selectedTriageIds = state.selectedTriageIds.filter((itemId) => !normalizedIds.includes(itemId));
  pushActionEntry({
    kind: copy("story seed", "故事生成"),
    label: state.language === "zh"
      ? `已从分诊生成故事：${created.title}`
      : `Created story from triage: ${created.title}`,
    detail: state.language === "zh"
      ? `来源条目：${selectedItems.map((item) => item.title || item.id).slice(0, 3).join("、")}`
      : `Source items: ${selectedItems.map((item) => item.title || item.id).slice(0, 3).join(", ")}`,
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
  await loadStory(created.id, { mode: "editor", syncUrl: true });
  jumpToSection("section-story");
  setStageFeedback("review", {
    kind: "completion",
    title: state.language === "zh"
      ? `已从 ${normalizedIds.length} 条分诊记录生成故事`
      : `Created story from ${normalizedIds.length} triage item(s)`,
    copy: copy(
      "The review lane now owns a promoted story candidate. Refine it in the workspace before delivery.",
      "审阅阶段现在已经拥有被提升的故事候选；下一步先在工作台里完善，再进入交付。"
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
    state.language === "zh"
      ? `已从 ${normalizedIds.length} 条分诊记录生成故事`
      : `Created story from ${normalizedIds.length} triage item(s)`,
    "success",
  );
}

async function runTriageBatchStateUpdate(nextState) {
  const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
  if (!itemIds.length || !nextState || state.triageBulkBusy) {
    return;
  }
  state.triageBulkBusy = true;
  if (!itemIds.includes(state.selectedTriageId)) {
    state.selectedTriageId = itemIds[0];
  }
  const previousStates = {};
  itemIds.forEach((itemId) => {
    const currentItem = state.triage.find((item) => item.id === itemId);
    previousStates[itemId] = currentItem ? String(currentItem.review_state || "new") : "new";
    if (currentItem) {
      currentItem.review_state = nextState;
    }
  });
  renderTriage();
  const appliedIds = [];
  try {
    for (const itemId of itemIds) {
      await postTriageState(itemId, nextState);
      appliedIds.push(itemId);
    }
    state.selectedTriageIds = [];
    pushActionEntry({
      kind: copy("triage batch", "分诊批处理"),
      label: state.language === "zh"
        ? `已批量将 ${itemIds.length} 条记录标记为 ${localizeWord(nextState)}`
        : `Marked ${itemIds.length} triage items as ${nextState}`,
      detail: state.language === "zh"
        ? `涉及条目：${itemIds.join(", ")}`
        : `Items: ${itemIds.join(", ")}`,
      undoLabel: state.language === "zh"
        ? `恢复这 ${itemIds.length} 条记录`
        : `Restore ${itemIds.length} items`,
      undo: async () => {
        for (const itemId of itemIds) {
          await postTriageState(itemId, previousStates[itemId] || "new");
        }
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已恢复 ${itemIds.length} 条分诊记录`
            : `Restored ${itemIds.length} triage items`,
          "success",
        );
      },
    });
    await refreshBoard();
    setStageFeedback("review", {
      kind: "completion",
      title: state.language === "zh"
        ? `已批量处理 ${itemIds.length} 条分诊记录`
        : `Processed ${itemIds.length} triage items`,
      copy: copy(
        "The selected queue slice is now updated in place. Continue review or hand the verified evidence into stories.",
        "当前选中的队列切片已经原位更新；下一步可以继续审阅，或把已核验证据交给故事工作台。"
      ),
      actionHierarchy: {
        primary: {
          label: copy("Open Triage", "打开分诊"),
          attrs: { "data-empty-jump": "section-triage" },
        },
        secondary: [
          {
            label: copy("Open Story Workspace", "打开故事工作台"),
            attrs: { "data-empty-jump": "section-story" },
          },
        ],
      },
    });
    showToast(
      state.language === "zh"
        ? `已批量处理 ${itemIds.length} 条分诊记录`
        : `Processed ${itemIds.length} triage items`,
      "success",
    );
  } catch (error) {
    itemIds.forEach((itemId) => {
      const currentItem = state.triage.find((item) => item.id === itemId);
      if (currentItem) {
        currentItem.review_state = previousStates[itemId] || "new";
      }
    });
    renderTriage();
    for (const itemId of appliedIds.reverse()) {
      try {
        await postTriageState(itemId, previousStates[itemId] || "new");
      } catch (rollbackError) {
        console.error("triage batch rollback failed", rollbackError);
      }
    }
    await refreshBoard();
    throw error;
  } finally {
    state.triageBulkBusy = false;
    renderTriage();
  }
}

async function runTriageBatchDelete() {
  const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
  if (!itemIds.length || state.triageBulkBusy) {
    return;
  }
  const confirmed = window.confirm(
    state.language === "zh"
      ? `确认删除已选的 ${itemIds.length} 条分诊记录？该操作会把它们从当前收件箱中移除。`
      : `Delete ${itemIds.length} selected triage items from the inbox?`,
  );
  if (!confirmed) {
    return;
  }
  state.triageBulkBusy = true;
  renderTriage();
  let deletedCount = 0;
  try {
    for (const itemId of itemIds) {
      await deleteTriageItem(itemId);
      deletedCount += 1;
      delete state.triageExplain[itemId];
      delete state.triageNoteDrafts[itemId];
    }
    state.selectedTriageIds = [];
    pushActionEntry({
      kind: copy("triage batch delete", "分诊批量删除"),
      label: state.language === "zh"
        ? `已批量删除 ${itemIds.length} 条分诊记录`
        : `Deleted ${itemIds.length} triage items`,
      detail: state.language === "zh"
        ? `涉及条目：${itemIds.join(", ")}`
        : `Items: ${itemIds.join(", ")}`,
    });
    await refreshBoard();
    showToast(
      state.language === "zh"
        ? `已批量删除 ${itemIds.length} 条分诊记录`
        : `Deleted ${itemIds.length} triage items`,
      "success",
    );
  } catch (error) {
    await refreshBoard();
    const message = error && error.message ? error.message : String(error || "Unknown error");
    if (deletedCount > 0) {
      throw new Error(
        state.language === "zh"
          ? `已删除 ${deletedCount}/${itemIds.length} 条记录后失败：${message}`
          : `Deleted ${deletedCount}/${itemIds.length} items before failure: ${message}`,
      );
    }
    throw error;
  } finally {
    state.triageBulkBusy = false;
    renderTriage();
  }
}

function focusTriageNoteComposer(itemId) {
  if (!itemId) {
    return;
  }
  state.selectedTriageId = itemId;
  renderTriage();
  const field = document.querySelector(`[data-triage-note-input="${itemId}"]`);
  if (field) {
    field.focus();
    field.setSelectionRange(field.value.length, field.value.length);
  }
}

function moveTriageSelection(delta) {
  const visibleItems = getVisibleTriageItems();
  if (!visibleItems.length) {
    return;
  }
  const currentIndex = Math.max(
    0,
    visibleItems.findIndex((item) => item.id === state.selectedTriageId),
  );
  const nextIndex = Math.min(
    visibleItems.length - 1,
    Math.max(0, currentIndex + delta),
  );
  state.selectedTriageId = visibleItems[nextIndex].id;
  renderTriage();
  const selectedCard = document.querySelector(`[data-triage-card="${state.selectedTriageId}"]`);
  selectedCard?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function renderTriage() {
  const root = $("triage-list");
  const inlineStats = $("triage-stats-inline");
  if (state.loading.board && !state.triage.length) {
    renderTriageSectionSummary();
    inlineStats.innerHTML = `<span>${copy("loading", "加载中")}=triage</span>`;
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    renderTopbarContext();
    return;
  }
  const stats = state.triageStats || {};
  const triageStates = stats.states || {};
  const triageSearchValue = String(state.triageSearch || "");
  const filterOptions = [
    { key: "open", label: copy("open", "开放"), count: stats.open_count || 0 },
    { key: "all", label: copy("all", "全部"), count: stats.total || state.triage.length },
    ...Object.entries(triageStates).map(([key, count]) => ({ key, label: localizeWord(key), count: count || 0 })),
  ];
  const activeFilter = normalizeTriageFilter(state.triageFilter);
  state.triageFilter = activeFilter;
  const filteredItems = getVisibleTriageItems();
  const defaultItemId = filteredItems[0] ? filteredItems[0].id : (state.triage[0] ? state.triage[0].id : "");
  const evidenceFocusCount = uniqueValues(state.triagePinnedIds).filter((itemId) => state.triage.some((item) => item.id === itemId)).length;
  const visibleIds = new Set(filteredItems.map((item) => item.id));
  state.selectedTriageIds = uniqueValues(state.selectedTriageIds).filter((itemId) => visibleIds.has(itemId));
  if (filteredItems.length && !filteredItems.some((item) => item.id === state.selectedTriageId)) {
    state.selectedTriageId = filteredItems[0].id;
  }
  if (!filteredItems.length) {
    state.selectedTriageId = "";
  }
  const selectedCount = state.selectedTriageIds.length;
  const batchBusy = Boolean(state.triageBulkBusy);
  const selectedTriageItem = filteredItems.find((item) => item.id === state.selectedTriageId) || null;
  renderTriageSectionSummary({
    stats,
    filteredItems,
    selectedItem: selectedTriageItem,
    evidenceFocusCount,
    activeFilter,
    searchValue: triageSearchValue,
  });
  const triageSearchCard = `
    <div class="card section-toolbox">
      <div class="section-toolbox-head">
        <div>
          <div class="mono">${copy("queue search", "队列搜索")}</div>
          <div class="panel-sub">${copy("Search the visible queue by title, url, id, or recent review notes.", "按标题、链接、条目 ID 或最近备注搜索当前可见队列。")}</div>
        </div>
        <div class="section-toolbox-meta">
          <span class="chip">${copy("shown", "显示")}=${filteredItems.length}</span>
          <span class="chip">${copy("selected", "已选")}=${selectedCount}</span>
          <span class="chip ${evidenceFocusCount ? "hot" : ""}">${copy("evidence", "证据")}=${evidenceFocusCount || 0}</span>
        </div>
      </div>
      <div class="search-shell">
        <input type="search" value="${escapeHtml(triageSearchValue)}" data-triage-search placeholder="${copy("Search visible queue", "搜索当前队列")}">
        <button class="btn-secondary" type="button" data-triage-search-clear ${triageSearchValue.trim() ? "" : "disabled"}>${copy("Clear", "清空")}</button>
      </div>
      ${
        evidenceFocusCount
          ? `
            <div class="actions" style="margin-top:12px;">
              <span class="chip hot">${copy("evidence focus active", "证据聚焦中")}</span>
              <span class="panel-sub">${copy(`Showing ${evidenceFocusCount} triage evidence item(s) linked to the current story.`, `当前只显示与故事关联的 ${evidenceFocusCount} 条分诊证据。`)}</span>
              <button class="btn-secondary" type="button" data-triage-pin-clear>${copy("Show Full Queue", "显示完整队列")}</button>
            </div>
          `
          : ""
      }
    </div>
  `;
  const batchCopy = selectedCount
    ? copy(
        `Selected ${selectedCount} items. Apply one queue action or clear the selection.`,
        `已选 ${selectedCount} 条。直接执行一个批量动作，或先清空选择。`,
      )
    : copy(
        "Select visible items, then apply one review action across the queue without leaving the page.",
        "先选择当前列表中的条目，再在当前页面内一次性执行统一审核动作。",
      );
  const filterBlock = `
    <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Triage queue filters", "分诊队列筛选"))}">
      ${filterOptions.map((option) => `
        <button class="ui-segment-button ${activeFilter === option.key ? "active" : ""}" type="button" data-triage-filter="${escapeHtml(option.key)}" aria-pressed="${activeFilter === option.key ? "true" : "false"}">${escapeHtml(option.label)} (${option.count || 0})</button>
      `).join("")}
    </div>
  `;
  const batchToolbar = `
    <div class="card batch-toolbar-card ${selectedCount ? "selection-live" : ""}">
      <div class="batch-toolbar">
        <div class="batch-toolbar-head">
          <div>
            <div class="mono">${copy("batch actions", "批量操作")}</div>
            <div class="panel-sub">${batchCopy}</div>
          </div>
          <span class="chip ${selectedCount ? "ok" : ""}">${copy("selected", "已选")}=${selectedCount}</span>
        </div>
        ${
          selectedCount
            ? `<div class="actions">
                <button class="btn-secondary" type="button" data-triage-selection-clear ${batchBusy ? "disabled" : ""}>${copy("Clear Selection", "清空选择")}</button>
                <button class="btn-secondary" type="button" data-triage-batch-state="triaged" ${batchBusy ? "disabled" : ""}>${copy("Batch Triage", "批量分诊")}</button>
                <button class="btn-secondary" type="button" data-triage-batch-state="verified" ${batchBusy ? "disabled" : ""}>${copy("Batch Verify", "批量核验")}</button>
                <button class="btn-secondary" type="button" data-triage-batch-state="escalated" ${batchBusy ? "disabled" : ""}>${copy("Batch Escalate", "批量升级")}</button>
                <button class="btn-secondary" type="button" data-triage-batch-state="ignored" ${batchBusy ? "disabled" : ""}>${copy("Batch Ignore", "批量忽略")}</button>
                <button class="btn-secondary" type="button" data-triage-batch-story ${batchBusy ? "disabled" : ""}>${copy("Batch Story", "批量生成故事")}</button>
                <button class="btn-danger" type="button" data-triage-batch-delete ${batchBusy ? "disabled" : ""}>${copy("Batch Delete", "批量删除")}</button>
              </div>`
            : `<div class="actions">
                <button class="btn-secondary" type="button" data-triage-select-visible ${(!filteredItems.length || batchBusy) ? "disabled" : ""}>${copy("Select Visible", "选择当前列表")}</button>
              </div>`
        }
      </div>
    </div>
  `;
  const triageWorkbench = selectedTriageItem
    ? renderTriageWorkbench(selectedTriageItem, { filteredCount: filteredItems.length, evidenceFocusCount })
    : "";
  inlineStats.innerHTML = `
    <span>${copy("open", "开放")}=${stats.open_count || 0}</span>
    <span>${copy("closed", "关闭")}=${stats.closed_count || 0}</span>
    <span>${copy("notes", "备注")}=${stats.note_count || 0}</span>
    <span>${copy("verified", "已核验")}=${(stats.states || {}).verified || 0}</span>
    <span>${copy("filter", "筛选")}=${localizeWord(activeFilter)}</span>
    <span>${copy("selected", "选中")}=${selectedCount}</span>
    <span>${copy("evidence", "证据")}=${evidenceFocusCount}</span>
    <span>${copy("focus", "焦点")}=${state.selectedTriageId || "-"}</span>
  `;
  if (!state.triage.length) {
    root.innerHTML = `
      ${triageSearchCard}
      <div class="card">
        <div class="mono">${copy("triage filters", "分诊筛选")}</div>
        <div class="panel-sub">${copy("Slice the queue by current review state before applying notes or state transitions.", "在写备注或修改状态前，先按审核状态切分队列。")}</div>
        <div class="stack" style="margin-top:12px;">${filterBlock}</div>
      </div>
      <div class="card">
        <div class="mono">${copy("triage shortcuts", "分诊快捷键")}</div>
        <div class="panel-sub">${copy("Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, S to create a story, D to explain duplicates, and N to focus the note composer.", "使用 J/K 上下移动，V 核验，T 分诊，E 升级，I 忽略，S 生成故事，D 查看重复解释，N 聚焦备注输入。")}</div>
      </div>
      ${batchToolbar}
      ${renderLifecycleGuideCard({
        title: copy("Triage opens after the first mission run writes inbox items", "任务第一次执行并写入收件箱后，分诊区才会展开"),
        summary: copy(
          "You do not need CLI-first setup to use the review lane. Create or run a mission in the browser, then use this queue to verify signal, mark duplicates, and promote stories.",
          "进入审阅工作流不需要先读 CLI 文档。先在浏览器里创建或执行任务，随后就在这个队列里完成核验、去重和故事提升。"
        ),
        steps: [
          {
            title: copy("Run A Mission", "先执行任务"),
            copy: copy("Mission Board or Cockpit will populate the inbox once evidence is collected.", "任务列表或任务详情执行后，收件箱就会开始积累证据。"),
          },
          {
            title: copy("Review Evidence", "审阅证据"),
            copy: copy("Mark duplicates, verify findings, or escalate items directly inside this queue.", "直接在这个队列里完成去重、核验或升级处理。"),
          },
          {
            title: copy("Promote Story", "提升故事"),
            copy: copy("Use Create Story when the queue has enough verified signal to become a narrative.", "当队列里积累了足够的已核验信号时，就可以直接生成故事。"),
          },
          {
            title: copy("Attach Delivery Later", "稍后再接交付"),
            copy: copy("Routes stay optional until the mission or story is ready to notify downstream.", "只有在任务或故事需要通知下游时，才需要回去接入路由。"),
          },
        ],
        actions: [
          { label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true },
          { label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title" },
          { label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" },
        ],
      })}
      <div class="empty">${copy("No triage item stored right now.", "当前没有分诊条目。")}</div>`;
    wireLifecycleGuideActions(root);
    syncTriageUrlState({ defaultItemId });
    flushTriageUrlFocus();
    renderTopbarContext();
    scheduleCanvasTextFit(root);
    return;
  }
  const totalTriageCount = state.triage.length;
  const hiddenTriageCount = Math.max(0, totalTriageCount - filteredItems.length);
  const filterBannerBits = [];
  if (evidenceFocusCount) {
    filterBannerBits.push(copy("evidence focus", "证据聚焦"));
  }
  if (triageSearchValue.trim()) {
    filterBannerBits.push(phrase("search \"{value}\"", "搜索 \"{value}\"", { value: triageSearchValue.trim() }));
  }
  if (activeFilter !== "open" && activeFilter !== "all") {
    filterBannerBits.push(phrase("state={value}", "状态={value}", { value: localizeWord(activeFilter) }));
  }
  const bannerReasonLabel = filterBannerBits.length ? filterBannerBits.join(" · ") : "";
  const showClearFocusButton = Boolean(evidenceFocusCount);
  const showClearSearchButton = Boolean(triageSearchValue.trim());
  const showResetFilterButton = activeFilter !== "open" && activeFilter !== "all";
  const shouldShowBanner = hiddenTriageCount > 0 || bannerReasonLabel;
  const listContextBanner = shouldShowBanner
    ? `
      <div class="triage-list-banner ${showClearFocusButton ? "hot" : ""}" style="position:sticky;top:0;z-index:2;padding:10px 12px;margin-bottom:10px;border-radius:10px;background:rgba(16,18,24,0.85);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;gap:8px;">
        <div class="meta" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
          <span class="chip ${hiddenTriageCount ? "hot" : "ok"}">${copy("shown", "显示")} ${filteredItems.length} / ${totalTriageCount}</span>
          ${hiddenTriageCount ? `<span class="panel-sub">${phrase("{count} hidden by active filter.", "有 {count} 条被筛选条件隐藏。", { count: hiddenTriageCount })}</span>` : `<span class="panel-sub">${copy("All queue items shown.", "当前队列无隐藏条目。")}</span>`}
          ${bannerReasonLabel ? `<span class="chip">${escapeHtml(bannerReasonLabel)}</span>` : ""}
        </div>
        ${(showClearFocusButton || showClearSearchButton || showResetFilterButton)
          ? `<div class="actions" style="display:flex;flex-wrap:wrap;gap:8px;">
              ${showClearFocusButton ? `<button class="btn-secondary" type="button" data-triage-banner-clear-focus>${copy("Show Full Queue", "显示完整队列")}</button>` : ""}
              ${showClearSearchButton ? `<button class="btn-secondary" type="button" data-triage-banner-clear-search>${copy("Clear Search", "清空搜索")}</button>` : ""}
              ${showResetFilterButton ? `<button class="btn-secondary" type="button" data-triage-banner-reset-filter>${copy("Reset To Open", "回到开放筛选")}</button>` : ""}
            </div>`
          : ""}
      </div>
    `
    : "";
  const listFooterHint = shouldShowBanner
    ? `<div class="empty" style="margin-top:12px;">${phrase("End of filtered list. {count} item(s) hidden.", "当前筛选下列表到底，还有 {count} 条被隐藏。", { count: hiddenTriageCount })}</div>`
    : "";
  const listItemsHtml = filteredItems.length
    ? filteredItems.map((item) => {
        const linkedStories = getStoriesForEvidenceItem(item.id);
        const noteCount = Array.isArray(item.review_notes) ? item.review_notes.length : 0;
        const itemMission = String(item?.extra?.watch_mission_name || item?.watch_mission_name || "").trim();
        const actionHierarchy = getTriageCardActionHierarchy(item, linkedStories);
        return `
  <div class="card selectable ${item.id === state.selectedTriageId ? "selected" : ""}" data-triage-card="${item.id}">
    <div class="card-top">
      <div class="triage-card-head">
        <label class="checkbox-inline">
          <input type="checkbox" data-triage-select="${item.id}" ${isTriageItemSelected(item.id) ? "checked" : ""}>
          <span>${copy("select", "选择")}</span>
        </label>
        <div>
          <h3 class="card-title">${item.title}</h3>
          <div class="meta">
            <span>${item.id}</span>
            <span>${copy("state", "状态")}=${localizeWord(item.review_state || "new")}</span>
            <span>${copy("score", "分数")}=${item.score || 0}</span>
            <span>${copy("confidence", "置信度")}=${Number(item.confidence || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>
      <span class="chip ${item.review_state === "escalated" ? "hot" : ""}">${localizeWord(item.review_state || "new")}</span>
    </div>
    <div class="panel-sub">${item.url}</div>
    <div class="meta">
      <span>${copy("notes", "备注")}=${noteCount}</span>
      <span>${copy("stories", "故事")}=${linkedStories.length}</span>
      ${itemMission ? `<span>${copy("mission", "任务")}=${escapeHtml(clampLabel(itemMission, 28))}</span>` : ""}
    </div>
    ${renderCardActionHierarchy(actionHierarchy)}
  </div>
`;
      }).join("")
    : `<div class="empty">${copy("No triage item matched the active queue filter.", "没有条目匹配当前分诊筛选。")}</div>`;

  const detailHtml = triageWorkbench
    ? triageWorkbench
    : `<div class="md-detail-empty">${copy("Select an evidence item from the queue to open the review workbench.", "在左侧队列中选择一条证据，打开审阅工作台。")}</div>`;

  root.innerHTML = `
    <div class="md-shell" data-layout="master-detail" data-md-mode="${selectedTriageItem ? "detail" : "list"}">
      <aside class="md-list">
        <div class="md-list-head">
          ${triageSearchCard}
          <div class="md-list-filter" role="group" aria-label="${escapeHtml(copy("Triage queue filters", "分诊队列筛选"))}">
            ${filterOptions.map((option) => `
              <button class="ui-segment-button ${activeFilter === option.key ? "active" : ""}" type="button" data-triage-filter="${escapeHtml(option.key)}" aria-pressed="${activeFilter === option.key ? "true" : "false"}">${escapeHtml(option.label)} (${option.count || 0})</button>
            `).join("")}
          </div>
          ${batchToolbar}
        </div>
        <div class="md-list-scroll">
          ${listContextBanner}
          ${listItemsHtml}
          ${hiddenTriageCount > 0 ? listFooterHint : ""}
        </div>
      </aside>
      <section class="md-detail">
        ${detailHtml}
      </section>
    </div>
  `;

  root.querySelectorAll("[data-triage-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.triageFilter = normalizeTriageFilter(button.dataset.triageFilter);
      renderTriage();
    });
  });

  root.querySelector("[data-triage-search]")?.addEventListener("input", (event) => {
    state.triageSearch = event.target.value;
    renderTriage();
  });

  root.querySelector("[data-triage-search-clear]")?.addEventListener("click", () => {
    state.triageSearch = "";
    renderTriage();
  });

  root.querySelector("[data-triage-pin-clear]")?.addEventListener("click", () => {
    clearTriageEvidenceFocus();
  });

  root.querySelector("[data-triage-banner-clear-focus]")?.addEventListener("click", () => {
    clearTriageEvidenceFocus();
  });

  root.querySelector("[data-triage-banner-clear-search]")?.addEventListener("click", () => {
    state.triageSearch = "";
    renderTriage();
  });

  root.querySelector("[data-triage-banner-reset-filter]")?.addEventListener("click", () => {
    state.triageFilter = "open";
    renderTriage();
  });

  root.querySelector("[data-triage-select-visible]")?.addEventListener("click", () => {
    selectVisibleTriageItems();
    renderTriage();
  });

  root.querySelector("[data-triage-selection-clear]")?.addEventListener("click", () => {
    clearTriageSelection();
    renderTriage();
  });

  root.querySelectorAll("[data-triage-batch-state]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await runTriageBatchStateUpdate(String(button.dataset.triageBatchState || "").trim());
      } catch (error) {
        reportError(error, copy("Batch triage", "批量分诊"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelector("[data-triage-batch-story]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await createStoryFromTriageItems(state.selectedTriageIds);
    } catch (error) {
      reportError(error, copy("Create story from triage", "从分诊生成故事"));
    } finally {
      button.disabled = false;
    }
  });

  root.querySelector("[data-triage-batch-delete]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await runTriageBatchDelete();
    } catch (error) {
      reportError(error, copy("Batch delete", "批量删除"));
    } finally {
      button.disabled = false;
    }
  });

  root.querySelectorAll("[data-triage-card]").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("button, textarea, input, select, a, form, label")) {
        return;
      }
      state.selectedTriageId = String(card.dataset.triageCard || "").trim();
      renderTriage();
    });
  });

  root.querySelectorAll("[data-triage-select]").forEach((input) => {
    input.addEventListener("change", () => {
      toggleTriageSelection(String(input.dataset.triageSelect || "").trim(), input.checked);
      renderTriage();
    });
  });

  root.querySelectorAll("[data-triage-explain]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await runTriageExplain(String(button.dataset.triageExplain || "").trim());
      } catch (error) {
        reportError(error, copy("Explain duplicates", "查看重复解释"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-triage-state]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await runTriageStateUpdate(
          String(button.dataset.triageId || "").trim(),
          String(button.dataset.triageState || "").trim(),
        );
      } catch (error) {
        reportError(error, copy("Update triage state", "更新分诊状态"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-triage-story]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await createStoryFromTriageItems([String(button.dataset.triageStory || "").trim()]);
      } catch (error) {
        reportError(error, copy("Create story from triage", "从分诊生成故事"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-triage-delete]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await runTriageDelete(String(button.dataset.triageDelete || "").trim());
      } catch (error) {
        reportError(error, copy("Delete triage item", "删除分诊条目"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-triage-note-input]").forEach((field) => {
    field.addEventListener("input", () => {
      state.triageNoteDrafts[field.dataset.triageNoteInput] = field.value;
    });
  });

  root.querySelectorAll("[data-triage-note-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const itemId = String(form.dataset.triageNoteForm || "").trim();
      const note = String(new FormData(form).get("note") || "").trim();
      if (!note) {
        showToast(copy("Provide a note before saving.", "保存前请先填写备注。"), "error");
        return;
      }
      const submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      try {
        await api(`/api/triage/${itemId}/note`, {
          method: "POST",
          payload: { note, author: "console" },
        });
        state.triageNoteDrafts[itemId] = "";
        await refreshBoard();
      } catch (error) {
        reportError(error, copy("Save triage note", "保存分诊备注"));
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  });
  wireLifecycleGuideActions(root);
  syncTriageUrlState({ defaultItemId });
  flushTriageUrlFocus();
  renderTopbarContext();
  scheduleCanvasTextFit(root);
}
