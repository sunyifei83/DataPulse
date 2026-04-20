// Split group 2g: story workspace rendering, inspector flows, and story detail surfaces.
// Depends on prior fragments and 00-common.js.

async function loadStory(identifier, { mode = null, syncUrl = true, force = false } = {}) {
  const normalizedId = String(identifier || "").trim();
  if (!normalizedId) {
    return;
  }
  const normalizedMode = mode == null ? null : normalizeStoryWorkspaceMode(mode);
  if (normalizedMode !== null) {
    applyStoryWorkspaceMode(normalizedMode, { persist: true, syncUrl: false });
  }
  state.selectedStoryId = normalizedId;
  state.loading.storyDetail = true;
  renderStories();
  try {
    if (force || !state.storyDetails[normalizedId] || !state.storyGraph[normalizedId]) {
      const [detail, graph] = await Promise.all([
        api(`/api/stories/${normalizedId}`),
        api(`/api/stories/${normalizedId}/graph`),
      ]);
      state.storyDetails[normalizedId] = detail;
      state.storyGraph[normalizedId] = graph;
    }
  } finally {
    state.loading.storyDetail = false;
  }
  if (syncUrl) {
    syncStoryUrlState({ defaultStoryId: normalizedId });
  }
  renderStories();
}

function syncStoryInspectorChrome() {
  const backdrop = $("story-inspector-backdrop");
  const shell = $("story-inspector-shell");
  const inspectorOpen = Boolean(state.storyInspector?.open);
  if (document.body) {
    document.body.dataset.storyInspectorOpen = inspectorOpen ? "true" : "false";
  }
  if (backdrop) {
    backdrop.hidden = !inspectorOpen;
    backdrop.classList.toggle("open", inspectorOpen);
  }
  if (shell) {
    shell.setAttribute("aria-hidden", inspectorOpen ? "false" : "true");
  }
}

