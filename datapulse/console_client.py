"""Client-side console script extracted from the HTML markup bundle."""

from __future__ import annotations

from datapulse.console_api_client import render_console_api_client_script


def render_console_client_script(initial_state: str) -> str:
    return f"""    const initial = {initial_state};
    const state = {{
      watches: [],
      watchDetails: {{}},
      watchResultFilters: {{}},
      consoleOverflowEvidence: null,
      consoleOverflowEvidenceSignature: "",
      selectedWatchId: "",
      watchSearch: "",
      watchUrlFocusPending: false,
      alerts: [],
      routes: [],
      routeSearch: "",
      routeDraft: null,
      routeEditingId: "",
      routeAdvancedOpen: null,
      routeHealth: [],
      deliverySubscriptions: [],
      deliveryDispatchRecords: [],
      deliveryDraft: null,
      selectedDeliverySubscriptionId: "",
      deliveryPackageAudits: {{}},
      deliveryPackageErrors: {{}},
      deliveryPackageProfileIds: {{}},
      digestConsole: null,
      digestProfileDraft: null,
      digestDispatchResult: [],
      digestDispatchError: "",
      contextRouteName: "",
      contextRouteSection: "",
      status: null,
      ops: null,
      aiSurfacePrechecks: {{}},
      aiSurfaceProjections: {{}},
      overview: null,
      activeSectionId: "section-intake",
      activeWorkspaceMode: "intake",
      triage: [],
      triageStats: null,
      triageFilter: "open",
      triageSearch: "",
      triagePinnedIds: [],
      triageUrlFocusPending: false,
      selectedTriageId: "",
      selectedTriageIds: [],
      triageBulkBusy: false,
      triageExplain: {{}},
      triageNoteDrafts: {{}},
      stories: [],
      storyDraft: null,
      storySearch: "",
      storyFilter: "all",
      storySort: "attention",
      storyWorkspaceMode: "board",
      storyUrlFocusPending: false,
      selectedStoryIds: [],
      storyBulkBusy: false,
      storyDetails: {{}},
      storyGraph: {{}},
      storyMarkdown: {{}},
      selectedStoryId: "",
      reportBriefs: [],
      claimCards: [],
      citationBundles: [],
      reportSections: [],
      reports: [],
      exportProfiles: [],
      reportCompositions: {{}},
      reportMarkdown: {{}},
      selectedClaimId: "",
      selectedReportId: "",
      selectedReportSectionId: "",
      createWatchDraft: null,
      createWatchEditingId: "",
      createWatchAdvancedOpen: null,
      createWatchPresetId: "",
      createWatchSuggestions: null,
      createWatchSuggestionTimer: 0,
      actionLog: [],
      stageFeedback: {{
        start: null,
        monitor: null,
        review: null,
        deliver: null,
      }},
      sharedSignalFocus: "quality",
      language: "en",
      contextLensOpen: false,
      contextLinkHistory: [],
      contextSavedViews: [],
      contextDockEditingName: "",
      contextLensRestoreFocusId: "context-summary",
      contextDefaultBootPending: true,
      loading: {{
        board: false,
        watchDetail: false,
        storyDetail: false,
        suggestions: false,
      }},
      commandPalette: {{
        open: false,
        query: "",
        selectedIndex: 0,
        recentIds: [],
      }},
      responsiveContract: {{
        viewport: "desktop",
        density: "comfortable",
        pane: "split",
        modal: "side-panel",
        actionSheet: "inline",
      }},
    }};

    const $ = (id) => document.getElementById(id);
    const hydration = {{
      loaded: Object.create(null),
      pending: Object.create(null),
    }};
{render_console_api_client_script()}

    function jumpToSection(targetId, {{ updateHash = true }} = {{}}) {{
      const normalized = normalizeSectionId(targetId);
      if (!normalized) {{
        return;
      }}
      const target = document.getElementById(normalized);
      if (!target) {{
        return;
      }}
      const currentSectionId = normalizeSectionId(state.activeSectionId);
      const currentMode = workspaceModeForSection(currentSectionId);
      const targetMode = workspaceModeForSection(normalized);
      const paneContract = String(document.body && document.body.dataset ? document.body.dataset.paneContract : "").trim() || "split";
      const shouldScroll = targetMode !== currentMode || paneContract !== "split";
      setContextLensOpen(false);
      state.activeSectionId = normalized;
      renderWorkspaceModeChrome();
      renderTopbarContext();
      hydrateBoardForSection(normalized).catch((error) => {{
        reportError(error, copy("Load workspace stage", "加载工作阶段"));
      }});
      if (shouldScroll) {{
        target.scrollIntoView({{ block: "start", behavior: "smooth" }});
      }}
      if (!updateHash) {{
        return;
      }}
      const url = new URL(window.location.href);
      const nextHash = `#${{normalized}}`;
      if (url.hash === nextHash) {{
        return;
      }}
      const nextSearch = url.searchParams.toString();
      window.history.replaceState(
        window.history.state,
        "",
        `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{nextHash}}`,
      );
    }}

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => {{
        return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[char];
      }});
    }}

    function clampLabel(value, maxLength = 34) {{
      const text = String(value || "").trim();
      if (text.length <= maxLength) {{
        return text;
      }}
      return `${{text.slice(0, Math.max(0, maxLength - 1)).trimEnd()}}…`;
    }}

    function markHydrationLoaded(key) {{
      hydration.loaded[String(key || "").trim()] = true;
    }}

    function markHydrationLoadedMany(keys) {{
      (Array.isArray(keys) ? keys : []).forEach((key) => {{
        if (key) {{
          markHydrationLoaded(key);
        }}
      }});
    }}

    function isHydrationLoaded(key) {{
      return Boolean(hydration.loaded[String(key || "").trim()]);
    }}

    async function runHydrationTask(key, loader, {{ force = false }} = {{}}) {{
      const normalizedKey = String(key || "").trim();
      if (!normalizedKey) {{
        return null;
      }}
      if (hydration.pending[normalizedKey]) {{
        return hydration.pending[normalizedKey];
      }}
      if (!force && isHydrationLoaded(normalizedKey)) {{
        return null;
      }}
      const task = (async () => {{
        const result = await loader();
        markHydrationLoaded(normalizedKey);
        return result;
      }})();
      hydration.pending[normalizedKey] = task;
      try {{
        return await task;
      }} finally {{
        if (hydration.pending[normalizedKey] === task) {{
          delete hydration.pending[normalizedKey];
        }}
      }}
    }}

    function selectExistingOrFirst(rows, currentId = "") {{
      const availableRows = Array.isArray(rows) ? rows : [];
      if (!availableRows.length) {{
        return "";
      }}
      const normalizedCurrentId = String(currentId || "").trim();
      return availableRows.some((row) => String(row.id || "").trim() === normalizedCurrentId)
        ? normalizedCurrentId
        : String(availableRows[0].id || "").trim();
    }}

    const textFitSegmenter = typeof Intl !== "undefined" && typeof Intl.Segmenter === "function"
      ? new Intl.Segmenter(undefined, {{ granularity: "grapheme" }})
      : null;
    const canvasTextWidthCache = new Map();
    const consoleOverflowEvidenceLedger = new Map();
    let canvasTextMeasureContext = null;
    let pendingTextFitFrame = 0;
    let pendingOverflowEvidenceRender = 0;
    const pendingTextFitRoots = new Set();

    function defaultConsoleOverflowEvidence() {{
      return {{
        surface_count: 0,
        checked_sample_count: 0,
        fitted_sample_count: 0,
        survivor_count: 0,
        residual_surface_count: 0,
        surfaces: [],
        residual_surfaces: [],
        updated_at: "",
      }};
    }}

    function consoleOverflowEvidenceSignature(evidence) {{
      return JSON.stringify({{
        surface_count: Number(evidence?.surface_count || 0),
        checked_sample_count: Number(evidence?.checked_sample_count || 0),
        fitted_sample_count: Number(evidence?.fitted_sample_count || 0),
        survivor_count: Number(evidence?.survivor_count || 0),
        residual_surface_count: Number(evidence?.residual_surface_count || 0),
        surfaces: Array.isArray(evidence?.surfaces)
          ? evidence.surfaces.map((surface) => ({{
              surface_id: String(surface?.surface_id || ""),
              checked_sample_count: Number(surface?.checked_sample_count || 0),
              fitted_sample_count: Number(surface?.fitted_sample_count || 0),
              survivor_count: Number(surface?.survivor_count || 0),
              sample_labels: Array.isArray(surface?.sample_labels) ? surface.sample_labels : [],
            }}))
          : [],
      }});
    }}

    function buildConsoleOverflowSampleKey(surfaceId, originalText) {{
      return `${{surfaceId}}::${{originalText}}`;
    }}

    function isNodeVisibleForOverflowEvidence(node) {{
      if (!(node instanceof HTMLElement) || !node.isConnected) {{
        return false;
      }}
      const style = window.getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden") {{
        return false;
      }}
      const rect = node.getBoundingClientRect();
      return Number(node.clientWidth || rect.width || 0) > 0 && Number(node.clientHeight || rect.height || 0) > 0;
    }}

    function hasResidualInlineOverflow(node) {{
      if (!isNodeVisibleForOverflowEvidence(node)) {{
        return false;
      }}
      const clientWidth = Number(node.clientWidth || node.getBoundingClientRect().width || 0);
      const scrollWidth = Number(node.scrollWidth || 0);
      return scrollWidth > clientWidth + 1;
    }}

    function recordConsoleOverflowEvidence(nodes) {{
      nodes.forEach((node) => {{
        if (!(node instanceof HTMLElement) || !isNodeVisibleForOverflowEvidence(node)) {{
          return;
        }}
        const surfaceId = String(node.dataset.fitText || "").trim();
        const originalText = String(node.dataset.fitTextOriginal || node.textContent || "").trim();
        if (!surfaceId || !originalText) {{
          return;
        }}
        const sampleKey = buildConsoleOverflowSampleKey(surfaceId, originalText);
        const surface = consoleOverflowEvidenceLedger.get(surfaceId) || {{
          surface_id: surfaceId,
          checked_keys: new Set(),
          fitted_keys: new Set(),
          survivor_keys: new Set(),
          sample_labels: [],
        }};
        surface.checked_keys.add(sampleKey);
        if (String(node.dataset.fitApplied || "").trim() === "true") {{
          surface.fitted_keys.add(sampleKey);
        }}
        if (hasResidualInlineOverflow(node)) {{
          surface.survivor_keys.add(sampleKey);
          const sampleLabel = clampLabel(originalText, 52);
          if (sampleLabel && !surface.sample_labels.includes(sampleLabel) && surface.sample_labels.length < 3) {{
            surface.sample_labels.push(sampleLabel);
          }}
        }}
        consoleOverflowEvidenceLedger.set(surfaceId, surface);
      }});
    }}

    function buildConsoleOverflowEvidenceSnapshot() {{
      const surfaces = Array.from(consoleOverflowEvidenceLedger.values())
        .map((surface) => ({{
          surface_id: surface.surface_id,
          checked_sample_count: surface.checked_keys.size,
          fitted_sample_count: surface.fitted_keys.size,
          survivor_count: surface.survivor_keys.size,
          sample_labels: surface.sample_labels.slice(0, 3),
        }}))
        .sort((left, right) => (
          right.survivor_count - left.survivor_count
          || right.checked_sample_count - left.checked_sample_count
          || left.surface_id.localeCompare(right.surface_id)
        ));
      const residualSurfaces = surfaces.filter((surface) => surface.survivor_count > 0);
      return {{
        surface_count: surfaces.length,
        checked_sample_count: surfaces.reduce((sum, surface) => sum + surface.checked_sample_count, 0),
        fitted_sample_count: surfaces.reduce((sum, surface) => sum + surface.fitted_sample_count, 0),
        survivor_count: surfaces.reduce((sum, surface) => sum + surface.survivor_count, 0),
        residual_surface_count: residualSurfaces.length,
        surfaces,
        residual_surfaces: residualSurfaces,
        updated_at: new Date().toISOString(),
      }};
    }}

    function scheduleConsoleOverflowEvidenceRender() {{
      if (pendingOverflowEvidenceRender || !$("status-card")) {{
        return;
      }}
      pendingOverflowEvidenceRender = window.requestAnimationFrame(() => {{
        pendingOverflowEvidenceRender = 0;
        if ($("status-card") && !(state.loading.board && !state.status && !state.ops)) {{
          renderStatus();
        }}
      }});
    }}

    function refreshConsoleOverflowEvidence() {{
      const nodes = Array.from(document.querySelectorAll("[data-fit-text]"));
      recordConsoleOverflowEvidence(nodes);
      const nextEvidence = buildConsoleOverflowEvidenceSnapshot();
      const nextSignature = consoleOverflowEvidenceSignature(nextEvidence);
      if (nextSignature === state.consoleOverflowEvidenceSignature && state.consoleOverflowEvidence) {{
        window.__DATAPULSE_CONSOLE_OVERFLOW__ = state.consoleOverflowEvidence;
        return state.consoleOverflowEvidence;
      }}
      state.consoleOverflowEvidence = nextEvidence;
      state.consoleOverflowEvidenceSignature = nextSignature;
      if (document.body?.dataset) {{
        document.body.dataset.consoleOverflowHotspots = String(nextEvidence.residual_surface_count || 0);
        document.body.dataset.consoleOverflowSurvivors = String(nextEvidence.survivor_count || 0);
      }}
      window.__DATAPULSE_CONSOLE_OVERFLOW__ = nextEvidence;
      scheduleConsoleOverflowEvidenceRender();
      return nextEvidence;
    }}

    function getConsoleOverflowEvidence() {{
      return JSON.parse(JSON.stringify(state.consoleOverflowEvidence || defaultConsoleOverflowEvidence()));
    }}

    function segmentTextForFit(value) {{
      const text = String(value || "").trim();
      if (!text) {{
        return [];
      }}
      if (textFitSegmenter) {{
        return Array.from(textFitSegmenter.segment(text), (entry) => entry.segment);
      }}
      return Array.from(text);
    }}

    function getCanvasTextMeasureContext() {{
      if (canvasTextMeasureContext) {{
        return canvasTextMeasureContext;
      }}
      if (typeof document === "undefined" || typeof document.createElement !== "function") {{
        return null;
      }}
      const canvas = document.createElement("canvas");
      canvasTextMeasureContext = typeof canvas.getContext === "function" ? canvas.getContext("2d") : null;
      return canvasTextMeasureContext;
    }}

    function measureCanvasTextWidth(text, font) {{
      const context = getCanvasTextMeasureContext();
      if (!context || !font) {{
        return -1;
      }}
      const cacheKey = `${{font}}::${{text}}`;
      if (canvasTextWidthCache.has(cacheKey)) {{
        return canvasTextWidthCache.get(cacheKey);
      }}
      context.font = font;
      const width = Number(context.measureText(text).width || 0);
      canvasTextWidthCache.set(cacheKey, width);
      return width;
    }}

    function resolveCanvasFitFont(node) {{
      const style = window.getComputedStyle(node);
      return style.font || `${{style.fontWeight || 400}} ${{style.fontSize || "14px"}} ${{style.fontFamily || "sans-serif"}}`;
    }}

    function resolveCanvasFitWidth(node) {{
      const style = window.getComputedStyle(node);
      const explicitWidth = Number(node.dataset.fitMaxWidth || 0);
      const measuredWidth = explicitWidth > 0
        ? explicitWidth
        : Number(node.getBoundingClientRect().width || node.clientWidth || 0);
      if (measuredWidth <= 0) {{
        return 0;
      }}
      const chromeWidth = (
        parseFloat(style.paddingLeft || "0")
        + parseFloat(style.paddingRight || "0")
        + parseFloat(style.borderLeftWidth || "0")
        + parseFloat(style.borderRightWidth || "0")
      );
      return Math.max(0, measuredWidth - chromeWidth);
    }}

    function fitTextToWidth(value, maxWidth, {{ font = "", fallbackLength = 34 }} = {{}}) {{
      const text = String(value || "").trim();
      if (!text) {{
        return "";
      }}
      const widthBudget = Number(maxWidth || 0);
      if (widthBudget <= 0) {{
        return clampLabel(text, fallbackLength);
      }}
      const measuredFullWidth = measureCanvasTextWidth(text, font);
      if (measuredFullWidth >= 0 && measuredFullWidth <= widthBudget) {{
        return text;
      }}
      const segments = segmentTextForFit(text);
      if (!segments.length) {{
        return clampLabel(text, fallbackLength);
      }}
      const ellipsis = "…";
      const ellipsisWidth = measureCanvasTextWidth(ellipsis, font);
      if (ellipsisWidth < 0) {{
        return clampLabel(text, fallbackLength);
      }}
      if (ellipsisWidth >= widthBudget) {{
        return ellipsis;
      }}
      let low = 0;
      let high = segments.length;
      let best = ellipsis;
      while (low <= high) {{
        const mid = Math.floor((low + high) / 2);
        const head = segments.slice(0, mid).join("").trimEnd();
        const candidate = head ? `${{head}}${{ellipsis}}` : ellipsis;
        if (measureCanvasTextWidth(candidate, font) <= widthBudget) {{
          best = candidate;
          low = mid + 1;
        }} else {{
          high = mid - 1;
        }}
      }}
      return best || clampLabel(text, fallbackLength);
    }}

    function applyCanvasTextFit(root = document) {{
      const scope = root && typeof root.querySelectorAll === "function" ? root : document;
      if (!scope) {{
        return;
      }}
      const candidates = scope.matches?.("[data-fit-text]")
        ? [scope, ...scope.querySelectorAll("[data-fit-text]")]
        : Array.from(scope.querySelectorAll("[data-fit-text]"));
      candidates.forEach((node) => {{
        if (!(node instanceof HTMLElement)) {{
          return;
        }}
        const originalText = String(node.dataset.fitTextOriginal || node.textContent || "").trim();
        if (!originalText) {{
          return;
        }}
        node.dataset.fitTextOriginal = originalText;
        if (!node.getAttribute("title")) {{
          node.setAttribute("title", originalText);
        }}
        const fallbackLength = Number(node.dataset.fitFallback || 34);
        const fittedText = fitTextToWidth(originalText, resolveCanvasFitWidth(node), {{
          font: resolveCanvasFitFont(node),
          fallbackLength,
        }});
        node.textContent = fittedText;
        node.dataset.fitApplied = fittedText !== originalText ? "true" : "false";
      }});
      refreshConsoleOverflowEvidence();
    }}

    function scheduleCanvasTextFit(root = document) {{
      pendingTextFitRoots.add(root && typeof root.querySelectorAll === "function" ? root : document);
      if (pendingTextFitFrame) {{
        return;
      }}
      pendingTextFitFrame = window.requestAnimationFrame(() => {{
        pendingTextFitFrame = 0;
        const roots = Array.from(pendingTextFitRoots);
        pendingTextFitRoots.clear();
        roots.forEach((candidate) => applyCanvasTextFit(candidate));
      }});
    }}

    const responsiveInteractionContracts = {{
      desktop: {{
        viewport: "desktop",
        density: "comfortable",
        pane: "split",
        modal: "side-panel",
        actionSheet: "inline",
      }},
      compact: {{
        viewport: "compact",
        density: "compact",
        pane: "stacked",
        modal: "sheet",
        actionSheet: "inline",
      }},
      touch: {{
        viewport: "touch",
        density: "touch",
        pane: "single",
        modal: "fullscreen",
        actionSheet: "sheet",
      }},
    }};

    function resolveResponsiveInteractionContract(width = 0) {{
      const viewportWidth = Number(width) > 0
        ? Number(width)
        : window.innerWidth || document.documentElement?.clientWidth || 1280;
      if (viewportWidth <= 760) {{
        return responsiveInteractionContracts.touch;
      }}
      if (viewportWidth <= 1100) {{
        return responsiveInteractionContracts.compact;
      }}
      return responsiveInteractionContracts.desktop;
    }}

    function applyResponsiveInteractionContract() {{
      const contract = resolveResponsiveInteractionContract();
      state.responsiveContract = contract;
      if (!document.body) {{
        return contract;
      }}
      document.body.dataset.responsiveViewport = contract.viewport;
      document.body.dataset.densityMode = contract.density;
      document.body.dataset.paneContract = contract.pane;
      document.body.dataset.modalPresentation = contract.modal;
      document.body.dataset.actionSheetMode = contract.actionSheet;
      if (contract.actionSheet !== "sheet") {{
        document.querySelectorAll("[data-card-action-sheet]").forEach((sheet) => {{
          sheet.removeAttribute("open");
        }});
      }}
      scheduleCanvasTextFit(document);
      return contract;
    }}

    function bindResponsiveInteractionContract() {{
      applyResponsiveInteractionContract();
      let resizeTimer = 0;
      let lastViewportWidth = window.innerWidth || document.documentElement?.clientWidth || 0;
      const scheduleContractApply = () => {{
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(() => {{
          applyResponsiveInteractionContract();
        }}, 80);
      }};
      window.addEventListener("resize", scheduleContractApply, {{ passive: true }});
      if (window.visualViewport?.addEventListener) {{
        window.visualViewport.addEventListener("resize", scheduleContractApply, {{ passive: true }});
      }}
      ["(max-width: 760px)", "(max-width: 1100px)"].forEach((query) => {{
        const media = window.matchMedia ? window.matchMedia(query) : null;
        if (!media) {{
          return;
        }}
        if (typeof media.addEventListener === "function") {{
          media.addEventListener("change", scheduleContractApply);
        }} else if (typeof media.addListener === "function") {{
          media.addListener(scheduleContractApply);
        }}
      }});
      window.setInterval(() => {{
        const nextViewportWidth = window.innerWidth || document.documentElement?.clientWidth || 0;
        if (!nextViewportWidth || nextViewportWidth === lastViewportWidth) {{
          return;
        }}
        lastViewportWidth = nextViewportWidth;
        scheduleContractApply();
      }}, 250);
    }}

    const languageStorageKey = "datapulse.console.language.v1";
    const createWatchStorageKey = "datapulse.console.create-watch-draft.v2";
    const commandPaletteQueryStorageKey = "datapulse.console.palette-query.v1";
    const commandPaletteRecentStorageKey = "datapulse.console.palette-recent.v1";
    const contextLinkHistoryStorageKey = "datapulse.console.context-history.v1";
    const contextSavedViewsStorageKey = "datapulse.console.context-saved-views.v1";
    const watchUrlSearchParam = "watch_search";
    const watchUrlIdParam = "watch_id";
    const triageUrlFilterParam = "triage_filter";
    const triageUrlSearchParam = "triage_search";
    const triageUrlIdParam = "triage_id";
    const storyUrlViewParam = "story_view";
    const storyUrlFilterParam = "story_filter";
    const storyUrlSortParam = "story_sort";
    const storyUrlSearchParam = "story_search";
    const storyUrlIdParam = "story_id";
    const storyUrlModeParam = "story_mode";
    const storyFilterStorageKey = "datapulse.console.story-filter.v1";
    const storySortStorageKey = "datapulse.console.story-sort.v1";
    const storyWorkspaceModeStorageKey = "datapulse.console.story-workspace-mode.v1";
    const createWatchFormFields = ["name", "schedule", "query", "platform", "domain", "route", "keyword", "min_score", "min_confidence"];
    const routeFormFields = [
      "name",
      "channel",
      "description",
      "webhook_url",
      "authorization",
      "headers_json",
      "feishu_webhook",
      "telegram_bot_token",
      "telegram_chat_id",
      "timeout_seconds",
    ];
    const triageFilterOptions = ["open", "all", "new", "triaged", "verified", "duplicate", "ignored", "escalated"];
    const workspaceModeSectionMap = {{
      intake: ["section-intake"],
      missions: ["section-board", "section-cockpit"],
      review: ["section-triage", "section-story", "section-claims", "section-report-studio"],
      delivery: ["section-ops"],
    }};
    const reviewAdvancedSectionIds = ["section-claims", "section-report-studio"];

    function copy(enText, zhText) {{
      return state.language === "zh" ? zhText : enText;
    }}

    function phrase(enText, zhText, values = {{}}) {{
      const template = copy(enText, zhText);
      return String(template).replace(/\\{{(\\w+)\\}}/g, (_, key) => String(values[key] ?? ""));
    }}

    function localizeWord(value) {{
      const raw = String(value || "").trim();
      const key = raw.toLowerCase();
      const map = {{
        active: ["active", "活跃"],
        aligned: ["aligned", "一致"],
        all: ["all", "全部"],
        approve: ["approve", "批准"],
        approved: ["approved", "已批准"],
        blocked: ["blocked", "已阻断"],
        brief: ["brief", "摘要"],
        closed: ["closed", "关闭"],
        clear: ["clear", "清晰"],
        conflicted: ["conflicted", "冲突"],
        degraded: ["degraded", "降级"],
        disabled: ["disabled", "已停用"],
        done: ["done", "完成"],
        draft: ["draft", "草稿"],
        due: ["due", "待执行"],
        editable: ["editable", "可编辑"],
        duplicate: ["duplicate", "重复"],
        escalated: ["escalated", "已升级"],
        error: ["error", "错误"],
        events: ["events", "事件"],
        feishu: ["feishu", "飞书"],
        full: ["full", "完整版"],
        healthy: ["healthy", "健康"],
        hold_export: ["hold export", "暂停导出"],
        idle: ["idle", "空闲"],
        ignored: ["ignored", "已忽略"],
        keep: ["keep", "保留"],
        pass: ["pass", "通过"],
        manual: ["manual", "手动"],
        merge: ["merge", "合并"],
        missing: ["missing", "缺失"],
        mixed: ["mixed", "混合"],
        monitoring: ["monitoring", "监控中"],
        new: ["new", "新建"],
        ok: ["ok", "正常"],
        open: ["open", "开放"],
        pending: ["pending", "处理中"],
        paused: ["paused", "已暂停"],
        profile: ["profile", "配置"],
        pull: ["pull", "拉取"],
        push: ["push", "推送"],
        ready: ["ready", "就绪"],
        report: ["report", "报告"],
        resolved: ["resolved", "已解决"],
        rss: ["rss", "rss"],
        review_before_export: ["review before export", "导出前复核"],
        reviewed: ["reviewed", "已复核"],
        review_required: ["review required", "需要复核"],
        running: ["running", "运行中"],
        same: ["same", "相同"],
        sources: ["sources", "来源清单"],
        story: ["story", "故事"],
        success: ["success", "成功"],
        synced: ["synced", "已同步"],
        telegram: ["telegram", "telegram"],
        triaged: ["triaged", "已分诊"],
        unknown: ["unknown", "未知"],
        verified: ["verified", "已核验"],
        waiting: ["waiting", "等待"],
        warn: ["warn", "警告"],
        warning: ["warning", "警告"],
        watch_mission: ["watch mission", "监控任务"],
        webhook: ["webhook", "webhook"],
        markdown: ["markdown", "markdown"],
      }};
      const pair = map[key];
      return pair ? copy(pair[0], pair[1]) : raw;
    }}

    function localizeBoolean(value) {{
      return value ? copy("yes", "是") : copy("no", "否");
    }}
    const createWatchPresets = [
      {{
        id: "launch",
        label: "Launch Pulse",
        zhLabel: "发布脉冲",
        description: "Tight interval for product or company launches.",
        zhDescription: "适合产品或公司发布场景的高频任务。",
        values: {{
          name: "Launch Pulse",
          schedule: "interval:15m",
          query: "OpenAI launch",
          platform: "twitter",
          domain: "",
          route: "",
          keyword: "launch",
          min_score: "70",
          min_confidence: "0.75",
        }},
      }},
      {{
        id: "risk",
        label: "Risk Sweep",
        zhLabel: "风险巡检",
        description: "Higher confidence gate for operational risk review.",
        zhDescription: "适合运维风险巡检的高置信度门槛。",
        values: {{
          name: "Risk Sweep",
          schedule: "@hourly",
          query: "service outage rumor",
          platform: "web",
          domain: "",
          route: "",
          keyword: "outage",
          min_score: "80",
          min_confidence: "0.88",
        }},
      }},
      {{
        id: "market",
        label: "Market Shift",
        zhLabel: "市场异动",
        description: "Cross-signal watch for moves around listed names.",
        zhDescription: "适合上市主体异动监测的跨信号任务。",
        values: {{
          name: "Market Shift",
          schedule: "@hourly",
          query: "Xiaomi earnings",
          platform: "news",
          domain: "",
          route: "",
          keyword: "earnings",
          min_score: "68",
          min_confidence: "0.8",
        }},
      }},
      {{
        id: "creator",
        label: "Creator Surge",
        zhLabel: "创作者热度",
        description: "Faster scan for creator and social breakout chatter.",
        zhDescription: "适合创作者与社媒爆发信号的快速扫描。",
        values: {{
          name: "Creator Surge",
          schedule: "interval:30m",
          query: "viral creator trend",
          platform: "reddit",
          domain: "",
          route: "",
          keyword: "viral",
          min_score: "55",
          min_confidence: "0.65",
        }},
      }},
    ];
    const scheduleLaneOptions = [
      {{ label: "manual", value: "manual" }},
      {{ label: "15m", value: "interval:15m" }},
      {{ label: "30m", value: "interval:30m" }},
      {{ label: "hourly", value: "@hourly" }},
    ];
    const platformLaneOptions = [
      {{ label: "twitter", value: "twitter" }},
      {{ label: "reddit", value: "reddit" }},
      {{ label: "news", value: "news" }},
      {{ label: "web", value: "web" }},
    ];
    const routeChannelOptions = [
      {{ label: "Webhook", zhLabel: "Webhook", value: "webhook" }},
      {{ label: "Telegram", zhLabel: "Telegram", value: "telegram" }},
      {{ label: "Feishu", zhLabel: "飞书", value: "feishu" }},
      {{ label: "Markdown", zhLabel: "Markdown", value: "markdown" }},
    ];
    const claimStatusOptions = ["draft", "reviewed", "ready", "conflicted", "blocked"];
    const reportStatusOptions = ["draft", "review_required", "ready", "blocked"];
    const storyStatusOptions = ["active", "monitoring", "resolved", "archived"];
    const storySortOptions = ["attention", "recent", "evidence", "conflict", "score"];
    const storyWorkspaceModeOptions = ["board", "editor"];
    const storyViewPresetOptions = ["desk", "fresh", "conflicts", "archive"];
    const scoreSuggestionOptions = ["40", "55", "68", "70", "80", "90"];
    const confidenceSuggestionOptions = ["0.6", "0.65", "0.75", "0.8", "0.88", "0.95"];
    const deliverySubjectOptions = ["profile", "watch_mission", "story", "report"];
    const deliveryModeOptions = ["pull", "push"];
    const deliveryStatusOptions = ["active", "paused", "disabled"];
    const deliveryOutputOptionsBySubject = {{
      profile: ["feed_json", "feed_rss", "feed_atom"],
      watch_mission: ["alert_event"],
      story: ["story_json", "story_markdown"],
      report: ["report_brief", "report_full", "report_sources", "report_watch_pack"],
    }};

    function uniqueValues(values) {{
      return Array.from(new Set((Array.isArray(values) ? values : [values])
        .flatMap((value) => Array.isArray(value) ? value : [value])
        .map((value) => String(value ?? "").trim())
        .filter(Boolean)));
    }}

    function normalizeStorySort(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "attention";
      return storySortOptions.includes(normalized) ? normalized : "attention";
    }}

    function normalizeStoryFilter(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "all";
      if (normalized === "all" || normalized === "conflicted") {{
        return normalized;
      }}
      return storyStatusOptions.includes(normalized) ? normalized : "all";
    }}

    function normalizeStoryWorkspaceMode(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "board";
      return storyWorkspaceModeOptions.includes(normalized) ? normalized : "board";
    }}

    function normalizeTriageFilter(value) {{
      const normalized = String(value || "").trim().toLowerCase() || "open";
      return triageFilterOptions.includes(normalized) ? normalized : "open";
    }}

    function storyViewPresetLabel(viewKey) {{
      const labels = {{
        desk: copy("Ops Desk", "运营台"),
        fresh: copy("Fresh Radar", "新近雷达"),
        conflicts: copy("Conflict Queue", "冲突队列"),
        archive: copy("Archive Review", "归档回看"),
        custom: copy("Custom", "自定义"),
      }};
      return labels[String(viewKey || "").trim().toLowerCase()] || labels.custom;
    }}

    function storyViewPresetDescription(viewKey) {{
      const descriptions = {{
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
      }};
      return descriptions[String(viewKey || "").trim().toLowerCase()] || descriptions.custom;
    }}

    function getStoryViewPreset(viewKey) {{
      const normalized = String(viewKey || "").trim().toLowerCase();
      const presets = {{
        desk: {{ key: "desk", filter: "all", sort: "attention" }},
        fresh: {{ key: "fresh", filter: "all", sort: "recent" }},
        conflicts: {{ key: "conflicts", filter: "conflicted", sort: "conflict" }},
        archive: {{ key: "archive", filter: "archived", sort: "recent" }},
      }};
      return presets[normalized] || null;
    }}

    function detectStoryViewPreset({{ filter = "all", sort = "attention", search = "" }} = {{}}) {{
      if (String(search || "").trim()) {{
        return "custom";
      }}
      const normalizedFilter = normalizeStoryFilter(filter);
      const normalizedSort = normalizeStorySort(sort);
      const matchedPreset = storyViewPresetOptions.find((viewKey) => {{
        const preset = getStoryViewPreset(viewKey);
        return preset && preset.filter === normalizedFilter && preset.sort === normalizedSort;
      }});
      return matchedPreset || "custom";
    }}

    function storySortLabel(sortKey) {{
      const normalized = normalizeStorySort(sortKey);
      const labels = {{
        attention: copy("Attention Order", "优先级排序"),
        recent: copy("Most Recent", "最近更新"),
        evidence: copy("Most Evidence", "证据最多"),
        conflict: copy("Conflict Load", "冲突强度"),
        score: copy("Highest Score", "最高分数"),
      }};
      return labels[normalized] || labels.attention;
    }}

    function storySortSummary(sortKey) {{
      const normalized = normalizeStorySort(sortKey);
      const summaries = {{
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
      }};
      return summaries[normalized] || summaries.attention;
    }}

    function parseDateValue(value) {{
      const stamp = Date.parse(String(value || "").trim());
      return Number.isFinite(stamp) ? stamp : 0;
    }}

    function formatCompactDateTime(value) {{
      const stamp = parseDateValue(value);
      if (!stamp) {{
        return "-";
      }}
      const formatter = new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-US", {{
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }});
      return formatter.format(new Date(stamp));
    }}

    function getStoryUpdatedAt(story) {{
      return parseDateValue((story && (story.updated_at || story.generated_at)) || "");
    }}

    function getStoryContradictionCount(story) {{
      return Array.isArray(story?.contradictions) ? story.contradictions.length : 0;
    }}

    function getStoryAttentionScore(story) {{
      const status = String(story?.status || "active").trim().toLowerCase() || "active";
      const contradictionCount = getStoryContradictionCount(story);
      const itemCount = Math.max(0, Number(story?.item_count || 0));
      const sourceCount = Math.max(0, Number(story?.source_count || 0));
      const score = Number(story?.score || 0);
      const confidence = Number(story?.confidence || 0);
      const updatedAt = getStoryUpdatedAt(story);
      const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
      const freshness = Math.max(0, 48 - Math.min(48, ageHours));
      const statusWeights = {{
        active: 40,
        monitoring: 26,
        resolved: 10,
        archived: -24,
      }};
      return (
        contradictionCount * 70 +
        itemCount * 8 +
        sourceCount * 4 +
        score * 0.4 +
        confidence * 18 +
        freshness +
        (statusWeights[status] ?? 16)
      );
    }}

    function compareNumberDesc(leftValue, rightValue) {{
      if (leftValue === rightValue) {{
        return 0;
      }}
      return leftValue < rightValue ? 1 : -1;
    }}

    function compareStoriesByWorkspaceOrder(left, right, sortKey) {{
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
      for (const result of chain) {{
        if (result) {{
          return result;
        }}
      }}
      return String(left?.title || left?.id || "").localeCompare(String(right?.title || right?.id || ""));
    }}

    function describeStoryPriority(story) {{
      const contradictionCount = getStoryContradictionCount(story);
      const itemCount = Math.max(0, Number(story?.item_count || 0));
      const status = String(story?.status || "active").trim().toLowerCase() || "active";
      const updatedAt = getStoryUpdatedAt(story);
      const ageHours = updatedAt ? Math.max(0, (Date.now() - updatedAt) / 3600000) : 999;
      if (status === "archived") {{
        return {{ tone: "", label: copy("cold lane", "冷队列") }};
      }}
      if (contradictionCount > 0) {{
        return {{
          tone: "hot",
          label: phrase("conflict x{{count}}", "冲突 x{{count}}", {{ count: contradictionCount }}),
        }};
      }}
      if (ageHours <= 12) {{
        return {{ tone: "ok", label: copy("fresh update", "新近更新") }};
      }}
      if (itemCount >= 4) {{
        return {{ tone: "ok", label: copy("deep evidence", "证据较多") }};
      }}
      if (status === "monitoring") {{
        return {{ tone: "", label: copy("watching", "持续监控") }};
      }}
      if (status === "resolved") {{
        return {{ tone: "", label: copy("resolved lane", "已解决") }};
      }}
      return {{ tone: "ok", label: copy("active lane", "活跃队列") }};
    }}

    function renderDatalist(identifier, values) {{
      const root = $(identifier);
      if (!root) {{
        return;
      }}
      root.innerHTML = uniqueValues(values).slice(0, 32).map((value) => `<option value="${{escapeHtml(value)}}"></option>`).join("");
    }}

    function collectWatchValues(fieldName) {{
      return [
        ...state.watches.map((watch) => watch ? watch[fieldName] : ""),
        ...Object.values(state.watchDetails || {{}}).map((watch) => watch ? watch[fieldName] : ""),
      ];
    }}

    function collectWatchArrayValues(fieldName) {{
      return [
        ...state.watches.flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
        ...Object.values(state.watchDetails || {{}}).flatMap((watch) => Array.isArray(watch?.[fieldName]) ? watch[fieldName] : []),
      ];
    }}

    function collectAlertRuleValues(fieldName) {{
      return Object.values(state.watchDetails || {{}}).flatMap((watch) => {{
        return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).flatMap((rule) => {{
          const raw = rule ? rule[fieldName] : "";
          return Array.isArray(raw) ? raw : [raw];
        }});
      }});
    }}

    function collectRouteNames() {{
      return state.routes.map((route) => route && (route.name || route.route_name || route.id || ""));
    }}

    function renderFormSuggestionLists() {{
      const suggestionPatch = state.createWatchSuggestions?.autofill_patch || {{}};
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
    }}

    function defaultCreateWatchDraft() {{
      return {{
        name: "",
        schedule: "",
        query: "",
        platform: "",
        domain: "",
        route: "",
        keyword: "",
        min_score: "",
        min_confidence: "",
      }};
    }}

    function draftHasAdvancedSignal(payload = {{}}) {{
      const draft = normalizeCreateWatchDraft(payload || defaultCreateWatchDraft());
      return Boolean(
        draft.schedule.trim() ||
        draft.platform.trim() ||
        draft.domain.trim() ||
        draft.route.trim() ||
        draft.keyword.trim() ||
        draft.min_score.trim() ||
        draft.min_confidence.trim()
      );
    }}

    function normalizeCreateWatchDraft(payload = {{}}) {{
      const draft = defaultCreateWatchDraft();
      createWatchFormFields.forEach((field) => {{
        draft[field] = String(payload[field] ?? "");
      }});
      return draft;
    }}

    function isCreateWatchAdvancedOpen(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      if (typeof state.createWatchAdvancedOpen === "boolean") {{
        return state.createWatchAdvancedOpen;
      }}
      return Boolean(String(state.createWatchEditingId || "").trim() || draftHasAdvancedSignal(draft));
    }}

    function summarizeCreateWatchAdvanced(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      const chips = [];
      if (draft.schedule.trim()) {{
        chips.push(scheduleModeLabel(draft.schedule));
      }}
      if (draft.platform.trim()) {{
        chips.push(phrase("platform: {{value}}", "平台：{{value}}", {{ value: draft.platform.trim() }}));
      }}
      if (draft.domain.trim()) {{
        chips.push(phrase("domain: {{value}}", "域名：{{value}}", {{ value: draft.domain.trim() }}));
      }}
      if (draft.route.trim()) {{
        chips.push(phrase("route: {{value}}", "路由：{{value}}", {{ value: draft.route.trim() }}));
      }}
      if (draft.keyword.trim()) {{
        chips.push(phrase("keyword: {{value}}", "关键词：{{value}}", {{ value: draft.keyword.trim() }}));
      }}
      if (draft.min_score.trim()) {{
        chips.push(phrase("score >= {{value}}", "分数 >= {{value}}", {{ value: draft.min_score.trim() }}));
      }}
      if (draft.min_confidence.trim()) {{
        chips.push(phrase("confidence >= {{value}}", "置信度 >= {{value}}", {{ value: draft.min_confidence.trim() }}));
      }}
      if (!chips.length) {{
        chips.push(copy("No scope or alert gate yet", "当前还没有范围或告警门槛"));
      }}
      return chips.slice(0, 6);
    }}

    function defaultRouteDraft() {{
      return {{
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
      }};
    }}

    function normalizeRouteDraft(payload = {{}}) {{
      const draft = defaultRouteDraft();
      routeFormFields.forEach((field) => {{
        if (field === "channel") {{
          return;
        }}
        draft[field] = String(payload[field] ?? draft[field] ?? "");
      }});
      const channel = String(payload.channel ?? draft.channel ?? "webhook").trim().toLowerCase();
      draft.channel = routeChannelOptions.some((option) => option.value === channel) ? channel : "webhook";
      return draft;
    }}

    function routeChannelLabel(channel) {{
      const normalized = String(channel || "").trim().toLowerCase();
      const option = routeChannelOptions.find((candidate) => candidate.value === normalized);
      if (!option) {{
        return normalized || copy("unknown", "未知");
      }}
      return copy(option.label, option.zhLabel || option.label);
    }}

    function routeDraftHasAdvancedSignal(payload = {{}}) {{
      const draft = normalizeRouteDraft(payload || defaultRouteDraft());
      return Boolean(
        draft.description.trim() ||
        draft.authorization.trim() ||
        draft.headers_json.trim() ||
        draft.timeout_seconds.trim()
      );
    }}

    function isRouteAdvancedOpen(draftInput) {{
      const draft = normalizeRouteDraft(draftInput || defaultRouteDraft());
      if (typeof state.routeAdvancedOpen === "boolean") {{
        return state.routeAdvancedOpen;
      }}
      return Boolean(String(state.routeEditingId || "").trim() || routeDraftHasAdvancedSignal(draft));
    }}

    function normalizeRouteName(value) {{
      return String(value || "").trim().toLowerCase();
    }}

    function normalizeRouteRuleNames(rule) {{
      if (!rule) {{
        return [];
      }}
      const raw = Array.isArray(rule.routes) ? rule.routes : [rule.route];
      return uniqueValues(raw).map((value) => normalizeRouteName(value)).filter(Boolean);
    }}

    function watchUsesRoute(watch, routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return false;
      }}
      return (Array.isArray(watch?.alert_rules) ? watch.alert_rules : []).some((rule) => {{
        return normalizeRouteRuleNames(rule).includes(normalized);
      }});
    }}

    function getRouteUsageRows(routeName) {{
      const rows = [
        ...state.watches,
        ...Object.values(state.watchDetails || {{}}),
      ];
      const seen = new Set();
      return rows.filter((watch) => {{
        const identifier = String(watch?.id || "").trim();
        if (!identifier || seen.has(identifier)) {{
          return false;
        }}
        seen.add(identifier);
        return watchUsesRoute(watch, routeName);
      }});
    }}

    function getRouteUsageCount(routeName) {{
      return getRouteUsageRows(routeName).length;
    }}

    function getRouteUsageNames(routeName) {{
      return getRouteUsageRows(routeName).map((watch) => String(watch.name || watch.id || "").trim()).filter(Boolean);
    }}

    function getRouteHealthRow(routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return null;
      }}
      return state.routeHealth.find((route) => normalizeRouteName(route?.name) === normalized) || null;
    }}

    function summarizeUrlHost(rawUrl) {{
      const value = String(rawUrl || "").trim();
      if (!value) {{
        return "";
      }}
      try {{
        const parsed = new URL(value);
        const path = parsed.pathname && parsed.pathname !== "/" ? parsed.pathname.slice(0, 18) : "";
        return `${{parsed.host}}${{path}}`;
      }} catch {{
        return value;
      }}
    }}

    function summarizeRouteDestination(route) {{
      const channel = normalizeRouteName(route?.channel);
      if (channel === "webhook") {{
        return route?.webhook_url
          ? summarizeUrlHost(route.webhook_url)
          : copy("Webhook URL missing", "Webhook URL 未配置");
      }}
      if (channel === "feishu") {{
        return route?.feishu_webhook
          ? summarizeUrlHost(route.feishu_webhook)
          : copy("Feishu webhook missing", "飞书 webhook 未配置");
      }}
      if (channel === "telegram") {{
        return route?.telegram_chat_id
          ? phrase("chat {{value}}", "会话 {{value}}", {{ value: route.telegram_chat_id }})
          : copy("Telegram chat missing", "Telegram 会话未配置");
      }}
      if (channel === "markdown") {{
        return copy("Append to alert markdown log", "追加到告警 Markdown 日志");
      }}
      return copy("Route target not configured", "路由目标未配置");
    }}

    function createRouteDraftFromRoute(route) {{
      const rawHeaders = route && typeof route.headers === "object" && !Array.isArray(route.headers)
        ? {{ ...route.headers }}
        : {{}};
      let authorization = "";
      if (typeof route?.authorization === "string" && route.authorization !== "***") {{
        authorization = route.authorization;
      }}
      if (!authorization && typeof rawHeaders.Authorization === "string" && rawHeaders.Authorization !== "***") {{
        authorization = rawHeaders.Authorization;
      }}
      delete rawHeaders.Authorization;
      return normalizeRouteDraft({{
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
      }});
    }}

    function collectRouteDraft(form) {{
      if (!form) {{
        return normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
      }}
      const next = defaultRouteDraft();
      routeFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        next[fieldName] = field ? String(field.value ?? "") : "";
      }});
      return normalizeRouteDraft(next);
    }}

    function setRouteDraft(nextDraft, editingId = state.routeEditingId) {{
      state.routeDraft = normalizeRouteDraft(nextDraft || defaultRouteDraft());
      state.routeEditingId = String(editingId || "").trim();
      const deliveryFeedback = state.stageFeedback?.deliver;
      if (deliveryFeedback && ["blocked", "warning", "no_result"].includes(String(deliveryFeedback.kind || "").trim().toLowerCase())) {{
        state.stageFeedback.deliver = null;
      }}
      renderRouteDeck();
    }}

    function focusRouteDeck(fieldName = "name") {{
      jumpToSection("section-ops");
      window.setTimeout(() => {{
        $("route-manager-shell")?.scrollIntoView({{ block: "start", behavior: "smooth" }});
        const form = $("route-form");
        const field = form?.elements?.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
        }}
      }}, 140);
    }}

    async function editRouteInDeck(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      const route = state.routes.find((item) => normalizeRouteName(item?.name) === normalized);
      if (!route) {{
        throw new Error(copy("Alert route not found in current board state.", "当前看板中没有找到该告警路由。"));
      }}
      setContextRouteName(normalized, "section-ops");
      state.routeAdvancedOpen = true;
      setRouteDraft(createRouteDraftFromRoute(route), normalized);
      focusRouteDeck(route.channel === "markdown" ? "description" : "name");
    }}

    async function applyRouteToMissionDraft(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      state.createWatchAdvancedOpen = true;
      updateCreateWatchDraft({{ route: normalized }});
      focusCreateWatchDeck("route");
      showToast(
        state.language === "zh"
          ? `已把路由载入任务草稿：${{normalized}}`
          : `Route loaded into mission deck: ${{normalized}}`,
        "success",
      );
    }}

    function parseRouteHeaders(rawValue) {{
      const text = String(rawValue || "").trim();
      if (!text) {{
        return null;
      }}
      let parsed;
      try {{
        parsed = JSON.parse(text);
      }} catch (error) {{
        throw new Error(copy("Custom headers must be valid JSON.", "自定义请求头必须是合法 JSON。"));
      }}
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {{
        throw new Error(copy("Custom headers must be a JSON object.", "自定义请求头必须是 JSON 对象。"));
      }}
      return Object.fromEntries(
        Object.entries(parsed)
          .map(([key, value]) => [String(key || "").trim(), String(value ?? "").trim()])
          .filter(([key]) => Boolean(key)),
      );
    }}

    function defaultStoryDraft() {{
      return {{
        title: "",
        summary: "",
        status: "active",
      }};
    }}

    function normalizeStoryDraft(payload = {{}}) {{
      return {{
        title: String(payload.title ?? "").trimStart(),
        summary: String(payload.summary ?? ""),
        status: storyStatusOptions.includes(String(payload.status || "").trim().toLowerCase())
          ? String(payload.status || "").trim().toLowerCase()
          : "active",
      }};
    }}

    function collectStoryDraft(form) {{
      if (!form) {{
        return normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
      }}
      return normalizeStoryDraft({{
        title: String(form.elements.namedItem("title")?.value || ""),
        summary: String(form.elements.namedItem("summary")?.value || ""),
        status: String(form.elements.namedItem("status")?.value || "active"),
      }});
    }}

    function setStoryDraft(nextDraft) {{
      state.storyDraft = normalizeStoryDraft(nextDraft || defaultStoryDraft());
      const reviewFeedback = state.stageFeedback?.review;
      if (reviewFeedback && ["blocked", "warning", "no_result"].includes(String(reviewFeedback.kind || "").trim().toLowerCase())) {{
        state.stageFeedback.review = null;
      }}
      renderStoryCreateDeck();
    }}

    function focusStoryDeck(fieldName = "title") {{
      jumpToSection("section-story");
      window.setTimeout(() => {{
        $("story-intake-shell")?.scrollIntoView({{ block: "start", behavior: "smooth" }});
        const form = $("story-create-form");
        const field = form?.elements?.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
        }}
      }}, 140);
    }}

    function getStoryRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.storyDetails[normalized] || state.stories.find((story) => story.id === normalized) || null;
    }}

    function removeStoryFromState(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      state.stories = state.stories.filter((story) => story.id !== normalized);
      delete state.storyDetails[normalized];
      delete state.storyGraph[normalized];
      delete state.storyMarkdown[normalized];
      if (state.selectedStoryId === normalized) {{
        state.selectedStoryId = state.stories[0] ? state.stories[0].id : "";
      }}
    }}

    function parseDelimitedInput(value) {{
      return uniqueValues(
        String(value || "")
          .split(",")
          .flatMap((value) => value.split(String.fromCharCode(10)).map((value) => value.replace(String.fromCharCode(13), "")))
      );
    }}

    function getClaimCardLabel(claim) {{
      if (!claim || typeof claim !== "object") {{
        return "";
      }}
      return String(claim.statement || claim.title || claim.id || "").trim();
    }}

    function getClaimCardRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.claimCards.find((claim) => String(claim.id || "").trim() === normalized) || null;
    }}

    function getReportRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const compositionReport = state.reportCompositions[normalized]?.report;
      if (compositionReport && typeof compositionReport === "object") {{
        return compositionReport;
      }}
      return state.reports.find((report) => String(report.id || "").trim() === normalized) || null;
    }}

    function getReportSectionsForReport(reportId) {{
      const normalized = String(reportId || "").trim();
      if (!normalized) {{
        return [];
      }}
      return state.reportSections
        .filter((section) => String(section.report_id || "").trim() === normalized)
        .sort((left, right) => {{
          const leftPosition = Number(left.position || 0);
          const rightPosition = Number(right.position || 0);
          if (leftPosition !== rightPosition) {{
            return leftPosition - rightPosition;
          }}
          return String(left.title || left.id || "").localeCompare(String(right.title || right.id || ""));
        }});
    }}

    function getReportComposition(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const payload = state.reportCompositions[normalized];
      return payload && typeof payload === "object" ? payload : null;
    }}

    function getSelectedClaimCard() {{
      return getClaimCardRecord(state.selectedClaimId);
    }}

    function getSelectedReportRecord() {{
      return getReportRecord(state.selectedReportId);
    }}

    function getSelectedReportSectionRecord() {{
      const selectedReport = getSelectedReportRecord();
      if (!selectedReport) {{
        return null;
      }}
      const sections = getReportSectionsForReport(selectedReport.id);
      return sections.find((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim()) || null;
    }}

    function getReportClaimIds(reportId) {{
      const composition = getReportComposition(reportId);
      if (composition && Array.isArray(composition.claim_cards)) {{
        return uniqueValues(composition.claim_cards.map((claim) => String(claim.id || "").trim()));
      }}
      const report = getReportRecord(reportId);
      return uniqueValues(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []);
    }}

    function getCitationBundleRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.citationBundles.find((bundle) => String(bundle.id || "").trim() === normalized) || null;
    }}

    function reportStatusTone(status) {{
      const normalized = String(status || "").trim().toLowerCase();
      if (["ready", "ok", "pass", "clear", "success", "approved"].includes(normalized)) {{
        return "ok";
      }}
      if (["blocked", "error", "fail", "failed", "review_required", "warning", "warn", "conflicted"].includes(normalized)) {{
        return "hot";
      }}
      return "";
    }}

    function formatReportCheckLabel(key) {{
      const normalized = String(key || "").trim().toLowerCase();
      const labels = {{
        claim_source: copy("Claim source binding", "主张来源绑定"),
        section_coverage: copy("Section coverage", "章节覆盖"),
        contradictions: copy("Contradictions", "冲突"),
        export_gates: copy("Export gates", "导出门禁"),
        fact_consistency: copy("Fact consistency", "事实一致性"),
        coverage: copy("Coverage", "覆盖度"),
      }};
      return labels[normalized] || String(key || "").replace(/_/g, " ").trim();
    }}

    function formatReportOperatorAction(action) {{
      const normalized = String(action || "").trim().toLowerCase();
      const labels = {{
        allow_export: copy("Allow export", "允许导出"),
        review_before_export: copy("Review before export", "导出前复核"),
        hold_export: copy("Hold export", "暂停导出"),
        approve: copy("Approve", "批准"),
      }};
      return labels[normalized] || String(action || "").replace(/_/g, " ").trim();
    }}

    function syncReportSelectionState() {{
      const availableReports = Array.isArray(state.reports) ? state.reports : [];
      if (!availableReports.some((report) => String(report.id || "").trim() === String(state.selectedReportId || "").trim())) {{
        state.selectedReportId = availableReports[0] ? String(availableReports[0].id || "") : "";
      }}
      const sections = getReportSectionsForReport(state.selectedReportId);
      if (!sections.some((section) => String(section.id || "").trim() === String(state.selectedReportSectionId || "").trim())) {{
        state.selectedReportSectionId = sections[0] ? String(sections[0].id || "") : "";
      }}
      const availableClaims = Array.isArray(state.claimCards) ? state.claimCards : [];
      if (!availableClaims.some((claim) => String(claim.id || "").trim() === String(state.selectedClaimId || "").trim())) {{
        const reportClaimIds = getReportClaimIds(state.selectedReportId);
        const matchingClaim = availableClaims.find((claim) => reportClaimIds.includes(String(claim.id || "").trim()));
        state.selectedClaimId = matchingClaim
          ? String(matchingClaim.id || "")
          : (availableClaims[0] ? String(availableClaims[0].id || "") : "");
      }}
    }}

    async function loadReportComposition(identifier, {{ includeMarkdown = false, render = true, force = false }} = {{}}) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      if (force || !state.reportCompositions[normalized]) {{
        state.reportCompositions[normalized] = await api(`/api/reports/${{normalized}}/compose`);
      }}
      if (includeMarkdown && (force || !state.reportMarkdown[normalized])) {{
        state.reportMarkdown[normalized] = await apiText(`/api/reports/${{normalized}}/export?output_format=markdown`);
      }}
      if (render) {{
        renderClaimsWorkspace();
        renderReportStudio();
        renderTopbarContext();
      }}
    }}

    async function selectReport(identifier, {{ sectionId = "" }} = {{}}) {{
      state.selectedReportId = String(identifier || "").trim();
      if (sectionId) {{
        state.selectedReportSectionId = String(sectionId || "").trim();
      }}
      syncReportSelectionState();
      renderClaimsWorkspace();
      renderReportStudio();
      renderTopbarContext();
      if (state.selectedReportId) {{
        await loadReportComposition(state.selectedReportId);
      }}
    }}

    async function previewReportMarkdown(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      state.reportMarkdown[normalized] = await apiText(`/api/reports/${{normalized}}/export?output_format=markdown`);
      renderReportStudio();
    }}

    function formatDeliverySubjectKind(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      const labels = {{
        profile: copy("Profile", "配置"),
        watch_mission: copy("Mission", "任务"),
        story: copy("Story", "故事"),
        report: copy("Report", "报告"),
      }};
      return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
    }}

    function formatDeliveryOutputKind(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      const labels = {{
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
      }};
      return labels[normalized] || String(value || "").replace(/_/g, " ").trim();
    }}

    function defaultDeliveryDraft() {{
      const selectedReport = getSelectedReportRecord();
      const firstReport = Array.isArray(state.reports) && state.reports.length ? state.reports[0] : null;
      const report = selectedReport || firstReport;
      const firstRoute = Array.isArray(state.routes) && state.routes.length
        ? normalizeRouteName(state.routes[0]?.name)
        : "";
      return {{
        subject_kind: report ? "report" : "profile",
        subject_ref: report ? String(report.id || "").trim() : "default",
        output_kind: report ? "report_full" : "feed_json",
        delivery_mode: firstRoute ? "push" : "pull",
        status: "active",
        route_names: firstRoute ? [firstRoute] : [],
        cursor_or_since: "",
      }};
    }}

    function getDeliverySubjectRefOptions(subjectKind) {{
      const normalized = String(subjectKind || "").trim().toLowerCase();
      if (normalized === "profile") {{
        return [{{
          value: "default",
          label: copy("Default profile", "默认配置"),
          detail: copy("Use the canonical feed subscription target.", "使用默认的订阅配置目标。"),
        }}];
      }}
      if (normalized === "watch_mission") {{
        return (Array.isArray(state.watches) ? state.watches : []).map((watch) => ({{
          value: String(watch.id || "").trim(),
          label: String(watch.name || watch.id || "").trim(),
          detail: String(watch.query || "").trim(),
        }}));
      }}
      if (normalized === "story") {{
        return (Array.isArray(state.stories) ? state.stories : []).map((story) => ({{
          value: String(story.id || "").trim(),
          label: String(story.title || story.id || "").trim(),
          detail: String(story.summary || "").trim(),
        }}));
      }}
      if (normalized === "report") {{
        return (Array.isArray(state.reports) ? state.reports : []).map((report) => ({{
          value: String(report.id || "").trim(),
          label: String(report.title || report.id || "").trim(),
          detail: String(report.summary || "").trim(),
        }}));
      }}
      return [];
    }}

    function getDeliveryOutputOptions(subjectKind) {{
      const normalized = String(subjectKind || "").trim().toLowerCase();
      return (deliveryOutputOptionsBySubject[normalized] || []).map((value) => ({{
        value,
        label: formatDeliveryOutputKind(value),
      }}));
    }}

    function normalizeDeliveryDraft(draft) {{
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
      return {{
        subject_kind: subjectKind,
        subject_ref: subjectRef,
        output_kind: outputKind,
        delivery_mode: deliveryMode,
        status,
        route_names: routeNames,
        cursor_or_since: String(source.cursor_or_since || "").trim(),
      }};
    }}

    function collectDeliveryDraft(form) {{
      const formData = new FormData(form);
      return normalizeDeliveryDraft({{
        subject_kind: formData.get("subject_kind"),
        subject_ref: formData.get("subject_ref"),
        output_kind: formData.get("output_kind"),
        delivery_mode: formData.get("delivery_mode"),
        status: formData.get("status"),
        route_names: parseDelimitedInput(formData.get("route_names")),
        cursor_or_since: formData.get("cursor_or_since"),
      }});
    }}

    function syncDeliveryDraft() {{
      state.deliveryDraft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
    }}

    function defaultDigestProfileDraft() {{
      const profile = state.digestConsole?.profile?.profile && typeof state.digestConsole.profile.profile === "object"
        ? state.digestConsole.profile.profile
        : {{}};
      const target = profile.default_delivery_target && typeof profile.default_delivery_target === "object"
        ? profile.default_delivery_target
        : {{}};
      const firstRoute = Array.isArray(state.routes) && state.routes.length
        ? normalizeRouteName(state.routes[0]?.name)
        : "";
      return {{
        language: String(profile.language || "en").trim() || "en",
        timezone: String(profile.timezone || "UTC").trim() || "UTC",
        frequency: String(profile.frequency || "@daily").trim() || "@daily",
        default_delivery_target: {{
          kind: "route",
          ref: normalizeRouteName(target.ref || firstRoute),
        }},
      }};
    }}

    function normalizeDigestProfileDraft(draft) {{
      const source = draft && typeof draft === "object" ? draft : defaultDigestProfileDraft();
      const target = source.default_delivery_target && typeof source.default_delivery_target === "object"
        ? source.default_delivery_target
        : {{}};
      return {{
        language: String(source.language || "en").trim() || "en",
        timezone: String(source.timezone || "UTC").trim() || "UTC",
        frequency: String(source.frequency || "@daily").trim() || "@daily",
        default_delivery_target: {{
          kind: "route",
          ref: normalizeRouteName(target.ref || ""),
        }},
      }};
    }}

    function syncDigestProfileDraft() {{
      state.digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
    }}

    function collectDigestProfileDraft(form) {{
      const formData = new FormData(form);
      return normalizeDigestProfileDraft({{
        language: formData.get("language"),
        timezone: formData.get("timezone"),
        frequency: formData.get("frequency"),
        default_delivery_target: {{
          kind: "route",
          ref: formData.get("default_delivery_target_ref"),
        }},
      }});
    }}

    function summarizePathTail(value, depth = 2) {{
      const parts = String(value || "").split("/").filter(Boolean);
      if (!parts.length) {{
        return "";
      }}
      return parts.slice(-Math.max(1, depth)).join("/");
    }}

    function getDeliverySubscriptionRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return (Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [])
        .find((row) => String(row.id || "").trim() === normalized) || null;
    }}

    function getSelectedDeliverySubscription() {{
      return getDeliverySubscriptionRecord(state.selectedDeliverySubscriptionId);
    }}

    function syncDeliverySelectionState() {{
      const rows = Array.isArray(state.deliverySubscriptions) ? state.deliverySubscriptions : [];
      if (!rows.some((row) => String(row.id || "").trim() === String(state.selectedDeliverySubscriptionId || "").trim())) {{
        state.selectedDeliverySubscriptionId = rows[0] ? String(rows[0].id || "").trim() : "";
      }}
      const selected = getSelectedDeliverySubscription();
      if (!selected) {{
        return;
      }}
      const subscriptionId = String(selected.id || "").trim();
      const reportProfiles = String(selected.subject_kind || "").trim().toLowerCase() === "report"
        ? state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selected.subject_ref || "").trim())
        : [];
      const currentProfileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
      if (!reportProfiles.some((profile) => String(profile.id || "").trim() === currentProfileId)) {{
        state.deliveryPackageProfileIds[subscriptionId] = reportProfiles[0] ? String(reportProfiles[0].id || "").trim() : "";
      }}
    }}

    function summarizeDeliverySubject(subscription) {{
      if (!subscription || typeof subscription !== "object") {{
        return "";
      }}
      const subjectKind = String(subscription.subject_kind || "").trim().toLowerCase();
      const subjectRef = String(subscription.subject_ref || "").trim();
      if (subjectKind === "report") {{
        return getReportRecord(subjectRef)?.title || subjectRef;
      }}
      if (subjectKind === "story") {{
        return (Array.isArray(state.stories) ? state.stories : [])
          .find((story) => String(story.id || "").trim() === subjectRef)?.title || subjectRef;
      }}
      if (subjectKind === "watch_mission") {{
        return (Array.isArray(state.watches) ? state.watches : [])
          .find((watch) => String(watch.id || "").trim() === subjectRef)?.name || subjectRef;
      }}
      return subjectRef || copy("Default profile", "默认配置");
    }}

    function getDeliveryDispatchRowsForSubscription(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return [];
      }}
      return (Array.isArray(state.deliveryDispatchRecords) ? state.deliveryDispatchRecords : [])
        .filter((row) => String(row.subscription_id || "").trim() === normalized);
    }}

    async function loadDeliveryPackageAudit(identifier, {{ profileId = "", render = true }} = {{}}) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      const query = profileId ? `?profile_id=${{encodeURIComponent(profileId)}}` : "";
      try {{
        const payload = await api(`/api/delivery-subscriptions/${{normalized}}/package${{query}}`);
        state.deliveryPackageAudits[normalized] = payload;
        state.deliveryPackageErrors[normalized] = "";
        state.deliveryPackageProfileIds[normalized] = String(payload.profile_id || profileId || "").trim();
        if (render) {{
          renderDeliveryWorkspace();
        }}
        return payload;
      }} catch (error) {{
        state.deliveryPackageErrors[normalized] = error.message;
        if (render) {{
          renderDeliveryWorkspace();
        }}
        throw error;
      }}
    }}

    async function loadDigestConsole({{ render = true, preserveDraft = true, force = false }} = {{}}) {{
      if (!force && state.digestConsole) {{
        if (!preserveDraft || !state.digestProfileDraft) {{
          state.digestProfileDraft = normalizeDigestProfileDraft(state.digestConsole?.profile?.profile || defaultDigestProfileDraft());
        }}
        if (render) {{
          renderDeliveryWorkspace();
        }}
        return state.digestConsole;
      }}
      const payload = await api("/api/digest/console?profile=default&limit=8");
      state.digestConsole = payload;
      if (!preserveDraft || !state.digestProfileDraft) {{
        state.digestProfileDraft = normalizeDigestProfileDraft(payload?.profile?.profile || defaultDigestProfileDraft());
      }}
      if (render) {{
        renderDeliveryWorkspace();
      }}
      return payload;
    }}

    async function attachClaimToReport(claimId, reportId, sectionId = "", bundleId = "") {{
      const normalizedClaimId = String(claimId || "").trim();
      const normalizedReportId = String(reportId || "").trim();
      const normalizedSectionId = String(sectionId || "").trim();
      const normalizedBundleId = String(bundleId || "").trim();
      if (!normalizedClaimId || !normalizedReportId) {{
        return;
      }}
      const report = getReportRecord(normalizedReportId) || await api(`/api/reports/${{normalizedReportId}}`);
      const nextReportClaimIds = uniqueValues([...(Array.isArray(report?.claim_card_ids) ? report.claim_card_ids : []), normalizedClaimId]);
      const nextReportBundleIds = normalizedBundleId
        ? uniqueValues([...(Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []), normalizedBundleId])
        : (Array.isArray(report?.citation_bundle_ids) ? report.citation_bundle_ids : []);
      await api(`/api/reports/${{normalizedReportId}}`, {{
        method: "PUT",
        payload: {{ claim_card_ids: nextReportClaimIds, citation_bundle_ids: nextReportBundleIds }},
      }});
      if (normalizedSectionId) {{
        const section = getReportSectionsForReport(normalizedReportId).find((entry) => String(entry.id || "").trim() === normalizedSectionId)
          || await api(`/api/report-sections/${{normalizedSectionId}}`);
        const nextSectionClaimIds = uniqueValues([...(Array.isArray(section?.claim_card_ids) ? section.claim_card_ids : []), normalizedClaimId]);
        await api(`/api/report-sections/${{normalizedSectionId}}`, {{
          method: "PUT",
          payload: {{ claim_card_ids: nextSectionClaimIds }},
        }});
      }}
    }}

    async function submitStoryDeck(form) {{
      const draft = collectStoryDraft(form);
      state.storyDraft = draft;
      if (!draft.title.trim()) {{
        setStageFeedback("review", {{
          kind: "blocked",
          title: copy("Story draft still needs a title", "故事草稿仍然缺少标题"),
          copy: copy("Add a story title before this brief can move into the review lane.", "补上故事标题后，这条简报才能进入审阅阶段。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Complete Story Intake", "继续补全故事录入"),
              attrs: {{ "data-empty-focus": "story", "data-empty-field": "title" }},
            }},
            secondary: [
              {{
                label: copy("Open Triage", "打开分诊"),
                attrs: {{ "data-empty-jump": "section-triage" }},
              }},
            ],
          }},
        }});
        showToast(copy("Provide a story title before creating a brief.", "创建故事前请先填写标题。"), "error");
        focusStoryDeck("title");
        return;
      }}
      const submitButton = form?.querySelector("button[type='submit']");
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      try {{
        const created = await api("/api/stories", {{
          method: "POST",
          payload: draft,
        }});
        setStoryDraft(defaultStoryDraft());
        pushActionEntry({{
          kind: copy("story create", "故事创建"),
          label: state.language === "zh" ? `已创建故事：${{created.title}}` : `Created story: ${{created.title}}`,
          detail: copy("The story is now part of the workspace and can be archived or refined in place.", "该故事已进入工作台，后续可以继续编辑或归档。"),
          undoLabel: copy("Delete story", "删除故事"),
          undo: async () => {{
            await api(`/api/stories/${{created.id}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除故事：${{created.title}}` : `Story deleted: ${{created.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        state.selectedStoryId = created.id;
        state.storyDetails[created.id] = created;
        renderStories();
        setStageFeedback("review", {{
          kind: "completion",
          title: state.language === "zh" ? `故事已创建：${{created.title}}` : `Story created: ${{created.title}}`,
          copy: copy(
            "The review lane now has a persisted story object. Refine it in the workspace or inspect delivery readiness next.",
            "审阅阶段现在已经拥有持久化故事对象；下一步可以继续在工作台里完善它，或检查交付就绪度。"
          ),
          actionHierarchy: {{
            primary: {{
              label: copy("Open Story Workspace", "打开故事工作台"),
              attrs: {{ "data-empty-jump": "section-story" }},
            }},
            secondary: [
              {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            ],
          }},
        }});
        showToast(
          state.language === "zh" ? `故事已创建：${{created.title}}` : `Story created: ${{created.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Create story", "创建故事"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }}

    async function setStoryStatusQuick(identifier, nextStatus) {{
      const story = getStoryRecord(identifier);
      if (!story) {{
        throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
      }}
      const targetStatus = String(nextStatus || "").trim().toLowerCase();
      if (!targetStatus || targetStatus === String(story.status || "active").trim().toLowerCase()) {{
        return;
      }}
      const previousStory = {{
        title: story.title || "",
        summary: story.summary || "",
        status: story.status || "active",
      }};
      try {{
        await api(`/api/stories/${{story.id}}`, {{
          method: "PUT",
          payload: {{ status: targetStatus }},
        }});
        pushActionEntry({{
          kind: copy("story state", "故事状态"),
          label: state.language === "zh"
            ? `已将故事切换为 ${{localizeWord(targetStatus)}}：${{story.title}}`
            : `Story moved to ${{targetStatus}}: ${{story.title}}`,
          detail: copy("Use undo to restore the previous workspace state.", "如需回退，可在最近操作里恢复。"),
          undoLabel: copy("Restore story", "恢复故事"),
          undo: async () => {{
            await api(`/api/stories/${{story.id}}`, {{
              method: "PUT",
              payload: previousStory,
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已恢复故事：${{previousStory.title}}` : `Story restored: ${{previousStory.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `故事状态已更新：${{story.title}}`
            : `Story status updated: ${{story.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Update story state", "更新故事状态"));
      }}
    }}

    async function deleteStoryFromWorkspace(identifier) {{
      const story = getStoryRecord(identifier);
      if (!story) {{
        throw new Error(copy("Story not found in the current workspace.", "当前工作区中没有找到该故事。"));
      }}
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除故事 ${{story.title}}？这会把它从当前工作台移除。`
          : `Delete story ${{story.title}} from the workspace?`,
      );
      if (!confirmed) {{
        return;
      }}
      const snapshot = JSON.parse(JSON.stringify(story));
      try {{
        await api(`/api/stories/${{story.id}}`, {{ method: "DELETE" }});
        removeStoryFromState(story.id);
        pushActionEntry({{
          kind: copy("story delete", "故事删除"),
          label: state.language === "zh" ? `已删除故事：${{story.title}}` : `Deleted story: ${{story.title}}`,
          detail: copy("The full story payload is kept in recent actions so you can restore it once.", "完整故事快照会暂存在最近操作中，方便你单次恢复。"),
          undoLabel: copy("Restore story", "恢复故事"),
          undo: async () => {{
            await api("/api/stories", {{
              method: "POST",
              payload: snapshot,
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已恢复故事：${{snapshot.title}}` : `Story restored: ${{snapshot.title}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh" ? `故事已删除：${{story.title}}` : `Story deleted: ${{story.title}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Delete story", "删除故事"));
      }}
    }}

    function isStorySelected(storyId) {{
      return state.selectedStoryIds.includes(storyId);
    }}

    function toggleStorySelection(storyId, checked = null) {{
      if (!storyId) {{
        return;
      }}
      const next = new Set(state.selectedStoryIds);
      const shouldSelect = checked === null ? !next.has(storyId) : Boolean(checked);
      if (shouldSelect) {{
        next.add(storyId);
        state.selectedStoryId = storyId;
      }} else {{
        next.delete(storyId);
      }}
      state.selectedStoryIds = Array.from(next);
    }}

    function selectVisibleStories(filteredStories) {{
      const visibleIds = (Array.isArray(filteredStories) ? filteredStories : []).map((story) => story.id);
      state.selectedStoryIds = visibleIds;
      if (visibleIds.length && !visibleIds.includes(state.selectedStoryId)) {{
        state.selectedStoryId = visibleIds[0];
      }}
    }}

    function clearStorySelection() {{
      state.selectedStoryIds = [];
    }}

    async function runStoryBatchStatusUpdate(storyIds, nextStatus) {{
      const normalizedIds = uniqueValues(storyIds).filter((storyId) => state.stories.some((story) => story.id === storyId));
      if (!normalizedIds.length || !nextStatus || state.storyBulkBusy) {{
        return;
      }}
      state.storyBulkBusy = true;
      const previousStates = {{}};
      normalizedIds.forEach((storyId) => {{
        const currentStory = getStoryRecord(storyId);
        previousStates[storyId] = currentStory ? String(currentStory.status || "active") : "active";
        if (currentStory && state.storyDetails[storyId]) {{
          state.storyDetails[storyId] = {{
            ...state.storyDetails[storyId],
            status: nextStatus,
          }};
        }}
      }});
      renderStories();
      try {{
        for (const storyId of normalizedIds) {{
          await api(`/api/stories/${{storyId}}`, {{
            method: "PUT",
            payload: {{ status: nextStatus }},
          }});
        }}
        state.selectedStoryIds = [];
        pushActionEntry({{
          kind: copy("story batch", "故事批处理"),
          label: state.language === "zh"
            ? `已批量将 ${{normalizedIds.length}} 条故事切换为 ${{localizeWord(nextStatus)}}`
            : `Moved ${{normalizedIds.length}} stories to ${{nextStatus}}`,
          detail: state.language === "zh"
            ? `涉及故事：${{normalizedIds.join(", ")}}`
            : `Stories: ${{normalizedIds.join(", ")}}`,
          undoLabel: copy("Restore stories", "恢复故事"),
          undo: async () => {{
            for (const storyId of normalizedIds) {{
              await api(`/api/stories/${{storyId}}`, {{
                method: "PUT",
                payload: {{ status: previousStates[storyId] || "active" }},
              }});
            }}
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复 ${{normalizedIds.length}} 条故事`
                : `Restored ${{normalizedIds.length}} stories`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已批量更新 ${{normalizedIds.length}} 条故事`
            : `Updated ${{normalizedIds.length}} stories`,
          "success",
        );
      }} catch (error) {{
        normalizedIds.forEach((storyId) => {{
          if (state.storyDetails[storyId]) {{
            state.storyDetails[storyId] = {{
              ...state.storyDetails[storyId],
              status: previousStates[storyId] || "active",
            }};
          }}
        }});
        renderStories();
        throw error;
      }} finally {{
        state.storyBulkBusy = false;
        renderStories();
      }}
    }}

    function safeLocalStorageGet(key) {{
      try {{
        return window.localStorage.getItem(key);
      }} catch (error) {{
        return null;
      }}
    }}

    function safeLocalStorageSet(key, value) {{
      try {{
        window.localStorage.setItem(key, value);
      }} catch (error) {{
        console.warn("localStorage write skipped", error);
      }}
    }}

    function safeLocalStorageRemove(key) {{
      try {{
        window.localStorage.removeItem(key);
      }} catch (error) {{
        console.warn("localStorage remove skipped", error);
      }}
    }}

    function loadCreateWatchDraft() {{
      const raw = safeLocalStorageGet(createWatchStorageKey);
      if (!raw) {{
        return defaultCreateWatchDraft();
      }}
      try {{
        return normalizeCreateWatchDraft(JSON.parse(raw));
      }} catch (error) {{
        safeLocalStorageRemove(createWatchStorageKey);
        return defaultCreateWatchDraft();
      }}
    }}

    function persistCreateWatchDraft() {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      const hasSignal = createWatchFormFields.some((field) => String(draft[field] || "").trim());
      if (!hasSignal) {{
        safeLocalStorageRemove(createWatchStorageKey);
        return;
      }}
      safeLocalStorageSet(createWatchStorageKey, JSON.stringify(draft));
    }}

    function persistStoryWorkspacePrefs() {{
      safeLocalStorageSet(storyFilterStorageKey, normalizeStoryFilter(state.storyFilter));
      safeLocalStorageSet(storySortStorageKey, normalizeStorySort(state.storySort));
      safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
    }}

    function loadCommandPaletteQuery() {{
      return String(safeLocalStorageGet(commandPaletteQueryStorageKey) || "").trim();
    }}

    function persistCommandPaletteQuery() {{
      const query = String(state.commandPalette.query || "").trim();
      if (!query) {{
        safeLocalStorageRemove(commandPaletteQueryStorageKey);
        return;
      }}
      safeLocalStorageSet(commandPaletteQueryStorageKey, query);
    }}

    function loadCommandPaletteRecent() {{
      const raw = safeLocalStorageGet(commandPaletteRecentStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        return uniqueValues(JSON.parse(raw)).slice(0, 8);
      }} catch (error) {{
        safeLocalStorageRemove(commandPaletteRecentStorageKey);
        return [];
      }}
    }}

    function persistCommandPaletteRecent() {{
      const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
      if (!recentIds.length) {{
        safeLocalStorageRemove(commandPaletteRecentStorageKey);
        return;
      }}
      safeLocalStorageSet(commandPaletteRecentStorageKey, JSON.stringify(recentIds));
    }}

    function noteCommandPaletteRecent(entryId) {{
      const normalized = String(entryId || "").trim();
      if (!normalized) {{
        return;
      }}
      state.commandPalette.recentIds = [normalized, ...uniqueValues(state.commandPalette.recentIds || []).filter((id) => id !== normalized)].slice(0, 8);
      persistCommandPaletteRecent();
    }}

    function normalizeContextLinkHistoryEntry(entry) {{
      const url = String(entry?.url || "").trim();
      if (!url) {{
        return null;
      }}
      const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
      const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
      const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
      return {{ url, summary, sectionId, timestamp }};
    }}

    function loadContextLinkHistory() {{
      const raw = safeLocalStorageGet(contextLinkHistoryStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        const parsed = JSON.parse(raw);
        return (Array.isArray(parsed) ? parsed : [])
          .map((entry) => normalizeContextLinkHistoryEntry(entry))
          .filter(Boolean)
          .slice(0, 6);
      }} catch (error) {{
        safeLocalStorageRemove(contextLinkHistoryStorageKey);
        return [];
      }}
    }}

    function persistContextLinkHistory() {{
      const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
        .map((entry) => normalizeContextLinkHistoryEntry(entry))
        .filter(Boolean)
        .slice(0, 6);
      if (!entries.length) {{
        safeLocalStorageRemove(contextLinkHistoryStorageKey);
        return;
      }}
      safeLocalStorageSet(contextLinkHistoryStorageKey, JSON.stringify(entries));
    }}

    function noteContextLinkHistory(entry) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      state.contextLinkHistory = [
        normalized,
        ...(Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
          .map((candidate) => normalizeContextLinkHistoryEntry(candidate))
          .filter((candidate) => candidate && candidate.url !== normalized.url),
      ].slice(0, 6);
      persistContextLinkHistory();
      renderCommandPalette();
    }}

    function clearContextLinkHistory({{ toast = true }} = {{}}) {{
      state.contextLinkHistory = [];
      persistContextLinkHistory();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Shared context history cleared", "已清空分享上下文历史"), "success");
      }}
    }}

    function normalizeContextSavedViewEntry(entry) {{
      const url = String(entry?.url || "").trim();
      const rawName = String(entry?.name || "").trim();
      if (!(url && rawName)) {{
        return null;
      }}
      const name = clampLabel(rawName, 72);
      const summary = clampLabel(String(entry?.summary || "").trim(), 96) || url;
      const sectionId = normalizeSectionId(entry?.sectionId || "section-intake");
      const timestamp = String(entry?.timestamp || "").trim() || new Date().toISOString();
      const pinned = Boolean(entry?.pinned);
      const isDefault = Boolean(entry?.isDefault);
      return {{ name, url, summary, sectionId, timestamp, pinned, isDefault }};
    }}

    function loadContextSavedViews() {{
      const raw = safeLocalStorageGet(contextSavedViewsStorageKey);
      if (!raw) {{
        return [];
      }}
      try {{
        const parsed = JSON.parse(raw);
        return (Array.isArray(parsed) ? parsed : [])
          .map((entry) => normalizeContextSavedViewEntry(entry))
          .filter(Boolean)
          .slice(0, 8);
      }} catch (error) {{
        safeLocalStorageRemove(contextSavedViewsStorageKey);
        return [];
      }}
    }}

    function persistContextSavedViews() {{
      const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter(Boolean)
        .slice(0, 8);
      if (!entries.length) {{
        safeLocalStorageRemove(contextSavedViewsStorageKey);
        return;
      }}
      safeLocalStorageSet(contextSavedViewsStorageKey, JSON.stringify(entries));
    }}

    function upsertContextSavedView(entry) {{
      const normalized = normalizeContextSavedViewEntry(entry);
      if (!normalized) {{
        return false;
      }}
      const hasPinnedOverride = Object.prototype.hasOwnProperty.call(entry || {{}}, "pinned");
      const hasDefaultOverride = Object.prototype.hasOwnProperty.call(entry || {{}}, "isDefault");
      const existing = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((candidate) => normalizeContextSavedViewEntry(candidate))
        .filter(Boolean);
      const existingIndex = existing.findIndex((candidate) => candidate.name.toLowerCase() === normalized.name.toLowerCase());
      const existingPinned = existingIndex >= 0 ? Boolean(existing[existingIndex]?.pinned) : false;
      const existingDefault = existingIndex >= 0 ? Boolean(existing[existingIndex]?.isDefault) : false;
      const resolvedEntry = {{
        ...normalized,
        pinned: hasPinnedOverride ? Boolean(entry.pinned) : existingPinned,
        isDefault: hasDefaultOverride ? Boolean(entry.isDefault) : existingDefault,
      }};
      const next = existingIndex >= 0
        ? existing.map((candidate, index) => (index === existingIndex ? resolvedEntry : candidate))
        : [resolvedEntry, ...existing].slice(0, 8);
      state.contextSavedViews = next;
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      return existingIndex >= 0;
    }}

    function findContextSavedViewIndexByName(viewName) {{
      const normalizedName = String(viewName || "").trim().toLowerCase();
      if (!normalizedName) {{
        return -1;
      }}
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
    }}

    function findContextSavedViewIndexByUrl(viewUrl) {{
      const normalizedUrl = String(viewUrl || "").trim();
      if (!normalizedUrl) {{
        return -1;
      }}
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.url === normalizedUrl);
    }}

    function buildUniqueContextSavedViewName(baseName) {{
      const trimmedBase = clampLabel(String(baseName || "").trim(), 72) || copy("Saved View", "保存视图");
      const normalizedExisting = new Set(
        (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
          .map((entry) => normalizeContextSavedViewEntry(entry))
          .filter(Boolean)
          .map((entry) => entry.name.toLowerCase())
      );
      if (!normalizedExisting.has(trimmedBase.toLowerCase())) {{
        return trimmedBase;
      }}
      let counter = 2;
      while (counter < 100) {{
        const candidate = clampLabel(`${{trimmedBase}} ${{counter}}`, 72);
        if (!normalizedExisting.has(candidate.toLowerCase())) {{
          return candidate;
        }}
        counter += 1;
      }}
      return clampLabel(`${{trimmedBase}} copy`, 72);
    }}

    function saveCurrentContextView(rawName = "") {{
      const base = buildCurrentContextLinkRecord();
      if (!base) {{
        return;
      }}
      const preferredName = String(rawName || "").trim() || base.summary;
      const wasOverwrite = upsertContextSavedView({{
        name: preferredName,
        ...base,
        timestamp: new Date().toISOString(),
      }});
      const input = $("context-save-name");
      if (input) {{
        input.value = "";
      }}
      showToast(
        wasOverwrite
          ? copy("Saved view updated", "已更新保存视图")
          : copy("Saved view added", "已保存当前视图"),
        "success",
      );
    }}

    function saveAndPinCurrentContextView() {{
      const current = buildCurrentContextLinkRecord();
      if (!current) {{
        return;
      }}
      const existingIndex = findContextSavedViewIndexByUrl(current.url);
      if (existingIndex >= 0) {{
        const existing = normalizeContextSavedViewEntry(state.contextSavedViews[existingIndex]);
        if (existing?.pinned) {{
          showToast(copy("Current view is already pinned", "当前视图已固定到坞站"), "success");
          return;
        }}
        if (countPinnedContextSavedViews() >= 4) {{
          showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
          return;
        }}
        upsertContextSavedView({{
          ...existing,
          ...current,
          name: existing.name,
          pinned: true,
          isDefault: existing.isDefault,
          timestamp: new Date().toISOString(),
        }});
        showToast(copy("Current view saved to the top dock", "已将当前视图固定到顶部坞站"), "success");
        return;
      }}
      if (countPinnedContextSavedViews() >= 4) {{
        showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
        return;
      }}
      upsertContextSavedView({{
        name: buildUniqueContextSavedViewName(current.summary),
        ...current,
        pinned: true,
        timestamp: new Date().toISOString(),
      }});
      showToast(copy("Current view saved and pinned", "已保存并固定当前视图"), "success");
    }}

    function startContextDockRename(viewName) {{
      const index = findContextSavedViewIndexByName(viewName);
      if (index < 0) {{
        return;
      }}
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry || !entry.pinned) {{
        return;
      }}
      state.contextDockEditingName = entry.name;
      renderTopbarContext();
      window.setTimeout(() => {{
        const input = $("context-dock-rename-input");
        input?.focus();
        input?.select();
      }}, 10);
    }}

    function cancelContextDockRename() {{
      if (!String(state.contextDockEditingName || "").trim()) {{
        return;
      }}
      state.contextDockEditingName = "";
      renderTopbarContext();
    }}

    function renameContextSavedView(viewName, rawNextName) {{
      const index = findContextSavedViewIndexByName(viewName);
      if (index < 0) {{
        return;
      }}
      const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!current) {{
        return;
      }}
      const nextName = clampLabel(String(rawNextName || "").trim(), 72);
      if (!nextName) {{
        showToast(copy("Provide a name before saving the view label.", "保存视图标签前请先填写名称。"), "error");
        return;
      }}
      const duplicateIndex = findContextSavedViewIndexByName(nextName);
      if (duplicateIndex >= 0 && duplicateIndex !== index) {{
        showToast(copy("A saved view with that name already exists.", "已有同名保存视图。"), "error");
        return;
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        if (candidateIndex !== index) {{
          return normalized;
        }}
        return {{
          ...normalized,
          name: nextName,
          timestamp: new Date().toISOString(),
        }};
      }});
      state.contextDockEditingName = "";
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        state.language === "zh" ? `已重命名视图：${{nextName}}` : `Saved view renamed: ${{nextName}}`,
        "success",
      );
    }}

    function deleteContextSavedView(entryIndex, {{ toast = true }} = {{}}) {{
      const index = Number(entryIndex);
      const current = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!current) {{
        return;
      }}
      if (String(state.contextDockEditingName || "").trim().toLowerCase() === String(current.name || "").trim().toLowerCase()) {{
        state.contextDockEditingName = "";
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .filter((_, candidateIndex) => candidateIndex !== index);
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(
          state.language === "zh" ? `已删除保存视图：${{current.name}}` : `Saved view removed: ${{current.name}}`,
          "success",
        );
      }}
    }}

    function clearContextSavedViews({{ toast = true }} = {{}}) {{
      state.contextSavedViews = [];
      state.contextDockEditingName = "";
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Saved views cleared", "已清空保存视图"), "success");
      }}
    }}

    function getDefaultContextSavedView() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .find((entry) => entry && entry.isDefault) || null;
    }}

    function clearDefaultContextSavedView({{ toast = true }} = {{}}) {{
      const currentDefault = getDefaultContextSavedView();
      if (!currentDefault) {{
        return;
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        return normalized ? {{ ...normalized, isDefault: false }} : candidate;
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      if (toast) {{
        showToast(copy("Default landing view cleared", "已清除默认落地视图"), "success");
      }}
    }}

    function setDefaultContextSavedView(entryIndex) {{
      const index = Number(entryIndex);
      const target = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!target) {{
        return;
      }}
      const shouldUnset = Boolean(target.isDefault);
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        return {{
          ...normalized,
          isDefault: shouldUnset ? false : candidateIndex === index,
        }};
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        shouldUnset
          ? copy("Default landing view cleared", "已清除默认落地视图")
          : copy("Default landing view updated", "已更新默认落地视图"),
        "success",
      );
    }}

    function hasExplicitWorkspaceUrlContext() {{
      return Boolean(
        readWatchUrlState().hasWatchContext ||
        readTriageUrlState().hasTriageContext ||
        readStoryUrlState().hasStoryContext ||
        String(window.location.hash || "").trim()
      );
    }}

    function countPinnedContextSavedViews() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter((entry) => entry && entry.pinned)
        .length;
    }}

    function getPinnedContextSavedViewIndexes() {{
      return (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry, index) => {{
          const normalized = normalizeContextSavedViewEntry(entry);
          return normalized && normalized.pinned ? index : -1;
        }})
        .filter((index) => index >= 0);
    }}

    function toggleContextSavedViewPinned(entryIndex) {{
      const index = Number(entryIndex);
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry) {{
        return;
      }}
      if (!entry.pinned && countPinnedContextSavedViews() >= 4) {{
        showToast(copy("Pin up to four saved views in the top dock.", "顶部坞站最多固定四个保存视图。"), "error");
        return;
      }}
      if (entry.pinned && String(state.contextDockEditingName || "").trim().toLowerCase() === String(entry.name || "").trim().toLowerCase()) {{
        state.contextDockEditingName = "";
      }}
      state.contextSavedViews = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : []).map((candidate, candidateIndex) => {{
        const normalized = normalizeContextSavedViewEntry(candidate);
        if (!normalized) {{
          return candidate;
        }}
        if (candidateIndex !== index) {{
          return normalized;
        }}
        return {{
          ...normalized,
          pinned: !normalized.pinned,
          timestamp: new Date().toISOString(),
        }};
      }});
      persistContextSavedViews();
      renderCommandPalette();
      renderTopbarContext();
      showToast(
        entry.pinned
          ? copy("Saved view removed from the top dock", "已从顶部坞站取消固定")
          : copy("Saved view pinned to the top dock", "已固定到顶部坞站"),
        "success",
      );
    }}

    function moveContextSavedViewInDock(entryIndex, direction = "left") {{
      const index = Number(entryIndex);
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[index]);
      if (!entry || !entry.pinned) {{
        return;
      }}
      const pinnedIndexes = getPinnedContextSavedViewIndexes();
      const currentPosition = pinnedIndexes.indexOf(index);
      if (currentPosition < 0) {{
        return;
      }}
      const offset = direction === "right" ? 1 : -1;
      const nextPosition = currentPosition + offset;
      if (nextPosition < 0 || nextPosition >= pinnedIndexes.length) {{
        return;
      }}
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
    }}

    function resetWorkspaceContext({{ jump = true, toast = true }} = {{}}) {{
      setContextLensOpen(false);
      state.watchSearch = "";
      state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
      state.watchResultFilters = {{}};
      setContextRouteName("", "");

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
      if (jump) {{
        jumpToSection("section-intake");
      }}
      if (toast) {{
        showToast(copy("Workspace context reset", "当前工作上下文已重置"), "success");
      }}
    }}

    function applyStoryViewPreset(viewKey, {{ jump = false, toast = false }} = {{}}) {{
      const preset = getStoryViewPreset(viewKey);
      if (!preset) {{
        return;
      }}
      state.storySearch = "";
      state.storyFilter = preset.filter;
      state.storySort = preset.sort;
      persistStoryWorkspacePrefs();
      renderStories();
      if (jump) {{
        jumpToSection("section-story");
      }}
      if (toast) {{
        showToast(
          state.language === "zh"
            ? `故事视图已切换：${{storyViewPresetLabel(preset.key)}}`
            : `Story view switched: ${{storyViewPresetLabel(preset.key)}}`,
          "success",
        );
      }}
    }}

    function renderStoryViewJumpStrip() {{
      const root = $("story-view-jumps");
      if (!root) {{
        return;
      }}
      const activeStoryView = detectStoryViewPreset({{
        filter: state.storyFilter,
        sort: state.storySort,
        search: state.storySearch,
      }});
      root.innerHTML = `
        ${{storyViewPresetOptions.map((option) => `
          <button class="chip-btn ${{activeStoryView === option ? "active" : ""}}" type="button" data-story-view-shortcut="${{escapeHtml(option)}}">
            ${{escapeHtml(storyViewPresetLabel(option))}}
          </button>
        `).join("")}}
        ${{activeStoryView === "custom" ? `<span class="chip hot">${{storyViewPresetLabel("custom")}}</span>` : ""}}
      `;
      root.querySelectorAll("[data-story-view-shortcut]").forEach((button) => {{
        button.addEventListener("click", () => {{
          applyStoryViewPreset(String(button.dataset.storyViewShortcut || "").trim(), {{ jump: true }});
        }});
      }});
    }}

    function readWatchUrlState() {{
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const search = String(params.get(watchUrlSearchParam) || "").trim();
      const watchId = String(params.get(watchUrlIdParam) || "").trim();
      const hasWatchContext = Boolean(search || watchId || url.hash === "#section-board" || url.hash === "#section-cockpit");
      return {{ hasWatchContext, search, watchId }};
    }}

    function applyWatchUrlStateFromLocation() {{
      const urlState = readWatchUrlState();
      if (!urlState.hasWatchContext) {{
        return;
      }}
      state.watchSearch = urlState.search;
      if (urlState.watchId) {{
        state.selectedWatchId = urlState.watchId;
      }}
      state.watchUrlFocusPending = true;
    }}

    function syncWatchUrlState({{ defaultWatchId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const search = String(state.watchSearch || "").trim();
      const watchId = String(state.selectedWatchId || "").trim();

      if (search) {{
        params.set(watchUrlSearchParam, search);
      }} else {{
        params.delete(watchUrlSearchParam);
      }}

      if (watchId) {{
        params.set(watchUrlIdParam, watchId);
      }} else {{
        params.delete(watchUrlIdParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushWatchUrlFocus() {{
      if (!state.watchUrlFocusPending) {{
        return;
      }}
      state.watchUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection(window.location.hash === "#section-board" ? "section-board" : "section-cockpit", {{ updateHash: false }});
      }}, 0);
    }}

    function readTriageUrlState() {{
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = String(params.get(triageUrlFilterParam) || "").trim().toLowerCase();
      const search = String(params.get(triageUrlSearchParam) || "").trim();
      const itemId = String(params.get(triageUrlIdParam) || "").trim();
      const hasTriageContext = Boolean(filter || search || itemId || url.hash === "#section-triage");
      return {{
        hasTriageContext,
        filter: normalizeTriageFilter(filter || state.triageFilter),
        search,
        itemId,
      }};
    }}

    function applyTriageUrlStateFromLocation() {{
      const urlState = readTriageUrlState();
      if (!urlState.hasTriageContext) {{
        return;
      }}
      state.triageFilter = urlState.filter;
      state.triageSearch = urlState.search;
      if (urlState.itemId) {{
        state.selectedTriageId = urlState.itemId;
      }}
      state.triageUrlFocusPending = true;
    }}

    function syncTriageUrlState({{ defaultItemId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = normalizeTriageFilter(state.triageFilter);
      const search = String(state.triageSearch || "").trim();
      const itemId = String(state.selectedTriageId || "").trim();

      if (filter !== "open") {{
        params.set(triageUrlFilterParam, filter);
      }} else {{
        params.delete(triageUrlFilterParam);
      }}

      if (search) {{
        params.set(triageUrlSearchParam, search);
      }} else {{
        params.delete(triageUrlSearchParam);
      }}

      if (itemId) {{
        params.set(triageUrlIdParam, itemId);
      }} else {{
        params.delete(triageUrlIdParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushTriageUrlFocus() {{
      if (!state.triageUrlFocusPending) {{
        return;
      }}
      state.triageUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection("section-triage", {{ updateHash: false }});
      }}, 0);
    }}

    function applyStoryWorkspaceMode(mode, {{ persist = true, syncUrl = false, defaultStoryId = "" }} = {{}}) {{
      state.storyWorkspaceMode = normalizeStoryWorkspaceMode(mode);
      if (document.body) {{
        document.body.dataset.storyWorkspaceMode = state.storyWorkspaceMode;
      }}
      const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
      if (storyWorkspaceModeSwitch) {{
        storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {{
          const buttonMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode);
          const isActive = buttonMode === state.storyWorkspaceMode;
          button.classList.toggle("active", isActive);
          button.setAttribute("aria-pressed", isActive ? "true" : "false");
        }});
      }}
      if (persist) {{
        safeLocalStorageSet(storyWorkspaceModeStorageKey, normalizeStoryWorkspaceMode(state.storyWorkspaceMode));
      }}
      if (syncUrl) {{
        syncStoryUrlState({{ defaultStoryId }});
      }}
    }}

    function readStoryUrlState() {{
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
      return {{
        hasStoryContext,
        filter: resolvedFilter,
        sort: resolvedSort,
        search,
        storyId,
        storyWorkspaceMode: resolvedStoryWorkspaceMode,
      }};
    }}

    function applyStoryUrlStateFromLocation() {{
      const urlState = readStoryUrlState();
      if (!urlState.hasStoryContext) {{
        return;
      }}
      state.storyFilter = urlState.filter;
      state.storySort = urlState.sort;
      state.storySearch = urlState.search;
      state.storyWorkspaceMode = urlState.storyWorkspaceMode;
      if (urlState.storyId) {{
        state.selectedStoryId = urlState.storyId;
      }}
      state.storyUrlFocusPending = true;
    }}

    function syncStoryUrlState({{ defaultStoryId = "" }} = {{}}) {{
      if (state.loading.board) {{
        return;
      }}
      const url = new URL(window.location.href);
      const params = url.searchParams;
      const filter = normalizeStoryFilter(state.storyFilter);
      const sort = normalizeStorySort(state.storySort);
      const search = String(state.storySearch || "").trim();
      const storyId = String(state.selectedStoryId || "").trim();
      const activeView = detectStoryViewPreset({{ filter, sort, search }});

      if (!search && activeView !== "custom" && activeView !== "desk") {{
        params.set(storyUrlViewParam, activeView);
      }} else {{
        params.delete(storyUrlViewParam);
      }}

      if (activeView === "custom") {{
        if (filter !== "all") {{
          params.set(storyUrlFilterParam, filter);
        }} else {{
          params.delete(storyUrlFilterParam);
        }}
        if (sort !== "attention") {{
          params.set(storyUrlSortParam, sort);
        }} else {{
          params.delete(storyUrlSortParam);
        }}
      }} else {{
        params.delete(storyUrlFilterParam);
        params.delete(storyUrlSortParam);
      }}

      if (search) {{
        params.set(storyUrlSearchParam, search);
      }} else {{
        params.delete(storyUrlSearchParam);
      }}

      if (storyId) {{
        params.set(storyUrlIdParam, storyId);
      }} else {{
        params.delete(storyUrlIdParam);
      }}
      if (state.storyWorkspaceMode === "editor") {{
        params.set(storyUrlModeParam, state.storyWorkspaceMode);
      }} else {{
        params.delete(storyUrlModeParam);
      }}

      const nextSearch = params.toString();
      const nextUrl = `${{url.pathname}}${{nextSearch ? `?${{nextSearch}}` : ""}}${{url.hash || ""}}`;
      const currentUrl = `${{window.location.pathname}}${{window.location.search}}${{window.location.hash}}`;
      if (nextUrl !== currentUrl) {{
        window.history.replaceState(window.history.state, "", nextUrl);
      }}
    }}

    function flushStoryUrlFocus() {{
      if (!state.storyUrlFocusPending) {{
        return;
      }}
      state.storyUrlFocusPending = false;
      window.setTimeout(() => {{
        jumpToSection("section-story", {{ updateHash: false }});
      }}, 0);
    }}

    applyWatchUrlStateFromLocation();
    applyTriageUrlStateFromLocation();
    state.storyWorkspaceMode = normalizeStoryWorkspaceMode(safeLocalStorageGet(storyWorkspaceModeStorageKey) || state.storyWorkspaceMode);
    state.storyFilter = normalizeStoryFilter(safeLocalStorageGet(storyFilterStorageKey) || state.storyFilter);
    state.storySort = normalizeStorySort(safeLocalStorageGet(storySortStorageKey) || state.storySort);
    applyStoryUrlStateFromLocation();
    applyStoryWorkspaceMode(state.storyWorkspaceMode, {{ persist: false }});
    state.commandPalette.query = loadCommandPaletteQuery();
    state.commandPalette.recentIds = loadCommandPaletteRecent();
    state.contextLinkHistory = loadContextLinkHistory();
    state.contextSavedViews = loadContextSavedViews();
    state.contextDefaultBootPending = !hasExplicitWorkspaceUrlContext();

    function detectInitialLanguage() {{
      const stored = String(safeLocalStorageGet(languageStorageKey) || "").trim().toLowerCase();
      if (stored === "zh" || stored === "en") {{
        return stored;
      }}
      const browserLanguage = String(window.navigator.language || "").trim().toLowerCase();
      return browserLanguage.startsWith("zh") ? "zh" : "en";
    }}

    function normalizeSectionId(value) {{
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
    }}

    state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);

    function setText(id, value) {{
      const node = $(id);
      if (node) {{
        node.textContent = value;
        if (node instanceof HTMLElement && node.hasAttribute("data-fit-text")) {{
          delete node.dataset.fitTextOriginal;
          delete node.dataset.fitApplied;
        }}
      }}
    }}

    function setHTML(id, value) {{
      const node = $(id);
      if (node) {{
        node.innerHTML = value;
      }}
    }}

    function setPlaceholder(id, value) {{
      const node = $(id);
      if (node) {{
        node.placeholder = value;
      }}
    }}

    function activeSectionLabel(sectionId) {{
      const labels = {{
        "section-intake": copy("Mission Intake", "任务录入"),
        "section-board": copy("Mission Board", "任务列表"),
        "section-cockpit": copy("Cockpit", "任务详情"),
        "section-triage": copy("Triage", "分诊"),
        "section-story": copy("Stories", "故事"),
        "section-claims": copy("Claim Composer", "主张装配"),
        "section-report-studio": copy("Report Studio", "报告工作台"),
        "section-ops": copy("Ops Snapshot", "运行状态"),
      }};
      return labels[normalizeSectionId(sectionId)] || labels["section-intake"];
    }}

    function normalizeWorkspaceMode(value) {{
      const normalized = String(value || "").trim().toLowerCase();
      return Object.prototype.hasOwnProperty.call(workspaceModeSectionMap, normalized) ? normalized : "intake";
    }}

    function workspaceModeForSection(sectionId) {{
      const normalizedSection = normalizeSectionId(sectionId);
      if (workspaceModeSectionMap.missions.includes(normalizedSection)) {{
        return "missions";
      }}
      if (workspaceModeSectionMap.review.includes(normalizedSection)) {{
        return "review";
      }}
      if (workspaceModeSectionMap.delivery.includes(normalizedSection)) {{
        return "delivery";
      }}
      return "intake";
    }}

    function workspaceModeDescriptor(modeId) {{
      const normalized = normalizeWorkspaceMode(modeId);
      const descriptors = {{
        intake: {{
          id: "intake",
          label: copy("Start", "开始"),
          kicker: copy("Start", "开始"),
          summary: copy(
            "Keep mission intake as the clean starting surface so the first decision stays focused on what to monitor next.",
            "把任务录入单独作为起始界面，确保进入控制台后的第一个判断仍然只是下一步要监测什么。"
          ),
          modules: [
            {{
              sectionId: "section-intake",
              title: copy("Mission Intake", "任务录入"),
              summary: copy(
                "Start from one mission draft and keep the first move narrow: define the watch, then hand it into monitoring.",
                "从一个任务草稿开始，把第一步收窄成定义监测对象，然后再交给监测阶段。"
              ),
              output: copy("Readiness state and current checklist", "就绪状态和当前清单"),
              nextAction: copy("Create one mission", "创建一个任务"),
              cta: copy("Open Start Surface", "打开开始视图"),
            }},
          ],
          advancedActions: [],
          landingSection: "section-intake",
          footnote: copy("Keep this stage narrow: readiness first, downstream detail later.", "这个阶段只保留最小必要范围：先确认就绪，再进入下游细节。"),
          topbarSubtitle: copy("Workflow stages | Start -> Monitor -> Review -> Deliver", "工作流阶段 | 开始 -> 监测 -> 审阅 -> 交付"),
        }},
        missions: {{
          id: "missions",
          label: copy("Monitor", "监测"),
          kicker: copy("Monitor", "监测"),
          summary: copy(
            "Keep mission selection and cockpit inspection in one monitoring lane so run posture, recent evidence, and handoff facts stay together.",
            "把任务选择和任务详情收进同一条监测工作线，让执行姿态、近期证据和交接事实保持连贯。"
          ),
          modules: [
            {{
              sectionId: "section-board",
              title: copy("Mission Board", "任务列表"),
              summary: copy(
                "Choose the current mission, confirm readiness, and keep due or degraded watches visible without diving into every detail at once.",
                "先选定当前任务，确认就绪度，并把待执行或降级任务保持可见，而不是一开始就展开全部细节。"
              ),
              output: copy("Mission posture, due state, and latest lane status", "任务姿态、待执行状态和最近工作线状态"),
              nextAction: copy("Select one mission", "选中一个任务"),
              cta: copy("Open Mission Board", "打开任务列表"),
            }},
            {{
              sectionId: "section-cockpit",
              title: copy("Mission Cockpit", "任务详情"),
              summary: copy(
                "Inspect one mission's run history, results, and route handoff facts once it becomes the current work object.",
                "当某个任务成为当前工作对象后，在这里查看它的执行历史、结果和路由交接事实。"
              ),
              output: copy("Latest run outcome and stored results", "最新运行结果和已存储结果"),
              nextAction: copy("Inspect the selected mission", "查看当前任务详情"),
              cta: copy("Open Cockpit", "打开任务详情"),
            }},
          ],
          advancedActions: [],
          landingSection: "section-board",
          footnote: copy("Stay on the current mission until the run outcome and next handoff are obvious.", "围绕当前任务工作，直到运行结果和下一步交接都清晰为止。"),
          topbarSubtitle: copy("Monitor | Mission Board -> Cockpit", "监测 | 任务列表 -> 任务详情"),
        }},
        review: {{
          id: "review",
          label: copy("Review", "审阅"),
          kicker: copy("Review", "审阅"),
          summary: copy(
            "Keep triage and story work first-rank so evidence review can progress before claim composition and report assembly are needed.",
            "把分诊和故事工作保持在第一层级，让证据审阅先完成，再按需进入主张装配和报告编排。"
          ),
          modules: [
            {{
              sectionId: "section-triage",
              title: copy("Triage Queue", "分诊队列"),
              summary: copy(
                "Review the inbox and keep the selected evidence workbench visible before promoting anything downstream.",
                "先处理收件队列，并让选中的证据工作台保持可见，再决定是否向下游提升。"
              ),
              output: copy("Queue state and selected evidence", "队列状态和当前证据"),
              nextAction: copy("Verify or promote evidence", "核验或提升证据"),
              cta: copy("Open Triage", "打开分诊"),
            }},
            {{
              sectionId: "section-story",
              title: copy("Story Workspace", "故事工作台"),
              summary: copy(
                "Keep the promoted story, contradictions, and delivery readiness in one place before editorial packaging begins.",
                "在进入编辑包装前，把已提升故事、冲突点和交付就绪度收进同一个工作台。"
              ),
              output: copy("Promoted story candidate and readiness state", "已提升故事候选和就绪状态"),
              nextAction: copy("Refine the current story", "完善当前故事"),
              cta: copy("Open Story Workspace", "打开故事工作台"),
            }},
          ],
          advancedActions: [
            {{
              sectionId: "section-claims",
              label: copy("Open Claim Composer", "打开主张装配"),
            }},
            {{
              sectionId: "section-report-studio",
              label: copy("Open Report Studio", "打开报告工作台"),
            }},
          ],
          landingSection: "section-triage",
          footnote: copy("Claims and reports remain available, but they should not compete with the current evidence object by default.", "主张和报告仍然可用，但默认不再与当前证据对象争夺第一层级注意力。"),
          topbarSubtitle: copy("Review | Triage -> Stories -> Advanced Review", "审阅 | 分诊 -> 故事 -> 高级审阅"),
        }},
        delivery: {{
          id: "delivery",
          label: copy("Deliver", "交付"),
          kicker: copy("Deliver", "交付"),
          summary: copy(
            "Keep route posture, dispatch state, and delivery history first-rank so downstream status stays visible without exposing every diagnostic surface by default.",
            "把路由姿态、分发状态和交付历史保留在第一层级，让下游状态保持可见，而不是默认把所有诊断面板都展开。"
          ),
          modules: [
            {{
              sectionId: "section-ops",
              title: copy("Delivery Lane", "交付工作线"),
              summary: copy(
                "Watch route posture, recent alert flow, and dispatch history in one owned delivery surface before opening diagnostics.",
                "先在一个交付面板里查看路由姿态、近期告警流和分发历史，再按需打开诊断视图。"
              ),
              output: copy("Dispatch posture and delivery history", "分发姿态和交付历史"),
              nextAction: copy("Inspect routes or dispatch output", "查看路由或分发输出"),
              cta: copy("Open Delivery Lane", "打开交付工作线"),
            }},
          ],
          advancedActions: [
            {{
              shellId: "delivery-advanced-shell",
              label: copy("Open Advanced Delivery Surfaces", "打开高级交付面板"),
            }},
          ],
          landingSection: "section-ops",
          footnote: copy("Keep delivery diagnostics available on demand instead of leaving them in the default scan path.", "让交付诊断面按需可见，而不是继续留在默认扫描路径上。"),
          topbarSubtitle: copy("Deliver | Route posture -> Dispatch -> History", "交付 | 路由姿态 -> 分发 -> 历史"),
        }},
      }};
      return descriptors[normalized] || descriptors.intake;
    }}

    function workspaceModeCurrentObjectLabel(activeSectionId) {{
      if (activeSectionId === "section-intake") {{
        const draftName = String(state.createWatchDraft?.name || "").trim();
        const draftQuery = String(state.createWatchDraft?.query || "").trim();
        return clampLabel(draftName || draftQuery || copy("Mission draft not started", "任务草稿尚未开始"), 42);
      }}
      if (activeSectionId === "section-board" || activeSectionId === "section-cockpit") {{
        const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
        return clampLabel(selectedWatch?.name || selectedWatch?.id || copy("No mission selected", "未选择任务"), 42);
      }}
      if (activeSectionId === "section-triage") {{
        const triageFocus = state.triage.find((item) => item.id === state.selectedTriageId);
        return clampLabel(triageFocus?.title || triageFocus?.id || copy("No evidence selected", "未选择证据"), 42);
      }}
      if (activeSectionId === "section-story") {{
        const selectedStory = getStoryRecord(state.selectedStoryId);
        return clampLabel(selectedStory?.title || selectedStory?.id || copy("No story selected", "未选择故事"), 42);
      }}
      if (activeSectionId === "section-claims") {{
        const selectedClaim = getSelectedClaimCard();
        const selectedReport = getSelectedReportRecord();
        return clampLabel(
          getClaimCardLabel(selectedClaim) || selectedReport?.title || selectedReport?.id || copy("No claim target selected", "未选择主张目标"),
          42,
        );
      }}
      if (activeSectionId === "section-report-studio") {{
        const selectedReport = getSelectedReportRecord();
        return clampLabel(selectedReport?.title || selectedReport?.id || copy("No report selected", "未选择报告"), 42);
      }}
      const selectedSubscription = getSelectedDeliverySubscription();
      const routeName = normalizeRouteName(state.contextRouteName) || selectedSubscription?.route_names?.[0] || state.routes[0]?.name || "";
      return clampLabel(
        summarizeDeliverySubject(selectedSubscription) || routeName || copy("No delivery object selected", "未选择交付对象"),
        42,
      );
    }}

    function workspaceModeOwnedOutputLabel(modeId, activeSectionId) {{
      if (modeId === "intake") {{
        const hasRequiredInput = Boolean(String(state.createWatchDraft?.name || "").trim() && String(state.createWatchDraft?.query || "").trim());
        return hasRequiredInput
          ? copy("Mission draft ready to create", "任务草稿已具备创建条件")
          : copy("Waiting for Name + Query", "等待填写名称和查询词");
      }}
      if (modeId === "missions") {{
        const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
        const resultStats = selectedWatch?.result_stats || state.watchDetails[state.selectedWatchId]?.result_stats || null;
        if (!selectedWatch) {{
          return copy("Select one mission to inspect its latest run", "选中一个任务后才能查看它的最新运行结果");
        }}
        return phrase(
          "{{status}} | {{count}} stored results",
          "{{status}} | {{count}} 条已存储结果",
          {{
            status: localizeWord(selectedWatch.last_run_status || "waiting"),
            count: Number(resultStats?.stored_result_count || resultStats?.returned_result_count || 0),
          }},
        );
      }}
      if (modeId === "review") {{
        if (activeSectionId === "section-story" || activeSectionId === "section-claims" || activeSectionId === "section-report-studio") {{
          const selectedStory = getStoryRecord(state.selectedStoryId);
          const selectedReport = getSelectedReportRecord();
          const quality = getReportComposition(selectedReport?.id || "")?.quality || null;
          if (activeSectionId === "section-story" && selectedStory) {{
            return phrase(
              "{{status}} | {{count}} evidence items",
              "{{status}} | {{count}} 条证据",
              {{
                status: localizeWord(selectedStory.status || "active"),
                count: Number(selectedStory.item_count || 0),
              }},
            );
          }}
          if (selectedReport) {{
            return phrase(
              "{{status}} | {{count}} sections",
              "{{status}} | {{count}} 个章节",
              {{
                status: localizeWord(quality?.status || selectedReport.status || "draft"),
                count: getReportSectionsForReport(selectedReport.id).length,
              }},
            );
          }}
        }}
        return phrase(
          "{{count}} open items in triage",
          "分诊中有 {{count}} 条待处理项",
          {{ count: Number(state.triageStats?.open_count || 0) }},
        );
      }}
      const routeSummary = state.ops?.route_summary || {{}};
      return phrase(
        "{{healthy}} healthy routes | {{alerts}} alerts",
        "{{healthy}} 条健康路由 | {{alerts}} 条告警",
        {{
          healthy: Number(routeSummary.healthy || 0),
          alerts: Number(state.alerts.length || 0),
        }},
      );
    }}

    function workspaceModeNextActionLabel(modeId, activeSectionId) {{
      if (modeId === "intake") {{
        const hasRequiredInput = Boolean(String(state.createWatchDraft?.name || "").trim() && String(state.createWatchDraft?.query || "").trim());
        return hasRequiredInput
          ? copy("Create the mission", "创建任务")
          : copy("Fill the required mission input", "补全任务必填信息");
      }}
      if (modeId === "missions") {{
        return state.selectedWatchId
          ? copy("Open Cockpit or run the mission", "打开任务详情或立即执行任务")
          : copy("Select one mission from the board", "先从列表选中一个任务");
      }}
      if (modeId === "review") {{
        if (activeSectionId === "section-claims" || activeSectionId === "section-report-studio") {{
          return getSelectedReportRecord()
            ? copy("Refresh composition or attach claims", "刷新编排或挂接主张")
            : copy("Choose a report target first", "先选择一个报告目标");
        }}
        return state.selectedStoryId
          ? copy("Refine the story and confirm readiness", "完善故事并确认交付就绪度")
          : (state.selectedTriageId
              ? copy("Verify or promote the selected evidence", "核验或提升当前证据")
              : copy("Pick one evidence item from triage", "先从分诊队列选中一条证据"));
      }}
      return state.routes.length
        ? copy("Inspect route posture or dispatch current output", "查看路由姿态或分发当前输出")
        : copy("Create a named route", "创建一个命名路由");
    }}

    function syncAdvancedSurfaceShells() {{
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      const reviewShell = $("review-advanced-shell");
      if (reviewShell instanceof HTMLDetailsElement) {{
        if (reviewAdvancedSectionIds.includes(activeSectionId)) {{
          reviewShell.open = true;
        }} else if (state.activeWorkspaceMode !== "review") {{
          reviewShell.open = false;
        }}
      }}
      const deliveryShell = $("delivery-advanced-shell");
      if (deliveryShell instanceof HTMLDetailsElement && state.activeWorkspaceMode !== "delivery") {{
        deliveryShell.open = false;
      }}
    }}

    function openAdvancedSurfaceShell(shellId) {{
      const shell = $(shellId);
      if (!(shell instanceof HTMLElement)) {{
        return;
      }}
      if (shell instanceof HTMLDetailsElement) {{
        shell.open = true;
      }}
      shell.scrollIntoView({{ block: "start", behavior: "smooth" }});
    }}

    function renderWorkspaceModeShell() {{
      const root = $("workspace-mode-shell");
      if (!root) {{
        return;
      }}
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode);
      const currentObject = workspaceModeCurrentObjectLabel(activeSectionId);
      const ownedOutput = workspaceModeOwnedOutputLabel(modeDescriptor.id, activeSectionId);
      const nextAction = workspaceModeNextActionLabel(modeDescriptor.id, activeSectionId);
      const cards = Array.isArray(modeDescriptor.modules) ? modeDescriptor.modules : [];
      const advancedActions = Array.isArray(modeDescriptor.advancedActions) ? modeDescriptor.advancedActions : [];
      const traceCard = renderStageLinkedTraceCard();
      const sharedSignalCard = renderSharedSignalTaxonomyCard();

      root.hidden = false;
      root.innerHTML = `
        <div class="workspace-mode-head">
          <div class="workspace-mode-summary">
            <div class="workspace-mode-kicker">${{escapeHtml(modeDescriptor.kicker)}}</div>
            <div class="workspace-mode-title">${{escapeHtml(modeDescriptor.label)}}</div>
            <div class="workspace-mode-copy">${{escapeHtml(modeDescriptor.summary)}}</div>
          </div>
          <div class="workspace-mode-meta">
            <span class="chip">${{copy("Current surface", "当前视图")}}: ${{escapeHtml(activeSectionLabel(activeSectionId))}}</span>
            <span class="chip ok">${{copy("Current object", "当前对象")}}: ${{escapeHtml(currentObject)}}</span>
            <span class="chip">${{copy("Owned output", "阶段产出")}}: ${{escapeHtml(ownedOutput)}}</span>
            <span class="chip hot">${{copy("Next action", "下一步动作")}}: ${{escapeHtml(nextAction)}}</span>
          </div>
        </div>
        <div class="workspace-mode-insight-grid">
          ${{traceCard}}
          ${{sharedSignalCard}}
        </div>
        <div class="workspace-mode-grid">
          ${{cards.map((card) => {{
            const sectionId = normalizeSectionId(card.sectionId || modeDescriptor.landingSection);
            const active = sectionId === activeSectionId;
            return `
              <button class="workspace-mode-card ${{active ? "active" : ""}}" type="button" data-workspace-jump="${{sectionId}}">
                <div class="workspace-mode-card-head">
                  <div>
                    <div class="workspace-mode-kicker">${{escapeHtml(modeDescriptor.label)}}</div>
                    <div class="workspace-mode-title">${{escapeHtml(card.title || activeSectionLabel(sectionId))}}</div>
                  </div>
                  <span class="chip ${{active ? "ok" : ""}}">${{active ? copy("Current", "当前") : copy("Open", "打开")}}</span>
                </div>
                <div class="workspace-mode-copy">${{escapeHtml(card.summary || "")}}</div>
                <div class="workspace-mode-modules">
                  <span class="workspace-mode-module">${{copy("Owned output", "阶段产出")}} · ${{escapeHtml(card.output || "")}}</span>
                  <span class="workspace-mode-module">${{copy("Next action", "下一步动作")}} · ${{escapeHtml(card.nextAction || "")}}</span>
                </div>
                <div class="workspace-mode-foot">
                  <span>${{copy("Surface", "视图")}} · ${{escapeHtml(activeSectionLabel(sectionId))}}</span>
                  <span>${{escapeHtml(card.cta || copy("Open surface", "打开视图"))}}</span>
                </div>
              </button>
            `;
          }}).join("")}}
        </div>
        <div class="workspace-mode-foot">
          <span>${{escapeHtml(modeDescriptor.footnote)}}</span>
          ${{advancedActions.map((action) => action.sectionId
            ? `<button class="chip-btn" type="button" data-workspace-jump="${{escapeHtml(action.sectionId)}}">${{escapeHtml(action.label)}}</button>`
            : `<button class="chip-btn" type="button" data-workspace-advanced-open="${{escapeHtml(action.shellId || "")}}">${{escapeHtml(action.label)}}</button>`
          ).join("")}}
        </div>
      `;
      root.querySelectorAll("[data-workspace-jump]").forEach((button) => {{
        button.addEventListener("click", () => {{
          jumpToSection(String(button.dataset.workspaceJump || "").trim());
        }});
      }});
      root.querySelectorAll("[data-workspace-advanced-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          openAdvancedSurfaceShell(String(button.dataset.workspaceAdvancedOpen || "").trim());
        }});
      }});
      root.querySelectorAll("[data-shared-signal-button]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const signalId = String(button.dataset.sharedSignalButton || "").trim();
          if (!signalId) {{
            return;
          }}
          state.sharedSignalFocus = signalId;
          renderWorkspaceModeShell();
        }});
      }});
      wireLifecycleGuideActions(root);
      scheduleCanvasTextFit(root);
    }}

    function renderWorkspaceModeChrome() {{
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      state.activeSectionId = activeSectionId;
      state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
      const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode);
      document.querySelectorAll("[data-workspace-group]").forEach((group) => {{
        const groupMode = normalizeWorkspaceMode(group.dataset.workspaceGroup || "");
        group.hidden = groupMode !== modeDescriptor.id;
      }});
      document.querySelectorAll(".topbar-nav [data-jump-target]").forEach((button) => {{
        const buttonMode = normalizeWorkspaceMode(button.dataset.workspaceMode || workspaceModeForSection(button.dataset.jumpTarget || ""));
        const active = buttonMode === modeDescriptor.id;
        button.hidden = false;
        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "page" : "false");
      }});
      setText("topbar-subtitle", modeDescriptor.topbarSubtitle);
      syncAdvancedSurfaceShells();
      renderWorkspaceModeShell();
    }}

    state.activeWorkspaceMode = workspaceModeForSection(state.activeSectionId);

    function contextLensEmptyValue() {{
      return copy("Not set", "未设置");
    }}

    function buildTopbarContextDescriptor() {{
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      state.activeSectionId = activeSectionId;
      state.activeWorkspaceMode = workspaceModeForSection(activeSectionId);
      const descriptor = {{
        modeId: state.activeWorkspaceMode,
        modeLabel: workspaceModeDescriptor(state.activeWorkspaceMode).label,
        sectionId: activeSectionId,
        sectionLabel: activeSectionLabel(activeSectionId),
        detail: "",
        rows: [],
      }};
      const pushRow = (label, value, {{ mono = false, muted = false }} = {{}}) => {{
        const hasValue = ![null, undefined].includes(value) && String(value).trim() !== "";
        descriptor.rows.push({{
          label,
          value: hasValue ? String(value).trim() : contextLensEmptyValue(),
          className: [
            mono ? "mono" : "",
            !hasValue || muted ? "muted" : "",
          ].filter(Boolean).join(" "),
        }});
      }};
      pushRow(copy("Rail", "主轨"), descriptor.modeLabel);

      if (activeSectionId === "section-intake") {{
        const draftName = String(state.createWatchDraft?.name || "").trim();
        const draftQuery = String(state.createWatchDraft?.query || "").trim();
        descriptor.detail = draftName || draftQuery
          ? clampLabel(draftName || draftQuery, 28)
          : copy("mission intake", "任务录入");
        pushRow(copy("Mode", "模式"), String(state.createWatchEditingId || "").trim() ? copy("Editing mission", "编辑任务") : copy("New mission", "新建任务"));
        pushRow(copy("Name", "名称"), clampLabel(draftName, 52));
        pushRow(copy("Query", "查询词"), clampLabel(draftQuery, 72), {{ mono: true }});
        pushRow(copy("Schedule", "频率"), String(state.createWatchDraft?.schedule || "").trim() || "manual", {{ mono: true }});
      }} else if (activeSectionId === "section-board" || activeSectionId === "section-cockpit") {{
        const selectedWatch = state.watchDetails[state.selectedWatchId] || state.watches.find((watch) => watch.id === state.selectedWatchId);
        const watchLabel = selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 28) : "";
        const watchSearch = String(state.watchSearch || "").trim();
        descriptor.detail = watchSearch
          ? phrase("q={{query}}", "搜索={{query}}", {{ query: clampLabel(watchSearch, 20) }})
          : (watchLabel || copy("mission focus", "任务聚焦"));
        pushRow(copy("Mission", "任务"), selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 52) : "");
        pushRow(copy("Search", "搜索"), clampLabel(watchSearch, 52), {{ mono: true }});
        pushRow(copy("Schedule", "频率"), String(selectedWatch?.schedule_label || selectedWatch?.schedule || "").trim(), {{ mono: true }});
        pushRow(copy("Alerts", "告警"), selectedWatch ? String(selectedWatch.alert_rule_count || (Array.isArray(selectedWatch.alert_rules) ? selectedWatch.alert_rules.length : 0) || 0) : "", {{ mono: true }});
      }} else if (activeSectionId === "section-triage") {{
        const triageFocus = state.triage.find((item) => item.id === state.selectedTriageId);
        const triageSearch = String(state.triageSearch || "").trim();
        if (state.triagePinnedIds.length) {{
          descriptor.detail = phrase("evidence x{{count}}", "证据 x{{count}}", {{ count: state.triagePinnedIds.length }});
        }} else if (triageSearch) {{
          descriptor.detail = phrase("{{filter}} | {{query}}", "{{filter}} | {{query}}", {{
            filter: localizeWord(state.triageFilter || "open"),
            query: clampLabel(triageSearch, 18),
          }});
        }} else {{
          descriptor.detail = triageFocus
            ? clampLabel(triageFocus.title || triageFocus.id, 28)
            : localizeWord(state.triageFilter || "open");
        }}
        pushRow(copy("Queue", "队列"), localizeWord(state.triageFilter || "open"));
        pushRow(copy("Search", "搜索"), clampLabel(triageSearch, 52), {{ mono: true }});
        pushRow(copy("Selected", "当前条目"), triageFocus ? clampLabel(triageFocus.title || triageFocus.id, 52) : "");
        pushRow(copy("Evidence focus", "证据聚焦"), state.triagePinnedIds.length ? phrase("{{count}} linked items", "{{count}} 个关联条目", {{ count: state.triagePinnedIds.length }}) : "");
        pushRow(copy("Batch", "批量"), state.selectedTriageIds.length ? phrase("{{count}} selected", "{{count}} 个已选", {{ count: state.selectedTriageIds.length }}) : "");
      }} else if (activeSectionId === "section-story") {{
        const activeStoryView = detectStoryViewPreset({{
          filter: state.storyFilter,
          sort: state.storySort,
          search: state.storySearch,
        }});
        const selectedStory = getStoryRecord(state.selectedStoryId);
        const storySearch = String(state.storySearch || "").trim();
        descriptor.detail = storySearch
          ? phrase("{{view}} | {{query}}", "{{view}} | {{query}}", {{
            view: storyViewPresetLabel(activeStoryView),
            query: clampLabel(storySearch, 18),
          }})
          : (selectedStory
              ? phrase("{{view}} | {{title}}", "{{view}} | {{title}}", {{
                  view: storyViewPresetLabel(activeStoryView),
                  title: clampLabel(selectedStory.title || selectedStory.id, 18),
                }})
              : storyViewPresetLabel(activeStoryView));
        pushRow(copy("View", "视图"), storyViewPresetLabel(activeStoryView));
        pushRow(
          copy("Workspace Mode", "工作区模式"),
          state.storyWorkspaceMode === "editor" ? copy("Editor", "编辑") : copy("Board", "看板"),
        );
        pushRow(copy("Sort", "排序"), storySortLabel(state.storySort));
        pushRow(copy("Search", "搜索"), clampLabel(storySearch, 52), {{ mono: true }});
        pushRow(copy("Selected", "当前故事"), selectedStory ? clampLabel(selectedStory.title || selectedStory.id, 52) : "");
        pushRow(copy("Batch", "批量"), state.selectedStoryIds.length ? phrase("{{count}} selected", "{{count}} 个已选", {{ count: state.selectedStoryIds.length }}) : "");
      }} else if (activeSectionId === "section-claims") {{
        const selectedReport = getSelectedReportRecord();
        const selectedSection = getSelectedReportSectionRecord();
        const selectedClaim = getSelectedClaimCard();
        const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
        descriptor.detail = selectedClaim
          ? clampLabel(getClaimCardLabel(selectedClaim), 28)
          : (selectedReport
              ? phrase("report={{title}}", "报告={{title}}", {{ title: clampLabel(selectedReport.title || selectedReport.id, 18) }})
              : copy("claim composition", "主张装配"));
        pushRow(copy("Report", "报告"), selectedReport ? clampLabel(selectedReport.title || selectedReport.id, 52) : "");
        pushRow(copy("Section", "章节"), selectedSection ? clampLabel(selectedSection.title || selectedSection.id, 52) : "");
        pushRow(copy("Claim", "主张"), selectedClaim ? clampLabel(getClaimCardLabel(selectedClaim), 72) : "");
        pushRow(copy("Quality", "质量"), selectedQuality ? `${{localizeWord(selectedQuality.status || "draft")}} / ${{Number(selectedQuality.score || 0).toFixed(2)}}` : "");
      }} else if (activeSectionId === "section-report-studio") {{
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
        pushRow(copy("Sections", "章节"), selectedReport ? String(reportSections.length) : "", {{ mono: true }});
        pushRow(copy("Claims", "主张"), selectedReport ? String(reportClaimIds.length) : "", {{ mono: true }});
        pushRow(copy("Quality", "质量"), selectedQuality ? `${{localizeWord(selectedQuality.status || "draft")}} / ${{Number(selectedQuality.score || 0).toFixed(2)}}` : "");
      }} else if (activeSectionId === "section-ops") {{
        const daemonState = String(state.status?.state || "").trim();
        const routeSummary = state.ops?.route_summary || {{}};
        descriptor.detail = copy("health and delivery", "健康与交付");
        pushRow(copy("Daemon", "守护进程"), daemonState ? localizeWord(daemonState) : "");
        pushRow(copy("Routes", "路由"), String(state.routes.length || 0), {{ mono: true }});
        pushRow(copy("Healthy", "健康"), String(routeSummary.healthy || 0), {{ mono: true }});
        pushRow(copy("Alerts", "告警"), String(state.alerts.length || 0), {{ mono: true }});
      }}

      descriptor.summary = descriptor.detail
        ? `${{descriptor.modeLabel}} / ${{descriptor.sectionLabel}} | ${{descriptor.detail}}`
        : `${{descriptor.modeLabel}} / ${{descriptor.sectionLabel}}`;
      return descriptor;
    }}

    function buildCurrentContextLinkRecord(descriptor = buildTopbarContextDescriptor()) {{
      const url = new URL(window.location.href);
      url.hash = descriptor.sectionId ? `#${{descriptor.sectionId}}` : "";
      return normalizeContextLinkHistoryEntry({{
        url: `${{url.pathname}}${{url.search}}${{url.hash}}`,
        summary: descriptor.summary,
        sectionId: descriptor.sectionId,
        timestamp: new Date().toISOString(),
      }});
    }}

    function renderContextViewDock() {{
      const root = $("context-view-dock");
      if (!root) {{
        return;
      }}
      const modeDescriptor = workspaceModeDescriptor(state.activeWorkspaceMode || workspaceModeForSection(state.activeSectionId));
      const stageSections = workspaceModeSectionMap[modeDescriptor.id] || [];
      const current = buildCurrentContextLinkRecord();
      const currentUrl = current ? current.url : "";
      const currentSavedIndex = current ? findContextSavedViewIndexByUrl(current.url) : -1;
      const currentSavedEntry = currentSavedIndex >= 0 ? normalizeContextSavedViewEntry(state.contextSavedViews[currentSavedIndex]) : null;
      const defaultEntry = getDefaultContextSavedView();
      const pinnedEntries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter((entry) => entry && entry.pinned)
        .slice(0, 4);
      const pinnedCount = pinnedEntries.length;
      const remainingSlots = Math.max(0, 4 - pinnedCount);
      const onIntake = normalizeSectionId(state.activeSectionId) === "section-intake";
      const showSectionRail = stageSections.length > 1;
      const shouldShowDock = Boolean(pinnedEntries.length);
      const showUnsavedHint = Boolean(
        current &&
        !currentSavedEntry &&
        !onIntake
      );
      const showSavedOnlyHint = Boolean(currentSavedEntry && !currentSavedEntry.pinned);
      const canSaveCurrent = Boolean(!onIntake && current && !currentSavedEntry);
      const canPinCurrent = Boolean(currentSavedIndex >= 0 && currentSavedEntry && !currentSavedEntry.pinned);
      const summaryLabel = current?.summary || copy("No active context", "当前没有激活上下文");
      const summaryCopy = copy(
        "Use the lifecycle rail for primary movement. Pinned views stay here as accelerators, while deep links and palette actions remain optional speed paths.",
        "主导航仍由生命周期主轨负责；这里保留固定视图作为加速入口，而深链和命令面板继续只是可选捷径。"
      );
      root.hidden = !shouldShowDock;
      if (!shouldShowDock) {{
        root.innerHTML = "";
        return;
      }}
      root.innerHTML = `
        <div class="context-view-dock-head">
          <div>
            <div class="context-view-dock-title">${{copy("Workspace Context", "工作上下文")}}</div>
            <div class="context-view-dock-summary" data-fit-text="dock-summary" data-fit-fallback="40">${{escapeHtml(summaryLabel)}}</div>
          </div>
          <div class="meta">
            <span class="chip ok">${{escapeHtml(modeDescriptor.label)}}</span>
            <span class="chip">${{remainingSlots ? phrase("{{count}} open", "{{count}} 个空位", {{ count: remainingSlots }}) : copy("Rail full", "轨道已满")}}</span>
            ${{showUnsavedHint ? `<span class="chip hot">${{copy("Unsaved", "未保存")}}</span>` : ""}}
            ${{showSavedOnlyHint ? `<span class="chip">${{copy("Saved only", "仅已保存")}}</span>` : ""}}
            ${{defaultEntry ? `<span class="chip ok" data-fit-text="dock-default-chip" data-fit-max-width="190" data-fit-fallback="24">${{copy("Default", "默认")}}: ${{escapeHtml(defaultEntry.name)}}</span>` : ""}}
            <button class="btn-secondary" type="button" data-context-dock-manage>${{copy("Open Context", "打开上下文")}}</button>
          </div>
        </div>
        ${{showSectionRail
          ? `<div class="context-view-dock-section">
              <div class="context-view-dock-title">${{copy("Current Rail", "当前主轨")}}</div>
              <div class="context-view-dock-list">
                ${{stageSections.map((sectionId) => `
                  <button
                    class="chip-btn ${{sectionId === normalizeSectionId(state.activeSectionId) ? "active" : ""}}"
                    type="button"
                    data-context-section="${{sectionId}}"
                  >
                    ${{escapeHtml(activeSectionLabel(sectionId))}}
                  </button>
                `).join("")}}
              </div>
            </div>`
          : ""}}
        ${{pinnedEntries.length
          ? `<div class="context-view-dock-section">
              <div class="context-view-dock-title">${{copy("Pinned Views", "已固定视图")}}</div>
              <div class="context-view-dock-list">
              ${{pinnedEntries.map((entry, index) => `
                <button
                  class="chip-btn ${{entry.url === currentUrl ? "active" : ""}}"
                  type="button"
                  data-context-dock-open="${{index}}"
                  data-fit-text="saved-view-chip"
                  data-fit-max-width="184"
                  data-fit-fallback="22"
                  title="${{escapeHtml(entry.isDefault ? phrase("Default | {{summary}}", "默认 | {{summary}}", {{ summary: entry.summary }}) : entry.summary)}}"
                >
                  ${{escapeHtml(entry.isDefault ? phrase("{{name}} [default]", "{{name}} [默认]", {{ name: entry.name }}) : entry.name)}}
                </button>
              `).join("")}}
              </div>
            </div>`
          : ""}}
        <div class="context-view-dock-tools">
          <div class="context-view-dock-copy">${{escapeHtml(summaryCopy)}}</div>
          <div class="context-view-dock-actions">
            ${{currentSavedEntry?.pinned ? `<span class="chip ok">${{copy("Current pinned", "当前已固定")}}</span>` : ""}}
            ${{canPinCurrent ? `<button class="btn-secondary" type="button" data-context-dock-pin-current>${{copy("Pin Current View", "固定当前视图")}}</button>` : ""}}
            ${{canSaveCurrent ? `<button class="btn-secondary" type="button" data-context-dock-save-pin>${{copy("Save + Pin Current", "保存并固定当前视图")}}</button>` : ""}}
          </div>
        </div>
      `;
      root.querySelector("[data-context-dock-manage]")?.addEventListener("click", () => {{
        state.contextLensRestoreFocusId = "context-summary";
        setContextLensOpen(true);
      }});
      root.querySelectorAll("[data-context-section]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const sectionId = String(button.dataset.contextSection || "").trim();
          if (sectionId) {{
            jumpToSection(sectionId);
          }}
        }});
      }});
      root.querySelectorAll("[data-context-dock-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const pinnedIndex = Number(button.dataset.contextDockOpen || -1);
          const entry = pinnedEntries[pinnedIndex];
          if (entry) {{
            restoreContextSavedViewByName(entry.name);
          }}
        }});
      }});
      root.querySelector("[data-context-dock-pin-current]")?.addEventListener("click", () => {{
        if (currentSavedIndex >= 0) {{
          toggleContextSavedViewPinned(currentSavedIndex);
        }}
      }});
      root.querySelector("[data-context-dock-save-pin]")?.addEventListener("click", () => {{
        saveAndPinCurrentContextView();
      }});
      scheduleCanvasTextFit(root);
    }}

    function renderContextSavedViews() {{
      const root = $("context-lens-saved");
      if (!root) {{
        return;
      }}
      const entries = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .filter(Boolean)
        .slice(0, 8);
      const pinnedIndexes = entries
        .map((entry, index) => (entry.pinned ? index : -1))
        .filter((index) => index >= 0);
      root.innerHTML = `
        <div class="context-lens-history-head">
          <div class="context-lens-history-title">${{copy("Saved Views", "已保存视图")}}</div>
          ${{entries.length ? `<button class="btn-secondary" type="button" data-context-saved-clear>${{copy("Clear", "清空")}}</button>` : ""}}
        </div>
        ${{entries.length
          ? `<div class="context-lens-history-list">
              ${{entries.map((entry, index) => {{
                const pinnedPosition = pinnedIndexes.indexOf(index);
                const canMoveLeft = pinnedPosition > 0;
                const canMoveRight = pinnedPosition >= 0 && pinnedPosition < pinnedIndexes.length - 1;
                return `
                <div class="context-history-item">
                  <div class="context-history-summary">${{escapeHtml(entry.name)}}</div>
                  <div class="context-history-meta">
                    <span>${{escapeHtml(activeSectionLabel(entry.sectionId))}}</span>
                    <span>${{escapeHtml(formatCompactDateTime(entry.timestamp))}}</span>
                    ${{entry.isDefault ? `<span class="chip ok">${{copy("Default", "默认")}}</span>` : ""}}
                    ${{entry.pinned ? `<span class="chip">${{copy("Pinned", "已固定")}}</span>` : ""}}
                  </div>
                  <div class="panel-sub">${{escapeHtml(entry.summary)}}</div>
                  <div class="context-history-url">${{escapeHtml(clampLabel(entry.url, 96))}}</div>
                  <div class="context-history-actions">
                    <button class="btn-secondary" type="button" data-context-saved-open="${{index}}">${{copy("Open", "打开")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-copy="${{index}}">${{copy("Copy", "复制")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-pin="${{index}}">${{entry.pinned ? copy("Unpin", "取消固定") : copy("Pin", "固定")}}</button>
                    ${{entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-left="${{index}}" ${{canMoveLeft ? "" : "disabled"}}>${{copy("Move Left", "左移")}}</button>` : ""}}
                    ${{entry.pinned ? `<button class="btn-secondary" type="button" data-context-saved-move-right="${{index}}" ${{canMoveRight ? "" : "disabled"}}>${{copy("Move Right", "右移")}}</button>` : ""}}
                    <button class="btn-secondary" type="button" data-context-saved-default="${{index}}">${{entry.isDefault ? copy("Clear Default", "取消默认") : copy("Set Default", "设为默认")}}</button>
                    <button class="btn-secondary" type="button" data-context-saved-delete="${{index}}">${{copy("Delete", "删除")}}</button>
                  </div>
                </div>
              `;
              }}).join("")}}
            </div>`
          : `<div class="empty">${{copy("No saved view yet. Name one above and it will stay here.", "还没有保存视图。给上面的当前视图起个名字，它就会保留在这里。")}}</div>`}}
      `;
      root.querySelector("[data-context-saved-clear]")?.addEventListener("click", () => {{
        clearContextSavedViews();
      }});
      root.querySelectorAll("[data-context-saved-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          restoreContextSavedViewEntry(Number(button.dataset.contextSavedOpen || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-copy]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await copyContextSavedViewEntry(Number(button.dataset.contextSavedCopy || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-pin]").forEach((button) => {{
        button.addEventListener("click", () => {{
          toggleContextSavedViewPinned(Number(button.dataset.contextSavedPin || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-move-left]").forEach((button) => {{
        button.addEventListener("click", () => {{
          moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveLeft || -1), "left");
        }});
      }});
      root.querySelectorAll("[data-context-saved-move-right]").forEach((button) => {{
        button.addEventListener("click", () => {{
          moveContextSavedViewInDock(Number(button.dataset.contextSavedMoveRight || -1), "right");
        }});
      }});
      root.querySelectorAll("[data-context-saved-default]").forEach((button) => {{
        button.addEventListener("click", () => {{
          setDefaultContextSavedView(Number(button.dataset.contextSavedDefault || -1));
        }});
      }});
      root.querySelectorAll("[data-context-saved-delete]").forEach((button) => {{
        button.addEventListener("click", () => {{
          deleteContextSavedView(Number(button.dataset.contextSavedDelete || -1));
        }});
      }});
    }}

    function renderContextLinkHistory() {{
      const root = $("context-lens-history");
      if (!root) {{
        return;
      }}
      const entries = (Array.isArray(state.contextLinkHistory) ? state.contextLinkHistory : [])
        .map((entry) => normalizeContextLinkHistoryEntry(entry))
        .filter(Boolean)
        .slice(0, 6);
      root.innerHTML = `
        <div class="context-lens-history-head">
          <div class="context-lens-history-title">${{copy("Recently Shared", "最近分享")}}</div>
          ${{entries.length ? `<button class="btn-secondary" type="button" data-context-history-clear>${{copy("Clear", "清空")}}</button>` : ""}}
        </div>
        ${{entries.length
          ? `<div class="context-lens-history-list">
              ${{entries.map((entry, index) => `
                <div class="context-history-item">
                  <div class="context-history-summary">${{escapeHtml(entry.summary)}}</div>
                  <div class="context-history-meta">
                    <span>${{escapeHtml(activeSectionLabel(entry.sectionId))}}</span>
                    <span>${{escapeHtml(formatCompactDateTime(entry.timestamp))}}</span>
                  </div>
                  <div class="context-history-url">${{escapeHtml(clampLabel(entry.url, 96))}}</div>
                  <div class="context-history-actions">
                    <button class="btn-secondary" type="button" data-context-history-open="${{index}}">${{copy("Open", "打开")}}</button>
                    <button class="btn-secondary" type="button" data-context-history-copy="${{index}}">${{copy("Copy", "复制")}}</button>
                  </div>
                </div>
              `).join("")}}
            </div>`
          : `<div class="empty">${{copy("No shared context yet. Copy a deep link and it will appear here.", "还没有分享上下文。复制一次深链后，这里就会出现。")}}</div>`}}
      `;
      root.querySelector("[data-context-history-clear]")?.addEventListener("click", () => {{
        clearContextLinkHistory();
      }});
      root.querySelectorAll("[data-context-history-open]").forEach((button) => {{
        button.addEventListener("click", () => {{
          restoreContextLinkHistoryEntry(Number(button.dataset.contextHistoryOpen || -1));
        }});
      }});
      root.querySelectorAll("[data-context-history-copy]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await copyContextLinkHistoryEntry(Number(button.dataset.contextHistoryCopy || -1));
        }});
      }});
    }}

    function syncContextLensChrome() {{
      const summary = $("context-summary");
      const lens = $("context-lens");
      const backdrop = $("context-lens-backdrop");
      const lensOpen = Boolean(state.contextLensOpen);
      if (summary) {{
        summary.setAttribute("aria-expanded", lensOpen ? "true" : "false");
      }}
      if (document.body) {{
        document.body.dataset.contextLensOpen = lensOpen ? "true" : "false";
      }}
      if (backdrop) {{
        backdrop.hidden = !lensOpen;
        backdrop.classList.toggle("open", lensOpen);
      }}
      if (lens) {{
        lens.hidden = !lensOpen;
        lens.setAttribute("aria-hidden", lensOpen ? "false" : "true");
      }}
    }}

    function renderContextLens(descriptor = buildTopbarContextDescriptor()) {{
      const body = $("context-lens-body");
      if (!body) {{
        return;
      }}
      body.innerHTML = descriptor.rows.length
        ? descriptor.rows.map((row) => `
            <div class="context-lens-row">
              <div class="context-lens-label">${{escapeHtml(row.label)}}</div>
              <div class="context-lens-value ${{escapeHtml(row.className || "")}}">${{escapeHtml(row.value)}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No active workspace context.", "当前没有工作上下文。")}}</div>`;
      renderContextSavedViews();
      renderContextLinkHistory();
    }}

    function getContextLensFocusableElements() {{
      const shell = $("context-lens-shell");
      if (!shell) {{
        return [];
      }}
      return Array.from(shell.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
        .filter((element) => !element.hasAttribute("hidden") && element.getAttribute("aria-hidden") !== "true");
    }}

    function setContextLensOpen(nextOpen) {{
      state.contextLensOpen = Boolean(nextOpen);
      const shell = $("context-lens-shell");
      syncContextLensChrome();
      if (state.contextLensOpen) {{
        renderContextLens();
        window.setTimeout(() => {{
          shell?.focus();
        }}, 10);
        return;
      }}
      window.setTimeout(() => {{
        $(state.contextLensRestoreFocusId || "context-summary")?.focus();
      }}, 0);
    }}

    function toggleContextLens() {{
      setContextLensOpen(!state.contextLensOpen);
    }}

    function applyWorkspaceUrlStateFromLocation({{ jump = true }} = {{}}) {{
      state.watchSearch = "";
      state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
      state.watchResultFilters = {{}};
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
      applyStoryWorkspaceMode(state.storyWorkspaceMode, {{ persist: false }});
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
      if (state.watchUrlFocusPending) {{
        flushWatchUrlFocus();
      }}
      if (state.triageUrlFocusPending) {{
        flushTriageUrlFocus();
      }}
      if (state.storyUrlFocusPending) {{
        flushStoryUrlFocus();
      }}
      if (jump && !hasFocusedSection) {{
        window.setTimeout(() => {{
          jumpToSection(state.activeSectionId, {{ updateHash: false }});
        }}, 0);
      }}
    }}

    async function copyContextLinkRecord(entry, {{ toastMessage = "" }} = {{}}) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      const href = new URL(normalized.url, window.location.origin).href;
      try {{
        if (window.navigator.clipboard?.writeText) {{
          await window.navigator.clipboard.writeText(href);
        }} else {{
          const helper = document.createElement("textarea");
          helper.value = href;
          helper.setAttribute("readonly", "readonly");
          helper.style.position = "absolute";
          helper.style.left = "-9999px";
          document.body.appendChild(helper);
          helper.select();
          document.execCommand("copy");
          document.body.removeChild(helper);
        }}
        noteContextLinkHistory({{
          ...normalized,
          timestamp: new Date().toISOString(),
        }});
        renderTopbarContext();
        showToast(toastMessage || copy("Context link copied", "已复制当前上下文链接"), "success");
      }} catch (error) {{
        reportError(error, copy("Copy context link", "复制上下文链接"));
      }}
    }}

    async function copyCurrentContextLink() {{
      await copyContextLinkRecord(buildCurrentContextLinkRecord());
    }}

    async function copyContextSavedViewEntry(entryIndex) {{
      const entry = normalizeContextSavedViewEntry(state.contextSavedViews[Number(entryIndex)]);
      if (!entry) {{
        return;
      }}
      await copyContextLinkRecord(entry, {{
        toastMessage: copy("Saved view link copied", "已复制保存视图链接"),
      }});
    }}

    async function copyContextLinkHistoryEntry(entryIndex) {{
      const entry = state.contextLinkHistory[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      await copyContextLinkRecord(entry, {{
        toastMessage: copy("Shared context link copied", "已复制分享上下文链接"),
      }});
    }}

    function restoreContextLinkRecord(entry, toastMessage, {{ noteHistory = true, closeLens = true, showToastMessage = true }} = {{}}) {{
      const normalized = normalizeContextLinkHistoryEntry(entry);
      if (!normalized) {{
        return;
      }}
      const target = new URL(normalized.url, window.location.origin);
      if (target.pathname !== window.location.pathname) {{
        window.location.assign(target.href);
        return;
      }}
      window.history.replaceState(
        window.history.state,
        "",
        `${{target.pathname}}${{target.search}}${{target.hash}}`,
      );
      if (noteHistory) {{
        noteContextLinkHistory({{
          ...normalized,
          timestamp: new Date().toISOString(),
        }});
      }}
      if (closeLens) {{
        setContextLensOpen(false);
      }}
      applyWorkspaceUrlStateFromLocation({{ jump: true }});
      if (showToastMessage && toastMessage) {{
        showToast(toastMessage, "success");
      }}
    }}

    function restoreContextLinkHistoryEntry(entryIndex) {{
      const entry = state.contextLinkHistory[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      restoreContextLinkRecord(entry, copy("Shared context restored", "已恢复分享上下文"));
    }}

    function restoreContextSavedViewEntry(entryIndex) {{
      const entry = state.contextSavedViews[Number(entryIndex)];
      if (!entry) {{
        return;
      }}
      restoreContextLinkRecord(entry, copy("Saved view restored", "已恢复保存视图"));
    }}

    function restoreContextSavedViewByName(viewName) {{
      const normalizedName = String(viewName || "").trim().toLowerCase();
      if (!normalizedName) {{
        return;
      }}
      const index = (Array.isArray(state.contextSavedViews) ? state.contextSavedViews : [])
        .map((entry) => normalizeContextSavedViewEntry(entry))
        .findIndex((entry) => entry && entry.name.toLowerCase() === normalizedName);
      if (index >= 0) {{
        restoreContextSavedViewEntry(index);
      }}
    }}

    function applyDefaultSavedViewOnBoot() {{
      if (!state.contextDefaultBootPending) {{
        return;
      }}
      state.contextDefaultBootPending = false;
      const defaultEntry = getDefaultContextSavedView();
      if (!defaultEntry) {{
        return;
      }}
      restoreContextLinkRecord(defaultEntry, "", {{
        noteHistory: false,
        closeLens: false,
        showToastMessage: false,
      }});
    }}

    function hasIntakePopulation() {{
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
    }}

    function renderIntakeLiveDesk() {{
      const onboardingHero = $("intake-hero-onboarding");
      const liveHero = $("intake-hero-live");
      const onboardingSide = $("intake-side-onboarding");
      const liveSide = $("intake-side-live");
      if (!onboardingHero || !liveHero || !onboardingSide || !liveSide) {{
        return;
      }}

      const hasPopulation = hasIntakePopulation();
      onboardingHero.hidden = hasPopulation;
      onboardingSide.hidden = hasPopulation;
      liveHero.hidden = !hasPopulation;
      liveSide.hidden = !hasPopulation;

      if (!hasPopulation) {{
        return;
      }}

      const overview = state.overview || {{}};
      const selectedWatch = state.watches.find((watch) => watch.id === state.selectedWatchId) || null;
      const selectedName = String((selectedWatch && (selectedWatch.name || selectedWatch.id)) || "").trim() || copy("No mission selected", "未选择任务");
      const enabledCount = Number(overview.enabled_watches ?? 0);
      const dueCount = Number(overview.due_watches ?? 0);
      const openQueue = Number(overview.triage_open_count ?? 0);
      const readyStories = Number(overview.story_ready_count ?? 0);
      const alertingMissions = Number(overview.alerting_mission_count ?? 0);
      const heroActions = selectedWatch ? [
        {{ label: copy("Open Cockpit", "打开任务详情"), section: "section-cockpit" }},
        {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
        selectedWatch.enabled
          ? {{ label: copy("Run Mission", "立即执行任务"), runWatch: selectedWatch.id }}
          : {{ label: copy("Enable Mission", "启用任务"), toggleWatch: selectedWatch.id, watchEnabled: "0" }},
      ] : [
        {{ label: copy("Create Mission", "新建任务"), focus: "mission", field: "name" }},
        {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board" }},
      ];
      const heroActionsHtml = heroActions.length
        ? heroActions.map((action) => `
            <button
              class="btn-primary"
              type="button"
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
              ${{action.toggleWatch ? `data-watch-toggle="${{escapeHtml(action.toggleWatch)}}"` : ""}}
              ${{action.watchEnabled ? `data-watch-enabled="${{escapeHtml(action.watchEnabled)}}"` : ""}}
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
            >${{escapeHtml(action.label)}}</button>
          `).join("")
        : "";
      const sideActions = [
        {{ label: copy("Open Story Workspace", "打开故事工作台"), section: "section-story" }},
        {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
        {{ label: copy("Reset Draft", "清空草稿"), reset: "mission" }},
      ];
      const sideActionsHtml = sideActions.map((action) => `
        <button
          class="chip-btn"
          type="button"
          ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
          ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
          ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
          ${{action.reset ? `data-empty-reset="${{escapeHtml(action.reset)}}"` : ""}}
        >${{escapeHtml(action.label)}}</button>
      `).join("");

      liveHero.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Live Intake Desk", "实时工作台")}}</div>
              <h3 class="panel-title" style="margin-top:8px;">${{escapeHtml(selectedName)}}</h3>
            </div>
            <span class="chip ${{selectedWatch ? "ok" : "hot"}}">${{selectedWatch ? copy("Mission Focus", "任务聚焦") : copy("Population Present", "已有数据")}}</span>
          </div>
          <div class="panel-sub">${{copy("Current object facts and pressure signal", "先显示当前对象事实与压力信号，再展示下一步动作。")}}</div>
          <div class="meta">
            <span class="chip ok">${{copy("Enabled missions", "活跃任务")}}=${{enabledCount}}</span>
            <span class="chip hot">${{copy("Due now", "当前待执行")}}=${{dueCount}}</span>
            <span class="chip">${{copy("Open queue", "待分诊")}}=${{openQueue}}</span>
            <span class="chip">${{copy("Ready stories", "待交付故事")}}=${{readyStories}}</span>
            <span class="chip">${{copy("Alerting missions", "告警中任务")}}=${{alertingMissions}}</span>
          </div>
          <div class="meta">${{copy("Next actions", "下一步动作")}}</div>
          <div class="actions">${{heroActionsHtml}}</div>
        </div>
      `;

      liveSide.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Current Object", "当前对象")}}</div>
              <h3 class="panel-title" style="margin-top:8px;">${{copy("Mission and Route Handoff", "任务与交付交接")}}</h3>
            </div>
          </div>
          <div class="panel-sub">${{copy("Mission continuity keeps review and routing actions close to live evidence so the shell opens on actionability before guidance text.", "任务连续性优先显示审阅与交付动作，避免先看到引导文案。")}}</div>
          <div class="meta">
            <span class="chip">${{copy("Object", "对象")}}=${{escapeHtml(selectedName)}}</span>
            <span class="chip">${{copy("Status", "状态")}}=${{selectedWatch ? (selectedWatch.enabled ? copy("enabled", "已启用") : copy("paused", "已暂停")) : copy("idle", "空闲")}}</span>
            <span class="chip">${{copy("Pressure", "压力")}}=${{openQueue + dueCount}}</span>
          </div>
          <div class="actions">${{sideActionsHtml}}</div>
        </div>
      `;

      wireLifecycleGuideActions(liveHero);
      wireLifecycleGuideActions(liveSide);
    }}

    function renderTopbarContext() {{
      const descriptor = buildTopbarContextDescriptor();
      setText("context-summary", descriptor.summary);
      $("context-summary")?.setAttribute("title", descriptor.summary);
      setPlaceholder("context-save-name", descriptor.summary);
      renderContextObjectRail();
      renderContextLens(descriptor);
      renderContextViewDock();
      syncContextLensChrome();
      renderIntakeLiveDesk();
      renderWorkspaceModeShell();
      scheduleCanvasTextFit($("context-shell"));
      scheduleCanvasTextFit($("context-view-dock"));
    }}

    function normalizeContextObjectId(value) {{
      return String(value || "").trim();
    }}

    function setContextRouteName(value, section = "") {{
      state.contextRouteName = normalizeContextObjectId(normalizeRouteName(value));
      state.contextRouteSection = String(section || "").trim();
    }}

    function getRouteRecordByName(routeName) {{
      const normalized = normalizeRouteName(routeName);
      if (!normalized) {{
        return null;
      }}
      return state.routes.find((route) => normalizeRouteName(route?.name) === normalized) || null;
    }}

    function getSelectedWatchForContext() {{
      const selectedWatchId = normalizeContextObjectId(state.selectedWatchId);
      if (!selectedWatchId) {{
        return null;
      }}
      return (
        state.watchDetails[selectedWatchId]
        || state.watches.find((watch) => watch.id === selectedWatchId)
        || null
      );
    }}

    function collectWatchRouteCandidates(watch) {{
      const watchRecord = watch || {{}};
      const rules = Array.isArray(watchRecord.alert_rules) ? watchRecord.alert_rules : [];
      const out = [];
      rules.forEach((rule) => {{
        const routeNames = normalizeRouteRuleNames(rule);
        routeNames.forEach((routeName) => {{
          if (routeName && !out.includes(routeName)) {{
            out.push(routeName);
          }}
        }});
      }});
      return out;
    }}

    function setContextRouteFromWatch() {{
      const selectedWatch = getSelectedWatchForContext();
      const draftRouteName = normalizeRouteName(state.createWatchDraft?.route);
      const routeCandidates = collectWatchRouteCandidates(selectedWatch);
      const contextRouteName = normalizeContextObjectId(state.contextRouteName);
      const activeSectionId = normalizeSectionId(state.activeSectionId);
      const activeRouteRecord = getRouteRecordByName(contextRouteName);

      if (draftRouteName) {{
        setContextRouteName(draftRouteName, "section-ops");
        return;
      }}

      if (contextRouteName && activeSectionId === "section-ops" && activeRouteRecord) {{
        setContextRouteName(contextRouteName, "section-ops");
        return;
      }}

      if (contextRouteName && routeCandidates.includes(contextRouteName)) {{
        setContextRouteName(contextRouteName, state.contextRouteSection || "section-board");
        return;
      }}

      if (routeCandidates.length) {{
        setContextRouteName(routeCandidates[0], "section-board");
        return;
      }}
      setContextRouteName("", "");
    }}

    function buildContextObjectRailDescriptor() {{
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

      return {{
        steps: [
          {{
            step: "mission",
            sectionId: "section-board",
            id: missionId,
            title: copy("Mission", "任务"),
            label: missionLabel,
          }},
          {{
            step: "evidence",
            sectionId: "section-triage",
            id: evidenceId,
            title: copy("Evidence", "证据"),
            label: evidenceLabel,
          }},
          {{
            step: "story",
            sectionId: "section-story",
            id: storyId,
            title: copy("Story", "故事"),
            label: storyLabel,
          }},
          {{
            step: "report",
            sectionId: "section-report-studio",
            id: reportId,
            title: copy("Report", "报告"),
            label: reportLabel,
          }},
          {{
            step: "route",
            sectionId: "section-ops",
            id: routeName,
            title: copy("Route", "路由"),
            label: routeRecord?.name || routeName || contextLensEmptyValue(),
          }},
        ],
      }};
    }}

    function renderContextObjectRail(descriptor = buildContextObjectRailDescriptor()) {{
      const root = $("context-object-rail");
      if (!root) {{
        return;
      }}
      const steps = Array.isArray(descriptor?.steps) ? descriptor.steps : [];
      root.innerHTML = steps
        .map((step) => `
          <button
            class="context-object-step"
            type="button"
            data-context-object-step="${{step.step}}"
            data-context-object-id="${{escapeHtml(step.id || "")}}"
            data-context-object-section="${{step.sectionId}}"
            title="${{escapeHtml(`${{step.title}}: ${{step.label || contextLensEmptyValue()}}`)}}"
          >
            <span class="context-object-step-title">${{escapeHtml(step.title)}}</span>
            <span class="context-object-step-value" data-fit-text="context-object-value" data-fit-fallback="18">${{escapeHtml(step.label || contextLensEmptyValue())}}</span>
          </button>`)
        .join('<span class="context-object-divider">→</span>');
      scheduleCanvasTextFit(root);
    }}

    async function activateContextObjectRailStep(stepName, objectId, sectionId) {{
      const normalizedStep = String(stepName || "").trim().toLowerCase();
      const normalizedObjectId = normalizeContextObjectId(objectId);
      const normalizedSectionId = normalizeSectionId(sectionId);

      if (normalizedStep === "mission" && normalizedObjectId) {{
        try {{
          await loadWatch(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open mission", "打开任务"));
        }}
      }} else if (normalizedStep === "evidence" && normalizedObjectId) {{
        const triageItem = state.triage.find((item) => item.id === normalizedObjectId) || null;
        if (triageItem) {{
          focusTriageEvidence([normalizedObjectId], {{ itemId: normalizedObjectId, jump: false, showToastMessage: false }});
        }}
      }} else if (normalizedStep === "story" && normalizedObjectId) {{
        try {{
          await loadStory(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open story", "打开故事"));
        }}
      }} else if (normalizedStep === "report" && normalizedObjectId) {{
        try {{
          await selectReport(normalizedObjectId);
        }} catch (error) {{
          reportError(error, copy("Open report", "打开报告"));
        }}
      }} else if (normalizedStep === "route" && normalizedObjectId) {{
        try {{
          await editRouteInDeck(normalizedObjectId);
          return;
        }} catch (error) {{
          reportError(error, copy("Open route", "打开路由"));
        }}
      }}

      if (normalizedSectionId) {{
        jumpToSection(normalizedSectionId);
      }}
    }}

    function bindContextObjectRail() {{
      const root = $("context-object-rail");
      if (!root) {{
        return;
      }}
      root.addEventListener("click", async (event) => {{
        const step = event.target.closest("[data-context-object-step]");
        if (!step) {{
          return;
        }}
        await activateContextObjectRailStep(
          String(step.dataset.contextObjectStep || ""),
          String(step.dataset.contextObjectId || ""),
          String(step.dataset.contextObjectSection || ""),
        );
      }});
    }}

    function applyLanguageChrome() {{
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
      setText("context-open-section", copy("Open Current Surface", "打开当前区块"));
      setText("context-copy-link", copy("Copy Link", "复制链接"));
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
      setText("deck-step-2-copy", copy("Use schedule and platform to narrow the mission only when you already know the operating lane.", "只有当你已经知道主要监测通道时，再补充频率、平台或站点。"));
      setText("label-schedule", copy("Schedule", "调度频率"));
      setText("label-platform", copy("Platform", "平台"));
      setText("label-domain", copy("Alert Domain", "站点/域名"));
      setText("hint-schedule", copy("Manual is fine for first exploration.", "初次探索时，用手动执行就够了。"));
      setText("hint-platform", copy("Leave empty for broader discovery.", "如果还不确定监测来源，可以先留空。"));
      setText("hint-domain", copy("Optional domain guard for tighter recall.", "可选的站点约束，用来提升结果收敛度。"));
      setText("schedule-lanes-title", copy("Schedule Lanes", "常用频率"));
      setText("platform-lanes-title", copy("Platform Lanes", "常用平台"));
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
      setText("review-advanced-title", copy("Advanced Review Surfaces", "高级审阅面板"));
      setText("review-advanced-copy", copy("Claim composition and report assembly stay available here without competing with triage and story work by default.", "主张装配和报告编排仍然可用，但默认不再与分诊和故事工作争夺同一级注意力。"));
      setText("review-advanced-chip", copy("Claim Composer + Report Studio", "主张装配 + 报告工作台"));
      setText("delivery-advanced-title", copy("Advanced Delivery Surfaces", "高级交付面板"));
      setText("delivery-advanced-copy", copy("AI projection inspection and route-health drill-down stay available here without competing with dispatch posture and delivery history by default.", "AI 投影视图和路由健康钻取仍然可用，但默认不再与分发姿态和交付历史争夺同一级注意力。"));
      setText("delivery-advanced-chip", copy("AI Assistance + Distribution Health", "AI 辅助 + 分发健康"));
      setText("triage-title", copy("Triage Queue", "分诊队列"));
      setText("triage-copy", copy("Review open items with one selected evidence workbench, keep analyst reasoning visible, and hand verified signal into stories without leaving the queue.", "通过一个选中证据工作台完成审阅，持续看到分析师推理，并在不离开队列的前提下把已核验信号交接给故事。"));
      setText("story-title", copy("Story Workspace", "故事工作台"));
      setText("story-copy", copy("Inspect promoted stories, evidence stacks, contradictions, and delivery readiness before the narrative leaves the browser.", "查看已提升的故事、证据堆栈、冲突点和交付就绪度，并在叙事离开浏览器前完成整理。"));
      setText("claims-title", copy("Claim Composer", "主张装配"));
      setText("claims-copy", copy("Compose source-bound claims and attach them to report sections without leaving the review lane.", "在不离开审阅主轨的前提下，编排带来源绑定的主张并把它挂进报告章节。"));
      setText("report-studio-title", copy("Report Studio", "报告工作台"));
      setText("report-studio-copy", copy("Inspect report sections, quality guardrails, and export previews over persisted report objects.", "围绕持久化报告对象查看章节结构、质量门禁和导出预览。"));
      setText("story-mode-switch-label", copy("Workspace mode", "工作区模式"));
      setText("story-mode-board-button", copy("Board", "看板"));
      setText("story-mode-editor-button", copy("Editor", "编辑"));
      setText("story-intake-title", copy("Story Intake", "故事录入"));
      setText("story-intake-copy", copy("Capture a manual brief when a story should exist before clustering catches up, then refine it inside the workspace.", "当某个故事需要先落下来、而聚类还没跟上时，可以先手工补录，再在工作台里继续完善。"));
      setText("story-intake-mode", copy("Editable", "可编辑"));
      setText("footer-note", copy("The browser is the operating surface. CLI and MCP remain first-class control planes.", "浏览器是主要操作界面；CLI 和 MCP 仍保持一等能力。"));
      setPlaceholder("command-palette-input", copy("Search actions, missions, stories, or routes", "搜索操作、任务、故事或路由"));
      setPlaceholder("input-name", copy("Launch Ops", "新品发布监测"));
      setPlaceholder("input-query", copy("OpenAI launch", "OpenAI 发布"));
      setPlaceholder("input-schedule", copy("@hourly / interval:15m", "@hourly / interval:15m"));
      setPlaceholder("input-platform", copy("twitter", "twitter"));
      setPlaceholder("input-domain", copy("openai.com", "openai.com"));
      setPlaceholder("input-route", copy("ops-webhook", "ops-webhook"));
      setPlaceholder("input-keyword", copy("launch", "发布"));
      setPlaceholder("input-score", copy("70", "70"));
      setPlaceholder("input-confidence", copy("0.8", "0.8"));
      document.querySelectorAll("[data-lang]").forEach((button) => {{
        button.classList.toggle("active", String(button.dataset.lang || "") === state.language);
      }});
      renderWorkspaceModeChrome();
      renderTopbarContext();
    }}

    state.language = detectInitialLanguage();

    function showToast(message, tone = "info") {{
      const rack = $("toast-rack");
      if (!rack) {{
        return;
      }}
      const toast = document.createElement("div");
      toast.className = `toast ${{tone}}`;
      toast.innerHTML = `
        <div class="mono">${{copy("mission signal", "任务信号")}} / ${{localizeWord(tone)}}</div>
        <div style="margin-top:6px;">${{escapeHtml(message)}}</div>
      `;
      rack.appendChild(toast);
      window.setTimeout(() => {{
        toast.style.opacity = "0";
        toast.style.transform = "translateY(8px)";
        toast.style.transition = "opacity .18s ease, transform .18s ease";
        window.setTimeout(() => toast.remove(), 220);
      }}, 2800);
    }}

    window.alert = (message) => showToast(String(message || ""), "error");

    function reportError(error, prefix = "") {{
      console.error(error);
      const message = error && error.message ? error.message : String(error || "Unknown error");
      showToast(prefix ? `${{prefix}}: ${{message}}` : message, "error");
    }}

    function focusCreateWatchDeck(fieldName = "query") {{
      const form = $("create-watch-form");
      if (!form) {{
        return;
      }}
      jumpToSection("section-intake");
      window.setTimeout(() => {{
        form.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
        const field = form.elements.namedItem(fieldName);
        if (field && typeof field.focus === "function") {{
          field.focus();
          if (typeof field.select === "function") {{
            field.select();
          }}
        }}
      }}, 140);
    }}

    function scheduleModeLabel(value) {{
      const schedule = String(value || "").trim();
      if (!schedule || schedule === "manual") {{
        return copy("manual dispatch", "手动执行");
      }}
      if (schedule.startsWith("interval:")) {{
        return state.language === "zh"
          ? `频率 ${{schedule.replace("interval:", "")}}`
          : `cadence ${{schedule.replace("interval:", "")}}`;
      }}
      if (schedule.startsWith("@")) {{
        return state.language === "zh" ? `Cron 别名 ${{schedule}}` : `cron alias ${{schedule}}`;
      }}
      return schedule;
    }}

    function buildCreateWatchPreview(draftInput) {{
      const draft = normalizeCreateWatchDraft(draftInput || defaultCreateWatchDraft());
      const requiredReady = Boolean(draft.name.trim() && draft.query.trim());
      const alertArmed = Boolean(
        draft.route.trim() ||
        draft.keyword.trim() ||
        draft.domain.trim() ||
        Number(draft.min_score || 0) > 0 ||
        Number(draft.min_confidence || 0) > 0,
      );
      const readiness = Math.min(
        100,
        (draft.name.trim() ? 34 : 0) +
        (draft.query.trim() ? 34 : 0) +
        (draft.schedule.trim() ? 8 : 0) +
        (draft.platform.trim() ? 8 : 0) +
        ((draft.route.trim() || draft.keyword.trim() || draft.domain.trim()) ? 8 : 0) +
        ((draft.min_score.trim() || draft.min_confidence.trim()) ? 8 : 0),
      );
      const filters = [draft.platform.trim(), draft.domain.trim(), draft.keyword.trim()].filter(Boolean);
      return {{
        draft,
        requiredReady,
        alertArmed,
        readiness,
        summary: draft.query.trim()
          ? phrase(
              "Track {{query}} with {{schedule}} across {{platform}} surfaces.",
              "围绕 {{query}} 以 {{schedule}} 跟踪 {{platform}} 信号。",
              {{
                query: draft.query.trim(),
                schedule: scheduleModeLabel(draft.schedule),
                platform: draft.platform.trim() || copy("cross-platform", "跨平台"),
              }},
            )
          : copy("Add a query to project the mission into the live preview lane.", "填入查询词后，任务会立即投射到实时预览区。"),
        scoreLabel: draft.min_score.trim() ? copy(`score >= ${{draft.min_score.trim()}}`, `分数 >= ${{draft.min_score.trim()}}`) : copy("score gate unset", "未设置分数门槛"),
        confidenceLabel: draft.min_confidence.trim() ? copy(`confidence >= ${{draft.min_confidence.trim()}}`, `置信度 >= ${{draft.min_confidence.trim()}}`) : copy("confidence gate unset", "未设置置信度门槛"),
        filtersLabel: filters.length ? filters.join(" / ") : copy("no scope filter", "未设置范围过滤"),
        routeLabel: draft.route.trim() || copy("route not attached", "未绑定路由"),
        scheduleLabel: scheduleModeLabel(draft.schedule),
      }};
    }}

    function syncCreateWatchForm() {{
      const form = $("create-watch-form");
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      if (!form) {{
        return;
      }}
      createWatchFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        if (!field || field.value === draft[fieldName]) {{
          return;
        }}
        field.value = draft[fieldName];
      }});
    }}

    function collectCreateWatchDraft(form) {{
      if (!form) {{
        return defaultCreateWatchDraft();
      }}
      const next = defaultCreateWatchDraft();
      createWatchFormFields.forEach((fieldName) => {{
        const field = form.elements.namedItem(fieldName);
        next[fieldName] = field ? String(field.value ?? "") : "";
      }});
      return normalizeCreateWatchDraft(next);
    }}

    function setCreateWatchDraft(nextDraft, presetId = "", editingId = state.createWatchEditingId) {{
      state.createWatchDraft = normalizeCreateWatchDraft(nextDraft || defaultCreateWatchDraft());
      state.createWatchPresetId = presetId;
      state.createWatchEditingId = String(editingId || "").trim();
      const startFeedback = state.stageFeedback?.start;
      if (startFeedback && ["blocked", "warning", "no_result"].includes(String(startFeedback.kind || "").trim().toLowerCase())) {{
        state.stageFeedback.start = null;
      }}
      syncCreateWatchForm();
      persistCreateWatchDraft();
      renderCreateWatchDeck();
      queueCreateWatchSuggestions();
      setContextRouteFromWatch();
    }}

    function updateCreateWatchDraft(patch = {{}}, presetId = "") {{
      setCreateWatchDraft({{
        ...normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft()),
        ...patch,
      }}, presetId);
    }}

    async function refreshCreateWatchSuggestions(force = false) {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      if (!force && !(draft.name.trim() || draft.query.trim() || draft.keyword.trim())) {{
        state.createWatchSuggestions = null;
        renderCreateWatchDeck();
        return;
      }}
      state.loading.suggestions = true;
      renderCreateWatchDeck();
      try {{
        state.createWatchSuggestions = await api("/api/console/deck/suggestions", {{
          method: "POST",
          payload: draft,
        }});
      }} catch (error) {{
        state.createWatchSuggestions = null;
        reportError(error, "Load mission suggestions");
      }} finally {{
        state.loading.suggestions = false;
        renderCreateWatchDeck();
      }}
    }}

    function queueCreateWatchSuggestions(force = false) {{
      if (state.createWatchSuggestionTimer) {{
        window.clearTimeout(state.createWatchSuggestionTimer);
      }}
      state.createWatchSuggestionTimer = window.setTimeout(() => {{
        refreshCreateWatchSuggestions(force).catch((error) => reportError(error, "Load mission suggestions"));
      }}, force ? 20 : 220);
    }}

    function renderCreateWatchDeck() {{
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

      if (deployTitle) {{
        deployTitle.textContent = editing ? copy("Edit Mission", "编辑监测任务") : copy("Deploy Mission", "创建监测任务");
      }}
      if (deployCopy) {{
        deployCopy.textContent = editing
          ? copy("Update one existing watch in place using the same mission deck.", "沿用同一套任务草稿面板，直接原位修改已有任务。")
          : copy("Create one watch, add optional scope, then decide whether alert routing is needed.", "先定义监测任务，再按需补充范围和通知条件。");
      }}
      if (advancedTitle) {{
        advancedTitle.textContent = editing ? copy("Refine Scope Carefully", "精细调整范围") : copy("Keep It Simple First", "先从简单输入开始");
      }}
      if (advancedCopy) {{
        advancedCopy.textContent = advancedOpen
          ? copy("Only fill the extra controls you actually need. Empty fields keep the mission broad and easier to operate.", "只填写真正需要的额外条件；留空代表任务保持更宽、更易操作。")
          : copy("Most missions only need Name and Query. Open advanced settings only when you need scope or alert delivery.", "大多数任务只需要名称和查询词；只有在要限定范围或接入告警时，再展开高级设置。");
      }}
      if (advancedToggle) {{
        advancedToggle.textContent = advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置");
        advancedToggle.setAttribute("aria-expanded", String(advancedOpen));
      }}
      if (advancedSummary) {{
        advancedSummary.innerHTML = summarizeCreateWatchAdvanced(draft).map((item) => `<span class="chip">${{escapeHtml(item)}}</span>`).join("");
      }}
      if (advancedPanel) {{
        advancedPanel.classList.toggle("collapsed", !advancedOpen);
        advancedPanel.setAttribute("aria-hidden", String(!advancedOpen));
      }}
      if (presetPanel) {{
        presetPanel.hidden = editing;
      }}
      if (clonePanel) {{
        clonePanel.hidden = editing;
      }}

      if (submitButton) {{
        submitButton.textContent = editing ? copy("Save Changes", "保存修改") : copy("Create Watch", "创建任务");
      }}
      if (clearButton) {{
        clearButton.textContent = editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿");
      }}

      if (presetRoot) {{
        presetRoot.innerHTML = createWatchPresets.map((preset, index) => `
          <button
            class="chip-btn ${{state.createWatchPresetId === preset.id ? "active" : ""}}"
            type="button"
            data-create-watch-preset="${{preset.id}}"
            title="${{escapeHtml(copy(preset.description, preset.zhDescription || preset.description))}}"
          >${{index + 1}}. ${{escapeHtml(copy(preset.label, preset.zhLabel || preset.label))}}</button>
        `).join("");
      }}

      if (scheduleRoot) {{
        scheduleRoot.innerHTML = scheduleLaneOptions.map((option) => `
          <button
            class="chip-btn ${{draft.schedule.trim() === option.value ? "active" : ""}}"
            type="button"
            data-create-watch-schedule="${{option.value}}"
          >${{escapeHtml(option.value === "manual" ? copy("manual", "手动") : option.label)}}</button>
        `).join("");
      }}

      if (platformRoot) {{
        platformRoot.innerHTML = platformLaneOptions.map((option) => `
          <button
            class="chip-btn ${{draft.platform.trim() === option.value ? "active" : ""}}"
            type="button"
            data-create-watch-platform="${{option.value}}"
          >${{escapeHtml(option.label)}}</button>
        `).join("");
      }}

      if (routeRoot) {{
        const routeButtons = state.routes.length
          ? state.routes.slice(0, 6).map((route) => `
              <button
                class="chip-btn ${{draft.route.trim() === String(route.name || "").trim() ? "active" : ""}}"
                type="button"
                data-create-watch-route="${{escapeHtml(route.name || "")}}"
              >${{escapeHtml(route.name || "unnamed-route")}}</button>
            `).join("")
          : `<span class="chip">${{copy("No named routes", "暂无命名路由")}}</span>`;
        routeRoot.innerHTML = routeButtons;
      }}

      if (cloneRoot) {{
        const cloneButtons = state.watches.length
          ? state.watches.slice(0, 6).map((watch) => `
              <button class="chip-btn" type="button" data-create-watch-clone="${{escapeHtml(watch.id)}}">${{escapeHtml(watch.name || watch.id)}}</button>
            `).join("")
          : `<span class="chip">${{copy("No mission to clone", "暂无可克隆任务")}}</span>`;
        cloneRoot.innerHTML = cloneButtons;
      }}

      if (previewRoot) {{
        previewRoot.className = `card mission-preview ${{preview.requiredReady ? "ready" : ""}}`;
        previewRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">${{copy("mission brief", "任务概览")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(draft.name.trim() || copy("Unnamed Mission", "未命名任务"))}}</h3>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : "hot"}}">${{preview.requiredReady ? copy("ready", "就绪") : copy("needs query/name", "缺少名称或查询词")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(preview.summary)}}</div>
          <div class="preview-meter">
            <div class="preview-meter-fill" style="width:${{preview.readiness}}%;"></div>
          </div>
          <div class="meta">
            <span>${{copy("mode", "模式")}}=${{editing ? copy("edit existing", "编辑已有任务") : copy("create new", "新建任务")}}</span>
            <span>${{copy("readiness", "就绪度")}}=${{preview.readiness}}%</span>
            <span>${{copy("alert", "告警")}}=${{preview.alertArmed ? copy("armed", "已启用") : copy("passive", "未启用")}}</span>
            <span>${{copy("schedule", "频率")}}=${{escapeHtml(preview.scheduleLabel)}}</span>
          </div>
          <div class="preview-grid">
            <div class="preview-line">
              <div class="preview-label">${{copy("Scope", "范围")}}</div>
              <div class="preview-value">${{escapeHtml(preview.filtersLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Route", "路由")}}</div>
              <div class="preview-value">${{escapeHtml(preview.routeLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Score Gate", "分数门槛")}}</div>
              <div class="preview-value">${{escapeHtml(preview.scoreLabel)}}</div>
            </div>
            <div class="preview-line">
              <div class="preview-label">${{copy("Confidence Gate", "置信度门槛")}}</div>
              <div class="preview-value">${{escapeHtml(preview.confidenceLabel)}}</div>
            </div>
          </div>
        `;
      }}

      if (suggestionRoot) {{
        if (state.loading.suggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
            <div class="panel-sub">${{copy("Deriving route, cadence, and duplicate signals from the current repository state.", "正在基于当前仓库状态推导路由、频率和重复信号。")}}</div>
            <div class="stack" style="margin-top:12px;">${{skeletonCard(4)}}</div>
            ${{buildMissionGuidanceSurface(preview)}}
          `;
        }} else if (!state.createWatchSuggestions) {{
          suggestionRoot.innerHTML = `
            <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
            <div class="panel-sub">${{copy("Start typing a mission draft and the deck will derive cadence, route, and duplicate pressure from current watches and stories.", "开始输入任务草稿后，系统会根据现有任务和故事自动推导频率、路由与重复风险。")}}</div>
            ${{buildMissionGuidanceSurface(preview)}}
          `;
        }} else {{
          const suggestions = state.createWatchSuggestions;
          const warningBlock = Array.isArray(suggestions.warnings) && suggestions.warnings.length
            ? `<div class="suggestion-list">${{suggestions.warnings.map((item) => `<div class="mini-item">${{escapeHtml(item)}}</div>`).join("")}}</div>`
            : `<div class="panel-sub">${{copy("No active conflict or delivery warning for this draft.", "当前草稿没有冲突或交付告警。")}}</div>`;
          const similarWatches = Array.isArray(suggestions.similar_watches) ? suggestions.similar_watches : [];
          const relatedStories = Array.isArray(suggestions.related_stories) ? suggestions.related_stories : [];
          suggestionRoot.innerHTML = `
            <div class="card-top">
              <div>
                <div class="mono">${{copy("mission suggestions", "任务建议")}}</div>
                <div class="panel-sub" style="margin-top:8px;">${{escapeHtml(suggestions.summary || "")}}</div>
              </div>
              <button class="btn-secondary" id="apply-all-suggestions" type="button">${{copy("Apply All", "全部应用")}}</button>
            </div>
            <div class="suggestion-grid">
              <div class="preview-grid">
                <div class="preview-line">
                  <div class="preview-label">${{copy("Cadence", "频率")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_schedule || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.schedule_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Platform", "平台")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_platform || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.platform_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Route", "路由")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_route || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.route_reason || "")}}</div>
                </div>
                <div class="preview-line">
                  <div class="preview-label">${{copy("Scope Hints", "范围提示")}}</div>
                  <div class="preview-value">${{escapeHtml(suggestions.recommended_keyword || "-")}} / ${{escapeHtml(suggestions.recommended_domain || "-")}}</div>
                  <div class="panel-sub">${{escapeHtml(suggestions.keyword_reason || suggestions.domain_reason || "")}}</div>
                </div>
              </div>
              <div class="chip-row">
                <button class="chip-btn" type="button" data-suggestion-apply="schedule">${{escapeHtml(suggestions.recommended_schedule || "schedule")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="platform">${{escapeHtml(suggestions.recommended_platform || "platform")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="route">${{escapeHtml(suggestions.recommended_route || "route")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="keyword">${{escapeHtml(suggestions.recommended_keyword || "keyword")}}</button>
                <button class="chip-btn" type="button" data-suggestion-apply="thresholds">${{copy("score/confidence", "分数/置信度")}}</button>
              </div>
              <div class="stack">
                <div class="mono">${{copy("Warnings", "提醒")}}</div>
                ${{warningBlock}}
              </div>
              <div class="preview-grid">
                <div class="stack">
                  <div class="mono">${{copy("Similar Missions", "相似任务")}}</div>
                  ${{similarWatches.length ? similarWatches.map((item) => `<div class="mini-item">${{escapeHtml(item.name)}} | ${{copy("similarity", "相似度")}}=${{Number(item.similarity || 0).toFixed(2)}} | ${{escapeHtml(item.schedule || copy("manual", "手动"))}}</div>`).join("") : `<div class="panel-sub">${{copy("No mission conflict found.", "未发现任务冲突。")}}</div>`}}
                </div>
                <div class="stack">
                  <div class="mono">${{copy("Related Stories", "相关故事")}}</div>
                  ${{relatedStories.length ? relatedStories.map((item) => `<div class="mini-item">${{escapeHtml(item.title)}} | ${{copy("similarity", "相似度")}}=${{Number(item.similarity || 0).toFixed(2)}} | ${{copy("items", "条目")}}=${{item.item_count || 0}}</div>`).join("") : `<div class="panel-sub">${{copy("No story cluster overlap found.", "未发现故事簇重叠。")}}</div>`}}
                </div>
              </div>
            </div>
            ${{buildMissionGuidanceSurface(preview, suggestions)}}
          `;
          suggestionRoot.querySelector("#apply-all-suggestions")?.addEventListener("click", () => {{
            const patch = suggestions.autofill_patch || {{}};
            state.createWatchAdvancedOpen = true;
            updateCreateWatchDraft(patch);
            showToast(copy("Applied suggested mission defaults", "已应用建议的任务默认值"), "success");
          }});
          suggestionRoot.querySelectorAll("[data-suggestion-apply]").forEach((button) => {{
            button.addEventListener("click", () => {{
              const patch = suggestions.autofill_patch || {{}};
              const field = String(button.dataset.suggestionApply || "").trim();
              if (field === "thresholds") {{
                state.createWatchAdvancedOpen = true;
                updateCreateWatchDraft({{
                  min_score: String(patch.min_score || ""),
                  min_confidence: String(patch.min_confidence || ""),
                }});
                return;
              }}
              if (!field || !(field in patch)) {{
                return;
              }}
              if (["schedule", "platform", "route", "keyword", "domain", "min_score", "min_confidence"].includes(field)) {{
                state.createWatchAdvancedOpen = true;
              }}
              updateCreateWatchDraft({{ [field]: String(patch[field] || "") }});
            }});
          }});
        }}
        wireLifecycleGuideActions(suggestionRoot);
        scheduleCanvasTextFit(suggestionRoot);
      }}

      if (feedbackRoot) {{
        if (editing) {{
          feedbackRoot.textContent = preview.requiredReady
            ? copy(
                `Editing ${{editingId}}. Use Cmd/Ctrl+Enter to save${{preview.alertArmed ? " with alert gating." : "."}}`,
                `正在编辑 ${{editingId}}。使用 Cmd/Ctrl+Enter 保存${{preview.alertArmed ? "，并带上告警门槛。" : "。"}}`,
              )
            : copy(
                `Editing ${{editingId}}. Name and Query are still required before saving.`,
                `正在编辑 ${{editingId}}。保存前仍需填写名称和查询词。`,
              );
        }} else {{
          feedbackRoot.textContent = preview.requiredReady
            ? copy(
                `Deck armed. Use Cmd/Ctrl+Enter to dispatch${{preview.alertArmed ? " with alert gating." : "."}}`,
                `草稿已就绪。使用 Cmd/Ctrl+Enter 提交${{preview.alertArmed ? "，并带上告警门槛。" : "。"}}`,
              )
            : copy("Required fields: Name and Query. Use / to focus the mission deck.", "必填字段：名称和查询词。按 / 可快速聚焦任务草稿。");
        }}
      }}

      if (stageHudRoot) {{
        stageHudRoot.innerHTML = `
          <div class="card-top">
            <div>
              <div class="mono">${{copy("Live Mission Projection", "实时任务投影")}}</div>
              <div class="stage-hud-title">${{escapeHtml(draft.name.trim() || draft.query.trim() || copy("Awaiting Mission Draft", "等待任务草稿"))}}</div>
            </div>
            <span class="chip ${{preview.requiredReady ? "ok" : ""}}">${{preview.requiredReady ? copy("synced", "已同步") : copy("draft", "草稿")}}</span>
          </div>
          <div class="stage-hud-summary">${{escapeHtml(preview.summary)}}</div>
          <div class="stage-hud-meta">
            <span class="chip">${{escapeHtml(preview.scheduleLabel)}}</span>
            <span class="chip">${{escapeHtml(preview.filtersLabel)}}</span>
            <span class="chip ${{preview.alertArmed ? "hot" : ""}}">${{preview.alertArmed ? copy("alert armed", "告警已启用") : copy("passive watch", "仅监测")}}</span>
          </div>
        `;
      }}
      renderActionHistory();
    }}

    function createWatchDraftFromMissionDetail(detail, {{ copyName = false }} = {{}}) {{
      const firstRule = Array.isArray(detail.alert_rules) && detail.alert_rules.length ? detail.alert_rules[0] : {{}};
      return {{
        name: copyName && detail.name ? `${{detail.name}} copy` : (detail.name || ""),
        schedule: detail.schedule || "",
        query: detail.query || "",
        platform: Array.isArray(detail.platforms) && detail.platforms.length ? detail.platforms[0] : "",
        domain: Array.isArray(firstRule.domains) && firstRule.domains.length ? firstRule.domains[0] : "",
        route: Array.isArray(firstRule.routes) && firstRule.routes.length ? firstRule.routes[0] : "",
        keyword: Array.isArray(firstRule.keyword_any) && firstRule.keyword_any.length ? firstRule.keyword_any[0] : "",
        min_score: firstRule.min_score ? String(firstRule.min_score) : "",
        min_confidence: firstRule.min_confidence ? String(firstRule.min_confidence) : "",
      }};
    }}

    async function editMissionInCreateWatch(identifier) {{
      if (!identifier) {{
        return;
      }}
      const detail = state.watchDetails[identifier] || await api(`/api/watches/${{identifier}}`);
      state.watchDetails[identifier] = detail;
      state.createWatchAdvancedOpen = true;
      setCreateWatchDraft(createWatchDraftFromMissionDetail(detail), "", detail.id || identifier);
      showToast(
        state.language === "zh"
          ? `已载入任务编辑：${{detail.name || identifier}}`
          : `Editing mission: ${{detail.name || identifier}}`,
        "success",
      );
      focusCreateWatchDeck("name");
    }}

    async function cloneMissionIntoCreateWatch(identifier) {{
      if (!identifier) {{
        return;
      }}
      const detail = state.watchDetails[identifier] || await api(`/api/watches/${{identifier}}`);
      state.watchDetails[identifier] = detail;
      state.createWatchAdvancedOpen = true;
      setCreateWatchDraft(createWatchDraftFromMissionDetail(detail, {{ copyName: true }}), "", "");
      showToast(
        state.language === "zh"
          ? `已从 ${{detail.name || identifier}} 克隆任务草稿`
          : `Mission deck cloned from ${{detail.name || identifier}}`,
        "success",
      );
      focusCreateWatchDeck("name");
    }}

    function bindCreateWatchDeck() {{
      const form = $("create-watch-form");
      const presetRoot = $("create-watch-presets");
      const scheduleRoot = $("create-watch-schedule-picks");
      const platformRoot = $("create-watch-platform-picks");
      const routeRoot = $("create-watch-route-picks");
      const cloneRoot = $("create-watch-clones");
      const clearButton = $("create-watch-clear");
      const advancedToggle = $("create-watch-advanced-toggle");
      if (!form) {{
        return;
      }}

      syncCreateWatchForm();
      renderCreateWatchDeck();

      form.addEventListener("input", () => {{
        state.createWatchPresetId = "";
        state.createWatchDraft = collectCreateWatchDraft(form);
        persistCreateWatchDraft();
        renderCreateWatchDeck();
        queueCreateWatchSuggestions();
      }});

      form.addEventListener("keydown", (event) => {{
        if ((event.metaKey || event.ctrlKey) && String(event.key || "").toLowerCase() === "enter") {{
          event.preventDefault();
          form.requestSubmit();
        }}
      }});

      advancedToggle?.addEventListener("click", () => {{
        state.createWatchAdvancedOpen = !isCreateWatchAdvancedOpen(state.createWatchDraft || defaultCreateWatchDraft());
        renderCreateWatchDeck();
      }});

      presetRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-preset]");
        if (!button) {{
          return;
        }}
        const preset = createWatchPresets.find((candidate) => candidate.id === button.dataset.createWatchPreset);
        if (!preset) {{
          return;
        }}
        state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
        setCreateWatchDraft(preset.values, preset.id, "");
        showToast(
          state.language === "zh"
            ? `${{preset.zhLabel || preset.label}} 已载入任务草稿`
            : `${{preset.label}} loaded into the mission deck`,
          "success",
        );
        focusCreateWatchDeck("query");
      }});

      scheduleRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-schedule]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft({{ schedule: String(button.dataset.createWatchSchedule || "") }});
      }});

      platformRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-platform]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft({{ platform: String(button.dataset.createWatchPlatform || "") }});
      }});

      routeRoot?.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-create-watch-route]");
        if (!button) {{
          return;
        }}
        state.createWatchAdvancedOpen = true;
        updateCreateWatchDraft({{ route: String(button.dataset.createWatchRoute || "") }});
      }});

      cloneRoot?.addEventListener("click", async (event) => {{
        const button = event.target.closest("[data-create-watch-clone]");
        if (!button) {{
          return;
        }}
        button.disabled = true;
        try {{
          await cloneMissionIntoCreateWatch(String(button.dataset.createWatchClone || ""));
        }} catch (error) {{
          reportError(error, copy("Clone mission", "克隆任务"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      clearButton?.addEventListener("click", () => {{
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
      }});
    }}

    function bindRouteDeck() {{
      if (!state.routeDraft) {{
        state.routeDraft = defaultRouteDraft();
      }}
      renderRouteDeck();
    }}

    function bindStoryDeck() {{
      if (!state.storyDraft) {{
        state.storyDraft = defaultStoryDraft();
      }}
      renderStoryCreateDeck();
      const storyWorkspaceModeSwitch = $("story-workspace-mode-switch");
      if (storyWorkspaceModeSwitch) {{
        storyWorkspaceModeSwitch.querySelectorAll("[data-story-workspace-mode]").forEach((button) => {{
          button.addEventListener("click", () => {{
            const nextMode = String(button.dataset.storyWorkspaceMode || "").trim().toLowerCase();
            applyStoryWorkspaceMode(nextMode, {{ persist: true, syncUrl: true }});
          }});
        }});
      }}
    }}

    function bindHeroStageMotion() {{
      const hero = $("hero-main");
      const stage = hero?.querySelector(".hero-stage");
      const visual = hero?.querySelector(".hero-visual");
      const globe = hero?.querySelector(".stage-globe");
      const leftRing = hero?.querySelector(".stage-ring-left");
      const rightRing = hero?.querySelector(".stage-ring-right");
      const leftConsole = hero?.querySelector(".stage-console-left");
      const rightConsole = hero?.querySelector(".stage-console-right");
      if (!hero || !stage || !visual || !globe || !leftRing || !rightRing || !leftConsole || !rightConsole) {{
        return;
      }}

      const reset = () => {{
        stage.style.transform = "";
        visual.style.transform = "";
        globe.style.transform = "translateX(-50%)";
        leftRing.style.transform = "";
        rightRing.style.transform = "";
        leftConsole.style.transform = "";
        rightConsole.style.transform = "";
      }};

      hero.addEventListener("pointermove", (event) => {{
        const rect = hero.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) - 0.5;
        const y = ((event.clientY - rect.top) / rect.height) - 0.5;
        stage.style.transform = `perspective(1200px) rotateX(${{-y * 6}}deg) rotateY(${{x * 7}}deg)`;
        visual.style.transform = `scale(1.05) translate(${{x * -16}}px, ${{y * -12}}px)`;
        globe.style.transform = `translate(calc(-50% + ${{x * 20}}px), ${{y * 12}}px)`;
        leftRing.style.transform = `translateX(${{x * -10}}px)`;
        rightRing.style.transform = `translateX(${{x * 10}}px)`;
        leftConsole.style.transform = `translate(${{x * -8}}px, ${{y * 6}}px)`;
        rightConsole.style.transform = `translate(${{x * 8}}px, ${{y * 6}}px)`;
      }});

      hero.addEventListener("pointerleave", reset);
      reset();
    }}

    function rerenderLanguageSensitiveViews() {{
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
    }}

    function setLanguage(nextLanguage) {{
      const normalized = String(nextLanguage || "").trim().toLowerCase() === "zh" ? "zh" : "en";
      state.language = normalized;
      safeLocalStorageSet(languageStorageKey, normalized);
      rerenderLanguageSensitiveViews();
    }}

    function bindLanguageSwitch() {{
      document.querySelectorAll("[data-lang]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const nextLanguage = String(button.dataset.lang || "").trim();
          if (!nextLanguage || nextLanguage === state.language) {{
            return;
          }}
          setLanguage(nextLanguage);
        }});
      }});
    }}

    function bindSectionJumps() {{
      document.querySelectorAll("[data-jump-target]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const targetId = String(button.dataset.jumpTarget || "").trim();
          jumpToSection(targetId);
        }});
      }});
    }}

    function bindSectionTracking() {{
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
      if (!sections.length) {{
        return;
      }}
      if ("IntersectionObserver" in window) {{
        const observer = new IntersectionObserver((entries) => {{
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((left, right) => right.intersectionRatio - left.intersectionRatio);
          if (!visible.length) {{
            return;
          }}
          const nextSectionId = normalizeSectionId(visible[0].target.id);
          if (nextSectionId === state.activeSectionId) {{
            return;
          }}
          state.activeSectionId = nextSectionId;
          renderWorkspaceModeChrome();
          renderTopbarContext();
          hydrateBoardForSection(nextSectionId).catch((error) => {{
            reportError(error, copy("Load workspace stage", "加载工作阶段"));
          }});
        }}, {{
          root: null,
          rootMargin: "-18% 0px -56% 0px",
          threshold: [0.18, 0.35, 0.55],
        }});
        sections.forEach((section) => observer.observe(section));
      }}
      window.addEventListener("hashchange", () => {{
        state.activeSectionId = normalizeSectionId(window.location.hash || state.activeSectionId);
        renderWorkspaceModeChrome();
        renderTopbarContext();
        hydrateBoardForSection(state.activeSectionId).catch((error) => {{
          reportError(error, copy("Load workspace stage", "加载工作阶段"));
        }});
      }});
    }}

    function buildCommandPaletteEntries() {{
      const entries = [
        {{
          id: "refresh",
          group: copy("system", "系统"),
          title: copy("Refresh Console", "刷新控制台"),
          subtitle: copy("Reload overview, missions, triage, stories, and ops.", "重新加载总览、任务、分诊、故事和运维视图。"),
          run: async () => {{
            await refreshBoard();
            showToast(copy("Console refreshed", "控制台已刷新"), "success");
          }},
        }},
        {{
          id: "run-due",
          group: copy("system", "系统"),
          title: copy("Run Due Missions", "执行到点任务"),
          subtitle: copy("Dispatch every mission currently due.", "立即执行当前所有到点任务。"),
          run: async () => {{
            await api("/api/watches/run-due", {{ method: "POST", payload: {{ limit: 0 }} }});
            await refreshBoard();
            showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
          }},
        }},
        {{
          id: "reset-context",
          group: copy("system", "系统"),
          title: copy("Reset Workspace Context", "重置工作上下文"),
          subtitle: copy("Clear mission, triage, story, and palette browsing context without touching drafts or saved data.", "清除任务、分诊、故事和命令面板的浏览上下文，但不影响草稿和已保存数据。"),
          run: async () => {{
            resetWorkspaceContext();
          }},
        }},
        {{
          id: "copy-context-link",
          group: copy("system", "系统"),
          title: copy("Copy Context Link", "复制当前上下文链接"),
          subtitle: copy("Copy the current deep link with section, filters, and focused records.", "复制包含当前区块、筛选条件和焦点记录的深链。"),
          run: async () => {{
            await copyCurrentContextLink();
          }},
        }},
        {{
          id: "save-current-view",
          group: copy("system", "系统"),
          title: copy("Save Current View", "保存当前视图"),
          subtitle: copy("Pin the current workspace context as a reusable saved view.", "把当前工作上下文固定成一个可复用的保存视图。"),
          run: async () => {{
            saveCurrentContextView();
          }},
        }},
        {{
          id: "save-pin-current-view",
          group: copy("system", "系统"),
          title: copy("Save + Pin Current View", "保存并固定当前视图"),
          subtitle: copy("Save the current workspace context and pin it into the top dock in one step.", "一步把当前工作上下文保存并固定到顶部坞站。"),
          run: async () => {{
            saveAndPinCurrentContextView();
          }},
        }},
        ...(state.contextLinkHistory[0]
          ? [{{
              id: "open-last-context-link",
              group: copy("system", "系统"),
              title: copy("Open Last Shared Context", "打开最近分享上下文"),
              subtitle: copy("Restore the most recently copied deep link without reloading the page.", "在不刷新页面的情况下恢复最近一次复制的深链。"),
              run: async () => {{
                restoreContextLinkHistoryEntry(0);
              }},
            }}]
          : []),
        ...(state.contextLinkHistory.length
          ? [{{
              id: "clear-context-link-history",
              group: copy("system", "系统"),
              title: copy("Clear Shared Context History", "清空分享上下文历史"),
              subtitle: copy("Remove recent shared deep links from the context lens.", "清空上下文透镜中的最近分享深链。"),
              run: async () => {{
                clearContextLinkHistory();
              }},
            }}]
          : []),
        ...(state.contextSavedViews.length
          ? state.contextSavedViews
              .map((entry, index) => normalizeContextSavedViewEntry(entry))
              .filter(Boolean)
              .slice(0, 6)
              .map((entry, index) => ({{
                id: `open-saved-context-${{index}}`,
                group: copy("system", "系统"),
                title: state.language === "zh"
                  ? `打开保存视图：${{entry.pinned ? "[已固定] " : ""}}${{entry.name}}`
                  : `Open Saved View: ${{entry.pinned ? "[Pinned] " : ""}}${{entry.name}}`,
                subtitle: entry.pinned
                  ? phrase("Pinned | {{summary}}", "已固定 | {{summary}}", {{ summary: entry.summary }})
                  : entry.summary,
                run: async () => {{
                  restoreContextSavedViewEntry(index);
                }},
              }}))
          : []),
        ...(getDefaultContextSavedView()
          ? [{{
              id: "open-default-saved-view",
              group: copy("system", "系统"),
              title: copy("Open Default Landing View", "打开默认落地视图"),
              subtitle: getDefaultContextSavedView()?.summary || copy("Restore the default saved workspace view.", "恢复默认保存工作视图。"),
              run: async () => {{
                const entry = getDefaultContextSavedView();
                if (entry) {{
                  restoreContextSavedViewByName(entry.name);
                }}
              }},
            }},
            {{
              id: "clear-default-saved-view",
              group: copy("system", "系统"),
              title: copy("Clear Default Landing View", "清除默认落地视图"),
              subtitle: copy("Stop auto-opening a saved view when the console boots without a deep link.", "控制台在没有深链时启动时，不再自动打开保存视图。"),
              run: async () => {{
                clearDefaultContextSavedView();
              }},
            }}]
          : []),
        ...(state.contextSavedViews.length
          ? [{{
              id: "clear-saved-context-views",
              group: copy("system", "系统"),
              title: copy("Clear Saved Views", "清空保存视图"),
              subtitle: copy("Remove every named saved view from the context lens.", "移除上下文透镜里的全部命名保存视图。"),
              run: async () => {{
                clearContextSavedViews();
              }},
            }}]
          : []),
        {{
          id: "focus-deck",
          group: copy("deck", "草稿"),
          title: copy("Focus Mission Deck", "聚焦任务草稿"),
          subtitle: copy("Jump to the draft deck and focus the main field.", "跳转到任务草稿区并聚焦主输入框。"),
          run: async () => {{
            focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
          }},
        }},
        {{
          id: "clear-deck",
          group: copy("deck", "草稿"),
          title: copy("Reset Mission Deck", "清空任务草稿"),
          subtitle: copy("Clear the current draft and its stored local state.", "清空当前草稿及其本地缓存。"),
          run: async () => {{
            const wasEditing = Boolean(String(state.createWatchEditingId || "").trim());
            state.createWatchAdvancedOpen = null;
            setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
            showToast(
              wasEditing
                ? copy("Mission edit cancelled", "已取消任务编辑")
                : copy("Mission deck draft cleared", "已清空任务草稿"),
              "success",
            );
          }},
        }},
        {{
          id: "focus-route-deck",
          group: copy("routes", "路由"),
          title: copy("Focus Route Deck", "聚焦路由草稿"),
          subtitle: copy("Jump to the route manager and focus the route name field.", "跳转到路由管理区并聚焦路由名称。"),
          run: async () => {{
            focusRouteDeck((state.routeDraft && state.routeDraft.name.trim()) ? "description" : "name");
          }},
        }},
        {{
          id: "clear-route-deck",
          group: copy("routes", "路由"),
          title: copy("Reset Route Deck", "清空路由草稿"),
          subtitle: copy("Clear the current route draft or exit edit mode.", "清空当前路由草稿或退出编辑模式。"),
          run: async () => {{
            const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
            state.routeAdvancedOpen = null;
            setRouteDraft(defaultRouteDraft(), "");
            showToast(
              wasEditing
                ? copy("Route edit cancelled", "已取消路由编辑")
                : copy("Route deck draft cleared", "已清空路由草稿"),
              "success",
            );
          }},
        }},
        {{
          id: "focus-story-deck",
          group: copy("stories", "故事"),
          title: copy("Focus Story Intake", "聚焦故事录入"),
          subtitle: copy("Jump to the manual story deck and start a new brief.", "跳转到手工故事草稿区，直接开始新建简报。"),
          run: async () => {{
            focusStoryDeck((state.storyDraft && state.storyDraft.title.trim()) ? "summary" : "title");
          }},
        }},
      ];
      storyViewPresetOptions.forEach((viewKey) => {{
        entries.push({{
          id: `story-view-${{viewKey}}`,
          group: copy("stories", "故事"),
          title: state.language === "zh"
            ? `切换故事视图：${{storyViewPresetLabel(viewKey)}}`
            : `Story View: ${{storyViewPresetLabel(viewKey)}}`,
          subtitle: storyViewPresetDescription(viewKey),
          run: async () => {{
            applyStoryViewPreset(viewKey, {{ jump: true, toast: true }});
          }},
        }});
      }});
      if (state.actionLog.length && state.actionLog[0].undo) {{
        const latestAction = state.actionLog[0];
        entries.unshift({{
          id: `undo-${{latestAction.id}}`,
          group: copy("actions", "操作"),
          title: state.language === "zh" ? `撤销：${{latestAction.label}}` : `Undo: ${{latestAction.label}}`,
          subtitle: latestAction.detail || copy("Reverse the latest reversible action.", "撤销最近一次可回退操作。"),
          run: async () => {{
            await latestAction.undo();
            state.actionLog = state.actionLog.filter((entry) => entry.id !== latestAction.id);
            renderActionHistory();
          }},
        }});
      }}
      state.watches.slice(0, 6).forEach((watch) => {{
        entries.push({{
          id: `watch-open-${{watch.id}}`,
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `打开任务：${{watch.name}}` : `Open Mission: ${{watch.name}}`,
          subtitle: `${{watch.query || "-"}} | ${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}`,
          run: async () => {{
            await loadWatch(watch.id);
          }},
        }});
        entries.push({{
          id: `watch-edit-${{watch.id}}`,
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `编辑任务：${{watch.name}}` : `Edit Mission: ${{watch.name}}`,
          subtitle: copy("Load this mission into the deck for in-place editing.", "把该任务载入草稿区，直接原位编辑。"),
          run: async () => {{
            await editMissionInCreateWatch(watch.id);
          }},
        }});
        entries.push({{
          id: `watch-clone-${{watch.id}}`,
          group: copy("missions", "任务"),
          title: state.language === "zh" ? `克隆任务：${{watch.name}}` : `Clone Mission: ${{watch.name}}`,
          subtitle: copy("Pull this mission into the deck as a draft fork.", "把这个任务拉进草稿区，作为分支任务继续编辑。"),
          run: async () => {{
            await cloneMissionIntoCreateWatch(watch.id);
          }},
        }});
      }});
      state.routes.slice(0, 6).forEach((route) => {{
        entries.push({{
          id: `route-edit-${{route.name}}`,
          group: copy("routes", "路由"),
          title: state.language === "zh" ? `编辑路由：${{route.name}}` : `Edit Route: ${{route.name}}`,
          subtitle: `${{routeChannelLabel(route.channel)}} | ${{summarizeRouteDestination(route)}}`,
          run: async () => {{
            await editRouteInDeck(route.name);
          }},
        }});
        entries.push({{
          id: `route-apply-${{route.name}}`,
          group: copy("routes", "路由"),
          title: state.language === "zh" ? `把路由用于任务：${{route.name}}` : `Use Route In Mission: ${{route.name}}`,
          subtitle: copy("Attach this named route to the mission intake deck.", "把这个命名路由直接带入任务草稿。"),
          run: async () => {{
            await applyRouteToMissionDraft(route.name);
          }},
        }});
      }});
      const visibleTriage = getVisibleTriageItems();
      const focusedTriageId = state.selectedTriageId || (visibleTriage[0] ? visibleTriage[0].id : "");
      const focusedTriage = focusedTriageId
        ? visibleTriage.find((item) => item.id === focusedTriageId) || state.triage.find((item) => item.id === focusedTriageId)
        : null;
      if (focusedTriage) {{
        entries.push({{
          id: `triage-story-${{focusedTriage.id}}`,
          group: copy("triage", "分诊"),
          title: state.language === "zh" ? `从分诊生成故事：${{focusedTriage.title}}` : `Create Story From Triage: ${{focusedTriage.title}}`,
          subtitle: copy("Promote the focused triage item into a story draft and jump to Story Workspace.", "把当前焦点分诊条目提升为故事草稿，并跳转到故事工作台。"),
          run: async () => {{
            await createStoryFromTriageItems([focusedTriage.id]);
          }},
        }});
        entries.push({{
          id: `triage-note-${{focusedTriage.id}}`,
          group: copy("triage", "分诊"),
          title: state.language === "zh" ? `聚焦备注：${{focusedTriage.title}}` : `Focus Note: ${{focusedTriage.title}}`,
          subtitle: copy("Jump back to the queue and place the cursor in the note composer.", "跳回分诊队列，并把光标放进备注输入框。"),
          run: async () => {{
            focusTriageNoteComposer(focusedTriage.id);
          }},
        }});
      }}
      state.stories.slice(0, 5).forEach((story) => {{
        entries.push({{
          id: `story-open-${{story.id}}`,
          group: copy("stories", "故事"),
          title: state.language === "zh" ? `打开故事：${{story.title}}` : `Open Story: ${{story.title}}`,
          subtitle: `${{localizeWord(story.status || "active")}} | ${{copy("items", "条目")}}=${{story.item_count || 0}}`,
          run: async () => {{
            await loadStory(story.id);
          }},
        }});
      }});
      return entries;
    }}

    function getCommandPaletteEntriesForQuery() {{
      const query = String(state.commandPalette.query || "").trim().toLowerCase();
      const filteredEntries = buildCommandPaletteEntries().filter((entry) => {{
        if (!query) {{
          return true;
        }}
        return [entry.group, entry.title, entry.subtitle].some((value) => String(value || "").toLowerCase().includes(query));
      }});
      if (query) {{
        return filteredEntries;
      }}
      const recentIds = uniqueValues(state.commandPalette.recentIds || []).slice(0, 8);
      if (!recentIds.length) {{
        return filteredEntries;
      }}
      const recentEntries = recentIds
        .map((entryId) => filteredEntries.find((entry) => entry.id === entryId))
        .filter(Boolean)
        .map((entry) => ({{
          ...entry,
          group: copy("recent", "最近"),
          subtitle: entry.subtitle
            ? `${{copy("from", "来自")}} ${{entry.group}} | ${{entry.subtitle}}`
            : `${{copy("from", "来自")}} ${{entry.group}}`,
        }}));
      const seen = new Set(recentEntries.map((entry) => entry.id));
      return [...recentEntries, ...filteredEntries.filter((entry) => !seen.has(entry.id))];
    }}

    async function executePaletteEntry(entry) {{
      if (!entry) {{
        return;
      }}
      closeCommandPalette();
      noteCommandPaletteRecent(entry.id);
      try {{
        await entry.run();
      }} catch (error) {{
        reportError(error, "Palette action");
      }}
    }}

    function renderCommandPalette() {{
      const backdrop = $("command-palette");
      const input = $("command-palette-input");
      const list = $("command-palette-list");
      if (!backdrop || !input || !list) {{
        return;
      }}
      backdrop.classList.toggle("open", state.commandPalette.open);
      if (!state.commandPalette.open) {{
        return;
      }}
      const entries = getCommandPaletteEntriesForQuery();
      if (state.commandPalette.selectedIndex >= entries.length) {{
        state.commandPalette.selectedIndex = Math.max(entries.length - 1, 0);
      }}
      list.innerHTML = entries.length
        ? entries.map((entry, index) => `
            <div class="palette-item ${{index === state.commandPalette.selectedIndex ? "active" : ""}}" data-palette-id="${{entry.id}}" data-palette-index="${{index}}">
              <div class="palette-kicker">${{escapeHtml(entry.group)}}</div>
              <div>${{escapeHtml(entry.title)}}</div>
              <div class="panel-sub">${{escapeHtml(entry.subtitle || "")}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No command matched the current search.", "当前搜索没有匹配到命令。")}}</div>`;
      list.querySelectorAll("[data-palette-id]").forEach((item) => {{
        item.addEventListener("mouseenter", () => {{
          state.commandPalette.selectedIndex = Number(item.dataset.paletteIndex || 0);
          renderCommandPalette();
        }});
        item.addEventListener("click", async () => {{
          const entry = entries.find((candidate) => candidate.id === item.dataset.paletteId);
          await executePaletteEntry(entry);
        }});
      }});
      input.value = state.commandPalette.query;
    }}

    function openCommandPalette() {{
      setContextLensOpen(false);
      state.commandPalette.open = true;
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
      window.setTimeout(() => $("command-palette-input")?.focus(), 10);
    }}

    function closeCommandPalette() {{
      state.commandPalette.open = false;
      state.commandPalette.selectedIndex = 0;
      renderCommandPalette();
    }}

    function bindContextLens() {{
      const summary = $("context-summary");
      const lens = $("context-lens");
      const backdrop = $("context-lens-backdrop");
      const dialog = $("context-lens-shell");
      const saveForm = $("context-save-form");
      const saveInput = $("context-save-name");
      if (!summary || !lens || !backdrop || !dialog) {{
        return;
      }}
      summary.addEventListener("click", (event) => {{
        event.stopPropagation();
        state.contextLensRestoreFocusId = "context-summary";
        toggleContextLens();
      }});
      backdrop.addEventListener("click", (event) => {{
        if (event.target === backdrop) {{
          setContextLensOpen(false);
        }}
      }});
      dialog.addEventListener("keydown", (event) => {{
        if (String(event.key || "") !== "Tab" || !state.contextLensOpen) {{
          return;
        }}
        const focusable = getContextLensFocusableElements();
        if (!focusable.length) {{
          event.preventDefault();
          dialog.focus();
          return;
        }}
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (event.shiftKey && (active === first || active === dialog)) {{
          event.preventDefault();
          last.focus();
          return;
        }}
        if (!event.shiftKey && active === last) {{
          event.preventDefault();
          first.focus();
        }}
      }});
      saveForm?.addEventListener("submit", (event) => {{
        event.preventDefault();
        saveCurrentContextView(saveInput?.value || "");
      }});
      $("context-lens-close")?.addEventListener("click", () => {{
        setContextLensOpen(false);
      }});
      $("context-open-section")?.addEventListener("click", () => {{
        setContextLensOpen(false);
        jumpToSection(state.activeSectionId);
      }});
      $("context-copy-link")?.addEventListener("click", async () => {{
        await copyCurrentContextLink();
        setContextLensOpen(false);
      }});
    }}

    function bindCommandPalette() {{
      const backdrop = $("command-palette");
      const input = $("command-palette-input");
      if (!backdrop || !input) {{
        return;
      }}
      backdrop.addEventListener("click", (event) => {{
        if (event.target === backdrop) {{
          closeCommandPalette();
        }}
      }});
      input.addEventListener("input", () => {{
        state.commandPalette.query = input.value;
        state.commandPalette.selectedIndex = 0;
        persistCommandPaletteQuery();
        renderCommandPalette();
      }});
      input.addEventListener("keydown", async (event) => {{
        const list = getCommandPaletteEntriesForQuery();
        if (event.key === "ArrowDown") {{
          event.preventDefault();
          state.commandPalette.selectedIndex = Math.min(state.commandPalette.selectedIndex + 1, Math.max(list.length - 1, 0));
          renderCommandPalette();
        }} else if (event.key === "ArrowUp") {{
          event.preventDefault();
          state.commandPalette.selectedIndex = Math.max(state.commandPalette.selectedIndex - 1, 0);
          renderCommandPalette();
        }} else if (event.key === "Enter") {{
          event.preventDefault();
          const entry = list[state.commandPalette.selectedIndex];
          await executePaletteEntry(entry);
        }} else if (event.key === "Escape") {{
          event.preventDefault();
          closeCommandPalette();
        }}
      }});
    }}

    state.createWatchDraft = loadCreateWatchDraft();

    function metricCard(label, value, tone = "") {{
      return `<div class="metric"><div class="metric-label">${{label}}</div><div class="metric-value ${{tone}}">${{value}}</div></div>`;
    }}

    function formatRate(value) {{
      if (value === null || value === undefined || Number.isNaN(Number(value))) {{
        return "-";
      }}
      return `${{Math.round(Number(value) * 100)}}%`;
    }}

    function skeletonCard(lines = 3) {{
      return `
        <div class="card skeleton">
          <div class="stack">
            ${{Array.from({{ length: lines }}).map((_, index) => `
              <div class="skeleton-block ${{index === 0 ? "short" : index === lines - 1 ? "long" : "medium"}}"></div>
            `).join("")}}
          </div>
        </div>
      `;
    }}

    function renderActionHistory() {{
      const root = $("console-action-history");
      if (!root) {{
        return;
      }}
      if (!state.actionLog.length) {{
        root.innerHTML = `<div class="empty">${{copy("No reversible action yet. Create, tune, or triage something and it will show up here.", "当前还没有可回退的操作。创建、调整或分诊后，会在这里显示。")}}</div>`;
        return;
      }}
      root.innerHTML = state.actionLog.slice(0, 6).map((entry) => `
        <div class="action-log-item">
          <div class="card-top">
            <div>
              <div class="mono">${{escapeHtml(entry.kind || "action")}}</div>
              <div>${{escapeHtml(entry.label || "")}}</div>
            </div>
            <span class="chip ${{entry.status === "error" ? "hot" : entry.status === "ready" ? "ok" : ""}}">${{escapeHtml(localizeWord(entry.status || "done"))}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(entry.detail || "")}}</div>
          <div class="actions">
            ${{
              entry.undo
                ? `<button class="btn-secondary" type="button" data-action-undo="${{entry.id}}">${{escapeHtml(entry.undoLabel || copy("Undo", "撤销"))}}</button>`
                : ""
            }}
          </div>
        </div>
      `).join("");
      root.querySelectorAll("[data-action-undo]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const item = state.actionLog.find((entry) => entry.id === button.dataset.actionUndo);
          if (!item || !item.undo) {{
            return;
          }}
          button.disabled = true;
          try {{
            await item.undo();
            state.actionLog = state.actionLog.filter((entry) => entry.id !== item.id);
            renderActionHistory();
          }} catch (error) {{
            reportError(error, "Undo action");
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function pushActionEntry(entry) {{
      state.actionLog = [{{
        id: `action-${{Date.now()}}-${{Math.random().toString(16).slice(2, 8)}}`,
        timestamp: new Date().toISOString(),
        status: "ready",
        ...entry,
      }}, ...state.actionLog].slice(0, 8);
      renderActionHistory();
    }}

    function updateActionEntry(entryId, patch = {{}}) {{
      if (!entryId) {{
        return;
      }}
      let changed = false;
      state.actionLog = state.actionLog.map((entry) => {{
        if (entry.id !== entryId) {{
          return entry;
        }}
        changed = true;
        return {{
          ...entry,
          ...patch,
        }};
      }});
      if (changed) {{
        renderActionHistory();
      }}
    }}

    function buildAlertRules({{ route = "", keyword = "", domain = "", minScore = 0, minConfidence = 0 }}) {{
      const cleanedRoute = String(route || "").trim();
      const cleanedKeyword = String(keyword || "").trim();
      const cleanedDomain = String(domain || "").trim();
      const scoreValue = Math.max(0, Number(minScore || 0));
      const confidenceValue = Math.max(0, Number(minConfidence || 0));
      if (!(cleanedRoute || cleanedKeyword || cleanedDomain || scoreValue > 0 || confidenceValue > 0)) {{
        return [];
      }}
      const alertRule = {{
        name: "console-threshold",
        min_score: scoreValue,
        min_confidence: confidenceValue,
        channels: ["json"],
      }};
      if (cleanedRoute) alertRule.routes = [cleanedRoute];
      if (cleanedKeyword) alertRule.keyword_any = [cleanedKeyword];
      if (cleanedDomain) alertRule.domains = [cleanedDomain];
      return [alertRule];
    }}

    function renderLifecycleGuideCard({{ title = "", summary = "", steps = [], actions = [], tone = "ok" }} = {{}}) {{
      const stepsHtml = steps.map((step, index) => `
        <div class="guide-card">
          <div class="guide-step">${{String(index + 1).padStart(2, "0")}}</div>
          <div class="mono">${{escapeHtml(step.title || "")}}</div>
          <div class="panel-sub">${{escapeHtml(step.copy || "")}}</div>
        </div>
      `).join("");
      const actionsHtml = actions.length
        ? `<div class="actions" style="margin-top:14px;">${{actions.map((action) => `
            <button
              class="${{action.primary ? "btn-primary" : "btn-secondary"}}"
              type="button"
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
              ${{action.watch ? `data-empty-watch="${{escapeHtml(action.watch)}}"` : ""}}
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
              ${{action.toggleWatch ? `data-watch-toggle="${{escapeHtml(action.toggleWatch)}}"` : ""}}
              ${{action.watchEnabled ? `data-watch-enabled="${{escapeHtml(action.watchEnabled)}}"` : ""}}
            >${{escapeHtml(action.label || "")}}</button>
          `).join("")}}</div>`
        : "";
      return `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("lifecycle guide", "生命周期引导")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title)}}</h3>
            </div>
            <span class="chip ${{tone}}">${{copy("browser-first", "浏览器优先")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          <div class="guide-grid" style="margin-top:14px;">${{stepsHtml}}</div>
          ${{actionsHtml}}
        </div>
      `;
    }}

    function getWatchRecord(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return null;
      }}
      return state.watchDetails[normalized] || state.watches.find((watch) => watch.id === normalized) || null;
    }}

    async function triggerWatchRun(identifier) {{
      const normalized = String(identifier || "").trim();
      if (!normalized) {{
        return;
      }}
      const watch = getWatchRecord(normalized);
      if (watch && watch.enabled === false) {{
        setStageFeedback("monitor", {{
          kind: "blocked",
          title: copy("Mission is paused and cannot run yet", "任务已暂停，当前无法执行"),
          copy: copy("Enable the selected mission first, then rerun it from the monitoring lane.", "请先在监测阶段重新启用该任务，再发起执行。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Enable Mission", "启用任务"),
              attrs: {{ "data-watch-toggle": normalized, "data-watch-enabled": "0" }},
            }},
            secondary: [
              {{
                label: copy("Open Mission Board", "打开任务列表"),
                attrs: {{ "data-empty-jump": "section-board" }},
              }},
            ],
          }},
        }});
        showToast(copy("Mission is paused. Enable it before running.", "任务已停用，请先启用后再执行。"), "error");
        return;
      }}
      const watchLabel = String((watch && (watch.name || watch.id)) || normalized).trim() || normalized;
      const actionId = `mission-run-${{normalized}}-${{Date.now()}}`;
      pushActionEntry({{
        id: actionId,
        status: "pending",
        kind: copy("mission run", "任务执行"),
        label: state.language === "zh" ? `执行中：${{watchLabel}}` : `Running: ${{watchLabel}}`,
        detail: copy("Fetching sources and waiting for mission results.", "正在抓取来源并等待任务结果返回。"),
      }});
      showToast(
        state.language === "zh" ? `任务开始执行：${{watchLabel}}` : `Mission started: ${{watchLabel}}`,
        "info",
      );
      try {{
        const payload = await api(`/api/watches/${{normalized}}/run`, {{ method: "POST" }});
        const run = payload && typeof payload === "object" && payload.run && typeof payload.run === "object" ? payload.run : {{}};
        const items = Array.isArray(payload?.items) ? payload.items : [];
        const alertEvents = Array.isArray(payload?.alert_events) ? payload.alert_events : [];
        const itemCount = items.length || Number(run.item_count || 0);
        const alertCount = alertEvents.length;
        const outcomeDetail = itemCount > 0
          ? state.language === "zh"
            ? `执行完成，返回 ${{itemCount}} 条结果${{alertCount ? `，触发 ${{alertCount}} 条告警` : ""}}。`
            : `Run finished with ${{itemCount}} result(s)${{alertCount ? ` and ${{alertCount}} alert event(s)` : ""}}.`
          : state.language === "zh"
            ? "执行完成，但没有返回结果。可调整查询词、平台或阈值后重试。"
            : "Run finished with no results. Adjust the query, platform, or thresholds and try again.";
        updateActionEntry(actionId, {{
          status: "ready",
          label: state.language === "zh" ? `任务完成：${{watchLabel}}` : `Mission completed: ${{watchLabel}}`,
          detail: outcomeDetail,
        }});
        await refreshBoard();
        setStageFeedback("monitor", itemCount > 0
          ? {{
              kind: "completion",
              title: state.language === "zh"
                ? `任务已完成并返回 ${{itemCount}} 条结果`
                : `Mission completed with ${{itemCount}} result(s)`,
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
                {{ label: copy("Results", "结果数"), value: String(itemCount) }},
                {{ label: copy("Alerts", "告警数"), value: String(alertCount) }},
              ],
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Triage", "打开分诊"),
                  attrs: {{ "data-empty-jump": "section-triage" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Cockpit", "打开任务详情"),
                    attrs: {{ "data-empty-jump": "section-cockpit" }},
                  }},
                ],
              }},
            }}
          : {{
              kind: "no_result",
              title: copy("Mission completed with no results", "任务执行完成，但没有结果"),
              copy: copy(
                "The mission finished, but the current query, platform, or thresholds did not return usable evidence. Adjust the draft, then rerun it.",
                "任务已经执行完成，但当前查询词、平台或阈值没有返回可用证据。请调整草稿后再重跑。"
              ),
              facts: [
                {{ label: copy("Mission", "任务"), value: watchLabel }},
                {{ label: copy("Alerts", "告警数"), value: String(alertCount) }},
              ],
              actionHierarchy: {{
                primary: {{
                  label: copy("Edit Mission Draft", "编辑任务草稿"),
                  attrs: {{ "data-empty-focus": "mission", "data-empty-field": "query" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Cockpit", "打开任务详情"),
                    attrs: {{ "data-empty-jump": "section-cockpit" }},
                  }},
                ],
              }},
            }});
        showToast(
          itemCount > 0
            ? (state.language === "zh" ? `任务完成：${{itemCount}} 条结果` : `Mission completed: ${{itemCount}} result(s)`)
            : copy("Mission completed with no results.", "任务执行完成，但没有结果。"),
          itemCount > 0 ? "success" : "info",
        );
        return payload;
      }} catch (error) {{
        const message = error && error.message ? error.message : String(error || "Unknown error");
        updateActionEntry(actionId, {{
          status: "error",
          label: state.language === "zh" ? `任务失败：${{watchLabel}}` : `Mission failed: ${{watchLabel}}`,
          detail: message,
        }});
        setStageFeedback("monitor", {{
          kind: "blocked",
          title: state.language === "zh" ? `任务执行失败：${{watchLabel}}` : `Mission failed: ${{watchLabel}}`,
          copy: message,
          actionHierarchy: {{
            primary: {{
              label: copy("Open Cockpit", "打开任务详情"),
              attrs: {{ "data-empty-jump": "section-cockpit" }},
            }},
            secondary: [
              {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            ],
          }},
        }});
        throw error;
      }}
    }}

    async function handleWatchToggle(button) {{
      const identifier = String(button?.dataset?.watchToggle || "").trim();
      if (!identifier) {{
        return;
      }}
      const isEnabled = String(button.dataset.watchEnabled || "1") === "1";
      const previousWatch = state.watches.find((watch) => watch.id === identifier);
      const previousDetail = state.watchDetails[identifier] ? {{ ...state.watchDetails[identifier] }} : null;
      button.disabled = true;
      if (previousWatch) {{
        previousWatch.enabled = !isEnabled;
      }}
      if (state.watchDetails[identifier]) {{
        state.watchDetails[identifier].enabled = !isEnabled;
      }}
      renderWatches();
      renderWatchDetail();
      try {{
        await api(`/api/watches/${{identifier}}/${{isEnabled ? "disable" : "enable"}}`, {{ method: "POST" }});
        pushActionEntry({{
          kind: "mission state",
          label: `${{isEnabled ? "Disabled" : "Enabled"}} ${{previousWatch && previousWatch.name ? previousWatch.name : identifier}}`,
          detail: `${{identifier}} switched to ${{isEnabled ? "disabled" : "enabled"}}.`,
          undoLabel: isEnabled ? "Re-enable" : "Disable again",
          undo: async () => {{
            await api(`/api/watches/${{identifier}}/${{isEnabled ? "enable" : "disable"}}`, {{ method: "POST" }});
            await refreshBoard();
            showToast(`Mission ${{isEnabled ? "re-enabled" : "disabled"}}: ${{identifier}}`, "success");
          }},
        }});
        await refreshBoard();
        setStageFeedback("monitor", isEnabled
          ? {{
              kind: "warning",
              title: state.language === "zh" ? `任务已暂停：${{identifier}}` : `Mission paused: ${{identifier}}`,
              copy: copy(
                "The mission now stays out of monitoring until it is enabled again.",
                "这条任务会从监测阶段暂停，直到再次被启用。"
              ),
              actionHierarchy: {{
                primary: {{
                  label: copy("Enable Mission", "启用任务"),
                  attrs: {{ "data-watch-toggle": identifier, "data-watch-enabled": "0" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Mission Board", "打开任务列表"),
                    attrs: {{ "data-empty-jump": "section-board" }},
                  }},
                ],
              }},
            }}
          : {{
              kind: "completion",
              title: state.language === "zh" ? `任务已启用：${{identifier}}` : `Mission enabled: ${{identifier}}`,
              copy: copy(
                "The mission is back in the monitoring lane and can be run immediately.",
                "这条任务已经重新回到监测阶段，现在可以立即执行。"
              ),
              actionHierarchy: {{
                primary: {{
                  label: copy("Run Mission", "执行任务"),
                  attrs: {{ "data-empty-run-watch": identifier }},
                }},
                secondary: [
                  {{
                    label: copy("Open Cockpit", "打开任务详情"),
                    attrs: {{ "data-empty-jump": "section-cockpit" }},
                  }},
                ],
              }},
            }});
      }} catch (error) {{
        if (previousWatch) {{
          previousWatch.enabled = isEnabled;
        }}
        if (previousDetail) {{
          state.watchDetails[identifier] = previousDetail;
        }}
        renderWatches();
        renderWatchDetail();
        reportError(error, `${{isEnabled ? "Disable" : "Enable"}} mission`);
      }} finally {{
        button.disabled = false;
      }}
    }}

    function bindWatchToggleButtons(root) {{
      if (!root) {{
        return;
      }}
      root.querySelectorAll("[data-watch-toggle]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await handleWatchToggle(button);
        }});
      }});
    }}

    function wireLifecycleGuideActions(root) {{
      if (!root) {{
        return;
      }}
      root.querySelectorAll("[data-empty-jump]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const requestedMode = normalizeStoryWorkspaceMode(button.dataset.storyWorkspaceMode || "");
          if (requestedMode) {{
            applyStoryWorkspaceMode(requestedMode, {{ persist: true, syncUrl: true }});
          }}
          const section = String(button.dataset.emptyJump || "").trim();
          if (section) {{
            jumpToSection(section);
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-focus]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const focus = String(button.dataset.emptyFocus || "").trim();
          const field = String(button.dataset.emptyField || "").trim();
          if (focus === "mission") {{
            focusCreateWatchDeck(field || "name");
          }} else if (focus === "story") {{
            focusStoryDeck(field || "title");
          }} else if (focus === "route") {{
            focusRouteDeck(field || "name");
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-reset]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const target = String(button.dataset.emptyReset || "").trim();
          if (target === "mission") {{
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
          }} else if (target === "route") {{
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
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.emptyWatch || "").trim();
          if (!identifier) {{
            return;
          }}
          button.disabled = true;
          try {{
            await loadWatch(identifier);
          }} catch (error) {{
            reportError(error, copy("Open mission", "打开任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-empty-run-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.emptyRunWatch || "").trim();
          if (!identifier) {{
            return;
          }}
          button.disabled = true;
          try {{
            await triggerWatchRun(identifier);
          }} catch (error) {{
            reportError(error, copy("Run mission", "执行任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      bindWatchToggleButtons(root);
    }}

    function getGovernanceSignals() {{
      const scorecard = state.ops?.governance_scorecard;
      return scorecard && typeof scorecard.signals === "object" ? scorecard.signals : {{}};
    }}

    function getGovernanceSignal(signalId) {{
      const signal = getGovernanceSignals()[signalId];
      return signal && typeof signal === "object" ? signal : {{}};
    }}

    function getAiSurfacePrecheck(surfaceId) {{
      const payload = state.aiSurfacePrechecks?.[surfaceId];
      return payload && typeof payload === "object" ? payload : {{}};
    }}

    function getAiSurfaceProjection(surfaceId) {{
      const payload = state.aiSurfaceProjections?.[surfaceId];
      return payload && typeof payload === "object" ? payload : null;
    }}

    function summarizeAiSurfaceProjection(surfaceId, projection) {{
      if (!projection || typeof projection !== "object") {{
        return copy("No selected subject is loaded for this surface yet.", "这个 surface 还没有加载选中的对象。");
      }}
      const runtime = projection.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {{}};
      const output = projection.output && typeof projection.output === "object" ? projection.output : null;
      const payload = output && output.payload && typeof output.payload === "object" ? output.payload : {{}};
      if (surfaceId === "mission_suggest" && payload.summary) {{
        return String(payload.summary);
      }}
      if (surfaceId === "triage_assist") {{
        const candidateCount = payload.candidate_count ?? payload.returned_count;
        if (candidateCount !== undefined) {{
          return state.language === "zh"
            ? `重复解释候选数：${{candidateCount}}。`
            : `Duplicate explain candidates: ${{candidateCount}}.`;
        }}
      }}
      if (surfaceId === "claim_draft") {{
        if (payload.summary) {{
          return String(payload.summary);
        }}
        const claimCount = Array.isArray(payload.claim_cards) ? payload.claim_cards.length : 0;
        return state.language === "zh"
          ? `待审核主张卡：${{claimCount}} 条。`
          : `Claim cards ready for review: ${{claimCount}}.`;
      }}
      if (runtime.status) {{
        return state.language === "zh"
          ? `运行状态：${{localizeWord(runtime.status)}}。`
          : `Runtime status: ${{runtime.status}}.`;
      }}
      return copy("Governed projection loaded.", "治理投影已加载。");
    }}

    function getStoryEvidenceIds(story) {{
      return uniqueValues([
        story?.primary_item_id,
        ...(Array.isArray(story?.primary_evidence) ? story.primary_evidence.map((row) => row.item_id) : []),
        ...(Array.isArray(story?.secondary_evidence) ? story.secondary_evidence.map((row) => row.item_id) : []),
      ]);
    }}

    function getStoriesForEvidenceItem(itemId) {{
      const normalizedId = String(itemId || "").trim();
      if (!normalizedId) {{
        return [];
      }}
      return state.stories.filter((story) => getStoryEvidenceIds(story).includes(normalizedId));
    }}

    function getStoryDeliveryStatus(story) {{
      const governance = story && typeof story.governance === "object" ? story.governance : {{}};
      const deliveryRisk = governance && typeof governance.delivery_risk === "object" ? governance.delivery_risk : {{}};
      const rawStatus = String(deliveryRisk.status || "").trim().toLowerCase();
      if (rawStatus === "ready") {{
        return {{ key: "ready", label: copy("Ready", "已就绪"), tone: "ok" }};
      }}
      if (rawStatus === "blocked") {{
        return {{ key: "blocked", label: copy("Blocked", "已阻塞"), tone: "hot" }};
      }}
      if (rawStatus) {{
        return {{ key: rawStatus, label: localizeWord(rawStatus), tone: rawStatus === "watch" ? "hot" : "" }};
      }}
      return {{ key: "pending", label: copy("Not assessed", "未评估"), tone: "" }};
    }}

    function signalToneFromStatus(status = "") {{
      const normalized = String(status || "").trim().toLowerCase();
      if (["ok", "ready", "healthy", "clear", "completed", "delivered"].includes(normalized)) {{
        return "ok";
      }}
      if (["watch", "warning", "blocked", "error", "fail", "failed", "degraded", "no_result"].includes(normalized)) {{
        return "hot";
      }}
      return "";
    }}

    function traceStageStatusLabel(status = "") {{
      const normalized = String(status || "").trim().toLowerCase() || "pending";
      const labels = {{
        ready: copy("ready", "已就绪"),
        ok: copy("ok", "正常"),
        watch: copy("watch", "关注"),
        warning: copy("warning", "警告"),
        blocked: copy("blocked", "阻塞"),
        no_result: copy("no result", "无结果"),
        pending: copy("pending", "待推进"),
        delivered: copy("delivered", "已送达"),
      }};
      return labels[normalized] || localizeWord(normalized);
    }}

    function buildStageLinkedTrace() {{
      const watch = getSelectedWatchForContext() || state.watches[0] || null;
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      const recentRuns = Array.isArray(watch?.runs) ? watch.runs : [];
      const latestRun = recentRuns[0] || null;
      const recentAlerts = Array.isArray(watch?.recent_alerts) ? watch.recent_alerts : [];
      const resultStats = watch?.result_stats || {{}};
      const storedResults = Number(resultStats.stored_result_count || resultStats.returned_result_count || 0);
      const selectedTriage = state.triage.find((item) => String(item.id || "").trim() === String(state.selectedTriageId || "").trim()) || null;
      const selectedStory = getStoryRecord(state.selectedStoryId);
      const selectedReport = getSelectedReportRecord();
      const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
      const routeSummary = state.ops?.route_summary || {{}};
      const routeTimeline = Array.isArray(state.ops?.route_timeline) ? state.ops.route_timeline : [];
      const storySignal = getGovernanceSignal("story_conversion");
      const triageSignal = getGovernanceSignal("triage_throughput");
      const readyStories = Number(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0);
      const openQueue = Number(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0);
      const contradictionCount = Array.isArray(selectedStory?.contradictions) ? selectedStory.contradictions.length : 0;
      const selectedStoryEvidenceCount = Number(selectedStory?.item_count || 0);

      const startStage = watch
        ? {{
            id: "start",
            status: "ready",
            title: String(watch.name || watch.id || copy("Mission anchor", "任务锚点")),
            summary: copy(
              "The current trace is anchored to the selected mission and its latest workflow trigger.",
              "当前 trace 以选中的任务及其最近一次流程触发为锚点。"
            ),
            facts: [
              {{ label: copy("Subject", "主体"), value: String(watch.id || watch.name || "") }},
              {{ label: copy("Trigger", "触发方式"), value: localizeWord(latestRun?.trigger || watch.schedule_label || watch.schedule || "manual") }},
              {{ label: copy("Started", "开始时间"), value: formatCompactDateTime(latestRun?.started_at || watch.last_run_at || "") }},
            ],
          }}
        : {{
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
              {{ label: copy("Name", "名称"), value: draft.name || copy("unset", "未设置") }},
              {{ label: copy("Query", "查询词"), value: clampLabel(draft.query || copy("unset", "未设置"), 28) }},
              {{ label: copy("Route", "路由"), value: draft.route || copy("not attached", "未绑定") }},
            ],
          }};

      let monitorStage = null;
      if (latestRun && String(latestRun.status || "").trim().toLowerCase() === "error") {{
        monitorStage = {{
          id: "monitor",
          status: "blocked",
          title: copy("Run failed before output stabilized", "执行在输出稳定前失败"),
          summary: latestRun.error || copy("The latest run failed and still needs operator retry guidance.", "最近一次执行失败，仍需要操作者根据重试建议处理。"),
          facts: [
            {{ label: copy("Run", "执行"), value: String(latestRun.id || "-") }},
            {{ label: copy("Status", "状态"), value: localizeWord(latestRun.status || "error") }},
            {{ label: copy("Results", "结果"), value: String(latestRun.item_count || 0) }},
          ],
        }};
      }} else if (watch && (latestRun || watch.last_run_at) && (storedResults > 0 || Number(latestRun?.item_count || 0) > 0)) {{
        monitorStage = {{
          id: "monitor",
          status: "ready",
          title: copy("Run output is inspectable", "执行输出已可检查"),
          summary: copy(
            "Monitoring now exposes a concrete run outcome and stored result count without forcing operators into raw logs.",
            "监测阶段现在直接暴露明确的执行结果和存储结果数，不需要操作者回到原始日志里重建上下文。"
          ),
          facts: [
            {{ label: copy("Outcome", "结果"), value: localizeWord(latestRun?.status || watch.last_run_status || "success") }},
            {{ label: copy("Stored results", "已存储结果"), value: String(storedResults || latestRun?.item_count || 0) }},
            {{ label: copy("Finished", "结束时间"), value: formatCompactDateTime(latestRun?.finished_at || watch.last_run_at || "") }},
          ],
        }};
      }} else if (watch && (latestRun || watch.last_run_at)) {{
        monitorStage = {{
          id: "monitor",
          status: "no_result",
          title: copy("Mission completed with no results", "任务执行完成但没有结果"),
          summary: copy(
            "The latest run finished, but it did not leave behind any stored result for review.",
            "最近一次执行已经结束，但没有留下可供审阅的存储结果。"
          ),
          facts: [
            {{ label: copy("Outcome", "结果"), value: localizeWord(latestRun?.status || watch.last_run_status || "success") }},
            {{ label: copy("Stored results", "已存储结果"), value: "0" }},
            {{ label: copy("Finished", "结束时间"), value: formatCompactDateTime(latestRun?.finished_at || watch.last_run_at || "") }},
          ],
        }};
      }} else if (watch) {{
        monitorStage = {{
          id: "monitor",
          status: watch.enabled ? "pending" : "blocked",
          title: watch.enabled
            ? copy("Mission has not run yet", "任务尚未开始执行")
            : copy("Mission is paused before monitoring", "任务在监测前已暂停"),
          summary: watch.enabled
            ? copy("One run is still required before output, review, or delivery facts can appear.", "还需要先执行一次，输出、审阅和交付事实才会开始出现。")
            : copy("Enable the mission first so monitoring facts can start moving again.", "请先启用任务，再让监测事实重新流动起来。"),
          facts: [
            {{ label: copy("Mission", "任务"), value: String(watch.name || watch.id || "") }},
            {{ label: copy("Status", "状态"), value: watch.enabled ? copy("ready to run", "待执行") : copy("paused", "已暂停") }},
            {{ label: copy("Schedule", "频率"), value: String(watch.schedule_label || watch.schedule || "manual") }},
          ],
        }};
      }} else {{
        monitorStage = {{
          id: "monitor",
          status: "pending",
          title: copy("Monitoring starts after mission creation", "创建任务后才会进入监测"),
          summary: copy("Create or select one mission before run output can be traced.", "先创建或选中一条任务，执行输出才有可追踪的起点。"),
          facts: [
            {{ label: copy("Mission", "任务"), value: copy("not selected", "未选择") }},
            {{ label: copy("Stored results", "已存储结果"), value: "0" }},
            {{ label: copy("Run state", "执行状态"), value: copy("not started", "未开始") }},
          ],
        }};
      }}

      let reviewStage = null;
      if (selectedQuality) {{
        const qualityStatus = String(selectedQuality.status || "draft").trim().toLowerCase();
        reviewStage = {{
          id: "review",
          status: selectedQuality.can_export ? "ready" : (qualityStatus === "review_required" ? "watch" : qualityStatus || "blocked"),
          title: selectedReport?.title || copy("Report quality guardrails", "报告质量门禁"),
          summary: selectedQuality.can_export
            ? copy("Review has already produced an export-ready report quality snapshot.", "审阅阶段已经产出可导出的报告质量快照。")
            : copy("Review is still holding on report guardrails before this output should be treated as ready.", "在把当前输出视为就绪之前，审阅阶段仍然被报告质量门禁卡住。"),
          facts: [
            {{ label: copy("Quality", "质量"), value: localizeWord(selectedQuality.status || "draft") }},
            {{ label: copy("Score", "分数"), value: Number(selectedQuality.score || 0).toFixed(2) }},
            {{ label: copy("Action", "动作"), value: formatReportOperatorAction(selectedQuality.operator_action || "") }},
          ],
        }};
      }} else if (selectedStory) {{
        const deliveryStatus = getStoryDeliveryStatus(selectedStory);
        reviewStage = {{
          id: "review",
          status: contradictionCount ? "blocked" : (selectedStoryEvidenceCount ? "ready" : "watch"),
          title: String(selectedStory.title || selectedStory.id || copy("Story review", "故事审阅")),
          summary: contradictionCount
            ? copy("Review already promoted signal into a story, but contradiction markers still need resolution.", "审阅阶段已经把信号提升成故事，但冲突标记仍然需要先处理。")
            : copy("Review has already linked evidence to a persisted story object.", "审阅阶段已经把证据连接到持久化故事对象。"),
          facts: [
            {{ label: copy("Story", "故事"), value: localizeWord(selectedStory.status || "active") }},
            {{ label: copy("Evidence", "证据"), value: String(selectedStoryEvidenceCount) }},
            {{ label: copy("Contradictions", "冲突"), value: String(contradictionCount) }},
          ],
        }};
      }} else if (selectedTriage) {{
        const linkedStories = getStoriesForEvidenceItem(selectedTriage.id);
        reviewStage = {{
          id: "review",
          status: linkedStories.length || String(selectedTriage.review_state || "").trim().toLowerCase() === "verified" ? "ready" : "watch",
          title: String(selectedTriage.title || selectedTriage.id || copy("Selected evidence", "当前证据")),
          summary: linkedStories.length
            ? copy("Review has already linked the selected evidence to downstream story work.", "审阅阶段已经把当前证据连接到下游故事工作。")
            : copy("The selected evidence is in review, but it still needs a verify-or-promote decision.", "当前证据已经进入审阅，但仍需要一个核验或提升决定。"),
          facts: [
            {{ label: copy("Disposition", "处置"), value: localizeWord(selectedTriage.review_state || "new") }},
            {{ label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) }},
            {{ label: copy("Open queue", "开放队列"), value: String(openQueue) }},
          ],
        }};
      }} else {{
        reviewStage = {{
          id: "review",
          status: openQueue > 0 || readyStories > 0 ? "watch" : "pending",
          title: copy("Review lane status", "审阅阶段状态"),
          summary: openQueue > 0
            ? copy("Review still owns open queue pressure before the flow can move cleanly toward delivery.", "在流程顺畅进入交付之前，审阅阶段仍然背着开放队列压力。")
            : copy("No active review object is selected right now, but the review lane remains the next promotion owner.", "当前没有选中激活中的审阅对象，但审阅阶段仍然是下一个负责提升的所有者。"),
          facts: [
            {{ label: copy("Open queue", "开放队列"), value: String(openQueue) }},
            {{ label: copy("Acted on", "已处理"), value: String(state.overview?.triage_acted_on_count ?? triageSignal.acted_on_items ?? 0) }},
            {{ label: copy("Ready stories", "待交付故事"), value: String(readyStories) }},
          ],
        }};
      }}

      let deliverStage = null;
      if ((routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0) {{
        deliverStage = {{
          id: "deliver",
          status: "blocked",
          title: copy("Delivery stopped on route health", "交付因路由健康问题停止"),
          summary: copy("Route health is currently the explicit stop reason before this flow can be trusted downstream again.", "路由健康当前是这条流程无法继续被下游信任的明确停止原因。"),
          facts: [
            {{ label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) }},
            {{ label: copy("Missing", "缺失"), value: String(routeSummary.missing || 0) }},
            {{ label: copy("Routes", "路由"), value: String(routeSummary.total || state.routes.length || 0) }},
          ],
        }};
      }} else if (routeTimeline.length || recentAlerts.length || state.deliveryDispatchRecords.length) {{
        const latestRouteEvent = routeTimeline[0] || null;
        const latestAlert = recentAlerts[0] || null;
        deliverStage = {{
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
            {{ label: copy("Route", "路由"), value: String(latestRouteEvent?.route || "-") }},
            {{ label: copy("Outcome", "结果"), value: localizeWord(latestRouteEvent?.status || "delivered") }},
            {{ label: copy("Last event", "最近事件"), value: formatCompactDateTime(latestRouteEvent?.created_at || latestAlert?.created_at || "") }},
          ],
        }};
      }} else if (readyStories > 0 && state.routes.length) {{
        deliverStage = {{
          id: "deliver",
          status: "watch",
          title: copy("Ready output is waiting for dispatch", "就绪输出正在等待分发"),
          summary: copy("Review has already produced ready output, but there is still no recorded delivery outcome for it.", "审阅阶段已经产出就绪输出，但当前还没有对应的交付结果记录。"),
          facts: [
            {{ label: copy("Ready stories", "待交付故事"), value: String(readyStories) }},
            {{ label: copy("Routes", "路由"), value: String(state.routes.length || 0) }},
            {{ label: copy("Dispatch records", "dispatch 记录"), value: String(state.deliveryDispatchRecords.length || 0) }},
          ],
        }};
      }} else if (selectedStory || selectedTriage || openQueue > 0) {{
        deliverStage = {{
          id: "deliver",
          status: "blocked",
          title: copy("Flow stopped before delivery", "流程在交付前停止"),
          summary: readyStories > 0
            ? copy("A delivery target still needs an explicit dispatch outcome.", "当前仍需要一个明确的 dispatch 结果，才能完成交付。")
            : copy("The flow has not produced a delivery-ready object yet, so the stop reason still lives upstream in review.", "当前流程还没有产出可交付对象，所以停止原因仍然位于上游审阅阶段。"),
          facts: [
            {{ label: copy("Ready stories", "待交付故事"), value: String(readyStories) }},
            {{ label: copy("Open queue", "开放队列"), value: String(openQueue) }},
            {{ label: copy("Routes", "路由"), value: String(state.routes.length || 0) }},
          ],
        }};
      }} else {{
        deliverStage = {{
          id: "deliver",
          status: "pending",
          title: copy("Delivery path is not active yet", "交付路径尚未激活"),
          summary: copy("Create a route or produce review-ready output before the delivery stage can record an outcome.", "先创建路由或产出可交付的审阅结果，交付阶段才会开始记录结果。"),
          facts: [
            {{ label: copy("Routes", "路由"), value: String(state.routes.length || 0) }},
            {{ label: copy("Ready stories", "待交付故事"), value: String(readyStories) }},
            {{ label: copy("Dispatch records", "dispatch 记录"), value: String(state.deliveryDispatchRecords.length || 0) }},
          ],
        }};
      }}

      return {{
        title: copy("Stage-Linked Output Trace", "阶段联动输出 Trace"),
        summary: copy(
          "Follow one visible path from mission start through monitor, review, and route-backed delivery without reconstructing the story from logs.",
          "沿着一条可见路径，从任务启动一路看到监测、审阅和带路由的交付结果，而不必回到日志里重建流程。"
        ),
        stages: [startStage, monitorStage, reviewStage, deliverStage],
      }};
    }}

    function renderStageLinkedTraceCard(trace = buildStageLinkedTrace()) {{
      const stages = Array.isArray(trace?.stages) ? trace.stages : [];
      return `
        <div class="card workflow-trace-card" data-stage-trace="workflow">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("output trace", "输出追踪")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(trace?.title || copy("Stage-Linked Output Trace", "阶段联动输出 Trace"))}}</h3>
            </div>
            <span class="chip ok">${{copy("Start -> Monitor -> Review -> Deliver", "Start -> Monitor -> Review -> Deliver")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(trace?.summary || "")}}</div>
          <div class="trace-stage-grid">
            ${{stages.map((stage) => {{
              const tone = signalToneFromStatus(stage?.status || "");
              return `
                <div class="trace-stage ${{tone}}" data-trace-stage="${{escapeHtml(stage?.id || "")}}" data-trace-status="${{escapeHtml(String(stage?.status || ""))}}">
                  <div class="trace-stage-head">
                    <div class="trace-stage-kicker">${{escapeHtml(localizeWord(stage?.id || ""))}}</div>
                    <span class="chip ${{tone}}">${{escapeHtml(traceStageStatusLabel(stage?.status || ""))}}</span>
                  </div>
                  <div class="trace-stage-title">${{escapeHtml(stage?.title || "")}}</div>
                  <div class="trace-stage-copy">${{escapeHtml(stage?.summary || "")}}</div>
                  ${{renderSectionSummaryFacts(stage?.facts || [])}}
                </div>
              `;
            }}).join("")}}
          </div>
        </div>
      `;
    }}

    function buildSharedSignalTaxonomy() {{
      const selectedWatch = getSelectedWatchForContext() || state.watches[0] || null;
      const selectedStory = getStoryRecord(state.selectedStoryId);
      const selectedReport = getSelectedReportRecord();
      const selectedQuality = getReportComposition(selectedReport?.id || "")?.quality || null;
      const routeSummary = state.ops?.route_summary || {{}};
      const routeTimeline = Array.isArray(state.ops?.route_timeline) ? state.ops.route_timeline : [];
      const overflowEvidence = state.consoleOverflowEvidence || defaultConsoleOverflowEvidence();
      const aiPrechecks = Object.values(state.aiSurfacePrechecks || {{}}).filter((value) => value && typeof value === "object");
      const aiTrustRisk = aiPrechecks.find((precheck) => {{
        const normalized = String(precheck.mode_status || "").trim().toLowerCase();
        return ["rejected", "invalid"].includes(normalized);
      }}) || aiPrechecks.find((precheck) => {{
        const normalized = String(precheck.mode_status || "").trim().toLowerCase();
        return ["admitted", "fallback_used"].includes(normalized);
      }}) || null;
      const contradictionCount = Array.isArray(selectedStory?.contradictions) ? selectedStory.contradictions.length : 0;
      const readyStories = Number(state.overview?.story_ready_count ?? getGovernanceSignal("story_conversion").ready_story_count ?? 0);
      const qualitySignal = selectedQuality
        ? {{
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
              {{ label: copy("Report", "报告"), value: String(selectedReport?.title || selectedReport?.id || "") }},
              {{ label: copy("Status", "状态"), value: localizeWord(selectedQuality.status || "draft") }},
              {{ label: copy("Score", "分数"), value: Number(selectedQuality.score || 0).toFixed(2) }},
            ],
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
            }},
          }}
        : selectedStory
          ? {{
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
                {{ label: copy("Story", "故事"), value: localizeWord(selectedStory.status || "active") }},
                {{ label: copy("Evidence", "证据"), value: String(selectedStory.item_count || 0) }},
                {{ label: copy("Contradictions", "冲突"), value: String(contradictionCount) }},
              ],
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Story Workspace", "打开故事工作台"),
                  attrs: {{ "data-empty-jump": "section-story" }},
                }},
              }},
            }}
          : {{
              id: "quality",
              classLabel: copy("Quality", "质量"),
              status: Number(state.overview?.triage_open_count || 0) > 0 ? "watch" : "pending",
              title: copy("Review lane still owns the next quality decision", "审阅阶段仍然持有下一个质量决策"),
              summary: copy("Without a selected story or report, quality stays owned by the active review lane and its promotion decisions.", "在没有选中故事或报告时，质量解释仍由当前审阅工作线及其提升决策持有。"),
              owner: copy("Triage and promotion surfaces", "分诊与提升 surface"),
              meaning: copy("Review readiness, contradiction handling, and export guardrail state.", "审阅就绪度、冲突处理和导出门禁状态。"),
              facts: [
                {{ label: copy("Open queue", "开放队列"), value: String(state.overview?.triage_open_count || 0) }},
                {{ label: copy("Ready stories", "待交付故事"), value: String(readyStories) }},
                {{ label: copy("Reports", "报告"), value: String(state.reports.length || 0) }},
              ],
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Review Lane", "打开审阅工作线"),
                  attrs: {{ "data-empty-jump": "section-triage" }},
                }},
              }},
            }};

      const deliverySignal = {{
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
          {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
          {{ label: copy("Degraded routes", "降级路由"), value: String(routeSummary.degraded || 0) }},
          {{ label: copy("Last route", "最近路由"), value: String(routeTimeline[0]?.route || "-") }},
        ],
        actionHierarchy: {{
          primary: {{
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: {{ "data-empty-jump": "section-ops" }},
          }},
        }},
      }};

      const overflowSignal = {{
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
          {{ label: copy("Survivors", "残余样本"), value: String(overflowEvidence.survivor_count || 0) }},
          {{ label: copy("Hotspots", "热点"), value: String(overflowEvidence.residual_surface_count || 0) }},
          {{ label: copy("Sampled", "采样"), value: overflowEvidence.updated_at ? formatCompactDateTime(overflowEvidence.updated_at) : copy("not yet", "尚未") }},
        ],
        actionHierarchy: Number(overflowEvidence.residual_surface_count || 0) > 0
          ? {{
              primary: {{
                label: copy("Inspect Overflow Evidence", "查看溢出证据"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            }}
          : null,
        noActionOutcome: copy("No operator action: keep the overflow evidence visible as a residual hotspot baseline.", "无需操作：把溢出证据继续保留为残余热点基线。"),
      }};

      const trustSignal = selectedWatch && (selectedWatch.retry_advice || selectedWatch.last_failure)
        ? {{
            id: "trust",
            classLabel: copy("Trust", "可信度"),
            status: "watch",
            title: copy("Mission trust is currently owned by retry guidance", "当前任务可信度由重试建议持有"),
            summary: copy("The nearest trust explainer is still the mission retry guidance because the latest failure remains visible.", "当前最近的可信度解释器仍然是任务重试建议，因为最近失败事实依然可见。"),
            owner: copy("Retry guidance", "重试建议"),
            meaning: copy("Whether the current mission, route, or assisted surface is trustworthy enough to continue.", "当前任务、路由或辅助 surface 是否足够可信，可以继续推进。"),
            facts: [
              {{ label: copy("Mission", "任务"), value: String(selectedWatch.name || selectedWatch.id || "") }},
              {{ label: copy("Retry", "重试"), value: String(selectedWatch.retry_advice?.retry_command || "-") }},
              {{ label: copy("Last failure", "最近失败"), value: String(selectedWatch.last_failure?.error || selectedWatch.retry_advice?.failure_class || "-") }},
            ],
            actionHierarchy: {{
              primary: {{
                label: copy("Open Cockpit Guidance", "打开任务详情指引"),
                attrs: {{ "data-empty-jump": "section-cockpit" }},
              }},
            }},
          }}
        : aiTrustRisk
          ? {{
              id: "trust",
              classLabel: copy("Trust", "可信度"),
              status: String(aiTrustRisk.mode_status || "watch").trim().toLowerCase() || "watch",
              title: copy("Governed assist trust needs a surface check", "治理辅助可信度需要 surface 检查"),
              summary: copy("The nearest trust explainer is currently an AI surface precheck or runtime fact guard.", "当前最近的可信度解释器是 AI surface 的预检或运行事实门禁。"),
              owner: copy("AI surface precheck", "AI surface 预检"),
              meaning: copy("Whether the current mission, route, or assisted surface is trustworthy enough to continue.", "当前任务、路由或辅助 surface 是否足够可信，可以继续推进。"),
              facts: [
                {{ label: copy("Surface", "surface"), value: String(aiTrustRisk.alias || aiTrustRisk.contract_id || "-") }},
                {{ label: copy("Mode status", "模式状态"), value: localizeWord(aiTrustRisk.mode_status || "pending") }},
                {{ label: copy("Fallback", "回退"), value: localizeWord(aiTrustRisk.manual_fallback || "-") }},
              ],
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: {{ "data-empty-jump": "section-ops" }},
                }},
              }},
            }}
          : {{
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
                {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
                {{ label: copy("Degraded routes", "降级路由"), value: String(routeSummary.degraded || 0) }},
                {{ label: copy("Missing routes", "缺失路由"), value: String(routeSummary.missing || 0) }},
              ],
              actionHierarchy: (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
                ? {{
                    primary: {{
                      label: copy("Inspect Route Health", "查看路由健康"),
                      attrs: {{ "data-empty-jump": "section-ops" }},
                    }},
                  }}
                : null,
              noActionOutcome: copy("No operator action: trust posture is currently clear enough to continue.", "无需操作：当前可信度姿态已足够清晰，可以继续推进。"),
            }};

      return [qualitySignal, deliverySignal, overflowSignal, trustSignal];
    }}

    function renderSharedSignalTaxonomyCard(signals = buildSharedSignalTaxonomy()) {{
      const rows = Array.isArray(signals) ? signals : [];
      const activeSignal = rows.find((signal) => signal.id === state.sharedSignalFocus) || rows[0] || null;
      if (activeSignal && state.sharedSignalFocus !== activeSignal.id) {{
        state.sharedSignalFocus = activeSignal.id;
      }}
      return `
        <div class="card shared-signal-taxonomy-card" data-shared-signal-taxonomy="true">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("shared signal taxonomy", "共享信号 taxonomy")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{copy("Shared Signal Taxonomy", "共享信号分类")}}</h3>
            </div>
            <span class="chip">${{copy("owner-backed", "解释有归属")}}</span>
          </div>
          <div class="panel-sub">${{copy(
            "Every shared signal below names its owner, meaning, and next action instead of behaving like a decorative badge.",
            "下面每个共享信号都会明确说明 owner、含义和下一步，而不是只做装饰性 badge。"
          )}}</div>
          <div class="shared-signal-row">
            ${{rows.map((signal) => {{
              const tone = signalToneFromStatus(signal?.status || "");
              const active = signal?.id === activeSignal?.id;
              return `
                <button
                  class="chip-btn shared-signal-button ${{tone}} ${{active ? "active" : ""}}"
                  type="button"
                  data-shared-signal-button="${{escapeHtml(signal?.id || "")}}"
                  aria-expanded="${{String(active)}}"
                >${{escapeHtml(signal?.classLabel || signal?.id || "")}} · ${{escapeHtml(traceStageStatusLabel(signal?.status || ""))}}</button>
              `;
            }}).join("")}}
          </div>
          ${{activeSignal ? `
            <div class="shared-signal-detail ${{signalToneFromStatus(activeSignal.status || "")}}" data-shared-signal-panel="${{escapeHtml(activeSignal.id || "")}}">
              <div class="shared-signal-detail-head">
                <div>
                  <div class="section-summary-kicker">${{escapeHtml(activeSignal.classLabel || activeSignal.id || "")}}</div>
                  <div class="section-summary-title">${{escapeHtml(activeSignal.title || "")}}</div>
                </div>
                <span class="chip ${{signalToneFromStatus(activeSignal.status || "")}}">${{escapeHtml(traceStageStatusLabel(activeSignal.status || ""))}}</span>
              </div>
              <div class="section-summary-copy">${{escapeHtml(activeSignal.summary || "")}}</div>
              <div class="meta">
                <span data-shared-signal-owner>${{copy("Owner", "归属")}}: ${{escapeHtml(activeSignal.owner || "-")}}</span>
                <span>${{copy("Meaning", "含义")}}: ${{escapeHtml(activeSignal.meaning || "-")}}</span>
              </div>
              ${{renderSectionSummaryFacts(activeSignal.facts || [])}}
              ${{activeSignal.actionHierarchy ? renderCardActionHierarchy(activeSignal.actionHierarchy) : `<div class="panel-sub" data-shared-signal-noop="true">${{escapeHtml(activeSignal.noActionOutcome || copy("No operator action.", "当前无需操作。"))}}</div>`}}
            </div>
          ` : ""}}
        </div>
      `;
    }}

    function renderLifecycleContinuityCard({{ title = "", summary = "", stages = [], actions = [], tone = "ok" }} = {{}}) {{
      const stagesHtml = stages.map((stage) => `
        <div class="continuity-stage ${{escapeHtml(stage.tone || "")}}">
          <div class="continuity-stage-kicker">${{escapeHtml(stage.kicker || "")}}</div>
          <div class="continuity-stage-title">${{escapeHtml(stage.title || "")}}</div>
          <div class="continuity-stage-copy">${{escapeHtml(stage.copy || "")}}</div>
          <div class="continuity-fact-list">
            ${{(stage.facts || []).map((fact) => {{
              const hasValue = ![null, undefined].includes(fact.value) && String(fact.value).trim() !== "";
              return `
                <div class="continuity-fact">
                  <span>${{escapeHtml(fact.label || "")}}</span>
                  <strong>${{escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}}</strong>
                </div>
              `;
            }}).join("")}}
          </div>
        </div>
      `).join("");
      const actionsHtml = actions.length
        ? `<div class="actions" style="margin-top:14px;">${{actions.map((action) => `
            <button
              class="${{action.primary ? "btn-primary" : "btn-secondary"}}"
              type="button"
              ${{action.section ? `data-empty-jump="${{escapeHtml(action.section)}}"` : ""}}
              ${{action.focus ? `data-empty-focus="${{escapeHtml(action.focus)}}"` : ""}}
              ${{action.field ? `data-empty-field="${{escapeHtml(action.field)}}"` : ""}}
              ${{action.watch ? `data-empty-watch="${{escapeHtml(action.watch)}}"` : ""}}
              ${{action.runWatch ? `data-empty-run-watch="${{escapeHtml(action.runWatch)}}"` : ""}}
              ${{action.toggleWatch ? `data-watch-toggle="${{escapeHtml(action.toggleWatch)}}"` : ""}}
              ${{action.watchEnabled ? `data-watch-enabled="${{escapeHtml(action.watchEnabled)}}"` : ""}}
            >${{escapeHtml(action.label || "")}}</button>
          `).join("")}}</div>`
        : "";
      return `
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("lifecycle continuity", "生命周期衔接")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title)}}</h3>
            </div>
            <span class="chip ${{tone}}">${{copy("cross-stage", "跨阶段")}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          <div class="continuity-lane" style="margin-top:14px;">${{stagesHtml}}</div>
          ${{actionsHtml}}
        </div>
      `;
    }}

    function sectionSummaryRootId(sectionId) {{
      const map = {{
        "section-intake": "intake-section-summary",
        "section-board": "board-section-summary",
        "section-cockpit": "cockpit-section-summary",
        "section-triage": "triage-section-summary",
        "section-story": "story-section-summary",
        "section-ops": "ops-section-summary",
      }};
      return map[normalizeSectionId(sectionId)] || "";
    }}

    function stageFeedbackIdForSection(sectionId) {{
      const normalizedSectionId = normalizeSectionId(sectionId);
      const map = {{
        "section-intake": "start",
        "section-board": "monitor",
        "section-cockpit": "monitor",
        "section-triage": "review",
        "section-story": "review",
        "section-claims": "review",
        "section-report-studio": "review",
        "section-ops": "deliver",
      }};
      return map[normalizedSectionId] || normalizedSectionId;
    }}

    function getStageFeedback(stageOrSectionId) {{
      const stageId = stageFeedbackIdForSection(stageOrSectionId);
      return state.stageFeedback?.[stageId] || null;
    }}

    function refreshStageFeedbackSurfaces(stageId) {{
      const normalizedStageId = stageFeedbackIdForSection(stageId);
      if (normalizedStageId === "start") {{
        renderCreateWatchDeck();
        return;
      }}
      if (normalizedStageId === "monitor") {{
        renderWatches();
        renderWatchDetail();
        return;
      }}
      if (normalizedStageId === "review") {{
        renderTriage();
        renderStories();
        return;
      }}
      if (normalizedStageId === "deliver") {{
        renderStatus();
      }}
    }}

    function setStageFeedback(stageOrSectionId, payload = null) {{
      const stageId = stageFeedbackIdForSection(stageOrSectionId);
      if (!stageId || !state.stageFeedback) {{
        return;
      }}
      state.stageFeedback[stageId] = payload
        ? {{
            stageId,
            kind: String(payload.kind || "info").trim().toLowerCase() || "info",
            title: String(payload.title || "").trim(),
            copy: String(payload.copy || "").trim(),
            tone: String(payload.tone || "").trim(),
            facts: Array.isArray(payload.facts) ? payload.facts : [],
            actionHierarchy: payload.actionHierarchy && typeof payload.actionHierarchy === "object"
              ? payload.actionHierarchy
              : null,
          }}
        : null;
      refreshStageFeedbackSurfaces(stageId);
    }}

    function stageFeedbackKindLabel(kind = "") {{
      const labels = {{
        completion: copy("completion", "完成状态"),
        warning: copy("warning", "警告"),
        blocked: copy("blocked", "阻塞状态"),
        no_result: copy("no result", "无结果"),
        info: copy("stage note", "阶段说明"),
      }};
      return labels[String(kind || "").trim().toLowerCase()] || copy("stage note", "阶段说明");
    }}

    function renderStageFeedbackCard(feedback = {{}}, sectionId = "") {{
      if (!feedback || !(feedback.title || feedback.copy)) {{
        return "";
      }}
      const stageId = stageFeedbackIdForSection(feedback.stageId || sectionId);
      const kind = String(feedback.kind || "info").trim().toLowerCase() || "info";
      const tone = String(feedback.tone || "").trim()
        || (kind === "completion" ? "ok" : ["warning", "blocked"].includes(kind) ? "hot" : "");
      return `
        <div class="section-summary-feedback ${{escapeHtml(tone)}}" data-stage-feedback-stage="${{escapeHtml(stageId)}}" data-stage-feedback-kind="${{escapeHtml(kind)}}">
          <div class="section-summary-feedback-head">
            <div>
              <div class="section-summary-kicker">${{escapeHtml(stageFeedbackKindLabel(kind))}}</div>
              <div class="section-summary-title">${{escapeHtml(feedback.title || copy("Stage feedback", "阶段反馈"))}}</div>
            </div>
            <span class="chip ${{escapeHtml(tone)}}">${{escapeHtml(stageFeedbackKindLabel(kind))}}</span>
          </div>
          <div class="section-summary-feedback-copy">${{escapeHtml(feedback.copy || "")}}</div>
          ${{renderSectionSummaryFacts(feedback.facts)}}
          ${{feedback.actionHierarchy ? renderCardActionHierarchy(feedback.actionHierarchy) : ""}}
        </div>
      `;
    }}

    function renderSectionSummaryFacts(facts = []) {{
      const rows = Array.isArray(facts) ? facts.filter(Boolean) : [];
      if (!rows.length) {{
        return "";
      }}
      return `
        <div class="continuity-fact-list">
          ${{rows.map((fact) => {{
            const hasValue = ![null, undefined].includes(fact.value) && String(fact.value).trim() !== "";
            return `
              <div class="continuity-fact">
                <span>${{escapeHtml(fact.label || "")}}</span>
                <strong>${{escapeHtml(hasValue ? String(fact.value).trim() : copy("n/a", "暂无"))}}</strong>
              </div>
            `;
          }}).join("")}}
        </div>
      `;
    }}

    function renderSectionSummarySignal(kind, signal = {{}}) {{
      const normalizedKind = String(kind || "").trim().toLowerCase();
      const kindLabels = {{
        objective: copy("current objective", "当前目标"),
        success: copy("success signal", "成功信号"),
        blocker: copy("blocker or next prerequisite", "阻塞点或下一个前提"),
      }};
      const hasExplicitTone = Object.prototype.hasOwnProperty.call(signal || {{}}, "tone");
      const tone = hasExplicitTone
        ? String(signal.tone || "").trim()
        : (normalizedKind === "success" ? "ok" : normalizedKind === "blocker" ? "hot" : "");
      return `
        <div class="section-summary-signal ${{escapeHtml(tone)}}" data-section-summary-kind="${{escapeHtml(normalizedKind)}}">
          <div class="section-summary-kicker">${{escapeHtml(kindLabels[normalizedKind] || normalizedKind)}}</div>
          <div class="section-summary-title">${{escapeHtml(signal.title || copy("No signal yet", "当前没有信号"))}}</div>
          <div class="section-summary-copy">${{escapeHtml(signal.copy || "")}}</div>
          ${{renderSectionSummaryFacts(signal.facts)}}
        </div>
      `;
    }}

    function renderSectionSummaryFrame({{ sectionId = "", title = "", summary = "", objective = {{}}, success = {{}}, blocker = {{}} }} = {{}}) {{
      const normalizedSectionId = normalizeSectionId(sectionId);
      const feedback = getStageFeedback(normalizedSectionId);
      return `
        <div class="card section-summary-card" data-section-summary="${{escapeHtml(normalizedSectionId)}}">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("section summary", "区块摘要")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title || activeSectionLabel(normalizedSectionId))}}</h3>
            </div>
            <span class="chip">${{escapeHtml(activeSectionLabel(normalizedSectionId))}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          ${{feedback ? renderStageFeedbackCard(feedback, normalizedSectionId) : ""}}
          <div class="section-summary-grid">
            ${{renderSectionSummarySignal("objective", objective)}}
            ${{renderSectionSummarySignal("success", success)}}
            ${{renderSectionSummarySignal("blocker", blocker)}}
          </div>
        </div>
      `;
    }}

    function setSectionSummary(sectionId, payload = {{}}) {{
      const rootId = sectionSummaryRootId(sectionId);
      const root = rootId ? $(rootId) : null;
      if (!root) {{
        return;
      }}
      root.innerHTML = renderSectionSummaryFrame({{
        sectionId,
        ...payload,
      }});
      wireLifecycleGuideActions(root);
      scheduleCanvasTextFit(root);
    }}

    function operatorGuidanceLaneLabel(lane = "") {{
      const labels = {{
        mission: copy("mission lane", "任务工作线"),
        triage: copy("triage lane", "分诊工作线"),
        story: copy("story lane", "故事工作线"),
        route: copy("route lane", "路由工作线"),
      }};
      return labels[String(lane || "").trim().toLowerCase()] || copy("operator guidance", "操作指引");
    }}

    function operatorGuidanceColumnMeta(kind = "") {{
      const normalizedKind = String(kind || "").trim().toLowerCase();
      const labels = {{
        reasons: {{
          title: copy("Action reasons", "动作原因"),
          subtitle: copy("What is driving the current guidance right now.", "当前这条指引背后的驱动事实。"),
        }},
        next_steps: {{
          title: copy("Next steps", "下一步"),
          subtitle: copy("What the operator should do next from this lane.", "操作者在这条工作线里的下一步动作。"),
        }},
        sources: {{
          title: copy("Explanation owners", "解释归属"),
          subtitle: copy("Which runtime or static source owns this copy.", "哪些运行时或静态来源拥有这部分解释。"),
        }},
      }};
      return labels[normalizedKind] || {{
        title: copy("Guidance", "指引"),
        subtitle: copy("Shared operator wording for this lane.", "当前工作线的共享操作文案。"),
      }};
    }}

    function normalizeOperatorGuidanceItems(items = []) {{
      return Array.isArray(items)
        ? items.filter((item) => item && (item.title || item.copy || (Array.isArray(item.facts) && item.facts.length)))
        : [];
    }}

    function renderOperatorGuidanceItem(item = {{}}, kind = "") {{
      const tone = String(item.tone || "").trim();
      const owner = item.owner
        ? `<span class="chip">${{escapeHtml(item.owner)}}</span>`
        : "";
      return `
        <div class="operator-guidance-item ${{escapeHtml(tone)}}" data-guidance-kind="${{escapeHtml(kind)}}" data-guidance-item="${{escapeHtml(String(item.title || kind || "guidance").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-"))}}">
          <div class="operator-guidance-item-head">
            <div class="operator-guidance-item-title">${{escapeHtml(item.title || copy("Guidance item", "指引条目"))}}</div>
            ${{owner}}
          </div>
          <div class="operator-guidance-item-copy">${{escapeHtml(item.copy || "")}}</div>
          ${{renderSectionSummaryFacts(item.facts)}}
        </div>
      `;
    }}

    function renderOperatorGuidanceColumn(kind, items = []) {{
      const rows = normalizeOperatorGuidanceItems(items);
      if (!rows.length) {{
        return "";
      }}
      const meta = operatorGuidanceColumnMeta(kind);
      return `
        <div class="operator-guidance-column" data-guidance-column="${{escapeHtml(kind)}}">
          <div class="operator-guidance-column-head">
            <div class="mono">${{escapeHtml(meta.title)}}</div>
            <div class="panel-sub">${{escapeHtml(meta.subtitle)}}</div>
          </div>
          <div class="operator-guidance-list">
            ${{rows.map((item) => renderOperatorGuidanceItem(item, kind)).join("")}}
          </div>
        </div>
      `;
    }}

    function renderOperatorGuidanceSurface({{
      surfaceId = "",
      lane = "",
      title = "",
      summary = "",
      reasons = [],
      nextSteps = [],
      sources = [],
      actionHierarchy = null,
    }} = {{}}) {{
      const normalizedLane = String(lane || "").trim().toLowerCase() || "generic";
      return `
        <div
          class="card operator-guidance-surface"
          ${{surfaceId ? `id="${{escapeHtml(surfaceId)}}"` : ""}}
          data-operator-guidance-surface="${{escapeHtml(normalizedLane)}}"
        >
          <div class="card-top">
            <div>
              <div class="mono">${{copy("operator guidance", "操作指引")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(title || operatorGuidanceLaneLabel(normalizedLane))}}</h3>
            </div>
            <span class="chip">${{escapeHtml(operatorGuidanceLaneLabel(normalizedLane))}}</span>
          </div>
          <div class="panel-sub">${{escapeHtml(summary)}}</div>
          <div class="operator-guidance-grid">
            ${{renderOperatorGuidanceColumn("reasons", reasons)}}
            ${{renderOperatorGuidanceColumn("next_steps", nextSteps)}}
            ${{renderOperatorGuidanceColumn("sources", sources)}}
          </div>
          ${{actionHierarchy ? renderCardActionHierarchy(actionHierarchy) : ""}}
        </div>
      `;
    }}

    function renderIntakeSectionSummary(preview = buildCreateWatchPreview(state.createWatchDraft || defaultCreateWatchDraft())) {{
      const draft = normalizeCreateWatchDraft(state.createWatchDraft || defaultCreateWatchDraft());
      const routeName = normalizeRouteName(draft.route);
      const routeRecord = routeName ? getRouteRecordByName(routeName) : null;
      const hardBlocker = !draft.name.trim()
        ? {{
            title: copy("Mission name is still missing", "任务名称仍未填写"),
            copy: copy("Add a short operator-facing name before the draft can create or update a mission.", "先补一个面向操作者的短名称，任务草稿才能创建或更新。"),
            facts: [
              {{ label: copy("Query", "查询词"), value: clampLabel(draft.query, 24) }},
              {{ label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") }},
            ],
          }}
        : !draft.query.trim()
          ? {{
              title: copy("Mission query is still missing", "任务查询词仍未填写"),
              copy: copy("Add the signal or topic to track before the draft can become a valid mission.", "先补上要追踪的主题或信号，草稿才能成为有效任务。"),
              facts: [
                {{ label: copy("Name", "名称"), value: clampLabel(draft.name, 24) }},
                {{ label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") }},
              ],
            }}
          : routeName && !routeRecord
            ? {{
                title: copy("Named route is not available", "命名路由当前不可用"),
                copy: copy("The draft references a route that is not present in the current route inventory.", "当前草稿引用了一个不在现有路由库存中的命名路由。"),
                facts: [
                  {{ label: copy("Route", "路由"), value: routeName }},
                  {{ label: copy("Known routes", "现有路由"), value: String(state.routes.length || 0) }},
                ],
              }}
            : {{
                title: copy("Next prerequisite is optional delivery wiring", "下一个前提是决定是否接入交付"),
                copy: copy("The draft is already valid. Only add a named route when this mission should notify downstream systems.", "当前草稿已经有效；只有在这个任务需要通知下游系统时，才需要继续补命名路由。"),
                tone: "",
                facts: [
                  {{ label: copy("Route", "路由"), value: routeName || copy("not attached", "未绑定") }},
                  {{ label: copy("Cadence", "频率"), value: draft.schedule || "manual" }},
                ],
              }};
      const successSignal = preview.requiredReady
        ? {{
            title: copy("Draft can already map to a valid mission", "当前草稿已经能映射成有效任务"),
            copy: copy("The required mission fields are present, so this draft can create or update a watch without leaving the intake lane.", "必填任务字段已经齐全，所以这份草稿可以直接在录入区创建或更新任务。"),
            tone: "ok",
            facts: [
              {{ label: copy("Name", "名称"), value: clampLabel(draft.name, 24) }},
              {{ label: copy("Query", "查询词"), value: clampLabel(draft.query, 28) }},
              {{ label: copy("Readiness", "就绪度"), value: `${{preview.readiness}}%` }},
            ],
          }}
        : (state.createWatchPresetId || String(state.createWatchEditingId || "").trim())
          ? {{
              title: copy("Reusable mission source is already loaded", "可复用的任务来源已经载入"),
              copy: copy("A preset or existing mission is already shaping this draft, so the operator does not need to rebuild everything from scratch.", "当前草稿已经带着预设或已有任务来源，操作者不需要从零重建。"),
              facts: [
                {{ label: copy("Preset", "预设"), value: state.createWatchPresetId || copy("editing existing", "编辑已有任务") }},
                {{ label: copy("Route", "路由"), value: routeName || copy("unset", "未设置") }},
              ],
            }}
          : {{
              title: copy("Mission intake deck is live", "任务录入面板已就绪"),
              copy: copy("The intake lane is ready for the next mission draft even before a reusable source or complete payload exists.", "即使还没有复用来源或完整载荷，录入工作线也已经可以承接下一条任务草稿。"),
              facts: [
                {{ label: copy("Routes", "路由数"), value: String(state.routes.length || 0) }},
                {{ label: copy("Presets", "预设数"), value: String(createWatchPresets.length || 0) }},
              ],
            }};
      setSectionSummary("section-intake", {{
        title: copy("Mission Intake Readiness", "任务录入就绪度"),
        summary: copy(
          "Keep one concise intake frame visible so operators know what mission or route-aware watch they are preparing to launch.",
          "保持一个简洁的录入摘要框，让操作者始终知道自己正在准备哪条任务或路由感知型 watch。"
        ),
        objective: {{
          title: preview.draft.name.trim() || preview.draft.query.trim() || copy("Prepare the next watch mission", "准备下一条监控任务"),
          copy: copy(
            "Mission Intake is currently shaping the next watch payload, including optional alert route and threshold fields.",
            "任务录入区当前正在整理下一条 watch 载荷，其中也包括可选的告警路由和阈值字段。"
          ),
          facts: [
            {{ label: copy("Schedule", "频率"), value: preview.scheduleLabel }},
            {{ label: copy("Scope", "范围"), value: preview.filtersLabel }},
            {{ label: copy("Route", "路由"), value: preview.routeLabel }},
          ],
        }},
        success: successSignal,
        blocker: hardBlocker,
      }});
    }}

    function renderBoardSectionSummary(filteredWatches = [], searchValue = "") {{
      const selectedWatch = state.watches.find((watch) => watch.id === state.selectedWatchId) || null;
      const dueCount = filteredWatches.filter((watch) => watch.is_due).length;
      const blockerSignal = !state.watches.length
        ? {{
            title: copy("Mission board is still empty", "任务列表当前为空"),
            copy: copy("Create one watch from Mission Intake before the board can provide a mission set for inspection.", "先从任务录入区创建一条任务，任务列表才能提供可检查的任务集合。"),
            facts: [
              {{ label: copy("Loaded missions", "已加载任务"), value: "0" }},
              {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) }},
            ],
          }}
        : !filteredWatches.length
          ? {{
              title: copy("Current mission search returned zero matches", "当前任务搜索没有命中"),
              copy: copy("The board has missions, but the active search has removed the next mission context needed for inspection.", "当前任务列表里其实有任务，但激活中的搜索把下一条可检查的任务上下文筛掉了。"),
              facts: [
                {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) }},
                {{ label: copy("Total missions", "任务总数"), value: String(state.watches.length || 0) }},
              ],
            }}
          : !selectedWatch
            ? {{
                title: copy("Select one mission for cockpit inspection", "先选择一条任务进入驾驶舱"),
                copy: copy("The board already has candidate missions, but cockpit inspection still needs one active mission context.", "当前任务列表里已经有候选任务，但驾驶舱检查仍然需要一个激活中的任务上下文。"),
                tone: "",
                facts: [
                  {{ label: copy("Shown", "显示"), value: String(filteredWatches.length) }},
                  {{ label: copy("Due now", "当前待执行"), value: String(dueCount) }},
                ],
              }}
            : {{
                title: copy("Next prerequisite is cockpit inspection", "下一个前提是进入驾驶舱检查"),
                copy: copy("The board is populated. Open the selected mission in Cockpit when the operator needs detailed run or delivery facts.", "当前任务列表已经有内容；当操作者需要查看更细的执行或交付事实时，下一步就进入驾驶舱。"),
                tone: "",
                facts: [
                  {{ label: copy("Selected", "当前任务"), value: clampLabel(selectedWatch.name || selectedWatch.id, 24) }},
                  {{ label: copy("Due now", "当前待执行"), value: String(dueCount) }},
                ],
              }};
      const successSignal = filteredWatches.length
        ? {{
            title: copy("Mission board already has reviewable missions", "任务列表里已经有可继续推进的任务"),
            copy: copy("The board can already hand one or more missions into Cockpit without sending the operator back to Intake first.", "当前任务列表已经可以把一条或多条任务直接交给驾驶舱，不需要先退回录入区。"),
            tone: "ok",
            facts: [
              {{ label: copy("Shown", "显示"), value: String(filteredWatches.length) }},
              {{ label: copy("Total", "总数"), value: String(state.watches.length || 0) }},
              {{ label: copy("Due", "待执行"), value: String(dueCount) }},
            ],
          }}
        : {{
            title: copy("Mission board shell is ready", "任务列表工作面已经就绪"),
            copy: copy("Search and board controls are live even when the current slice does not expose a reviewable mission set yet.", "即使当前切片里还没有可审阅的任务集合，搜索和列表控制也已经可用。"),
            facts: [
              {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) }},
              {{ label: copy("Total", "总数"), value: String(state.watches.length || 0) }},
            ],
          }};
      setSectionSummary("section-board", {{
        title: copy("Mission Board Snapshot", "任务列表摘要"),
        summary: copy(
          "Frame the current mission set first so operators can see whether the board already contains the next inspectable mission context.",
          "先框定当前正在审阅的任务集合，让操作者快速看清任务列表里是否已经存在下一条可检查任务。"
        ),
        objective: {{
          title: selectedWatch
            ? phrase("Review {{mission}}", "审阅 {{mission}}", {{ mission: clampLabel(selectedWatch.name || selectedWatch.id, 18) }})
            : (searchValue.trim()
              ? phrase("Review search: {{query}}", "审阅搜索：{{query}}", {{ query: clampLabel(searchValue, 18) }})
              : copy("Review the current mission set", "审阅当前任务集合")),
          copy: copy(
            "Mission Board is defining which mission set is under review before the operator commits to Cockpit or Triage.",
            "任务列表当前正在界定哪一组任务处于审阅范围，然后操作者才会继续进入驾驶舱或分诊。"
          ),
          facts: [
            {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") }},
            {{ label: copy("Selected", "当前任务"), value: selectedWatch ? clampLabel(selectedWatch.name || selectedWatch.id, 24) : copy("none", "无") }},
            {{ label: copy("Due now", "当前待执行"), value: String(dueCount) }},
          ],
        }},
        success: successSignal,
        blocker: blockerSignal,
      }});
    }}

    function renderCockpitSectionSummary(watch = null, {{
      recentRuns = [],
      recentResults = [],
      retryAdvice = null,
      lastFailure = null,
      deliveryStats = {{}},
    }} = {{}}) {{
      const routeSummary = state.ops?.route_summary || {{}};
      const hasInspectableState = Boolean((Array.isArray(recentRuns) && recentRuns.length) || (Array.isArray(recentResults) && recentResults.length) || Number(watch?.alert_rule_count || 0) > 0);
      const blockerSignal = !watch
        ? {{
            title: copy("No mission is selected for cockpit inspection", "当前没有选中任务进入驾驶舱"),
            copy: copy("Cockpit needs one selected mission before it can project current runs, results, or retry guidance.", "驾驶舱需要先有一条被选中的任务，才能投射当前执行、结果和重试建议。"),
            facts: [
              {{ label: copy("Board missions", "任务数"), value: String(state.watches.length || 0) }},
            ],
          }}
        : (retryAdvice || lastFailure || String(watch.last_run_status || "").trim().toLowerCase() === "error")
          ? {{
              title: copy("Latest run is asking for remediation", "最近一次执行正在请求修复"),
              copy: copy(
                retryAdvice?.summary || lastFailure?.error || "The latest mission run failed and needs operator action before trust is restored.",
                retryAdvice?.summary || lastFailure?.error || "最近一次任务执行失败，在恢复可信度之前需要操作者介入。"
              ),
              facts: [
                {{ label: copy("Last run", "最近执行"), value: localizeWord(watch.last_run_status || "error") }},
                {{ label: copy("Retry", "重试"), value: retryAdvice?.retry_command || copy("open retry advice", "查看重试建议") }},
                {{ label: copy("Alerts", "告警"), value: String(deliveryStats.recent_alert_count || 0) }},
              ],
            }}
          : !(Array.isArray(recentRuns) && recentRuns.length)
            ? {{
                title: copy("Run this mission once before deeper inspection", "先执行一次任务，再进入更深检查"),
                copy: copy("Cockpit already has the selected mission context, but one run is still missing before results and delivery facts become inspectable.", "驾驶舱已经拿到当前任务上下文，但还缺少至少一次执行，结果流和交付事实才能真正可检查。"),
                tone: "",
                facts: [
                  {{ label: copy("Mission", "任务"), value: clampLabel(watch.name || watch.id, 24) }},
                  {{ label: copy("Alert rules", "告警规则"), value: String(watch.alert_rule_count || 0) }},
                ],
              }}
            : {{
                title: copy("Next prerequisite is deciding the next operator action", "下一个前提是决定当前操作者动作"),
                copy: copy("The mission is already live in Cockpit. Decide whether the next move belongs in Triage, retry, or downstream delivery handling.", "当前任务已经在驾驶舱内处于可检查状态；下一步只需判断该进入分诊、重试，还是继续处理下游交付。"),
                tone: "",
                facts: [
                  {{ label: copy("Recent results", "最近结果"), value: String(recentResults.length || 0) }},
                  {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
                ],
              }};
      const successSignal = watch && hasInspectableState
        ? {{
            title: copy("Selected mission is already inspectable", "当前选中任务已经可检查"),
            copy: copy("Runs, result stream, or alert settings already provide enough runtime facts to inspect the mission without leaving Cockpit.", "执行记录、结果流或告警设置已经提供了足够的运行事实，可以直接在驾驶舱里检查任务。"),
            tone: "ok",
            facts: [
              {{ label: copy("Runs", "执行次数"), value: String(recentRuns.length || 0) }},
              {{ label: copy("Results", "结果数"), value: String(recentResults.length || 0) }},
              {{ label: copy("Alert rules", "告警规则"), value: String(watch.alert_rule_count || 0) }},
            ],
          }}
        : {{
            title: copy("Cockpit shell is ready for mission detail", "驾驶舱工作面已经可以承接任务详情"),
            copy: copy("Mission detail, retry guidance, and delivery handoff surfaces are already mounted in this lane.", "任务详情、重试建议和交付交接面板已经全部挂载到当前工作线里。"),
            facts: [
              {{ label: copy("Mission", "任务"), value: watch ? clampLabel(watch.name || watch.id, 24) : copy("not selected", "未选择") }},
              {{ label: copy("Routes", "路由"), value: String(state.routes.length || 0) }},
            ],
          }};
      setSectionSummary("section-cockpit", {{
        title: copy("Mission Cockpit Snapshot", "任务驾驶舱摘要"),
        summary: copy(
          "Show what the selected mission is doing now, whether it is already inspectable, and what currently blocks trust or the next operator move.",
          "直接展示当前选中任务此刻正在做什么、是否已经可检查，以及当前阻碍可信度或下一步动作的因素。"
        ),
        objective: {{
          title: watch
            ? phrase("Inspect {{mission}} now", "当前检查 {{mission}}", {{ mission: clampLabel(watch.name || watch.id, 18) }})
            : copy("Select a mission to inspect", "先选择一条任务开始检查"),
          copy: copy(
            "Cockpit keeps the active mission, runtime detail, and delivery handoff in one surface instead of scattering them across the shell.",
            "驾驶舱会把当前任务、运行细节和交付交接维持在同一个面板里，而不是让它们散落在整个 shell 里。"
          ),
          facts: [
            {{ label: copy("Mission", "任务"), value: watch ? clampLabel(watch.name || watch.id, 24) : copy("none", "无") }},
            {{ label: copy("Status", "状态"), value: watch ? localizeWord(watch.last_run_status || "idle") : copy("idle", "空闲") }},
            {{ label: copy("Last run", "最近执行"), value: watch ? formatCompactDateTime(watch.last_run_at || "") : copy("n/a", "暂无") }},
          ],
        }},
        success: successSignal,
        blocker: blockerSignal,
      }});
    }}

    function renderTriageSectionSummary({{
      stats = {{}},
      filteredItems = [],
      selectedItem = null,
      evidenceFocusCount = 0,
      activeFilter = "open",
      searchValue = "",
    }} = {{}}) {{
      const linkedStories = selectedItem ? getStoriesForEvidenceItem(selectedItem.id) : [];
      const noteCount = selectedItem && Array.isArray(selectedItem.review_notes) ? selectedItem.review_notes.length : 0;
      const blockerSignal = !state.triage.length
        ? {{
            title: copy("Triage queue is still empty", "分诊队列当前为空"),
            copy: copy("The review lane needs inbox evidence from at least one mission run before operators can verify or promote anything.", "审阅工作线需要至少一次任务执行产生的收件箱证据，操作者才能开始核验或提升内容。"),
            facts: [
              {{ label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) }},
            ],
          }}
        : !filteredItems.length
          ? {{
              title: copy("Active queue slice hides every item", "当前队列切片把所有条目都隐藏了"),
              copy: copy("The queue exists, but the current filter or search has removed the next evidence context needed for review.", "队列本身有内容，但当前筛选或搜索把下一条可审阅证据上下文筛掉了。"),
              facts: [
                {{ label: copy("Filter", "筛选"), value: localizeWord(activeFilter) }},
                {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) }},
              ],
            }}
          : !selectedItem
            ? {{
                title: copy("Pick one evidence item to continue review", "先选中一条证据再继续审阅"),
                copy: copy("The queue already has a reviewable slice, but the current workspace still needs one active evidence selection.", "当前队列里已经有可审阅切片，但当前工作区还需要一个激活中的证据选择。"),
                tone: "",
                facts: [
                  {{ label: copy("Shown", "显示"), value: String(filteredItems.length) }},
                  {{ label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) }},
                ],
              }}
            : (Number(stats.open_count || 0) > filteredItems.length && String(selectedItem.review_state || "new").trim().toLowerCase() === "new")
              ? {{
                  title: copy("Backlog pressure is still ahead of this review", "当前审阅前方仍有积压压力"),
                  copy: copy("The selected item is loaded, but open backlog pressure still suggests more queue work remains before this lane feels clear.", "当前条目已经载入，但开放队列的积压仍然说明这条工作线还没有真正清空。"),
                  facts: [
                    {{ label: copy("Open queue", "开放队列"), value: String(stats.open_count || 0) }},
                    {{ label: copy("Selected state", "当前状态"), value: localizeWord(selectedItem.review_state || "new") }},
                  ],
                }}
              : {{
                  title: copy("Next prerequisite is verification or story handoff", "下一个前提是完成核验或故事交接"),
                  copy: copy("The queue slice is visible. Decide whether the selected evidence should be verified, escalated, or promoted into a story next.", "当前队列切片已经可见；下一步只需要判断这条证据该被核验、升级，还是提升成故事。"),
                  tone: "",
                  facts: [
                    {{ label: copy("Stories", "关联故事"), value: String(linkedStories.length) }},
                    {{ label: copy("Notes", "备注"), value: String(noteCount) }},
                  ],
                }};
      const successSignal = filteredItems.length
        ? {{
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
              {{ label: copy("Shown", "显示"), value: String(filteredItems.length) }},
              {{ label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) }},
              {{ label: copy("Evidence focus", "证据聚焦"), value: String(evidenceFocusCount || 0) }},
            ],
          }}
        : {{
            title: copy("Triage controls are already mounted", "分诊控制已经挂载完成"),
            copy: copy("Filter, search, and batch controls are ready even when the current queue slice is empty.", "即使当前队列切片为空，筛选、搜索和批量控制也都已经可用。"),
            facts: [
              {{ label: copy("Filter", "筛选"), value: localizeWord(activeFilter) }},
              {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") }},
            ],
          }};
      setSectionSummary("section-triage", {{
        title: copy("Triage Queue Snapshot", "分诊队列摘要"),
        summary: copy(
          "Keep the current inbox slice explicit so operators can see which evidence lane is under review, what is already advancing, and what is still blocking movement.",
          "明确显示当前收件箱切片，让操作者快速看清哪条证据工作线正在被审阅、哪些部分已经推进、哪些因素仍在阻塞。"
        ),
        objective: {{
          title: selectedItem
            ? phrase("Review {{item}}", "审阅 {{item}}", {{ item: clampLabel(selectedItem.title || selectedItem.id, 18) }})
            : phrase("Review {{queue}} queue", "审阅 {{queue}} 队列", {{ queue: localizeWord(activeFilter) }}),
          copy: copy(
            "Triage is currently framing which inbox slice requires review before the operator decides on verification, duplicate handling, or story promotion.",
            "分诊区当前正在界定哪一段收件箱切片需要审阅，然后操作者才会决定是否进行核验、去重或故事提升。"
          ),
          facts: [
            {{ label: copy("Queue", "队列"), value: localizeWord(activeFilter) }},
            {{ label: copy("Search", "搜索"), value: clampLabel(searchValue, 24) || copy("none", "无") }},
            {{ label: copy("Selected", "当前条目"), value: selectedItem ? clampLabel(selectedItem.title || selectedItem.id, 24) : copy("none", "无") }},
          ],
        }},
        success: successSignal,
        blocker: blockerSignal,
      }});
    }}

    function renderStorySectionSummary({{
      filteredStories = [],
      activeStoryView = "all",
      storySort = "attention",
      storySearchValue = "",
    }} = {{}}) {{
      const selectedStory = getStoryRecord(state.selectedStoryId);
      const deliveryStatus = selectedStory ? getStoryDeliveryStatus(selectedStory) : null;
      const contradictionCount = selectedStory ? (selectedStory.contradictions || []).length : 0;
      const evidenceCount = selectedStory ? Number(selectedStory.item_count || 0) : 0;
      const timelineCount = selectedStory ? (selectedStory.timeline || []).length : 0;
      const blockerSignal = !state.stories.length
        ? {{
            title: copy("No persisted story snapshot exists yet", "当前还没有持久化故事快照"),
            copy: copy("Promote one triage item or seed a manual brief before the story lane can advance narrative work.", "先提升一条分诊证据或写下一条手工简报，故事工作线才能开始推进叙事工作。"),
            facts: [
              {{ label: copy("Stories", "故事数"), value: "0" }},
              {{ label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) }},
            ],
          }}
        : !filteredStories.length
          ? {{
              title: copy("Active story view returned zero matches", "当前故事视图没有返回任何匹配"),
              copy: copy("The story lane has persisted stories, but the active view or search is hiding the next narrative context.", "故事工作线里其实已经有持久化故事，但当前视图或搜索把下一段叙事上下文隐藏掉了。"),
              facts: [
                {{ label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) }},
                {{ label: copy("Search", "搜索"), value: clampLabel(storySearchValue, 24) }},
              ],
            }}
          : !selectedStory
            ? {{
                title: copy("Select one story to keep advancing", "先选中一条故事再继续推进"),
                copy: copy("The story lane is populated, but the workspace still needs one active story selection for evidence or editor detail.", "故事工作线已经有内容，但工作区仍然需要一条激活中的故事选择，才能展示证据或编辑细节。"),
                tone: "",
                facts: [
                  {{ label: copy("Shown", "显示"), value: String(filteredStories.length) }},
                  {{ label: copy("Sort", "排序"), value: storySortLabel(storySort) }},
                ],
              }}
            : contradictionCount
              ? {{
                  title: copy("Resolve contradiction markers before export", "导出前先处理冲突标记"),
                  copy: copy("This story is already selected, but contradiction markers still block confident promotion or export.", "当前故事已经选中，但冲突标记仍然会阻塞可信的提升或导出。"),
                  facts: [
                    {{ label: copy("Conflicts", "冲突数"), value: String(contradictionCount) }},
                    {{ label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") }},
                  ],
                }}
              : !evidenceCount
                ? {{
                    title: copy("Story still needs evidence context", "当前故事仍然缺少证据上下文"),
                    copy: copy("A story object exists, but evidence count is still empty, so narrative promotion is not yet grounded enough.", "当前已经存在故事对象，但证据数仍然为空，所以叙事提升还不够扎实。"),
                    facts: [
                      {{ label: copy("Evidence", "证据"), value: "0" }},
                      {{ label: copy("Timeline", "时间线"), value: String(timelineCount) }},
                    ],
                  }}
                : deliveryStatus?.key === "blocked"
                  ? {{
                      title: copy("Delivery gate is blocked for this story", "这条故事的交付门禁当前被阻塞"),
                      copy: copy("Evidence is present, but the delivery gate still reports a blocked state that needs operator review.", "当前故事已经有证据，但交付门禁仍然报告为阻塞状态，需要操作者复核。"),
                      facts: [
                        {{ label: copy("Delivery", "交付"), value: deliveryStatus.label }},
                        {{ label: copy("Evidence", "证据"), value: String(evidenceCount) }},
                      ],
                    }}
                  : {{
                      title: copy("Next prerequisite is export or downstream handoff", "下一个前提是导出或下游交接"),
                      copy: copy("The selected story is already grounded enough for the operator to choose between more editing and downstream handoff.", "当前选中的故事已经足够扎实，操作者只需要决定是继续编辑，还是直接进入下游交接。"),
                      tone: "",
                      facts: [
                        {{ label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") }},
                        {{ label: copy("Timeline", "时间线"), value: String(timelineCount) }},
                      ],
                    }};
      const successSignal = selectedStory && evidenceCount
        ? {{
            title: copy("Selected story already carries enough context to move", "当前选中的故事已经带着足够上下文继续推进"),
            copy: copy("Evidence, timeline, or delivery-readiness facts already make this story actionable inside the current workspace.", "证据、时间线或交付就绪度事实已经让这条故事在当前工作区里具备可操作性。"),
            tone: "ok",
            facts: [
              {{ label: copy("Evidence", "证据"), value: String(evidenceCount) }},
              {{ label: copy("Timeline", "时间线"), value: String(timelineCount) }},
              {{ label: copy("Delivery", "交付"), value: deliveryStatus?.label || copy("n/a", "暂无") }},
            ],
          }}
        : (filteredStories.length
          ? {{
              title: copy("Story board already has narrative candidates", "故事看板里已经有叙事候选项"),
              copy: copy("The story lane is populated, so operators can keep advancing narrative work without re-entering triage first.", "故事工作线已经有内容，操作者可以继续推进叙事工作，而不必先重新回到分诊。"),
              tone: "ok",
              facts: [
                {{ label: copy("Shown", "显示"), value: String(filteredStories.length) }},
                {{ label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) }},
                {{ label: copy("Sort", "排序"), value: storySortLabel(storySort) }},
              ],
            }}
          : {{
              title: copy("Story workspace controls are ready", "故事工作台控制已经就绪"),
              copy: copy("View presets, search, and editor mode are already mounted even when the active slice is empty.", "即使当前切片为空，视图预设、搜索和编辑模式也已经全部挂载完成。"),
              facts: [
                {{ label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) }},
                {{ label: copy("Search", "搜索"), value: clampLabel(storySearchValue, 24) || copy("none", "无") }},
              ],
            }});
      setSectionSummary("section-story", {{
        title: copy("Story Workspace Snapshot", "故事工作台摘要"),
        summary: copy(
          "Keep the current story objective, one success signal, and one blocker signal visible so narrative work stays grounded before export or delivery.",
          "把当前故事目标、一条成功信号和一条阻塞信号持续保持可见，让叙事工作在导出或交付前始终有事实锚点。"
        ),
        objective: {{
          title: selectedStory
            ? phrase("Advance {{story}}", "推进 {{story}}", {{ story: clampLabel(selectedStory.title || selectedStory.id, 18) }})
            : phrase("Review {{view}} stories", "审阅 {{view}} 故事", {{ view: storyViewPresetLabel(activeStoryView) }}),
          copy: copy(
            "Story Workspace is defining which story or evidence package is currently being advanced in board or editor mode.",
            "故事工作台当前正在界定哪条故事或证据包正在被推进，不管它处于看板模式还是编辑模式。"
          ),
          facts: [
            {{ label: copy("View", "视图"), value: storyViewPresetLabel(activeStoryView) }},
            {{ label: copy("Mode", "模式"), value: state.storyWorkspaceMode === "editor" ? copy("Editor", "编辑") : copy("Board", "看板") }},
            {{ label: copy("Selected", "当前故事"), value: selectedStory ? clampLabel(selectedStory.title || selectedStory.id, 24) : copy("none", "无") }},
          ],
        }},
        success: successSignal,
        blocker: blockerSignal,
      }});
    }}

    function renderOpsSectionSummary() {{
      const ops = state.ops || {{}};
      const status = ops.daemon || state.status || {{}};
      const collectorSummary = ops.collector_summary || {{}};
      const routeSummary = ops.route_summary || {{}};
      const routeTimeline = Array.isArray(ops.route_timeline) ? ops.route_timeline : [];
      const recentFailures = Array.isArray(ops.recent_failures) ? ops.recent_failures : [];
      const activeRoute = normalizeRouteName(state.contextRouteName);
      const activeRouteHealth = activeRoute ? getRouteHealthRow(activeRoute) : null;
      const blockerSignal = (routeSummary.degraded || 0) > 0 || (routeSummary.missing || 0) > 0
        ? {{
            title: copy("Route health requires remediation", "路由健康当前需要修复"),
            copy: copy("Degraded or missing routes are currently the dominant blocker in the delivery lane.", "降级或缺失的路由当前是交付工作线上的主要阻塞因素。"),
            facts: [
              {{ label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) }},
              {{ label: copy("Missing", "缺失"), value: String(routeSummary.missing || 0) }},
              {{ label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") }},
            ],
          }}
        : (collectorSummary.error || 0) > 0 || (collectorSummary.warn || 0) > 0
          ? {{
              title: copy("Collector health is degrading the lane", "采集器健康正在拖慢这条工作线"),
              copy: copy("Collector warnings or errors are currently the main operational blocker before delivery can be trusted again.", "在重新信任交付之前，采集器警告或错误是当前最主要的运行阻塞因素。"),
              facts: [
                {{ label: copy("Collector warn", "采集器警告"), value: String(collectorSummary.warn || 0) }},
                {{ label: copy("Collector error", "采集器错误"), value: String(collectorSummary.error || 0) }},
              ],
            }}
          : recentFailures.length
            ? {{
                title: copy("Recent failures still need review", "最近失败记录仍需复核"),
                copy: copy("The delivery lane has recent runtime failures that should be acknowledged before operators treat it as stable.", "当前交付工作线里还有最近的运行失败，在认定它稳定之前仍应先复核。"),
                facts: [
                  {{ label: copy("Recent failures", "最近失败"), value: String(recentFailures.length) }},
                  {{ label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") }},
                ],
              }}
            : !routeTimeline.length
              ? {{
                  title: copy("Trigger one routed delivery to seed live ops evidence", "先触发一次路由交付，沉淀实时运维证据"),
                  copy: copy("The ops lane is mounted, but it still needs at least one delivery event before route posture is fully observable.", "当前运维工作线已经挂载完成，但还需要至少一次交付事件，路由姿态才能完全可观测。"),
                  tone: "",
                  facts: [
                    {{ label: copy("Routes", "路由数"), value: String(state.routes.length || 0) }},
                    {{ label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") }},
                  ],
                }}
              : {{
                  title: copy("Next operational risk is route coverage drift", "下一个运行风险是路由覆盖漂移"),
                  copy: copy("No hard blocker is active right now, but operators should keep route usage and delivery posture in view.", "当前没有硬阻塞，但操作者仍应继续关注路由使用情况和整体交付姿态。"),
                  tone: "",
                  facts: [
                    {{ label: copy("Healthy", "健康"), value: String(routeSummary.healthy || 0) }},
                    {{ label: copy("Idle", "空闲"), value: String(routeSummary.idle || 0) }},
                  ],
                }};
      const successSignal = String(status.state || "").trim().toLowerCase() !== "error" && (((routeSummary.healthy || 0) > 0) || activeRouteHealth?.status === "healthy")
        ? {{
            title: copy("Delivery lane is healthy enough to trust", "交付工作线当前健康到可被信任"),
            copy: copy("Daemon state, route health, and recent delivery observations already show a live lane that operators can supervise with confidence.", "守护进程状态、路由健康和最近交付观察已经共同表明，这是一条可以被稳定监督的工作线。"),
            tone: "ok",
            facts: [
              {{ label: copy("Daemon", "守护进程"), value: localizeWord(status.state || "running") }},
              {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
              {{ label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") }},
            ],
          }}
        : {{
            title: copy("Ops surfaces are already mounted", "运维工作面已经全部挂载"),
            copy: copy("Daemon, route health, and delivery diagnostics are already available in one surface even before the lane turns fully healthy.", "即使当前工作线还没有完全转绿，守护进程、路由健康和交付诊断也已经都汇集到同一个面板里。"),
            facts: [
              {{ label: copy("Routes", "路由数"), value: String(state.routes.length || 0) }},
              {{ label: copy("Alerts", "告警数"), value: String(state.alerts.length || 0) }},
              {{ label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") }},
            ],
          }};
      setSectionSummary("section-ops", {{
        title: copy("Ops Snapshot Summary", "运维快照摘要"),
        summary: copy(
          "Keep route or delivery posture visible in one summary frame so operators can see what is healthy, what is blocked, and which route or lane they are supervising.",
          "把当前路由或交付姿态收进一个摘要框，让操作者快速看到什么是健康的、什么被阻塞，以及自己正在监督哪条路由或工作线。"
        ),
        objective: {{
          title: activeRoute
            ? phrase("Supervise {{route}}", "监督 {{route}}", {{ route: clampLabel(activeRoute, 18) }})
            : copy("Supervise current delivery posture", "监督当前交付姿态"),
          copy: copy(
            "Ops Snapshot is currently framing which route or delivery lane the operator is supervising across daemon, alert, and route facts.",
            "运维快照当前正在界定操作者正监督哪条路由或交付工作线，并把守护进程、告警和路由事实压到同一视图里。"
          ),
          facts: [
            {{ label: copy("Focused route", "当前路由"), value: activeRoute || copy("none", "无") }},
            {{ label: copy("Daemon", "守护进程"), value: localizeWord(status.state || "idle") }},
            {{ label: copy("Routes", "路由数"), value: String(state.routes.length || 0) }},
          ],
        }},
        success: successSignal,
        blocker: blockerSignal,
      }});
    }}

    function makeSurfaceAction(label, attrs = {{}}, extra = {{}}) {{
      return {{ label, attrs, ...extra }};
    }}

    function renderCardActionControl(action, tone = "secondary") {{
      if (!action || !action.label) {{
        return "";
      }}
      const className = tone === "primary" ? "btn-primary" : tone === "danger" ? "btn-danger" : "btn-secondary";
      const attrList = Object.entries(action.attrs || {{}})
        .filter(([, value]) => value !== null && value !== undefined && value !== false && value !== "")
        .map(([key, value]) => (value === true ? key : `${{key}}="${{escapeHtml(String(value))}}"`));
      if (action.href) {{
        attrList.push(`href="${{escapeHtml(String(action.href))}}"`);
        if (action.target) {{
          attrList.push(`target="${{escapeHtml(String(action.target))}}"`);
        }}
        if (action.rel) {{
          attrList.push(`rel="${{escapeHtml(String(action.rel))}}"`);
        }}
        return `<a class="${{className}}" data-action-tone="${{tone}}" ${{attrList.join(" ")}}>${{escapeHtml(action.label)}}</a>`;
      }}
      if (action.disabled) {{
        attrList.push("disabled");
      }}
      return `<button class="${{className}}" type="button" data-action-tone="${{tone}}" ${{attrList.join(" ")}}>${{escapeHtml(action.label)}}</button>`;
    }}

    function renderCardActionHierarchy({{ primary = null, secondary = [], danger = [] }} = {{}}) {{
      const sections = [];
      if (primary) {{
        sections.push(`
          <div class="actions action-primary-row" data-card-action-primary>
            ${{renderCardActionControl(primary, "primary")}}
          </div>
        `);
      }}
      const secondaryActions = secondary.filter(Boolean);
      if (secondaryActions.length) {{
        sections.push(`
          <div class="actions action-secondary-row" data-card-action-secondary>
            ${{secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}}
          </div>
        `);
      }}
      const dangerActions = danger.filter(Boolean);
      if (dangerActions.length) {{
        sections.push(`
          <div class="actions action-danger-row" data-card-action-danger>
            ${{dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}}
          </div>
        `);
      }}
      if (secondaryActions.length || dangerActions.length) {{
        sections.push(`
          <details class="action-sheet" data-card-action-sheet>
            <summary class="action-sheet-toggle">${{copy("More Actions", "更多操作")}}</summary>
            <div class="action-sheet-panel">
              ${{secondaryActions.length
                ? `<div class="actions action-secondary-row" data-card-action-sheet-secondary>
                    ${{secondaryActions.map((action) => renderCardActionControl(action, "secondary")).join("")}}
                  </div>`
                : ""}}
              ${{dangerActions.length
                ? `<div class="actions action-danger-row" data-card-action-sheet-danger>
                    ${{dangerActions.map((action) => renderCardActionControl(action, "danger")).join("")}}
                  </div>`
                : ""}}
            </div>
          </details>
        `);
      }}
      return sections.length ? `<div class="action-hierarchy">${{sections.join("")}}</div>` : "";
    }}

    function buildMissionGuidanceSurface(preview, suggestions = null) {{
      const draft = preview?.draft || defaultCreateWatchDraft();
      const warningItems = Array.isArray(suggestions?.warnings) ? suggestions.warnings : [];
      const reasons = [];
      const cadenceReason = [suggestions?.schedule_reason, suggestions?.platform_reason].filter(Boolean).join(" ");
      if (cadenceReason) {{
        reasons.push({{
          title: copy("Cadence and platform were derived from current repo state", "频率与平台建议来自当前仓库状态"),
          copy: cadenceReason,
          tone: "ok",
          facts: [
            {{ label: copy("Cadence", "频率"), value: suggestions?.recommended_schedule || preview?.scheduleLabel || "manual" }},
            {{ label: copy("Platform", "平台"), value: suggestions?.recommended_platform || draft.platform || copy("unset", "未设置") }},
          ],
          owner: copy("mission suggestions", "任务建议"),
        }});
      }}
      const routeReason = [suggestions?.route_reason, suggestions?.keyword_reason, suggestions?.domain_reason].filter(Boolean).join(" ");
      if (routeReason) {{
        reasons.push({{
          title: copy("Route and scope guidance stays tied to current delivery and duplicate pressure", "路由与范围建议继续绑定交付和重复压力"),
          copy: routeReason,
          tone: normalizeRouteName(suggestions?.recommended_route || draft.route) ? "ok" : "",
          facts: [
            {{ label: copy("Route", "路由"), value: suggestions?.recommended_route || draft.route || copy("unset", "未设置") }},
            {{ label: copy("Scope", "范围"), value: preview?.filtersLabel || copy("broad", "宽范围") }},
          ],
          owner: copy("mission suggestions", "任务建议"),
        }});
      }}
      if (warningItems.length) {{
        reasons.push({{
          title: copy("Current draft already has conflict or delivery pressure to watch", "当前草稿已经暴露出冲突或交付压力"),
          copy: warningItems.slice(0, 2).join(" "),
          tone: "hot",
          facts: [
            {{ label: copy("Warnings", "提醒"), value: String(warningItems.length) }},
            {{ label: copy("Readiness", "就绪度"), value: `${{preview?.readiness || 0}}%` }},
          ],
          owner: copy("mission suggestions", "任务建议"),
        }});
      }}
      if (!reasons.length) {{
        reasons.push({{
          title: copy("Current draft is still the primary mission fact source", "当前草稿本身仍是首要任务事实来源"),
          copy: preview?.summary || copy("Mission guidance stays lightweight until the draft accumulates enough scope or delivery context.", "在草稿积累到足够的范围或交付上下文之前，任务指引保持轻量。"),
          facts: [
            {{ label: copy("Name", "名称"), value: clampLabel(draft.name || copy("unset", "未设置"), 24) }},
            {{ label: copy("Query", "查询词"), value: clampLabel(draft.query || copy("unset", "未设置"), 24) }},
          ],
          owner: copy("mission brief", "任务概览"),
        }});
      }}

      const nextSteps = !preview?.requiredReady
        ? [{{
            title: copy("Complete Name and Query before expecting mission creation", "先补齐名称与查询词，再期待任务创建"),
            copy: copy("Mission Intake only needs the required fields first. Extra scope and delivery controls can remain empty until the draft is valid.", "任务录入区只要求先补齐必填字段。额外的范围和交付控制可以在草稿有效之后再决定。"),
            tone: "hot",
            facts: [
              {{ label: copy("Missing", "缺失"), value: !String(draft.name || "").trim() ? copy("name", "名称") : copy("query", "查询词") }},
            ],
            owner: copy("mission intake", "任务录入"),
          }}]
        : [{{
            title: preview?.alertArmed
              ? copy("Create or update the mission, then verify delivery posture in board or cockpit", "创建或更新任务后，再去任务列表或驾驶舱确认交付姿态")
              : copy("Create the mission first and add route wiring only when downstream delivery is required", "先创建任务；只有确实需要下游交付时再补路由"),
            copy: preview?.alertArmed
              ? copy("This draft already includes alert gates. After saving, the next hop is usually Mission Board or Cockpit rather than more intake edits.", "当前草稿已经包含告警门槛；保存后下一步通常是进入任务列表或驾驶舱，而不是继续改录入。")
              : copy("The draft is valid already. Keep the mission broad, run it once, and only add more delivery wiring if the resulting signal is worth downstream notification.", "当前草稿已经有效。先保持任务宽一些并执行一次，只有当结果值得通知下游时再补更多交付设置。"),
            tone: "ok",
            facts: [
              {{ label: copy("Ready", "就绪"), value: `${{preview?.readiness || 0}}%` }},
              {{ label: copy("Alert", "告警"), value: preview?.alertArmed ? copy("armed", "已启用") : copy("passive", "未启用") }},
            ],
            owner: copy("mission intake", "任务录入"),
          }}];

      const sources = [
        {{
          title: copy("Runtime suggestion facts stay owned by the mission suggestion payload", "运行时建议事实继续归任务建议载荷所有"),
          copy: copy("Cadence, route, duplicate pressure, and similar-mission warnings are projected from current watches and stories rather than invented by browser-only heuristics.", "频率、路由、重复压力和相似任务提醒都来自当前任务与故事投影，而不是浏览器本地臆测。"),
          owner: copy("runtime facts", "运行时事实"),
        }},
        {{
          title: copy("Field semantics still stay in the parameter guide", "字段语义仍然归参数说明文档所有"),
          copy: copy("Alert Route, domain, thresholds, digest defaults, and prompt-pack provenance rules remain documented in docs/datapulse_console_parameter_guide.md.", "告警路由、域名、阈值、digest 默认值和 prompt-pack 来源规则继续记录在 docs/datapulse_console_parameter_guide.md。"),
          owner: copy("static docs", "静态文档"),
        }},
      ];

      return renderOperatorGuidanceSurface({{
        surfaceId: "mission-guidance-surface",
        lane: "mission",
        title: copy("Mission Guidance Contract", "任务指引契约"),
        summary: suggestions?.summary || copy("Keep mission setup reasons and next-step wording persistent so operators do not have to infer intent from one-off hints or toast feedback.", "把任务设置的原因与下一步文案固定下来，避免操作者只能从零散提示或 toast 里猜测意图。"),
        reasons,
        nextSteps,
        sources,
        actionHierarchy: {{
          primary: preview?.requiredReady
            ? makeSurfaceAction(copy("Open Mission Board", "打开任务列表"), {{ "data-empty-jump": "section-board" }})
            : makeSurfaceAction(copy("Focus Mission Draft", "聚焦任务草稿"), {{ "data-empty-focus": "mission", "data-empty-field": !String(draft.name || "").trim() ? "name" : "query" }}),
          secondary: [
            makeSurfaceAction(copy("Focus Alert Route", "聚焦告警路由"), {{ "data-empty-focus": "mission", "data-empty-field": "route" }}),
            makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), {{ "data-empty-jump": "section-ops" }}),
          ],
        }},
      }});
    }}

    function buildCockpitGuidanceSurface(watch, {{ recentRuns = [], recentResults = [], recentAlerts = [], retryAdvice = null, deliveryStats = {{}} }} = {{}}) {{
      const reasons = [];
      if (retryAdvice) {{
        reasons.push({{
          title: copy("Retry guidance is already projecting the dominant mission blocker", "重试建议已经投射出当前任务的主要阻塞"),
          copy: retryAdvice.summary || copy("Latest failed run still needs operator remediation.", "最近失败执行仍需要操作者修复。"),
          tone: "hot",
          facts: [
            {{ label: copy("Retry", "重试"), value: retryAdvice.retry_command || copy("open guidance", "查看指引") }},
            {{ label: copy("Daemon", "守护进程"), value: retryAdvice.daemon_retry_command || "-" }},
          ],
          owner: copy("retry advice", "重试建议"),
        }});
      }}
      reasons.push({{
        title: recentResults.length
          ? copy("Current mission already has inspectable results", "当前任务已经有可检查的结果")
          : copy("Cockpit still shows the current mission posture even before results accumulate", "即使结果尚未积累，驾驶舱也会继续显示当前任务姿态"),
        copy: recentResults.length
          ? copy("Result stream, alert rules, and delivery stats are already enough to keep the mission in one inspectable surface.", "结果流、告警规则和交付统计已经足以把任务保持在一个可检查工作面里。")
          : copy("Run history, alert rules, and board context are already enough to keep the next action visible in Cockpit.", "执行历史、告警规则和任务列表上下文已经足以让驾驶舱显示下一步动作。"),
        tone: recentResults.length ? "ok" : "",
        facts: [
          {{ label: copy("Runs", "执行次数"), value: String(recentRuns.length || 0) }},
          {{ label: copy("Results", "结果数"), value: String(recentResults.length || 0) }},
          {{ label: copy("Alerts", "告警"), value: String(deliveryStats.recent_alert_count || recentAlerts.length || 0) }},
        ],
        owner: copy("mission cockpit", "任务驾驶舱"),
      }});

      const nextSteps = retryAdvice
        ? [{{
            title: copy("Use retry guidance before treating this mission as trustworthy again", "在重新信任这条任务前，先执行重试指引"),
            copy: copy("Fix the collector or credential issue first, then rerun the mission and re-check delivery posture from Cockpit.", "先修复采集器或凭据问题，再重新执行任务，并回到驾驶舱复核交付姿态。"),
            tone: "hot",
            facts: [
              {{ label: copy("Mission", "任务"), value: clampLabel(watch?.name || watch?.id || copy("selected", "当前任务"), 24) }},
              {{ label: copy("Alert rules", "告警规则"), value: String(watch?.alert_rule_count || 0) }},
            ],
            owner: copy("retry advice", "重试建议"),
          }}]
        : [{{
            title: recentResults.length
              ? copy("Review the result stream, then hand verified evidence into triage or delivery", "先看结果流，再把已确认信号交给分诊或交付")
              : copy("Run the mission once before expecting triage or delivery movement", "先执行一次任务，再期待分诊或交付推进"),
            copy: recentResults.length
              ? copy("Cockpit already has enough runtime facts. The next hop is usually Triage for verification or Ops for delivery inspection.", "驾驶舱已经有足够的运行事实；下一跳通常是进入分诊做核验，或进入运维看交付。")
              : copy("One successful run is enough to seed real evidence for the next lifecycle lanes.", "只要成功执行一次，就足以为后续生命周期工作线沉淀真实证据。"),
            tone: recentResults.length ? "ok" : "",
            facts: [
              {{ label: copy("Last run", "最近执行"), value: localizeWord(watch?.last_run_status || "idle") }},
              {{ label: copy("Recent alerts", "最近告警"), value: String(recentAlerts.length || 0) }},
            ],
            owner: copy("mission cockpit", "任务驾驶舱"),
          }}];

      const sources = [
        {{
          title: copy("Retry and delivery wording stays owned by runtime watch facts", "重试与交付文案继续归运行时任务事实所有"),
          copy: copy("Cockpit guidance reuses watch retry advice, recent alerts, and current run statistics instead of inventing a separate browser-only explanation layer.", "驾驶舱指引会复用任务重试建议、近期告警和当前执行统计，而不是再发明一层浏览器私有解释。"),
          owner: copy("runtime facts", "运行时事实"),
        }},
        {{
          title: copy("Alert field meaning still stays in the parameter guide", "告警字段含义仍然归参数说明文档所有"),
          copy: copy("Alert Route, domain, score gate, and confidence gate semantics remain documented centrally in docs/datapulse_console_parameter_guide.md.", "告警路由、域名、分数门槛和置信度门槛的含义仍集中写在 docs/datapulse_console_parameter_guide.md。"),
          owner: copy("static docs", "静态文档"),
        }},
      ];

      return renderOperatorGuidanceSurface({{
        surfaceId: "cockpit-guidance-surface",
        lane: "mission",
        title: copy("Mission Action Guidance", "任务动作指引"),
        summary: copy("Keep runtime reasons, retry posture, and the next cockpit handoff persistent so operators do not rely on transient success or error toasts.", "把运行原因、重试姿态和驾驶舱下一步交接固定下来，避免操作者只能依赖短暂的成功或错误 toast。"),
        reasons,
        nextSteps,
        sources,
        actionHierarchy: {{
          primary: retryAdvice
            ? makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), {{ "data-empty-jump": "section-ops" }})
            : recentResults.length
              ? makeSurfaceAction(copy("Open Triage", "打开分诊"), {{ "data-empty-jump": "section-triage" }})
              : watch?.enabled === false
                ? makeSurfaceAction(copy("Enable Mission", "启用任务"), {{ "data-watch-toggle": watch?.id || "", "data-watch-enabled": "0" }})
                : makeSurfaceAction(copy("Run Mission", "执行任务"), {{ "data-empty-run-watch": watch?.id || "" }}),
          secondary: [
            makeSurfaceAction(copy("Open Mission Board", "打开任务列表"), {{ "data-empty-jump": "section-board" }}),
            makeSurfaceAction(copy("Focus Alert Rules", "聚焦告警规则"), {{ "data-empty-focus": "mission", "data-empty-field": "route" }}),
          ],
        }},
      }});
    }}

    function buildTriageGuidanceSurface(item, linkedStories = [], duplicateExplain = null, nextHopActions = {{}}) {{
      const noteCount = Array.isArray(item?.review_notes) ? item.review_notes.length : 0;
      const candidateCount = Number(duplicateExplain?.candidate_count || 0);
      const reasons = [];
      if (candidateCount) {{
        reasons.push({{
          title: copy("Duplicate explain already surfaced merge pressure", "重复解释已经暴露出合并压力"),
          copy: copy("Keep the selected evidence here while comparing close matches so the queue can move without losing reasoning context.", "在比较相近候选时，把当前证据保留在这里，队列推进就不会丢失推理上下文。"),
          tone: "hot",
          facts: [
            {{ label: copy("Matches", "匹配数"), value: String(candidateCount) }},
            {{ label: copy("Primary", "主项"), value: duplicateExplain?.suggested_primary_id || copy("n/a", "暂无") }},
          ],
          owner: copy("duplicate explain", "重复解释"),
        }});
      }}
      reasons.push({{
        title: linkedStories.length
          ? copy("Story handoff is already visible for the selected evidence", "当前证据已经能直接看到故事交接")
          : copy("Reviewer context stays attached to the selected evidence", "审核上下文继续附着在当前证据上"),
        copy: linkedStories.length
          ? copy("Linked stories mean the operator can continue narrative work without re-finding this evidence later.", "已有的关联故事意味着操作者无需以后重新定位这条证据，就能继续推进叙事。")
          : copy("Notes, score, and queue state remain visible here so the next review action does not depend on list scanning alone.", "备注、分数和队列状态会留在这里，下一次审阅动作不必只靠扫列表决定。"),
        tone: linkedStories.length ? "ok" : "",
        facts: [
          {{ label: copy("Notes", "备注"), value: String(noteCount) }},
          {{ label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) }},
          {{ label: copy("State", "状态"), value: localizeWord(item?.review_state || "new") }},
        ],
        owner: copy("triage workspace", "分诊工作区"),
      }});

      const nextSteps = [{{
        title: candidateCount
          ? copy("Resolve duplicate status or keep the suggested primary before promotion", "在提升前先处理重复状态，或保留建议主项")
          : linkedStories.length
            ? copy("Continue from the linked story instead of restarting review from the queue", "直接沿关联故事继续推进，而不是从队列重新开始")
            : copy("Choose whether this evidence should be verified, escalated, or promoted next", "决定这条证据下一步该被核验、升级还是提升"),
        copy: candidateCount
          ? copy("Duplicate explain already loaded the nearby candidates. Use the action row below without leaving the current workbench.", "重复解释已经把相近候选载入；直接使用下方动作区，不必离开当前工作台。")
          : linkedStories.length
            ? copy("The story lane already knows about this evidence, so the queue can hand off without losing continuity.", "故事工作线已经认识这条证据，因此队列可以直接交接而不会丢失连续性。")
            : copy("The selected evidence is ready for one explicit decision. Keep the next move visible instead of relying on memory or one-off keyboard hints.", "当前证据已经准备好进入一个明确决策；把下一步保持可见，而不是依赖记忆或一次性快捷键提示。"),
        tone: candidateCount ? "hot" : "ok",
        facts: [
          {{ label: copy("Queue", "队列"), value: localizeWord(state.triageFilter || "open") }},
          {{ label: copy("Score", "分数"), value: String(item?.score || 0) }},
        ],
        owner: candidateCount ? copy("duplicate explain", "重复解释") : copy("triage workspace", "分诊工作区"),
      }}];

      const sources = [
        {{
          title: copy("Duplicate reasoning remains owned by duplicate explain", "重复推理继续归重复解释接口所有"),
          copy: copy("The browser only projects candidate counts, suggested primary, and similarity signals that already came from the triage explain endpoint.", "浏览器只投影来自 triage explain 接口的候选数、建议主项和相似度信号。"),
          owner: copy("runtime facts", "运行时事实"),
        }},
        {{
          title: copy("Reviewer notes remain the human-authored rationale surface", "审核备注仍然是人工填写的理由面"),
          copy: copy("Note capture stays visible beside the selected evidence so operator reasoning is not hidden behind a mutation toast.", "备注录入会和当前证据并排可见，操作者推理不会被隐藏在一次 mutation toast 之后。"),
          owner: copy("review notes", "审核备注"),
        }},
      ];

      return renderOperatorGuidanceSurface({{
        surfaceId: "triage-guidance-surface",
        lane: "triage",
        title: copy("Triage Action Guidance", "分诊动作指引"),
        summary: copy("Keep duplicate pressure, reviewer rationale, and the next triage move in one persistent surface while the list remains available for switching.", "把重复压力、审核理由和分诊下一步固定在一个持久面板里，同时保留列表用于切换条目。"),
        reasons,
        nextSteps,
        sources,
        actionHierarchy: nextHopActions,
      }});
    }}

    function buildStoryGuidanceSurface(story, storyDeliveryStatus) {{
      const evidenceCount = getStoryEvidenceIds(story).length;
      const contradictionCount = Array.isArray(story?.contradictions) ? story.contradictions.length : 0;
      const reasons = [{{
        title: contradictionCount
          ? copy("Contradiction markers are still shaping editorial confidence", "冲突标记仍在影响编辑可信度")
          : copy("Current story has enough grounded context to keep moving", "当前故事已经有足够的落地上下文继续推进"),
        copy: contradictionCount
          ? copy("Resolve the contradiction markers before treating this story as export-ready or delivery-safe.", "在把这条故事视为可导出或可交付之前，先处理冲突标记。")
          : copy("Evidence, timeline, and story status are already aligned enough to keep editorial work inside one workspace.", "证据、时间线和故事状态已经足够一致，可以继续在同一个工作区推进编辑。"),
        tone: contradictionCount ? "hot" : "ok",
        facts: [
          {{ label: copy("Evidence", "证据"), value: String(evidenceCount) }},
          {{ label: copy("Conflicts", "冲突"), value: String(contradictionCount) }},
          {{ label: copy("Delivery", "交付"), value: storyDeliveryStatus?.label || copy("n/a", "暂无") }},
        ],
        owner: copy("story snapshot", "故事快照"),
      }}];
      if (storyDeliveryStatus?.key === "blocked") {{
        reasons.push({{
          title: copy("Delivery gate is still explicitly blocked", "交付门禁仍然明确处于阻塞"),
          copy: copy("Story readiness exists, but downstream delivery posture still needs operator review before promotion or export.", "当前故事已经具备一定就绪度，但在提升或导出前，下游交付姿态仍需要操作者复核。"),
          tone: "hot",
          facts: [
            {{ label: copy("Status", "状态"), value: localizeWord(story?.status || "active") }},
            {{ label: copy("Updated", "更新"), value: formatCompactDateTime(story?.updated_at || story?.generated_at || "") }},
          ],
          owner: copy("story delivery status", "故事交付状态"),
        }});
      }}

      const nextSteps = [{{
        title: contradictionCount
          ? copy("Resolve contradictions or return to evidence before export", "导出前先处理冲突，或回到证据上下文")
          : storyDeliveryStatus?.key === "ready"
            ? copy("Choose between final edits and downstream delivery now", "现在就在最终编辑和下游交付之间做决定")
            : copy("Keep editing summary and status until delivery posture turns clear", "继续调整摘要和状态，直到交付姿态足够明确"),
        copy: contradictionCount
          ? copy("Use the contradiction and evidence stacks below to remove ambiguity before the story leaves the workspace.", "利用下方的冲突和证据堆栈先消除歧义，再让故事离开工作台。")
          : storyDeliveryStatus?.key === "ready"
            ? copy("This story already has the context needed for handoff. The remaining choice is whether to ship now or keep refining the wording.", "当前故事已经具备交接所需上下文，剩下只是在“现在交付”还是“继续润色”之间做选择。")
            : copy("The story can keep evolving here without losing evidence or timeline continuity.", "这条故事可以继续在这里演进，而不会丢失证据或时间线连续性。"),
        tone: contradictionCount || storyDeliveryStatus?.key === "blocked" ? "hot" : "ok",
        facts: [
          {{ label: copy("Timeline", "时间线"), value: String((story?.timeline || []).length) }},
          {{ label: copy("Entities", "实体"), value: String((story?.entities || []).length) }},
        ],
        owner: copy("story workspace", "故事工作台"),
      }}];

      const sources = [
        {{
          title: copy("Editorial guidance stays owned by persisted story facts", "编辑指引继续归持久化故事事实所有"),
          copy: copy("Story summary, contradiction markers, delivery posture, and evidence counts all come from the persisted story snapshot rather than browser-only staging text.", "故事摘要、冲突标记、交付姿态和证据计数都来自持久化故事快照，而不是浏览器私有暂存文案。"),
          owner: copy("runtime facts", "运行时事实"),
        }},
        {{
          title: copy("Route and delivery wording stays shared with the delivery lane", "路由与交付文案继续与交付工作线共享"),
          copy: copy("When the story points toward delivery, the browser keeps using the same route-health and delivery-posture semantics already visible in Ops.", "当故事进入交付判断时，浏览器继续沿用 Ops 里已经可见的路由健康和交付姿态语义。"),
          owner: copy("shared contract", "共享契约"),
        }},
      ];

      return renderOperatorGuidanceSurface({{
        surfaceId: "story-guidance-surface",
        lane: "story",
        title: copy("Story Action Guidance", "故事动作指引"),
        summary: copy("Keep editorial blockers, delivery posture, and the next narrative move explicit before the operator exports or hands the story downstream.", "在操作者导出或下游交接前，把编辑阻塞、交付姿态和叙事下一步明确显示出来。"),
        reasons,
        nextSteps,
        sources,
        actionHierarchy: {{
          primary: contradictionCount
            ? makeSurfaceAction(copy("Focus Evidence In Triage", "回查分诊证据"), {{ "data-empty-jump": "section-triage" }})
            : makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), {{ "data-empty-jump": "section-ops" }}),
          secondary: [
            makeSurfaceAction(copy("Preview Markdown", "预览 Markdown"), {{ "data-story-markdown": story?.id || "" }}),
            makeSurfaceAction(copy("Open Route Manager", "打开路由管理"), {{ "data-empty-focus": "route", "data-empty-field": "name" }}),
          ],
        }},
      }});
    }}

    function buildRouteGuidanceSurface({{ draft = {{}}, editing = false, health = null, usageCount = 0 }} = {{}}) {{
      const reasons = [];
      if (health && String(health.status || "").trim() && String(health.status || "").trim().toLowerCase() !== "healthy" && String(health.status || "").trim().toLowerCase() !== "idle") {{
        reasons.push({{
          title: copy("Route health is the main delivery-side explanation owner here", "路由健康是这里最主要的交付侧解释来源"),
          copy: health.last_error || health.last_summary || copy("Recent route events already indicate this sink needs review before operators trust it again.", "最近的路由事件已经表明，这个交付目标在重新被信任前需要复核。"),
          tone: "hot",
          facts: [
            {{ label: copy("Status", "状态"), value: localizeWord(health.status || "idle") }},
            {{ label: copy("Rate", "成功率"), value: formatRate(health.success_rate) }},
            {{ label: copy("Last", "最近"), value: formatCompactDateTime(health.last_event_at || "") }},
          ],
          owner: copy("route health", "路由健康"),
        }});
      }}
      reasons.push({{
        title: editing
          ? copy("Named routes keep mission references stable while the sink changes in place", "命名路由允许在原位改 sink，同时保持任务引用稳定")
          : copy("A named route becomes reusable mission delivery plumbing", "命名路由会沉淀成可复用的任务交付基础设施"),
        copy: editing
          ? copy("Route name remains fixed during edit, so existing mission alert rules keep resolving to the same route contract.", "编辑期间路由名称保持不变，因此已有任务的告警规则仍会解析到同一契约。")
          : copy("Create the sink once here, then reuse it from Mission Intake or Cockpit instead of retyping delivery details for every mission.", "先在这里把交付目标配置好，后续从任务录入区或驾驶舱直接复用，而不是每条任务都重填交付细节。"),
        tone: usageCount ? "ok" : "",
        facts: [
          {{ label: copy("Used", "已引用"), value: String(usageCount) }},
          {{ label: copy("Channel", "通道"), value: routeChannelLabel(draft.channel || "webhook") }},
          {{ label: copy("Route", "路由"), value: normalizeRouteName(draft.name) || copy("draft", "草稿") }},
        ],
        owner: copy("route manager", "路由管理"),
      }});

      let missingField = "";
      if (!String(draft.name || "").trim()) {{
        missingField = "name";
      }} else if (draft.channel === "webhook" && !String(draft.webhook_url || "").trim()) {{
        missingField = "webhook_url";
      }} else if (draft.channel === "feishu" && !String(draft.feishu_webhook || "").trim()) {{
        missingField = "feishu_webhook";
      }} else if (draft.channel === "telegram" && !String(draft.telegram_chat_id || "").trim()) {{
        missingField = "telegram_chat_id";
      }}
      const nextSteps = missingField
        ? [{{
            title: copy("Complete the route draft before expecting route-backed delivery", "先补齐路由草稿，再期待路由驱动的交付"),
            copy: copy("Route creation should stay explicit. Fill the required sink field for the chosen channel before binding missions to this route.", "路由创建应该保持明确可见；先补齐当前通道要求的目标字段，再把任务绑定到这条路由。"),
            tone: "hot",
            facts: [
              {{ label: copy("Missing field", "缺失字段"), value: missingField }},
              {{ label: copy("Channel", "通道"), value: routeChannelLabel(draft.channel || "webhook") }},
            ],
            owner: copy("route manager", "路由管理"),
          }}]
        : [{{
            title: health && String(health.status || "").trim().toLowerCase() === "healthy"
              ? copy("Attach this route to missions that now need downstream delivery", "把这条路由绑定到当前需要下游交付的任务")
              : copy("Save the route, then inspect mission and delivery posture from the same shell", "先保存路由，再在同一个控制台里检查任务和交付姿态"),
            copy: health && String(health.status || "").trim().toLowerCase() === "healthy"
              ? copy("This route already shows a healthy posture. The next move is usually to reuse it from mission alert rules.", "当前路由已经表现出健康姿态；下一步通常是从任务告警规则里复用它。")
              : copy("Once the route is saved, Mission Intake and Cockpit can reuse the same named sink without inventing another explanation layer.", "一旦路由保存完成，任务录入区和驾驶舱就能复用同一个命名 sink，而不需要另一套解释层。"),
            tone: health && String(health.status || "").trim().toLowerCase() === "healthy" ? "ok" : "",
            facts: [
              {{ label: copy("Used", "已引用"), value: String(usageCount) }},
              {{ label: copy("Focused route", "当前路由"), value: normalizeRouteName(draft.name) || copy("draft", "草稿") }},
            ],
            owner: health ? copy("route health", "路由健康") : copy("route manager", "路由管理"),
          }}];

      const sources = [
        {{
          title: copy("Route remediation wording remains owned by route health facts", "路由修复文案继续归路由健康事实所有"),
          copy: copy("Delivery failures, degraded status, and recent route event summaries keep coming from route health rather than browser-only heuristics.", "交付失败、降级状态和最近路由事件摘要继续来自 route health，而不是浏览器本地 heuristics。"),
          owner: copy("runtime facts", "运行时事实"),
        }},
        {{
          title: copy("Alert Route field meaning still stays in the parameter guide", "Alert Route 字段含义仍然归参数说明文档所有"),
          copy: copy("The route field remains a reusable named sink reference, as documented in docs/datapulse_console_parameter_guide.md.", "路由字段仍然表示可复用的命名交付目标，定义继续记录在 docs/datapulse_console_parameter_guide.md。"),
          owner: copy("static docs", "静态文档"),
        }},
      ];

      return renderOperatorGuidanceSurface({{
        surfaceId: "route-guidance-surface",
        lane: "route",
        title: copy("Route Action Guidance", "路由动作指引"),
        summary: copy("Keep route remediation, sink readiness, and mission attachment guidance persistent so delivery setup does not rely on ephemeral toast feedback.", "把路由修复、目标就绪度和任务绑定指引固定下来，避免交付设置只能依赖短暂 toast。"),
        reasons,
        nextSteps,
        sources,
        actionHierarchy: {{
          primary: missingField
            ? makeSurfaceAction(copy("Focus Route Draft", "聚焦路由草稿"), {{ "data-empty-focus": "route", "data-empty-field": missingField }})
            : makeSurfaceAction(copy("Focus Mission Draft", "聚焦任务草稿"), {{ "data-empty-focus": "mission", "data-empty-field": "route" }}),
          secondary: [
            makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), {{ "data-empty-jump": "section-ops" }}),
            editing ? makeSurfaceAction(copy("Use In Mission", "用于任务草稿"), {{ "data-route-apply": draft.name || "" }}) : null,
          ].filter(Boolean),
        }},
      }});
    }}

    function isHighRiskTriageItem(item) {{
      return Number(item?.score || 0) >= 80 || Number(item?.confidence || 0) >= 0.9;
    }}

    function getMissionCardActionHierarchy(watch) {{
      const enabled = Boolean(watch?.enabled);
      const lastStatus = String(watch?.last_run_status || "").trim().toLowerCase();
      const neverRun = !String(watch?.last_run_at || "").trim();
      const due = Boolean(watch?.is_due);
      const secondary = [];
      const danger = [];
      if (!watch || !watch.id) {{
        return {{ primary: null, secondary, danger }};
      }}
      const openCockpit = makeSurfaceAction(copy("Open Cockpit", "打开驾驶舱"), {{ "data-watch-open": watch.id }});
      const editMission = makeSurfaceAction(copy("Edit Mission", "编辑任务"), {{ "data-edit-watch": watch.id }});
      const runMission = makeSurfaceAction(copy("Run Mission", "执行任务"), {{ "data-run-watch": watch.id }});
      const retryMission = makeSurfaceAction(copy("Retry Mission", "重试任务"), {{ "data-run-watch": watch.id }});
      const enableMission = makeSurfaceAction(copy("Enable", "启用"), {{
        "data-watch-toggle": watch.id,
        "data-watch-enabled": "0",
      }});
      const disableMission = makeSurfaceAction(copy("Disable", "停用"), {{
        "data-watch-toggle": watch.id,
        "data-watch-enabled": "1",
      }});
      const deleteMission = makeSurfaceAction(copy("Delete", "删除"), {{ "data-delete-watch": watch.id }});
      if (!enabled) {{
        return {{
          primary: enableMission,
          secondary: [openCockpit, editMission],
          danger: [deleteMission],
        }};
      }}
      danger.push(disableMission, deleteMission);
      if (lastStatus === "error") {{
        secondary.push(openCockpit, editMission);
        return {{ primary: retryMission, secondary, danger }};
      }}
      if (due || neverRun) {{
        secondary.push(openCockpit, editMission);
        return {{ primary: runMission, secondary, danger }};
      }}
      secondary.push(runMission, editMission);
      return {{ primary: openCockpit, secondary, danger }};
    }}

    function getTriageCardActionHierarchy(item, linkedStories = []) {{
      const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
      const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
      const isOpenState = reviewState === "new" || reviewState === "triaged";
      const openStoryWorkspace = makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {{
        "data-empty-jump": "section-story",
        "data-story-workspace-mode": "editor",
      }});
      const createStory = makeSurfaceAction(copy("Create Story", "生成故事"), {{ "data-triage-story": item.id }});
      const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), {{ "data-triage-explain": item.id }});
      const verifyItem = makeSurfaceAction(copy("Verify", "核验"), {{
        "data-triage-state": "verified",
        "data-triage-id": item.id,
      }});
      const escalateItem = makeSurfaceAction(copy("Escalate", "升级"), {{
        "data-triage-state": "escalated",
        "data-triage-id": item.id,
      }});
      const ignoreItem = makeSurfaceAction(copy("Ignore", "忽略"), {{
        "data-triage-state": "ignored",
        "data-triage-id": item.id,
      }});
      const deleteItem = makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }});
      const storyAction = hasLinkedStory ? openStoryWorkspace : createStory;
      const danger = reviewState === "ignored" ? [deleteItem] : [ignoreItem, deleteItem];
      if (isOpenState && isHighRiskTriageItem(item)) {{
        return {{
          primary: escalateItem,
          secondary: [verifyItem, storyAction],
          danger,
        }};
      }}
      if (isOpenState) {{
        return {{
          primary: verifyItem,
          secondary: [escalateItem, storyAction],
          danger,
        }};
      }}
      if (reviewState === "verified" || reviewState === "escalated") {{
        return {{
          primary: storyAction,
          secondary: [explainDup, reviewState === "escalated" ? verifyItem : null].filter(Boolean).slice(0, 2),
          danger,
        }};
      }}
      return {{
        primary: hasLinkedStory ? openStoryWorkspace : explainDup,
        secondary: [storyAction, verifyItem],
        danger,
      }};
    }}

    function getTriageWorkbenchActionHierarchy(item, linkedStories = []) {{
      const base = getTriageCardActionHierarchy(item, linkedStories);
      const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
      const primary = hasLinkedStory
        ? makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {{
          "data-empty-jump": "section-story",
          "data-story-workspace-mode": "editor",
        }})
        : makeSurfaceAction(copy("Create Story", "生成故事"), {{ "data-triage-story": item.id }});
      const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), {{ "data-triage-explain": item.id }});
      const secondary = [];
      if (base.primary && base.primary.label !== primary.label) {{
        secondary.push(base.primary);
      }}
      secondary.push(explainDup);
      const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
      const danger = reviewState === "ignored"
        ? [makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }})]
        : [
            makeSurfaceAction(copy("Ignore", "忽略"), {{
              "data-triage-state": "ignored",
              "data-triage-id": item.id,
            }}),
            makeSurfaceAction(copy("Delete", "删除"), {{ "data-triage-delete": item.id }}),
          ];
      return {{
        primary,
        secondary: secondary.filter(Boolean).slice(0, 2),
        danger,
      }};
    }}

    function getStoryCardActionHierarchy(story) {{
      const archived = String(story?.status || "active").trim().toLowerCase() === "archived";
      return {{
        primary: makeSurfaceAction(copy("Open Story", "打开故事"), {{
          "data-story-open": story.id,
          "data-story-open-mode": state.storyWorkspaceMode,
        }}),
        secondary: [
          makeSurfaceAction(
            archived ? copy("Restore", "恢复") : copy("Archive", "归档"),
            {{
              "data-story-quick-status": story.id,
              "data-story-next-status": archived ? "active" : "archived",
            }},
          ),
          makeSurfaceAction(copy("Preview MD", "预览 MD"), {{ "data-story-preview": story.id }}),
        ],
        danger: [],
      }};
    }}

    function getRouteCardActionHierarchy(route, health = null, usageCount = 0) {{
      const routeName = String(route?.name || health?.name || "").trim();
      if (!routeName) {{
        return {{ primary: null, secondary: [], danger: [] }};
      }}
      const healthStatus = String(health?.status || route?.status || "idle").trim().toLowerCase() || "idle";
      const unhealthy = healthStatus && !["healthy", "idle"].includes(healthStatus);
      const editRoute = makeSurfaceAction(
        unhealthy ? copy("Inspect Route", "检查路由") : copy("Edit Route", "编辑路由"),
        {{ "data-route-edit": routeName }},
      );
      const attachRoute = makeSurfaceAction(copy("Attach To Mission", "绑定到任务"), {{ "data-route-attach": routeName }});
      const deleteRoute = makeSurfaceAction(copy("Delete", "删除"), {{ "data-route-delete": routeName }});
      if (unhealthy) {{
        return {{
          primary: editRoute,
          secondary: [attachRoute],
          danger: [deleteRoute],
        }};
      }}
      if (!usageCount) {{
        return {{
          primary: attachRoute,
          secondary: [editRoute],
          danger: [deleteRoute],
        }};
      }}
      return {{
        primary: editRoute,
        secondary: [attachRoute],
        danger: [deleteRoute],
      }};
    }}

    function renderOverview() {{
      const metrics = state.overview || {{}};
      if (state.loading.board && !state.overview) {{
        $("overview-metrics").innerHTML = [metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "...")].join("");
        renderTopbarContext();
        return;
      }}
      $("overview-metrics").innerHTML = [
        metricCard(copy("Enabled Missions", "已启用任务"), metrics.enabled_watches ?? 0),
        metricCard(copy("Due Now", "当前到点"), metrics.due_watches ?? 0, "hot"),
        metricCard(copy("Acted On Queue", "已处理队列"), metrics.triage_acted_on_count ?? 0),
        metricCard(copy("Stories", "故事"), metrics.story_count ?? 0),
        metricCard(copy("Ready Stories", "待交付故事"), metrics.story_ready_count ?? 0),
        metricCard(copy("Alert Routes", "告警路由"), metrics.route_count ?? 0),
        metricCard(copy("Open Queue", "待分诊队列"), metrics.triage_open_count ?? 0),
        metricCard(copy("Daemon State", "守护进程状态"), localizeWord(String(metrics.daemon_state || "idle")).toUpperCase()),
      ].join("");
      renderTopbarContext();
    }}

    function renderWatches() {{
      const root = $("watch-list");
      const searchValue = String(state.watchSearch || "");
      if (state.loading.board && !state.watches.length) {{
        renderBoardSectionSummary([], searchValue);
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      if (!state.watches.length) {{
        renderBoardSectionSummary([], searchValue);
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Start the lifecycle with one mission draft", "先用一个任务草稿启动生命周期"),
            summary: copy(
              "Name and Query are enough to create the first watch. Once it runs, the browser can guide you through triage, story promotion, and delivery setup without leaving this shell.",
              "只用名称和查询词就能先把第一个任务建起来。任务执行后，浏览器会继续把你带到分诊、故事沉淀和交付设置，不需要离开当前界面。"
            ),
            steps: [
              {{
                title: copy("Create Watch", "创建任务"),
                copy: copy("Use Mission Intake to create or clone the first watch.", "先在任务创建区新建或复制第一个任务。"),
              }},
              {{
                title: copy("Run From Board", "从列表执行"),
                copy: copy("Mission Board turns the draft into real evidence collection.", "任务列表会把草稿真正推进到实时证据采集。"),
              }},
              {{
                title: copy("Review In Triage", "进入分诊审阅"),
                copy: copy("Inbox items arrive in Triage after the first successful run.", "第一次成功执行后，收件箱条目会进入分诊队列。"),
              }},
              {{
                title: copy("Promote And Route", "提升并接入路由"),
                copy: copy("Stories and named routes matter once signal is worth downstream action.", "当信号值得触发下游动作时，再去沉淀故事和接入命名路由。"),
              }},
            ],
            actions: [
              {{ label: copy("Open Mission Draft", "打开任务草稿"), focus: "mission", field: "name", primary: true }},
              {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("No watch mission configured yet.", "当前还没有配置监测任务。")}}</div>`;
        wireLifecycleGuideActions(root);
        syncWatchUrlState();
        flushWatchUrlFocus();
        renderTopbarContext();
        return;
      }}
      const searchQuery = searchValue.trim().toLowerCase();
      const defaultWatchId = state.watches[0] ? state.watches[0].id : "";
      const filteredWatches = state.watches.filter((watch) => {{
        if (!searchQuery) {{
          return true;
        }}
        const haystack = [
          watch.id,
          watch.name,
          watch.query,
          ...(Array.isArray(watch.platforms) ? watch.platforms : []),
          ...(Array.isArray(watch.sites) ? watch.sites : []),
          watch.schedule,
          watch.schedule_label,
        ].join(" ").toLowerCase();
        return haystack.includes(searchQuery);
      }});
      renderBoardSectionSummary(filteredWatches, searchValue);
      const searchToolbar = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("mission search", "任务搜索")}}</div>
              <div class="panel-sub">${{copy("Search by name, query, id, platform, or site to narrow the board before acting.", "可按名称、查询词、任务 ID、平台或站点快速缩小任务列表。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredWatches.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.watches.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(searchValue)}}" data-watch-search placeholder="${{copy("Search missions", "搜索任务")}}">
            <button class="btn-secondary" type="button" data-watch-search-clear ${{searchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
        </div>
      `;
      if (!filteredWatches.length) {{
        root.innerHTML = `${{searchToolbar}}<div class="empty">${{copy("No mission matched the current search.", "没有任务匹配当前搜索。")}}</div>`;
        root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {{
          state.watchSearch = event.target.value;
          renderWatches();
        }});
        root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {{
          state.watchSearch = "";
          renderWatches();
        }});
        syncWatchUrlState({{ defaultWatchId }});
        flushWatchUrlFocus();
        return;
      }}
      root.innerHTML = `${{searchToolbar}}${{filteredWatches.map((watch) => {{
        const platforms = (watch.platforms || []).join(", ") || copy("any", "任意");
        const sites = (watch.sites || []).join(", ") || "-";
        const stateChip = watch.enabled ? "ok" : "";
        const dueChip = watch.is_due ? "hot" : "";
        const selected = watch.id === state.selectedWatchId ? "selected" : "";
        const actionHierarchy = getMissionCardActionHierarchy(watch);
        return `
          <div class="card selectable ${{selected}}">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{watch.name}}</h3>
                <div class="meta">
                  <span>${{watch.id}}</span>
                  <span>${{copy("schedule", "频率")}}=${{watch.schedule_label || watch.schedule || copy("manual", "手动")}}</span>
                  <span>${{copy("platforms", "平台")}}=${{platforms}}</span>
                  <span>${{copy("sites", "站点")}}=${{sites}}</span>
                </div>
              </div>
              <div style="display:grid; gap:6px; justify-items:end;">
                <span class="chip ${{stateChip}}">${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}</span>
                <span class="chip ${{dueChip}}">${{watch.is_due ? copy("due", "待执行") : copy("waiting", "等待")}}</span>
              </div>
            </div>
            <div class="meta">
              <span>${{copy("alert_rules", "告警规则")}}=${{watch.alert_rule_count || 0}}</span>
              <span>${{copy("last_run", "上次执行")}}=${{watch.last_run_at || "-"}}</span>
              <span>${{copy("status", "状态")}}=${{localizeWord(watch.last_run_status || "-")}}</span>
              <span>${{copy("next", "下次")}}=${{watch.next_run_at || "-"}}</span>
            </div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>`;
      }}).join("")}}`;

      root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {{
        state.watchSearch = event.target.value;
        renderWatches();
      }});
      root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {{
        state.watchSearch = "";
        renderWatches();
      }});

      root.querySelectorAll("[data-watch-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await loadWatch(button.dataset.watchOpen);
          }} catch (error) {{
            reportError(error, copy("Open mission", "打开任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-edit-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editMissionInCreateWatch(button.dataset.editWatch);
          }} catch (error) {{
            reportError(error, copy("Edit mission", "编辑任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-run-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.runWatch || "").trim();
          if (!identifier) {{
            return;
          }}
          button.disabled = true;
          try {{
            await triggerWatchRun(identifier);
          }} catch (error) {{
            reportError(error, copy("Run mission", "执行任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      bindWatchToggleButtons(root);

      root.querySelectorAll("[data-delete-watch]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const identifier = String(button.dataset.deleteWatch || "").trim();
          const removedWatch = state.watches.find((watch) => watch.id === identifier);
          const removedDetail = state.watchDetails[identifier] ? {{ ...state.watchDetails[identifier] }} : null;
          button.disabled = true;
          state.watches = state.watches.filter((watch) => watch.id !== identifier);
          delete state.watchDetails[identifier];
          if (state.selectedWatchId === identifier) {{
            state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
          }}
          renderWatches();
          renderWatchDetail();
          try {{
            await api(`/api/watches/${{identifier}}`, {{ method: "DELETE" }});
            pushActionEntry({{
              kind: "mission delete",
              label: `Deleted ${{removedWatch && removedWatch.name ? removedWatch.name : identifier}}`,
              detail: "Deletion is reversible from the recent action log.",
              undoLabel: "Restore",
              undo: async () => {{
                if (!removedWatch) {{
                  return;
                }}
                const payload = {{
                  name: String(removedWatch.name || identifier),
                  query: String(removedWatch.query || ""),
                  schedule: String(removedWatch.schedule || removedWatch.schedule_label || "manual"),
                  platforms: Array.isArray(removedWatch.platforms) ? removedWatch.platforms : [],
                  alert_rules: removedDetail && Array.isArray(removedDetail.alert_rules) ? removedDetail.alert_rules : [],
                }};
                await api("/api/watches", {{ method: "POST", payload }});
                await refreshBoard();
                showToast(`Mission restored: ${{payload.name}}`, "success");
              }},
            }});
            await refreshBoard();
          }} catch (error) {{
            if (removedWatch) {{
              state.watches = [removedWatch, ...state.watches];
            }}
            if (removedDetail) {{
              state.watchDetails[identifier] = removedDetail;
            }}
            reportError(error, "Delete mission");
            await refreshBoard();
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      syncWatchUrlState({{ defaultWatchId }});
      flushWatchUrlFocus();
      renderTopbarContext();
    }}

    async function loadWatch(identifier, {{ force = false }} = {{}}) {{
      const normalizedId = String(identifier || "").trim();
      if (!normalizedId) {{
        return null;
      }}
      state.selectedWatchId = normalizedId;
      state.loading.watchDetail = true;
      renderWatches();
      renderWatchDetail();
      try {{
        if (force || !state.watchDetails[normalizedId]) {{
          state.watchDetails[normalizedId] = await api(`/api/watches/${{normalizedId}}`);
        }}
      }} finally {{
        state.loading.watchDetail = false;
      }}
      setContextRouteFromWatch();
      renderWatches();
      renderWatchDetail();
      return state.watchDetails[normalizedId] || null;
    }}

    function renderWatchDetail() {{
      const root = $("watch-detail");
      renderFormSuggestionLists();
      const selected = state.selectedWatchId;
      const loadingWatch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected) || null;
      if (state.loading.watchDetail && selected) {{
        renderCockpitSectionSummary(loadingWatch);
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      const watch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected);
      if (!watch) {{
        renderCockpitSectionSummary(null);
        const firstWatch = state.watches[0] || null;
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Open one mission to move from draft into live evidence", "打开一个任务，把草稿推进到实时证据"),
            summary: copy(
              "Cockpit is the handoff point between mission setup and downstream review. Open a mission here to run it, inspect recent output, and decide whether triage or delivery needs attention next.",
              "任务详情是“创建任务”和“进入审阅”之间的交接点。先在这里打开一个任务，执行它、查看近期输出，再决定下一步是进入分诊还是补充交付设置。"
            ),
            steps: [
              {{
                title: copy("Open Cockpit", "打开任务详情"),
                copy: copy("Pick a mission from the board to inspect its current operating lane.", "先从任务列表里选中一个任务，查看它当前的运行状态。"),
              }},
              {{
                title: copy("Run Mission", "执行任务"),
                copy: copy("One run is enough to populate results, timeline, and future triage work.", "先执行一次任务，就能填充结果流、时间线和后续分诊工作。"),
              }},
              {{
                title: copy("Inspect Output", "检查输出"),
                copy: copy("Review result filters, retry guidance, and alert rules before you leave the cockpit.", "离开任务详情前，先看结果筛选、重试建议和告警规则。"),
              }},
              {{
                title: copy("Follow The Lifecycle", "沿生命周期推进"),
                copy: copy("From here, the next hop is usually Triage, then Stories, then route-backed delivery.", "从这里出发，通常下一站是分诊，然后是故事，最后才是路由交付。"),
              }},
            ],
            actions: [
              firstWatch
                ? {{ label: copy("Open First Mission", "打开第一个任务"), watch: firstWatch.id, primary: true }}
                : {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true }},
              {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("Select one mission from the board to inspect schedule, run history, and alert output.", "从看板中选择一个任务，以查看调度、执行历史和告警输出。")}}</div>`;
        wireLifecycleGuideActions(root);
        renderTopbarContext();
        return;
      }}
      const recentRuns = Array.isArray(watch.runs) ? watch.runs : [];
      const recentResults = Array.isArray(watch.recent_results) ? watch.recent_results : [];
      const recentAlerts = Array.isArray(watch.recent_alerts) ? watch.recent_alerts : [];
      const lastFailure = watch.last_failure || null;
      const retryAdvice = watch.retry_advice || null;
      const runStats = watch.run_stats || {{}};
      const resultStats = watch.result_stats || {{}};
      const visibleResultCount = Number(resultStats.visible_result_count);
      const deliveryStats = watch.delivery_stats || {{}};
      const resultFilters = watch.result_filters || {{}};
      const timelineEvents = Array.isArray(watch.timeline_strip) ? watch.timeline_strip : [];
      const stateOptions = Array.isArray(resultFilters.states) ? resultFilters.states : [];
      const sourceOptions = Array.isArray(resultFilters.sources) ? resultFilters.sources : [];
      const domainOptions = Array.isArray(resultFilters.domains) ? resultFilters.domains : [];
      const savedFilters = state.watchResultFilters[watch.id] || {{}};
      const normalizeFilterValue = (key, options) => {{
        const raw = String(savedFilters[key] || "all");
        return raw === "all" || options.some((option) => option.key === raw) ? raw : "all";
      }};
      const activeFilters = {{
        state: normalizeFilterValue("state", stateOptions),
        source: normalizeFilterValue("source", sourceOptions),
        domain: normalizeFilterValue("domain", domainOptions),
      }};
      state.watchResultFilters[watch.id] = activeFilters;
      const runsBlock = recentRuns.length
        ? recentRuns.map((run) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{run.status || "success"}}</h3>
                  <div class="meta">
                    <span>${{run.id || "-"}}</span>
                    <span>${{copy("trigger", "触发方式")}}=${{localizeWord(run.trigger || "manual")}}</span>
                    <span>${{copy("items", "条目")}}=${{run.item_count || 0}}</span>
                  </div>
                </div>
                <span class="chip ${{run.status === "success" ? "ok" : "hot"}}">${{localizeWord(run.status || "unknown")}}</span>
              </div>
              <div class="meta">
                <span>${{copy("started", "开始")}}=${{run.started_at || "-"}}</span>
                <span>${{copy("finished", "结束")}}=${{run.finished_at || "-"}}</span>
              </div>
              <div class="panel-sub">${{run.error || copy("No recorded error.", "没有记录到错误。")}}</div>
            </div>
          `).join("")
        : `
            <div class="card">
              <div class="mono">${{copy("no run yet", "尚未执行")}}</div>
              <div class="panel-sub">${{watch.enabled
                ? copy("Run this mission once to seed the triage queue, story workspace, and alert history with real evidence.", "先执行一次这个任务，分诊队列、故事工作台和告警历史才会开始出现真实证据。")
                : copy("This mission is paused. Enable it first so triage, story, and alert surfaces can start receiving real evidence again.", "这条任务当前已停用。请先启用，再让分诊、故事和告警面开始接收真实证据。")}}</div>
              <div class="actions" style="margin-top:12px;">
                ${{
                  watch.enabled
                    ? `<button class="btn-primary" type="button" data-empty-run-watch="${{escapeHtml(watch.id)}}">${{copy("Run Mission Now", "立即执行任务")}}</button>`
                    : `<button class="btn-primary" type="button" data-watch-toggle="${{escapeHtml(watch.id)}}" data-watch-enabled="0">${{copy("Enable Mission", "启用任务")}}</button>`
                }}
                <button class="btn-secondary" type="button" data-empty-jump="section-triage">${{copy("Open Triage", "打开分诊")}}</button>
              </div>
            </div>
          `;
      const alertsBlock = recentAlerts.length
        ? recentAlerts.map((alert) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{alert.rule_name}}</h3>
                  <div class="meta">
                    <span>${{alert.created_at || "-"}}</span>
                    <span>${{copy("items", "条目")}}=${{(alert.item_ids || []).length}}</span>
                  </div>
                </div>
                <span class="chip ${{alert.extra && alert.extra.delivery_errors ? "hot" : "ok"}}">${{(alert.delivered_channels || ["json"]).join(",")}}</span>
              </div>
              <div class="panel-sub">${{alert.summary || copy("No alert summary captured.", "没有记录到告警摘要。")}}</div>
            </div>
          `).join("")
        : `
            <div class="card">
              <div class="mono">${{copy("delivery is still quiet", "交付尚未启动")}}</div>
              <div class="panel-sub">${{copy("No recent alert event is recorded for this mission. Add or tune alert rules here, then attach a named route once the mission should notify downstream.", "这个任务近期还没有告警事件。先在这里补充或调整告警规则，等任务需要通知下游时，再绑定命名路由。")}}</div>
              <div class="actions" style="margin-top:12px;">
                <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${{copy("Open Route Manager", "打开路由管理")}}</button>
                <button class="btn-secondary" type="button" data-empty-jump="section-ops">${{copy("Open Delivery Surfaces", "打开交付视图")}}</button>
              </div>
            </div>
          `;
      const filteredResults = recentResults.filter((item) => {{
        const filters = item.watch_filters || {{}};
        if (activeFilters.state !== "all" && (filters.state || "new") !== activeFilters.state) {{
          return false;
        }}
        if (activeFilters.source !== "all" && (filters.source || "unknown") !== activeFilters.source) {{
          return false;
        }}
        if (activeFilters.domain !== "all" && (filters.domain || "unknown") !== activeFilters.domain) {{
          return false;
        }}
        return true;
      }});
      const filterGroups = [
        {{ key: "state", label: copy("state", "状态"), options: stateOptions }},
        {{ key: "source", label: copy("source", "来源"), options: sourceOptions }},
        {{ key: "domain", label: copy("domain", "域名"), options: domainOptions }},
      ];
      const filterWindowCount = Number(resultFilters.window_count || recentResults.length || 0);
      const filterBlock = filterGroups.map((group) => `
          <div class="stack">
            <div class="panel-sub">${{group.label}}</div>
            <div class="chip-row">
              <button class="chip-btn ${{activeFilters[group.key] === "all" ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="all">${{copy("all", "全部")}} (${{filterWindowCount}})</button>
              ${{group.options.map((option) => `
                <button class="chip-btn ${{activeFilters[group.key] === option.key ? "active" : ""}}" type="button" data-filter-group="${{group.key}}" data-filter-value="${{escapeHtml(option.key)}}">${{escapeHtml(localizeWord(option.label))}} (${{option.count || 0}})</button>
              `).join("")}}
            </div>
          </div>
        `).join("");
      const resultsBlock = filteredResults.length
        ? filteredResults.map((item) => `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{item.title}}</h3>
                  <div class="meta">
                    <span>${{item.id}}</span>
                    <span>${{copy("score", "分数")}}=${{item.score || 0}}</span>
                    <span>${{copy("confidence", "置信度")}}=${{Number(item.confidence || 0).toFixed(2)}}</span>
                    <span>${{item.source_name || item.source_type || "-"}}</span>
                  </div>
                </div>
                <span class="chip">${{localizeWord(item.review_state || "new")}}</span>
              </div>
              <div class="panel-sub">${{item.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No persisted result matched the active filter chips in the current mission window.", "当前任务窗口内没有结果匹配所选筛选条件。")}}</div>`;
      const timelineBlock = timelineEvents.length
        ? `<div class="timeline-strip">${{timelineEvents.map((event) => `
            <div class="timeline-event ${{event.tone || ""}}">
              <div class="card-top">
                <span class="chip ${{event.tone || ""}}">${{event.kind || "event"}}</span>
                <span class="panel-sub">${{event.time || "-"}}</span>
              </div>
              <div class="mono">${{event.label || "-"}}</div>
              <div class="panel-sub">${{event.detail || "-"}}</div>
            </div>
          `).join("")}}</div>`
        : `<div class="empty">${{copy("No mission timeline event captured yet.", "当前还没有记录到任务时间线事件。")}}</div>`;
      const retryCollectors = retryAdvice && Array.isArray(retryAdvice.suspected_collectors)
        ? retryAdvice.suspected_collectors
        : [];
      const retryNotes = retryAdvice && Array.isArray(retryAdvice.notes) ? retryAdvice.notes : [];
      const failureBlock = lastFailure
        ? `
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("latest failure", "最近失败")}}</h3>
                  <div class="meta">
                    <span>${{lastFailure.id || "-"}}</span>
                    <span>${{copy("status", "状态")}}=${{localizeWord(lastFailure.status || "error")}}</span>
                    <span>${{copy("trigger", "触发方式")}}=${{localizeWord(lastFailure.trigger || "manual")}}</span>
                    <span>${{copy("finished", "结束")}}=${{lastFailure.finished_at || "-"}}</span>
                  </div>
                </div>
                <span class="chip hot">${{retryAdvice && retryAdvice.failure_class ? retryAdvice.failure_class : localizeWord("error")}}</span>
              </div>
              <div class="panel-sub">${{lastFailure.error || copy("No failure message captured.", "没有记录到失败信息。")}}</div>
            </div>
          `
        : "";
      const retryAdviceBlock = retryAdvice
        ? `
            <div class="card">
              <div class="mono">${{copy("retry advice", "重试建议")}}</div>
              <div class="meta">
                <span>${{copy("retry", "重试")}}=${{retryAdvice.retry_command || "-"}}</span>
                <span>${{copy("daemon", "守护进程")}}=${{retryAdvice.daemon_retry_command || "-"}}</span>
              </div>
              <div class="panel-sub">${{retryAdvice.summary || copy("No retry guidance recorded.", "没有记录到重试建议。")}}</div>
              ${{
                retryCollectors.length
                  ? `<div class="stack" style="margin-top:12px;">${{retryCollectors.map((collector) => `
                      <div class="mini-item">${{collector.name}} | ${{collector.tier || "-"}} | ${{collector.status || "-"}} | available=${{collector.available}} | ${{collector.setup_hint || collector.message || "-"}}</div>
                    `).join("")}}</div>`
                  : ""
              }}
              ${{
                retryNotes.length
                  ? `<div class="stack" style="margin-top:12px;">${{retryNotes.map((note) => `<div class="mini-item">${{note}}</div>`).join("")}}</div>`
                  : ""
              }}
            </div>
          `
        : "";
      const triageSignal = getGovernanceSignal("triage_throughput");
      const storySignal = getGovernanceSignal("story_conversion");
      const routeSummary = state.ops?.route_summary || {{}};
      const missionContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Mission Continuity", "任务连续性"),
        summary: copy(
          "Mission output, review backlog, and downstream delivery facts stay visible together before you leave the cockpit.",
          "在离开任务详情之前，任务输出、审阅积压和下游交付事实会同时保持可见。"
        ),
        stages: [
          {{
            kicker: copy("Current", "当前"),
            title: copy("Mission Output", "任务输出"),
            copy: copy(
              "Runs, result filters, and retry context stay attached to the active mission instead of splitting into separate hops.",
              "执行记录、结果筛选和重试上下文会继续附着在当前任务上，而不是被拆成多个跳转。"
            ),
            tone: Number.isFinite(visibleResultCount) && visibleResultCount > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Visible results", "可见结果"), value: String(Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)) }},
              {{ label: copy("Filtered out", "已过滤"), value: String(resultStats.filtered_result_count || 0) }},
              {{ label: copy("Last run", "最近执行"), value: formatCompactDateTime(watch.last_run_at || recentRuns[0]?.finished_at || "") }},
            ],
          }},
          {{
            kicker: copy("Review", "审阅"),
            title: copy("Review Lane", "审阅工作线"),
            copy: copy(
              "Queue load and story carry-over stay visible here so you can decide whether this mission needs review attention next.",
              "这里直接保留队列压力和故事承接情况，方便判断这个任务下一步是否需要进入审阅。"
            ),
            tone: (state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) > 0 ? "hot" : "ok",
            facts: [
              {{ label: copy("Open queue", "开放队列"), value: String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) }},
              {{ label: copy("Acted on", "已处理"), value: String(state.overview?.triage_acted_on_count ?? triageSignal.acted_on_items ?? 0) }},
              {{ label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) }},
            ],
          }},
          {{
            kicker: copy("Delivery", "交付"),
            title: copy("Delivery Lane", "交付工作线"),
            copy: copy(
              "Alert events, ready stories, and healthy routes stay one glance away from the same mission.",
              "告警事件、待交付故事和健康路由会与同一任务保持一眼可见。"
            ),
            tone: (deliveryStats.recent_alert_count || 0) > 0 || (routeSummary.healthy || 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Recent alerts", "最近告警"), value: String(deliveryStats.recent_alert_count || 0) }},
              {{ label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Open Triage", "打开分诊"), section: "section-triage", primary: true }},
          {{ label: copy("Open Stories", "打开故事"), section: "section-story" }},
          {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
        ],
      }});
      const cockpitGuidanceBlock = buildCockpitGuidanceSurface(watch, {{
        recentRuns,
        recentResults,
        recentAlerts,
        retryAdvice,
        deliveryStats,
      }});
      renderCockpitSectionSummary(watch, {{
        recentRuns,
        recentResults,
        retryAdvice,
        lastFailure,
        deliveryStats,
      }});

      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
                <h3 class="card-title">${{watch.name}}</h3>
                <div class="meta">
                  <span>${{watch.id}}</span>
                  <span>${{copy("schedule", "频率")}}=${{watch.schedule_label || watch.schedule || copy("manual", "手动")}}</span>
                  <span>${{copy("next", "下次")}}=${{watch.next_run_at || "-"}}</span>
                  <span>${{copy("query", "查询")}}=${{watch.query || "-"}}</span>
                </div>
              </div>
            <span class="chip ${{watch.enabled ? "ok" : "hot"}}">${{watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}}</span>
          </div>
          <div class="meta">
            <span>${{copy("due", "到点")}}=${{localizeBoolean(watch.is_due)}}</span>
            <span>${{copy("alert_rules", "告警规则")}}=${{watch.alert_rule_count || 0}}</span>
            <span>${{copy("runs", "执行")}}=${{runStats.total || 0}}</span>
            <span>${{copy("success", "成功")}}=${{runStats.success || 0}}</span>
            <span>${{copy("errors", "错误")}}=${{runStats.error || 0}}</span>
            <span>${{copy("results", "结果")}}=${{Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)}}</span>
            <span>${{copy("alerts", "告警")}}=${{deliveryStats.recent_alert_count || 0}}</span>
          </div>
          <div class="actions" style="margin-top:12px;">
            <button class="btn-secondary" type="button" data-watch-edit="${{watch.id}}">${{copy("Edit Mission", "编辑任务")}}</button>
            ${{
              watch.enabled
                ? `<button class="btn-secondary" type="button" data-empty-run-watch="${{escapeHtml(watch.id)}}">${{copy("Run Mission", "执行任务")}}</button>`
                : `<button class="btn-secondary" type="button" data-watch-toggle="${{escapeHtml(watch.id)}}" data-watch-enabled="0">${{copy("Enable Mission", "启用任务")}}</button>`
            }}
            <button class="btn-secondary" type="button" data-empty-jump="section-triage">${{copy("Open Triage", "打开分诊")}}</button>
            <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${{copy("Focus Route Manager", "聚焦路由管理")}}</button>
          </div>
          <div class="panel-sub">${{watch.last_run_error || copy("Mission history and recent delivery outcomes are visible below.", "下方可查看任务历史和最近交付结果。")}}</div>
        </div>
        ${{missionContinuityBlock}}
        ${{cockpitGuidanceBlock}}
        ${{failureBlock}}
        ${{retryAdviceBlock}}
        <div class="card">
          <div class="mono">${{copy("timeline strip", "时间线")}}</div>
          <div class="panel-sub">${{copy("Recent run, result, and alert events are merged into one server-backed mission timeline.", "最近的运行、结果和告警事件会合并成一条服务端驱动的任务时间线。")}}</div>
          <div style="margin-top:12px;">
            ${{timelineBlock}}
          </div>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="mono">${{copy("recent runs", "最近执行")}}</div>
            ${{runsBlock}}
          </div>
          <div class="stack">
            <div class="mono">${{copy("recent alerts", "最近告警")}}</div>
            ${{alertsBlock}}
          </div>
        </div>
        <div class="stack">
          <div class="mono">${{copy("result stream", "结果流")}}</div>
          <div class="card">
            <div class="mono">${{copy("filter chips", "筛选标签")}}</div>
            <div class="panel-sub">${{copy("Filter the current persisted result window by review state, source, or domain without leaving the cockpit.", "在不离开驾驶舱的情况下，按审核状态、来源或域名筛选当前结果窗口。")}}</div>
            <div class="stack" style="margin-top:12px;">
              ${{filterBlock}}
            </div>
          </div>
          ${{resultsBlock}}
        </div>
        <div class="card">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("alert rule editor", "告警规则编辑器")}}</div>
              <div class="panel-sub">${{copy("Edit multiple console threshold rules for this mission, then replace the saved rule set in one write.", "可以在这里为任务编辑多条阈值规则，并一次性替换已保存的规则集。")}}</div>
            </div>
            <span class="chip">${{(watch.alert_rules || []).length}} ${{copy("rule(s)", "条规则")}}</span>
          </div>
          <form id="watch-alert-form" data-watch-id="${{watch.id}}">
            <div class="stack" id="watch-alert-rules">
              ${{
                ((watch.alert_rules || []).length ? watch.alert_rules : [{{}}]).map((rule, index) => `
                  <div class="card" data-alert-rule-card="${{index}}">
                    <div class="card-top">
                      <div>
                        <div class="mono">${{copy("rule", "规则")}} ${{index + 1}}</div>
                        <div class="panel-sub">${{copy("Current name", "当前名称")}}: ${{rule.name || "console-threshold"}}</div>
                      </div>
                      <button class="btn-secondary" type="button" data-remove-alert-rule="${{index}}">${{copy("Remove", "移除")}}</button>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Alert Route", "告警路由")}}<input name="route" list="route-options-list" placeholder="ops-webhook" value="${{(rule.routes || [])[0] || ""}}"></label>
                      <label>${{copy("Alert Keyword", "告警关键词")}}<input name="keyword" list="keyword-options-list" placeholder="launch" value="${{(rule.keyword_any || [])[0] || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Alert Domain", "告警域名")}}<input name="domain" list="domain-options-list" placeholder="openai.com" value="${{(rule.domains || [])[0] || ""}}"></label>
                      <label>${{copy("Min Score", "最低分数")}}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric" value="${{(rule.min_score || 0) || ""}}"></label>
                    </div>
                    <div class="field-grid">
                      <label>${{copy("Min Confidence", "最低置信度")}}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal" value="${{(rule.min_confidence || 0) || ""}}"></label>
                      <div class="stack">
                        <div class="panel-sub">${{copy("Channels are still pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}}</div>
                      </div>
                    </div>
                  </div>
                `).join("")
              }}
            </div>
            <div class="toolbar">
              <button class="btn-secondary" id="watch-alert-add" type="button">${{copy("Add Alert Rule", "新增告警规则")}}</button>
              <button class="btn-primary" type="submit">${{copy("Save Alert Rules", "保存告警规则")}}</button>
              <button class="btn-secondary" id="watch-alert-clear" type="button">${{copy("Clear Alert Rules", "清空告警规则")}}</button>
            </div>
          </form>
        </div>
      `;

      root.querySelectorAll("[data-filter-group]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const filterGroup = String(button.dataset.filterGroup || "").trim();
          if (!filterGroup) {{
            return;
          }}
          const current = state.watchResultFilters[watch.id] || {{ state: "all", source: "all", domain: "all" }};
          current[filterGroup] = String(button.dataset.filterValue || "all");
          state.watchResultFilters[watch.id] = current;
          renderWatchDetail();
        }});
      }});

      const alertForm = document.getElementById("watch-alert-form");
      const addRuleButton = document.getElementById("watch-alert-add");
      if (addRuleButton) {{
        addRuleButton.addEventListener("click", () => {{
          const rulesRoot = document.getElementById("watch-alert-rules");
          if (!rulesRoot) {{
            return;
          }}
          const nextIndex = rulesRoot.querySelectorAll("[data-alert-rule-card]").length;
          rulesRoot.insertAdjacentHTML("beforeend", `
            <div class="card" data-alert-rule-card="${{nextIndex}}">
              <div class="card-top">
                <div>
                  <div class="mono">${{copy("rule", "规则")}} ${{nextIndex + 1}}</div>
                  <div class="panel-sub">${{copy("New console threshold rule.", "新的控制台阈值规则。")}}</div>
                </div>
                <button class="btn-secondary" type="button" data-remove-alert-rule="${{nextIndex}}">${{copy("Remove", "移除")}}</button>
              </div>
              <div class="field-grid">
                <label>${{copy("Alert Route", "告警路由")}}<input name="route" list="route-options-list" placeholder="ops-webhook"></label>
                <label>${{copy("Alert Keyword", "告警关键词")}}<input name="keyword" list="keyword-options-list" placeholder="launch"></label>
              </div>
              <div class="field-grid">
                <label>${{copy("Alert Domain", "告警域名")}}<input name="domain" list="domain-options-list" placeholder="openai.com"></label>
                <label>${{copy("Min Score", "最低分数")}}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric"></label>
              </div>
              <div class="field-grid">
                <label>${{copy("Min Confidence", "最低置信度")}}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal"></label>
                <div class="stack">
                  <div class="panel-sub">${{copy("Channels stay pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}}</div>
                </div>
              </div>
            </div>
          `);
          rulesRoot.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {{
            button.onclick = () => {{
              button.closest("[data-alert-rule-card]")?.remove();
            }};
          }});
        }});
      }}
      root.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {{
        button.onclick = () => {{
          button.closest("[data-alert-rule-card]")?.remove();
        }};
      }});
      if (alertForm) {{
        alertForm.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const cards = Array.from(document.querySelectorAll("[data-alert-rule-card]"));
          const alertRules = cards.flatMap((card) => {{
            return buildAlertRules({{
              route: String(card.querySelector('[name=\"route\"]')?.value || "").trim(),
              keyword: String(card.querySelector('[name=\"keyword\"]')?.value || "").trim(),
              domain: String(card.querySelector('[name=\"domain\"]')?.value || "").trim(),
              minScore: Number(card.querySelector('[name=\"min_score\"]')?.value || 0),
              minConfidence: Number(card.querySelector('[name=\"min_confidence\"]')?.value || 0),
            }});
          }});
          const payload = {{
            alert_rules: alertRules,
          }};
          if (!payload.alert_rules.length) {{
            showToast(copy("Provide at least one route, keyword, domain, or threshold across the rule set.", "请至少提供一个路由、关键词、域名或阈值。"), "error");
            return;
          }}
          try {{
            await api(`/api/watches/${{watch.id}}/alert-rules`, {{
              method: "PUT",
              payload,
            }});
            await refreshBoard();
          }} catch (error) {{
            reportError(error, copy("Update alert rules", "更新告警规则"));
          }}
        }});
      }}

      const clearButton = document.getElementById("watch-alert-clear");
      if (clearButton) {{
        clearButton.addEventListener("click", async () => {{
          try {{
            await api(`/api/watches/${{watch.id}}/alert-rules`, {{
              method: "PUT",
              payload: {{ alert_rules: [] }},
            }});
            await refreshBoard();
          }} catch (error) {{
            reportError(error, copy("Clear alert rules", "清空告警规则"));
          }}
        }});
      }}

      root.querySelectorAll("[data-watch-edit]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editMissionInCreateWatch(String(button.dataset.watchEdit || "").trim());
          }} catch (error) {{
            reportError(error, copy("Edit mission", "编辑任务"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      wireLifecycleGuideActions(root);
      renderTopbarContext();
    }}

    function renderAlerts() {{
      const root = $("alert-list");
      if (state.loading.board && !state.alerts.length) {{
        root.innerHTML = [skeletonCard(3), skeletonCard(3)].join("");
        return;
      }}
      if (!state.alerts.length) {{
        root.innerHTML = `<div class="empty">${{copy("No alert event stored.", "当前没有告警事件。")}}</div>`;
        return;
      }}
      root.innerHTML = state.alerts.map((alert) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{alert.mission_name}}</h3>
              <div class="meta">
                <span>${{alert.rule_name}}</span>
                <span>${{alert.created_at || "-"}}</span>
              </div>
            </div>
            <span class="chip hot">${{(alert.delivered_channels || ["json"]).join(",")}}</span>
          </div>
          <div class="panel-sub">${{alert.summary || ""}}</div>
        </div>
      `).join("");
    }}

    async function submitRouteDeck(form) {{
      const draft = collectRouteDraft(form);
      state.routeDraft = draft;
      const editingId = normalizeRouteName(state.routeEditingId);
      let headers = null;
      try {{
        headers = parseRouteHeaders(draft.headers_json);
      }} catch (error) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Route draft is blocked by header formatting", "路由草稿被请求头格式阻塞"),
          copy: error.message,
          actionHierarchy: {{
            primary: {{
              label: copy("Fix Route Headers", "修正路由请求头"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "headers_json" }},
            }},
          }},
        }});
        showToast(error.message, "error");
        focusRouteDeck("headers_json");
        return;
      }}
      if (!draft.name.trim()) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Route draft still needs a name", "路由草稿仍然缺少名称"),
          copy: copy("Give the route a stable name before it can become a delivery surface.", "先给路由一个稳定名称，它才能成为可复用的交付目标。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Complete Route Draft", "继续补全路由草稿"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "name" }},
            }},
          }},
        }});
        showToast(copy("Provide a route name before saving.", "保存前请先填写路由名称。"), "error");
        focusRouteDeck("name");
        return;
      }}
      if (draft.channel === "webhook" && !draft.webhook_url.trim()) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Webhook route needs a destination", "Webhook 路由仍缺少目标地址"),
          copy: copy("Provide the webhook URL before this route can own delivery traffic.", "补上 webhook URL 后，这条路由才能承接交付流量。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Add Webhook URL", "填写 Webhook URL"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "webhook_url" }},
            }},
          }},
        }});
        showToast(copy("Webhook routes need a webhook URL.", "Webhook 路由需要填写 webhook URL。"), "error");
        focusRouteDeck("webhook_url");
        return;
      }}
      if (draft.channel === "feishu" && !draft.feishu_webhook.trim()) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Feishu route needs a destination", "飞书路由仍缺少目标地址"),
          copy: copy("Provide the Feishu webhook URL before this route can deliver alerts.", "补上飞书 webhook URL 后，这条路由才能投递告警。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Add Feishu URL", "填写飞书地址"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "feishu_webhook" }},
            }},
          }},
        }});
        showToast(copy("Feishu routes need a webhook URL.", "飞书路由需要填写 webhook URL。"), "error");
        focusRouteDeck("feishu_webhook");
        return;
      }}
      if (draft.channel === "telegram" && !draft.telegram_chat_id.trim()) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Telegram route needs a chat target", "Telegram 路由仍缺少会话目标"),
          copy: copy("Provide the chat ID before this route can deliver Telegram messages.", "补上 chat ID 后，这条路由才能投递 Telegram 消息。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Add Chat ID", "填写 Chat ID"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "telegram_chat_id" }},
            }},
          }},
        }});
        showToast(copy("Telegram routes need a chat ID.", "Telegram 路由需要填写 chat ID。"), "error");
        focusRouteDeck("telegram_chat_id");
        return;
      }}
      if (draft.channel === "telegram" && !editingId && !draft.telegram_bot_token.trim()) {{
        setStageFeedback("deliver", {{
          kind: "blocked",
          title: copy("Telegram route needs a bot token", "Telegram 路由仍缺少机器人 token"),
          copy: copy("A new Telegram route needs the bot token before it can become reusable.", "新建 Telegram 路由前必须提供 bot token，它才能成为可复用目标。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Add Bot Token", "填写 Bot Token"),
              attrs: {{ "data-empty-focus": "route", "data-empty-field": "telegram_bot_token" }},
            }},
          }},
        }});
        showToast(copy("Telegram routes need a bot token when created.", "创建 Telegram 路由时必须填写 bot token。"), "error");
        focusRouteDeck("telegram_bot_token");
        return;
      }}
      let timeoutSeconds = null;
      if (draft.timeout_seconds.trim()) {{
        timeoutSeconds = Number(draft.timeout_seconds);
        if (!(timeoutSeconds > 0)) {{
          setStageFeedback("deliver", {{
            kind: "blocked",
            title: copy("Route timeout is invalid", "路由超时时间无效"),
            copy: copy("Set the timeout to a value greater than zero before saving the route.", "保存路由前，请把超时时间设为大于零的值。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Fix Timeout", "修正超时时间"),
                attrs: {{ "data-empty-focus": "route", "data-empty-field": "timeout_seconds" }},
              }},
            }},
          }});
          showToast(copy("Timeout must be greater than 0.", "超时时间必须大于 0。"), "error");
          focusRouteDeck("timeout_seconds");
          return;
        }}
      }}

      const payload = {{
        channel: draft.channel,
      }};
      if (draft.description.trim()) {{
        payload.description = draft.description.trim();
      }}
      if (timeoutSeconds !== null) {{
        payload.timeout_seconds = timeoutSeconds;
      }}
      if (draft.channel === "webhook") {{
        payload.webhook_url = draft.webhook_url.trim();
        if (draft.authorization.trim()) {{
          payload.authorization = draft.authorization.trim();
        }}
        if (headers && Object.keys(headers).length) {{
          payload.headers = headers;
        }}
      }}
      if (draft.channel === "feishu") {{
        payload.feishu_webhook = draft.feishu_webhook.trim();
      }}
      if (draft.channel === "telegram") {{
        payload.telegram_chat_id = draft.telegram_chat_id.trim();
        if (draft.telegram_bot_token.trim()) {{
          payload.telegram_bot_token = draft.telegram_bot_token.trim();
        }}
      }}

      const submitButton = form?.querySelector("button[type='submit']");
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      try {{
        if (editingId) {{
          const updated = await api(`/api/alert-routes/${{editingId}}`, {{
            method: "PUT",
            payload,
          }});
          setContextRouteName(normalizeRouteName(updated.name), "section-ops");
          state.routeAdvancedOpen = null;
          setRouteDraft(defaultRouteDraft(), "");
          pushActionEntry({{
            kind: copy("route update", "路由修改"),
            label: state.language === "zh" ? `已更新路由：${{updated.name}}` : `Updated route: ${{updated.name}}`,
            detail: state.language === "zh"
              ? `通道：${{routeChannelLabel(updated.channel)}}`
              : `Channel: ${{routeChannelLabel(updated.channel)}}`,
          }});
          await refreshBoard();
          setStageFeedback("deliver", {{
            kind: "completion",
            title: state.language === "zh" ? `路由已更新：${{updated.name}}` : `Route updated: ${{updated.name}}`,
            copy: copy(
              "The delivery lane now exposes the updated route posture. Reuse it from monitoring when missions need downstream delivery.",
              "交付阶段现在已经反映更新后的路由姿态；当监测任务需要下游交付时，可以直接复用它。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
              secondary: [
                {{
                  label: copy("Use In Mission Draft", "用于任务草稿"),
                  attrs: {{ "data-empty-focus": "mission", "data-empty-field": "route" }},
                }},
              ],
            }},
          }});
          showToast(
            state.language === "zh" ? `路由已更新：${{updated.name}}` : `Route updated: ${{updated.name}}`,
            "success",
          );
          return;
        }}
        const created = await api("/api/alert-routes", {{
          method: "POST",
          payload: {{ name: draft.name.trim(), ...payload }},
        }});
        setContextRouteName(normalizeRouteName(created.name), "section-ops");
        const nextChannel = draft.channel;
        state.routeAdvancedOpen = null;
        setRouteDraft({{ ...defaultRouteDraft(), channel: nextChannel }}, "");
        pushActionEntry({{
          kind: copy("route create", "路由创建"),
          label: state.language === "zh" ? `已创建路由：${{created.name}}` : `Created route: ${{created.name}}`,
          detail: copy("The route is now available in mission alert rules and route quick-picks.", "该路由现在已可用于任务告警规则和快捷选择。"),
          undoLabel: copy("Delete route", "删除路由"),
          undo: async () => {{
            await api(`/api/alert-routes/${{created.name}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除路由：${{created.name}}` : `Route deleted: ${{created.name}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        setStageFeedback("deliver", {{
          kind: "completion",
          title: state.language === "zh" ? `路由已创建：${{created.name}}` : `Route created: ${{created.name}}`,
          copy: copy(
            "The route now belongs to the delivery lane and can be attached from Mission Intake or Cockpit.",
            "这条路由现在已经进入交付阶段，可以直接从任务录入区或驾驶舱里挂接。"
          ),
          actionHierarchy: {{
            primary: {{
              label: copy("Use In Mission Draft", "用于任务草稿"),
              attrs: {{ "data-empty-focus": "mission", "data-empty-field": "route" }},
            }},
            secondary: [
              {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            ],
          }},
        }});
        showToast(
          state.language === "zh" ? `路由已创建：${{created.name}}` : `Route created: ${{created.name}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Save route", "保存路由"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }}

    async function deleteRouteFromBoard(identifier) {{
      const normalized = normalizeRouteName(identifier);
      if (!normalized) {{
        return;
      }}
      const usageNames = getRouteUsageNames(normalized);
      const confirmation = usageNames.length
        ? copy(
            `Delete route ${{normalized}}? It is referenced by ${{usageNames.length}} mission(s): ${{usageNames.slice(0, 3).join(", ")}}.`,
            `确认删除路由 ${{normalized}}？它仍被 ${{usageNames.length}} 个任务引用：${{usageNames.slice(0, 3).join("、")}}。`,
          )
        : copy(
            `Delete route ${{normalized}}?`,
            `确认删除路由 ${{normalized}}？`,
          );
      if (!window.confirm(confirmation)) {{
        return;
      }}
      try {{
        const deleted = await api(`/api/alert-routes/${{normalized}}`, {{ method: "DELETE" }});
        if (normalizeRouteName(state.contextRouteName) === normalized) {{
          setContextRouteName("", "");
        }}
        if (normalizeRouteName(state.routeEditingId) === normalized) {{
          state.routeAdvancedOpen = null;
          setRouteDraft(defaultRouteDraft(), "");
        }}
        const createDraftRoute = normalizeRouteName(state.createWatchDraft?.route);
        if (createDraftRoute === normalized) {{
          updateCreateWatchDraft({{ route: "" }});
        }}
        pushActionEntry({{
          kind: copy("route delete", "路由删除"),
          label: state.language === "zh" ? `已删除路由：${{deleted.name}}` : `Deleted route: ${{deleted.name}}`,
          detail: usageNames.length
            ? copy("This route was still referenced by one or more missions. Review mission alert rules before the next run.", "该路由此前仍被任务引用，请在下一次执行前检查相关任务的告警规则。")
            : copy("Unused route removed from the delivery surface.", "未使用路由已从交付面移除。"),
        }});
        await refreshBoard();
        setStageFeedback("deliver", usageNames.length
          ? {{
              kind: "warning",
              title: state.language === "zh" ? `路由已删除：${{deleted.name}}` : `Route deleted: ${{deleted.name}}`,
              copy: copy(
                "The deleted route was still referenced by missions. Review mission alert rules before the next delivery run.",
                "被删除的路由此前仍被任务引用；请在下一次交付前检查相关任务的告警规则。"
              ),
              actionHierarchy: {{
                primary: {{
                  label: copy("Review Mission Drafts", "检查任务草稿"),
                  attrs: {{ "data-empty-focus": "mission", "data-empty-field": "route" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Delivery Lane", "打开交付工作线"),
                    attrs: {{ "data-empty-jump": "section-ops" }},
                  }},
                ],
              }},
            }}
          : {{
              kind: "completion",
              title: state.language === "zh" ? `路由已删除：${{deleted.name}}` : `Route deleted: ${{deleted.name}}`,
              copy: copy(
                "The unused route has been removed from the delivery lane.",
                "这条未使用路由已经从交付阶段移除。"
              ),
              actionHierarchy: {{
                primary: {{
                  label: copy("Create Route", "创建路由"),
                  attrs: {{ "data-empty-focus": "route", "data-empty-field": "name" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Delivery Lane", "打开交付工作线"),
                    attrs: {{ "data-empty-jump": "section-ops" }},
                  }},
                ],
              }},
            }});
        showToast(
          state.language === "zh" ? `路由已删除：${{deleted.name}}` : `Route deleted: ${{deleted.name}}`,
          "success",
        );
      }} catch (error) {{
        reportError(error, copy("Delete route", "删除路由"));
      }}
    }}

    function wireRouteSurfaceActions(root) {{
      if (!root) {{
        return;
      }}
      root.querySelectorAll("[data-route-edit]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await editRouteInDeck(String(button.dataset.routeEdit || ""));
          }} catch (error) {{
            reportError(error, copy("Edit route", "编辑路由"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-route-attach]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await applyRouteToMissionDraft(String(button.dataset.routeAttach || ""));
          }} catch (error) {{
            reportError(error, copy("Apply route", "应用路由"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-route-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await deleteRouteFromBoard(String(button.dataset.routeDelete || ""));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderRouteDeck() {{
      const root = $("route-deck");
      if (!root) {{
        return;
      }}
      const draft = normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
      const editingId = normalizeRouteName(state.routeEditingId);
      const editing = Boolean(editingId);
      const advancedOpen = isRouteAdvancedOpen(draft);
      const routeName = normalizeRouteName(editing ? editingId : draft.name);
      const usageCount = routeName ? getRouteUsageCount(routeName) : 0;
      const health = routeName ? getRouteHealthRow(routeName) : null;
      const routeGuidanceBlock = buildRouteGuidanceSurface({{ draft, editing, health, usageCount }});
      const advancedChips = [];
      if (draft.description.trim()) {{
        advancedChips.push(copy("description added", "已补充说明"));
      }}
      if (draft.authorization.trim()) {{
        advancedChips.push(copy("auth attached", "已附带认证"));
      }}
      if (draft.headers_json.trim()) {{
        advancedChips.push(copy("custom headers", "自定义请求头"));
      }}
      if (draft.timeout_seconds.trim()) {{
        advancedChips.push(phrase("timeout {{value}}s", "超时 {{value}} 秒", {{ value: draft.timeout_seconds.trim() }}));
      }}
      if (!advancedChips.length) {{
        advancedChips.push(copy("No advanced control yet", "当前没有高级设置"));
      }}

      root.innerHTML = `
        <form id="route-form">
          <div class="card-top">
            <div>
              <div class="mono">${{editing ? copy("route edit", "路由编辑") : copy("route create", "路由创建")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{editing ? escapeHtml(draft.name) : copy("Create Named Route", "创建命名路由")}}</h3>
            </div>
            <div style="display:grid; gap:6px; justify-items:end;">
              <span class="chip ${{health && health.status === "healthy" ? "ok" : health && health.status && health.status !== "idle" ? "hot" : ""}}">${{health ? localizeWord(health.status || "idle") : localizeWord(editing ? "editable" : "new")}}</span>
              <span class="chip">${{copy("used", "已引用")}}=${{usageCount}}</span>
            </div>
          </div>
          <div class="panel-sub">${{
            editing
              ? copy("Update the sink in place. Route name stays fixed so existing mission rules do not drift.", "原位更新交付路由。路由名称保持不变，避免已有任务规则漂移。")
              : copy("Add a reusable sink once, then pick it from mission alert rules and quick route chips.", "先把可复用的交付路由配置好，后续在任务告警规则和快捷路由里直接选择。")
          }}</div>
          <div class="chip-row" style="margin-top:4px;">
            ${{
              routeChannelOptions.map((option) => `
                <button
                  class="chip-btn ${{draft.channel === option.value ? "active" : ""}}"
                  type="button"
                  data-route-channel="${{option.value}}"
                >${{escapeHtml(copy(option.label, option.zhLabel || option.label))}}</button>
              `).join("")
            }}
          </div>
          <div class="field-grid" style="margin-top:2px;">
            <label>${{copy("Route Name", "路由名称")}}<input name="name" placeholder="ops-webhook" value="${{escapeHtml(draft.name)}}" ${{editing ? "readonly" : ""}}><span class="field-hint">${{editing ? copy("Name is fixed during edit so existing mission rules keep resolving.", "编辑时名称固定，避免已有任务规则失效。") : copy("Use a short reusable id, such as ops-webhook or exec-telegram.", "建议使用可复用的简短 ID，例如 ops-webhook 或 exec-telegram。")}}</span></label>
            <label>${{copy("Channel", "通道")}}<input name="channel" value="${{escapeHtml(routeChannelLabel(draft.channel))}}" readonly><span class="field-hint">${{copy("Change channel with the route type chips above.", "通过上方的路由类型按钮切换通道。")}}</span></label>
          </div>
          <div class="field-grid">
            ${{
              draft.channel === "webhook"
                ? `
                    <label>${{copy("Webhook URL", "Webhook URL")}}<input name="webhook_url" placeholder="https://hooks.example.com/ops" value="${{escapeHtml(draft.webhook_url)}}"><span class="field-hint">${{copy("Paste the receiver endpoint once, then reuse the route everywhere else.", "把接收端地址配置一次，后续在其他地方直接复用。")}}</span></label>
                    <label>${{copy("Destination Preview", "目标预览")}}<input value="${{escapeHtml(draft.webhook_url.trim() ? summarizeUrlHost(draft.webhook_url) : copy("Waiting for URL", "等待输入 URL"))}}" readonly><span class="field-hint">${{copy("Only the host preview is shown here to keep scanning fast.", "这里只显示主机预览，方便快速扫描。")}}</span></label>
                  `
                : draft.channel === "feishu"
                  ? `
                    <label>${{copy("Feishu Webhook", "飞书 Webhook")}}<input name="feishu_webhook" placeholder="https://open.feishu.cn/..." value="${{escapeHtml(draft.feishu_webhook)}}"><span class="field-hint">${{copy("Use the bot webhook issued by the target Feishu group.", "填写目标飞书群机器人提供的 webhook。")}}</span></label>
                    <label>${{copy("Destination Preview", "目标预览")}}<input value="${{escapeHtml(draft.feishu_webhook.trim() ? summarizeUrlHost(draft.feishu_webhook) : copy("Waiting for URL", "等待输入 URL"))}}" readonly><span class="field-hint">${{copy("Preview keeps the card readable without exposing the full URL at a glance.", "保留预览而不是完整地址，列表浏览时更轻量。")}}</span></label>
                  `
                  : draft.channel === "telegram"
                    ? `
                      <label>${{copy("Telegram Chat ID", "Telegram Chat ID")}}<input name="telegram_chat_id" placeholder="-1001234567890" value="${{escapeHtml(draft.telegram_chat_id)}}"><span class="field-hint">${{copy("The chat id remains visible so you can confirm the destination quickly.", "保留 chat id 可见，便于快速确认目标会话。")}}</span></label>
                      <label>${{copy("Bot Token", "Bot Token")}}<input name="telegram_bot_token" type="password" placeholder="${{editing ? copy("Leave blank to keep the current token", "留空则保留当前 token") : "123456:ABCDEF"}}" value="${{escapeHtml(draft.telegram_bot_token)}}"><span class="field-hint">${{editing ? copy("Leave blank to keep the existing bot token.", "留空会保留当前 bot token。") : copy("Required when the route is created.", "创建路由时必须填写。")}}</span></label>
                    `
                    : `
                      <label>${{copy("Markdown Delivery", "Markdown 交付")}}<input value="${{copy("Append alert summaries to the local markdown log.", "把告警摘要追加到本地 Markdown 日志。")}}" readonly><span class="field-hint">${{copy("Use this when operators want a file-backed trail with zero external dependency.", "当你需要零外部依赖的文件留痕时，用这个通道。")}}</span></label>
                      <label>${{copy("Destination Preview", "目标预览")}}<input value="${{copy("alerts.md append target", "alerts.md 追加目标")}}" readonly><span class="field-hint">${{copy("Markdown routes need no extra endpoint fields.", "Markdown 路由不需要额外的目标配置字段。")}}</span></label>
                    `
            }}
          </div>
          <div class="deck-mode-strip">
            <div class="deck-mode-head">
              <div>
                <div class="mono">${{copy("advanced controls", "高级设置")}}</div>
                <div class="panel-sub">${{copy("Keep advanced fields closed until you need auth headers, timeout control, or delivery notes.", "只有在需要认证、超时控制或交付备注时，再展开高级设置。")}}</div>
              </div>
              <button class="btn-secondary advanced-toggle" id="route-advanced-toggle" type="button" aria-expanded="${{String(advancedOpen)}}">${{advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置")}}</button>
            </div>
            <div class="chip-row advanced-summary">${{advancedChips.map((chip) => `<span class="chip">${{escapeHtml(chip)}}</span>`).join("")}}</div>
            <div class="deck-advanced-panel ${{advancedOpen ? "" : "collapsed"}}" aria-hidden="${{String(!advancedOpen)}}">
              <div class="field-grid">
                <label>${{copy("Description", "说明")}}<input name="description" placeholder="${{copy("Primary route for on-call ops", "值班运维主路由")}}" value="${{escapeHtml(draft.description)}}"><span class="field-hint">${{copy("Use one short note so operators know why this sink exists.", "补一句简短说明，让操作者知道这个路由的用途。")}}</span></label>
                <label>${{copy("Timeout Seconds", "超时秒数")}}<input name="timeout_seconds" inputmode="decimal" placeholder="10" value="${{escapeHtml(draft.timeout_seconds)}}"><span class="field-hint">${{copy("Optional override for slower receivers.", "当接收端偏慢时，可以单独覆盖超时时间。")}}</span></label>
              </div>
              ${{
                draft.channel === "webhook"
                  ? `
                      <div class="field-grid">
                        <label>${{copy("Authorization Header", "Authorization 请求头")}}<input name="authorization" type="password" placeholder="${{editing ? copy("Leave blank to keep current auth", "留空则保留当前认证") : "Bearer ..."}}" value="${{escapeHtml(draft.authorization)}}"><span class="field-hint">${{editing ? copy("Leave blank to keep the current secret.", "留空会保留当前密钥。") : copy("Optional bearer token or pre-shared auth header.", "可选的 bearer token 或预共享认证头。")}}</span></label>
                        <label>${{copy("Custom Headers JSON", "自定义请求头 JSON")}}<textarea name="headers_json" rows="4" placeholder='{{"X-Env":"prod"}}'>${{escapeHtml(draft.headers_json)}}</textarea><span class="field-hint">${{copy("Only include extra headers that are not already captured above.", "这里只填写上方未覆盖的额外请求头。")}}</span></label>
                      </div>
                    `
                  : ""
              }}
            </div>
          </div>
          <div class="toolbar">
            <button class="btn-primary" id="route-submit" type="submit">${{editing ? copy("Save Route", "保存路由") : copy("Create Route", "创建路由")}}</button>
            <button class="btn-secondary" id="route-clear" type="button">${{editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿")}}</button>
            ${{
              editing
                ? `<button class="btn-secondary" id="route-apply" type="button">${{copy("Use In Mission", "用于任务草稿")}}</button>`
                : ""
            }}
          </div>
        </form>
        ${{routeGuidanceBlock}}
      `;

      const form = $("route-form");
      form?.addEventListener("input", () => {{
        state.routeDraft = collectRouteDraft(form);
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        await submitRouteDeck(form);
      }});
      $("route-advanced-toggle")?.addEventListener("click", () => {{
        state.routeDraft = collectRouteDraft(form);
        state.routeAdvancedOpen = !isRouteAdvancedOpen(state.routeDraft || defaultRouteDraft());
        renderRouteDeck();
      }});
      root.querySelectorAll("[data-route-channel]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const nextChannel = String(button.dataset.routeChannel || "webhook").trim().toLowerCase();
          state.routeDraft = {{
            ...collectRouteDraft(form),
            channel: nextChannel,
          }};
          if (nextChannel !== "markdown") {{
            state.routeAdvancedOpen = true;
          }}
          renderRouteDeck();
        }});
      }});
      $("route-clear")?.addEventListener("click", () => {{
        const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
        state.routeAdvancedOpen = null;
        setRouteDraft(defaultRouteDraft(), "");
        showToast(
          wasEditing
            ? copy("Route edit cancelled", "已取消路由编辑")
            : copy("Route draft cleared", "已清空路由草稿"),
          "success",
        );
      }});
      root.querySelectorAll("[data-route-apply], #route-apply").forEach((button) => {{
        button.addEventListener("click", async () => {{
          await applyRouteToMissionDraft(String(button.dataset.routeApply || draft.name || "").trim());
        }});
      }});
      wireLifecycleGuideActions(root);
    }}

    function renderRouteHealth() {{
      const root = $("route-health");
      if (state.loading.board && !state.routeHealth.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      if (!state.routeHealth.length) {{
        root.innerHTML = `
          ${{renderLifecycleGuideCard({{
            title: copy("Delivery health appears after one named-route alert lands", "至少触发一次命名路由告警后，才会看到交付健康"),
            summary: copy(
              "Create a named route, attach it from Mission Intake or Cockpit alert rules, then let one alert flow through so this panel can report delivery quality.",
              "先创建命名路由，再从任务创建区或任务详情的告警规则里把它接上，等至少一条告警流过后，这里就会开始显示交付质量。"
            ),
            steps: [
              {{
                title: copy("Create Route", "创建路由"),
                copy: copy("Route Manager stores reusable delivery sinks inside the browser shell.", "路由管理会把可复用的交付目标直接保存在浏览器工作流里。"),
              }},
              {{
                title: copy("Attach To Mission", "绑定到任务"),
                copy: copy("Use Mission Intake or Cockpit alert rules to attach the named route.", "在任务创建区或任务详情的告警规则里绑定这个命名路由。"),
              }},
              {{
                title: copy("Trigger Alert", "触发告警"),
                copy: copy("One route-backed alert is enough to seed health and timeline facts.", "只要有一次带路由的告警，就足以开始沉淀健康和时间线事实。"),
              }},
            ],
            actions: [
              {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
              {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" }},
            ],
          }})}}
          <div class="empty">${{copy("No route health signal yet. Trigger named-route alerts to populate delivery quality.", "当前还没有路由健康信号。触发命名路由告警后会出现交付质量数据。")}}</div>`;
        wireLifecycleGuideActions(root);
        return;
      }}
      root.innerHTML = state.routeHealth.map((route) => {{
        const usageCount = Array.isArray(route.mission_ids) && route.mission_ids.length
          ? route.mission_ids.length
          : getRouteUsageCount(route.name);
        const actionHierarchy = getRouteCardActionHierarchy(route, route, usageCount);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{route.name}}</h3>
                <div class="meta">
                  <span>${{copy("channel", "通道")}}=${{routeChannelLabel(route.channel || "unknown")}}</span>
                  <span>${{copy("status", "状态")}}=${{localizeWord(route.status || "idle")}}</span>
                  <span>${{copy("rate", "成功率")}}=${{formatRate(route.success_rate)}}</span>
                </div>
              </div>
              <span class="chip ${{route.status === "healthy" ? "ok" : route.status === "idle" ? "" : "hot"}}">${{localizeWord(route.status || "idle")}}</span>
            </div>
            <div class="meta">
              <span>${{copy("events", "事件")}}=${{route.event_count || 0}}</span>
              <span>${{copy("delivered", "送达")}}=${{route.delivered_count || 0}}</span>
              <span>${{copy("failed", "失败")}}=${{route.failure_count || 0}}</span>
              <span>${{copy("last", "最近")}}=${{route.last_event_at || "-"}}</span>
            </div>
            <div class="panel-sub">${{route.last_error || route.last_summary || copy("No recent route delivery attempt recorded.", "近期没有记录到路由投递尝试。")}}</div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("");
      wireRouteSurfaceActions(root);
    }}

    function renderRoutes() {{
      const root = $("route-list");
      renderRouteDeck();
      if (state.loading.board && !state.routes.length) {{
        root.innerHTML = skeletonCard(3);
        return;
      }}
      const searchValue = String(state.routeSearch || "");
      const searchQuery = searchValue.trim().toLowerCase();
      const filteredRoutes = state.routes.filter((route) => {{
        if (!searchQuery) {{
          return true;
        }}
        const health = getRouteHealthRow(route.name);
        const haystack = [
          route.name,
          route.channel,
          route.description,
          route.webhook_url,
          route.feishu_webhook,
          route.telegram_chat_id,
          summarizeRouteDestination(route),
          health?.status,
          health?.last_error,
          ...getRouteUsageNames(route.name),
        ].join(" ").toLowerCase();
        return haystack.includes(searchQuery);
      }});
      const toolbox = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("route search", "路由搜索")}}</div>
              <div class="panel-sub">${{copy("Search by name, channel, destination, or attached mission before you edit or delete a route.", "可按名称、通道、目标地址或引用任务快速定位路由。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredRoutes.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.routes.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(searchValue)}}" data-route-search placeholder="${{copy("Search routes", "搜索路由")}}">
            <button class="btn-secondary" type="button" data-route-search-clear ${{searchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
        </div>
      `;
      if (!filteredRoutes.length) {{
        root.innerHTML = `${{toolbox}}${{
          state.routes.length
            ? ""
            : renderLifecycleGuideCard({{
                title: copy("Create one reusable route before missions need delivery", "在任务需要交付前，先准备一个可复用路由"),
                summary: copy(
                  "Routes are browser-managed delivery sinks. Create one here once, then attach it from Mission Intake or Cockpit alert rules instead of retyping destination details each time.",
                  "路由是浏览器内管理的交付目标。先在这里建一次，后续在任务创建区或任务详情的告警规则里直接绑定，不必每次重复填写目标信息。"
                ),
                steps: [
                  {{
                    title: copy("Create Named Sink", "创建命名目标"),
                    copy: copy("Give the route a stable name such as ops-webhook or exec-telegram.", "先给路由一个稳定的名字，比如 ops-webhook 或 exec-telegram。"),
                  }},
                  {{
                    title: copy("Attach In Mission", "在任务里绑定"),
                    copy: copy("Mission Intake and Cockpit reuse the route through Alert Route fields.", "任务创建区和任务详情会通过“告警路由”字段复用它。"),
                  }},
                  {{
                    title: copy("Monitor Health", "观察健康状态"),
                    copy: copy("Distribution Health and Alert Stream show whether downstream delivery is behaving.", "分发健康和告警动态会继续告诉你下游投递是否正常。"),
                  }},
                ],
                actions: [
                  {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
                  {{ label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" }},
                ],
              }})
        }}<div class="empty">${{state.routes.length ? copy("No route matched the current search.", "没有路由匹配当前搜索。") : copy("No named alert route configured yet. Start with one route so mission alerts can attach to a reusable sink.", "当前还没有配置命名告警路由。先创建一个路由，任务告警才能直接复用。")}}</div>`;
        wireLifecycleGuideActions(root);
        root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {{
          state.routeSearch = event.target.value;
          renderRoutes();
        }});
        root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {{
          state.routeSearch = "";
          renderRoutes();
        }});
        return;
      }}
      root.innerHTML = `${{toolbox}}${{filteredRoutes.map((route) => {{
        const health = getRouteHealthRow(route.name);
        const usageNames = getRouteUsageNames(route.name);
        const usageCount = usageNames.length;
        const healthTone = health?.status === "healthy" ? "ok" : health?.status && health.status !== "idle" ? "hot" : "";
        const destination = summarizeRouteDestination(route);
        const actionHierarchy = getRouteCardActionHierarchy(route, health, usageCount);
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${{escapeHtml(route.name || "unnamed-route")}}</h3>
                <div class="meta">
                  <span>${{copy("channel", "通道")}}=${{escapeHtml(routeChannelLabel(route.channel))}}</span>
                  <span>${{copy("used", "已引用")}}=${{usageCount}}</span>
                  <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(health?.status || "idle"))}}</span>
                </div>
              </div>
              <div style="display:grid; gap:6px; justify-items:end;">
                <span class="chip ${{healthTone}}">${{escapeHtml(localizeWord(health?.status || "idle"))}}</span>
                <span class="chip">${{escapeHtml(routeChannelLabel(route.channel))}}</span>
              </div>
            </div>
            <div class="panel-sub">${{escapeHtml(route.description || destination)}}</div>
            <div class="meta">
              <span>${{copy("destination", "目标")}}=${{escapeHtml(destination)}}</span>
              <span>${{copy("rate", "成功率")}}=${{formatRate(health?.success_rate)}}</span>
              <span>${{copy("last", "最近")}}=${{escapeHtml(health?.last_event_at || "-")}}</span>
            </div>
            ${{
              usageCount
                ? `<div class="panel-sub">${{copy("Used by", "正在被这些任务引用")}}: ${{escapeHtml(usageNames.slice(0, 3).join(", "))}}${{usageCount > 3 ? " ..." : ""}}</div>`
                : ""
            }}
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("")}}`;
      root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {{
        state.routeSearch = event.target.value;
        renderRoutes();
      }});
      root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {{
        state.routeSearch = "";
        renderRoutes();
      }});
      wireRouteSurfaceActions(root);
    }}

    function renderDeliveryWorkspace() {{
      const root = $("delivery-workspace-shell");
      if (!root) {{
        return;
      }}
      syncDeliveryDraft();
      syncDigestProfileDraft();
      syncDeliverySelectionState();
      if (state.loading.board && !state.deliverySubscriptions.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}

      const draft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
      state.deliveryDraft = draft;
      const digestConsole = state.digestConsole && typeof state.digestConsole === "object" ? state.digestConsole : {{}};
      const digestProjection = digestConsole.prepared_payload && typeof digestConsole.prepared_payload === "object"
        ? digestConsole.prepared_payload
        : {{}};
      const digestProfileShell = digestConsole.profile && typeof digestConsole.profile === "object"
        ? digestConsole.profile
        : {{}};
      const digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
      state.digestProfileDraft = digestProfileDraft;
      const digestBundle = digestProjection.content?.feed_bundle && typeof digestProjection.content.feed_bundle === "object"
        ? digestProjection.content.feed_bundle
        : {{}};
      const digestPromptConfig = digestProjection.prompts && typeof digestProjection.prompts === "object"
        ? digestProjection.prompts
        : {{}};
      const digestStats = digestProjection.stats && typeof digestProjection.stats === "object"
        ? digestProjection.stats
        : {{}};
      const digestProfile = digestProjection.config?.digest_profile && typeof digestProjection.config.digest_profile === "object"
        ? digestProjection.config.digest_profile
        : digestProfileDraft;
      const digestTarget = digestProfile.default_delivery_target && typeof digestProfile.default_delivery_target === "object"
        ? digestProfile.default_delivery_target
        : {{}};
      const digestRouteName = normalizeRouteName(digestTarget.ref || digestProfileDraft.default_delivery_target.ref);
      const digestRouteHealth = digestRouteName ? getRouteHealthRow(digestRouteName) : null;
      const digestBundleItems = Array.isArray(digestBundle.items) ? digestBundle.items.slice(0, 4) : [];
      const digestPromptFiles = Array.isArray(digestPromptConfig.files) ? digestPromptConfig.files.slice(0, 6) : [];
      const digestPromptOverrides = Array.isArray(digestPromptConfig.overrides_applied) ? digestPromptConfig.overrides_applied : [];
      const digestProjectionErrors = Array.isArray(digestProjection.errors) ? digestProjection.errors : [];
      const digestRouteDispatchRows = digestRouteName
        ? state.deliveryDispatchRecords.filter((row) => String(row.route_name || "").trim().toLowerCase() === digestRouteName).slice(0, 4)
        : [];
      const digestDispatchRows = Array.isArray(state.digestDispatchResult) ? state.digestDispatchResult : [];
      const subjectOptions = getDeliverySubjectRefOptions(draft.subject_kind);
      const outputOptions = getDeliveryOutputOptions(draft.subject_kind);
      const routeInputValue = draft.route_names.join(", ");
      const selectedSubscription = getSelectedDeliverySubscription();
      const selectedSubscriptionId = String(selectedSubscription?.id || "").trim();
      const selectedPackage = selectedSubscriptionId ? state.deliveryPackageAudits[selectedSubscriptionId] || null : null;
      const selectedPackageError = selectedSubscriptionId ? String(state.deliveryPackageErrors[selectedSubscriptionId] || "").trim() : "";
      const selectedReportProfiles = selectedSubscription && String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report"
        ? state.exportProfiles.filter((profile) => String(profile.report_id || "").trim() === String(selectedSubscription.subject_ref || "").trim())
        : [];
      const selectedProfileId = selectedSubscriptionId
        ? String(state.deliveryPackageProfileIds[selectedSubscriptionId] || "").trim()
        : "";
      const selectedDispatchRows = selectedSubscription ? getDeliveryDispatchRowsForSubscription(selectedSubscription.id).slice(0, 8) : [];
      const dispatchTimeline = selectedDispatchRows.length
        ? selectedDispatchRows.map((row) => `
            <div class="mini-item">${{row.route_label || row.route_name || "-"}} | ${{localizeWord(row.status || "pending")}} | ${{row.package_profile_id || copy("default", "默认")}}</div>
            <div class="panel-sub">${{row.error || row.package_id || copy("No package audit detail.", "当前没有包审计详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No dispatch audit recorded for the current selection.", "当前选中的订阅还没有 dispatch 审计记录。")}}</div>`;
      const inventoryRows = state.deliverySubscriptions.length
        ? state.deliverySubscriptions.map((subscription) => {{
            const subscriptionId = String(subscription.id || "").trim();
            const isSelected = subscriptionId === selectedSubscriptionId;
            const routeNames = Array.isArray(subscription.route_names) ? subscription.route_names : [];
            const auditCount = getDeliveryDispatchRowsForSubscription(subscriptionId).length;
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(summarizeDeliverySubject(subscription) || subscriptionId)}}</h3>
                    <div class="meta">
                      <span>${{formatDeliverySubjectKind(subscription.subject_kind)}}</span>
                      <span>${{formatDeliveryOutputKind(subscription.output_kind)}}</span>
                      <span>${{localizeWord(subscription.delivery_mode || "pull")}}</span>
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(subscription.status)}}">${{escapeHtml(localizeWord(subscription.status || "active"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(subscription.subject_ref || copy("No subject ref.", "没有 subject ref。"))}}</div>
                <div class="meta">
                  <span>${{copy("routes", "路由")}}=${{routeNames.length ? routeNames.join(", ") : copy("none", "无")}}</span>
                  <span>${{copy("cursor", "游标")}}=${{subscription.cursor_or_since || "-"}}</span>
                  <span>${{copy("audit", "审计")}}=${{auditCount}}</span>
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-delivery-select="${{escapeHtml(subscriptionId)}}">${{isSelected ? copy("Inspecting", "查看中") : copy("Inspect", "查看")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-toggle-status="${{escapeHtml(subscriptionId)}}" data-next-status="${{subscription.status === "active" ? "paused" : "active"}}">${{subscription.status === "active" ? copy("Pause", "暂停") : copy("Resume", "恢复")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-delete="${{escapeHtml(subscriptionId)}}">${{copy("Delete", "删除")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `${{renderLifecycleGuideCard({{
              title: copy("Create one persisted subscription before delivery turns into habit", "在交付进入常态前，先创建一个持久化订阅"),
              summary: copy(
                "Use the same Reader-backed delivery objects the API, CLI, and MCP already share. The browser should only project those persisted nouns.",
                "直接复用 API、CLI 和 MCP 已共享的 Reader-backed 交付对象。浏览器只负责投影这些持久化名词。"
              ),
              steps: [
                {{
                  title: copy("Pick Subject", "选择主体"),
                  copy: copy("Reports, stories, watch missions, and profile feeds all stay under one delivery contract.", "报告、故事、监控任务和配置订阅都共用同一套交付契约。"),
                }},
                {{
                  title: copy("Bind Route", "绑定路由"),
                  copy: copy("Push delivery stays attached to named routes instead of ad hoc browser state.", "推送交付继续绑定命名路由，而不是浏览器私有状态。"),
                }},
                {{
                  title: copy("Inspect Package", "检查包"),
                  copy: copy("Report subscriptions can preview the exact package before dispatch.", "报告订阅可以在 dispatch 前预览准确的输出包。"),
                }},
              ],
              actions: [
                {{ label: copy("Open Report Studio", "打开报告工作台"), section: "section-report-studio", primary: true }},
                {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name" }},
              ],
            }})}}`;
      const recentDispatchRows = state.deliveryDispatchRecords.length
        ? state.deliveryDispatchRecords.slice(0, 8).map((row) => `
            <div class="mini-item">${{row.route_label || row.route_name || "-"}} | ${{localizeWord(row.status || "pending")}} | ${{formatDeliveryOutputKind(row.output_kind)}}</div>
            <div class="panel-sub">${{row.subject_ref || "-"}} | ${{row.package_id || copy("No package id.", "没有 package id。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No delivery dispatch audit recorded yet.", "当前还没有记录到交付 dispatch 审计。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card" id="digest-console-card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Digest Command Surface", "摘要控制面")}}</h3>
                  <div class="panel-sub">${{copy("Edit the shared digest profile, inspect the replayable feed bundle, and surface prompt-pack plus route diagnostics over Reader-backed truth.", "直接编辑共享 digest_profile，查看可回放 feed_bundle，并把 prompt-pack 与路由诊断建立在 Reader 真实状态上。")}}</div>
                </div>
                <span class="chip ${{digestProfileShell.onboarding_status === "ready" ? "ok" : "hot"}}">${{digestProfileShell.onboarding_status === "ready" ? copy("Shared profile", "共享配置") : copy("Onboarding", "待初始化")}}</span>
              </div>
              <form id="digest-profile-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Language", "语言")}}<input name="language" value="${{escapeHtml(digestProfileDraft.language)}}" placeholder="en"></label>
                  <label>${{copy("Timezone", "时区")}}<input name="timezone" value="${{escapeHtml(digestProfileDraft.timezone)}}" placeholder="UTC"></label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Frequency", "频率")}}<input name="frequency" value="${{escapeHtml(digestProfileDraft.frequency)}}" placeholder="@daily"></label>
                  <label>${{copy("Default Route", "默认路由")}}
                    <select name="default_delivery_target_ref">
                      <option value="">${{copy("Select route", "选择路由")}}</option>
                      ${{state.routes.map((route) => {{
                        const routeName = normalizeRouteName(route.name);
                        return `<option value="${{escapeHtml(routeName)}}" ${{routeName === digestProfileDraft.default_delivery_target.ref ? "selected" : ""}}>${{escapeHtml(routeName)}}</option>`;
                      }}).join("")}}
                    </select>
                  </label>
                </div>
                <div class="meta">
                  <span>${{copy("status", "状态")}}=${{localizeWord(digestProfileShell.onboarding_status || "needs_setup")}}</span>
                  <span>${{copy("path", "路径")}}=${{escapeHtml(summarizePathTail(digestProfileShell.profile_path || "", 3) || "-")}}</span>
                  <span>${{copy("route", "路由")}}=${{escapeHtml(digestRouteName || copy("unset", "未设置"))}}</span>
                </div>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Save Shared Defaults", "保存共享默认值")}}</button>
                  <button class="btn-secondary" type="button" data-digest-refresh>${{copy("Refresh Preview", "刷新预览")}}</button>
                  <button class="btn-secondary" type="button" data-digest-dispatch ${{digestRouteName ? "" : "disabled"}}>${{copy("Dispatch Digest", "发送摘要")}}</button>
                </div>
              </form>
              <div class="graph-meta" style="margin-top:14px;">
                <div class="mini-list" id="digest-preview-feed">
                  <div class="mono">${{copy("Feed Bundle Preview", "Feed Bundle 预览")}}</div>
                  <div class="meta">
                    <span>${{copy("items", "条目")}}=${{digestStats.feed_bundle?.items_selected ?? digestBundle.stats?.items_selected ?? 0}}</span>
                    <span>${{copy("sources", "来源")}}=${{digestStats.feed_bundle?.sources_selected ?? digestBundle.stats?.sources_selected ?? 0}}</span>
                    <span>${{copy("window end", "窗口结束")}}=${{escapeHtml(digestBundle.window?.end_at || "-")}}</span>
                  </div>
                  ${{digestBundleItems.length
                    ? digestBundleItems.map((item) => `<div class="mini-item">${{escapeHtml(item.title || item.id || "-")}}</div><div class="panel-sub">${{escapeHtml(item.source_name || item.url || "-")}}</div>`).join("")
                    : `<div class="empty">${{copy("No feed-bundle item projected yet.", "当前还没有投影出 feed-bundle 条目。")}}</div>`}}
                </div>
                <div class="mini-list" id="digest-preview-prompts">
                  <div class="mono">${{copy("Prompt Readiness", "Prompt 就绪度")}}</div>
                  <div class="meta">
                    <span>${{copy("pack", "包")}}=${{escapeHtml(digestPromptConfig.repo_default_pack || "-")}}</span>
                    <span>${{copy("overrides", "覆盖")}}=${{digestPromptOverrides.length || 0}}</span>
                    <span>${{copy("files", "文件")}}=${{digestPromptFiles.length || 0}}</span>
                  </div>
                  <div class="panel-sub">${{escapeHtml((digestPromptConfig.override_order || []).join(" -> ") || copy("No prompt order projected.", "当前没有 prompt 顺序信息。"))}}</div>
                  ${{digestPromptFiles.length
                    ? digestPromptFiles.map((path) => `<div class="mini-item">${{escapeHtml(summarizePathTail(path, 3))}}</div>`).join("")
                    : `<div class="empty">${{copy("No prompt provenance file projected yet.", "当前还没有投影出 prompt 来源文件。")}}</div>`}}
                </div>
              </div>
              <div class="graph-meta" style="margin-top:14px;">
                <div class="mini-list" id="digest-route-diagnostics">
                  <div class="mono">${{copy("Route Diagnostics", "路由诊断")}}</div>
                  <div class="meta">
                    <span>${{copy("route", "路由")}}=${{escapeHtml(digestRouteName || copy("unset", "未设置"))}}</span>
                    <span>${{copy("health", "健康")}}=${{escapeHtml(localizeWord(digestRouteHealth?.status || "idle"))}}</span>
                    <span>${{copy("report audit", "报告审计")}}=${{digestRouteDispatchRows.length}}</span>
                  </div>
                  ${{digestDispatchRows.length
                    ? digestDispatchRows.map((row) => `<div class="mini-item">${{escapeHtml(row.route_label || row.route_name || "-")}} | ${{escapeHtml(localizeWord(row.status || "pending"))}}</div><div class="panel-sub">${{escapeHtml(row.governance?.delivery_diagnostics?.rendering?.selected_format || copy("Digest dispatch completed.", "摘要发送已完成。"))}}</div>`).join("")
                    : digestRouteDispatchRows.length
                      ? digestRouteDispatchRows.map((row) => `<div class="mini-item">${{escapeHtml(row.route_label || row.route_name || "-")}} | ${{escapeHtml(localizeWord(row.status || "pending"))}}</div><div class="panel-sub">${{escapeHtml(row.package_id || row.error || "-")}}</div>`).join("")
                      : `<div class="empty">${{escapeHtml(state.digestDispatchError || copy("No route-backed diagnostic row is visible yet. Dispatch once or inspect report-backed audit on the same route.", "当前还没有看到路由诊断记录。先发送一次摘要，或查看同一路由上的报告审计。"))}}</div>`}}
                </div>
                <div class="mini-list" id="digest-preview-errors">
                  <div class="mono">${{copy("Projection Notes", "投影说明")}}</div>
                  <div class="meta">
                    <span>${{copy("exists", "已持久化")}}=${{digestProfileShell.exists ? copy("yes", "是") : copy("no", "否")}}</span>
                    <span>${{copy("missing", "缺字段")}}=${{(digestProfileShell.missing_fields || []).length || 0}}</span>
                    <span>${{copy("errors", "错误")}}=${{digestProjectionErrors.length}}</span>
                  </div>
                  <div class="panel-sub">${{escapeHtml((digestProfileShell.missing_fields || []).join(", ") || copy("Shared digest defaults are projected from the persisted profile.", "共享 digest 默认值正从持久化 profile 投影而来。"))}}</div>
                  ${{digestProjectionErrors.length
                    ? digestProjectionErrors.map((error) => `<div class="mini-item">${{escapeHtml(error.code || "error")}}</div><div class="panel-sub">${{escapeHtml(error.message || "")}}</div>`).join("")
                    : `<div class="mini-item">${{copy("Route-backed digest dispatch stays on the same Reader nouns as CLI and MCP.", "摘要路由发送继续复用与 CLI / MCP 相同的 Reader 名词。")}}</div>`}}
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Subscription Intake", "订阅创建")}}</h3>
                  <div class="panel-sub">${{copy("Create one persisted delivery subscription in the same shell. No browser-only delivery state is introduced here.", "直接在同一个 shell 里创建持久化交付订阅；这里不会引入浏览器私有状态。")}}</div>
                </div>
                <span class="chip ok">${{copy("persisted", "持久化")}}</span>
              </div>
              <form id="delivery-subscription-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Subject Kind", "主体类型")}}
                    <select name="subject_kind">
                      ${{deliverySubjectOptions.map((value) => `<option value="${{value}}" ${{draft.subject_kind === value ? "selected" : ""}}>${{escapeHtml(formatDeliverySubjectKind(value))}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Subject Ref", "主体对象")}}
                    <select name="subject_ref">
                      ${{subjectOptions.map((option) => `<option value="${{escapeHtml(option.value)}}" ${{draft.subject_ref === option.value ? "selected" : ""}}>${{escapeHtml(option.label || option.value)}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Output Kind", "输出类型")}}
                    <select name="output_kind">
                      ${{outputOptions.map((option) => `<option value="${{option.value}}" ${{draft.output_kind === option.value ? "selected" : ""}}>${{escapeHtml(option.label)}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Delivery Mode", "交付模式")}}
                    <select name="delivery_mode">
                      ${{deliveryModeOptions.map((value) => `<option value="${{value}}" ${{draft.delivery_mode === value ? "selected" : ""}}>${{escapeHtml(localizeWord(value))}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <div class="field-grid">
                  <label>${{copy("Status", "状态")}}
                    <select name="status">
                      ${{deliveryStatusOptions.map((value) => `<option value="${{value}}" ${{draft.status === value ? "selected" : ""}}>${{escapeHtml(localizeWord(value))}}</option>`).join("")}}
                    </select>
                  </label>
                  <label>${{copy("Cursor Or Since", "游标或起点")}}<input name="cursor_or_since" placeholder="2026-03-01T00:00:00Z" value="${{escapeHtml(draft.cursor_or_since)}}"></label>
                </div>
                <label>${{copy("Route Names", "路由名称")}}<input name="route_names" placeholder="ops-webhook, exec-telegram" value="${{escapeHtml(routeInputValue)}}"><span class="field-hint">${{copy("Push delivery should reference one or more named routes. Pull delivery can leave this blank.", "推送交付应绑定一个或多个命名路由；拉取模式可以留空。")}}</span></label>
                <div class="chip-row" style="margin-top:4px;">
                  ${{state.routes.map((route) => {{
                    const routeName = normalizeRouteName(route.name);
                    const active = draft.route_names.includes(routeName);
                    return `<button class="chip-btn ${{active ? "active" : ""}}" type="button" data-delivery-route-toggle="${{escapeHtml(routeName)}}">${{escapeHtml(routeName)}}</button>`;
                  }}).join("") || `<span class="chip">${{copy("No route available yet", "当前还没有路由")}}</span>`}}
                </div>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Subscription", "创建订阅")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-reset>${{copy("Reset Draft", "重置草稿")}}</button>
                  <button class="btn-secondary" type="button" data-delivery-jump-report>${{copy("Open Report Studio", "打开报告工作台")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Package Audit", "报告包审计")}}</h3>
                  <div class="panel-sub">${{copy("Inspect the exact Reader-backed package before dispatch. This stays tied to the selected persisted subscription.", "在 dispatch 前检查准确的 Reader-backed 输出包，并始终绑定到当前选中的持久化订阅。")}}</div>
                </div>
                <span class="chip ${{selectedSubscription ? "ok" : ""}}">${{selectedSubscription ? escapeHtml(formatDeliveryOutputKind(selectedSubscription.output_kind)) : copy("No selection", "未选择")}}</span>
              </div>
              ${{selectedSubscription
                ? `
                  <div class="field-grid" style="margin-top:12px;">
                    <label>${{copy("Selected Subscription", "当前订阅")}}
                      <select id="delivery-subscription-select">
                        ${{state.deliverySubscriptions.map((subscription) => `<option value="${{escapeHtml(subscription.id)}}" ${{String(subscription.id || "").trim() === selectedSubscriptionId ? "selected" : ""}}>${{escapeHtml(summarizeDeliverySubject(subscription) || subscription.id)}}</option>`).join("")}}
                      </select>
                    </label>
                    <label>${{copy("Package Profile", "包配置")}}
                      <select id="delivery-package-profile-select" ${{String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report" ? "" : "disabled"}}>
                        <option value="">${{copy("Default package", "默认包")}}</option>
                        ${{selectedReportProfiles.map((profile) => `<option value="${{escapeHtml(profile.id)}}" ${{String(profile.id || "").trim() === selectedProfileId ? "selected" : ""}}>${{escapeHtml(profile.name || profile.id)}}</option>`).join("")}}
                      </select>
                    </label>
                  </div>
                  <div class="meta">
                    <span>${{formatDeliverySubjectKind(selectedSubscription.subject_kind)}}</span>
                    <span>${{escapeHtml(summarizeDeliverySubject(selectedSubscription))}}</span>
                    <span>${{copy("routes", "路由")}}=${{(selectedSubscription.route_names || []).join(", ") || copy("none", "无")}}</span>
                  </div>
                  ${{String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report"
                    ? `
                      <div class="actions">
                        <button class="btn-secondary" type="button" data-delivery-package-refresh="${{escapeHtml(selectedSubscriptionId)}}">${{copy("Refresh Package", "刷新输出包")}}</button>
                        <button class="btn-primary" type="button" data-delivery-dispatch="${{escapeHtml(selectedSubscriptionId)}}">${{copy("Dispatch Now", "立即 dispatch")}}</button>
                        <button class="btn-secondary" type="button" data-delivery-open-report="${{escapeHtml(selectedSubscription.subject_ref || "")}}">${{copy("Open Report Studio", "打开报告工作台")}}</button>
                      </div>
                      ${{
                        selectedPackage
                          ? `
                            <div class="meta">
                              <span>${{copy("package", "输出包")}}=${{escapeHtml(selectedPackage.package_id || "-")}}</span>
                              <span>${{copy("signature", "签名")}}=${{escapeHtml(selectedPackage.package_signature || "-")}}</span>
                              <span>${{copy("profile", "配置")}}=${{escapeHtml(selectedPackage.profile_id || copy("default", "默认"))}}</span>
                            </div>
                            <pre class="text-block">${{escapeHtml(JSON.stringify(selectedPackage.payload || {{}}, null, 2))}}</pre>
                          `
                          : selectedPackageError
                            ? `<div class="empty">${{escapeHtml(selectedPackageError)}}</div>`
                            : `<div class="empty">${{copy("Load one report-backed package to inspect the payload before dispatch.", "先加载一次报告输出包，再在 dispatch 前检查具体载荷。")}}</div>`
                      }}
                    `
                    : `
                      <div class="empty">${{copy("Package audit is only available for report subscriptions. The selected subscription remains persisted and auditable through dispatch records below.", "当前只有报告订阅支持 package 审计；已选中的其他订阅仍会通过下方 dispatch 记录保持可审计。")}}</div>
                    `}}
                `
                : `<div class="empty">${{copy("Select one subscription from the inventory on the right to inspect its package and dispatch audit.", "先从右侧库存里选中一个订阅，再查看它的输出包和 dispatch 审计。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            <div class="meta">
              <span class="mono">${{copy("subscription inventory", "订阅库存")}}</span>
              <span class="chip ok">${{copy("count", "数量")}}=${{state.deliverySubscriptions.length}}</span>
              <span class="chip">${{copy("dispatch", "dispatch")}}=${{state.deliveryDispatchRecords.length}}</span>
            </div>
            ${{inventoryRows}}
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Dispatch Audit", "Dispatch 审计")}}</h3>
                  <div class="panel-sub">${{copy("Route-backed dispatch stays attributable to one subscription and one package signature.", "路由驱动的 dispatch 会继续精确归因到具体订阅和具体包签名。")}}</div>
                </div>
                <span class="chip">${{selectedSubscription ? copy("selected focus", "当前聚焦") : copy("recent", "最近记录")}}</span>
              </div>
              <div class="mini-list">${{selectedSubscription ? dispatchTimeline : recentDispatchRows}}</div>
            </div>
          </div>
        </div>
      `;

      wireLifecycleGuideActions(root);
      const digestForm = root.querySelector("#digest-profile-form");
      digestForm?.addEventListener("input", () => {{
        state.digestProfileDraft = collectDigestProfileDraft(digestForm);
      }});
      digestForm?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const submitButton = digestForm.querySelector("button[type='submit']");
        const nextDraft = collectDigestProfileDraft(digestForm);
        state.digestProfileDraft = nextDraft;
        if (!nextDraft.default_delivery_target.ref) {{
          setStageFeedback("deliver", {{
            kind: "blocked",
            title: copy("Shared digest defaults still need a named route", "共享 digest 默认值仍缺少命名路由"),
            copy: copy("Pick one named route before this delivery default can persist on the stage-owned surface.", "请先选择一个命名路由，这组交付默认值才能持久化到当前阶段。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Focus Route Draft", "聚焦路由草稿"),
                attrs: {{ "data-empty-focus": "route", "data-empty-field": "name" }},
              }},
              secondary: [
                {{
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: {{ "data-empty-jump": "section-ops" }},
                }},
              ],
            }},
          }});
          showToast(copy("Choose one named route before saving shared digest defaults.", "保存共享 digest 默认值前请先选择一个命名路由。"), "error");
          return;
        }}
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const updated = await api("/api/digest-profile", {{
            method: "PUT",
            payload: nextDraft,
          }});
          state.digestProfileDraft = normalizeDigestProfileDraft(updated?.profile || nextDraft);
          await loadDigestConsole({{ preserveDraft: false }});
          setStageFeedback("deliver", {{
            kind: "completion",
            title: copy("Shared digest defaults saved", "共享 digest 默认值已保存"),
            copy: copy(
              "The delivery lane now keeps the shared digest route on the owned surface instead of leaving it in toast history.",
              "交付阶段现在已经把共享 digest 路由保留在拥有它的面板上，而不是只留在 toast 历史里。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Refresh Digest Preview", "刷新摘要预览"),
                attrs: {{ "data-digest-refresh": true }},
              }},
            }},
          }});
          showToast(copy("Shared digest defaults saved.", "共享 digest 默认值已保存。"), "success");
        }} catch (error) {{
          reportError(error, copy("Save digest profile", "保存 digest 配置"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("[data-digest-refresh]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadDigestConsole({{ preserveDraft: false }});
          showToast(copy("Digest preview refreshed.", "摘要预览已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh digest preview", "刷新摘要预览"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-digest-dispatch]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        state.digestDispatchError = "";
        try {{
          state.digestDispatchResult = await api("/api/digest/dispatch", {{
            method: "POST",
            payload: {{ profile: "default", limit: 8 }},
          }});
          renderDeliveryWorkspace();
          showToast(copy("Digest dispatch completed.", "摘要发送已完成。"), "success");
        }} catch (error) {{
          state.digestDispatchResult = [];
          state.digestDispatchError = error.message;
          renderDeliveryWorkspace();
          reportError(error, copy("Dispatch digest", "发送摘要"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      const form = root.querySelector("#delivery-subscription-form");
      form?.addEventListener("input", () => {{
        state.deliveryDraft = collectDeliveryDraft(form);
      }});
      form?.addEventListener("change", (event) => {{
        state.deliveryDraft = collectDeliveryDraft(form);
        const fieldName = String(event.target?.name || "").trim();
        if (fieldName === "subject_kind" || fieldName === "subject_ref" || fieldName === "delivery_mode") {{
          renderDeliveryWorkspace();
        }}
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const submitButton = form.querySelector("button[type='submit']");
        const nextDraft = collectDeliveryDraft(form);
        state.deliveryDraft = nextDraft;
        if (!nextDraft.subject_ref) {{
          setStageFeedback("deliver", {{
            kind: "blocked",
            title: copy("Delivery subscription still needs a subject", "交付订阅仍缺少主体对象"),
            copy: copy("Pick the report, story, profile, or mission that this delivery lane should own.", "请选择这条交付工作线要负责的报告、故事、配置或任务对象。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            }},
          }});
          showToast(copy("Pick one subject before saving the subscription.", "保存订阅前请先选择一个主体对象。"), "error");
          return;
        }}
        if (nextDraft.delivery_mode === "push" && !nextDraft.route_names.length) {{
          setStageFeedback("deliver", {{
            kind: "blocked",
            title: copy("Push delivery still needs a named route", "推送交付仍缺少命名路由"),
            copy: copy("Attach at least one named route before this subscription can dispatch downstream.", "请至少绑定一个命名路由，这条订阅才能向下游发送。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Focus Route Draft", "聚焦路由草稿"),
                attrs: {{ "data-empty-focus": "route", "data-empty-field": "name" }},
              }},
              secondary: [
                {{
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: {{ "data-empty-jump": "section-ops" }},
                }},
              ],
            }},
          }});
          showToast(copy("Push delivery needs at least one named route.", "推送交付至少需要绑定一个命名路由。"), "error");
          return;
        }}
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/delivery-subscriptions", {{
            method: "POST",
            payload: nextDraft,
          }});
          state.selectedDeliverySubscriptionId = String(created.id || "").trim();
          state.deliveryDraft = defaultDeliveryDraft();
          pushActionEntry({{
            kind: copy("delivery create", "交付创建"),
            label: state.language === "zh"
              ? `已创建订阅：${{summarizeDeliverySubject(created) || created.id}}`
              : `Created subscription: ${{summarizeDeliverySubject(created) || created.id}}`,
            detail: state.language === "zh"
              ? `输出：${{formatDeliveryOutputKind(created.output_kind)}}`
              : `Output: ${{formatDeliveryOutputKind(created.output_kind)}}`,
          }});
          await refreshBoard();
          setStageFeedback("deliver", {{
            kind: "completion",
            title: copy("Delivery subscription created", "交付订阅已创建"),
            copy: copy(
              "The delivery lane now owns a persisted subscription record. Inspect its package or dispatch it next.",
              "交付阶段现在已经拥有持久化订阅记录；下一步可以检查输出包，或直接执行 dispatch。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            }},
          }});
          showToast(copy("Delivery subscription created.", "交付订阅已创建。"), "success");
        }} catch (error) {{
          reportError(error, copy("Create delivery subscription", "创建交付订阅"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-delivery-route-toggle]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const routeName = normalizeRouteName(button.dataset.deliveryRouteToggle || "");
          const draftRoutes = state.deliveryDraft?.route_names || [];
          state.deliveryDraft = normalizeDeliveryDraft({{
            ...(state.deliveryDraft || draft),
            route_names: draftRoutes.includes(routeName)
              ? draftRoutes.filter((value) => value !== routeName)
              : [...draftRoutes, routeName],
          }});
          renderDeliveryWorkspace();
        }});
      }});
      root.querySelector("[data-delivery-reset]")?.addEventListener("click", () => {{
        state.deliveryDraft = defaultDeliveryDraft();
        renderDeliveryWorkspace();
        showToast(copy("Delivery draft reset.", "交付草稿已重置。"), "success");
      }});
      root.querySelector("[data-delivery-jump-report]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("#delivery-subscription-select")?.addEventListener("change", async (event) => {{
        state.selectedDeliverySubscriptionId = String(event.target.value || "").trim();
        renderDeliveryWorkspace();
        const subscription = getSelectedDeliverySubscription();
        if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {{
          try {{
            await loadDeliveryPackageAudit(subscription.id, {{
              profileId: String(state.deliveryPackageProfileIds[subscription.id] || "").trim(),
            }});
          }} catch (error) {{
            reportError(error, copy("Load report package", "加载报告输出包"));
          }}
        }}
      }});
      root.querySelector("#delivery-package-profile-select")?.addEventListener("change", async (event) => {{
        const subscription = getSelectedDeliverySubscription();
        if (!subscription) {{
          return;
        }}
        const profileId = String(event.target.value || "").trim();
        state.deliveryPackageProfileIds[String(subscription.id || "").trim()] = profileId;
        try {{
          await loadDeliveryPackageAudit(subscription.id, {{ profileId }});
        }} catch (error) {{
          reportError(error, copy("Load report package", "加载报告输出包"));
        }}
      }});
      root.querySelector("[data-delivery-package-refresh]")?.addEventListener("click", async (event) => {{
        const subscriptionId = String(event.currentTarget.dataset.deliveryPackageRefresh || "").trim();
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadDeliveryPackageAudit(subscriptionId, {{
            profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
          }});
          showToast(copy("Report package refreshed.", "报告输出包已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh report package", "刷新报告输出包"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-delivery-dispatch]")?.addEventListener("click", async (event) => {{
        const subscriptionId = String(event.currentTarget.dataset.deliveryDispatch || "").trim();
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          const profileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
          await api(`/api/delivery-subscriptions/${{subscriptionId}}/dispatch`, {{
            method: "POST",
            payload: {{ profile_id: profileId || null }},
          }});
          pushActionEntry({{
            kind: copy("delivery dispatch", "交付执行"),
            label: state.language === "zh"
              ? `已执行 dispatch：${{subscriptionId}}`
              : `Dispatched subscription: ${{subscriptionId}}`,
            detail: state.language === "zh"
              ? `配置：${{profileId || "default"}}`
              : `Profile: ${{profileId || "default"}}`,
          }});
          await refreshBoard();
          setStageFeedback("deliver", {{
            kind: "completion",
            title: copy("Delivery dispatch completed", "交付 dispatch 已完成"),
            copy: copy(
              "Dispatch results are now part of the delivery lane history. Inspect the audit timeline or route posture next.",
              "dispatch 结果现在已经进入交付阶段历史；下一步可以查看审计时间线或路由姿态。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: {{ "data-empty-jump": "section-ops" }},
              }},
            }},
          }});
          showToast(copy("Delivery dispatch completed.", "交付 dispatch 已完成。"), "success");
        }} catch (error) {{
          reportError(error, copy("Dispatch delivery subscription", "执行交付订阅"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-delivery-open-report]")?.addEventListener("click", async (event) => {{
        const reportId = String(event.currentTarget.dataset.deliveryOpenReport || "").trim();
        if (reportId) {{
          await selectReport(reportId);
        }}
        jumpToSection("section-report-studio");
      }});
      root.querySelectorAll("[data-delivery-select]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliverySelect || "").trim();
          state.selectedDeliverySubscriptionId = subscriptionId;
          renderDeliveryWorkspace();
          const subscription = getDeliverySubscriptionRecord(subscriptionId);
          if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {{
            try {{
              await loadDeliveryPackageAudit(subscriptionId, {{
                profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
              }});
            }} catch (error) {{
              reportError(error, copy("Load report package", "加载报告输出包"));
            }}
          }}
        }});
      }});
      root.querySelectorAll("[data-delivery-toggle-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliveryToggleStatus || "").trim();
          const nextStatus = String(button.dataset.nextStatus || "active").trim().toLowerCase();
          button.disabled = true;
          try {{
            await api(`/api/delivery-subscriptions/${{subscriptionId}}`, {{
              method: "PUT",
              payload: {{ status: nextStatus }},
            }});
            await refreshBoard();
            setStageFeedback("deliver", nextStatus === "paused"
              ? {{
                  kind: "warning",
                  title: copy("Delivery subscription paused", "交付订阅已暂停"),
                  copy: copy("This subscription will stop dispatching until it is resumed from the delivery lane.", "这条订阅会停止 dispatch，直到在交付阶段重新恢复。"),
                  actionHierarchy: {{
                    primary: {{
                      label: copy("Open Delivery Lane", "打开交付工作线"),
                      attrs: {{ "data-empty-jump": "section-ops" }},
                    }},
                  }},
                }}
              : {{
                  kind: "completion",
                  title: copy("Delivery subscription resumed", "交付订阅已恢复"),
                  copy: copy("The subscription is back in the delivery lane and can dispatch again.", "这条订阅已经重新回到交付阶段，可以再次 dispatch。"),
                  actionHierarchy: {{
                    primary: {{
                      label: copy("Open Delivery Lane", "打开交付工作线"),
                      attrs: {{ "data-empty-jump": "section-ops" }},
                    }},
                  }},
                }});
            showToast(
              nextStatus === "paused"
                ? copy("Delivery subscription paused.", "交付订阅已暂停。")
                : copy("Delivery subscription resumed.", "交付订阅已恢复。"),
              "success",
            );
          }} catch (error) {{
            reportError(error, copy("Update delivery subscription", "更新交付订阅"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelectorAll("[data-delivery-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const subscriptionId = String(button.dataset.deliveryDelete || "").trim();
          if (!subscriptionId) {{
            return;
          }}
          const confirmed = window.confirm(copy(
            `Delete delivery subscription ${{subscriptionId}}?`,
            `确认删除交付订阅 ${{subscriptionId}}？`,
          ));
          if (!confirmed) {{
            return;
          }}
          button.disabled = true;
          try {{
            await api(`/api/delivery-subscriptions/${{subscriptionId}}`, {{ method: "DELETE" }});
            if (state.selectedDeliverySubscriptionId === subscriptionId) {{
              state.selectedDeliverySubscriptionId = "";
            }}
            await refreshBoard();
            setStageFeedback("deliver", {{
              kind: "completion",
              title: copy("Delivery subscription deleted", "交付订阅已删除"),
              copy: copy("The selected subscription has been removed from the delivery lane inventory.", "当前选中的订阅已经从交付阶段库存中移除。"),
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: {{ "data-empty-jump": "section-ops" }},
                }},
              }},
            }});
            showToast(copy("Delivery subscription deleted.", "交付订阅已删除。"), "success");
          }} catch (error) {{
            reportError(error, copy("Delete delivery subscription", "删除交付订阅"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
    }}

    function renderAiSurfaces() {{
      const root = $("ai-surface-shell");
      if (!root) {{
        return;
      }}
      const hasPrechecks = Object.keys(state.aiSurfacePrechecks || {{}}).length > 0;
      if (state.loading.board && !hasPrechecks) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const surfaces = [
        {{
          id: "mission_suggest",
          title: copy("Mission Suggest", "任务建议"),
          subjectLabel: copy("watch", "任务"),
          section: "section-board",
        }},
        {{
          id: "triage_assist",
          title: copy("Triage Assist", "分诊辅助"),
          subjectLabel: copy("evidence", "证据"),
          section: "section-triage",
        }},
        {{
          id: "claim_draft",
          title: copy("Claim Draft", "主张草稿"),
          subjectLabel: copy("story", "故事"),
          section: "section-story",
        }},
      ];
      root.innerHTML = surfaces.map((surface) => {{
        const precheck = getAiSurfacePrecheck(surface.id);
        const projection = getAiSurfaceProjection(surface.id);
        const runtime = projection?.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {{}};
        const subject = projection?.subject && typeof projection.subject === "object" ? projection.subject : {{}};
        const rejectableGaps = Array.isArray(precheck.rejectable_gaps) ? precheck.rejectable_gaps : [];
        const mustExposeFacts = Array.isArray(precheck.must_expose_runtime_facts) ? precheck.must_expose_runtime_facts : [];
        const tone = runtime.status === "invalid" || precheck.mode_status === "rejected"
          ? "hot"
          : runtime.status === "fallback_used" || precheck.mode_status === "admitted"
            ? "ok"
            : "";
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <div class="mono">${{escapeHtml(surface.id)}}</div>
                <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(surface.title)}}</h3>
              </div>
              <span class="chip ${{tone}}">${{escapeHtml(localizeWord(runtime.status || precheck.mode_status || "pending"))}}</span>
            </div>
            <div class="meta">
              <span>${{copy("mode", "模式")}}=${{escapeHtml(precheck.mode || "assist")}}</span>
              <span>${{copy("subject", "对象")}}=${{escapeHtml(subject.id || "-")}}</span>
              <span>${{copy("contract", "契约")}}=${{escapeHtml(precheck.contract_id || "-")}}</span>
            </div>
            <div class="panel-sub">${{escapeHtml(summarizeAiSurfaceProjection(surface.id, projection))}}</div>
            <div class="meta" style="margin-top:10px;">
              <span>${{copy("alias", "别名")}}=${{escapeHtml(precheck.alias || "-")}}</span>
              <span>${{copy("fallback", "回退")}}=${{escapeHtml(localizeWord(precheck.manual_fallback || "-"))}}</span>
              <span>${{copy("gaps", "缺口")}}=${{rejectableGaps.length}}</span>
              <span>${{copy("runtime facts", "运行事实")}}=${{mustExposeFacts.length}}</span>
            </div>
            <div class="panel-sub">${{escapeHtml(runtime.request_id || copy("No runtime request id yet.", "当前还没有运行请求 ID。"))}}</div>
            <div class="actions" style="margin-top:12px;">
              <button class="btn-secondary" type="button" data-empty-jump="${{escapeHtml(surface.section)}}">${{copy("Open Surface", "打开对应界面")}}</button>
            </div>
          </div>
        `;
      }}).join("");
      wireLifecycleGuideActions(root);
    }}

    function renderStatus() {{
      const root = $("status-card");
      renderOpsSectionSummary();
      if (state.loading.board && !state.status && !state.ops) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const ops = state.ops || {{}};
      const status = ops.daemon || state.status || {{}};
      const metrics = status.metrics || {{}};
      const collectorSummary = ops.collector_summary || {{}};
      const collectorTiers = ops.collector_tiers || {{}};
      const collectorDrilldown = Array.isArray(ops.collector_drilldown) ? ops.collector_drilldown : [];
      const watchMetrics = ops.watch_metrics || {{}};
      const watchSummary = ops.watch_summary || {{}};
      const watchHealth = Array.isArray(ops.watch_health) ? ops.watch_health : [];
      const routeSummary = ops.route_summary || {{}};
      const routeDrilldown = Array.isArray(ops.route_drilldown) ? ops.route_drilldown : [];
      const routeTimeline = Array.isArray(ops.route_timeline) ? ops.route_timeline : [];
      const degradedCollectors = ops.degraded_collectors || [];
      const recentFailures = ops.recent_failures || [];
      const isError = status.state === "error";
      const tierBlock = Object.entries(collectorTiers).length
        ? Object.entries(collectorTiers).map(([tierName, tier]) => `
            <div class="mini-item">${{tierName}} | total=${{tier.total || 0}} | ok=${{tier.ok || 0}} | warn=${{tier.warn || 0}} | error=${{tier.error || 0}}</div>
          `).join("")
        : `<div class="empty">${{copy("No collector tier breakdown available.", "没有采集器层级拆分数据。")}}</div>`;
      const watchBlock = watchHealth.length
        ? watchHealth.slice(0, 5).map((mission) => `
            <div class="mini-item">${{mission.id}} | ${{mission.status || "idle"}} | due=${{mission.is_due ? "yes" : "no"}} | rate=${{formatRate(mission.success_rate)}}</div>
          `).join("")
        : `<div class="empty">${{copy("No watch mission health record yet.", "当前没有任务健康记录。")}}</div>`;
      const collectorBlock = degradedCollectors.length
        ? degradedCollectors.slice(0, 4).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier}} | ${{collector.status}} | available=${{collector.available}}</div>
          `).join("")
        : `<div class="empty">${{copy("No degraded collector currently reported.", "当前没有降级采集器。")}}</div>`;
      const collectorDrilldownBlock = collectorDrilldown.length
        ? collectorDrilldown.slice(0, 8).map((collector) => `
            <div class="mini-item">${{collector.name}} | ${{collector.tier || "-"}} | ${{collector.status || "ok"}} | available=${{collector.available}}</div>
            <div class="panel-sub">${{collector.setup_hint || collector.message || copy("No remediation note.", "没有修复说明。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No collector drill-down entry available.", "没有采集器下钻条目。")}}</div>`;
      const routeDrilldownBlock = routeDrilldown.length
        ? routeDrilldown.slice(0, 8).map((route) => `
            <div class="mini-item">${{route.name}} | channel=${{route.channel || "unknown"}} | status=${{route.status || "idle"}} | rate=${{formatRate(route.success_rate)}}</div>
            <div class="panel-sub">missions=${{route.mission_count || 0}} | rules=${{route.rule_count || 0}} | events=${{route.event_count || 0}} | failed=${{route.failure_count || 0}}</div>
            <div class="panel-sub">${{route.last_error || route.last_summary || copy("No recent route detail.", "没有最近路由详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No route drill-down entry available.", "没有路由下钻条目。")}}</div>`;
      const routeTimelineBlock = routeTimeline.length
        ? routeTimeline.slice(0, 8).map((event) => `
            <div class="mini-item">${{event.created_at || "-"}} | ${{event.route || "-"}} | ${{event.status || "pending"}} | ${{event.mission_name || event.mission_id || "-"}}</div>
            <div class="panel-sub">${{event.error || event.summary || copy("No route event detail.", "没有路由事件详情。")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No route delivery timeline event available.", "没有路由投递时间线事件。")}}</div>`;
      const failureBlock = recentFailures.length
        ? recentFailures.slice(0, 4).map((failure) => `
            <div class="mini-item">${{failure.kind}} | ${{failure.mission_name || failure.name || "-"}} | ${{localizeWord(failure.status || "error")}} | ${{failure.error || "-"}}</div>
          `).join("")
        : `<div class="empty">${{copy("No recent failure captured.", "近期没有失败记录。")}}</div>`;
      const overflowEvidence = state.consoleOverflowEvidence || defaultConsoleOverflowEvidence();
      const overflowSampledAt = overflowEvidence.updated_at
        ? formatCompactDateTime(overflowEvidence.updated_at)
        : copy("not sampled yet", "尚未采样");
      const overflowResidualBlock = Array.isArray(overflowEvidence.residual_surfaces) && overflowEvidence.residual_surfaces.length
        ? overflowEvidence.residual_surfaces.map((surface) => {{
            const samples = Array.isArray(surface.sample_labels) ? surface.sample_labels : [];
            const sampleLine = samples.length
              ? `<div class="panel-sub">${{samples.map((label) => escapeHtml(label)).join(" | ")}}</div>`
              : `<div class="panel-sub">${{copy("No residual sample label captured.", "没有残余样本文本。")}}</div>`;
            return `
              <div class="mini-item" data-overflow-surface="${{escapeHtml(surface.surface_id || "")}}">
                ${{escapeHtml(surface.surface_id || "unknown")}} | survivors=${{surface.survivor_count || 0}} | fitted=${{surface.fitted_sample_count || 0}}/${{surface.checked_sample_count || 0}}
              </div>
              ${{sampleLine}}
            `;
          }}).join("")
        : `<div class="empty" data-overflow-surface-empty="true">${{copy("No residual overflow survivors captured in this runtime session.", "当前运行会话没有捕获到残余溢出样本。")}}</div>`;
      const alertSignal = getGovernanceSignal("alert_yield");
      const storySignal = getGovernanceSignal("story_conversion");
      const deliveryContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Delivery Continuity", "交付连续性"),
        summary: copy(
          "Alerting missions, ready stories, and route-backed delivery health stay in one lane so downstream status is visible without backtracking.",
          "触发告警的任务、待交付故事和路由健康会保持在同一条工作线里，让下游状态无需回跳即可看清。"
        ),
        stages: [
          {{
            kicker: copy("Mission", "任务"),
            title: copy("Alerting Missions", "触发告警任务"),
            copy: copy(
              "Mission-side alert load stays visible here so delivery work starts from real upstream pressure instead of guesswork.",
              "这里会持续展示任务侧的告警压力，让交付工作基于真实上游负载，而不是靠猜测。"
            ),
            tone: (state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) }},
              {{ label: copy("Recent alerts", "最近告警"), value: String(alertSignal.alert_count ?? state.alerts.length ?? 0) }},
              {{ label: copy("Successful runs", "成功执行"), value: String(alertSignal.successful_runs ?? metrics.runs_total ?? 0) }},
            ],
          }},
          {{
            kicker: copy("Story", "故事"),
            title: copy("Story Readiness", "故事就绪度"),
            copy: copy(
              "Ready stories stay visible beside delivery operations so handoff decisions do not require a separate story audit pass.",
              "待交付故事会与交付操作并排可见，避免为了判断交接是否成立再单独回去审计故事。"
            ),
            tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) }},
              {{ label: copy("Ready", "已就绪"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Converted items", "已转化条目"), value: String(storySignal.converted_item_count ?? 0) }},
            ],
          }},
          {{
            kicker: copy("Route", "路由"),
            title: copy("Route Delivery", "路由交付"),
            copy: copy(
              "Route health and the latest delivery event stay close to the editor so fix-or-forward decisions happen in one place.",
              "路由健康和最新投递事件会贴近编辑器展示，让修复或继续推进都能在同一位置完成。"
            ),
            tone: (routeSummary.degraded || 0) > 0 ? "hot" : "ok",
            facts: [
              {{ label: copy("Healthy", "健康"), value: String(routeSummary.healthy || 0) }},
              {{ label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) }},
              {{ label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true }},
          {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board" }},
          {{ label: copy("Open Stories", "打开故事"), section: "section-story" }},
        ],
      }});
      root.innerHTML = `
        ${{deliveryContinuityBlock}}
        <div class="state-banner ${{isError ? "error" : ""}}">
          <div class="eyebrow"><span class="dot"></span> ${{copy("daemon", "守护进程")}} / ${{localizeWord(status.state || "idle")}}</div>
          <h3 class="card-title" style="margin-top:12px;">${{copy("Heartbeat", "心跳")}}: ${{status.heartbeat_at || "-"}}</h3>
          <div class="meta">
            <span>${{copy("cycles", "轮次")}}=${{metrics.cycles_total || 0}}</span>
            <span>${{copy("runs", "执行")}}=${{metrics.runs_total || 0}}</span>
            <span>${{copy("alerts", "告警")}}=${{metrics.alerts_total || 0}}</span>
            <span>${{copy("errors", "错误")}}=${{metrics.error_total || 0}}</span>
            <span>${{copy("success", "成功")}}=${{metrics.success_total || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("collector health", "采集器健康")}}</div>
          <div class="meta">
            <span>total=${{collectorSummary.total || 0}}</span>
            <span>ok=${{collectorSummary.ok || 0}}</span>
            <span>warn=${{collectorSummary.warn || 0}}</span>
            <span>error=${{collectorSummary.error || 0}}</span>
            <span>unavailable=${{collectorSummary.unavailable || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("route health", "路由健康")}}</div>
          <div class="meta">
            <span>healthy=${{routeSummary.healthy || 0}}</span>
            <span>degraded=${{routeSummary.degraded || 0}}</span>
            <span>missing=${{routeSummary.missing || 0}}</span>
            <span>idle=${{routeSummary.idle || 0}}</span>
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("watch health", "任务健康")}}</div>
          <div class="meta">
            <span>total=${{watchSummary.total || 0}}</span>
            <span>enabled=${{watchSummary.enabled || 0}}</span>
            <span>healthy=${{watchSummary.healthy || 0}}</span>
            <span>degraded=${{watchSummary.degraded || 0}}</span>
            <span>idle=${{watchSummary.idle || 0}}</span>
            <span>disabled=${{watchSummary.disabled || 0}}</span>
            <span>due=${{watchSummary.due || 0}}</span>
            <span>rate=${{formatRate(watchMetrics.success_rate)}}</span>
          </div>
        </div>
        <div class="card" id="console-overflow-evidence-card">
          <div class="mono">${{copy("text overflow evidence", "文本溢出证据")}}</div>
          <div class="meta" data-console-overflow-summary>
            <span>surfaces=${{overflowEvidence.surface_count || 0}}</span>
            <span>checked=${{overflowEvidence.checked_sample_count || 0}}</span>
            <span>fitted=${{overflowEvidence.fitted_sample_count || 0}}</span>
            <span>survivors=${{overflowEvidence.survivor_count || 0}}</span>
            <span>hotspots=${{overflowEvidence.residual_surface_count || 0}}</span>
            <span>sampled=${{overflowSampledAt}}</span>
          </div>
          <div class="panel-sub">${{copy(
            "Session-scoped evidence for data-fit console text surfaces after the current truncation and canvas-fit layers run.",
            "会话级证据，覆盖当前截断与 canvas-fit 层运行后的 data-fit 控制台文本表面。"
          )}}</div>
          <div class="mini-list" style="margin-top:12px;" data-console-overflow-hotspots>
            <div class="mono">${{copy("residual hotspots", "残余热点")}}</div>
            ${{overflowResidualBlock}}
          </div>
        </div>
        <div class="card">
          <div class="mono">${{copy("last_error", "最近错误")}}</div>
          <div>${{status.last_error || "-"}}</div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("collector tiers", "采集器层级")}}</div>
            ${{tierBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("watch board", "任务面板")}}</div>
            ${{watchBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("degraded collectors", "降级采集器")}}</div>
            ${{collectorBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("collector drill-down", "采集器下钻")}}</div>
            ${{collectorDrilldownBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("route drill-down", "路由下钻")}}</div>
            ${{routeDrilldownBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("recent failures", "最近失败")}}</div>
            ${{failureBlock}}
          </div>
        </div>
        <div class="graph-meta">
          <div class="mini-list">
            <div class="mono">${{copy("route timeline", "路由时间线")}}</div>
            ${{routeTimelineBlock}}
          </div>
          <div class="mini-list">
            <div class="mono">${{copy("degraded collectors", "降级采集器")}}</div>
            ${{collectorBlock}}
          </div>
        </div>`;
      wireLifecycleGuideActions(root);
    }}

    function renderDuplicateExplain(payload) {{
      if (!payload) {{
        return "";
      }}
      const candidates = payload.candidates || [];
      const header = `
        <div class="meta">
          <span>${{copy("suggested_primary", "建议主项")}}=${{payload.suggested_primary_id || "-"}}</span>
          <span>${{copy("matches", "匹配数")}}=${{payload.candidate_count || 0}}</span>
          <span>${{copy("shown", "显示数")}}=${{payload.returned_count || 0}}</span>
        </div>
      `;
      if (!candidates.length) {{
        return `<div class="card" style="margin-top:12px;">${{header}}<div class="panel-sub">${{copy("No close duplicate candidate found.", "没有找到接近的重复候选项。")}}</div></div>`;
      }}
      return `
        <div class="card" style="margin-top:12px;">
          ${{header}}
          <div class="stack" style="margin-top:12px;">
            ${{candidates.map((candidate) => `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{candidate.title}}</h3>
                    <div class="meta">
                      <span>${{candidate.id}}</span>
                      <span>${{copy("similarity", "相似度")}}=${{Number(candidate.similarity || 0).toFixed(2)}}</span>
                      <span>${{copy("state", "状态")}}=${{localizeWord(candidate.review_state || "new")}}</span>
                    </div>
                  </div>
                  <span class="chip ${{candidate.suggested_primary_id === candidate.id ? "ok" : ""}}">${{candidate.suggested_primary_id === candidate.id ? copy("keep", "保留") : copy("merge", "合并")}}</span>
                </div>
                <div class="meta">
                  <span>${{copy("signals", "信号")}}=${{(candidate.signals || []).join(", ") || "-"}}</span>
                  <span>${{copy("domain", "域名")}}=${{candidate.same_domain ? copy("same", "相同") : copy("mixed", "混合")}}</span>
                </div>
              </div>
            `).join("")}}
          </div>
        </div>
      `;
    }}

    function renderReviewNotes(notes) {{
      const entries = Array.isArray(notes) ? notes : [];
      if (!entries.length) {{
        return `<div class="panel-sub">${{copy("No review note recorded yet.", "当前还没有审核备注。")}}</div>`;
      }}
      return `
        <div class="stack" style="margin-top:12px;">
          ${{entries.slice(-3).map((entry) => `
            <div class="mini-item">${{escapeHtml(entry.author || "console")}} | ${{escapeHtml(entry.created_at || "-")}}</div>
            <div class="panel-sub">${{escapeHtml(entry.note || "")}}</div>
          `).join("")}}
        </div>
      `;
    }}

    function renderTriageWorkbench(item, {{ filteredCount = 0, evidenceFocusCount = 0 }} = {{}}) {{
      if (!item) {{
        return "";
      }}
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
              <div class="mono">${{copy("Selected Evidence Workbench", "选中证据工作台")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{escapeHtml(item.title || item.id || copy("Selected evidence", "选中证据"))}}</h3>
            </div>
            <span class="chip ${{item.review_state === "escalated" ? "hot" : "ok"}}">${{localizeWord(item.review_state || "new")}}</span>
          </div>
          <div class="panel-sub">${{copy(
            "Keep queue context, reviewer notes, and story handoff in one focused surface while the list stays available for fast switching.",
            "把队列上下文、审核备注和故事交接集中在一个聚焦工作面里，同时保留列表用于快速切换。"
          )}}</div>
          <div class="workbench-meta">
            <span class="chip">${{copy("Queue", "队列")}}: ${{escapeHtml(localizeWord(state.triageFilter || "open"))}}</span>
            <span class="chip">${{copy("Shown", "显示")}}: ${{filteredCount}}</span>
            <span class="chip">${{copy("Score", "分数")}}: ${{item.score || 0}}</span>
            <span class="chip">${{copy("Confidence", "置信度")}}: ${{Number(item.confidence || 0).toFixed(2)}}</span>
            ${{itemMission ? `<span class="chip ok" data-fit-text="triage-mission-chip" data-fit-max-width="190" data-fit-fallback="28">${{copy("Mission", "任务")}}: ${{escapeHtml(itemMission)}}</span>` : ""}}
            ${{evidenceFocusCount ? `<span class="chip hot">${{copy("Evidence Focus", "证据聚焦")}}: ${{evidenceFocusCount}}</span>` : ""}}
          </div>
          ${{linkedStories.length
            ? `<div class="workbench-story-links">
                ${{linkedStories.map((story) => `<span class="chip ok" data-fit-text="triage-story-chip" data-fit-max-width="176" data-fit-fallback="24">${{escapeHtml(story.title || story.id)}}</span>`).join("")}}
              </div>`
            : ""}}
          <div class="continuity-lane">
            <div class="continuity-stage ${{itemMission ? "ok" : ""}}">
              <div class="continuity-stage-kicker">${{copy("From", "来自")}}</div>
              <div class="continuity-stage-title">${{copy("Mission Intake", "任务入口")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "The queue keeps mission context close so evidence review does not require bouncing back to the board first.",
                "队列会把任务上下文保持在附近，避免为了回忆来源而先跳回任务列表。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("Mission", "任务")}}</span><strong>${{escapeHtml(itemMission || copy("Shared queue", "共享队列"))}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Open queue", "开放队列")}}</span><strong>${{String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Enabled missions", "已启用任务")}}</span><strong>${{String(state.overview?.enabled_watches ?? 0)}}</strong></div>
              </div>
            </div>
            <div class="continuity-stage ok">
              <div class="continuity-stage-kicker">${{copy("Now", "当前")}}</div>
              <div class="continuity-stage-title">${{copy("Selected Evidence", "选中证据")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "State transitions and reviewer notes stay attached to the selected evidence instead of being buried inside the full queue.",
                "状态切换和审核备注会直接附着在当前证据上，而不是继续埋在整条长队列里。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("State", "状态")}}</span><strong>${{escapeHtml(localizeWord(item.review_state || "new"))}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Notes", "备注")}}</span><strong>${{String(noteCount)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("URL", "链接")}}</span><strong>${{escapeHtml(clampLabel(item.url || "-", 28))}}</strong></div>
              </div>
            </div>
            <div class="continuity-stage ${{linkedStories.length ? "ok" : ""}}">
              <div class="continuity-stage-kicker">${{copy("Next", "下一步")}}</div>
              <div class="continuity-stage-title">${{copy("Story Handoff", "故事交接")}}</div>
              <div class="continuity-stage-copy">${{copy(
                "Linked stories and conversion headroom stay visible so you can decide when this evidence should become narrative work.",
                "已关联故事和转化余量会继续可见，方便判断这条证据何时该进入叙事工作。"
              )}}</div>
              <div class="continuity-fact-list">
                <div class="continuity-fact"><span>${{copy("Linked stories", "已关联故事")}}</span><strong>${{String(linkedStories.length)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Eligible evidence", "可转故事证据")}}</span><strong>${{String(storySignal.eligible_item_count ?? 0)}}</strong></div>
                <div class="continuity-fact"><span>${{copy("Ready stories", "待交付故事")}}</span><strong>${{String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0)}}</strong></div>
              </div>
            </div>
          </div>
          <div class="workbench-columns">
            <div class="card">
              <div class="mono">${{copy("review notes", "审核备注")}}</div>
              <div class="panel-sub">${{copy("Capture reviewer rationale, route hints, and merge context without losing the selected evidence lane.", "在不丢失当前证据工作线的前提下，记录审核理由、路由提示和合并上下文。")}}</div>
              ${{renderReviewNotes(item.review_notes)}}
              <form data-triage-note-form="${{item.id}}" style="margin-top:12px;">
                <label>${{copy("note composer", "备注编辑")}}<textarea name="note" rows="3" data-triage-note-input="${{item.id}}" placeholder="${{copy("Capture reviewer rationale, routing hint, or merge context.", "记录审核理由、路由提示或合并上下文。")}}">${{escapeHtml(state.triageNoteDrafts[item.id] || "")}}</textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Save Note", "保存备注")}}</button>
                </div>
              </form>
            </div>
            <div class="card">
              ${{triageGuidanceBlock}}
              ${{duplicateExplain
                ? renderDuplicateExplain(duplicateExplain)
                : `<div class="panel-sub" style="margin-top:12px;">${{copy("Duplicate explain stays here once loaded so the list can remain focused on switching items.", "加载后的重复解释会留在这里，列表本身只负责切换条目。")}}</div>`}}
            </div>
          </div>
        </div>
      `;
    }}

    function getVisibleTriageItems() {{
      const activeFilter = state.triageFilter || "open";
      const searchQuery = String(state.triageSearch || "").trim().toLowerCase();
      const pinnedIds = new Set(uniqueValues(state.triagePinnedIds));
      return state.triage.filter((item) => {{
        if (pinnedIds.size && !pinnedIds.has(String(item.id || "").trim())) {{
          return false;
        }}
        const reviewState = String(item.review_state || "new").trim().toLowerCase() || "new";
        if (activeFilter === "all") {{
          // pass
        }} else if (activeFilter === "open") {{
          if (["verified", "duplicate", "ignored"].includes(reviewState)) {{
            return false;
          }}
        }} else if (reviewState !== activeFilter) {{
          return false;
        }}
        if (!searchQuery) {{
          return true;
        }}
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
      }});
    }}

    function isTriageItemSelected(itemId) {{
      return state.selectedTriageIds.includes(itemId);
    }}

    function toggleTriageSelection(itemId, checked = null) {{
      if (!itemId) {{
        return;
      }}
      const next = new Set(state.selectedTriageIds);
      const shouldSelect = checked === null ? !next.has(itemId) : Boolean(checked);
      if (shouldSelect) {{
        next.add(itemId);
        state.selectedTriageId = itemId;
      }} else {{
        next.delete(itemId);
      }}
      state.selectedTriageIds = Array.from(next);
    }}

    function selectVisibleTriageItems() {{
      const visibleIds = getVisibleTriageItems().map((item) => item.id);
      state.selectedTriageIds = visibleIds;
      if (visibleIds.length && !visibleIds.includes(state.selectedTriageId)) {{
        state.selectedTriageId = visibleIds[0];
      }}
    }}

    function clearTriageSelection() {{
      state.selectedTriageIds = [];
    }}

    function clearTriageEvidenceFocus() {{
      state.triagePinnedIds = [];
      renderTriage();
      showToast(copy("Returned to the full triage queue.", "已返回完整分诊队列。"), "success");
    }}

    function focusTriageEvidence(itemIds, {{ itemId = "", jump = true, showToastMessage = true }} = {{}}) {{
      const normalizedIds = uniqueValues(itemIds).filter((candidate) => state.triage.some((item) => item.id === candidate));
      if (!normalizedIds.length) {{
        if (showToastMessage) {{
          showToast(copy("No matching triage evidence is available for this story.", "当前没有可回查的分诊证据。"), "error");
        }}
        return;
      }}
      state.triagePinnedIds = normalizedIds;
      state.triageFilter = "all";
      state.triageSearch = "";
      state.selectedTriageId = itemId && normalizedIds.includes(itemId) ? itemId : normalizedIds[0];
      state.selectedTriageIds = [];
      renderTriage();
      if (jump) {{
        jumpToSection("section-triage");
      }}
      if (showToastMessage) {{
        showToast(
          state.language === "zh"
            ? `已聚焦 ${{normalizedIds.length}} 条相关分诊证据`
            : `Focused ${{normalizedIds.length}} related triage item(s)`,
          "success",
        );
      }}
    }}

    async function postTriageState(itemId, nextState) {{
      return api(`/api/triage/${{itemId}}/state`, {{
        method: "POST",
        payload: {{ state: nextState, actor: "console" }},
      }});
    }}

    async function deleteTriageItem(itemId) {{
      return api(`/api/triage/${{itemId}}`, {{
        method: "DELETE",
      }});
    }}

    async function runTriageExplain(itemId) {{
      if (!itemId) {{
        return;
      }}
      state.selectedTriageId = itemId;
      state.triageExplain[itemId] = await api(`/api/triage/${{itemId}}/explain?limit=4`);
      renderTriage();
    }}

    async function runTriageStateUpdate(itemId, nextState) {{
      if (!itemId || !nextState) {{
        return;
      }}
      state.selectedTriageId = itemId;
      const currentItem = state.triage.find((item) => item.id === itemId);
      const previousState = currentItem ? String(currentItem.review_state || "new") : "new";
      if (currentItem) {{
        currentItem.review_state = nextState;
      }}
      renderTriage();
      try {{
        await postTriageState(itemId, nextState);
        pushActionEntry({{
          kind: copy("triage state", "分诊状态"),
          label: state.language === "zh" ? `已将 ${{itemId}} 标记为 ${{localizeWord(nextState)}}` : `Marked ${{itemId}} as ${{nextState}}`,
          detail: state.language === "zh" ? `之前状态为 ${{localizeWord(previousState)}}。` : `Previous state was ${{previousState}}.`,
          undoLabel: state.language === "zh" ? `恢复为 ${{localizeWord(previousState)}}` : `Restore ${{previousState}}`,
          undo: async () => {{
            await postTriageState(itemId, previousState);
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复分诊状态：${{itemId}} -> ${{localizeWord(previousState)}}`
                : `Triage state restored: ${{itemId}} -> ${{previousState}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        setStageFeedback("review", {{
          kind: "completion",
          title: state.language === "zh"
            ? `已将 ${{itemId}} 标记为 ${{localizeWord(nextState)}}`
            : `Marked ${{itemId}} as ${{nextState}}`,
          copy: copy(
            "The queue state is now persisted on the review lane. Continue in triage or hand the evidence into story work next.",
            "这条队列状态已经在审阅阶段持久化；下一步可以继续留在分诊，或把证据交给故事工作台。"
          ),
          actionHierarchy: {{
            primary: {{
              label: ["verified", "escalated"].includes(String(nextState || "").trim().toLowerCase())
                ? copy("Open Story Workspace", "打开故事工作台")
                : copy("Continue In Triage", "继续处理分诊"),
              attrs: ["verified", "escalated"].includes(String(nextState || "").trim().toLowerCase())
                ? {{ "data-empty-jump": "section-story" }}
                : {{ "data-empty-jump": "section-triage" }},
            }},
            secondary: [
              {{
                label: copy("Review Queue", "查看分诊队列"),
                attrs: {{ "data-empty-jump": "section-triage" }},
              }},
            ],
          }},
        }});
      }} catch (error) {{
        if (currentItem) {{
          currentItem.review_state = previousState;
        }}
        renderTriage();
        throw error;
      }}
    }}

    async function runTriageDelete(itemId) {{
      if (!itemId) {{
        return;
      }}
      const currentItem = state.triage.find((item) => item.id === itemId);
      const itemLabel = currentItem && currentItem.title ? currentItem.title : itemId;
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除分诊条目：${{itemLabel}}？该操作会把条目从当前收件箱中移除。`
          : `Delete triage item "${{itemLabel}}" from the inbox?`,
      );
      if (!confirmed) {{
        return;
      }}
      await deleteTriageItem(itemId);
      state.selectedTriageIds = state.selectedTriageIds.filter((selectedId) => selectedId !== itemId);
      delete state.triageExplain[itemId];
      delete state.triageNoteDrafts[itemId];
      pushActionEntry({{
        kind: copy("triage delete", "分诊删除"),
        label: state.language === "zh" ? `已删除：${{itemLabel}}` : `Deleted ${{itemLabel}}`,
        detail: state.language === "zh" ? `条目 ID：${{itemId}}` : `Item id: ${{itemId}}`,
      }});
      await refreshBoard();
      showToast(
        state.language === "zh" ? `已删除分诊条目：${{itemLabel}}` : `Deleted triage item: ${{itemLabel}}`,
        "success",
      );
    }}

    async function createStoryFromTriageItems(itemIds) {{
      const normalizedIds = uniqueValues(itemIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!normalizedIds.length) {{
        return;
      }}
      const selectedItems = normalizedIds
        .map((itemId) => state.triage.find((item) => item.id === itemId))
        .filter(Boolean);
      const created = await api("/api/stories/from-triage", {{
        method: "POST",
        payload: {{
          item_ids: normalizedIds,
          status: "monitoring",
        }},
      }});
      state.storySearch = "";
      state.storyFilter = "all";
      state.storySort = "attention";
      persistStoryWorkspacePrefs();
      state.selectedStoryId = created.id;
      state.storyDetails[created.id] = created;
      state.selectedTriageIds = state.selectedTriageIds.filter((itemId) => !normalizedIds.includes(itemId));
      pushActionEntry({{
        kind: copy("story seed", "故事生成"),
        label: state.language === "zh"
          ? `已从分诊生成故事：${{created.title}}`
          : `Created story from triage: ${{created.title}}`,
        detail: state.language === "zh"
          ? `来源条目：${{selectedItems.map((item) => item.title || item.id).slice(0, 3).join("、")}}`
          : `Source items: ${{selectedItems.map((item) => item.title || item.id).slice(0, 3).join(", ")}}`,
        undoLabel: copy("Delete story", "删除故事"),
        undo: async () => {{
          await api(`/api/stories/${{created.id}}`, {{ method: "DELETE" }});
          await refreshBoard();
          showToast(
            state.language === "zh" ? `已删除故事：${{created.title}}` : `Story deleted: ${{created.title}}`,
            "success",
          );
        }},
      }});
      await refreshBoard();
      await loadStory(created.id, {{ mode: "editor", syncUrl: true }});
      jumpToSection("section-story");
      setStageFeedback("review", {{
        kind: "completion",
        title: state.language === "zh"
          ? `已从 ${{normalizedIds.length}} 条分诊记录生成故事`
          : `Created story from ${{normalizedIds.length}} triage item(s)`,
        copy: copy(
          "The review lane now owns a promoted story candidate. Refine it in the workspace before delivery.",
          "审阅阶段现在已经拥有被提升的故事候选；下一步先在工作台里完善，再进入交付。"
        ),
        actionHierarchy: {{
          primary: {{
            label: copy("Open Story Workspace", "打开故事工作台"),
            attrs: {{ "data-empty-jump": "section-story" }},
          }},
          secondary: [
            {{
              label: copy("Open Delivery Lane", "打开交付工作线"),
              attrs: {{ "data-empty-jump": "section-ops" }},
            }},
          ],
        }},
      }});
      showToast(
        state.language === "zh"
          ? `已从 ${{normalizedIds.length}} 条分诊记录生成故事`
          : `Created story from ${{normalizedIds.length}} triage item(s)`,
        "success",
      );
    }}

    async function runTriageBatchStateUpdate(nextState) {{
      const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!itemIds.length || !nextState || state.triageBulkBusy) {{
        return;
      }}
      state.triageBulkBusy = true;
      if (!itemIds.includes(state.selectedTriageId)) {{
        state.selectedTriageId = itemIds[0];
      }}
      const previousStates = {{}};
      itemIds.forEach((itemId) => {{
        const currentItem = state.triage.find((item) => item.id === itemId);
        previousStates[itemId] = currentItem ? String(currentItem.review_state || "new") : "new";
        if (currentItem) {{
          currentItem.review_state = nextState;
        }}
      }});
      renderTriage();
      const appliedIds = [];
      try {{
        for (const itemId of itemIds) {{
          await postTriageState(itemId, nextState);
          appliedIds.push(itemId);
        }}
        state.selectedTriageIds = [];
        pushActionEntry({{
          kind: copy("triage batch", "分诊批处理"),
          label: state.language === "zh"
            ? `已批量将 ${{itemIds.length}} 条记录标记为 ${{localizeWord(nextState)}}`
            : `Marked ${{itemIds.length}} triage items as ${{nextState}}`,
          detail: state.language === "zh"
            ? `涉及条目：${{itemIds.join(", ")}}`
            : `Items: ${{itemIds.join(", ")}}`,
          undoLabel: state.language === "zh"
            ? `恢复这 ${{itemIds.length}} 条记录`
            : `Restore ${{itemIds.length}} items`,
          undo: async () => {{
            for (const itemId of itemIds) {{
              await postTriageState(itemId, previousStates[itemId] || "new");
            }}
            await refreshBoard();
            showToast(
              state.language === "zh"
                ? `已恢复 ${{itemIds.length}} 条分诊记录`
                : `Restored ${{itemIds.length}} triage items`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        setStageFeedback("review", {{
          kind: "completion",
          title: state.language === "zh"
            ? `已批量处理 ${{itemIds.length}} 条分诊记录`
            : `Processed ${{itemIds.length}} triage items`,
          copy: copy(
            "The selected queue slice is now updated in place. Continue review or hand the verified evidence into stories.",
            "当前选中的队列切片已经原位更新；下一步可以继续审阅，或把已核验证据交给故事工作台。"
          ),
          actionHierarchy: {{
            primary: {{
              label: copy("Open Triage", "打开分诊"),
              attrs: {{ "data-empty-jump": "section-triage" }},
            }},
            secondary: [
              {{
                label: copy("Open Story Workspace", "打开故事工作台"),
                attrs: {{ "data-empty-jump": "section-story" }},
              }},
            ],
          }},
        }});
        showToast(
          state.language === "zh"
            ? `已批量处理 ${{itemIds.length}} 条分诊记录`
            : `Processed ${{itemIds.length}} triage items`,
          "success",
        );
      }} catch (error) {{
        itemIds.forEach((itemId) => {{
          const currentItem = state.triage.find((item) => item.id === itemId);
          if (currentItem) {{
            currentItem.review_state = previousStates[itemId] || "new";
          }}
        }});
        renderTriage();
        for (const itemId of appliedIds.reverse()) {{
          try {{
            await postTriageState(itemId, previousStates[itemId] || "new");
          }} catch (rollbackError) {{
            console.error("triage batch rollback failed", rollbackError);
          }}
        }}
        await refreshBoard();
        throw error;
      }} finally {{
        state.triageBulkBusy = false;
        renderTriage();
      }}
    }}

    async function runTriageBatchDelete() {{
      const itemIds = uniqueValues(state.selectedTriageIds).filter((itemId) => state.triage.some((item) => item.id === itemId));
      if (!itemIds.length || state.triageBulkBusy) {{
        return;
      }}
      const confirmed = window.confirm(
        state.language === "zh"
          ? `确认删除已选的 ${{itemIds.length}} 条分诊记录？该操作会把它们从当前收件箱中移除。`
          : `Delete ${{itemIds.length}} selected triage items from the inbox?`,
      );
      if (!confirmed) {{
        return;
      }}
      state.triageBulkBusy = true;
      renderTriage();
      let deletedCount = 0;
      try {{
        for (const itemId of itemIds) {{
          await deleteTriageItem(itemId);
          deletedCount += 1;
          delete state.triageExplain[itemId];
          delete state.triageNoteDrafts[itemId];
        }}
        state.selectedTriageIds = [];
        pushActionEntry({{
          kind: copy("triage batch delete", "分诊批量删除"),
          label: state.language === "zh"
            ? `已批量删除 ${{itemIds.length}} 条分诊记录`
            : `Deleted ${{itemIds.length}} triage items`,
          detail: state.language === "zh"
            ? `涉及条目：${{itemIds.join(", ")}}`
            : `Items: ${{itemIds.join(", ")}}`,
        }});
        await refreshBoard();
        showToast(
          state.language === "zh"
            ? `已批量删除 ${{itemIds.length}} 条分诊记录`
            : `Deleted ${{itemIds.length}} triage items`,
          "success",
        );
      }} catch (error) {{
        await refreshBoard();
        const message = error && error.message ? error.message : String(error || "Unknown error");
        if (deletedCount > 0) {{
          throw new Error(
            state.language === "zh"
              ? `已删除 ${{deletedCount}}/${{itemIds.length}} 条记录后失败：${{message}}`
              : `Deleted ${{deletedCount}}/${{itemIds.length}} items before failure: ${{message}}`,
          );
        }}
        throw error;
      }} finally {{
        state.triageBulkBusy = false;
        renderTriage();
      }}
    }}

    function focusTriageNoteComposer(itemId) {{
      if (!itemId) {{
        return;
      }}
      state.selectedTriageId = itemId;
      renderTriage();
      const field = document.querySelector(`[data-triage-note-input="${{itemId}}"]`);
      if (field) {{
        field.focus();
        field.setSelectionRange(field.value.length, field.value.length);
      }}
    }}

    function moveTriageSelection(delta) {{
      const visibleItems = getVisibleTriageItems();
      if (!visibleItems.length) {{
        return;
      }}
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
      const selectedCard = document.querySelector(`[data-triage-card="${{state.selectedTriageId}}"]`);
      selectedCard?.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
    }}

    function renderTriage() {{
      const root = $("triage-list");
      const inlineStats = $("triage-stats-inline");
      if (state.loading.board && !state.triage.length) {{
        renderTriageSectionSummary();
        inlineStats.innerHTML = `<span>${{copy("loading", "加载中")}}=triage</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        renderTopbarContext();
        return;
      }}
      const stats = state.triageStats || {{}};
      const triageStates = stats.states || {{}};
      const triageSearchValue = String(state.triageSearch || "");
      const filterOptions = [
        {{ key: "open", label: copy("open", "开放"), count: stats.open_count || 0 }},
        {{ key: "all", label: copy("all", "全部"), count: stats.total || state.triage.length }},
        ...Object.entries(triageStates).map(([key, count]) => ({{ key, label: localizeWord(key), count: count || 0 }})),
      ];
      const activeFilter = normalizeTriageFilter(state.triageFilter);
      state.triageFilter = activeFilter;
      const filteredItems = getVisibleTriageItems();
      const defaultItemId = filteredItems[0] ? filteredItems[0].id : (state.triage[0] ? state.triage[0].id : "");
      const evidenceFocusCount = uniqueValues(state.triagePinnedIds).filter((itemId) => state.triage.some((item) => item.id === itemId)).length;
      const visibleIds = new Set(filteredItems.map((item) => item.id));
      state.selectedTriageIds = uniqueValues(state.selectedTriageIds).filter((itemId) => visibleIds.has(itemId));
      if (filteredItems.length && !filteredItems.some((item) => item.id === state.selectedTriageId)) {{
        state.selectedTriageId = filteredItems[0].id;
      }}
      if (!filteredItems.length) {{
        state.selectedTriageId = "";
      }}
      const selectedCount = state.selectedTriageIds.length;
      const batchBusy = Boolean(state.triageBulkBusy);
      const selectedTriageItem = filteredItems.find((item) => item.id === state.selectedTriageId) || null;
      renderTriageSectionSummary({{
        stats,
        filteredItems,
        selectedItem: selectedTriageItem,
        evidenceFocusCount,
        activeFilter,
        searchValue: triageSearchValue,
      }});
      const triageSearchCard = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("queue search", "队列搜索")}}</div>
              <div class="panel-sub">${{copy("Search the visible queue by title, url, id, or recent review notes.", "按标题、链接、条目 ID 或最近备注搜索当前可见队列。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <span class="chip">${{copy("shown", "显示")}}=${{filteredItems.length}}</span>
              <span class="chip">${{copy("selected", "已选")}}=${{selectedCount}}</span>
              <span class="chip ${{evidenceFocusCount ? "hot" : ""}}">${{copy("evidence", "证据")}}=${{evidenceFocusCount || 0}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(triageSearchValue)}}" data-triage-search placeholder="${{copy("Search visible queue", "搜索当前队列")}}">
            <button class="btn-secondary" type="button" data-triage-search-clear ${{triageSearchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
          ${{
            evidenceFocusCount
              ? `
                <div class="actions" style="margin-top:12px;">
                  <span class="chip hot">${{copy("evidence focus active", "证据聚焦中")}}</span>
                  <span class="panel-sub">${{copy(`Showing ${{evidenceFocusCount}} triage evidence item(s) linked to the current story.`, `当前只显示与故事关联的 ${{evidenceFocusCount}} 条分诊证据。`)}}</span>
                  <button class="btn-secondary" type="button" data-triage-pin-clear>${{copy("Show Full Queue", "显示完整队列")}}</button>
                </div>
              `
              : ""
          }}
        </div>
      `;
      const batchCopy = selectedCount
        ? copy(
            `Selected ${{selectedCount}} items. Apply one queue action or clear the selection.`,
            `已选 ${{selectedCount}} 条。直接执行一个批量动作，或先清空选择。`,
          )
        : copy(
            "Select visible items, then apply one review action across the queue without leaving the page.",
            "先选择当前列表中的条目，再在当前页面内一次性执行统一审核动作。",
          );
      const filterBlock = filterOptions.map((option) => `
        <button class="chip-btn ${{activeFilter === option.key ? "active" : ""}}" type="button" data-triage-filter="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
      `).join("");
      const batchToolbar = `
        <div class="card batch-toolbar-card ${{selectedCount ? "selection-live" : ""}}">
          <div class="batch-toolbar">
            <div class="batch-toolbar-head">
              <div>
                <div class="mono">${{copy("batch actions", "批量操作")}}</div>
                <div class="panel-sub">${{batchCopy}}</div>
              </div>
              <span class="chip ${{selectedCount ? "ok" : ""}}">${{copy("selected", "已选")}}=${{selectedCount}}</span>
            </div>
            ${{
              selectedCount
                ? `<div class="actions">
                    <button class="btn-secondary" type="button" data-triage-selection-clear ${{batchBusy ? "disabled" : ""}}>${{copy("Clear Selection", "清空选择")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="triaged" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Triage", "批量分诊")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="verified" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Verify", "批量核验")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="escalated" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Escalate", "批量升级")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-state="ignored" ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Ignore", "批量忽略")}}</button>
                    <button class="btn-secondary" type="button" data-triage-batch-story ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Story", "批量生成故事")}}</button>
                    <button class="btn-danger" type="button" data-triage-batch-delete ${{batchBusy ? "disabled" : ""}}>${{copy("Batch Delete", "批量删除")}}</button>
                  </div>`
                : `<div class="actions">
                    <button class="btn-secondary" type="button" data-triage-select-visible ${{(!filteredItems.length || batchBusy) ? "disabled" : ""}}>${{copy("Select Visible", "选择当前列表")}}</button>
                  </div>`
            }}
          </div>
        </div>
      `;
      const triageWorkbench = selectedTriageItem
        ? renderTriageWorkbench(selectedTriageItem, {{ filteredCount: filteredItems.length, evidenceFocusCount }})
        : "";
      inlineStats.innerHTML = `
        <span>${{copy("open", "开放")}}=${{stats.open_count || 0}}</span>
        <span>${{copy("closed", "关闭")}}=${{stats.closed_count || 0}}</span>
        <span>${{copy("notes", "备注")}}=${{stats.note_count || 0}}</span>
        <span>${{copy("verified", "已核验")}}=${{(stats.states || {{}}).verified || 0}}</span>
        <span>${{copy("filter", "筛选")}}=${{localizeWord(activeFilter)}}</span>
        <span>${{copy("selected", "选中")}}=${{selectedCount}}</span>
        <span>${{copy("evidence", "证据")}}=${{evidenceFocusCount}}</span>
        <span>${{copy("focus", "焦点")}}=${{state.selectedTriageId || "-"}}</span>
      `;
      if (!state.triage.length) {{
        root.innerHTML = `
          ${{triageSearchCard}}
          <div class="card">
            <div class="mono">${{copy("triage filters", "分诊筛选")}}</div>
            <div class="panel-sub">${{copy("Slice the queue by current review state before applying notes or state transitions.", "在写备注或修改状态前，先按审核状态切分队列。")}}</div>
            <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
          </div>
          <div class="card">
            <div class="mono">${{copy("triage shortcuts", "分诊快捷键")}}</div>
            <div class="panel-sub">${{copy("Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, S to create a story, D to explain duplicates, and N to focus the note composer.", "使用 J/K 上下移动，V 核验，T 分诊，E 升级，I 忽略，S 生成故事，D 查看重复解释，N 聚焦备注输入。")}}</div>
          </div>
          ${{batchToolbar}}
          ${{renderLifecycleGuideCard({{
            title: copy("Triage opens after the first mission run writes inbox items", "任务第一次执行并写入收件箱后，分诊区才会展开"),
            summary: copy(
              "You do not need CLI-first setup to use the review lane. Create or run a mission in the browser, then use this queue to verify signal, mark duplicates, and promote stories.",
              "进入审阅工作流不需要先读 CLI 文档。先在浏览器里创建或执行任务，随后就在这个队列里完成核验、去重和故事提升。"
            ),
            steps: [
              {{
                title: copy("Run A Mission", "先执行任务"),
                copy: copy("Mission Board or Cockpit will populate the inbox once evidence is collected.", "任务列表或任务详情执行后，收件箱就会开始积累证据。"),
              }},
              {{
                title: copy("Review Evidence", "审阅证据"),
                copy: copy("Mark duplicates, verify findings, or escalate items directly inside this queue.", "直接在这个队列里完成去重、核验或升级处理。"),
              }},
              {{
                title: copy("Promote Story", "提升故事"),
                copy: copy("Use Create Story when the queue has enough verified signal to become a narrative.", "当队列里积累了足够的已核验信号时，就可以直接生成故事。"),
              }},
              {{
                title: copy("Attach Delivery Later", "稍后再接交付"),
                copy: copy("Routes stay optional until the mission or story is ready to notify downstream.", "只有在任务或故事需要通知下游时，才需要回去接入路由。"),
              }},
            ],
            actions: [
              {{ label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true }},
              {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title" }},
              {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
            ],
          }})}}
          <div class="empty">${{copy("No triage item stored right now.", "当前没有分诊条目。")}}</div>`;
        wireLifecycleGuideActions(root);
        syncTriageUrlState({{ defaultItemId }});
        flushTriageUrlFocus();
        renderTopbarContext();
        scheduleCanvasTextFit(root);
        return;
      }}
      root.innerHTML = `
        ${{triageSearchCard}}
        <div class="card">
          <div class="mono">${{copy("triage filters", "分诊筛选")}}</div>
          <div class="panel-sub">${{copy("Slice the queue by current review state before applying notes or state transitions.", "在写备注或修改状态前，先按审核状态切分队列。")}}</div>
          <div class="stack" style="margin-top:12px;">${{filterBlock}}</div>
        </div>
        <div class="card">
          <div class="mono">${{copy("triage shortcuts", "分诊快捷键")}}</div>
          <div class="panel-sub">${{copy("Use J/K to move, V to verify, T to triage, E to escalate, I to ignore, S to create a story, D to explain duplicates, and N to focus the note composer.", "使用 J/K 上下移动，V 核验，T 分诊，E 升级，I 忽略，S 生成故事，D 查看重复解释，N 聚焦备注输入。")}}</div>
        </div>
        ${{batchToolbar}}
        ${{triageWorkbench}}
        ${{
          filteredItems.length
            ? filteredItems.map((item) => {{
                const linkedStories = getStoriesForEvidenceItem(item.id);
                const noteCount = Array.isArray(item.review_notes) ? item.review_notes.length : 0;
                const itemMission = String(item?.extra?.watch_mission_name || item?.watch_mission_name || "").trim();
                const actionHierarchy = getTriageCardActionHierarchy(item, linkedStories);
                return `
        <div class="card selectable ${{item.id === state.selectedTriageId ? "selected" : ""}}" data-triage-card="${{item.id}}">
          <div class="card-top">
            <div class="triage-card-head">
              <label class="checkbox-inline">
                <input type="checkbox" data-triage-select="${{item.id}}" ${{isTriageItemSelected(item.id) ? "checked" : ""}}>
                <span>${{copy("select", "选择")}}</span>
              </label>
              <div>
                <h3 class="card-title">${{item.title}}</h3>
                <div class="meta">
                  <span>${{item.id}}</span>
                  <span>${{copy("state", "状态")}}=${{localizeWord(item.review_state || "new")}}</span>
                  <span>${{copy("score", "分数")}}=${{item.score || 0}}</span>
                  <span>${{copy("confidence", "置信度")}}=${{Number(item.confidence || 0).toFixed(2)}}</span>
                </div>
              </div>
            </div>
            <span class="chip ${{item.review_state === "escalated" ? "hot" : ""}}">${{localizeWord(item.review_state || "new")}}</span>
          </div>
          <div class="panel-sub">${{item.url}}</div>
          <div class="meta">
            <span>${{copy("notes", "备注")}}=${{noteCount}}</span>
            <span>${{copy("stories", "故事")}}=${{linkedStories.length}}</span>
            ${{itemMission ? `<span>${{copy("mission", "任务")}}=${{escapeHtml(clampLabel(itemMission, 28))}}</span>` : ""}}
          </div>
          ${{renderCardActionHierarchy(actionHierarchy)}}
        </div>
      `;
              }}).join("")
            : `<div class="empty">${{copy("No triage item matched the active queue filter.", "没有条目匹配当前分诊筛选。")}}</div>`
        }}
      `;

      root.querySelectorAll("[data-triage-filter]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.triageFilter = normalizeTriageFilter(button.dataset.triageFilter);
          renderTriage();
        }});
      }});

      root.querySelector("[data-triage-search]")?.addEventListener("input", (event) => {{
        state.triageSearch = event.target.value;
        renderTriage();
      }});

      root.querySelector("[data-triage-search-clear]")?.addEventListener("click", () => {{
        state.triageSearch = "";
        renderTriage();
      }});

      root.querySelector("[data-triage-pin-clear]")?.addEventListener("click", () => {{
        clearTriageEvidenceFocus();
      }});

      root.querySelector("[data-triage-select-visible]")?.addEventListener("click", () => {{
        selectVisibleTriageItems();
        renderTriage();
      }});

      root.querySelector("[data-triage-selection-clear]")?.addEventListener("click", () => {{
        clearTriageSelection();
        renderTriage();
      }});

      root.querySelectorAll("[data-triage-batch-state]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageBatchStateUpdate(String(button.dataset.triageBatchState || "").trim());
          }} catch (error) {{
            reportError(error, copy("Batch triage", "批量分诊"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelector("[data-triage-batch-story]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await createStoryFromTriageItems(state.selectedTriageIds);
        }} catch (error) {{
          reportError(error, copy("Create story from triage", "从分诊生成故事"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      root.querySelector("[data-triage-batch-delete]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await runTriageBatchDelete();
        }} catch (error) {{
          reportError(error, copy("Batch delete", "批量删除"));
        }} finally {{
          button.disabled = false;
        }}
      }});

      root.querySelectorAll("[data-triage-card]").forEach((card) => {{
        card.addEventListener("click", (event) => {{
          if (event.target.closest("button, textarea, input, select, a, form, label")) {{
            return;
          }}
          state.selectedTriageId = String(card.dataset.triageCard || "").trim();
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-select]").forEach((input) => {{
        input.addEventListener("change", () => {{
          toggleTriageSelection(String(input.dataset.triageSelect || "").trim(), input.checked);
          renderTriage();
        }});
      }});

      root.querySelectorAll("[data-triage-explain]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageExplain(String(button.dataset.triageExplain || "").trim());
          }} catch (error) {{
            reportError(error, copy("Explain duplicates", "查看重复解释"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-state]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageStateUpdate(
              String(button.dataset.triageId || "").trim(),
              String(button.dataset.triageState || "").trim(),
            );
          }} catch (error) {{
            reportError(error, copy("Update triage state", "更新分诊状态"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-story]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await createStoryFromTriageItems([String(button.dataset.triageStory || "").trim()]);
          }} catch (error) {{
            reportError(error, copy("Create story from triage", "从分诊生成故事"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-delete]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runTriageDelete(String(button.dataset.triageDelete || "").trim());
          }} catch (error) {{
            reportError(error, copy("Delete triage item", "删除分诊条目"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-triage-note-input]").forEach((field) => {{
        field.addEventListener("input", () => {{
          state.triageNoteDrafts[field.dataset.triageNoteInput] = field.value;
        }});
      }});

      root.querySelectorAll("[data-triage-note-form]").forEach((form) => {{
        form.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const itemId = String(form.dataset.triageNoteForm || "").trim();
          const note = String(new FormData(form).get("note") || "").trim();
          if (!note) {{
            showToast(copy("Provide a note before saving.", "保存前请先填写备注。"), "error");
            return;
          }}
          const submitButton = form.querySelector("button[type='submit']");
          if (submitButton) {{
            submitButton.disabled = true;
          }}
          try {{
            await api(`/api/triage/${{itemId}}/note`, {{
              method: "POST",
              payload: {{ note, author: "console" }},
            }});
            state.triageNoteDrafts[itemId] = "";
            await refreshBoard();
          }} catch (error) {{
            reportError(error, copy("Save triage note", "保存分诊备注"));
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }});
      wireLifecycleGuideActions(root);
      syncTriageUrlState({{ defaultItemId }});
      flushTriageUrlFocus();
      renderTopbarContext();
      scheduleCanvasTextFit(root);
    }}

    async function loadStory(identifier, {{ mode = null, syncUrl = true, force = false }} = {{}}) {{
      const normalizedId = String(identifier || "").trim();
      if (!normalizedId) {{
        return;
      }}
      const normalizedMode = mode == null ? null : normalizeStoryWorkspaceMode(mode);
      if (normalizedMode !== null) {{
        applyStoryWorkspaceMode(normalizedMode, {{ persist: true, syncUrl: false }});
      }}
      state.selectedStoryId = normalizedId;
      state.loading.storyDetail = true;
      renderStories();
      try {{
        if (force || !state.storyDetails[normalizedId] || !state.storyGraph[normalizedId]) {{
          const [detail, graph] = await Promise.all([
            api(`/api/stories/${{normalizedId}}`),
            api(`/api/stories/${{normalizedId}}/graph`),
          ]);
          state.storyDetails[normalizedId] = detail;
          state.storyGraph[normalizedId] = graph;
        }}
      }} finally {{
        state.loading.storyDetail = false;
      }}
      if (syncUrl) {{
        syncStoryUrlState({{ defaultStoryId: normalizedId }});
      }}
      renderStories();
    }}

    async function previewStoryMarkdown(identifier) {{
      state.selectedStoryId = identifier;
      if (!state.storyDetails[identifier]) {{
        state.storyDetails[identifier] = await api(`/api/stories/${{identifier}}`);
      }}
      state.storyMarkdown[identifier] = await apiText(`/api/stories/${{identifier}}/export?format=markdown`);
      renderStories();
    }}

    function renderStoryGraph(payload) {{
      if (!payload || !Array.isArray(payload.nodes) || !payload.nodes.length) {{
        return `<div class="empty">${{copy("No entity graph available for this story.", "这个故事当前没有实体图谱。")}}</div>`;
      }}
      const storyNode = payload.nodes.find((node) => node.kind === "story") || payload.nodes[0];
      const entityNodes = payload.nodes.filter((node) => node.kind === "entity");
      const positions = {{}};
      positions[storyNode.id] = {{ x: 360, y: 160 }};
      const radius = Math.min(145, 88 + (entityNodes.length * 5));
      entityNodes.forEach((node, index) => {{
        const angle = ((Math.PI * 2) * index) / Math.max(entityNodes.length, 1) - (Math.PI / 2);
        positions[node.id] = {{
          x: 360 + (Math.cos(angle) * radius),
          y: 160 + (Math.sin(angle) * radius),
        }};
      }});

      const lines = (payload.edges || []).map((edge) => {{
        const source = positions[edge.source];
        const target = positions[edge.target];
        if (!source || !target) {{
          return "";
        }}
        const stroke = edge.kind === "entity_relation" ? "rgba(255, 106, 130, 0.78)" : "rgba(127, 228, 255, 0.42)";
        const dash = edge.kind === "entity_relation" ? "0" : "6 6";
        return `<line x1="${{source.x}}" y1="${{source.y}}" x2="${{target.x}}" y2="${{target.y}}" stroke="${{stroke}}" stroke-width="2.5" stroke-dasharray="${{dash}}" />`;
      }}).join("");

      const labels = [storyNode, ...entityNodes].map((node) => {{
        const pos = positions[node.id];
        if (!pos) {{
          return "";
        }}
        const isStory = node.kind === "story";
        const radiusValue = isStory ? 34 : 22 + Math.min(10, (Number(node.in_story_source_count || 0) * 2));
        const fill = isStory ? "#07111d" : "#102031";
        const stroke = isStory ? "rgba(234, 244, 255, 0.76)" : "rgba(127, 228, 255, 0.32)";
        const textFill = "#eaf4ff";
        const label = escapeHtml(node.label || node.id);
        const subtitle = isStory
          ? `${{node.item_count || 0}} items`
          : `${{node.entity_type || "UNKNOWN"}} / ${{node.in_story_source_count || 0}} src`;
        const subtitleY = isStory ? 8 : 6;
        return `
          <g>
            <circle cx="${{pos.x}}" cy="${{pos.y}}" r="${{radiusValue}}" fill="${{fill}}" stroke="${{stroke}}" stroke-width="2.5"></circle>
            <text x="${{pos.x}}" y="${{pos.y - 4}}" text-anchor="middle" font-family="Avenir Next Condensed, Arial Narrow, sans-serif" font-size="${{isStory ? 16 : 13}}" fill="${{textFill}}">
              ${{label.slice(0, isStory ? 22 : 14)}}
            </text>
            <text x="${{pos.x}}" y="${{pos.y + subtitleY}}" text-anchor="middle" font-family="SF Mono, IBM Plex Mono, monospace" font-size="10" fill="${{textFill}}">
              ${{escapeHtml(subtitle)}}
            </text>
          </g>
        `;
      }}).join("");

      const entityList = entityNodes.length
        ? entityNodes.map((node) => `
            <div class="mini-item">${{escapeHtml(node.label)}} | ${{copy("type", "类型")}}=${{escapeHtml(node.entity_type || "UNKNOWN")}} | ${{copy("in_story", "故事内来源")}}=${{node.in_story_source_count || 0}}</div>
          `).join("")
        : `<div class="empty">${{copy("No entity node captured.", "没有捕获到实体节点。")}}</div>`;

      const relationList = (payload.edges || []).filter((edge) => edge.kind === "entity_relation").length
        ? (payload.edges || []).filter((edge) => edge.kind === "entity_relation").map((edge) => `
            <div class="mini-item">${{escapeHtml(edge.source)}} -> ${{escapeHtml(edge.target)}} | ${{escapeHtml(edge.relation_type || "RELATED")}}</div>
          `).join("")
        : `<div class="empty">${{copy("No direct entity relation captured. Story-level mention edges are still shown above.", "没有直接实体关系；上方仍会展示故事级提及关系。")}}</div>`;

      return `
        <div class="graph-shell">
          <div class="graph-canvas">
            <svg viewBox="0 0 720 320" role="img" aria-label="Story entity graph">
              <rect x="0" y="0" width="720" height="320" fill="transparent"></rect>
              ${{lines}}
              ${{labels}}
            </svg>
          </div>
          <div class="meta">
            <span>${{copy("nodes", "节点")}}=${{payload.nodes.length}}</span>
            <span>${{copy("edges", "边")}}=${{payload.edge_count || 0}}</span>
            <span>${{copy("relations", "关系")}}=${{payload.relation_count || 0}}</span>
            <span>${{copy("entities", "实体")}}=${{payload.entity_count || 0}}</span>
          </div>
          <div class="graph-meta">
            <div class="mini-list">${{entityList}}</div>
            <div class="mini-list">${{relationList}}</div>
          </div>
        </div>
      `;
    }}

    function renderStoryCreateDeck() {{
      const root = $("story-intake-deck");
      if (!root) {{
        return;
      }}
      const draft = normalizeStoryDraft(state.storyDraft || defaultStoryDraft());
      const selectedStory = getStoryRecord(state.selectedStoryId);
      root.innerHTML = `
        <form id="story-create-form">
          <div class="card-top">
            <div>
              <div class="mono">${{copy("manual story", "手工故事")}}</div>
              <h3 class="card-title" style="margin-top:10px;">${{copy("Capture A Brief Before It Gets Lost", "在信号散掉前先补一条故事")}}</h3>
            </div>
            <span class="chip ok">${{copy("lightweight", "轻量录入")}}</span>
          </div>
          <div class="panel-sub">${{copy("Use this for operator-authored briefs, incident notes, or tracking stubs that should be visible before automated clustering catches up.", "适合录入人工简报、事故备注，或那些需要先被看见、再等待自动聚类补齐的追踪占位。")}}</div>
          <div class="chip-row">
            ${{
              storyStatusOptions.map((status) => `
                <button class="chip-btn ${{draft.status === status ? "active" : ""}}" type="button" data-story-draft-status="${{status}}">${{escapeHtml(localizeWord(status))}}</button>
              `).join("")
            }}
          </div>
          <div class="field-grid">
            <label>${{copy("Story Title", "故事标题")}}<input name="title" value="${{escapeHtml(draft.title)}}" placeholder="${{copy("OpenAI launch brief", "OpenAI 发布简报")}}"><span class="field-hint">${{copy("Keep it short and legible in the story list.", "标题尽量短，方便在故事列表里快速扫读。")}}</span></label>
            <label>${{copy("Story Status", "故事状态")}}
              <select name="status">
                ${{storyStatusOptions.map((value) => `<option value="${{value}}" ${{draft.status === value ? "selected" : ""}}>${{localizeWord(value)}}</option>`).join("")}}
              </select>
              <span class="field-hint">${{copy("Status decides which lane this manual story enters first.", "状态决定这条手工故事先落在哪个工作阶段。")}}</span>
            </label>
          </div>
          <label>${{copy("Story Summary", "故事摘要")}}<textarea name="summary" rows="4" placeholder="${{copy("Capture what happened, why it matters, and what still needs confirmation.", "记录发生了什么、为什么重要，以及哪些部分仍待确认。")}}">${{escapeHtml(draft.summary)}}</textarea><span class="field-hint">${{copy("A compact summary is enough. Evidence and timeline can remain empty for manual stories.", "摘要写到够用即可；手工故事不需要一开始就补齐证据和时间线。")}}</span></label>
          <div class="toolbar">
            <button class="btn-primary" type="submit">${{copy("Create Story", "创建故事")}}</button>
            <button class="btn-secondary" type="button" id="story-draft-clear">${{copy("Clear Draft", "清空草稿")}}</button>
            <button class="btn-secondary" type="button" id="story-draft-template" ${{selectedStory ? "" : "disabled"}}>${{copy("Use Selected As Template", "以当前故事为模板")}}</button>
          </div>
        </form>
      `;
      const form = $("story-create-form");
      form?.addEventListener("input", () => {{
        state.storyDraft = collectStoryDraft(form);
      }});
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        await submitStoryDeck(form);
      }});
      root.querySelectorAll("[data-story-draft-status]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.storyDraft = {{
            ...collectStoryDraft(form),
            status: String(button.dataset.storyDraftStatus || "active").trim().toLowerCase() || "active",
          }};
          renderStoryCreateDeck();
        }});
      }});
      $("story-draft-clear")?.addEventListener("click", () => {{
        setStoryDraft(defaultStoryDraft());
        showToast(copy("Story draft cleared", "已清空故事草稿"), "success");
      }});
      $("story-draft-template")?.addEventListener("click", () => {{
        if (!selectedStory) {{
          return;
        }}
        setStoryDraft({{
          title: `${{selectedStory.title || copy("Story", "故事")}} ${{copy("Follow-up", "跟进")}}`,
          summary: String(selectedStory.summary || ""),
          status: String(selectedStory.status || "active"),
        }});
        focusStoryDeck("title");
        showToast(
          state.language === "zh"
            ? `已从 ${{selectedStory.title}} 生成故事草稿`
            : `Story draft cloned from ${{selectedStory.title}}`,
          "success",
        );
      }});
    }}

    function renderStoryDetail() {{
      const root = $("story-detail");
      const selected = state.selectedStoryId;
      if (state.loading.storyDetail && selected) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
      const story = state.storyDetails[selected] || state.stories.find((candidate) => candidate.id === selected);
      if (!story) {{
        root.innerHTML = state.stories.length
          ? `<div class="empty">${{copy("No story is selected in the current filtered workspace.", "当前筛选后的工作区里没有选中的故事。")}}</div>`
          : `
              ${{renderLifecycleGuideCard({{
                title: copy("Stories are the promoted evidence layer", "故事层是被提升后的证据层"),
                summary: copy(
                  "Seed a story manually here when editorial context comes first, or promote one directly from Triage once verified signal is ready. The browser flow does not require a CLI detour.",
                  "如果编辑背景先于聚类出现，可以先在这里手工起一个故事；如果分诊里的已核验证据已经准备好，也可以直接从分诊提升。整个流程不需要再绕回 CLI。"
                ),
                steps: [
                  {{
                    title: copy("Review Triage", "先看分诊"),
                    copy: copy("Use Triage when the story should be grounded in reviewed inbox evidence.", "当故事需要建立在已审阅的收件箱证据上时，先从分诊开始。"),
                  }},
                  {{
                    title: copy("Create Story", "创建故事"),
                    copy: copy("Story Intake captures a manual brief when the narrative should exist immediately.", "如果叙事需要先落下来，故事录入可以直接创建手工简报。"),
                  }},
                  {{
                    title: copy("Refine Summary", "完善摘要"),
                    copy: copy("The workspace lets you tune title, summary, status, and evidence context in one place.", "工作台会把标题、摘要、状态和证据上下文集中到一个位置继续打磨。"),
                  }},
                  {{
                    title: copy("Prepare Delivery", "准备交付"),
                    copy: copy("Attach routes from missions once the story is ready to notify downstream teams.", "当故事准备好触发下游通知时，再回到任务里绑定路由。"),
                  }},
                ],
                actions: [
                  {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true }},
                  {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
                  {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
                ],
              }})}}
              <div class="empty">${{copy("No persisted story snapshot yet.", "当前还没有持久化故事快照。")}}</div>
            `;
        wireLifecycleGuideActions(root);
        return;
      }}
      const storyEvidenceIds = getStoryEvidenceIds(story);
      const storyDeliveryStatus = getStoryDeliveryStatus(story);
      const storySignal = getGovernanceSignal("story_conversion");
      const alertSignal = getGovernanceSignal("alert_yield");
      const routeSummary = state.ops?.route_summary || {{}};
      const evidenceBlock = (rows, emptyLabel) => rows.length
        ? rows.map((row) => `
            <div class="card">
              <div class="card-top">
                <div>
                    <h3 class="card-title">${{row.title}}</h3>
                    <div class="meta">
                      <span>${{row.item_id}}</span>
                      <span>${{row.source_name || row.source_type || "-"}}</span>
                      <span>${{copy("score", "分数")}}=${{row.score || 0}}</span>
                      <span>${{copy("confidence", "置信度")}}=${{Number(row.confidence || 0).toFixed(2)}}</span>
                    </div>
                  </div>
                <span class="chip ${{row.role === "primary" ? "ok" : ""}}">${{copy(row.role || "secondary", row.role === "primary" ? "主证据" : "次证据")}}</span>
              </div>
              <div class="panel-sub">${{row.url || "-"}}</div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-story-evidence-triage="${{row.item_id}}">${{copy("Open In Triage", "回到分诊")}}</button>
              </div>
            </div>
          `).join("")
        : `<div class="empty">${{emptyLabel}}</div>`;
      const contradictionBlock = (story.contradictions || []).length
        ? story.contradictions.map((conflict) => `
            <div class="card">
              <div class="card-top">
                <div>
                    <h3 class="card-title">${{conflict.topic}}</h3>
                    <div class="meta">
                    <span>${{copy("positive", "正向")}}=${{conflict.positive || 0}}</span>
                    <span>${{copy("negative", "负向")}}=${{conflict.negative || 0}}</span>
                    <span>${{copy("neutral", "中性")}}=${{conflict.neutral || 0}}</span>
                    </div>
                  </div>
                <span class="chip hot">${{copy("conflict", "冲突")}}</span>
              </div>
              <div class="panel-sub">${{conflict.note || copy("Cross-source stance divergence detected.", "检测到跨来源立场分歧。")}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No contradiction marker in this story.", "这个故事没有冲突标记。")}}</div>`;
      const timelineBlock = (story.timeline || []).length
        ? story.timeline.map((event) => `
            <div class="card">
              <div class="card-top">
                <div>
                    <h3 class="card-title">${{event.title}}</h3>
                    <div class="meta">
                      <span>${{event.time || "-"}}</span>
                      <span>${{event.source_name || "-"}}</span>
                      <span>${{copy("role", "角色")}}=${{copy(event.role || "secondary", event.role === "primary" ? "主证据" : "次证据")}}</span>
                      <span>${{copy("score", "分数")}}=${{event.score || 0}}</span>
                    </div>
                  </div>
                </div>
              <div class="panel-sub">${{event.url || "-"}}</div>
            </div>
          `).join("")
        : `<div class="empty">${{copy("No timeline event captured.", "当前没有时间线事件。")}}</div>`;
      const markdownPreview = state.storyMarkdown[selected]
        ? `
            <div class="card">
              <div class="mono">${{copy("markdown evidence pack", "Markdown 证据包")}}</div>
              <pre class="text-block">${{escapeHtml(state.storyMarkdown[selected])}}</pre>
            </div>
          `
        : "";
      const graphPreview = renderStoryGraph(state.storyGraph[selected]);
      const storyContinuityBlock = renderLifecycleContinuityCard({{
        title: copy("Story Delivery Readiness", "故事交付就绪度"),
        summary: copy(
          "Evidence, story editing, and downstream delivery status stay connected around the same narrative object.",
          "证据、故事编辑和下游交付状态会继续围绕同一个叙事对象保持连贯。"
        ),
        stages: [
          {{
            kicker: copy("Review", "审阅"),
            title: copy("Evidence Context", "证据上下文"),
            copy: copy(
              "Primary and secondary evidence stay visible so the story never drifts away from reviewed signal.",
              "主次证据会继续保持可见，避免故事脱离已审阅信号。"
            ),
            tone: storyEvidenceIds.length ? "ok" : "",
            facts: [
              {{ label: copy("Evidence", "证据"), value: String(storyEvidenceIds.length) }},
              {{ label: copy("Primary item", "主条目"), value: story.primary_item_id || "-" }},
              {{ label: copy("Conflicts", "冲突"), value: String((story.contradictions || []).length) }},
            ],
          }},
          {{
            kicker: copy("Current", "当前"),
            title: copy("Story Workspace", "故事工作台"),
            copy: copy(
              "Narrative edits happen beside evidence, timeline, and entity structure instead of in a detached editor.",
              "叙事编辑会与证据、时间线和实体结构并排存在，而不是进入一个脱离上下文的编辑器。"
            ),
            tone: storyDeliveryStatus.tone || "ok",
            facts: [
              {{ label: copy("Status", "状态"), value: localizeWord(story.status || "active") }},
              {{ label: copy("Updated", "更新"), value: formatCompactDateTime(story.updated_at || story.generated_at || "") }},
              {{ label: copy("Delivery", "交付"), value: storyDeliveryStatus.label }},
            ],
          }},
          {{
            kicker: copy("Delivery", "交付"),
            title: copy("Output Handoff", "输出交接"),
            copy: copy(
              "Ready stories, alerting missions, and route health stay nearby so the delivery decision is visible before you leave the workspace.",
              "待交付故事、触发告警的任务和路由健康会保留在附近，方便在离开工作台前判断是否该进入交付。"
            ),
            tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
            facts: [
              {{ label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) }},
              {{ label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) }},
              {{ label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) }},
            ],
          }},
        ],
        actions: [
          {{ label: copy("Focus Evidence In Triage", "回查分诊证据"), section: "section-triage", primary: true }},
          {{ label: copy("Open Delivery", "打开交付"), section: "section-ops" }},
          {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
        ],
      }});
      const storyGuidanceBlock = buildStoryGuidanceSurface(story, storyDeliveryStatus);
      root.innerHTML = `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{story.title}}</h3>
              <div class="meta">
                <span>${{story.id}}</span>
                <span>${{copy("status", "状态")}}=${{localizeWord(story.status || "active")}}</span>
                <span>${{copy("items", "条目")}}=${{story.item_count || 0}}</span>
                <span>${{copy("sources", "来源")}}=${{story.source_count || 0}}</span>
                <span>${{copy("score", "分数")}}=${{Number(story.score || 0).toFixed(1)}}</span>
                <span>${{copy("confidence", "置信度")}}=${{Number(story.confidence || 0).toFixed(2)}}</span>
              </div>
            </div>
            <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? copy("mixed signals", "信号冲突") : copy("aligned", "一致")}}</span>
          </div>
          <div class="panel-sub">${{story.summary || copy("No summary captured.", "没有记录到摘要。")}}</div>
          <div class="entity-row">
            ${{(story.entities || []).slice(0, 8).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || `<span class="chip">${{copy("no entities", "无实体")}}</span>`}}
          </div>
          <div class="actions">
            <button class="btn-secondary" data-story-markdown="${{story.id}}">${{copy("Preview Markdown", "预览 Markdown")}}</button>
            <button class="btn-secondary" type="button" data-story-focus-triage="${{story.id}}" ${{storyEvidenceIds.length ? "" : "disabled"}}>${{copy("Focus Evidence In Triage", "回查分诊证据")}}</button>
            <a href="/api/stories/${{story.id}}" target="_blank" rel="noreferrer">${{copy("Open JSON", "打开 JSON")}}</a>
            <a href="/api/stories/${{story.id}}/export?format=markdown" target="_blank" rel="noreferrer">${{copy("Export MD", "导出 MD")}}</a>
          </div>
        </div>
        ${{storyContinuityBlock}}
        ${{storyGuidanceBlock}}
        <div class="card">
          <div class="mono">${{copy("story editor", "故事编辑器")}}</div>
          <div class="meta" style="margin-top:8px;">
            <span class="chip ok">${{copy("editable", "可编辑")}}</span>
            <span>${{copy("Only title, summary, and status change here.", "这里只修改标题、摘要和状态。")}}</span>
          </div>
          <div class="panel-sub">${{copy("Tune the persisted title, summary, and story status without rebuilding the whole workspace snapshot.", "无需重建整个工作区快照，也能直接调整已持久化的标题、摘要和故事状态。")}}</div>
          <form id="story-editor-form" data-story-id="${{story.id}}" style="margin-top:12px;">
            <div class="field-grid">
              <label>${{copy("Story Title", "故事标题")}}<input name="title" value="${{escapeHtml(story.title || "")}}" placeholder="${{copy("OpenAI Launch Story", "OpenAI 发布故事")}}"></label>
              <label>${{copy("Story Status", "故事状态")}}
                <select name="status">
                  ${{storyStatusOptions.map((value) => `<option value="${{value}}" ${{(story.status || "active") === value ? "selected" : ""}}>${{localizeWord(value)}}</option>`).join("")}}
                </select>
              </label>
            </div>
            <label>${{copy("Story Summary", "故事摘要")}}<textarea name="summary" rows="4" placeholder="${{copy("Condense why this story matters right now.", "简要说明这个故事此刻为什么重要。")}}">${{escapeHtml(story.summary || "")}}</textarea></label>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${{copy("Save Story", "保存故事")}}</button>
              <button class="btn-secondary" type="button" data-story-detail-status="${{story.status === "archived" ? "active" : "archived"}}">${{story.status === "archived" ? copy("Restore Story", "恢复故事") : copy("Archive Story", "归档故事")}}</button>
              <button class="btn-danger" type="button" data-story-delete="${{story.id}}">${{copy("Delete Story", "删除故事")}}</button>
            </div>
          </form>
        </div>
        <div class="story-columns">
          <div class="stack">
            <div class="meta"><span class="mono">${{copy("primary evidence", "主证据")}}</span><span class="chip">${{copy("read-only snapshot", "只读快照")}}</span></div>
            ${{evidenceBlock(story.primary_evidence || [], copy("No primary evidence captured.", "没有主证据。"))}}
          </div>
          <div class="stack">
            <div class="meta"><span class="mono">${{copy("secondary evidence", "次证据")}}</span><span class="chip">${{copy("read-only snapshot", "只读快照")}}</span></div>
            ${{evidenceBlock(story.secondary_evidence || [], copy("No secondary evidence captured.", "没有次证据。"))}}
          </div>
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("contradiction markers", "冲突标记")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
          ${{contradictionBlock}}
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("timeline", "时间线")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
          ${{timelineBlock}}
        </div>
        <div class="stack">
          <div class="meta"><span class="mono">${{copy("entity graph", "实体图谱")}}</span><span class="chip">${{copy("read-only analysis", "只读分析")}}</span></div>
          ${{graphPreview}}
        </div>
        ${{markdownPreview}}
      `;

      root.querySelectorAll("[data-story-markdown]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await previewStoryMarkdown(button.dataset.storyMarkdown);
          }} catch (error) {{
            reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      root.querySelector("[data-story-focus-triage]")?.addEventListener("click", () => {{
        focusTriageEvidence(storyEvidenceIds, {{ itemId: story.primary_item_id || storyEvidenceIds[0] || "" }});
      }});
      root.querySelectorAll("[data-story-evidence-triage]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const itemId = String(button.dataset.storyEvidenceTriage || "").trim();
          if (!itemId) {{
            return;
          }}
          focusTriageEvidence(storyEvidenceIds, {{ itemId }});
        }});
      }});

      const storyEditorForm = document.getElementById("story-editor-form");
      if (storyEditorForm) {{
        storyEditorForm.addEventListener("submit", async (event) => {{
          event.preventDefault();
          const form = new FormData(storyEditorForm);
          const payload = {{
            title: String(form.get("title") || "").trim(),
            summary: String(form.get("summary") || "").trim(),
            status: String(form.get("status") || "").trim(),
          }};
          if (!payload.title) {{
            showToast(copy("Provide a story title before saving.", "保存前请先填写故事标题。"), "error");
            return;
          }}
          const submitButton = storyEditorForm.querySelector("button[type='submit']");
          if (submitButton) {{
            submitButton.disabled = true;
          }}
          const previousStory = {{
            title: story.title || "",
            summary: story.summary || "",
            status: story.status || "active",
          }};
          if (state.storyDetails[story.id]) {{
            state.storyDetails[story.id] = {{
              ...state.storyDetails[story.id],
              ...payload,
            }};
          }}
          renderStories();
          try {{
            await api(`/api/stories/${{story.id}}`, {{
              method: "PUT",
              payload,
            }});
            state.storyMarkdown[story.id] = "";
            pushActionEntry({{
              kind: copy("story update", "故事更新"),
              label: state.language === "zh" ? `已更新故事：${{payload.title}}` : `Updated story ${{payload.title}}`,
              detail: state.language === "zh" ? `当前故事状态为 ${{localizeWord(payload.status || "active")}}。` : `Story status is now ${{payload.status || "active"}}.`,
              undoLabel: copy("Restore story", "恢复故事"),
              undo: async () => {{
                await api(`/api/stories/${{story.id}}`, {{
                  method: "PUT",
                  payload: previousStory,
                }});
                await refreshBoard();
                showToast(
                  state.language === "zh" ? `已恢复故事：${{previousStory.title}}` : `Story restored: ${{previousStory.title}}`,
                  "success",
                );
              }},
            }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `故事已更新：${{payload.title}}` : `Story updated: ${{payload.title}}`,
              "success",
            );
          }} catch (error) {{
            if (state.storyDetails[story.id]) {{
              state.storyDetails[story.id] = {{
                ...state.storyDetails[story.id],
                ...previousStory,
              }};
            }}
            renderStories();
            reportError(error, copy("Update story", "更新故事"));
          }} finally {{
            if (submitButton) {{
              submitButton.disabled = false;
            }}
          }}
        }});
      }}
      root.querySelector("[data-story-detail-status]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await setStoryStatusQuick(story.id, String(button.dataset.storyDetailStatus || ""));
        }} catch (error) {{
          reportError(error, copy("Update story state", "更新故事状态"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-story-delete]")?.addEventListener("click", async (event) => {{
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await deleteStoryFromWorkspace(String(button.dataset.storyDelete || story.id));
        }} catch (error) {{
          reportError(error, copy("Delete story", "删除故事"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      wireLifecycleGuideActions(root);
    }}

    function renderStories() {{
      const root = $("story-list");
      const inlineStats = $("story-stats-inline");
      renderStoryViewJumpStrip();
      renderStoryCreateDeck();
      if (state.loading.board && !state.stories.length) {{
        renderStorySectionSummary();
        inlineStats.innerHTML = `<span>${{copy("loading", "加载中")}}=stories</span>`;
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        $("story-detail").innerHTML = skeletonCard(5);
        renderTopbarContext();
        return;
      }}
      const contradictions = state.stories.reduce((count, story) => count + ((story.contradictions || []).length ? 1 : 0), 0);
      const totalEvidence = state.stories.reduce((count, story) => count + (story.item_count || 0), 0);
      const storySearchValue = String(state.storySearch || "");
      const storySearchQuery = storySearchValue.trim().toLowerCase();
      const storyFilter = normalizeStoryFilter(state.storyFilter);
      const storySort = normalizeStorySort(state.storySort);
      const activeStoryView = detectStoryViewPreset({{ filter: storyFilter, sort: storySort, search: storySearchValue }});
      const matchedStories = state.stories.filter((story) => {{
        const storyStatus = String(story.status || "active").trim().toLowerCase() || "active";
        if (storyFilter === "conflicted" && !(Array.isArray(story.contradictions) && story.contradictions.length)) {{
          return false;
        }}
        if (storyFilter !== "all" && storyFilter !== "conflicted" && storyStatus !== storyFilter) {{
          return false;
        }}
        if (!storySearchQuery) {{
          return true;
        }}
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
      }});
      const filteredStories = [...matchedStories].sort((left, right) => compareStoriesByWorkspaceOrder(left, right, storySort));
      const defaultStoryId = filteredStories[0] ? filteredStories[0].id : (state.stories[0] ? state.stories[0].id : "");
      const visibleStoryIds = new Set(filteredStories.map((story) => story.id));
      state.selectedStoryIds = uniqueValues(state.selectedStoryIds).filter((storyId) => visibleStoryIds.has(storyId));
      const storyFilterOptions = [
        {{ key: "all", label: copy("all", "全部"), count: state.stories.length }},
        {{ key: "conflicted", label: copy("conflicted", "冲突"), count: contradictions }},
        ...["active", "monitoring", "resolved", "archived"].map((key) => ({{
          key,
          label: localizeWord(key),
          count: state.stories.filter((story) => (String(story.status || "active").trim().toLowerCase() || "active") === key).length,
        }})),
      ];
      inlineStats.innerHTML = `
        <span>${{copy("stories", "故事")}}=${{state.stories.length}}</span>
        <span>${{copy("evidence", "证据")}}=${{totalEvidence}}</span>
        <span>${{copy("contradicted", "冲突故事")}}=${{contradictions}}</span>
        <span>${{copy("shown", "显示")}}=${{filteredStories.length}}</span>
        <span>${{copy("view", "视图")}}=${{storyViewPresetLabel(activeStoryView)}}</span>
        <span>${{copy("sort", "排序")}}=${{storySortLabel(storySort)}}</span>
        <span>${{copy("selected", "已选")}}=${{state.selectedStoryIds.length}}</span>
        <span>${{copy("selected", "选中")}}=${{state.selectedStoryId || "-"}}</span>
      `;
      const storyBatchCount = state.selectedStoryIds.length;
      const storyBatchBusy = Boolean(state.storyBulkBusy);
      const storySearchCard = `
        <div class="card section-toolbox">
          <div class="section-toolbox-head">
            <div>
              <div class="mono">${{copy("story search", "故事搜索")}}</div>
              <div class="panel-sub">${{copy("Search by story title, summary, entity, id, or primary evidence title before opening the workspace.", "可按故事标题、摘要、实体、故事 ID 或主证据标题快速定位。")}}</div>
            </div>
            <div class="section-toolbox-meta">
              <button class="btn-secondary" type="button" data-story-deck-focus>${{copy("New Story", "新建故事")}}</button>
              <span class="chip ${{activeStoryView === "custom" ? "hot" : "ok"}}">${{storyViewPresetLabel(activeStoryView)}}</span>
              <span class="chip ok">${{storySortLabel(storySort)}}</span>
              <span class="chip">${{copy("shown", "显示")}}=${{filteredStories.length}}</span>
              <span class="chip">${{copy("total", "总数")}}=${{state.stories.length}}</span>
            </div>
          </div>
          <div class="search-shell">
            <input type="search" value="${{escapeHtml(storySearchValue)}}" data-story-search placeholder="${{copy("Search stories", "搜索故事")}}">
            <button class="btn-secondary" type="button" data-story-search-clear ${{storySearchValue.trim() ? "" : "disabled"}}>${{copy("Clear", "清空")}}</button>
          </div>
          <div class="field-grid" style="margin-top:12px;">
            <label>${{copy("Story Sort", "故事排序")}}
              <select data-story-sort>
                ${{storySortOptions.map((option) => `<option value="${{option}}" ${{storySort === option ? "selected" : ""}}>${{storySortLabel(option)}}</option>`).join("")}}
              </select>
            </label>
            <div>
              <div class="mono">${{copy("view hint", "视图提示")}}</div>
              <div class="panel-sub">${{activeStoryView === "custom" ? storySortSummary(storySort) : storyViewPresetDescription(activeStoryView)}}</div>
            </div>
          </div>
          <div class="chip-row">
            ${{storyViewPresetOptions.map((option) => `
              <button class="chip-btn ${{activeStoryView === option ? "active" : ""}}" type="button" data-story-view="${{escapeHtml(option)}}">${{escapeHtml(storyViewPresetLabel(option))}}</button>
            `).join("")}}
            ${{activeStoryView === "custom" ? `<span class="chip hot">${{storyViewPresetLabel("custom")}}</span>` : ""}}
          </div>
          <div class="chip-row">
            ${{storyFilterOptions.map((option) => `
              <button class="chip-btn ${{storyFilter === option.key ? "active" : ""}}" type="button" data-story-filter="${{escapeHtml(option.key)}}">${{escapeHtml(option.label)}} (${{option.count || 0}})</button>
            `).join("")}}
          </div>
        </div>
      `;
      const storyBatchToolbar = `
        <div class="card batch-toolbar-card ${{storyBatchCount ? "selection-live" : ""}}">
          <div class="batch-toolbar">
            <div class="batch-toolbar-head">
              <div>
                <div class="mono">${{copy("story batch", "故事批量操作")}}</div>
                <div class="panel-sub">${{
                  storyBatchCount
                    ? copy(`Selected ${{storyBatchCount}} stories. Move them together to reduce workspace churn.`, `已选 ${{storyBatchCount}} 条故事，可以一起切换状态。`)
                    : copy("Select visible stories when you need to archive, monitor, or resolve a whole lane together.", "当你需要整体归档、恢复监控或批量解决时，可以先选择当前可见故事。")
                }}</div>
              </div>
              <span class="chip ${{storyBatchCount ? "ok" : ""}}">${{copy("selected", "已选")}}=${{storyBatchCount}}</span>
            </div>
            ${{
              storyBatchCount
                ? `<div class="actions">
                    <button class="btn-secondary" type="button" data-story-selection-clear ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Clear Selection", "清空选择")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="monitoring" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Monitor", "批量监控")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="resolved" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Resolve", "批量解决")}}</button>
                    <button class="btn-secondary" type="button" data-story-batch-status="archived" ${{storyBatchBusy ? "disabled" : ""}}>${{copy("Batch Archive", "批量归档")}}</button>
                  </div>`
                : `<div class="actions">
                    <button class="btn-secondary" type="button" data-story-select-visible ${{(!filteredStories.length || storyBatchBusy) ? "disabled" : ""}}>${{copy("Select Visible", "选择当前列表")}}</button>
                  </div>`
            }}
          </div>
        </div>
      `;
      if (!state.stories.length) {{
        renderStorySectionSummary({{
          filteredStories: [],
          activeStoryView,
          storySort,
          storySearchValue,
        }});
        root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}${{renderLifecycleGuideCard({{
          title: copy("Promote verified signal into a story without leaving the browser", "无需离开浏览器，也能把已核验信号提升为故事"),
          summary: copy(
            "Use Story Intake for a manual brief, or create a story from Triage once the queue has enough evidence. Story edits, evidence review, and route setup can all stay inside this shell.",
            "可以用故事录入先写一条手工简报，也可以在分诊证据足够时直接提升成故事。后续的故事编辑、证据回查和路由设置都可以继续留在这个界面里完成。"
          ),
          steps: [
            {{
              title: copy("Start From Triage", "从分诊开始"),
              copy: copy("Create Story is the fastest path when verified inbox evidence already exists.", "如果收件箱里已经有已核验证据，直接创建故事是最快路径。"),
            }},
            {{
              title: copy("Or Seed Manually", "或手工起稿"),
              copy: copy("Story Intake is better when the narrative needs to exist before clustering catches up.", "如果叙事需要先存在、而聚类还没跟上，故事录入会更合适。"),
            }},
            {{
              title: copy("Refine In Workspace", "在工作台完善"),
              copy: copy("Tune title, summary, status, contradictions, and evidence context here.", "标题、摘要、状态、冲突点和证据上下文都可以在这里继续完善。"),
            }},
            {{
              title: copy("Link Delivery", "连接交付"),
              copy: copy("Attach named routes from missions once the story is ready for downstream notification.", "当故事准备好通知下游时，再从任务里把命名路由接上。"),
            }},
          ],
          actions: [
            {{ label: copy("Focus Story Intake", "聚焦故事录入"), focus: "story", field: "title", primary: true }},
            {{ label: copy("Open Triage", "打开分诊"), section: "section-triage" }},
            {{ label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" }},
          ],
        }})}}<div class="empty">${{copy("No story snapshot yet.", "当前还没有故事快照。")}}</div>`;
        wireLifecycleGuideActions(root);
        root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
          focusStoryDeck("title");
        }});
        root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
          state.storySearch = event.target.value;
          renderStories();
        }});
        root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
          state.storySearch = "";
          renderStories();
        }});
        root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
          state.storySort = normalizeStorySort(event.target.value);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
        root.querySelectorAll("[data-story-view]").forEach((button) => {{
          button.addEventListener("click", () => {{
            applyStoryViewPreset(String(button.dataset.storyView || "").trim());
          }});
        }});
        root.querySelectorAll("[data-story-filter]").forEach((button) => {{
          button.addEventListener("click", () => {{
            state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
            persistStoryWorkspacePrefs();
            renderStories();
          }});
        }});
        syncStoryUrlState({{ defaultStoryId }});
        flushStoryUrlFocus();
        renderTopbarContext();
        renderStoryDetail();
        return;
      }}
      if (filteredStories.length && !filteredStories.some((story) => story.id === state.selectedStoryId)) {{
        state.selectedStoryId = filteredStories[0].id;
      }}
      if (!filteredStories.length) {{
        state.selectedStoryId = "";
        renderStorySectionSummary({{
          filteredStories: [],
          activeStoryView,
          storySort,
          storySearchValue,
        }});
        root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}<div class="empty">${{copy("No story matched the current search or filter.", "没有故事匹配当前搜索或筛选。")}}</div>`;
        renderStoryDetail();
        root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
          focusStoryDeck("title");
        }});
        root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
          state.storySearch = event.target.value;
          renderStories();
        }});
        root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
          state.storySearch = "";
          renderStories();
        }});
        root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
          state.storySort = normalizeStorySort(event.target.value);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
        root.querySelectorAll("[data-story-view]").forEach((button) => {{
          button.addEventListener("click", () => {{
            applyStoryViewPreset(String(button.dataset.storyView || "").trim());
          }});
        }});
        root.querySelectorAll("[data-story-filter]").forEach((button) => {{
          button.addEventListener("click", () => {{
            state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
            persistStoryWorkspacePrefs();
            renderStories();
          }});
        }});
        syncStoryUrlState({{ defaultStoryId }});
        flushStoryUrlFocus();
        renderTopbarContext();
        return;
      }}
      renderStorySectionSummary({{
        filteredStories,
        activeStoryView,
        storySort,
        storySearchValue,
      }});
      root.innerHTML = `${{storySearchCard}}${{storyBatchToolbar}}${{filteredStories.map((story) => {{
        const selected = story.id === state.selectedStoryId ? "selected" : "";
        const primary = (story.primary_evidence || [])[0];
        const updatedLabel = formatCompactDateTime(story.updated_at || story.generated_at || "");
        const priority = describeStoryPriority(story);
        const deliveryStatus = getStoryDeliveryStatus(story);
        const actionHierarchy = getStoryCardActionHierarchy(story);
        return `
          <div class="card selectable ${{selected}}" data-story-card="${{story.id}}">
            <div class="card-top">
              <div>
                <label class="checkbox-inline" style="margin-bottom:8px;">
                  <input type="checkbox" data-story-select="${{story.id}}" ${{isStorySelected(story.id) ? "checked" : ""}}>
                  <span>${{copy("select", "选择")}}</span>
                </label>
                <h3 class="card-title">${{story.title}}</h3>
                <div class="meta">
                  <span>${{story.id}}</span>
                  <span>${{copy("status", "状态")}}=${{localizeWord(story.status || "active")}}</span>
                  <span>${{copy("updated", "更新")}}=${{updatedLabel}}</span>
                </div>
                <div class="meta">
                  <span>${{copy("items", "条目")}}=${{story.item_count || 0}}</span>
                  <span>${{copy("sources", "来源")}}=${{story.source_count || 0}}</span>
                  <span>${{copy("score", "分数")}}=${{Number(story.score || 0).toFixed(1)}}</span>
                  <span>${{copy("confidence", "置信度")}}=${{Number(story.confidence || 0).toFixed(2)}}</span>
                </div>
              </div>
              <span class="chip ${{(story.contradictions || []).length ? "hot" : "ok"}}">${{(story.contradictions || []).length ? copy("mixed", "冲突") : copy("aligned", "一致")}}</span>
            </div>
            <div class="panel-sub">${{story.summary || copy("No summary captured.", "没有记录到摘要。")}}</div>
            <div class="entity-row">
              <span class="chip ${{priority.tone}}">${{priority.label}}</span>
              ${{(story.entities || []).slice(0, 4).map((entity) => `<span class="chip">${{entity}}</span>`).join("") || `<span class="chip">${{copy("no entities", "无实体")}}</span>`}}
            </div>
            <div class="meta">
              <span>${{copy("primary", "主证据")}}=${{primary ? primary.title : "-"}}</span>
              <span>${{copy("timeline", "时间线")}}=${{(story.timeline || []).length}}</span>
              <span>${{copy("conflicts", "冲突")}}=${{(story.contradictions || []).length}}</span>
              <span>${{copy("delivery", "交付")}}=${{deliveryStatus.label}}</span>
            </div>
            ${{renderCardActionHierarchy(actionHierarchy)}}
          </div>
        `;
      }}).join("")}}`;

      root.querySelector("[data-story-deck-focus]")?.addEventListener("click", () => {{
        focusStoryDeck("title");
      }});

      root.querySelector("[data-story-search]")?.addEventListener("input", (event) => {{
        state.storySearch = event.target.value;
        renderStories();
      }});

      root.querySelector("[data-story-search-clear]")?.addEventListener("click", () => {{
        state.storySearch = "";
        renderStories();
      }});

      root.querySelector("[data-story-sort]")?.addEventListener("change", (event) => {{
        state.storySort = normalizeStorySort(event.target.value);
        persistStoryWorkspacePrefs();
        renderStories();
      }});

      root.querySelectorAll("[data-story-view]").forEach((button) => {{
        button.addEventListener("click", () => {{
          applyStoryViewPreset(String(button.dataset.storyView || "").trim());
        }});
      }});

      root.querySelector("[data-story-select-visible]")?.addEventListener("click", () => {{
        selectVisibleStories(filteredStories);
        renderStories();
      }});

      root.querySelector("[data-story-selection-clear]")?.addEventListener("click", () => {{
        clearStorySelection();
        renderStories();
      }});

      root.querySelectorAll("[data-story-filter]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.storyFilter = normalizeStoryFilter(button.dataset.storyFilter);
          persistStoryWorkspacePrefs();
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-batch-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await runStoryBatchStatusUpdate(state.selectedStoryIds, String(button.dataset.storyBatchStatus || "").trim());
          }} catch (error) {{
            reportError(error, copy("Batch update stories", "批量更新故事"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-card]").forEach((card) => {{
        card.addEventListener("click", (event) => {{
          if (event.target.closest("button, textarea, input, select, a, form, label")) {{
            return;
          }}
          state.selectedStoryId = String(card.dataset.storyCard || "").trim();
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-select]").forEach((input) => {{
        input.addEventListener("change", () => {{
          toggleStorySelection(String(input.dataset.storySelect || "").trim(), input.checked);
          renderStories();
        }});
      }});

      root.querySelectorAll("[data-story-open]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            const requestedMode = String(button.dataset.storyOpenMode || "").trim();
            await loadStory(button.dataset.storyOpen, {{
              mode: requestedMode || undefined,
              syncUrl: true,
            }});
          }} catch (error) {{
            reportError(error, copy("Open story", "打开故事"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-preview]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await previewStoryMarkdown(button.dataset.storyPreview);
          }} catch (error) {{
            reportError(error, copy("Preview story markdown", "预览故事 Markdown"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      root.querySelectorAll("[data-story-quick-status]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          button.disabled = true;
          try {{
            await setStoryStatusQuick(
              String(button.dataset.storyQuickStatus || ""),
              String(button.dataset.storyNextStatus || ""),
            );
          }} catch (error) {{
            reportError(error, copy("Update story state", "更新故事状态"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});

      syncStoryUrlState({{ defaultStoryId }});
      flushStoryUrlFocus();
      renderTopbarContext();
      renderStoryDetail();
    }}

    function renderReportQualityBlock(quality) {{
      if (!quality || typeof quality !== "object") {{
        return `<div class="empty">${{copy("No quality snapshot yet. Refresh the report composition to inspect guardrails.", "还没有质量快照。刷新一次报告编排后再查看门禁。")}}</div>`;
      }}
      const checks = quality.checks && typeof quality.checks === "object" ? quality.checks : {{}};
      const renderedChecks = Object.entries(checks).length
        ? Object.entries(checks).map(([key, check]) => {{
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
                    <h3 class="card-title">${{escapeHtml(formatReportCheckLabel(key))}}</h3>
                    <div class="meta">
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(status || "draft"))}}</span>
                      ${{summaryPairs.map(([summaryKey, summaryValue]) => `<span>${{escapeHtml(String(summaryKey).replace(/_/g, " "))}}=${{escapeHtml(String(summaryValue))}}</span>`).join("")}}
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(status)}}">${{escapeHtml(localizeWord(status || "draft"))}}</span>
                </div>
                <div class="stack">
                  ${{issues.length
                    ? issues.slice(0, 4).map((issue) => `
                        <div class="card">
                          <div class="panel-sub">${{escapeHtml(issue.detail || issue.kind || JSON.stringify(issue))}}</div>
                        </div>
                      `).join("")
                    : `<div class="empty">${{copy("No blocking issue recorded for this gate.", "这个门禁当前没有阻断问题。")}}</div>`}}
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No guardrail checks were returned.", "当前没有返回质量门禁检查。")}}</div>`;

      return `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${{copy("Quality Guardrails", "质量门禁")}}</h3>
              <div class="meta">
                <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(quality.status || "draft"))}}</span>
                <span>${{copy("score", "分数")}}=${{escapeHtml(Number(quality.score || 0).toFixed(2))}}</span>
                <span>${{copy("action", "动作")}}=${{escapeHtml(formatReportOperatorAction(quality.operator_action || ""))}}</span>
              </div>
            </div>
            <span class="chip ${{reportStatusTone(quality.status)}}">${{quality.can_export ? copy("export ready", "可导出") : copy("hold", "暂停")}}</span>
          </div>
          <div class="panel-sub">${{quality.can_export
            ? copy("The current report composition satisfies the visible guardrails.", "当前报告编排满足可见质量门禁。")
            : copy("Resolve the highlighted guardrails before treating this report as ready.", "先解决下面标出的质量门禁，再把这份报告视为就绪。")}}</div>
        </div>
        <div class="stack">${{renderedChecks}}</div>
      `;
    }}

    function renderClaimsWorkspace() {{
      const root = $("claim-composer-shell");
      if (!root) {{
        return;
      }}
      if (state.loading.board && !state.claimCards.length && !state.reports.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
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
        ? state.claimCards.map((claim) => {{
            const claimId = String(claim.id || "").trim();
            const claimLabel = getClaimCardLabel(claim) || claimId;
            const isSelected = claimId === String(state.selectedClaimId || "").trim();
            const inReport = reportClaimIds.has(claimId);
            const inSection = selectedSectionClaimIds.has(claimId);
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(claimLabel)}}</h3>
                    <div class="meta">
                      <span>${{claimId}}</span>
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(claim.status || "draft"))}}</span>
                      <span>${{copy("confidence", "置信度")}}=${{escapeHtml(Number(claim.confidence || 0).toFixed(2))}}</span>
                    </div>
                  </div>
                  <span class="chip ${{isSelected ? "ok" : reportStatusTone(claim.status)}}">${{escapeHtml(localizeWord(claim.status || "draft"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(claim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}}</div>
                <div class="meta">
                  <span class="chip ${{inReport ? "ok" : ""}}">${{inReport ? copy("in report", "已挂入报告") : copy("unassigned", "未挂接")}}</span>
                  <span class="chip ${{inSection ? "ok" : ""}}">${{selectedSection ? (inSection ? copy("in section", "已挂入章节") : copy("outside section", "未挂入章节")) : copy("report only", "仅报告级")}}</span>
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-claim-select="${{claimId}}">${{copy("Inspect", "查看")}}</button>
                  <button class="btn-secondary" type="button" data-claim-attach="${{claimId}}" ${{selectedReport ? "" : "disabled"}}>${{selectedSection ? copy("Attach To Section", "挂到章节") : copy("Attach To Report", "挂到报告")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No claim cards yet. Create the first source-bound claim on the left.", "当前还没有主张卡。先在左侧创建第一条带来源的主张。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Current Composition Target", "当前编排目标")}}</h3>
                  <div class="meta">
                    <span>${{copy("report", "报告")}}=${{escapeHtml(selectedReport ? (selectedReport.title || selectedReport.id) : copy("not set", "未设置"))}}</span>
                    <span>${{copy("section", "章节")}}=${{escapeHtml(selectedSection ? (selectedSection.title || selectedSection.id) : copy("report level", "报告级"))}}</span>
                    <span>${{copy("quality", "质量")}}=${{escapeHtml(selectedQuality ? localizeWord(selectedQuality.status || "draft") : copy("not loaded", "未加载"))}}</span>
                  </div>
                </div>
                <span class="chip ${{reportStatusTone(selectedQuality?.status || selectedReport?.status || "")}}">${{escapeHtml(localizeWord(selectedQuality?.status || selectedReport?.status || "draft"))}}</span>
              </div>
              <div class="panel-sub">${{selectedReport
                ? copy("Claims stay report-backed. Pick a section when the judgment should appear inside a specific narrative block.", "主张始终绑定到持久化报告。只有在需要进入具体叙事块时，再选择某个章节。")
                : copy("Choose or create a report in Report Studio, then come back to bind claims into sections.", "先去报告工作台选择或创建一份报告，再回来把主张挂进章节。")}}</div>
              <div class="field-grid" style="margin-top:12px;">
                <label>${{copy("Report", "报告")}}
                  <select id="claim-report-select">
                    <option value="">${{copy("No report selected", "未选择报告")}}</option>
                    ${{state.reports.map((report) => `<option value="${{escapeHtml(report.id)}}" ${{String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}}>${{escapeHtml(report.title || report.id)}}</option>`).join("")}}
                  </select>
                </label>
                <label>${{copy("Section", "章节")}}
                  <select id="claim-section-select" ${{selectedReport ? "" : "disabled"}}>
                    <option value="">${{copy("Attach at report level", "挂到报告级")}}</option>
                    ${{sections.map((section) => `<option value="${{escapeHtml(section.id)}}" ${{String(section.id || "") === String(state.selectedReportSectionId || "") ? "selected" : ""}}>${{escapeHtml(section.title || section.id)}}</option>`).join("")}}
                  </select>
                </label>
              </div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-claims-open-report-studio>${{copy("Open Report Studio", "打开报告工作台")}}</button>
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}" target="_blank" rel="noreferrer">${{copy("Open Report JSON", "打开报告 JSON")}}</a>` : ""}}
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Create Claim", "创建主张")}}</h3>
                  <div class="panel-sub">${{copy("Capture the bounded judgment here, then persist its source binding immediately.", "先记录边界明确的判断，再立即把来源绑定写进去。")}}</div>
                </div>
                <span class="chip ok">${{copy("persisted", "持久化")}}</span>
              </div>
              <form id="claim-composer-form" style="margin-top:12px;">
                <label>${{copy("Statement", "主张语句")}}<textarea name="statement" rows="3" placeholder="${{copy("AI adoption is landing first in quantity takeoff and schedule control.", "AI 最先在算量和计划控制环节跑通。")}}"></textarea></label>
                <label>${{copy("Rationale", "理由")}}<textarea name="rationale" rows="3" placeholder="${{copy("State the boundary, evidence pattern, or operational reason behind the claim.", "记录这个主张背后的边界、证据模式或业务理由。")}}"></textarea></label>
                <div class="field-grid">
                  <label>${{copy("Confidence", "置信度")}}<input name="confidence" type="number" min="0" max="1" step="0.01" value="0.8"></label>
                  <label>${{copy("Status", "状态")}}
                    <select name="status">
                      ${{claimStatusOptions.map((status) => `<option value="${{status}}">${{localizeWord(status)}}</option>`).join("")}}
                    </select>
                  </label>
                </div>
                <label>${{copy("Source Item IDs", "来源条目 ID")}}<input name="source_item_ids" placeholder="${{copy("item-123, item-456", "item-123, item-456")}}"><span class="field-hint">${{copy("Use commas or new lines when the claim already points to stored inbox items.", "如果主张已经对应到已存储条目，可以用逗号或换行补充 item ID。")}}</span></label>
                <label>${{copy("Source URLs", "来源 URL")}}<textarea name="source_urls" rows="3" placeholder="${{copy("https://example.com/source-a", "https://example.com/source-a")}}"></textarea><span class="field-hint">${{copy("URLs create a citation bundle so the claim stays source-bound even before every item is normalized into inbox IDs.", "URL 会生成 citation bundle，这样即使条目还没完全落进 inbox ID，主张也能保持来源绑定。")}}</span></label>
                <label>${{copy("Citation Note", "引用备注")}}<input name="bundle_note" placeholder="${{copy("Why these sources support the claim", "说明这些来源为什么支撑该主张")}}"></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Claim", "创建主张")}}</button>
                  <button class="btn-secondary" type="button" data-claim-form-focus-report-studio>${{copy("Need A Report First", "先去创建报告")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Selected Claim", "当前主张")}}</h3>
                  <div class="meta">
                    <span>${{escapeHtml(selectedClaim ? (selectedClaim.id || "-") : "-")}}</span>
                  <span>${{copy("bundles", "引用包")}}=${{selectedClaimBundles.length}}</span>
                  <span>${{copy("sources", "来源")}}=${{selectedClaimSources.length + selectedClaimUrls.length}}</span>
                </div>
              </div>
                <span class="chip ${{reportStatusTone(selectedClaim?.status || "")}}">${{escapeHtml(localizeWord(selectedClaim?.status || "draft"))}}</span>
              </div>
              ${{selectedClaim
                ? `
                  <div class="panel-sub">${{escapeHtml(selectedClaim.rationale || copy("No rationale captured yet.", "当前还没有记录理由。"))}}</div>
                  <div class="meta">
                    ${{selectedClaimSources.map((value) => `<span class="chip ok">${{escapeHtml(value)}}</span>`).join("") || `<span class="chip">${{copy("no direct item id", "没有直接 item id")}}</span>`}}
                    ${{selectedClaimUrls.map((value) => `<span class="chip" data-fit-text="claim-url-chip" data-fit-max-width="210" data-fit-fallback="42">${{escapeHtml(value)}}</span>`).join("")}}
                  </div>
                `
                : `<div class="empty">${{copy("Pick one claim from the right rail to inspect its binding and reuse it in the current section.", "先从右侧选中一条主张，再查看它的来源绑定并复用到当前章节。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            <div class="meta">
              <span class="mono">${{copy("claim inventory", "主张库存")}}</span>
              <span class="chip">${{copy("selected", "已选")}}=${{selectedClaim ? 1 : 0}}</span>
              <span class="chip ok">${{copy("report claims", "报告内主张")}}=${{reportClaimIds.size}}</span>
            </div>
            ${{claimRows}}
          </div>
        </div>
      `;

      root.querySelector("#claim-report-select")?.addEventListener("change", async (event) => {{
        state.selectedReportSectionId = "";
        await selectReport(String(event.target.value || "").trim());
      }});
      root.querySelector("#claim-section-select")?.addEventListener("change", (event) => {{
        state.selectedReportSectionId = String(event.target.value || "").trim();
        renderClaimsWorkspace();
        renderReportStudio();
        renderTopbarContext();
      }});
      root.querySelector("[data-claims-open-report-studio]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("[data-claim-form-focus-report-studio]")?.addEventListener("click", () => {{
        jumpToSection("section-report-studio");
      }});
      root.querySelector("#claim-composer-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const form = new FormData(event.target);
        const statement = String(form.get("statement") || "").trim();
        if (!statement) {{
          showToast(copy("Provide a claim statement before saving.", "保存前请先填写主张语句。"), "error");
          return;
        }}
        const reportId = String(state.selectedReportId || form.get("report_id") || "").trim();
        const sectionId = String(state.selectedReportSectionId || "").trim();
        const sourceItemIds = parseDelimitedInput(form.get("source_item_ids"));
        const sourceUrls = parseDelimitedInput(form.get("source_urls"));
        const rationale = String(form.get("rationale") || "").trim();
        const status = String(form.get("status") || "draft").trim().toLowerCase() || "draft";
        const confidence = Number(form.get("confidence") || 0);
        const selectedReportRecord = getReportRecord(reportId);
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          let createdClaim = await api("/api/claim-cards", {{
            method: "POST",
            payload: {{
              statement,
              rationale,
              confidence,
              status,
              brief_id: String(selectedReportRecord?.brief_id || "").trim(),
              source_item_ids: sourceItemIds,
            }},
          }});
          let createdBundleId = "";
          const bundleNote = String(form.get("bundle_note") || "").trim();
          if (sourceUrls.length || sourceItemIds.length) {{
            const bundle = await api("/api/citation-bundles", {{
              method: "POST",
              payload: {{
                claim_card_id: createdClaim.id,
                label: `${{statement.slice(0, 42)}} ${{copy("sources", "来源")}}`,
                source_item_ids: sourceItemIds,
                source_urls: sourceUrls,
                note: bundleNote,
              }},
            }});
            createdBundleId = String(bundle.id || "").trim();
            createdClaim = await api(`/api/claim-cards/${{createdClaim.id}}`, {{
              method: "PUT",
              payload: {{
                source_item_ids: sourceItemIds,
                citation_bundle_ids: uniqueValues([...(Array.isArray(createdClaim.citation_bundle_ids) ? createdClaim.citation_bundle_ids : []), createdBundleId]),
              }},
            }});
          }}
          if (reportId) {{
            await attachClaimToReport(createdClaim.id, reportId, sectionId, createdBundleId);
          }}
          state.selectedClaimId = String(createdClaim.id || "").trim();
          if (reportId) {{
            state.selectedReportId = reportId;
          }}
          if (sectionId) {{
            state.selectedReportSectionId = sectionId;
          }}
          await refreshBoard();
          showToast(
            state.language === "zh"
              ? `主张已创建：${{statement}}`
              : `Claim created: ${{statement}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Create claim", "创建主张"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-claim-select]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.selectedClaimId = String(button.dataset.claimSelect || "").trim();
          renderClaimsWorkspace();
          renderReportStudio();
          renderTopbarContext();
        }});
      }});
      root.querySelectorAll("[data-claim-attach]").forEach((button) => {{
        button.addEventListener("click", async () => {{
          const claimId = String(button.dataset.claimAttach || "").trim();
          const reportId = String(state.selectedReportId || "").trim();
          const sectionId = String(state.selectedReportSectionId || "").trim();
          if (!claimId || !reportId) {{
            return;
          }}
          button.disabled = true;
          try {{
            await attachClaimToReport(claimId, reportId, sectionId);
            state.selectedClaimId = claimId;
            await refreshBoard();
            setStageFeedback("review", {{
              kind: "completion",
              title: copy("Claim attached to the current report target", "主张已挂接到当前报告目标"),
              copy: copy(
                "The review lane now shows that this claim is attached to the selected report target.",
                "审阅阶段现在已经明确显示，这条主张已挂接到当前选中的报告目标。"
              ),
              actionHierarchy: {{
                primary: {{
                  label: copy("Open Report Studio", "打开报告工作台"),
                  attrs: {{ "data-empty-jump": "section-report-studio" }},
                }},
                secondary: [
                  {{
                    label: copy("Open Claim Composer", "打开主张装配"),
                    attrs: {{ "data-empty-jump": "section-claims" }},
                  }},
                ],
              }},
            }});
            showToast(copy("Claim attached to the current report target.", "主张已挂接到当前报告目标。"), "success");
          }} catch (error) {{
            reportError(error, copy("Attach claim", "挂接主张"));
          }} finally {{
            button.disabled = false;
          }}
        }});
      }});
      scheduleCanvasTextFit(root);
    }}

    function renderReportStudio() {{
      const root = $("report-studio-shell");
      if (!root) {{
        return;
      }}
      if (state.loading.board && !state.reports.length) {{
        root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
        return;
      }}
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
      const markdownPreview = String(state.reportMarkdown[selectedReport?.id || ""] || "").trim();
      const sectionRows = sections.length
        ? sections.map((section) => {{
            const sectionClaimIds = Array.isArray(section.claim_card_ids) ? section.claim_card_ids : [];
            const sectionClaims = sectionClaimIds
              .map((claimId) => claims.find((claim) => String(claim.id || "").trim() === String(claimId || "").trim()) || getClaimCardRecord(claimId))
              .filter(Boolean);
            return `
              <div class="card">
                <div class="card-top">
                  <div>
                    <h3 class="card-title">${{escapeHtml(section.title || section.id)}}</h3>
                    <div class="meta">
                      <span>${{copy("position", "位置")}}=${{escapeHtml(String(section.position || 0))}}</span>
                      <span>${{copy("status", "状态")}}=${{escapeHtml(localizeWord(section.status || "draft"))}}</span>
                      <span>${{copy("claims", "主张")}}=${{sectionClaimIds.length}}</span>
                    </div>
                  </div>
                  <span class="chip ${{reportStatusTone(section.status)}}">${{escapeHtml(localizeWord(section.status || "draft"))}}</span>
                </div>
                <div class="panel-sub">${{escapeHtml(section.summary || copy("No section summary yet.", "当前还没有章节摘要。"))}}</div>
                <div class="meta">
                  ${{sectionClaims.length
                    ? sectionClaims.map((claim) => `<span class="chip ok" data-fit-text="report-section-claim-chip" data-fit-max-width="198" data-fit-fallback="32">${{escapeHtml(getClaimCardLabel(claim))}}</span>`).join("")
                    : `<span class="chip hot">${{copy("no claims attached", "当前没有挂接主张")}}</span>`}}
                </div>
                <div class="actions">
                  <button class="btn-secondary" type="button" data-report-section-focus="${{escapeHtml(section.id)}}">${{copy("Focus In Claim Composer", "去主张装配")}}</button>
                </div>
              </div>
            `;
          }}).join("")
        : `<div class="empty">${{copy("No report section yet. Create one on the left, then bind claims into it.", "当前还没有章节。先在左侧创建一个章节，再把主张挂进去。")}}</div>`;

      root.innerHTML = `
        <div class="story-columns">
          <div class="stack">
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Workspace", "报告工作区")}}</h3>
                  <div class="panel-sub">${{copy("The browser stays a projection over persisted report objects. No report-only browser state is hidden here.", "浏览器仍然只是持久化报告对象的投射，这里不会偷偷生成浏览器专属状态。")}}</div>
                </div>
                <span class="chip ${{reportStatusTone(quality?.status || selectedReport?.status || "")}}">${{escapeHtml(localizeWord(quality?.status || selectedReport?.status || "draft"))}}</span>
              </div>
              <div class="field-grid" style="margin-top:12px;">
                <label>${{copy("Current Report", "当前报告")}}
                  <select id="report-studio-select">
                    <option value="">${{copy("No report selected", "未选择报告")}}</option>
                    ${{state.reports.map((report) => `<option value="${{escapeHtml(report.id)}}" ${{String(report.id || "") === String(state.selectedReportId || "") ? "selected" : ""}}>${{escapeHtml(report.title || report.id)}}</option>`).join("")}}
                  </select>
                </label>
                <label>${{copy("Export Profiles", "导出配置")}}
                  <div class="meta">
                    ${{exportProfiles.length
                      ? exportProfiles.map((profile) => `<span class="chip ok">${{escapeHtml(profile.name || profile.id)}}</span>`).join("")
                      : `<span class="chip">${{copy("none yet", "暂无")}}</span>`}}
                  </div>
                </label>
              </div>
              <div class="actions">
                <button class="btn-secondary" type="button" data-report-compose-refresh ${{selectedReport ? "" : "disabled"}}>${{copy("Refresh Composition", "刷新编排")}}</button>
                <button class="btn-secondary" type="button" data-report-preview-markdown ${{selectedReport ? "" : "disabled"}}>${{copy("Preview Markdown", "预览 Markdown")}}</button>
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}" target="_blank" rel="noreferrer">${{copy("Open JSON", "打开 JSON")}}</a>` : ""}}
                ${{selectedReport ? `<a href="/api/reports/${{selectedReport.id}}/export?output_format=markdown" target="_blank" rel="noreferrer">${{copy("Export MD", "导出 MD")}}</a>` : ""}}
              </div>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Create Report", "创建报告")}}</h3>
                  <div class="panel-sub">${{copy("Start a persisted report shell first. Claim Composer can bind judgments into it immediately after.", "先创建一个持久化报告壳，再回到主张装配里把判断挂进去。")}}</div>
                </div>
              </div>
              <form id="report-create-form" style="margin-top:12px;">
                <div class="field-grid">
                  <label>${{copy("Title", "标题")}}<input name="title" placeholder="${{copy("AI Infrastructure Brief", "AI 基建调研报告")}}"></label>
                  <label>${{copy("Audience", "受众")}}<input name="audience" placeholder="${{copy("leadership", "管理层")}}"></label>
                </div>
                <label>${{copy("Summary", "摘要")}}<textarea name="summary" rows="3" placeholder="${{copy("Describe what this report is trying to help decide.", "描述这份报告希望帮助回答什么决策问题。")}}"></textarea></label>
                <div class="toolbar">
                  <button class="btn-primary" type="submit">${{copy("Create Report", "创建报告")}}</button>
                </div>
              </form>
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Report Editor", "报告编辑")}}</h3>
                  <div class="panel-sub">${{copy("Tune report metadata and keep the assembled surface aligned with the persisted object graph.", "调整报告元数据，并让浏览器展示继续和持久化对象图保持一致。")}}</div>
                </div>
              </div>
              ${{selectedReport
                ? `
                  <form id="report-editor-form" data-report-id="${{selectedReport.id}}" style="margin-top:12px;">
                    <div class="field-grid">
                      <label>${{copy("Title", "标题")}}<input name="title" value="${{escapeHtml(selectedReport.title || "")}}"></label>
                      <label>${{copy("Audience", "受众")}}<input name="audience" value="${{escapeHtml(selectedReport.audience || "")}}"></label>
                    </div>
                    <label>${{copy("Status", "状态")}}
                      <select name="status">
                        ${{reportStatusOptions.map((status) => `<option value="${{status}}" ${{String(selectedReport.status || "draft") === status ? "selected" : ""}}>${{localizeWord(status)}}</option>`).join("")}}
                      </select>
                    </label>
                    <label>${{copy("Summary", "摘要")}}<textarea name="summary" rows="4">${{escapeHtml(selectedReport.summary || "")}}</textarea></label>
                    <div class="toolbar">
                      <button class="btn-primary" type="submit">${{copy("Save Report", "保存报告")}}</button>
                      <button class="btn-secondary" type="button" data-report-jump-claims>${{copy("Open Claim Composer", "打开主张装配")}}</button>
                    </div>
                  </form>
                `
                : `<div class="empty">${{copy("Create or select a report to edit it here.", "先创建或选中一份报告，再在这里编辑。")}}</div>`}}
            </div>

            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Section Builder", "章节构建")}}</h3>
                  <div class="panel-sub">${{copy("Create one deterministic section, then bind claims into it from Claim Composer.", "先创建一个确定性的章节，再回到主张装配里把主张挂进去。")}}</div>
                </div>
              </div>
              ${{selectedReport
                ? `
                  <form id="report-section-form" data-report-id="${{selectedReport.id}}" style="margin-top:12px;">
                    <div class="field-grid">
                      <label>${{copy("Title", "标题")}}<input name="title" placeholder="${{copy("Executive Summary", "执行摘要")}}"></label>
                      <label>${{copy("Position", "位置")}}<input name="position" type="number" min="0" step="1" value="${{escapeHtml(String(sections.length + 1))}}"></label>
                    </div>
                    <label>${{copy("Section Summary", "章节摘要")}}<textarea name="summary" rows="3" placeholder="${{copy("What should this section conclude or frame?", "这个章节主要要承接什么判断或框架？")}}"></textarea></label>
                    <div class="toolbar">
                      <button class="btn-primary" type="submit">${{copy("Create Section", "创建章节")}}</button>
                    </div>
                  </form>
                `
                : `<div class="empty">${{copy("No report selected, so there is nowhere to attach a section yet.", "当前没有选中报告，因此还没有章节可挂接。")}}</div>`}}
            </div>
          </div>

          <div class="stack">
            ${{selectedReport ? renderReportQualityBlock(quality) : `<div class="empty">${{copy("Select one report to inspect guardrails, sections, and export preview.", "选中一份报告后，这里会显示质量门禁、章节结构和导出预览。")}}</div>`}}
            <div class="stack">
              <div class="meta">
                <span class="mono">${{copy("report sections", "报告章节")}}</span>
                <span class="chip ok">${{copy("count", "数量")}}=${{sections.length}}</span>
                <span class="chip">${{copy("claims", "主张")}}=${{claims.length}}</span>
              </div>
              ${{sectionRows}}
            </div>
            <div class="card">
              <div class="card-top">
                <div>
                  <h3 class="card-title">${{copy("Markdown Preview", "Markdown 预览")}}</h3>
                  <div class="panel-sub">${{copy("Use the same Reader-backed export surface the CLI and API already share.", "直接复用 CLI 和 API 已共享的 Reader-backed 导出面。")}}</div>
                </div>
              </div>
              ${{markdownPreview
                ? `<pre class="text-block">${{escapeHtml(markdownPreview)}}</pre>`
                : `<div class="empty">${{copy("No Markdown preview cached yet. Click Preview Markdown above.", "当前还没有缓存的 Markdown 预览。点击上方“预览 Markdown”即可。")}}</div>`}}
            </div>
          </div>
        </div>
      `;

      root.querySelector("#report-studio-select")?.addEventListener("change", async (event) => {{
        await selectReport(String(event.target.value || "").trim());
      }});
      root.querySelector("[data-report-compose-refresh]")?.addEventListener("click", async (event) => {{
        if (!selectedReport) {{
          return;
        }}
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await loadReportComposition(selectedReport.id);
          showToast(copy("Report composition refreshed.", "报告编排已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Refresh report composition", "刷新报告编排"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("[data-report-preview-markdown]")?.addEventListener("click", async (event) => {{
        if (!selectedReport) {{
          return;
        }}
        const button = event.currentTarget;
        button.disabled = true;
        try {{
          await previewReportMarkdown(selectedReport.id);
          showToast(copy("Markdown preview refreshed.", "Markdown 预览已刷新。"), "success");
        }} catch (error) {{
          reportError(error, copy("Preview report markdown", "预览报告 Markdown"));
        }} finally {{
          button.disabled = false;
        }}
      }});
      root.querySelector("#report-create-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const form = new FormData(event.target);
        const title = String(form.get("title") || "").trim();
        if (!title) {{
          setStageFeedback("review", {{
            kind: "blocked",
            title: copy("Report still needs a title", "报告仍缺少标题"),
            copy: copy("Add a title before this report can become a persisted review object.", "补上标题后，这份报告才能成为持久化的审阅对象。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
            }},
          }});
          showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
          return;
        }}
        const payload = {{
          title,
          audience: String(form.get("audience") || "").trim(),
          summary: String(form.get("summary") || "").trim(),
        }};
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/reports", {{
            method: "POST",
            payload,
          }});
          state.selectedReportId = String(created.id || "").trim();
          state.selectedReportSectionId = "";
          await refreshBoard();
          setStageFeedback("review", {{
            kind: "completion",
            title: state.language === "zh" ? `报告已创建：${{title}}` : `Report created: ${{title}}`,
            copy: copy(
              "The review lane now owns a persisted report object. Add sections or attach claims next.",
              "审阅阶段现在已经拥有一份持久化报告对象；下一步可以继续创建章节，或挂接主张。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
              secondary: [
                {{
                  label: copy("Open Claim Composer", "打开主张装配"),
                  attrs: {{ "data-empty-jump": "section-claims" }},
                }},
              ],
            }},
          }});
          showToast(
            state.language === "zh"
              ? `报告已创建：${{title}}`
              : `Report created: ${{title}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Create report", "创建报告"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("#report-editor-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        if (!selectedReport) {{
          return;
        }}
        const form = new FormData(event.target);
        const payload = {{
          title: String(form.get("title") || "").trim(),
          audience: String(form.get("audience") || "").trim(),
          status: String(form.get("status") || "draft").trim().toLowerCase() || "draft",
          summary: String(form.get("summary") || "").trim(),
        }};
        if (!payload.title) {{
          setStageFeedback("review", {{
            kind: "blocked",
            title: copy("Report save is blocked by a missing title", "报告保存被缺失标题阻塞"),
            copy: copy("Keep the report title populated before saving changes in the review lane.", "请先保留报告标题，再在审阅阶段保存修改。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
            }},
          }});
          showToast(copy("Provide a report title before saving.", "保存前请先填写报告标题。"), "error");
          return;
        }}
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          await api(`/api/reports/${{selectedReport.id}}`, {{
            method: "PUT",
            payload,
          }});
          await refreshBoard();
          setStageFeedback("review", {{
            kind: "completion",
            title: copy("Report saved", "报告已保存"),
            copy: copy(
              "The persisted report object is updated in place on the review lane.",
              "这份持久化报告对象已经在审阅阶段原位更新。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
            }},
          }});
          showToast(copy("Report saved.", "报告已保存。"), "success");
        }} catch (error) {{
          reportError(error, copy("Save report", "保存报告"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelector("[data-report-jump-claims]")?.addEventListener("click", () => {{
        jumpToSection("section-claims");
      }});
      root.querySelector("#report-section-form")?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        if (!selectedReport) {{
          return;
        }}
        const form = new FormData(event.target);
        const title = String(form.get("title") || "").trim();
        if (!title) {{
          setStageFeedback("review", {{
            kind: "blocked",
            title: copy("Report section still needs a title", "报告章节仍缺少标题"),
            copy: copy("Add a section title before this report structure can advance.", "补上章节标题后，这份报告结构才能继续推进。"),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Report Studio", "打开报告工作台"),
                attrs: {{ "data-empty-jump": "section-report-studio" }},
              }},
            }},
          }});
          showToast(copy("Provide a section title before saving.", "保存前请先填写章节标题。"), "error");
          return;
        }}
        const payload = {{
          report_id: selectedReport.id,
          title,
          position: Number(form.get("position") || sections.length + 1),
          summary: String(form.get("summary") || "").trim(),
        }};
        const submitButton = event.target.querySelector("button[type='submit']");
        if (submitButton) {{
          submitButton.disabled = true;
        }}
        try {{
          const created = await api("/api/report-sections", {{
            method: "POST",
            payload,
          }});
          await api(`/api/reports/${{selectedReport.id}}`, {{
            method: "PUT",
            payload: {{
              section_ids: uniqueValues([...(Array.isArray(selectedReport.section_ids) ? selectedReport.section_ids : []), created.id]),
            }},
          }});
          state.selectedReportSectionId = String(created.id || "").trim();
          await refreshBoard();
          setStageFeedback("review", {{
            kind: "completion",
            title: copy("Report section created", "报告章节已创建"),
            copy: copy(
              "The report now exposes a persisted section that can receive claims from the review lane.",
              "这份报告现在已经拥有一个持久化章节，可以继续从审阅阶段接收主张。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Claim Composer", "打开主张装配"),
                attrs: {{ "data-empty-jump": "section-claims" }},
              }},
              secondary: [
                {{
                  label: copy("Open Report Studio", "打开报告工作台"),
                  attrs: {{ "data-empty-jump": "section-report-studio" }},
                }},
              ],
            }},
          }});
          showToast(copy("Report section created.", "报告章节已创建。"), "success");
        }} catch (error) {{
          reportError(error, copy("Create report section", "创建报告章节"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
      }});
      root.querySelectorAll("[data-report-section-focus]").forEach((button) => {{
        button.addEventListener("click", () => {{
          state.selectedReportSectionId = String(button.dataset.reportSectionFocus || "").trim();
          renderClaimsWorkspace();
          renderReportStudio();
          renderTopbarContext();
          jumpToSection("section-claims");
        }});
      }});
      scheduleCanvasTextFit(root);
    }}

    function renderBoardShell() {{
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
      renderClaimsWorkspace();
      renderReportStudio();
    }}

    async function ensureOverview({{ force = false }} = {{}}) {{
      await runHydrationTask("overview", async () => {{
        state.overview = await api("/api/overview");
        return state.overview;
      }}, {{ force }});
    }}

    async function ensureMonitorData({{ force = false }} = {{}}) {{
      await runHydrationTask("monitor", async () => {{
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
        if (state.watches.length) {{
          state.selectedWatchId = selectExistingOrFirst(state.watches, state.selectedWatchId);
        }} else {{
          state.selectedWatchId = "";
          setContextRouteName("", "");
        }}
        setContextRouteFromWatch();
        return watches;
      }}, {{ force }});
    }}

    async function ensureReviewData({{ force = false }} = {{}}) {{
      await runHydrationTask("review", async () => {{
        const [triage, triageStats, stories] = await Promise.all([
          api("/api/triage?limit=12&include_closed=true"),
          api("/api/triage/stats"),
          api("/api/stories?limit=6&min_items=0"),
        ]);
        state.triage = triage;
        state.triageStats = triageStats;
        state.stories = stories;
        if (state.stories.length) {{
          const selectedStoryId = selectExistingOrFirst(state.stories, state.selectedStoryId);
          state.selectedStoryId = selectedStoryId;
          if (!state.storyDetails[selectedStoryId]) {{
            const seeded = state.stories.find((story) => String(story.id || "").trim() === selectedStoryId);
            if (seeded) {{
              state.storyDetails[selectedStoryId] = seeded;
            }}
          }}
        }} else {{
          state.selectedStoryId = "";
        }}
        state.selectedTriageId = selectExistingOrFirst(state.triage, state.selectedTriageId);
        return triage;
      }}, {{ force }});
    }}

    async function ensureReportFamilyData({{ force = false }} = {{}}) {{
      await runHydrationTask("report-family", async () => {{
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
      }}, {{ force }});
    }}

    async function ensureDeliveryData({{ force = false }} = {{}}) {{
      await runHydrationTask("delivery", async () => {{
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
      }}, {{ force }});
    }}

    async function ensureSelectedWatchDetail({{ force = false }} = {{}}) {{
      const selectedWatchId = selectExistingOrFirst(state.watches, state.selectedWatchId);
      if (!selectedWatchId) {{
        state.selectedWatchId = "";
        return null;
      }}
      state.selectedWatchId = selectedWatchId;
      if (!force && state.watchDetails[selectedWatchId]) {{
        return state.watchDetails[selectedWatchId];
      }}
      return loadWatch(selectedWatchId, {{ force }});
    }}

    async function ensureSelectedStoryDetail({{ force = false }} = {{}}) {{
      const selectedStoryId = selectExistingOrFirst(state.stories, state.selectedStoryId);
      if (!selectedStoryId) {{
        state.selectedStoryId = "";
        return null;
      }}
      state.selectedStoryId = selectedStoryId;
      if (!force && state.storyDetails[selectedStoryId] && state.storyGraph[selectedStoryId]) {{
        return state.storyDetails[selectedStoryId];
      }}
      await loadStory(selectedStoryId, {{ syncUrl: false, force }});
      return state.storyDetails[selectedStoryId] || null;
    }}

    async function ensureSelectedReportComposition({{ force = false }} = {{}}) {{
      syncReportSelectionState();
      if (!state.selectedReportId) {{
        return null;
      }}
      if (!force && state.reportCompositions[state.selectedReportId]) {{
        return state.reportCompositions[state.selectedReportId];
      }}
      await loadReportComposition(state.selectedReportId, {{ render: false, force }});
      return state.reportCompositions[state.selectedReportId] || null;
    }}

    async function ensureDigestData({{ force = false }} = {{}}) {{
      await runHydrationTask("digest", async () => {{
        return loadDigestConsole({{ render: false, preserveDraft: true, force }});
      }}, {{ force }});
    }}

    async function ensureAiSurfacePrecheck(surfaceId, {{ force = false }} = {{}}) {{
      const normalizedSurfaceId = String(surfaceId || "").trim();
      if (!normalizedSurfaceId) {{
        return null;
      }}
      const cacheKey = `ai-precheck:${{normalizedSurfaceId}}`;
      if (!force && state.aiSurfacePrechecks[normalizedSurfaceId]) {{
        markHydrationLoaded(cacheKey);
        return state.aiSurfacePrechecks[normalizedSurfaceId];
      }}
      await runHydrationTask(cacheKey, async () => {{
        state.aiSurfacePrechecks[normalizedSurfaceId] = await api(`/api/ai/surfaces/${{normalizedSurfaceId}}/precheck?mode=assist`);
        return state.aiSurfacePrechecks[normalizedSurfaceId];
      }}, {{ force }});
      return state.aiSurfacePrechecks[normalizedSurfaceId] || null;
    }}

    async function hydrateBoardForSection(sectionId, {{ force = false }} = {{}}) {{
      const normalizedSectionId = normalizeSectionId(sectionId || state.activeSectionId);
      state.loading.board = true;
      renderBoardShell();
      try {{
        await ensureOverview({{ force }});
        if (normalizedSectionId === "section-board") {{
          await ensureMonitorData({{ force }});
          await ensureAiSurfacePrecheck("mission_suggest");
        }} else if (normalizedSectionId === "section-cockpit") {{
          await ensureMonitorData({{ force }});
          await ensureSelectedWatchDetail({{ force }});
          await ensureAiSurfacePrecheck("mission_suggest");
        }} else if (normalizedSectionId === "section-triage") {{
          await ensureReviewData({{ force }});
          await ensureAiSurfacePrecheck("triage_assist");
        }} else if (normalizedSectionId === "section-story") {{
          await ensureReviewData({{ force }});
          await ensureSelectedStoryDetail({{ force }});
          await ensureAiSurfacePrecheck("claim_draft");
        }} else if (normalizedSectionId === "section-claims" || normalizedSectionId === "section-report-studio") {{
          await ensureReviewData({{ force }});
          await ensureReportFamilyData({{ force }});
          await ensureSelectedReportComposition({{ force }});
        }} else if (normalizedSectionId === "section-ops") {{
          await ensureDeliveryData({{ force }});
          await ensureDigestData({{ force }});
        }}
      }} finally {{
        state.loading.board = false;
      }}
      renderBoardShell();
      renderCreateWatchDeck();
      applyDefaultSavedViewOnBoot();
    }}

    async function refreshBoard() {{
      state.loading.board = true;
      renderBoardShell();
      try {{
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
        if (!state.digestProfileDraft) {{
          state.digestProfileDraft = normalizeDigestProfileDraft(digestConsole?.profile?.profile || defaultDigestProfileDraft());
        }}
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
        state.aiSurfacePrechecks = {{
          mission_suggest: missionSuggestPrecheck,
          triage_assist: triageAssistPrecheck,
          claim_draft: claimDraftPrecheck,
        }};
        if (state.watches.length) {{
          const selectedWatch = state.watches.some((watch) => watch.id === state.selectedWatchId)
            ? state.selectedWatchId
            : state.watches[0].id;
          state.selectedWatchId = selectedWatch;
          state.watchDetails[selectedWatch] = await api(`/api/watches/${{selectedWatch}}`);
        }} else {{
          state.selectedWatchId = "";
          setContextRouteName("", "");
        }}
        setContextRouteFromWatch();
        if (state.stories.length) {{
          const selected = state.stories.some((story) => story.id === state.selectedStoryId)
            ? state.selectedStoryId
            : state.stories[0].id;
          state.selectedStoryId = selected;
          if (!state.storyDetails[selected]) {{
            const seeded = state.stories.find((story) => story.id === selected);
            if (seeded) {{
              state.storyDetails[selected] = seeded;
            }}
          }}
          if (!state.storyGraph[selected]) {{
            state.storyGraph[selected] = await api(`/api/stories/${{selected}}/graph`);
          }}
        }} else {{
          state.selectedStoryId = "";
        }}
        if (state.triage.length && !state.triage.some((item) => item.id === state.selectedTriageId)) {{
          state.selectedTriageId = state.triage[0].id;
        }}
        if (!state.triage.length) {{
          state.selectedTriageId = "";
        }}
        syncReportSelectionState();
        syncDeliverySelectionState();
        if (state.selectedReportId) {{
          state.reportCompositions[state.selectedReportId] = await api(`/api/reports/${{state.selectedReportId}}/compose`);
        }}
        const [missionSuggest, triageAssist, claimDraft] = await Promise.all([
          state.selectedWatchId
            ? api(`/api/watches/${{state.selectedWatchId}}/ai/mission-suggest?mode=assist`)
            : Promise.resolve(null),
          state.selectedTriageId
            ? api(`/api/triage/${{state.selectedTriageId}}/ai/assist?mode=assist&limit=5`)
            : Promise.resolve(null),
          state.selectedStoryId
            ? api(`/api/stories/${{state.selectedStoryId}}/ai/claim-draft?mode=assist`)
            : Promise.resolve(null),
        ]);
        state.aiSurfaceProjections = {{
          mission_suggest: missionSuggest,
          triage_assist: triageAssist,
          claim_draft: claimDraft,
        }};
        const selectedDelivery = getSelectedDeliverySubscription();
        if (selectedDelivery && String(selectedDelivery.subject_kind || "").trim().toLowerCase() === "report") {{
          try {{
            await loadDeliveryPackageAudit(String(selectedDelivery.id || "").trim(), {{
              profileId: String(state.deliveryPackageProfileIds[selectedDelivery.id] || "").trim(),
              render: false,
            }});
          }} catch (error) {{
            state.deliveryPackageErrors[String(selectedDelivery.id || "").trim()] = error.message;
          }}
        }}
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
      }} finally {{
        state.loading.board = false;
      }}
      renderBoardShell();
      renderCreateWatchDeck();
      applyDefaultSavedViewOnBoot();
    }}

    bindCreateWatchDeck();
    bindRouteDeck();
    bindStoryDeck();
    bindContextObjectRail();
    bindHeroStageMotion();
    bindSectionJumps();
    bindSectionTracking();
    bindContextLens();
    bindLanguageSwitch();
    bindCommandPalette();
    bindResponsiveInteractionContract();
    applyLanguageChrome();
    renderActionHistory();
    renderCommandPalette();
    $("palette-open")?.addEventListener("click", () => {{
      if (state.commandPalette.open) {{
        closeCommandPalette();
      }} else {{
        openCommandPalette();
      }}
    }});
    $("context-reset")?.addEventListener("click", () => {{
      resetWorkspaceContext();
    }});

    $("refresh-all").addEventListener("click", async () => {{
      const button = $("refresh-all");
      button.disabled = true;
      try {{
        await refreshBoard();
        showToast(copy("Console refreshed", "控制台已刷新"), "success");
      }} catch (error) {{
        reportError(error, copy("Refresh console", "刷新控制台"));
      }} finally {{
        button.disabled = false;
      }}
    }});
    $("run-due").addEventListener("click", async () => {{
      const button = $("run-due");
      button.disabled = true;
      try {{
        await api("/api/watches/run-due", {{ method: "POST", payload: {{ limit: 0 }} }});
        await refreshBoard();
        showToast(copy("Due missions dispatched", "到点任务已触发执行"), "success");
      }} catch (error) {{
        reportError(error, copy("Run due missions", "执行到点任务"));
      }} finally {{
        button.disabled = false;
      }}
    }});

    $("create-watch-form").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const formElement = event.target;
      const submitButton = formElement.querySelector("button[type='submit']");
      const draft = collectCreateWatchDraft(formElement);
      state.createWatchDraft = draft;
      persistCreateWatchDraft();
      renderCreateWatchDeck();
      if (!(draft.name.trim() && draft.query.trim())) {{
        const missingField = draft.name.trim() ? "query" : "name";
        setStageFeedback("start", {{
          kind: "blocked",
          title: String(state.createWatchEditingId || "").trim()
            ? copy("Mission edit is still blocked by required fields", "任务修改仍被必填字段阻塞")
            : copy("Mission draft is still blocked by required fields", "任务草稿仍被必填字段阻塞"),
          copy: draft.name.trim()
            ? copy("Add the query before this draft can move into monitoring.", "补上查询词后，这份草稿才能进入监测阶段。")
            : copy("Add a mission name before this draft can move into monitoring.", "补上任务名称后，这份草稿才能进入监测阶段。"),
          actionHierarchy: {{
            primary: {{
              label: copy("Complete Mission Draft", "继续补全任务草稿"),
              attrs: {{ "data-empty-focus": "mission", "data-empty-field": missingField }},
            }},
            secondary: [
              {{
                label: copy("Open Mission Board", "打开任务列表"),
                attrs: {{ "data-empty-jump": "section-board" }},
              }},
            ],
          }},
        }});
        showToast(
          String(state.createWatchEditingId || "").trim()
            ? copy("Provide both Name and Query before saving changes.", "保存修改前请同时填写名称和查询词。")
            : copy("Provide both Name and Query before creating a watch.", "创建任务前请同时填写名称和查询词。"),
          "error",
        );
        focusCreateWatchDeck(draft.name.trim() ? "query" : "name");
        return;
      }}
      const alertRules = buildAlertRules({{
        route: draft.route.trim(),
        keyword: draft.keyword.trim(),
        domain: draft.domain.trim(),
        minScore: Number(draft.min_score || 0),
        minConfidence: Number(draft.min_confidence || 0),
      }});
      const payload = {{
        name: draft.name.trim(),
        query: draft.query.trim(),
        schedule: draft.schedule.trim() || "manual",
        platforms: draft.platform.trim() ? [draft.platform.trim()] : null,
        alert_rules: alertRules.length ? alertRules : null,
      }};
      const editingId = String(state.createWatchEditingId || "").trim();
      if (submitButton) {{
        submitButton.disabled = true;
      }}
      if (editingId) {{
        try {{
          const updated = await api(`/api/watches/${{editingId}}`, {{
            method: "PUT",
            payload,
          }});
          state.selectedWatchId = updated.id || editingId;
          state.watchDetails[state.selectedWatchId] = updated;
          state.createWatchAdvancedOpen = null;
          setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
          formElement.reset();
          pushActionEntry({{
            kind: copy("mission update", "任务修改"),
            label: state.language === "zh" ? `已更新任务：${{payload.name}}` : `Updated ${{payload.name}}`,
            detail: state.language === "zh" ? `任务 ID：${{editingId}}` : `Mission id: ${{editingId}}`,
          }});
          await refreshBoard();
          setStageFeedback("start", {{
            kind: "completion",
            title: state.language === "zh" ? `任务已更新：${{payload.name}}` : `Mission updated: ${{payload.name}}`,
            copy: copy(
              "The updated mission now lives in the monitoring lane. Inspect its board posture or open Cockpit to verify the next run.",
              "更新后的任务已经进入监测阶段；下一步可以查看任务列表姿态，或直接打开驾驶舱确认下一次执行。"
            ),
            actionHierarchy: {{
              primary: {{
                label: copy("Open Mission Board", "打开任务列表"),
                attrs: {{ "data-empty-jump": "section-board" }},
              }},
              secondary: [
                {{
                  label: copy("Open Cockpit", "打开任务详情"),
                  attrs: {{ "data-empty-jump": "section-cockpit" }},
                }},
              ],
            }},
          }});
          showToast(
            state.language === "zh" ? `任务已更新：${{payload.name}}` : `Mission updated: ${{payload.name}}`,
            "success",
          );
        }} catch (error) {{
          reportError(error, copy("Update watch", "更新任务"));
        }} finally {{
          if (submitButton) {{
            submitButton.disabled = false;
          }}
        }}
        return;
      }}
      const optimisticId = `draft-${{Date.now()}}`;
      const optimisticWatch = {{
        id: optimisticId,
        name: payload.name,
        query: payload.query,
        enabled: true,
        platforms: payload.platforms || [],
        sites: draft.domain.trim() ? [draft.domain.trim()] : [],
        schedule: payload.schedule,
        schedule_label: payload.schedule,
        is_due: false,
        next_run_at: "",
        alert_rule_count: Array.isArray(payload.alert_rules) ? payload.alert_rules.length : 0,
        alert_rules: payload.alert_rules || [],
        last_run_at: "",
        last_run_status: "pending",
      }};
      state.watches = [optimisticWatch, ...state.watches];
      state.selectedWatchId = optimisticId;
      state.watchDetails[optimisticId] = optimisticWatch;
      renderWatches();
      renderWatchDetail();
      try {{
        const created = await api("/api/watches", {{ method: "POST", payload }});
        state.createWatchAdvancedOpen = null;
        setCreateWatchDraft(defaultCreateWatchDraft(), "", "");
        formElement.reset();
        pushActionEntry({{
          kind: copy("mission create", "任务创建"),
          label: state.language === "zh" ? `已创建任务：${{payload.name}}` : `Created ${{payload.name}}`,
          detail: copy("The new mission can be removed from the recent action log if this was a false start.", "如果这是误创建，可以在最近操作中直接删除。"),
          undoLabel: copy("Delete mission", "删除任务"),
          undo: async () => {{
            await api(`/api/watches/${{created.id}}`, {{ method: "DELETE" }});
            await refreshBoard();
            showToast(
              state.language === "zh" ? `已删除任务：${{created.name || created.id}}` : `Mission deleted: ${{created.name || created.id}}`,
              "success",
            );
          }},
        }});
        await refreshBoard();
        setStageFeedback("start", {{
          kind: "completion",
          title: state.language === "zh" ? `任务已创建：${{payload.name}}` : `Watch created: ${{payload.name}}`,
          copy: copy(
            "The new mission now owns a slot in monitoring. Select it on the board or open Cockpit to inspect the first run.",
            "新任务现在已经进入监测阶段；下一步可以在任务列表中选中它，或直接打开驾驶舱查看第一次执行。"
          ),
          actionHierarchy: {{
            primary: {{
              label: copy("Open Mission Board", "打开任务列表"),
              attrs: {{ "data-empty-jump": "section-board" }},
            }},
            secondary: [
              {{
                label: copy("Open Cockpit", "打开任务详情"),
                attrs: {{ "data-empty-jump": "section-cockpit" }},
              }},
            ],
          }},
        }});
        showToast(
          state.language === "zh" ? `任务已创建：${{payload.name}}` : `Watch created: ${{payload.name}}`,
          "success",
        );
      }} catch (error) {{
        state.watches = state.watches.filter((watch) => watch.id !== optimisticId);
        delete state.watchDetails[optimisticId];
        if (state.selectedWatchId === optimisticId) {{
          state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
        }}
        renderWatches();
        renderWatchDetail();
        reportError(error, copy("Create watch", "创建任务"));
      }} finally {{
        if (submitButton) {{
          submitButton.disabled = false;
        }}
      }}
    }});

    state.consoleOverflowEvidence = defaultConsoleOverflowEvidence();
    window.getConsoleOverflowEvidence = getConsoleOverflowEvidence;

    hydrateBoardForSection(state.activeSectionId).catch((error) => {{
      reportError(error, copy("Console boot failed", "控制台启动失败"));
    }});

    document.addEventListener("keydown", (event) => {{
      const target = event.target;
      const tagName = target && target.tagName ? String(target.tagName).toLowerCase() : "";
      const key = String(event.key || "").toLowerCase();
      if ((event.metaKey || event.ctrlKey) && key === "k") {{
        event.preventDefault();
        if (state.commandPalette.open) {{
          closeCommandPalette();
        }} else {{
          openCommandPalette();
        }}
        return;
      }}
      if (key === "escape" && state.commandPalette.open) {{
        event.preventDefault();
        closeCommandPalette();
        return;
      }}
      if (key === "escape" && state.contextLensOpen) {{
        event.preventDefault();
        setContextLensOpen(false);
        return;
      }}
      if (state.commandPalette.open) {{
        return;
      }}
      if (event.metaKey || event.ctrlKey || event.altKey) {{
        return;
      }}
      if (["input", "textarea", "select", "button"].includes(tagName)) {{
        return;
      }}
      if (key === "/") {{
        event.preventDefault();
        focusCreateWatchDeck((state.createWatchDraft && state.createWatchDraft.name.trim()) ? "query" : "name");
        return;
      }}
      if (["1", "2", "3", "4"].includes(key)) {{
        const preset = createWatchPresets[Number(key) - 1];
        if (preset) {{
          event.preventDefault();
          state.createWatchAdvancedOpen = draftHasAdvancedSignal(preset.values);
          setCreateWatchDraft(preset.values, preset.id, "");
          showToast(
            state.language === "zh"
              ? `${{preset.zhLabel || preset.label}} 已载入任务草稿`
              : `${{preset.label}} loaded into the mission deck`,
            "success",
          );
        }}
        return;
      }}
      const visibleItems = getVisibleTriageItems();
      if (!visibleItems.length) {{
        return;
      }}
      const selectedId = state.selectedTriageId || visibleItems[0].id;
      const hasBatchSelection = state.selectedTriageIds.length > 0;
      if (key === "j") {{
        event.preventDefault();
        moveTriageSelection(1);
      }} else if (key === "k") {{
        event.preventDefault();
        moveTriageSelection(-1);
      }} else if (key === "v") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("verified") : runTriageStateUpdate(selectedId, "verified")).catch((error) => reportError(error, copy("Verify triage item", "核验分诊条目")));
      }} else if (key === "t") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("triaged") : runTriageStateUpdate(selectedId, "triaged")).catch((error) => reportError(error, copy("Triage item", "分诊条目")));
      }} else if (key === "e") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("escalated") : runTriageStateUpdate(selectedId, "escalated")).catch((error) => reportError(error, copy("Escalate triage item", "升级分诊条目")));
      }} else if (key === "i") {{
        event.preventDefault();
        (hasBatchSelection ? runTriageBatchStateUpdate("ignored") : runTriageStateUpdate(selectedId, "ignored")).catch((error) => reportError(error, copy("Ignore triage item", "忽略分诊条目")));
      }} else if (key === "s") {{
        event.preventDefault();
        (hasBatchSelection ? createStoryFromTriageItems(state.selectedTriageIds) : createStoryFromTriageItems([selectedId])).catch((error) => reportError(error, copy("Create story from triage", "从分诊生成故事")));
      }} else if (key === "d") {{
        event.preventDefault();
        runTriageExplain(selectedId).catch((error) => reportError(error, copy("Explain duplicates", "查看重复解释")));
      }} else if (key === "n") {{
        event.preventDefault();
        focusTriageNoteComposer(selectedId);
      }}
    }});
  """
