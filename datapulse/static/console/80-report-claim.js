// Split group 2h: claim composer, report studio, hydration helpers, and board refresh orchestration.
// Depends on prior fragments and 00-common.js.

function renderReportQualityBlock(quality) {
  if (!quality || typeof quality !== "object") {
    return `<div class="empty">${copy("No quality snapshot yet. Refresh the report composition to inspect guardrails.", "还没有质量快照。刷新一次报告编排后再查看门禁。")}</div>`;
  }
  const checks = quality.checks && typeof quality.checks === "object" ? quality.checks : {};
  const renderedChecks = Object.entries(checks).length
    ? Object.entries(checks).map(([key, check]) => {
        const status = String(check?.status || "draft").trim().toLowerCase();
        const issues = Array.isArray(check?.issues)
          ? check.issues
          : (Array.isArray(check?.entries) ? check.entries : []);
        const summaryPairs = check?.summary && typeof check.summary === "object"
          ? Object.entries(check.summary)
          : [];
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${escapeHtml(formatReportCheckLabel(key))}</h3>
                <div class="meta">
                  <span>${copy("status", "状态")}=${escapeHtml(localizeWord(status || "draft"))}</span>
                  ${summaryPairs.map(([summaryKey, summaryValue]) => `<span>${escapeHtml(String(summaryKey).replace(/_/g, " "))}=${escapeHtml(String(summaryValue))}</span>`).join("")}
                </div>
              </div>
              <span class="chip ${reportStatusTone(status)}">${escapeHtml(localizeWord(status || "draft"))}</span>
            </div>
            <div class="stack">
              ${issues.length
                ? issues.slice(0, 4).map((issue) => `
                    <div class="card">
                      <div class="panel-sub">${escapeHtml(issue.detail || issue.kind || JSON.stringify(issue))}</div>
                    </div>
                  `).join("")
                : `<div class="empty">${copy("No blocking issue recorded for this gate.", "这个门禁当前没有阻断问题。")}</div>`}
            </div>
          </div>
        `;
      }).join("")
    : `<div class="empty">${copy("No guardrail checks were returned.", "当前没有返回质量门禁检查。")}</div>`;

  return `
    <div class="card">
      <div class="card-top">
        <div>
          <h3 class="card-title">${copy("Quality Guardrails", "质量门禁")}</h3>
          <div class="meta">
            <span>${copy("status", "状态")}=${escapeHtml(localizeWord(quality.status || "draft"))}</span>
            <span>${copy("score", "分数")}=${escapeHtml(Number(quality.score || 0).toFixed(2))}</span>
            <span>${copy("action", "动作")}=${escapeHtml(formatReportOperatorAction(quality.operator_action || ""))}</span>
          </div>
        </div>
        <span class="chip ${reportStatusTone(quality.status)}">${quality.can_export ? copy("export ready", "可导出") : copy("hold", "暂停")}</span>
      </div>
      <div class="panel-sub">${quality.can_export
        ? copy("The current report composition satisfies the visible guardrails.", "当前报告编排满足可见质量门禁。")
        : copy("Resolve the highlighted guardrails before treating this report as ready.", "先解决下面标出的质量门禁，再把这份报告视为就绪。")}</div>
    </div>
    <div class="stack">${renderedChecks}</div>
  `;
}

function renderClaimsWorkspace() {
  const root = $("claim-composer-shell");
  if (!root) {
    return;
  }
  if (state.loading.board && !state.claimCards.length && !state.reports.length) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
    return;
  }
  syncReportSelectionState();
  const selectedReport = getSelectedReportRecord();
  const selectedSection = getSelectedReportSectionRecord();
  const selectedClaim = getSelectedClaimCard();
  const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
  const sections = getReportSectionsForReport(selectedReport?.id || "");
  const reportClaimIds = new Set(getReportClaimIds(selectedReport?.id || ""));
  const selectedSectionClaimIds = new Set(Array.isArray(selectedSection?.claim_card_ids) ? selectedSection.claim_card_ids : []);
  const selectedClaimBundles = Array.isArray(selectedClaim?.citation_bundle_ids)
    ? selectedClaim.citation_bundle_ids.map((bundleId) => getCitationBundleRecord(bundleId)).filter(Boolean)
    : [];
  const selectedClaimSources = uniqueValues([
    ...(Array.isArray(selectedClaim?.source_item_ids) ? selectedClaim.source_item_ids : []),
    ...selectedClaimBundles.flatMap((bundle) => Array.isArray(bundle.source_item_ids) ? bundle.source_item_ids : []),
  ]);
  const selectedClaimUrls = uniqueValues(selectedClaimBundles.flatMap((bundle) => Array.isArray(bundle.source_urls) ? bundle.source_urls : []));
  const claimRows = state.claimCards.length
    ? state.claimCards.map((claim) => {
        const claimId = String(claim.id || "").trim();
        const claimLabel = getClaimCardLabel(claim) || claimId;
        const isSelected = claimId === String(state.selectedClaimId || "").trim();
        const inReport = reportClaimIds.has(claimId);
        const inSection = selectedSectionClaimIds.has(claimId);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${escapeHtml(claimLabel)}</h3>
                <div class="meta">
                  <span>${claimId}</span>
                  <span>${copy("status", "状态")}=${escapeHtml(localizeWord(claim.status || "draft"))}</span>
                  <span>${copy("confidence", "置信度")}=${escapeHtml(Number(claim.confidence || 0).toFixed(2))}</span>
                </div>
              </div>
              <span class="chip ${isSelected ? "ok" : reportStatusTone(claim.status)}">${escapeHtml(localizeWord(claim.status || "draft"))}</span>
            </div>
            <div class="panel-sub">${escapeHtml(claim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}</div>
            <div class="meta">
              <span class="chip ${inReport ? "ok" : ""}">${inReport ? copy("in report", "已挂入报告") : copy("unassigned", "未挂接")}</span>
              <span class="chip ${inSection ? "ok" : ""}">${selectedSection ? (inSection ? copy("in section", "已挂入章节") : copy("outside section", "未挂入章节")) : copy("report only", "仅报告级")}</span>
            </div>
            <div class="actions">
              <button class="btn-secondary" type="button" data-claim-select="${claimId}">${copy("Inspect", "查看")}</button>
              <button class="btn-secondary" type="button" data-claim-attach="${claimId}" ${selectedReport ? "" : "disabled"}>${selectedSection ? copy("Attach To Section", "挂到章节") : copy("Attach To Report", "挂到报告")}</button>
            </div>
          </div>
        `;
      }).join("")
    : `<div class="empty">${copy("No claim cards yet. Create the first source-bound claim on the left.", "当前还没有主张卡。先在左侧创建第一条带来源的主张。")}</div>`;

  root.innerHTML = `
    <div class="story-columns">
      <div class="stack">
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Current Composition Target", "当前编排目标")}</h3>
              <div class="meta">
                <span>${copy("report", "报告")}=${escapeHtml(selectedReport ? (selectedReport.title || selectedReport.id) : copy("not set", "未设置"))}</span>
                <span>${copy("section", "章节")}=${escapeHtml(selectedSection ? (selectedSection.title || selectedSection.id) : copy("report level", "报告级"))}</span>
                <span>${copy("quality", "质量")}=${escapeHtml(selectedQuality ? localizeWord(selectedQuality.status || "draft") : copy("not loaded", "未加载"))}</span>
              </div>
            </div>
            <span class="chip ${reportStatusTone(selectedQuality?.status || selectedReport?.status || "")}">${escapeHtml(localizeWord(selectedQuality?.status || selectedReport?.status || "draft"))}</span>
          </div>
          <div class="panel-sub">${selectedReport
            ? copy("Claims stay report-backed. Pick a section when the judgment should appear inside a specific narrative block.", "主张始终绑定到持久化报告。只有在需要进入具体叙事块时，再选择某个章节。")
            : copy("Choose or create a report in Report Studio, then come back to bind claims into sections.", "先去报告工作台选择或创建一份报告，再回来把主张挂进章节。")}</div>
          <div class="field-grid" style="margin-top:12px;">
            <label>${copy("Report", "报告")}
              <select id="claim-report-select">
                <option value="">${copy("No report selected", "未选择报告")}</option>
                ${state.reports.map((report) => `<option value="${escapeHtml(report.id)}" ${String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}>${escapeHtml(report.title || report.id)}</option>`).join("")}
              </select>
            </label>
            <label>${copy("Section", "章节")}
              <select id="claim-section-select" ${selectedReport ? "" : "disabled"}>
                <option value="">${copy("Attach at report level", "挂到报告级")}</option>
                ${sections.map((section) => `<option value="${escapeHtml(section.id)}" ${String(section.id || "") === String(state.selectedReportSectionId || "") ? "selected" : ""}>${escapeHtml(section.title || section.id)}</option>`).join("")}
              </select>
            </label>
          </div>
          <div class="actions">
            <button class="btn-secondary" type="button" data-claims-open-report-studio>${copy("Open Report Studio", "打开报告工作台")}</button>
            ${selectedReport ? `<a href="/api/reports/${selectedReport.id}" target="_blank" rel="noreferrer">${copy("Open Report JSON", "打开报告 JSON")}</a>` : ""}
          </div>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Create Claim", "创建主张")}</h3>
              <div class="panel-sub">${copy("Capture the bounded judgment here, then persist its source binding immediately.", "先记录边界明确的判断，再立即把来源绑定写进去。")}</div>
            </div>
            <span class="chip ok">${copy("persisted", "持久化")}</span>
          </div>
          <form id="claim-composer-form" style="margin-top:12px;">
            <label>${copy("Statement", "主张语句")}<textarea name="statement" rows="3" placeholder="${copy("AI adoption is landing first in quantity takeoff and schedule control.", "AI 最先在算量和计划控制环节跑通。")}"></textarea></label>
            <label>${copy("Rationale", "理由")}<textarea name="rationale" rows="3" placeholder="${copy("State the boundary, evidence pattern, or operational reason behind the claim.", "记录这个主张背后的边界、证据模式或业务理由。")}"></textarea></label>
            <div class="field-grid">
              <label>${copy("Confidence", "置信度")}<input name="confidence" type="number" min="0" max="1" step="0.01" value="0.8"></label>
              <label>${copy("Status", "状态")}
                <select name="status">
                  ${claimStatusOptions.map((status) => `<option value="${status}">${localizeWord(status)}</option>`).join("")}
                </select>
              </label>
            </div>
            <label>${copy("Source Item IDs", "来源条目 ID")}<input name="source_item_ids" placeholder="${copy("item-123, item-456", "item-123, item-456")}"><span class="field-hint">${copy("Use commas or new lines when the claim already points to stored inbox items.", "如果主张已经对应到已存储条目，可以用逗号或换行补充 item ID。")}</span></label>
            <label>${copy("Source URLs", "来源 URL")}<textarea name="source_urls" rows="3" placeholder="${copy("https://example.com/source-a", "https://example.com/source-a")}"></textarea><span class="field-hint">${copy("URLs create a citation bundle so the claim stays source-bound even before every item is normalized into inbox IDs.", "URL 会生成 citation bundle，这样即使条目还没完全落进 inbox ID，主张也能保持来源绑定。")}</span></label>
            <label>${copy("Citation Note", "引用备注")}<input name="bundle_note" placeholder="${copy("Why these sources support the claim", "说明这些来源为什么支撑该主张")}"></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${copy("Create Claim", "创建主张")}</button>
              <button class="btn-secondary" type="button" data-claim-form-focus-report-studio>${copy("Need A Report First", "先去创建报告")}</button>
            </div>
          </form>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Selected Claim", "当前主张")}</h3>
              <div class="meta">
                <span>${escapeHtml(selectedClaim ? (selectedClaim.id || "-") : "-")}</span>
              <span>${copy("bundles", "引用包")}=${selectedClaimBundles.length}</span>
              <span>${copy("sources", "来源")}=${selectedClaimSources.length + selectedClaimUrls.length}</span>
            </div>
          </div>
            <span class="chip ${reportStatusTone(selectedClaim?.status || "")}">${escapeHtml(localizeWord(selectedClaim?.status || "draft"))}</span>
          </div>
          ${selectedClaim
            ? `
              <div class="panel-sub">${escapeHtml(selectedClaim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}</div>
              <div class="meta">
                ${selectedClaimSources.map((value) => `<span class="chip ok">${escapeHtml(value)}</span>`).join("") || `<span class="chip">${copy("no direct item id", "没有直接 item id")}</span>`}
                ${selectedClaimUrls.map((value) => `<span class="chip" data-fit-text="claim-url-chip" data-fit-max-width="210" data-fit-fallback="42">${escapeHtml(value)}</span>`).join("")}
              </div>
            `
            : `<div class="empty">${copy("Pick one claim from the right rail to inspect its binding and reuse it in the current section.", "先从右侧选中一条主张，再查看它的来源绑定并复用到当前章节。")}</div>`}
        </div>
      </div>

      <div class="stack">
        <div class="meta">
          <span class="mono">${copy("claim inventory", "主张库存")}</span>
          <span class="chip">${copy("selected", "已选")}=${selectedClaim ? 1 : 0}</span>
          <span class="chip ok">${copy("report claims", "报告内主张")}=${reportClaimIds.size}</span>
        </div>
        ${claimRows}
      </div>
    </div>
  `;

  root.querySelector("#claim-report-select")?.addEventListener("change", async (event) => {
    state.selectedReportSectionId = "";
    await selectReport(String(event.target.value || "").trim());
  });
  root.querySelector("#claim-section-select")?.addEventListener("change", (event) => {
    state.selectedReportSectionId = String(event.target.value || "").trim();
    renderClaimsWorkspace();
    renderReportStudio();
    renderTopbarContext();
  });
  root.querySelector("[data-claims-open-report-studio]")?.addEventListener("click", () => {
    jumpToSection("section-report-studio");
  });
  root.querySelector("[data-claim-form-focus-report-studio]")?.addEventListener("click", () => {
    jumpToSection("section-report-studio");
  });
  root.querySelector("#claim-composer-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    const statement = String(form.get("statement") || "").trim();
    if (!statement) {
      showToast(copy("Provide a claim statement before saving.", "保存前请先填写主张语句。"), "error");
      return;
    }
    const reportId = String(state.selectedReportId || form.get("report_id") || "").trim();
    const sectionId = String(state.selectedReportSectionId || "").trim();
    const sourceItemIds = parseDelimitedInput(form.get("source_item_ids"));
    const sourceUrls = parseDelimitedInput(form.get("source_urls"));
    const rationale = String(form.get("rationale") || "").trim();
    const status = String(form.get("status") || "draft").trim().toLowerCase() || "draft";
    const confidence = Number(form.get("confidence") || 0);
    const selectedReportRecord = getReportRecord(reportId);
    const submitButton = event.target.querySelector("button[type='submit']");
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      let createdClaim = await api("/api/claim-cards", {
        method: "POST",
        payload: {
          statement,
          rationale,
          confidence,
          status,
          brief_id: String(selectedReportRecord?.brief_id || "").trim(),
          source_item_ids: sourceItemIds,
        },
      });
      let createdBundleId = "";
      const bundleNote = String(form.get("bundle_note") || "").trim();
      if (sourceUrls.length || sourceItemIds.length) {
        const bundle = await api("/api/citation-bundles", {
          method: "POST",
          payload: {
            claim_card_id: createdClaim.id,
            label: `${statement.slice(0, 42)} ${copy("sources", "来源")}`,
            source_item_ids: sourceItemIds,
            source_urls: sourceUrls,
            note: bundleNote,
          },
        });
        createdBundleId = String(bundle.id || "").trim();
        createdClaim = await api(`/api/claim-cards/${createdClaim.id}`, {
          method: "PUT",
          payload: {
            source_item_ids: sourceItemIds,
            citation_bundle_ids: uniqueValues([...(Array.isArray(createdClaim.citation_bundle_ids) ? createdClaim.citation_bundle_ids : []), createdBundleId]),
          },
        });
      }
      if (reportId) {
        await attachClaimToReport(createdClaim.id, reportId, sectionId, createdBundleId);
      }
      state.selectedClaimId = String(createdClaim.id || "").trim();
      if (reportId) {
        state.selectedReportId = reportId;
      }
      if (sectionId) {
        state.selectedReportSectionId = sectionId;
      }
      await refreshBoard();
      showToast(
        state.language === "zh"
          ? `主张已创建：${statement}`
          : `Claim created: ${statement}`,
        "success",
      );
    } catch (error) {
      reportError(error, copy("Create claim", "创建主张"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelectorAll("[data-claim-select]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedClaimId = String(button.dataset.claimSelect || "").trim();
      renderClaimsWorkspace();
      renderReportStudio();
      renderTopbarContext();
    });
  });
  root.querySelectorAll("[data-claim-attach]").forEach((button) => {
    button.addEventListener("click", async () => {
      const claimId = String(button.dataset.claimAttach || "").trim();
      const reportId = String(state.selectedReportId || "").trim();
      const sectionId = String(state.selectedReportSectionId || "").trim();
      if (!claimId || !reportId) {
        return;
      }
      button.disabled = true;
      try {
        await attachClaimToReport(claimId, reportId, sectionId);
        state.selectedClaimId = claimId;
        await refreshBoard();
        setStageFeedback("review", {
          kind: "completion",
          title: copy("Claim attached to the current report target", "主张已挂接到当前报告目标"),
          copy: copy(
            "The review lane now shows that this claim is attached to the selected report target.",
            "审阅阶段现在已经明确显示，这条主张已挂接到当前选中的报告目标。"
          ),
          actionHierarchy: {
            primary: {
              label: copy("Open Report Studio", "打开报告工作台"),
              attrs: { "data-empty-jump": "section-report-studio" },
            },
            secondary: [
              {
                label: copy("Open Claim Composer", "打开主张装配"),
                attrs: { "data-empty-jump": "section-claims" },
              },
            ],
          },
        });
        showToast(copy("Claim attached to the current report target.", "主张已挂接到当前报告目标。"), "success");
      } catch (error) {
        reportError(error, copy("Attach claim", "挂接主张"));
      } finally {
        button.disabled = false;
      }
    });
  });
  scheduleCanvasTextFit(root);
}

function renderReportStudio() {
  const root = $("report-studio-shell");
  if (!root) {
    return;
  }
  if (state.loading.board && !state.reports.length) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
    return;
  }
  syncReportSelectionState();
  const selectedReport = getSelectedReportRecord();
  const composition = getReportComposition(selectedReport?.id || "");
  const quality = composition?.quality || null;
  const sections = composition?.sections && Array.isArray(composition.sections)
    ? composition.sections
    : getReportSectionsForReport(selectedReport?.id || "");
  const claims = composition?.claim_cards && Array.isArray(composition.claim_cards)
    ? composition.claim_cards
    : state.claimCards.filter((claim) => getReportClaimIds(selectedReport?.id || "").includes(String(claim.id || "").trim()));
  const exportProfiles = state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selectedReport?.id || "").trim());
  const sectionRows = sections.length
    ? sections.map((section) => {
        const sectionClaimIds = Array.isArray(section.claim_card_ids) ? section.claim_card_ids : [];
        const sectionClaims = sectionClaimIds
          .map((claimId) => claims.find((claim) => String(claim.id || "").trim() === String(claimId || "").trim()) || getClaimCardRecord(claimId))
          .filter(Boolean);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${escapeHtml(section.title || section.id)}</h3>
                <div class="meta">
                  <span>${copy("position", "位置")}=${escapeHtml(String(section.position || 0))}</span>
                  <span>${copy("status", "状态")}=${escapeHtml(localizeWord(section.status || "draft"))}</span>
                  <span>${copy("claims", "主张")}=${sectionClaimIds.length}</span>
                </div>
              </div>
              <span class="chip ${reportStatusTone(section.status)}">${escapeHtml(localizeWord(section.status || "draft"))}</span>
            </div>
            <div class="panel-sub">${escapeHtml(section.summary || copy("No section summary yet.", "当前还没有章节摘要。"))}</div>
            <div class="meta">
              ${sectionClaims.length
                ? sectionClaims.map((claim) => `<span class="chip ok" data-fit-text="report-section-claim-chip" data-fit-max-width="198" data-fit-fallback="32">${escapeHtml(getClaimCardLabel(claim))}</span>`).join("")
                : `<span class="chip hot">${copy("no claims attached", "当前没有挂接主张")}</span>`}
            </div>
            <div class="actions">
              <button class="btn-secondary" type="button" data-report-section-focus="${escapeHtml(section.id)}">${copy("Focus In Claim Composer", "去主张装配")}</button>
            </div>
          </div>
        `;
      }).join("")
    : `<div class="empty">${copy("No report section yet. Create one on the left, then bind claims into it.", "当前还没有章节。先在左侧创建一个章节，再把主张挂进去。")}</div>`;

  root.innerHTML = `
    <div class="story-columns">
      <div class="stack">
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Report Workspace", "报告工作区")}</h3>
              <div class="panel-sub">${copy("The browser stays a projection over persisted report objects. No report-only browser state is hidden here.", "浏览器仍然只是持久化报告对象的投射，这里不会偷偷生成浏览器专属状态。")}</div>
            </div>
            <span class="chip ${reportStatusTone(quality?.status || selectedReport?.status || "")}">${escapeHtml(localizeWord(quality?.status || selectedReport?.status || "draft"))}</span>
          </div>
          <div class="field-grid" style="margin-top:12px;">
            <label>${copy("Current Report", "当前报告")}
              <select id="report-studio-select">
                <option value="">${copy("No report selected", "未选择报告")}</option>
                ${state.reports.map((report) => `<option value="${escapeHtml(report.id)}" ${String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}>${escapeHtml(report.title || report.id)}</option>`).join("")}
              </select>
            </label>
            <label>${copy("Export Profiles", "导出配置")}
              <div class="meta">
                ${exportProfiles.length
                  ? exportProfiles.map((profile) => `<span class="chip ok">${escapeHtml(profile.name || profile.id)}</span>`).join("")
                  : `<span class="chip">${copy("none yet", "暂无")}</span>`}
              </div>
            </label>
          </div>
          <div class="actions">
            <button class="btn-secondary" type="button" data-report-compose-refresh ${selectedReport ? "" : "disabled"}>${copy("Refresh Composition", "刷新编排")}</button>
            <button class="btn-secondary" type="button" data-report-preview-markdown ${selectedReport ? "" : "disabled"}>${copy("Preview Markdown", "预览 Markdown")}</button>
            <button class="btn-secondary" type="button" data-report-json="${selectedReport?.id || ""}" ${selectedReport ? "" : "disabled"}>${copy("Inspect JSON", "查看 JSON")}</button>
          </div>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Create Report", "创建报告")}</h3>
              <div class="panel-sub">${copy("Start a persisted report shell first. Claim Composer can bind judgments into it immediately after.", "先创建一个持久化报告壳，再回到主张装配里把判断挂进去。")}</div>
            </div>
          </div>
          <form id="report-create-form" style="margin-top:12px;">
            <div class="field-grid">
              <label>${copy("Title", "标题")}<input name="title" placeholder="${copy("AI Infrastructure Brief", "AI 基建调研报告")}"></label>
              <label>${copy("Audience", "受众")}<input name="audience" placeholder="${copy("leadership", "管理层")}"></label>
            </div>
            <label>${copy("Summary", "摘要")}<textarea name="summary" rows="3" placeholder="${copy("Describe what this report is trying to help decide.", "描述这份报告希望帮助回答什么决策问题。")}"></textarea></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${copy("Create Report", "创建报告")}</button>
            </div>
          </form>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Report Editor", "报告编辑")}</h3>
              <div class="panel-sub">${copy("Tune report metadata and keep the assembled surface aligned with the persisted object graph.", "调整报告元数据，并让浏览器展示继续和持久化对象图保持一致。")}</div>
            </div>
          </div>
          ${selectedReport
            ? `
              <form id="report-editor-form" data-report-id="${selectedReport.id}" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${copy("Title", "标题")}<input name="title" value="${escapeHtml(selectedReport.title || "")}"></label>
                  <label>${copy("Audience", "受众")}<input name="audience" value="${escapeHtml(selectedReport.audience || "")}"></label>
                </div>
                <label>${copy("Status", "状态")}
                  <select name="status">
                    ${reportStatusOptions.map((status) => `<option value="${status}" ${String(selectedReport.status || "draft") === status ? "selected" : ""}>${localizeWord(status)}</option>`).join("")}
                  </select>
                </label>
                <label>${copy("Summary", "摘要")}<textarea name="summary" rows="4">${escapeHtml(selectedReport.summary || "")}</textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${copy("Save Report", "保存报告")}</button>
                  <button class="btn-secondary" type="button" data-report-jump-claims>${copy("Open Claim Composer", "打开主张装配")}</button>
                </div>
              </form>
            `
            : `<div class="empty">${copy("Create or select a report to edit it here.", "先创建或选中一份报告，再在这里编辑。")}</div>`}
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Section Builder", "章节构建")}</h3>
              <div class="panel-sub">${copy("Create one deterministic section, then bind claims into it from Claim Composer.", "先创建一个确定性的章节，再回到主张装配里把主张挂进去。")}</div>
            </div>
          </div>
          ${selectedReport
            ? `
              <form id="report-section-form" data-report-id="${selectedReport.id}" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${copy("Title", "标题")}<input name="title" placeholder="${copy("Executive Summary", "执行摘要")}"></label>
                  <label>${copy("Position", "位置")}<input name="position" type="number" min="0" step="1" value="${escapeHtml(String(sections.length + 1))}"></label>
                </div>
                <label>${copy("Section Summary", "章节摘要")}<textarea name="summary" rows="3" placeholder="${copy("What should this section conclude or frame?", "这个章节主要要承接什么判断或框架？")}"></textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${copy("Create Section", "创建章节")}</button>
                </div>
              </form>
            `
            : `<div class="empty">${copy("No report selected, so there is nowhere to attach a section yet.", "当前没有选中报告，因此还没有章节可挂接。")}</div>`}
        </div>
      </div>

      <div class="stack">
        ${selectedReport ? renderReportQualityBlock(quality) : `<div class="empty">${copy("Select one report to inspect guardrails, sections, and export sheets.", "选中一份报告后，这里会显示质量门禁、章节结构和导出查看。")}</div>`}
        <div class="stack">
          <div class="meta">
            <span class="mono">${copy("report sections", "报告章节")}</span>
            <span class="chip ok">${copy("count", "数量")}=${sections.length}</span>
            <span class="chip">${copy("claims", "主张")}=${claims.length}</span>
          </div>
          ${sectionRows}
        </div>
      </div>
    </div>
  `;

  root.querySelector("#report-studio-select")?.addEventListener("change", async (event) => {
    await selectReport(String(event.target.value || "").trim());
  });
  root.querySelector("[data-report-compose-refresh]")?.addEventListener("click", async (event) => {
    if (!selectedReport) {
      return;
    }
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await loadReportComposition(selectedReport.id);
      showToast(copy("Report composition refreshed.", "报告编排已刷新。"), "success");
    } catch (error) {
      reportError(error, copy("Refresh report composition", "刷新报告编排"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-report-preview-markdown]")?.addEventListener("click", async (event) => {
    if (!selectedReport) {
      return;
    }
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await previewReportMarkdown(selectedReport.id);
    } catch (error) {
      reportError(error, copy("Preview report markdown", "预览报告 Markdown"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-report-json]")?.addEventListener("click", async (event) => {
    if (!selectedReport) {
      return;
    }
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await previewReportJson(String(button.dataset.reportJson || selectedReport.id));
    } catch (error) {
      reportError(error, copy("Inspect report JSON", "查看报告 JSON"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("#report-create-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    const title = String(form.get("title") || "").trim();
    if (!title) {
      setStageFeedback("review", {
        kind: "blocked",
        title: copy("Report still needs a title", "报告仍缺少标题"),
        copy: copy("Add a title before this report can become a persisted review object.", "补上标题后，这份报告才能成为持久化的审阅对象。"),
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
        },
      });
      showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
      return;
    }
    const payload = {
      title,
      audience: String(form.get("audience") || "").trim(),
      summary: String(form.get("summary") || "").trim(),
    };
    const submitButton = event.target.querySelector("button[type='submit']");
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      const created = await api("/api/reports", {
        method: "POST",
        payload,
      });
      state.selectedReportId = String(created.id || "").trim();
      state.selectedReportSectionId = "";
      await refreshBoard();
      setStageFeedback("review", {
        kind: "completion",
        title: state.language === "zh" ? `报告已创建：${title}` : `Report created: ${title}`,
        copy: copy(
          "The review lane now owns a persisted report object. Add sections or attach claims next.",
          "审阅阶段现在已经拥有一份持久化报告对象；下一步可以继续创建章节，或挂接主张。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
          secondary: [
            {
              label: copy("Open Claim Composer", "打开主张装配"),
              attrs: { "data-empty-jump": "section-claims" },
            },
          ],
        },
      });
      showToast(
        state.language === "zh"
          ? `报告已创建：${title}`
          : `Report created: ${title}`,
        "success",
      );
    } catch (error) {
      reportError(error, copy("Create report", "创建报告"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelector("#report-editor-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedReport) {
      return;
    }
    const form = new FormData(event.target);
    const payload = {
      title: String(form.get("title") || "").trim(),
      audience: String(form.get("audience") || "").trim(),
      status: String(form.get("status") || "draft").trim().toLowerCase() || "draft",
      summary: String(form.get("summary") || "").trim(),
    };
    if (!payload.title) {
      setStageFeedback("review", {
        kind: "blocked",
        title: copy("Report save is blocked by a missing title", "报告保存被缺失标题阻塞"),
        copy: copy("Keep the report title populated before saving changes in the review lane.", "请先保留报告标题，再在审阅阶段保存修改。"),
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
        },
      });
      showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
      return;
    }
    const submitButton = event.target.querySelector("button[type='submit']");
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      await api(`/api/reports/${selectedReport.id}`, {
        method: "PUT",
        payload,
      });
      await refreshBoard();
      setStageFeedback("review", {
        kind: "completion",
        title: copy("Report saved", "报告已保存"),
        copy: copy(
          "The persisted report object is updated in place on the review lane.",
          "这份持久化报告对象已经在审阅阶段原位更新。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
        },
      });
      showToast(copy("Report saved.", "报告已保存。"), "success");
    } catch (error) {
      reportError(error, copy("Save report", "保存报告"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelector("[data-report-jump-claims]")?.addEventListener("click", () => {
    jumpToSection("section-claims");
  });
  root.querySelector("#report-section-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedReport) {
      return;
    }
    const form = new FormData(event.target);
    const title = String(form.get("title") || "").trim();
    if (!title) {
      setStageFeedback("review", {
        kind: "blocked",
        title: copy("Report section still needs a title", "报告章节仍缺少标题"),
        copy: copy("Add a section title before this report structure can advance.", "补上章节标题后，这份报告结构才能继续推进。"),
        actionHierarchy: {
          primary: {
            label: copy("Open Report Studio", "打开报告工作台"),
            attrs: { "data-empty-jump": "section-report-studio" },
          },
        },
      });
      showToast(copy("Provide a section title before saving.", "保存前请先填写章节标题。"), "error");
      return;
    }
    const payload = {
      report_id: selectedReport.id,
      title,
      position: Number(form.get("position") || sections.length + 1),
      summary: String(form.get("summary") || "").trim(),
    };
    const submitButton = event.target.querySelector("button[type='submit']");
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      const created = await api("/api/report-sections", {
        method: "POST",
        payload,
      });
      await api(`/api/reports/${selectedReport.id}`, {
        method: "PUT",
        payload: {
          section_ids: uniqueValues([...(Array.isArray(selectedReport.section_ids) ? selectedReport.section_ids : []), created.id]),
        },
      });
      state.selectedReportSectionId = String(created.id || "").trim();
      await refreshBoard();
      setStageFeedback("review", {
        kind: "completion",
        title: copy("Report section created", "报告章节已创建"),
        copy: copy(
          "The report now exposes a persisted section that can receive claims from the review lane.",
          "这份报告现在已经拥有一个持久化章节，可以继续从审阅阶段接收主张。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Claim Composer", "打开主张装配"),
            attrs: { "data-empty-jump": "section-claims" },
          },
          secondary: [
            {
              label: copy("Open Report Studio", "打开报告工作台"),
              attrs: { "data-empty-jump": "section-report-studio" },
            },
          ],
        },
      });
      showToast(copy("Report section created.", "报告章节已创建。"), "success");
    } catch (error) {
      reportError(error, copy("Create report section", "创建报告章节"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelectorAll("[data-report-section-focus]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedReportSectionId = String(button.dataset.reportSectionFocus || "").trim();
      renderClaimsWorkspace();
      renderReportStudio();
      renderTopbarContext();
      jumpToSection("section-claims");
    });
  });
  scheduleCanvasTextFit(root);
}

function renderBoardShell() {
  renderOverview();
  renderWatches();
  renderWatchDetail();
  renderAlerts();
  renderRoutes();
  renderRouteHealth();
  renderDeliveryWorkspace();
  renderAiSurfaces();
  renderStatus();
  renderTriage();
  renderStories();
  renderStoryInspector();
  renderClaimsWorkspace();
  renderReportStudio();
}

async function ensureOverview({ force = false } = {}) {
  await runHydrationTask("overview", async () => {
    state.overview = await api("/api/overview");
    return state.overview;
  }, { force });
}

async function ensureMonitorData({ force = false } = {}) {
  await runHydrationTask("monitor", async () => {
    const [watches, alerts, routes, status] = await Promise.all([
      api("/api/watches?include_disabled=true"),
      api("/api/alerts?limit=8"),
      api("/api/alert-routes"),
      api("/api/watch-status"),
    ]);
    state.watches = watches;
    state.alerts = alerts;
    state.routes = routes;
    state.status = status;
    if (state.watches.length) {
      state.selectedWatchId = selectExistingOrFirst(state.watches, state.selectedWatchId);
    } else {
      state.selectedWatchId = "";
      setContextRouteName("", "");
    }
    setContextRouteFromWatch();
    return watches;
  }, { force });
}

async function ensureReviewData({ force = false } = {}) {
  await runHydrationTask("review", async () => {
    const [triage, triageStats, stories] = await Promise.all([
      api("/api/triage?limit=12&include_closed=true"),
      api("/api/triage/stats"),
      api("/api/stories?limit=6&min_items=0"),
    ]);
    state.triage = triage;
    state.triageStats = triageStats;
    state.stories = stories;
    if (state.stories.length) {
      const selectedStoryId = selectExistingOrFirst(state.stories, state.selectedStoryId);
      state.selectedStoryId = selectedStoryId;
      if (!state.storyDetails[selectedStoryId]) {
        const seeded = state.stories.find((story) => String(story.id || "").trim() === selectedStoryId);
        if (seeded) {
          state.storyDetails[selectedStoryId] = seeded;
        }
      }
    } else {
      state.selectedStoryId = "";
    }
    state.selectedTriageId = selectExistingOrFirst(state.triage, state.selectedTriageId);
    return triage;
  }, { force });
}

async function ensureReportFamilyData({ force = false } = {}) {
  await runHydrationTask("report-family", async () => {
    const [reportBriefs, claimCards, citationBundles, reportSections, reports, exportProfiles] = await Promise.all([
      api("/api/report-briefs?limit=20"),
      api("/api/claim-cards?limit=40"),
      api("/api/citation-bundles?limit=40"),
      api("/api/report-sections?limit=40"),
      api("/api/reports?limit=20"),
      api("/api/export-profiles?limit=40"),
    ]);
    state.reportBriefs = reportBriefs;
    state.claimCards = claimCards;
    state.citationBundles = citationBundles;
    state.reportSections = reportSections;
    state.reports = reports;
    state.exportProfiles = exportProfiles;
    syncReportSelectionState();
    return reports;
  }, { force });
}

async function ensureDeliveryData({ force = false } = {}) {
  await runHydrationTask("delivery", async () => {
    const [alerts, routes, routeHealth, deliverySubscriptions, deliveryDispatchRecords, status, ops, reports, exportProfiles] = await Promise.all([
      api("/api/alerts?limit=8"),
      api("/api/alert-routes"),
      api("/api/alert-routes/health?limit=60"),
      api("/api/delivery-subscriptions?limit=40"),
      api("/api/delivery-dispatch-records?limit=40"),
      api("/api/watch-status"),
      api("/api/ops"),
      api("/api/reports?limit=20"),
      api("/api/export-profiles?limit=40"),
    ]);
    state.alerts = alerts;
    state.routes = routes;
    state.routeHealth = routeHealth;
    state.deliverySubscriptions = deliverySubscriptions;
    state.deliveryDispatchRecords = deliveryDispatchRecords;
    state.status = status;
    state.ops = ops;
    state.reports = reports;
    state.exportProfiles = exportProfiles;
    syncDeliverySelectionState();
    return deliverySubscriptions;
  }, { force });
}

async function ensureSelectedWatchDetail({ force = false } = {}) {
  const selectedWatchId = selectExistingOrFirst(state.watches, state.selectedWatchId);
  if (!selectedWatchId) {
    state.selectedWatchId = "";
    return null;
  }
  state.selectedWatchId = selectedWatchId;
  if (!force && state.watchDetails[selectedWatchId]) {
    return state.watchDetails[selectedWatchId];
  }
  return loadWatch(selectedWatchId, { force });
}

async function ensureSelectedStoryDetail({ force = false } = {}) {
  const selectedStoryId = selectExistingOrFirst(state.stories, state.selectedStoryId);
  if (!selectedStoryId) {
    state.selectedStoryId = "";
    return null;
  }
  state.selectedStoryId = selectedStoryId;
  if (!force && state.storyDetails[selectedStoryId] && state.storyGraph[selectedStoryId]) {
    return state.storyDetails[selectedStoryId];
  }
  await loadStory(selectedStoryId, { syncUrl: false, force });
  return state.storyDetails[selectedStoryId] || null;
}

async function ensureSelectedReportComposition({ force = false } = {}) {
  syncReportSelectionState();
  if (!state.selectedReportId) {
    return null;
  }
  if (!force && state.reportCompositions[state.selectedReportId]) {
    return state.reportCompositions[state.selectedReportId];
  }
  await loadReportComposition(state.selectedReportId, { render: false, force });
  return state.reportCompositions[state.selectedReportId] || null;
}

async function ensureDigestData({ force = false } = {}) {
  await runHydrationTask("digest", async () => {
    return loadDigestConsole({ render: false, preserveDraft: true, force });
  }, { force });
}

async function ensureAiSurfacePrecheck(surfaceId, { force = false } = {}) {
  const normalizedSurfaceId = String(surfaceId || "").trim();
  if (!normalizedSurfaceId) {
    return null;
  }
  const cacheKey = `ai-precheck:${normalizedSurfaceId}`;
  if (!force && state.aiSurfacePrechecks[normalizedSurfaceId]) {
    markHydrationLoaded(cacheKey);
    return state.aiSurfacePrechecks[normalizedSurfaceId];
  }
  await runHydrationTask(cacheKey, async () => {
    state.aiSurfacePrechecks[normalizedSurfaceId] = await api(`/api/ai/surfaces/${normalizedSurfaceId}/precheck?mode=assist`);
    return state.aiSurfacePrechecks[normalizedSurfaceId];
  }, { force });
  return state.aiSurfacePrechecks[normalizedSurfaceId] || null;
}

async function hydrateBoardForSection(sectionId, { force = false } = {}) {
  const normalizedSectionId = normalizeSectionId(sectionId || state.activeSectionId);
  state.loading.board = true;
  renderBoardShell();
  try {
    await ensureOverview({ force });
    if (normalizedSectionId === "section-board") {
      await ensureMonitorData({ force });
      await ensureAiSurfacePrecheck("mission_suggest");
    } else if (normalizedSectionId === "section-cockpit") {
      await ensureMonitorData({ force });
      await ensureSelectedWatchDetail({ force });
      await ensureAiSurfacePrecheck("mission_suggest");
    } else if (normalizedSectionId === "section-triage") {
      await ensureReviewData({ force });
      await ensureAiSurfacePrecheck("triage_assist");
    } else if (normalizedSectionId === "section-story") {
      await ensureReviewData({ force });
      await ensureSelectedStoryDetail({ force });
      await ensureAiSurfacePrecheck("claim_draft");
    } else if (normalizedSectionId === "section-claims" || normalizedSectionId === "section-report-studio") {
      await ensureReviewData({ force });
      await ensureReportFamilyData({ force });
      await ensureSelectedReportComposition({ force });
    } else if (normalizedSectionId === "section-ops") {
      await ensureDeliveryData({ force });
      await ensureDigestData({ force });
    }
  } finally {
    state.loading.board = false;
  }
  renderBoardShell();
  renderCreateWatchDeck();
  applyDefaultSavedViewOnBoot();
}

async function refreshBoard() {
  state.loading.board = true;
  renderBoardShell();
  try {
    const [overview, watches, alerts, routes, routeHealth, deliverySubscriptions, deliveryDispatchRecords, digestConsole, status, ops, triage, triageStats, stories, reportBriefs, claimCards, citationBundles, reportSections, reports, exportProfiles, missionSuggestPrecheck, triageAssistPrecheck, claimDraftPrecheck] = await Promise.all([
      api("/api/overview"),
      api("/api/watches?include_disabled=true"),
      api("/api/alerts?limit=8"),
      api("/api/alert-routes"),
      api("/api/alert-routes/health?limit=60"),
      api("/api/delivery-subscriptions?limit=40"),
      api("/api/delivery-dispatch-records?limit=40"),
      api("/api/digest/console?profile=default&limit=8"),
      api("/api/watch-status"),
      api("/api/ops"),
      api("/api/triage?limit=12&include_closed=true"),
      api("/api/triage/stats"),
      api("/api/stories?limit=6&min_items=0"),
      api("/api/report-briefs?limit=20"),
      api("/api/claim-cards?limit=40"),
      api("/api/citation-bundles?limit=40"),
      api("/api/report-sections?limit=40"),
      api("/api/reports?limit=20"),
      api("/api/export-profiles?limit=40"),
      api("/api/ai/surfaces/mission_suggest/precheck?mode=assist"),
      api("/api/ai/surfaces/triage_assist/precheck?mode=assist"),
      api("/api/ai/surfaces/claim_draft/precheck?mode=assist"),
    ]);
    state.overview = overview;
    state.watches = watches;
    state.alerts = alerts;
    state.routes = routes;
    state.routeHealth = routeHealth;
    state.deliverySubscriptions = deliverySubscriptions;
    state.deliveryDispatchRecords = deliveryDispatchRecords;
    state.digestConsole = digestConsole;
    if (!state.digestProfileDraft) {
      state.digestProfileDraft = normalizeDigestProfileDraft(digestConsole?.profile?.profile || defaultDigestProfileDraft());
    }
    state.status = status;
    state.ops = ops;
    state.triage = triage;
    state.triageStats = triageStats;
    state.stories = stories;
    state.reportBriefs = reportBriefs;
    state.claimCards = claimCards;
    state.citationBundles = citationBundles;
    state.reportSections = reportSections;
    state.reports = reports;
    state.exportProfiles = exportProfiles;
    state.aiSurfacePrechecks = {
      mission_suggest: missionSuggestPrecheck,
      triage_assist: triageAssistPrecheck,
      claim_draft: claimDraftPrecheck,
    };
    if (state.watches.length) {
      const selectedWatch = state.watches.some((watch) => watch.id === state.selectedWatchId)
        ? state.selectedWatchId
        : state.watches[0].id;
      state.selectedWatchId = selectedWatch;
      state.watchDetails[selectedWatch] = await api(`/api/watches/${selectedWatch}`);
    } else {
      state.selectedWatchId = "";
      setContextRouteName("", "");
    }
    setContextRouteFromWatch();
    if (state.stories.length) {
      const selected = state.stories.some((story) => story.id === state.selectedStoryId)
        ? state.selectedStoryId
        : state.stories[0].id;
      state.selectedStoryId = selected;
      if (!state.storyDetails[selected]) {
        const seeded = state.stories.find((story) => story.id === selected);
        if (seeded) {
          state.storyDetails[selected] = seeded;
        }
      }
      if (!state.storyGraph[selected]) {
        state.storyGraph[selected] = await api(`/api/stories/${selected}/graph`);
      }
    } else {
      state.selectedStoryId = "";
    }
    if (state.triage.length && !state.triage.some((item) => item.id === state.selectedTriageId)) {
      state.selectedTriageId = state.triage[0].id;
    }
    if (!state.triage.length) {
      state.selectedTriageId = "";
    }
    syncReportSelectionState();
    syncDeliverySelectionState();
    if (state.selectedReportId) {
      state.reportCompositions[state.selectedReportId] = await api(`/api/reports/${state.selectedReportId}/compose`);
    }
    const [missionSuggest, triageAssist, claimDraft] = await Promise.all([
      state.selectedWatchId
        ? api(`/api/watches/${state.selectedWatchId}/ai/mission-suggest?mode=assist`)
        : Promise.resolve(null),
      state.selectedTriageId
        ? api(`/api/triage/${state.selectedTriageId}/ai/assist?mode=assist&limit=5`)
        : Promise.resolve(null),
      state.selectedStoryId
        ? api(`/api/stories/${state.selectedStoryId}/ai/claim-draft?mode=assist`)
        : Promise.resolve(null),
    ]);
    state.aiSurfaceProjections = {
      mission_suggest: missionSuggest,
      triage_assist: triageAssist,
      claim_draft: claimDraft,
    };
    const selectedDelivery = getSelectedDeliverySubscription();
    if (selectedDelivery && String(selectedDelivery.subject_kind || "").trim().toLowerCase() === "report") {
      try {
        await loadDeliveryPackageAudit(String(selectedDelivery.id || "").trim(), {
          profileId: String(state.deliveryPackageProfileIds[selectedDelivery.id] || "").trim(),
          render: false,
        });
      } catch (error) {
        state.deliveryPackageErrors[String(selectedDelivery.id || "").trim()] = error.message;
      }
    }
    markHydrationLoadedMany([
      "overview",
      "monitor",
      "review",
      "report-family",
      "delivery",
      "digest",
      "ai-precheck:mission_suggest",
      "ai-precheck:triage_assist",
      "ai-precheck:claim_draft",
    ]);
  } finally {
    state.loading.board = false;
  }
  renderBoardShell();
  renderCreateWatchDeck();
  applyDefaultSavedViewOnBoot();
}