function getStoryInspectorFocusableElements() {
  const shell = $("story-inspector-shell");
  if (!shell) {
    return [];
  }
  return Array.from(shell.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
    .filter((element) => !element.hasAttribute("hidden") && element.getAttribute("aria-hidden") !== "true");
}

function openStoryInspector(kind, storyId, { loading = false, restoreFocus = true, subjectKind = "story" } = {}) {
  if (restoreFocus) {
    const active = document.activeElement;
    storyInspectorRestoreNode = active instanceof HTMLElement ? active : null;
  }
  setContextLensOpen(false);
  closeCommandPalette();
  state.storyInspector = {
    open: true,
    subjectKind: String(subjectKind || "").trim().toLowerCase() === "report" ? "report" : "story",
    kind: normalizeStoryInspectorKind(kind),
    storyId: String(storyId || state.selectedStoryId || "").trim(),
    loading: Boolean(loading),
  };
  syncStoryInspectorChrome();
  renderStoryInspector();
  window.setTimeout(() => {
    $("story-inspector-shell")?.focus();
  }, 10);
}

function closeStoryInspector({ restoreFocus = true } = {}) {
  const wasOpen = Boolean(state.storyInspector?.open);
  state.storyInspector = {
    ...state.storyInspector,
    open: false,
    loading: false,
  };
  syncStoryInspectorChrome();
  renderStoryInspector();
  if (!wasOpen) {
    if (!restoreFocus) {
      storyInspectorRestoreNode = null;
    }
    return;
  }
  window.setTimeout(() => {
    if (restoreFocus && storyInspectorRestoreNode && storyInspectorRestoreNode.isConnected && typeof storyInspectorRestoreNode.focus === "function") {
      storyInspectorRestoreNode.focus();
    }
    storyInspectorRestoreNode = null;
  }, 0);
}

async function inspectStoryArtifact(kind, identifier, { preserveRestoreFocus = true } = {}) {
  const normalizedKind = normalizeStoryInspectorKind(kind);
  const normalizedId = String(identifier || "").trim();
  if (!normalizedId) {
    return;
  }
  state.selectedStoryId = normalizedId;
  const needsDetail = !state.storyDetails[normalizedId];
  const needsMarkdown = normalizedKind === "markdown" && !state.storyMarkdown[normalizedId];
  openStoryInspector(normalizedKind, normalizedId, {
    loading: needsDetail || needsMarkdown,
    restoreFocus: preserveRestoreFocus,
    subjectKind: "story",
  });
  renderStories();
  try {
    if (needsDetail) {
      state.storyDetails[normalizedId] = await api(`/api/stories/${normalizedId}`);
    }
    if (needsMarkdown) {
      state.storyMarkdown[normalizedId] = await apiText(`/api/stories/${normalizedId}/export?format=markdown`);
    }
  } finally {
    state.storyInspector = {
      ...state.storyInspector,
      open: true,
      subjectKind: "story",
      kind: normalizedKind,
      storyId: normalizedId,
      loading: false,
    };
    renderStoryInspector();
    renderStories();
  }
}

async function previewStoryMarkdown(identifier, options = {}) {
  await inspectStoryArtifact("markdown", identifier, { preserveRestoreFocus: options.preserveRestoreFocus !== false });
}

async function previewStoryJson(identifier, options = {}) {
  await inspectStoryArtifact("json", identifier, { preserveRestoreFocus: options.preserveRestoreFocus !== false });
}

async function inspectReportArtifact(kind, identifier, { preserveRestoreFocus = true } = {}) {
  const normalizedKind = normalizeStoryInspectorKind(kind);
  const normalizedId = String(identifier || "").trim();
  if (!normalizedId) {
    return;
  }
  const needsDetail = !getReportRecord(normalizedId);
  const needsMarkdown = normalizedKind === "markdown" && !state.reportMarkdown[normalizedId];
  openStoryInspector(normalizedKind, normalizedId, {
    loading: needsDetail || needsMarkdown,
    restoreFocus: preserveRestoreFocus,
    subjectKind: "report",
  });
  if (String(state.selectedReportId || "").trim() !== normalizedId) {
    state.selectedReportId = normalizedId;
    if (getReportRecord(normalizedId)) {
      syncReportSelectionState();
    }
  }
  renderClaimsWorkspace();
  renderReportStudio();
  renderTopbarContext();
  try {
    if (needsDetail) {
      const report = await api(`/api/reports/${normalizedId}`);
      const reportIndex = state.reports.findIndex((candidate) => String(candidate.id || "").trim() === normalizedId);
      if (reportIndex >= 0) {
        state.reports[reportIndex] = report;
      } else {
        state.reports = [report, ...state.reports];
      }
    }
    if (String(state.selectedReportId || "").trim() !== normalizedId) {
      state.selectedReportId = normalizedId;
    }
    syncReportSelectionState();
    if (needsMarkdown) {
      state.reportMarkdown[normalizedId] = await apiText(`/api/reports/${normalizedId}/export?output_format=markdown`);
    }
  } finally {
    state.storyInspector = {
      ...state.storyInspector,
      open: true,
      subjectKind: "report",
      kind: normalizedKind,
      storyId: normalizedId,
      loading: false,
    };
    renderStoryInspector();
    renderClaimsWorkspace();
    renderReportStudio();
    renderTopbarContext();
  }
}

async function previewReportJson(identifier, options = {}) {
  await inspectReportArtifact("json", identifier, { preserveRestoreFocus: options.preserveRestoreFocus !== false });
}

function renderStoryInspector() {
  const kicker = $("story-inspector-kicker");
  const title = $("story-inspector-title");
  const copyNode = $("story-inspector-copy");
  const body = $("story-inspector-body");
  const footer = $("story-inspector-footer");
  if (!kicker || !title || !copyNode || !body || !footer) {
    return;
  }
  syncStoryInspectorChrome();
  if (!state.storyInspector?.open) {
    body.innerHTML = "";
    footer.innerHTML = "";
    return;
  }
  const subjectKind = String(state.storyInspector.subjectKind || "").trim().toLowerCase() === "report" ? "report" : "story";
  const artifactId = String(
    state.storyInspector.storyId
    || (subjectKind === "report" ? state.selectedReportId : state.selectedStoryId)
    || ""
  ).trim();
  const kind = normalizeStoryInspectorKind(state.storyInspector.kind);
  const artifact = subjectKind === "report"
    ? getReportRecord(artifactId)
    : (state.storyDetails[artifactId] || state.stories.find((candidate) => candidate.id === artifactId));
  const loading = Boolean(state.storyInspector.loading);
  const artifactLabel = subjectKind === "report" ? copy("Report", "报告") : copy("Story", "故事");
  const artifactStatus = artifact ? localizeWord(artifact.status || (subjectKind === "report" ? "draft" : "active")) : "-";
  const artifactSummary = String(artifact?.summary || "").trim();
  const artifactSubtitle = subjectKind === "report"
    ? `${copy("sections", "章节")}=${getReportSectionsForReport(artifactId).length}`
    : `${copy("updated", "更新")}=${formatCompactDateTime(artifact?.updated_at || artifact?.generated_at || "") || "-"}`;
  kicker.textContent = subjectKind === "report"
    ? copy("report export sheet", "报告导出查看")
    : copy("story export sheet", "故事导出查看");
  title.textContent = subjectKind === "report"
    ? (kind === "markdown" ? copy("Report Markdown Export", "报告 Markdown 导出") : copy("Persisted Report JSON", "持久化报告 JSON"))
    : (kind === "markdown" ? copy("Markdown Evidence Pack", "Markdown 证据包") : copy("Persisted Story JSON", "持久化故事 JSON"));
  copyNode.textContent = subjectKind === "report"
    ? (kind === "markdown"
      ? copy(
        "Review report markdown in a sheet so the studio stays focused on structure, guardrails, and sections.",
        "把报告 Markdown 放进 sheet 查看，让工作台继续聚焦结构、门禁和章节。"
      )
      : copy(
        "Inspect the persisted report object in a sheet without dropping raw JSON into the main report workspace.",
        "把持久化报告对象放进 sheet 查看，避免主报告工作台被原始 JSON 打断。"
      ))
    : (kind === "markdown"
      ? copy(
        "Review the markdown export in a sheet so the main workspace stays editorial instead of raw-output heavy.",
        "把 Markdown 导出放进 sheet 查看，避免主工作台被原始输出挤占。"
      )
      : copy(
        "Inspect the persisted story object in a sheet without dumping raw JSON into the primary reading column.",
        "把持久化故事对象放进 sheet 查看，避免主阅读列被原始 JSON 打断。"
      ));
  const toolbar = `
    <div class="story-inspector-toolbar">
      <div class="ui-segment" role="tablist" aria-label="${escapeHtml(subjectKind === "report" ? copy("Report export surfaces", "报告导出视图") : copy("Story export surfaces", "故事导出视图"))}">
        <button class="ui-segment-button ${kind === "markdown" ? "active" : ""}" type="button" data-story-inspector-view="markdown" aria-pressed="${kind === "markdown" ? "true" : "false"}">${copy("Markdown", "Markdown")}</button>
        <button class="ui-segment-button ${kind === "json" ? "active" : ""}" type="button" data-story-inspector-view="json" aria-pressed="${kind === "json" ? "true" : "false"}">${copy("JSON", "JSON")}</button>
      </div>
      <div class="meta">
        <span>${artifactId || "-"}</span>
        <span>${copy("status", "状态")}=${artifactStatus}</span>
        <span>${artifactSubtitle}</span>
      </div>
    </div>
  `;
  if (!artifactId) {
    body.innerHTML = `${toolbar}<div class="empty">${subjectKind === "report" ? copy("Select one report before opening the export sheet.", "先选择一份报告，再打开导出查看。") : copy("Select one story before opening the export sheet.", "先选择一条故事，再打开导出查看。")}</div>`;
    footer.innerHTML = "";
    scheduleCanvasTextFit(body);
    return;
  }
  if (loading) {
    body.innerHTML = `${toolbar}${skeletonCard(6)}`;
    footer.innerHTML = "";
    scheduleCanvasTextFit(body);
    return;
  }
  const markdownValue = String(subjectKind === "report" ? state.reportMarkdown[artifactId] || "" : state.storyMarkdown[artifactId] || "");
  const jsonValue = artifact ? JSON.stringify(artifact, null, 2) : "";
  const previewBlock = kind === "markdown"
    ? (markdownValue
      ? `<pre class="text-block story-inspector-pre">${escapeHtml(markdownValue)}</pre>`
      : `<div class="empty">${subjectKind === "report" ? copy("Markdown export is still empty for this report.", "这份报告当前还没有可读的 Markdown 导出内容。") : copy("Markdown export is still empty for this story.", "这条故事当前还没有可读的 Markdown 导出内容。")}</div>`)
    : (jsonValue
      ? `<pre class="text-block story-inspector-pre">${escapeHtml(jsonValue)}</pre>`
      : `<div class="empty">${subjectKind === "report" ? copy("No persisted report snapshot is available yet.", "当前还没有可查看的持久化报告快照。") : copy("No persisted story snapshot is available yet.", "当前还没有可查看的持久化故事快照。")}</div>`);
  body.innerHTML = `
    ${toolbar}
    <div class="card story-inspector-panel">
      <div class="card-top">
        <div>
          <div class="mono">${kind === "markdown" ? copy("export preview", "导出预览") : copy("persisted snapshot", "持久化快照")}</div>
          <h3 class="card-title">${escapeHtml(artifact?.title || artifactId)}</h3>
        </div>
        <span class="chip ${kind === "markdown" ? "ok" : ""}">${kind === "markdown" ? copy("readable", "可读") : copy("raw", "原始")}</span>
      </div>
      <div class="panel-sub">${escapeHtml(artifactSummary || copy("No summary captured.", "没有记录到摘要。"))}</div>
      ${previewBlock}
    </div>
  `;
  const rawHref = subjectKind === "report"
    ? (kind === "markdown" ? `/api/reports/${artifactId}/export?output_format=markdown` : `/api/reports/${artifactId}`)
    : (kind === "markdown" ? `/api/stories/${artifactId}/export?format=markdown` : `/api/stories/${artifactId}`);
  footer.innerHTML = `
    <button class="btn-secondary" type="button" data-story-inspector-copy>${kind === "markdown" ? copy("Copy Markdown", "复制 Markdown") : copy("Copy JSON", "复制 JSON")}</button>
    <a href="${rawHref}" target="_blank" rel="noreferrer">${kind === "markdown" ? copy("Open Raw Markdown", "打开原始 Markdown") : copy("Open Raw JSON", "打开原始 JSON")}</a>
  `;
  body.querySelectorAll("[data-story-inspector-view]").forEach((button) => {
    button.addEventListener("click", async () => {
      const nextKind = String(button.dataset.storyInspectorView || "").trim();
      button.disabled = true;
      try {
        if (subjectKind === "report") {
          if (normalizeStoryInspectorKind(nextKind) === "json") {
            await previewReportJson(artifactId, { preserveRestoreFocus: false });
          } else {
            await inspectReportArtifact("markdown", artifactId, { preserveRestoreFocus: false });
          }
        } else {
          if (normalizeStoryInspectorKind(nextKind) === "json") {
            await previewStoryJson(artifactId, { preserveRestoreFocus: false });
          } else {
            await previewStoryMarkdown(artifactId, { preserveRestoreFocus: false });
          }
        }
      } catch (error) {
        reportError(error, subjectKind === "report" ? copy("Switch report export view", "切换报告导出视图") : copy("Switch story export view", "切换故事导出视图"));
      } finally {
        button.disabled = false;
      }
    });
  });
  footer.querySelector("[data-story-inspector-copy]")?.addEventListener("click", async () => {
    const value = kind === "markdown" ? markdownValue : jsonValue;
    if (!value) {
      showToast(
        kind === "markdown"
          ? copy("No markdown export is ready to copy.", "当前没有可复制的 Markdown 导出。")
          : (subjectKind === "report" ? copy("No report JSON is ready to copy.", "当前没有可复制的报告 JSON。") : copy("No story JSON is ready to copy.", "当前没有可复制的故事 JSON。")),
        "error",
      );
      return;
    }
    try {
      if (window.navigator.clipboard?.writeText) {
        await window.navigator.clipboard.writeText(value);
      } else {
        const helper = document.createElement("textarea");
        helper.value = value;
        helper.setAttribute("readonly", "readonly");
        helper.style.position = "absolute";
        helper.style.left = "-9999px";
        document.body.appendChild(helper);
        helper.select();
        document.execCommand("copy");
        document.body.removeChild(helper);
      }
      showToast(
        kind === "markdown"
          ? (subjectKind === "report" ? copy("Report markdown copied", "报告 Markdown 已复制") : copy("Story markdown copied", "故事 Markdown 已复制"))
          : (subjectKind === "report" ? copy("Report JSON copied", "报告 JSON 已复制") : copy("Story JSON copied", "故事 JSON 已复制")),
        "success",
      );
    } catch (error) {
      reportError(
        error,
        kind === "markdown"
          ? (subjectKind === "report" ? copy("Copy report markdown", "复制报告 Markdown") : copy("Copy story markdown", "复制故事 Markdown"))
          : (subjectKind === "report" ? copy("Copy report JSON", "复制报告 JSON") : copy("Copy story JSON", "复制故事 JSON")),
      );
    }
  });
  scheduleCanvasTextFit(body);
}

function renderStoryGraph(payload) {
  if (!payload || !Array.isArray(payload.nodes) || !payload.nodes.length) {
    return `<div class="empty">${copy("No entity graph available for this story.", "这个故事当前没有实体图谱。")}</div>`;
  }
  const storyNode = payload.nodes.find((node) => node.kind === "story") || payload.nodes[0];
  const entityNodes = payload.nodes.filter((node) => node.kind === "entity");
  const positions = {};
  positions[storyNode.id] = { x: 360, y: 160 };
  const radius = Math.min(145, 88 + (entityNodes.length * 5));
  entityNodes.forEach((node, index) => {
    const angle = ((Math.PI * 2) * index) / Math.max(entityNodes.length, 1) - (Math.PI / 2);
    positions[node.id] = {
      x: 360 + (Math.cos(angle) * radius),
      y: 160 + (Math.sin(angle) * radius),
    };
  });

  const lines = (payload.edges || []).map((edge) => {
    const source = positions[edge.source];
    const target = positions[edge.target];
    if (!source || !target) {
      return "";
    }
    const stroke = edge.kind === "entity_relation" ? "rgba(211, 108, 87, 0.78)" : "rgba(214, 196, 177, 0.38)";
    const dash = edge.kind === "entity_relation" ? "0" : "6 6";
    return `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" stroke="${stroke}" stroke-width="2.5" stroke-dasharray="${dash}" />`;
  }).join("");

  const labels = [storyNode, ...entityNodes].map((node) => {
    const pos = positions[node.id];
    if (!pos) {
      return "";
    }
    const isStory = node.kind === "story";
    const radiusValue = isStory ? 34 : 22 + Math.min(10, (Number(node.in_story_source_count || 0) * 2));
    const fill = isStory ? "#211710" : "#2d211a";
    const stroke = isStory ? "rgba(246, 239, 232, 0.76)" : "rgba(214, 196, 177, 0.3)";
    const textFill = "#f6efe8";
    const label = escapeHtml(node.label || node.id);
    const subtitle = isStory
      ? `${node.item_count || 0} items`
      : `${node.entity_type || "UNKNOWN"} / ${node.in_story_source_count || 0} src`;
    const subtitleY = isStory ? 8 : 6;
    return `
      <g>
        <circle cx="${pos.x}" cy="${pos.y}" r="${radiusValue}" fill="${fill}" stroke="${stroke}" stroke-width="2.5"></circle>
        <text x="${pos.x}" y="${pos.y - 4}" text-anchor="middle" font-family="Avenir Next Condensed, Arial Narrow, sans-serif" font-size="${isStory ? 16 : 13}" fill="${textFill}">
          ${label.slice(0, isStory ? 22 : 14)}
        </text>
        <text x="${pos.x}" y="${pos.y + subtitleY}" text-anchor="middle" font-family="SF Mono, IBM Plex Mono, monospace" font-size="10" fill="${textFill}">
          ${escapeHtml(subtitle)}
        </text>
      </g>
    `;
  }).join("");

  const entityList = entityNodes.length
    ? entityNodes.map((node) => `
        <div class="mini-item">${escapeHtml(node.label)} | ${copy("type", "类型")}=${escapeHtml(node.entity_type || "UNKNOWN")} | ${copy("in_story", "故事内来源")}=${node.in_story_source_count || 0}</div>
      `).join("")
    : `<div class="empty">${copy("No entity node captured.", "没有捕获到实体节点。")}</div>`;

  const relationList = (payload.edges || []).filter((edge) => edge.kind === "entity_relation").length
    ? (payload.edges || []).filter((edge) => edge.kind === "entity_relation").map((edge) => `
        <div class="mini-item">${escapeHtml(edge.source)} -> ${escapeHtml(edge.target)} | ${escapeHtml(edge.relation_type || "RELATED")}</div>
      `).join("")
    : `<div class="empty">${copy("No direct entity relation captured. Story-level mention edges are still shown above.", "没有直接实体关系；上方仍会展示故事级提及关系。")}</div>`;

  return `
    <div class="graph-shell">
      <div class="graph-canvas">
        <svg viewBox="0 0 720 320" role="img" aria-label="Story entity graph">
          <rect x="0" y="0" width="720" height="320" fill="transparent"></rect>
          ${lines}
          ${labels}
        </svg>
      </div>
      <div class="meta">
        <span>${copy("nodes", "节点")}=${payload.nodes.length}</span>
        <span>${copy("edges", "边")}=${payload.edge_count || 0}</span>
        <span>${copy("relations", "关系")}=${payload.relation_count || 0}</span>
        <span>${copy("entities", "实体")}=${payload.entity_count || 0}</span>
      </div>
      <div class="graph-meta">
        <div class="mini-list">${entityList}</div>
        <div class="mini-list">${relationList}</div>
      </div>
    </div>
  `;
}

function renderStoryCreateDeck() {
  const root = $("story-intake-deck");
  if (!root) {
    return;
  }
  const draft = normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
  const selectedStory = getStoryRecord(state.selectedStoryId);
  root.innerHTML = `
    <form id="story-create-form">
      <div class="card-top">
        <div>
          <div class="mono">${copy("manual story", "手工故事")}</div>
          <h3 class="card-title" style="margin-top:10px;">${copy("Capture A Brief Before It Gets Lost", "在信号散掉前先补一条故事")}</h3>
        </div>
        <span class="chip ok">${copy("lightweight", "轻量录入")}</span>
      </div>
      <div class="panel-sub">${copy("Use this for operator-authored briefs, incident notes, or tracking stubs that should be visible before automated clustering catches up.", "适合录入人工简报、事故备注，或那些需要先被看见、再等待自动聚类补齐的追踪占位。")}</div>
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Story draft status selection", "故事草稿状态选择"))}">
        ${
          storyStatusOptions.map((status) => `
            <button class="ui-segment-button ${draft.status === status ? "active" : ""}" type="button" data-story-draft-status="${status}" aria-pressed="${draft.status === status ? "true" : "false"}">${escapeHtml(localizeWord(status))}</button>
          `).join("")
        }
      </div>
      <div class="field-grid">
        <label>${copy("Story Title", "故事标题")}<input name="title" value="${escapeHtml(draft.title)}" placeholder="${copy("OpenAI launch brief", "OpenAI 发布简报")}"><span class="field-hint">${copy("Keep it short and legible in the story list.", "标题尽量短，方便在故事列表里快速扫读。")}</span></label>
        <label>${copy("Story Status", "故事状态")}
          <select name="status">
            ${storyStatusOptions.map((value) => `<option value="${value}" ${draft.status === value ? "selected" : ""}>${localizeWord(value)}</option>`).join("")}
          </select>
          <span class="field-hint">${copy("Status decides which lane this manual story enters first.", "状态决定这条手工故事先落在哪个工作阶段。")}</span>
        </label>
      </div>
      <label>${copy("Story Summary", "故事摘要")}<textarea name="summary" rows="4" placeholder="${copy("Capture what happened, why it matters, and what still needs confirmation.", "记录发生了什么、为什么重要，以及哪些部分仍待确认。")}">${escapeHtml(draft.summary)}</textarea><span class="field-hint">${copy("A compact summary is enough. Evidence and timeline can remain empty for manual stories.", "摘要写到够用即可；手工故事不需要一开始就补齐证据和时间线。")}</span></label>
      <div class="toolbar">
        <button class="btn-primary" type="submit">${copy("Create Story", "创建故事")}</button>
        <button class="btn-secondary" type="button" id="story-draft-clear">${copy("Clear Draft", "清空草稿")}</button>
        <button class="btn-secondary" type="button" id="story-draft-template" ${selectedStory ? "" : "disabled"}>${copy("Use Selected As Template", "以当前故事为模板")}</button>
      </div>
    </form>
  `;
  const form = $("story-create-form");
  form?.addEventListener("input", () => {
    state.storyDraft = collectStoryDraft(form);
  });
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitStoryDeck(form);
  });
  root.querySelectorAll("[data-story-draft-status]").forEach((button) => {
    button.addEventListener("click", () => {
      state.storyDraft = {
        ...collectStoryDraft(form),
        status: String(button.dataset.storyDraftStatus || "active").trim().toLowerCase() || "active",
      };
      renderStoryCreateDeck();
    });
  });
  $("story-draft-clear")?.addEventListener("click", () => {
    setStoryDraft(defaultStoryDraft());
    showToast(copy("Story draft cleared", "已清空故事草稿"), "success");
  });
  $("story-draft-template")?.addEventListener("click", () => {
    if (!selectedStory) {
      return;
    }
    setStoryDraft({
      title: `${selectedStory.title || copy("Story", "故事")} ${copy("Follow-up", "跟进")}`,
      summary: String(selectedStory.summary || ""),
      status: String(selectedStory.status || "active"),
    });
    focusStoryDeck("title");
    showToast(
      state.language === "zh"
        ? `已从 ${selectedStory.title} 生成故事草稿`
        : `Story draft cloned from ${selectedStory.title}`,
      "success",
    );
  });
}

function renderStoryDetail() {
  const root = $("story-detail");
  const selected = state.selectedStoryId;
  if (state.loading.storyDetail && selected) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    renderStoryInspector();
    return;
  }
  if (selected !== lastRenderedStoryDetailId) {
    state.storyDetailView = "overview";
    lastRenderedStoryDetailId = selected;
  }
  const story = state.storyDetails[selected] || state.stories.find((candidate) => candidate.id === selected);
  if (!story) {
    lastRenderedStoryDetailId = "";
    root.innerHTML = state.stories.length
      ? `<div class="empty">${copy("No story is selected in the current filtered workspace.", "当前筛选后的工作区里没有选中的故事。")}</div>`
      : `
          ${renderLifecycleGuideCard({
            title: copy("Stories are the promoted evidence layer", "故事层是被提升后的证据层"),
            summary: copy(
              "Seed a story manually here when editorial context comes first, or promote one directly from Triage once verified signal is ready. The browser flow does not require a CLI detour.",
              "如果编辑背景先于聚类出现，可以先在这里手工起一个故事；如果分诊里的已核验证据已经准备好，也可以直接从分诊提升。整个流程不需要再绕回 CLI。"
            ),
            steps: [
              {
                title: copy("Review Triage", "先看分诊"),
                copy: copy("Use Triage when the story should be grounded in reviewed inbox evidence.", "当故事需要建立在已审阅的收件箱证据上时，先从分诊开始。"),
              },
              {
                title: copy("Create Story", "创建故事"),
                copy: copy("Story Intake captures a manual brief when the narrative should exist immediately.", "如果叙事需要先落下来，故事录入可以直接创建手工简报。"),
              },
              {
                title: copy("Refine Summary", "完善摘要"),
                copy: copy("The workspace lets you tune title, summary, status, and evidence context in one place.", "工作台会把标题、摘要、状态和证据上下文集中到一个位置继续打磨。"),
              },
              {
                title: copy("Prepare Delivery", "准备交付"),
                copy: copy("Attach routes from missions once the story is ready to notify downstream teams.", "当故事准备好触发下游通知时，再回到任务里绑定路由。"),
              },
            ],
            actions: [
              { label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true },
              { label: copy("Open Triage", "打开分诊"), section: "section-triage" },
              { label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" },
            ],
          })}
          <div class="empty">${copy("No persisted story snapshot yet.", "当前还没有持久化故事快照。")}</div>
        `;
    wireLifecycleGuideActions(root);
    scheduleCanvasTextFit(root);
    renderStoryInspector();
    return;
  }
  const activeDetailView = normalizeStoryDetailView(state.storyDetailView);
  state.storyDetailView = activeDetailView;
  const storyEvidenceIds = getStoryEvidenceIds(story);
  const storyDeliveryStatus = getStoryDeliveryStatus(story);
  const storySignal = getGovernanceSignal("story_conversion");
  const alertSignal = getGovernanceSignal("alert_yield");
  const routeSummary = state.ops?.route_summary || {};
  const evidenceBlock = (rows, emptyLabel) => rows.length
    ? rows.map((row) => `
        <div class="card">
          <div class="card-top">
            <div>
                <h3 class="card-title">${row.title}</h3>
                <div class="meta">
                  <span>${row.item_id}</span>
                  <span>${row.source_name || row.source_type || "-"}</span>
                  <span>${copy("score", "分数")}=${row.score || 0}</span>
                  <span>${copy("confidence", "置信度")}=${Number(row.confidence || 0).toFixed(2)}</span>
                </div>
              </div>
            <span class="chip ${row.role === "primary" ? "ok" : ""}">${copy(row.role || "secondary", row.role === "primary" ? "主证据" : "次证据")}</span>
          </div>
          <div class="panel-sub">${row.url || "-"}</div>
          <div class="actions">
            <button class="btn-secondary" type="button" data-story-evidence-triage="${row.item_id}">${copy("Open In Triage", "回到分诊")}</button>
          </div>
        </div>
      `).join("")
    : `<div class="empty">${emptyLabel}</div>`;
  const contradictionBlock = (story.contradictions || []).length
    ? story.contradictions.map((conflict) => `
        <div class="card">
          <div class="card-top">
            <div>
                <h3 class="card-title">${conflict.topic}</h3>
                <div class="meta">
                <span>${copy("positive", "正向")}=${conflict.positive || 0}</span>
                <span>${copy("negative", "负向")}=${conflict.negative || 0}</span>
                <span>${copy("neutral", "中性")}=${conflict.neutral || 0}</span>
                </div>
              </div>
            <span class="chip hot">${copy("conflict", "冲突")}</span>
          </div>
          <div class="panel-sub">${conflict.note || copy("Cross-source stance divergence detected.", "检测到跨来源立场分歧。")}</div>
        </div>
      `).join("")
    : `<div class="empty">${copy("No contradiction marker in this story.", "这个故事没有冲突标记。")}</div>`;
  const timelineBlock = (story.timeline || []).length
    ? story.timeline.map((event) => `
        <div class="card">
          <div class="card-top">
            <div>
                <h3 class="card-title">${event.title}</h3>
                <div class="meta">
                  <span>${event.time || "-"}</span>
                  <span>${event.source_name || "-"}</span>
                  <span>${copy("role", "角色")}=${copy(event.role || "secondary", event.role === "primary" ? "主证据" : "次证据")}</span>
                  <span>${copy("score", "分数")}=${event.score || 0}</span>
                </div>
              </div>
            </div>
          <div class="panel-sub">${event.url || "-"}</div>
        </div>
      `).join("")
    : `<div class="empty">${copy("No timeline event captured.", "当前没有时间线事件。")}</div>`;
  const graphPreview = renderStoryGraph(state.storyGraph[selected]);
  const storyContinuityBlock = renderLifecycleContinuityCard({
    title: copy("Story Delivery Readiness", "故事交付就绪度"),
    summary: copy(
      "Evidence, story editing, and downstream delivery status stay connected around the same narrative object.",
      "证据、故事编辑和下游交付状态会继续围绕同一个叙事对象保持连贯。"
    ),
    stages: [
      {
        kicker: copy("Review", "审阅"),
        title: copy("Evidence Context", "证据上下文"),
        copy: copy(
          "Primary and secondary evidence stay visible so the story never drifts away from reviewed signal.",
          "主次证据会继续保持可见，避免故事脱离已审阅信号。"
        ),
        tone: storyEvidenceIds.length ? "ok" : "",
        facts: [
          { label: copy("Evidence", "证据"), value: String(storyEvidenceIds.length) },
          { label: copy("Primary item", "主条目"), value: story.primary_item_id || "-" },
          { label: copy("Conflicts", "冲突"), value: String((story.contradictions || []).length) },
        ],
      },
      {
        kicker: copy("Current", "当前"),
        title: copy("Story Workspace", "故事工作台"),
        copy: copy(
          "Narrative edits happen beside evidence, timeline, and entity structure instead of in a detached editor.",
          "叙事编辑会与证据、时间线和实体结构并排存在，而不是进入一个脱离上下文的编辑器。"
        ),
        tone: storyDeliveryStatus.tone || "ok",
        facts: [
          { label: copy("Status", "状态"), value: localizeWord(story.status || "active") },
          { label: copy("Updated", "更新"), value: formatCompactDateTime(story.updated_at || story.generated_at || "") },
          { label: copy("Delivery", "交付"), value: storyDeliveryStatus.label },
        ],
      },
      {
        kicker: copy("Delivery", "交付"),
        title: copy("Output Handoff", "输出交接"),
        copy: copy(
          "Ready stories, alerting missions, and route health stay nearby so the delivery decision is visible before you leave the workspace.",
          "待交付故事、触发告警的任务和路由健康会保留在附近，方便在离开工作台前判断是否该进入交付。"
        ),
        tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
        facts: [
          { label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) },
          { label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) },
          { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
        ],
      },
    ],
    actions: [
      { label: copy("Focus Evidence In Triage", "回查分诊证据"), section: "section-triage", primary: true },
      { label: copy("Open Delivery", "打开交付"), section: "section-ops" },
      { label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" },
    ],
  });
  const storyGuidanceBlock = buildStoryGuidanceSurface(story, storyDeliveryStatus);
  const storyOverviewFacts = `
    <div class="story-fact-grid">
      <div class="story-fact-card">
        <div class="mono">${copy("evidence", "证据")}</div>
        <div class="story-fact-value">${storyEvidenceIds.length}</div>
        <div class="story-fact-copy">${copy(
          `${(story.primary_evidence || []).length} primary / ${(story.secondary_evidence || []).length} secondary items stay attached to this story.`,
          `${(story.primary_evidence || []).length} 条主证据 / ${(story.secondary_evidence || []).length} 条次证据继续挂在这条故事上。`
        )}</div>
      </div>
      <div class="story-fact-card">
        <div class="mono">${copy("delivery", "交付")}</div>
        <div class="story-fact-value">${storyDeliveryStatus.label}</div>
        <div class="story-fact-copy">${copy(
          "Readiness stays visible here before the operator exports or routes the story downstream.",
          "在操作者导出或路由下游前，这里会继续直接显示交付就绪度。"
        )}</div>
      </div>
      <div class="story-fact-card">
        <div class="mono">${copy("contradictions", "冲突")}</div>
        <div class="story-fact-value">${(story.contradictions || []).length}</div>
        <div class="story-fact-copy">${copy(
          `${(story.timeline || []).length} timeline events and ${(story.entities || []).length} entities remain available in Evidence view.`,
          `${(story.timeline || []).length} 条时间线事件和 ${(story.entities || []).length} 个实体会继续留在证据视图里。`
        )}</div>
      </div>
      <div class="story-fact-card">
        <div class="mono">${copy("updated", "更新")}</div>
        <div class="story-fact-value">${formatCompactDateTime(story.updated_at || story.generated_at || "") || "-"}</div>
        <div class="story-fact-copy">${copy(
          "Use the editor surface only for title, summary, and status changes to keep the object stable.",
          "编辑面只负责标题、摘要和状态，避免对象语义继续发散。"
        )}</div>
      </div>
    </div>
  `;
  const storyOverviewPane = `
    <div class="story-detail-pane" data-story-detail-pane="overview">
      ${storyOverviewFacts}
      ${storyContinuityBlock}
      ${storyGuidanceBlock}
    </div>
  `;
  const storyEditorPane = `
    <div class="story-detail-pane" data-story-detail-pane="editor">
      <div class="card">
        <div class="story-pane-head">
          <div>
            <div class="mono">${copy("story editor", "故事编辑器")}</div>
            <h3 class="card-title" style="margin-top:10px;">${copy("Edit The Persisted Narrative Object", "编辑这条持久化叙事对象")}</h3>
          </div>
          <span class="chip ok">${copy("editable", "可编辑")}</span>
        </div>
        <div class="panel-sub story-pane-copy">${copy(
          "Keep edits limited to title, summary, and status. Raw markdown and JSON previews now live in the export sheet instead of this main column.",
          "这里只改标题、摘要和状态。Markdown 与 JSON 预览已经移到导出 sheet，不再挤占主列。"
        )}</div>
        <form id="story-editor-form" data-story-id="${story.id}" style="margin-top:12px;">
          <div class="field-grid">
            <label>${copy("Story Title", "故事标题")}<input name="title" value="${escapeHtml(story.title || "")}" placeholder="${copy("OpenAI Launch Story", "OpenAI 发布故事")}"></label>
            <label>${copy("Story Status", "故事状态")}
              <select name="status">
                ${storyStatusOptions.map((value) => `<option value="${value}" ${(story.status || "active") === value ? "selected" : ""}>${localizeWord(value)}</option>`).join("")}
              </select>
            </label>
          </div>
          <label>${copy("Story Summary", "故事摘要")}<textarea name="summary" rows="4" placeholder="${copy("Condense why this story matters right now.", "简要说明这个故事此刻为什么重要。")}">${escapeHtml(story.summary || "")}</textarea></label>
          <div class="toolbar">
            <button class="btn-primary" type="submit">${copy("Save Story", "保存故事")}</button>
            <button class="btn-secondary" type="button" data-story-detail-status="${story.status === "archived" ? "active" : "archived"}">${story.status === "archived" ? copy("Restore Story", "恢复故事") : copy("Archive Story", "归档故事")}</button>
            <button class="btn-danger" type="button" data-story-delete="${story.id}">${copy("Delete Story", "删除故事")}</button>
          </div>
        </form>
      </div>
    </div>
  `;
  const storyEvidencePane = `
    <div class="story-detail-pane" data-story-detail-pane="evidence">
      <div class="card">
        <div class="story-pane-head">
          <div>
            <div class="mono">${copy("evidence desk", "证据工作台")}</div>
            <h3 class="card-title" style="margin-top:10px;">${copy("Primary Proof, Contradictions, And Structure Stay Together", "主证据、冲突和结构分析留在同一层")}</h3>
          </div>
          <span class="chip">${copy("read-only analysis", "只读分析")}</span>
        </div>
        <div class="panel-sub story-pane-copy">${copy(
          "This tab keeps operational proof nearby while the Overview stays readable and the Editor stays narrow.",
          "把操作所需的证据集中到这里，避免总览过重，也让编辑面保持收敛。"
        )}</div>
      </div>
      <div class="story-columns">
        <div class="stack">
          <div class="meta"><span class="mono">${copy("primary evidence", "主证据")}</span><span class="chip">${copy("read-only snapshot", "只读快照")}</span></div>
          ${evidenceBlock(story.primary_evidence || [], copy("No primary evidence captured.", "没有主证据。"))}
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${copy("secondary evidence", "次证据")}</span><span class="chip">${copy("read-only snapshot", "只读快照")}</span></div>
          ${evidenceBlock(story.secondary_evidence || [], copy("No secondary evidence captured.", "没有次证据。"))}
        </div>
      </div>
      <div class="stack">
        <div class="meta"><span class="mono">${copy("contradiction markers", "冲突标记")}</span><span class="chip">${copy("read-only analysis", "只读分析")}</span></div>
        ${contradictionBlock}
      </div>
      <div class="stack">
        <div class="meta"><span class="mono">${copy("timeline", "时间线")}</span><span class="chip">${copy("read-only analysis", "只读分析")}</span></div>
        ${timelineBlock}
      </div>
      <div class="stack">
        <div class="meta"><span class="mono">${copy("entity graph", "实体图谱")}</span><span class="chip">${copy("read-only analysis", "只读分析")}</span></div>
        ${graphPreview}
      </div>
    </div>
  `;
  const detailViewLabels = {
    overview: copy("Overview", "总览"),
    editor: copy("Editor", "编辑"),
    evidence: copy("Evidence", "证据"),
  };
  const activePane = activeDetailView === "editor"
    ? storyEditorPane
    : (activeDetailView === "evidence" ? storyEvidencePane : storyOverviewPane);
  root.innerHTML = `
    <div class="story-detail-shell">
      <div class="card">
      <div class="card-top">
        <div>
          <h3 class="card-title">${story.title}</h3>
          <div class="meta">
            <span>${story.id}</span>
            <span>${copy("status", "状态")}=${localizeWord(story.status || "active")}</span>
            <span>${copy("items", "条目")}=${story.item_count || 0}</span>
            <span>${copy("sources", "来源")}=${story.source_count || 0}</span>
            <span>${copy("score", "分数")}=${Number(story.score || 0).toFixed(1)}</span>
            <span>${copy("confidence", "置信度")}=${Number(story.confidence || 0).toFixed(2)}</span>
          </div>
        </div>
        <span class="chip ${(story.contradictions || []).length ? "hot" : "ok"}">${(story.contradictions || []).length ? copy("mixed signals", "信号冲突") : copy("aligned", "一致")}</span>
      </div>
      <div class="panel-sub">${story.summary || copy("No summary captured.", "没有记录到摘要。")}</div>
      <div class="entity-row">
        ${(story.entities || []).slice(0, 8).map((entity) => `<span class="chip">${entity}</span>`).join("") || `<span class="chip">${copy("no entities", "无实体")}</span>`}
      </div>
      <div class="story-detail-toolbar">
        <div class="ui-segment" role="tablist" aria-label="${escapeHtml(copy("Story workspace panels", "故事工作台分段"))}">
          ${storyDetailViewOptions.map((view) => `
            <button class="ui-segment-button ${activeDetailView === view ? "active" : ""}" type="button" data-story-detail-view="${view}" aria-pressed="${activeDetailView === view ? "true" : "false"}">${escapeHtml(detailViewLabels[view])}</button>
          `).join("")}
        </div>
        <div class="actions story-detail-actions">
          <button class="btn-secondary" data-story-markdown="${story.id}">${copy("Preview Markdown", "预览 Markdown")}</button>
          <button class="btn-secondary" type="button" data-story-json="${story.id}">${copy("Inspect JSON", "查看 JSON")}</button>
          <button class="btn-secondary" type="button" data-story-focus-triage="${story.id}" ${storyEvidenceIds.length ? "" : "disabled"}>${copy("Focus Evidence In Triage", "回查分诊证据")}</button>
        </div>
      </div>
    </div>
    ${activePane}
  </div>
  `;

  root.querySelectorAll("[data-story-detail-view]").forEach((button) => {
    button.addEventListener("click", () => {
      state.storyDetailView = normalizeStoryDetailView(button.dataset.storyDetailView);
      renderStoryDetail();
    });
  });
  root.querySelectorAll("[data-story-markdown]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await previewStoryMarkdown(button.dataset.storyMarkdown);
      } catch (error) {
        reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelectorAll("[data-story-json]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await previewStoryJson(button.dataset.storyJson);
      } catch (error) {
        reportError(error, copy("Inspect story JSON", "查看故事 JSON"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelector("[data-story-focus-triage]")?.addEventListener("click", () => {
    focusTriageEvidence(storyEvidenceIds, { itemId: story.primary_item_id || storyEvidenceIds[0] || "" });
  });
  root.querySelectorAll("[data-story-evidence-triage]").forEach((button) => {
    button.addEventListener("click", () => {
      const itemId = String(button.dataset.storyEvidenceTriage || "").trim();
      if (!itemId) {
        return;
      }
      focusTriageEvidence(storyEvidenceIds, { itemId });
    });
  });

  const storyEditorForm = document.getElementById("story-editor-form");
  if (storyEditorForm) {
    storyEditorForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(storyEditorForm);
      const payload = {
        title: String(form.get("title") || "").trim(),
        summary: String(form.get("summary") || "").trim(),
        status: String(form.get("status") || "").trim(),
      };
      if (!payload.title) {
        showToast(copy("Provide a story title before saving.", "保存前请先填写故事标题。"), "error");
        return;
      }
      const submitButton = storyEditorForm.querySelector("button[type='submit']");
      if (submitButton) {
        submitButton.disabled = true;
      }
      const previousStory = {
        title: story.title || "",
        summary: story.summary || "",
        status: story.status || "active",
      };
      if (state.storyDetails[story.id]) {
        state.storyDetails[story.id] = {
          ...state.storyDetails[story.id],
          ...payload,
        };
      }
      renderStories();
      try {
        await api(`/api/stories/${story.id}`, {
          method: "PUT",
          payload,
        });
        state.storyMarkdown[story.id] = "";
        pushActionEntry({
          kind: copy("story update", "故事更新"),
          label: state.language === "zh" ? `已更新故事：${payload.title}` : `Updated story ${payload.title}`,
          detail: state.language === "zh" ? `当前故事状态为 ${localizeWord(payload.status || "active")}。` : `Story status is now ${payload.status || "active"}.`,
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
          state.language === "zh" ? `故事已更新：${payload.title}` : `Story updated: ${payload.title}`,
          "success",
        );
      } catch (error) {
        if (state.storyDetails[story.id]) {
          state.storyDetails[story.id] = {
            ...state.storyDetails[story.id],
            ...previousStory,
          };
        }
        renderStories();
        reportError(error, copy("Update story", "更新故事"));
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  }
  root.querySelector("[data-story-detail-status]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await setStoryStatusQuick(story.id, String(button.dataset.storyDetailStatus || ""));
    } catch (error) {
      reportError(error, copy("Update story state", "更新故事状态"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-story-delete]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await deleteStoryFromWorkspace(String(button.dataset.storyDelete || story.id));
    } catch (error) {
      reportError(error, copy("Delete story", "删除故事"));
    } finally {
      button.disabled = false;
    }
  });
  wireLifecycleGuideActions(root);
  scheduleCanvasTextFit(root);
  renderStoryInspector();
}

function renderStories() {
  const root = $("story-list");
  const inlineStats = $("story-stats-inline");
  renderStoryViewJumpStrip();
  renderStoryCreateDeck();
  if (state.loading.board && !state.stories.length) {
    renderStorySectionSummary();
    inlineStats.innerHTML = `<span>${copy("loading", "加载中")}=stories</span>`;
    root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
    $("story-detail").innerHTML = skeletonCard(5);
    renderTopbarContext();
    return;
  }
  const contradictions = state.stories.reduce((count, story) => count + ((story.contradictions || []).length ? 1 : 0), 0);
  const totalEvidence = state.stories.reduce((count, story) => count + (story.item_count || 0), 0);
  const storySearchValue = String(state.storySearch || "");
  const storySearchQuery = storySearchValue.trim().toLowerCase();
  const storyFilter = normalizeStoryFilter(state.storyFilter);
  const storySort = normalizeStorySort(state.storySort);
  const activeStoryView = detectStoryViewPreset({ filter: storyFilter, sort: storySort, search: storySearchValue });
  const matchedStories = state.stories.filter((story) => {
    const storyStatus = String(story.status || "active").trim().toLowerCase() || "active";
    if (storyFilter === "conflicted" && !(Array.isArray(story.contradictions) && story.contradictions.length)) {
      return false;
    }
    if (storyFilter !== "all" && storyFilter !== "conflicted" && storyStatus !== storyFilter) {
      return false;
    }
    if (!storySearchQuery) {
      return true;
    }
    const primaryTitles = Array.isArray(story.primary_evidence)
      ? story.primary_evidence.map((row) => String(row.title || "")).join(" ")
      : "";
    const haystack = [
      story.id,
      story.title,
      story.summary,
      ...(Array.isArray(story.entities) ? story.entities : []),
      primaryTitles,
    ].join(" ").toLowerCase();
    return haystack.includes(storySearchQuery);
  });
  const filteredStories = [...matchedStories].sort((left, right) => compareStoriesByWorkspaceOrder(left, right, storySort));
  const defaultStoryId = filteredStories[0] ? filteredStories[0].id : (state.stories[0] ? state.stories[0].id : "");
  const visibleStoryIds = new Set(filteredStories.map((story) => story.id));
  state.selectedStoryIds = uniqueValues(state.selectedStoryIds).filter((storyId) => visibleStoryIds.has(storyId));
  const storyFilterOptions = [
    { key: "all", label: copy("all", "全部"), count: state.stories.length },
    { key: "conflicted", label: copy("conflicted", "冲突"), count: contradictions },
    ...["active", "monitoring", "resolved", "archived"].map((key) => ({
      key,
      label: localizeWord(key),
      count: state.stories.filter((story) => (String(story.status || "active").trim().toLowerCase() || "active") === key).length,
    })),
  ];
  inlineStats.innerHTML = `
    <span>${copy("stories", "故事")}=${state.stories.length}</span>
    <span>${copy("evidence", "证据")}=${totalEvidence}</span>
    <span>${copy("contradicted", "冲突故事")}=${contradictions}</span>
    <span>${copy("shown", "显示")}=${filteredStories.length}</span>
    <span>${copy("view", "视图")}=${storyViewPresetLabel(activeStoryView)}</span>
    <span>${copy("sort", "排序")}=${storySortLabel(storySort)}</span>
    <span>${copy("selected", "已选")}=${state.selectedStoryIds.length}</span>
    <span>${copy("selected", "选中")}=${state.selectedStoryId || "-"}</span>
  `;
  const storyBatchCount = state.selectedStoryIds.length;
  const storyBatchBusy = Boolean(state.storyBulkBusy);
  const storySearchCard = `
    <div class="card section-toolbox">
      <div class="section-toolbox-head">
        <div>
          <div class="mono">${copy("story search", "故事搜索")}</div>
          <div class="panel-sub">${copy("Search by story title, summary, entity, id, or primary evidence title before opening the workspace.", "可按故事标题、摘要、实体、故事 ID 或主证据标题快速定位。")}</div>
        </div>
        <div class="section-toolbox-meta">
          <button class="btn-secondary" type="button" data-story-deck-focus>${copy("New Story", "新建故事")}</button>
          <span class="chip ${activeStoryView === "custom" ? "hot" : "ok"}">${storyViewPresetLabel(activeStoryView)}</span>
          <span class="chip ok">${storySortLabel(storySort)}</span>
          <span class="chip">${copy("shown", "显示")}=${filteredStories.length}</span>
          <span class="chip">${copy("total", "总数")}=${state.stories.length}</span>
        </div>
      </div>
      <div class="search-shell">
        <input type="search" value="${escapeHtml(storySearchValue)}" data-story-search placeholder="${copy("Search stories", "搜索故事")}">
        <button class="btn-secondary" type="button" data-story-search-clear ${storySearchValue.trim() ? "" : "disabled"}>${copy("Clear", "清空")}</button>
      </div>
      <div class="field-grid" style="margin-top:12px;">
        <label>${copy("Story Sort", "故事排序")}
          <select data-story-sort>
            ${storySortOptions.map((option) => `<option value="${option}" ${storySort === option ? "selected" : ""}>${storySortLabel(option)}</option>`).join("")}
          </select>
        </label>
        <div>
          <div class="mono">${copy("view hint", "视图提示")}</div>
          <div class="panel-sub">${activeStoryView === "custom" ? storySortSummary(storySort) : storyViewPresetDescription(activeStoryView)}</div>
        </div>
      </div>
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Story view presets", "故事视图预设"))}">
        ${storyViewPresetOptions.map((option) => `
          <button class="ui-segment-button ${activeStoryView === option ? "active" : ""}" type="button" data-story-view="${escapeHtml(option)}" aria-pressed="${activeStoryView === option ? "true" : "false"}">${escapeHtml(storyViewPresetLabel(option))}</button>
        `).join("")}
      </div>
      <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(copy("Story status filters", "故事状态筛选"))}">
        ${storyFilterOptions.map((option) => `
          <button class="ui-segment-button ${storyFilter === option.key ? "active" : ""}" type="button" data-story-filter="${escapeHtml(option.key)}" aria-pressed="${storyFilter === option.key ? "true" : "false"}">${escapeHtml(option.label)} (${option.count || 0})</button>
        `).join("")}
      </div>
    </div>
  `;
  const storyBatchToolbar = `
    <div class="card batch-toolbar-card ${storyBatchCount ? "selection-live" : ""}">
      <div class="batch-toolbar">
        <div class="batch-toolbar-head">
          <div>
            <div class="mono">${copy("story batch", "故事批量操作")}</div>
            <div class="panel-sub">${
              storyBatchCount
                ? copy(`Selected ${storyBatchCount} stories. Move them together to reduce workspace churn.`, `已选 ${storyBatchCount} 条故事，可以一起切换状态。`)
                : copy("Select visible stories when you need to archive, monitor, or resolve a whole lane together.", "当你需要整体归档、恢复监控或批量解决时，可以先选择当前可见故事。")
            }</div>
          </div>
          <span class="chip ${storyBatchCount ? "ok" : ""}">${copy("selected", "已选")}=${storyBatchCount}</span>
        </div>
        ${
          storyBatchCount
            ? `<div class="actions">
                <button class="btn-secondary" type="button" data-story-selection-clear ${storyBatchBusy ? "disabled" : ""}>${copy("Clear Selection", "清空选择")}</button>
                <button class="btn-secondary" type="button" data-story-batch-status="monitoring" ${storyBatchBusy ? "disabled" : ""}>${copy("Batch Monitor", "批量监控")}</button>
                <button class="btn-secondary" type="button" data-story-batch-status="resolved" ${storyBatchBusy ? "disabled" : ""}>${copy("Batch Resolve", "批量解决")}</button>
                <button class="btn-secondary" type="button" data-story-batch-status="archived" ${storyBatchBusy ? "disabled" : ""}>${copy("Batch Archive", "批量归档")}</button>
              </div>`
            : `<div class="actions">
                <button class="btn-secondary" type="button" data-story-select-visible ${(!filteredStories.length || storyBatchBusy) ? "disabled" : ""}>${copy("Select Visible", "选择当前列表")}</button>
              </div>`
        }
      </div>
    </div>
  `;
  if (!state.stories.length) {
    renderStorySectionSummary({
      filteredStories: [],
      activeStoryView,
      storySort,
      storySearchValue,
    });
    root.innerHTML = `${storySearchCard}${storyBatchToolbar}${renderLifecycleGuideCard({
      title: copy("Promote verified signal into a story without leaving the browser", "无需离开浏览器，也能把已核验信号提升为故事"),
      summary: copy(
        "Use Story Intake for a manual brief, or create a story from Triage once the queue has enough evidence. Story edits, evidence review, and route setup can all stay inside this shell.",
        "可以用故事录入先写一条手工简报，也可以在分诊证据足够时直接提升成故事。后续的故事编辑、证据回查和路由设置都可以继续留在这个界面里完成。"
      ),
      steps: [
        {
          title: copy("Start From Triage", "从分诊开始"),
          copy: copy("Create Story is the fastest path when verified inbox evidence already exists.", "如果收件箱里已经有已核验证据，直接创建故事是最快路径。"),
        },
        {
          title: copy("Or Seed Manually", "或手工起稿"),
          copy: copy("Story Intake is better when the narrative needs to exist before clustering catches up.", "如果叙事需要先存在、而聚类还没跟上，故事录入会更合适。"),
        },
        {
          title: copy("Refine In Workspace", "在工作台完善"),
          copy: copy("Tune title, summary, status, contradictions, and evidence context here.", "标题、摘要、状态、冲突点和证据上下文都可以在这里继续完善。"),
        },
        {
          title: copy("Link Delivery", "连接交付"),
          copy: copy("Attach named routes from missions once the story is ready for downstream notification.", "当故事准备好通知下游时，再从任务里把命名路由接上。"),
        },
      ],
      actions: [
        { label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true },
        { label: copy("Open Triage", "打开分诊"), section: "section-triage" },
        { label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" },
      ],
    })}<div class="empty">${copy("No story snapshot yet.", "当前还没有故事快照。")}</div>`;
    wireLifecycleGuideActions(root);
    root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {
      focusStoryDeck("title");
    });
    root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {
      state.storySearch = event.target.value;
      renderStories();
    });
    root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {
      state.storySearch = "";
      renderStories();
    });
    root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {
      state.storySort = normalizeStorySort(event.target.value);
      persistStoryWorkspacePrefs();
      renderStories();
    });
    root.querySelectorAll("[data-story-view]").forEach((button) => {
      button.addEventListener("click", () => {
        applyStoryViewPreset(String(button.dataset.storyView || "").trim());
      });
    });
    root.querySelectorAll("[data-story-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
        persistStoryWorkspacePrefs();
        renderStories();
      });
    });
    syncStoryUrlState({ defaultStoryId });
    flushStoryUrlFocus();
    renderTopbarContext();
    renderStoryDetail();
    return;
  }
  if (filteredStories.length && !filteredStories.some((story) => story.id === state.selectedStoryId)) {
    state.selectedStoryId = filteredStories[0].id;
  }
  if (!filteredStories.length) {
    state.selectedStoryId = "";
    renderStorySectionSummary({
      filteredStories: [],
      activeStoryView,
      storySort,
      storySearchValue,
    });
    root.innerHTML = `${storySearchCard}${storyBatchToolbar}<div class="empty">${copy("No story matched the current search or filter.", "没有故事匹配当前搜索或筛选。")}</div>`;
    renderStoryDetail();
    root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {
      focusStoryDeck("title");
    });
    root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {
      state.storySearch = event.target.value;
      renderStories();
    });
    root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {
      state.storySearch = "";
      renderStories();
    });
    root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {
      state.storySort = normalizeStorySort(event.target.value);
      persistStoryWorkspacePrefs();
      renderStories();
    });
    root.querySelectorAll("[data-story-view]").forEach((button) => {
      button.addEventListener("click", () => {
        applyStoryViewPreset(String(button.dataset.storyView || "").trim());
      });
    });
    root.querySelectorAll("[data-story-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
        persistStoryWorkspacePrefs();
        renderStories();
      });
    });
    syncStoryUrlState({ defaultStoryId });
    flushStoryUrlFocus();
    renderTopbarContext();
    return;
  }
  renderStorySectionSummary({
    filteredStories,
    activeStoryView,
    storySort,
    storySearchValue,
  });
  root.innerHTML = `${storySearchCard}${storyBatchToolbar}${filteredStories.map((story) => {
    const selected = story.id === state.selectedStoryId ? "selected" : "";
    const primary = (story.primary_evidence || [])[0];
    const updatedLabel = formatCompactDateTime(story.updated_at || story.generated_at || "");
    const priority = describeStoryPriority(story);
    const deliveryStatus = getStoryDeliveryStatus(story);
    const actionHierarchy = getStoryCardActionHierarchy(story);
    return `
      <div class="card selectable ${selected}" data-story-card="${story.id}">
        <div class="card-top">
          <div>
            <label class="checkbox-inline" style="margin-bottom:8px;">
              <input type="checkbox" data-story-select="${story.id}" ${isStorySelected(story.id) ? "checked" : ""}>
              <span>${copy("select", "选择")}</span>
            </label>
            <h3 class="card-title">${story.title}</h3>
            <div class="meta">
              <span>${story.id}</span>
              <span>${copy("status", "状态")}=${localizeWord(story.status || "active")}</span>
              <span>${copy("updated", "更新")}=${updatedLabel}</span>
            </div>
            <div class="meta">
              <span>${copy("items", "条目")}=${story.item_count || 0}</span>
              <span>${copy("sources", "来源")}=${story.source_count || 0}</span>
              <span>${copy("score", "分数")}=${Number(story.score || 0).toFixed(1)}</span>
              <span>${copy("confidence", "置信度")}=${Number(story.confidence || 0).toFixed(2)}</span>
            </div>
          </div>
          <span class="chip ${(story.contradictions || []).length ? "hot" : "ok"}">${(story.contradictions || []).length ? copy("mixed", "冲突") : copy("aligned", "一致")}</span>
        </div>
        <div class="panel-sub">${story.summary || copy("No summary captured.", "没有记录到摘要。")}</div>
        <div class="entity-row">
          <span class="chip ${priority.tone}">${priority.label}</span>
          ${(story.entities || []).slice(0, 4).map((entity) => `<span class="chip">${entity}</span>`).join("") || `<span class="chip">${copy("no entities", "无实体")}</span>`}
        </div>
        <div class="meta">
          <span>${copy("primary", "主证据")}=${primary ? primary.title : "-"}</span>
          <span>${copy("timeline", "时间线")}=${(story.timeline || []).length}</span>
          <span>${copy("conflicts", "冲突")}=${(story.contradictions || []).length}</span>
          <span>${copy("delivery", "交付")}=${deliveryStatus.label}</span>
        </div>
        ${renderCardActionHierarchy(actionHierarchy)}
      </div>
    `;
  }).join("")}`;

  root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {
    focusStoryDeck("title");
  });

  root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {
    state.storySearch = event.target.value;
    renderStories();
  });

  root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {
    state.storySearch = "";
    renderStories();
  });

  root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {
    state.storySort = normalizeStorySort(event.target.value);
    persistStoryWorkspacePrefs();
    renderStories();
  });

  root.querySelectorAll("[data-story-view]").forEach((button) => {
    button.addEventListener("click", () => {
      applyStoryViewPreset(String(button.dataset.storyView || "").trim());
    });
  });

  root.querySelector("[data-story-select-visible]")?.addEventListener("click", () => {
    selectVisibleStories(filteredStories);
    renderStories();
  });

  root.querySelector("[data-story-selection-clear]")?.addEventListener("click", () => {
    clearStorySelection();
    renderStories();
  });

  root.querySelectorAll("[data-story-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
      persistStoryWorkspacePrefs();
      renderStories();
    });
  });

  root.querySelectorAll("[data-story-batch-status]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await runStoryBatchStatusUpdate(state.selectedStoryIds, String(button.dataset.storyBatchStatus || "").trim());
      } catch (error) {
        reportError(error, copy("Batch update stories", "批量更新故事"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-story-card]").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("button, textarea, input, select, a, form, label")) {
        return;
      }
      state.selectedStoryId = String(card.dataset.storyCard || "").trim();
      renderStories();
    });
  });

  root.querySelectorAll("[data-story-select]").forEach((input) => {
    input.addEventListener("change", () => {
      toggleStorySelection(String(input.dataset.storySelect || "").trim(), input.checked);
      renderStories();
    });
  });

  root.querySelectorAll("[data-story-open]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        const requestedMode = String(button.dataset.storyOpenMode || "").trim();
        await loadStory(button.dataset.storyOpen, {
          mode: requestedMode || undefined,
          syncUrl: true,
        });
      } catch (error) {
        reportError(error, copy("Open story", "打开故事"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-story-preview]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await previewStoryMarkdown(button.dataset.storyPreview);
      } catch (error) {
        reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-story-quick-status]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await setStoryStatusQuick(
          String(button.dataset.storyQuickStatus || ""),
          String(button.dataset.storyNextStatus || ""),
        );
      } catch (error) {
        reportError(error, copy("Update story state", "更新故事状态"));
      } finally {
        button.disabled = false;
      }
    });
  });

  syncStoryUrlState({ defaultStoryId });
  flushStoryUrlFocus();
  renderTopbarContext();
  renderStoryDetail();
}
