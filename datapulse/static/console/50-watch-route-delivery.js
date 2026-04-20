// Split group 2e: mission board, route management, delivery workspace, and ops/status surfaces.
// Depends on prior fragments and 00-common.js.

function buildMissionGuidanceSurface(preview, suggestions = null) {
  const draft = preview?.draft || defaultCreateWatchDraft();
  const warningItems = Array.isArray(suggestions?.warnings) ? suggestions.warnings : [];
  const reasons = [];
  const cadenceReason = [suggestions?.schedule_reason, suggestions?.platform_reason].filter(Boolean).join(" ");
  if (cadenceReason) {
    reasons.push({
      title: copy("Cadence and platform were derived from current repo state", "频率与平台建议来自当前仓库状态"),
      copy: cadenceReason,
      tone: "ok",
      facts: [
        { label: copy("Cadence", "频率"), value: suggestions?.recommended_schedule || preview?.scheduleLabel || "manual" },
        { label: copy("Platform", "平台"), value: suggestions?.recommended_platform || draft.platform || copy("unset", "未设置") },
      ],
      owner: copy("mission suggestions", "任务建议"),
    });
  }
  const routeReason = [suggestions?.route_reason, suggestions?.keyword_reason, suggestions?.domain_reason].filter(Boolean).join(" ");
  if (routeReason) {
    reasons.push({
      title: copy("Route and scope guidance stays tied to current delivery and duplicate pressure", "路由与范围建议继续绑定交付和重复压力"),
      copy: routeReason,
      tone: normalizeRouteName(suggestions?.recommended_route || draft.route) ? "ok" : "",
      facts: [
        { label: copy("Route", "路由"), value: suggestions?.recommended_route || draft.route || copy("unset", "未设置") },
        { label: copy("Scope", "范围"), value: preview?.filtersLabel || copy("broad", "宽范围") },
      ],
      owner: copy("mission suggestions", "任务建议"),
    });
  }
  if (warningItems.length) {
    reasons.push({
      title: copy("Current draft already has conflict or delivery pressure to watch", "当前草稿已经暴露出冲突或交付压力"),
      copy: warningItems.slice(0, 2).join(" "),
      tone: "hot",
      facts: [
        { label: copy("Warnings", "提醒"), value: String(warningItems.length) },
        { label: copy("Readiness", "就绪度"), value: `${preview?.readiness || 0}%` },
      ],
      owner: copy("mission suggestions", "任务建议"),
    });
  }
  if (!reasons.length) {
    reasons.push({
      title: copy("Current draft is still the primary mission fact source", "当前草稿本身仍是首要任务事实来源"),
      copy: preview?.summary || copy("Mission guidance stays lightweight until the draft accumulates enough scope or delivery context.", "在草稿积累到足够的范围或交付上下文之前，任务指引保持轻量。"),
      facts: [
        { label: copy("Name", "名称"), value: clampLabel(draft.name || copy("unset", "未设置"), 24) },
        { label: copy("Query", "查询词"), value: clampLabel(draft.query || copy("unset", "未设置"), 24) },
      ],
      owner: copy("mission brief", "任务概览"),
    });
  }

  const nextSteps = !preview?.requiredReady
    ? [{
        title: copy("Complete Name and Query before expecting mission creation", "先补齐名称与查询词，再期待任务创建"),
        copy: copy("Mission Intake only needs the required fields first. Extra scope and delivery controls can remain empty until the draft is valid.", "任务录入区只要求先补齐必填字段。额外的范围和交付控制可以在草稿有效之后再决定。"),
        tone: "hot",
        facts: [
          { label: copy("Missing", "缺失"), value: !String(draft.name || "").trim() ? copy("name", "名称") : copy("query", "查询词") },
        ],
        owner: copy("mission intake", "任务录入"),
      }]
    : [{
        title: preview?.alertArmed
          ? copy("Create or update the mission, then verify delivery posture in board or cockpit", "创建或更新任务后，再去任务列表或驾驶舱确认交付姿态")
          : copy("Create the mission first and add route wiring only when downstream delivery is required", "先创建任务；只有确实需要下游交付时再补路由"),
        copy: preview?.alertArmed
          ? copy("This draft already includes alert gates. After saving, the next hop is usually Mission Board or Cockpit rather than more intake edits.", "当前草稿已经包含告警门槛；保存后下一步通常是进入任务列表或驾驶舱，而不是继续改录入。")
          : copy("The draft is valid already. Keep the mission broad, run it once, and only add more delivery wiring if the resulting signal is worth downstream notification.", "当前草稿已经有效。先保持任务宽一些并执行一次，只有当结果值得通知下游时再补更多交付设置。"),
        tone: "ok",
        facts: [
          { label: copy("Ready", "就绪"), value: `${preview?.readiness || 0}%` },
          { label: copy("Alert", "告警"), value: preview?.alertArmed ? copy("armed", "已启用") : copy("passive", "未启用") },
        ],
        owner: copy("mission intake", "任务录入"),
      }];

  const sources = [
    {
      title: copy("Runtime suggestion facts stay owned by the mission suggestion payload", "运行时建议事实继续归任务建议载荷所有"),
      copy: copy("Cadence, route, duplicate pressure, and similar-mission warnings are projected from current watches and stories rather than invented by browser-only heuristics.", "频率、路由、重复压力和相似任务提醒都来自当前任务与故事投影，而不是浏览器本地臆测。"),
      owner: copy("runtime facts", "运行时事实"),
    },
    {
      title: copy("Field semantics still stay in the parameter guide", "字段语义仍然归参数说明文档所有"),
      copy: copy("Alert Route, domain, thresholds, digest defaults, and prompt-pack provenance rules remain documented in docs/datapulse_console_parameter_guide.md.", "告警路由、域名、阈值、digest 默认值和 prompt-pack 来源规则继续记录在 docs/datapulse_console_parameter_guide.md。"),
      owner: copy("static docs", "静态文档"),
    },
  ];

  return renderOperatorGuidanceSurface({
    surfaceId: "mission-guidance-surface",
    lane: "mission",
    title: copy("Mission Guidance Contract", "任务指引契约"),
    summary: suggestions?.summary || copy("Keep mission setup reasons and next-step wording persistent so operators do not have to infer intent from one-off hints or toast feedback.", "把任务设置的原因与下一步文案固定下来，避免操作者只能从零散提示或 toast 里猜测意图。"),
    reasons,
    nextSteps,
    sources,
    actionHierarchy: {
      primary: preview?.requiredReady
        ? makeSurfaceAction(copy("Open Mission Board", "打开任务列表"), { "data-empty-jump": "section-board" })
        : makeSurfaceAction(copy("Focus Mission Draft", "聚焦任务草稿"), { "data-empty-focus": "mission", "data-empty-field": !String(draft.name || "").trim() ? "name" : "query" }),
      secondary: [
        makeSurfaceAction(copy("Focus Alert Route", "聚焦告警路由"), { "data-empty-focus": "mission", "data-empty-field": "route" }),
        makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), { "data-empty-jump": "section-ops" }),
      ],
    },
  });
}

function buildCockpitGuidanceSurface(watch, { recentRuns = [], recentResults = [], recentAlerts = [], retryAdvice = null, deliveryStats = {} } = {}) {
  const reasons = [];
  if (retryAdvice) {
    reasons.push({
      title: copy("Retry guidance is already projecting the dominant mission blocker", "重试建议已经投射出当前任务的主要阻塞"),
      copy: retryAdvice.summary || copy("Latest failed run still needs operator remediation.", "最近失败执行仍需要操作者修复。"),
      tone: "hot",
      facts: [
        { label: copy("Retry", "重试"), value: retryAdvice.retry_command || copy("open guidance", "查看指引") },
        { label: copy("Daemon", "守护进程"), value: retryAdvice.daemon_retry_command || "-" },
      ],
      owner: copy("retry advice", "重试建议"),
    });
  }
  reasons.push({
    title: recentResults.length
      ? copy("Current mission already has inspectable results", "当前任务已经有可检查的结果")
      : copy("Cockpit still shows the current mission posture even before results accumulate", "即使结果尚未积累，驾驶舱也会继续显示当前任务姿态"),
    copy: recentResults.length
      ? copy("Result stream, alert rules, and delivery stats are already enough to keep the mission in one inspectable surface.", "结果流、告警规则和交付统计已经足以把任务保持在一个可检查工作面里。")
      : copy("Run history, alert rules, and board context are already enough to keep the next action visible in Cockpit.", "执行历史、告警规则和任务列表上下文已经足以让驾驶舱显示下一步动作。"),
    tone: recentResults.length ? "ok" : "",
    facts: [
      { label: copy("Runs", "执行次数"), value: String(recentRuns.length || 0) },
      { label: copy("Results", "结果数"), value: String(recentResults.length || 0) },
      { label: copy("Alerts", "告警"), value: String(deliveryStats.recent_alert_count || recentAlerts.length || 0) },
    ],
    owner: copy("mission cockpit", "任务驾驶舱"),
  });

  const nextSteps = retryAdvice
    ? [{
        title: copy("Use retry guidance before treating this mission as trustworthy again", "在重新信任这条任务前，先执行重试指引"),
        copy: copy("Fix the collector or credential issue first, then rerun the mission and re-check delivery posture from Cockpit.", "先修复采集器或凭据问题，再重新执行任务，并回到驾驶舱复核交付姿态。"),
        tone: "hot",
        facts: [
          { label: copy("Mission", "任务"), value: clampLabel(watch?.name || watch?.id || copy("selected", "当前任务"), 24) },
          { label: copy("Alert rules", "告警规则"), value: String(watch?.alert_rule_count || 0) },
        ],
        owner: copy("retry advice", "重试建议"),
      }]
    : [{
        title: recentResults.length
          ? copy("Review the result stream, then hand verified evidence into triage or delivery", "先看结果流，再把已确认信号交给分诊或交付")
          : copy("Run the mission once before expecting triage or delivery movement", "先执行一次任务，再期待分诊或交付推进"),
        copy: recentResults.length
          ? copy("Cockpit already has enough runtime facts. The next hop is usually Triage for verification or Ops for delivery inspection.", "驾驶舱已经有足够的运行事实；下一跳通常是进入分诊做核验，或进入运维看交付。")
          : copy("One successful run is enough to seed real evidence for the next lifecycle lanes.", "只要成功执行一次，就足以为后续生命周期工作线沉淀真实证据。"),
        tone: recentResults.length ? "ok" : "",
        facts: [
          { label: copy("Last run", "最近执行"), value: localizeWord(watch?.last_run_status || "idle") },
          { label: copy("Recent alerts", "最近告警"), value: String(recentAlerts.length || 0) },
        ],
        owner: copy("mission cockpit", "任务驾驶舱"),
      }];

  const sources = [
    {
      title: copy("Retry and delivery wording stays owned by runtime watch facts", "重试与交付文案继续归运行时任务事实所有"),
      copy: copy("Cockpit guidance reuses watch retry advice, recent alerts, and current run statistics instead of inventing a separate browser-only explanation layer.", "驾驶舱指引会复用任务重试建议、近期告警和当前执行统计，而不是再发明一层浏览器私有解释。"),
      owner: copy("runtime facts", "运行时事实"),
    },
    {
      title: copy("Alert field meaning still stays in the parameter guide", "告警字段含义仍然归参数说明文档所有"),
      copy: copy("Alert Route, domain, score gate, and confidence gate semantics remain documented centrally in docs/datapulse_console_parameter_guide.md.", "告警路由、域名、分数门槛和置信度门槛的含义仍集中写在 docs/datapulse_console_parameter_guide.md。"),
      owner: copy("static docs", "静态文档"),
    },
  ];

  return renderOperatorGuidanceSurface({
    surfaceId: "cockpit-guidance-surface",
    lane: "mission",
    title: copy("Mission Action Guidance", "任务动作指引"),
    summary: copy("Keep runtime reasons, retry posture, and the next cockpit handoff persistent so operators do not rely on transient success or error toasts.", "把运行原因、重试姿态和驾驶舱下一步交接固定下来，避免操作者只能依赖短暂的成功或错误 toast。"),
    reasons,
    nextSteps,
    sources,
    actionHierarchy: {
      primary: retryAdvice
        ? makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), { "data-empty-jump": "section-ops" })
        : recentResults.length
          ? makeSurfaceAction(copy("Open Triage", "打开分诊"), { "data-empty-jump": "section-triage" })
          : watch?.enabled === false
            ? makeSurfaceAction(copy("Enable Mission", "启用任务"), { "data-watch-toggle": watch?.id || "", "data-watch-enabled": "0" })
            : makeSurfaceAction(copy("Run Mission", "执行任务"), { "data-empty-run-watch": watch?.id || "" }),
      secondary: [
        makeSurfaceAction(copy("Open Mission Board", "打开任务列表"), { "data-empty-jump": "section-board" }),
        makeSurfaceAction(copy("Focus Alert Rules", "聚焦告警规则"), { "data-empty-focus": "mission", "data-empty-field": "route" }),
      ],
    },
  });
}

function buildTriageGuidanceSurface(item, linkedStories = [], duplicateExplain = null, nextHopActions = {}) {
  const noteCount = Array.isArray(item?.review_notes) ? item.review_notes.length : 0;
  const candidateCount = Number(duplicateExplain?.candidate_count || 0);
  const reasons = [];
  if (candidateCount) {
    reasons.push({
      title: copy("Duplicate explain already surfaced merge pressure", "重复解释已经暴露出合并压力"),
      copy: copy("Keep the selected evidence here while comparing close matches so the queue can move without losing reasoning context.", "在比较相近候选时，把当前证据保留在这里，队列推进就不会丢失推理上下文。"),
      tone: "hot",
      facts: [
        { label: copy("Matches", "匹配数"), value: String(candidateCount) },
        { label: copy("Primary", "主项"), value: duplicateExplain?.suggested_primary_id || copy("n/a", "暂无") },
      ],
      owner: copy("duplicate explain", "重复解释"),
    });
  }
  reasons.push({
    title: linkedStories.length
      ? copy("Story handoff is already visible for the selected evidence", "当前证据已经能直接看到故事交接")
      : copy("Reviewer context stays attached to the selected evidence", "审核上下文继续附着在当前证据上"),
    copy: linkedStories.length
      ? copy("Linked stories mean the operator can continue narrative work without re-finding this evidence later.", "已有的关联故事意味着操作者无需以后重新定位这条证据，就能继续推进叙事。")
      : copy("Notes, score, and queue state remain visible here so the next review action does not depend on list scanning alone.", "备注、分数和队列状态会留在这里，下一次审阅动作不必只靠扫列表决定。"),
    tone: linkedStories.length ? "ok" : "",
    facts: [
      { label: copy("Notes", "备注"), value: String(noteCount) },
      { label: copy("Linked stories", "关联故事"), value: String(linkedStories.length) },
      { label: copy("State", "状态"), value: localizeWord(item?.review_state || "new") },
    ],
    owner: copy("triage workspace", "分诊工作区"),
  });

  const nextSteps = [{
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
      { label: copy("Queue", "队列"), value: localizeWord(state.triageFilter || "open") },
      { label: copy("Score", "分数"), value: String(item?.score || 0) },
    ],
    owner: candidateCount ? copy("duplicate explain", "重复解释") : copy("triage workspace", "分诊工作区"),
  }];

  const sources = [
    {
      title: copy("Duplicate reasoning remains owned by duplicate explain", "重复推理继续归重复解释接口所有"),
      copy: copy("The browser only projects candidate counts, suggested primary, and similarity signals that already came from the triage explain endpoint.", "浏览器只投影来自 triage explain 接口的候选数、建议主项和相似度信号。"),
      owner: copy("runtime facts", "运行时事实"),
    },
    {
      title: copy("Reviewer notes remain the human-authored rationale surface", "审核备注仍然是人工填写的理由面"),
      copy: copy("Note capture stays visible beside the selected evidence so operator reasoning is not hidden behind a mutation toast.", "备注录入会和当前证据并排可见，操作者推理不会被隐藏在一次 mutation toast 之后。"),
      owner: copy("review notes", "审核备注"),
    },
  ];

  return renderOperatorGuidanceSurface({
    surfaceId: "triage-guidance-surface",
    lane: "triage",
    title: copy("Triage Action Guidance", "分诊动作指引"),
    summary: copy("Keep duplicate pressure, reviewer rationale, and the next triage move in one persistent surface while the list remains available for switching.", "把重复压力、审核理由和分诊下一步固定在一个持久面板里，同时保留列表用于切换条目。"),
    reasons,
    nextSteps,
    sources,
    actionHierarchy: nextHopActions,
  });
}

function buildStoryGuidanceSurface(story, storyDeliveryStatus) {
  const evidenceCount = getStoryEvidenceIds(story).length;
  const contradictionCount = Array.isArray(story?.contradictions) ? story.contradictions.length : 0;
  const reasons = [{
    title: contradictionCount
      ? copy("Contradiction markers are still shaping editorial confidence", "冲突标记仍在影响编辑可信度")
      : copy("Current story has enough grounded context to keep moving", "当前故事已经有足够的落地上下文继续推进"),
    copy: contradictionCount
      ? copy("Resolve the contradiction markers before treating this story as export-ready or delivery-safe.", "在把这条故事视为可导出或可交付之前，先处理冲突标记。")
      : copy("Evidence, timeline, and story status are already aligned enough to keep editorial work inside one workspace.", "证据、时间线和故事状态已经足够一致，可以继续在同一个工作区推进编辑。"),
    tone: contradictionCount ? "hot" : "ok",
    facts: [
      { label: copy("Evidence", "证据"), value: String(evidenceCount) },
      { label: copy("Conflicts", "冲突"), value: String(contradictionCount) },
      { label: copy("Delivery", "交付"), value: storyDeliveryStatus?.label || copy("n/a", "暂无") },
    ],
    owner: copy("story snapshot", "故事快照"),
  }];
  if (storyDeliveryStatus?.key === "blocked") {
    reasons.push({
      title: copy("Delivery gate is still explicitly blocked", "交付门禁仍然明确处于阻塞"),
      copy: copy("Story readiness exists, but downstream delivery posture still needs operator review before promotion or export.", "当前故事已经具备一定就绪度，但在提升或导出前，下游交付姿态仍需要操作者复核。"),
      tone: "hot",
      facts: [
        { label: copy("Status", "状态"), value: localizeWord(story?.status || "active") },
        { label: copy("Updated", "更新"), value: formatCompactDateTime(story?.updated_at || story?.generated_at || "") },
      ],
      owner: copy("story delivery status", "故事交付状态"),
    });
  }

  const nextSteps = [{
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
      { label: copy("Timeline", "时间线"), value: String((story?.timeline || []).length) },
      { label: copy("Entities", "实体"), value: String((story?.entities || []).length) },
    ],
    owner: copy("story workspace", "故事工作台"),
  }];

  const sources = [
    {
      title: copy("Editorial guidance stays owned by persisted story facts", "编辑指引继续归持久化故事事实所有"),
      copy: copy("Story summary, contradiction markers, delivery posture, and evidence counts all come from the persisted story snapshot rather than browser-only staging text.", "故事摘要、冲突标记、交付姿态和证据计数都来自持久化故事快照，而不是浏览器私有暂存文案。"),
      owner: copy("runtime facts", "运行时事实"),
    },
    {
      title: copy("Route and delivery wording stays shared with the delivery lane", "路由与交付文案继续与交付工作线共享"),
      copy: copy("When the story points toward delivery, the browser keeps using the same route-health and delivery-posture semantics already visible in Ops.", "当故事进入交付判断时，浏览器继续沿用 Ops 里已经可见的路由健康和交付姿态语义。"),
      owner: copy("shared contract", "共享契约"),
    },
  ];

  return renderOperatorGuidanceSurface({
    surfaceId: "story-guidance-surface",
    lane: "story",
    title: copy("Story Action Guidance", "故事动作指引"),
    summary: copy("Keep editorial blockers, delivery posture, and the next narrative move explicit before the operator exports or hands the story downstream.", "在操作者导出或下游交接前，把编辑阻塞、交付姿态和叙事下一步明确显示出来。"),
    reasons,
    nextSteps,
    sources,
    actionHierarchy: {
      primary: contradictionCount
        ? makeSurfaceAction(copy("Focus Evidence In Triage", "回查分诊证据"), { "data-empty-jump": "section-triage" })
        : makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), { "data-empty-jump": "section-ops" }),
      secondary: [
        makeSurfaceAction(copy("Preview Markdown", "预览 Markdown"), { "data-story-markdown": story?.id || "" }),
        makeSurfaceAction(copy("Open Route Manager", "打开路由管理"), { "data-empty-focus": "route", "data-empty-field": "name" }),
      ],
    },
  });
}

function buildRouteGuidanceSurface({ draft = {}, editing = false, health = null, usageCount = 0 } = {}) {
  const reasons = [];
  if (health && String(health.status || "").trim() && String(health.status || "").trim().toLowerCase() !== "healthy" && String(health.status || "").trim().toLowerCase() !== "idle") {
    reasons.push({
      title: copy("Route health is the main delivery-side explanation owner here", "路由健康是这里最主要的交付侧解释来源"),
      copy: health.last_error || health.last_summary || copy("Recent route events already indicate this sink needs review before operators trust it again.", "最近的路由事件已经表明，这个交付目标在重新被信任前需要复核。"),
      tone: "hot",
      facts: [
        { label: copy("Status", "状态"), value: localizeWord(health.status || "idle") },
        { label: copy("Rate", "成功率"), value: formatRate(health.success_rate) },
        { label: copy("Last", "最近"), value: formatCompactDateTime(health.last_event_at || "") },
      ],
      owner: copy("route health", "路由健康"),
    });
  }
  reasons.push({
    title: editing
      ? copy("Named routes keep mission references stable while the sink changes in place", "命名路由允许在原位改 sink，同时保持任务引用稳定")
      : copy("A named route becomes reusable mission delivery plumbing", "命名路由会沉淀成可复用的任务交付基础设施"),
    copy: editing
      ? copy("Route name remains fixed during edit, so existing mission alert rules keep resolving to the same route contract.", "编辑期间路由名称保持不变，因此已有任务的告警规则仍会解析到同一契约。")
      : copy("Create the sink once here, then reuse it from Mission Intake or Cockpit instead of retyping delivery details for every mission.", "先在这里把交付目标配置好，后续从任务录入区或驾驶舱直接复用，而不是每条任务都重填交付细节。"),
    tone: usageCount ? "ok" : "",
    facts: [
      { label: copy("Used", "已引用"), value: String(usageCount) },
      { label: copy("Channel", "通道"), value: routeChannelLabel(draft.channel || "webhook") },
      { label: copy("Route", "路由"), value: normalizeRouteName(draft.name) || copy("draft", "草稿") },
    ],
    owner: copy("route manager", "路由管理"),
  });

  let missingField = "";
  if (!String(draft.name || "").trim()) {
    missingField = "name";
  } else if (draft.channel === "webhook" && !String(draft.webhook_url || "").trim()) {
    missingField = "webhook_url";
  } else if (draft.channel === "feishu" && !String(draft.feishu_webhook || "").trim()) {
    missingField = "feishu_webhook";
  } else if (draft.channel === "telegram" && !String(draft.telegram_chat_id || "").trim()) {
    missingField = "telegram_chat_id";
  }
  const nextSteps = missingField
    ? [{
        title: copy("Complete the route draft before expecting route-backed delivery", "先补齐路由草稿，再期待路由驱动的交付"),
        copy: copy("Route creation should stay explicit. Fill the required sink field for the chosen channel before binding missions to this route.", "路由创建应该保持明确可见；先补齐当前通道要求的目标字段，再把任务绑定到这条路由。"),
        tone: "hot",
        facts: [
          { label: copy("Missing field", "缺失字段"), value: missingField },
          { label: copy("Channel", "通道"), value: routeChannelLabel(draft.channel || "webhook") },
        ],
        owner: copy("route manager", "路由管理"),
      }]
    : [{
        title: health && String(health.status || "").trim().toLowerCase() === "healthy"
          ? copy("Attach this route to missions that now need downstream delivery", "把这条路由绑定到当前需要下游交付的任务")
          : copy("Save the route, then inspect mission and delivery posture from the same shell", "先保存路由，再在同一个控制台里检查任务和交付姿态"),
        copy: health && String(health.status || "").trim().toLowerCase() === "healthy"
          ? copy("This route already shows a healthy posture. The next move is usually to reuse it from mission alert rules.", "当前路由已经表现出健康姿态；下一步通常是从任务告警规则里复用它。")
          : copy("Once the route is saved, Mission Intake and Cockpit can reuse the same named sink without inventing another explanation layer.", "一旦路由保存完成，任务录入区和驾驶舱就能复用同一个命名 sink，而不需要另一套解释层。"),
        tone: health && String(health.status || "").trim().toLowerCase() === "healthy" ? "ok" : "",
        facts: [
          { label: copy("Used", "已引用"), value: String(usageCount) },
          { label: copy("Focused route", "当前路由"), value: normalizeRouteName(draft.name) || copy("draft", "草稿") },
        ],
        owner: health ? copy("route health", "路由健康") : copy("route manager", "路由管理"),
      }];

  const sources = [
    {
      title: copy("Route remediation wording remains owned by route health facts", "路由修复文案继续归路由健康事实所有"),
      copy: copy("Delivery failures, degraded status, and recent route event summaries keep coming from route health rather than browser-only heuristics.", "交付失败、降级状态和最近路由事件摘要继续来自 route health，而不是浏览器本地 heuristics。"),
      owner: copy("runtime facts", "运行时事实"),
    },
    {
      title: copy("Alert Route field meaning still stays in the parameter guide", "Alert Route 字段含义仍然归参数说明文档所有"),
      copy: copy("The route field remains a reusable named sink reference, as documented in docs/datapulse_console_parameter_guide.md.", "路由字段仍然表示可复用的命名交付目标，定义继续记录在 docs/datapulse_console_parameter_guide.md。"),
      owner: copy("static docs", "静态文档"),
    },
  ];

  return renderOperatorGuidanceSurface({
    surfaceId: "route-guidance-surface",
    lane: "route",
    title: copy("Route Action Guidance", "路由动作指引"),
    summary: copy("Keep route remediation, sink readiness, and mission attachment guidance persistent so delivery setup does not rely on ephemeral toast feedback.", "把路由修复、目标就绪度和任务绑定指引固定下来，避免交付设置只能依赖短暂 toast。"),
    reasons,
    nextSteps,
    sources,
    actionHierarchy: {
      primary: missingField
        ? makeSurfaceAction(copy("Focus Route Draft", "聚焦路由草稿"), { "data-empty-focus": "route", "data-empty-field": missingField })
        : makeSurfaceAction(copy("Focus Mission Draft", "聚焦任务草稿"), { "data-empty-focus": "mission", "data-empty-field": "route" }),
      secondary: [
        makeSurfaceAction(copy("Open Delivery Lane", "打开交付工作线"), { "data-empty-jump": "section-ops" }),
        editing ? makeSurfaceAction(copy("Use In Mission", "用于任务草稿"), { "data-route-apply": draft.name || "" }) : null,
      ].filter(Boolean),
    },
  });
}

function isHighRiskTriageItem(item) {
  return Number(item?.score || 0) >= 80 || Number(item?.confidence || 0) >= 0.9;
}

function getMissionCardActionHierarchy(watch) {
  const enabled = Boolean(watch?.enabled);
  const lastStatus = String(watch?.last_run_status || "").trim().toLowerCase();
  const neverRun = !String(watch?.last_run_at || "").trim();
  const due = Boolean(watch?.is_due);
  const secondary = [];
  const danger = [];
  if (!watch || !watch.id) {
    return { primary: null, secondary, danger };
  }
  const openCockpit = makeSurfaceAction(copy("Open Cockpit", "打开驾驶舱"), { "data-watch-open": watch.id });
  const editMission = makeSurfaceAction(copy("Edit Mission", "编辑任务"), { "data-edit-watch": watch.id });
  const runMission = makeSurfaceAction(copy("Run Mission", "执行任务"), { "data-run-watch": watch.id });
  const retryMission = makeSurfaceAction(copy("Retry Mission", "重试任务"), { "data-run-watch": watch.id });
  const enableMission = makeSurfaceAction(copy("Enable", "启用"), {
    "data-watch-toggle": watch.id,
    "data-watch-enabled": "0",
  });
  const disableMission = makeSurfaceAction(copy("Disable", "停用"), {
    "data-watch-toggle": watch.id,
    "data-watch-enabled": "1",
  });
  const deleteMission = makeSurfaceAction(copy("Delete", "删除"), { "data-delete-watch": watch.id });
  if (!enabled) {
    return {
      primary: enableMission,
      secondary: [openCockpit, editMission],
      danger: [deleteMission],
    };
  }
  danger.push(disableMission, deleteMission);
  if (lastStatus === "error") {
    secondary.push(openCockpit, editMission);
    return { primary: retryMission, secondary, danger };
  }
  if (due || neverRun) {
    secondary.push(openCockpit, editMission);
    return { primary: runMission, secondary, danger };
  }
  secondary.push(runMission, editMission);
  return { primary: openCockpit, secondary, danger };
}

function getTriageCardActionHierarchy(item, linkedStories = []) {
  const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
  const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
  const isOpenState = reviewState === "new" || reviewState === "triaged";
  const openStoryWorkspace = makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {
    "data-empty-jump": "section-story",
    "data-story-workspace-mode": "editor",
  });
  const createStory = makeSurfaceAction(copy("Create Story", "生成故事"), { "data-triage-story": item.id });
  const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), { "data-triage-explain": item.id });
  const verifyItem = makeSurfaceAction(copy("Verify", "核验"), {
    "data-triage-state": "verified",
    "data-triage-id": item.id,
  });
  const escalateItem = makeSurfaceAction(copy("Escalate", "升级"), {
    "data-triage-state": "escalated",
    "data-triage-id": item.id,
  });
  const ignoreItem = makeSurfaceAction(copy("Ignore", "忽略"), {
    "data-triage-state": "ignored",
    "data-triage-id": item.id,
  });
  const deleteItem = makeSurfaceAction(copy("Delete", "删除"), { "data-triage-delete": item.id });
  const storyAction = hasLinkedStory ? openStoryWorkspace : createStory;
  const danger = reviewState === "ignored" ? [deleteItem] : [ignoreItem, deleteItem];
  if (isOpenState && isHighRiskTriageItem(item)) {
    return {
      primary: escalateItem,
      secondary: [verifyItem, storyAction],
      danger,
    };
  }
  if (isOpenState) {
    return {
      primary: verifyItem,
      secondary: [escalateItem, storyAction],
      danger,
    };
  }
  if (reviewState === "verified" || reviewState === "escalated") {
    return {
      primary: storyAction,
      secondary: [explainDup, reviewState === "escalated" ? verifyItem : null].filter(Boolean).slice(0, 2),
      danger,
    };
  }
  return {
    primary: hasLinkedStory ? openStoryWorkspace : explainDup,
    secondary: [storyAction, verifyItem],
    danger,
  };
}

function getTriageWorkbenchActionHierarchy(item, linkedStories = []) {
  const base = getTriageCardActionHierarchy(item, linkedStories);
  const hasLinkedStory = Array.isArray(linkedStories) && linkedStories.length > 0;
  const primary = hasLinkedStory
    ? makeSurfaceAction(copy("Open Story Workspace", "打开故事工作台"), {
      "data-empty-jump": "section-story",
      "data-story-workspace-mode": "editor",
    })
    : makeSurfaceAction(copy("Create Story", "生成故事"), { "data-triage-story": item.id });
  const explainDup = makeSurfaceAction(copy("Explain Dup", "查看重复解释"), { "data-triage-explain": item.id });
  const secondary = [];
  if (base.primary && base.primary.label !== primary.label) {
    secondary.push(base.primary);
  }
  secondary.push(explainDup);
  const reviewState = String(item?.review_state || "new").trim().toLowerCase() || "new";
  const danger = reviewState === "ignored"
    ? [makeSurfaceAction(copy("Delete", "删除"), { "data-triage-delete": item.id })]
    : [
        makeSurfaceAction(copy("Ignore", "忽略"), {
          "data-triage-state": "ignored",
          "data-triage-id": item.id,
        }),
        makeSurfaceAction(copy("Delete", "删除"), { "data-triage-delete": item.id }),
      ];
  return {
    primary,
    secondary: secondary.filter(Boolean).slice(0, 2),
    danger,
  };
}

function getStoryCardActionHierarchy(story) {
  const archived = String(story?.status || "active").trim().toLowerCase() === "archived";
  return {
    primary: makeSurfaceAction(copy("Open Story", "打开故事"), {
      "data-story-open": story.id,
      "data-story-open-mode": state.storyWorkspaceMode,
    }),
    secondary: [
      makeSurfaceAction(
        archived ? copy("Restore", "恢复") : copy("Archive", "归档"),
        {
          "data-story-quick-status": story.id,
          "data-story-next-status": archived ? "active" : "archived",
        },
      ),
      makeSurfaceAction(copy("Preview MD", "预览 MD"), { "data-story-preview": story.id }),
    ],
    danger: [],
  };
}

function getRouteCardActionHierarchy(route, health = null, usageCount = 0) {
  const routeName = String(route?.name || health?.name || "").trim();
  if (!routeName) {
    return { primary: null, secondary: [], danger: [] };
  }
  const healthStatus = String(health?.status || route?.status || "idle").trim().toLowerCase() || "idle";
  const unhealthy = healthStatus && !["healthy", "idle"].includes(healthStatus);
  const editRoute = makeSurfaceAction(
    unhealthy ? copy("Inspect Route", "检查路由") : copy("Edit Route", "编辑路由"),
    { "data-route-edit": routeName },
  );
  const attachRoute = makeSurfaceAction(copy("Attach To Mission", "绑定到任务"), { "data-route-attach": routeName });
  const deleteRoute = makeSurfaceAction(copy("Delete", "删除"), { "data-route-delete": routeName });
  if (unhealthy) {
    return {
      primary: editRoute,
      secondary: [attachRoute],
      danger: [deleteRoute],
    };
  }
  if (!usageCount) {
    return {
      primary: attachRoute,
      secondary: [editRoute],
      danger: [deleteRoute],
    };
  }
  return {
    primary: editRoute,
    secondary: [attachRoute],
    danger: [deleteRoute],
  };
}

function renderOverview() {
  const metrics = state.overview || {};
  if (state.loading.board && !state.overview) {
    $("overview-metrics").innerHTML = [metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "..."), metricCard(copy("Loading", "加载中"), "...")].join("");
    renderTopbarContext();
    return;
  }
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
}

function renderWatches() {
  const root = $("watch-list");
  const searchValue = String(state.watchSearch || "");
  if (state.loading.board && !state.watches.length) {
    renderBoardSectionSummary([], searchValue);
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    renderTopbarContext();
    return;
  }
  if (!state.watches.length) {
    renderBoardSectionSummary([], searchValue);
    root.innerHTML = `
      ${renderLifecycleGuideCard({
        title: copy("Start the lifecycle with one mission draft", "先用一个任务草稿启动生命周期"),
        summary: copy(
          "Name and Query are enough to create the first watch. Once it runs, the browser can guide you through triage, story promotion, and delivery setup without leaving this shell.",
          "只用名称和查询词就能先把第一个任务建起来。任务执行后，浏览器会继续把你带到分诊、故事沉淀和交付设置，不需要离开当前界面。"
        ),
        steps: [
          {
            title: copy("Create Watch", "创建任务"),
            copy: copy("Use Mission Intake to create or clone the first watch.", "先在任务创建区新建或复制第一个任务。"),
          },
          {
            title: copy("Run From Board", "从列表执行"),
            copy: copy("Mission Board turns the draft into real evidence collection.", "任务列表会把草稿真正推进到实时证据采集。"),
          },
          {
            title: copy("Review In Triage", "进入分诊审阅"),
            copy: copy("Inbox items arrive in Triage after the first successful run.", "第一次成功执行后，收件箱条目会进入分诊队列。"),
          },
          {
            title: copy("Promote And Route", "提升并接入路由"),
            copy: copy("Stories and named routes matter once signal is worth downstream action.", "当信号值得触发下游动作时，再去沉淀故事和接入命名路由。"),
          },
        ],
        actions: [
          { label: copy("Open Mission Draft", "打开任务草稿"), focus: "mission", field: "name", primary: true },
          { label: copy("Open Route Manager", "打开路由管理"), focus: "route", field: "name" },
        ],
      })}
      <div class="empty">${copy("No watch mission configured yet.", "当前还没有配置监测任务。")}</div>`;
    wireLifecycleGuideActions(root);
    syncWatchUrlState();
    flushWatchUrlFocus();
    renderTopbarContext();
    return;
  }
  const searchQuery = searchValue.trim().toLowerCase();
  const defaultWatchId = state.watches[0] ? state.watches[0].id : "";
  const filteredWatches = state.watches.filter((watch) => {
    if (!searchQuery) {
      return true;
    }
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
  });
  renderBoardSectionSummary(filteredWatches, searchValue);
  const searchToolbar = `
    <div class="card section-toolbox">
      <div class="section-toolbox-head">
        <div>
          <div class="mono">${copy("mission search", "任务搜索")}</div>
          <div class="panel-sub">${copy("Search by name, query, id, platform, or site to narrow the board before acting.", "可按名称、查询词、任务 ID、平台或站点快速缩小任务列表。")}</div>
        </div>
        <div class="section-toolbox-meta">
          <span class="chip">${copy("shown", "显示")}=${filteredWatches.length}</span>
          <span class="chip">${copy("total", "总数")}=${state.watches.length}</span>
        </div>
      </div>
      <div class="search-shell">
        <input type="search" value="${escapeHtml(searchValue)}" data-watch-search placeholder="${copy("Search missions", "搜索任务")}">
        <button class="btn-secondary" type="button" data-watch-search-clear ${searchValue.trim() ? "" : "disabled"}>${copy("Clear", "清空")}</button>
      </div>
    </div>
  `;
  if (!filteredWatches.length) {
    root.innerHTML = `${searchToolbar}<div class="empty">${copy("No mission matched the current search.", "没有任务匹配当前搜索。")}</div>`;
    root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {
      state.watchSearch = event.target.value;
      renderWatches();
    });
    root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {
      state.watchSearch = "";
      renderWatches();
    });
    syncWatchUrlState({ defaultWatchId });
    flushWatchUrlFocus();
    return;
  }
  root.innerHTML = `${searchToolbar}${filteredWatches.map((watch) => {
    const platforms = (watch.platforms || []).join(", ") || copy("any", "任意");
    const sites = (watch.sites || []).join(", ") || "-";
    const stateChip = watch.enabled ? "ok" : "";
    const dueChip = watch.is_due ? "hot" : "";
    const selected = watch.id === state.selectedWatchId ? "selected" : "";
    const actionHierarchy = getMissionCardActionHierarchy(watch);
    return `
      <div class="card selectable ${selected}">
        <div class="card-top">
          <div>
            <h3 class="card-title">${watch.name}</h3>
            <div class="meta">
              <span>${watch.id}</span>
              <span>${copy("schedule", "频率")}=${watch.schedule_label || watch.schedule || copy("manual", "手动")}</span>
              <span>${copy("platforms", "平台")}=${platforms}</span>
              <span>${copy("sites", "站点")}=${sites}</span>
            </div>
          </div>
          <div style="display:grid; gap:6px; justify-items:end;">
            <span class="chip ${stateChip}">${watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}</span>
            <span class="chip ${dueChip}">${watch.is_due ? copy("due", "待执行") : copy("waiting", "等待")}</span>
          </div>
        </div>
        <div class="meta">
          <span>${copy("alert_rules", "告警规则")}=${watch.alert_rule_count || 0}</span>
          <span>${copy("last_run", "上次执行")}=${watch.last_run_at || "-"}</span>
          <span>${copy("status", "状态")}=${localizeWord(watch.last_run_status || "-")}</span>
          <span>${copy("next", "下次")}=${watch.next_run_at || "-"}</span>
        </div>
        ${renderCardActionHierarchy(actionHierarchy)}
      </div>`;
  }).join("")}`;

  root.querySelector("[data-watch-search]")?.addEventListener("input", (event) => {
    state.watchSearch = event.target.value;
    renderWatches();
  });
  root.querySelector("[data-watch-search-clear]")?.addEventListener("click", () => {
    state.watchSearch = "";
    renderWatches();
  });

  root.querySelectorAll("[data-watch-open]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await loadWatch(button.dataset.watchOpen);
      } catch (error) {
        reportError(error, copy("Open mission", "打开任务"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-edit-watch]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await editMissionInCreateWatch(button.dataset.editWatch);
      } catch (error) {
        reportError(error, copy("Edit mission", "编辑任务"));
      } finally {
        button.disabled = false;
      }
    });
  });

  root.querySelectorAll("[data-run-watch]").forEach((button) => {
    button.addEventListener("click", async () => {
      const identifier = String(button.dataset.runWatch || "").trim();
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

  root.querySelectorAll("[data-delete-watch]").forEach((button) => {
    button.addEventListener("click", async () => {
      const identifier = String(button.dataset.deleteWatch || "").trim();
      const removedWatch = state.watches.find((watch) => watch.id === identifier);
      const removedDetail = state.watchDetails[identifier] ? { ...state.watchDetails[identifier] } : null;
      button.disabled = true;
      state.watches = state.watches.filter((watch) => watch.id !== identifier);
      delete state.watchDetails[identifier];
      if (state.selectedWatchId === identifier) {
        state.selectedWatchId = state.watches[0] ? state.watches[0].id : "";
      }
      renderWatches();
      renderWatchDetail();
      try {
        await api(`/api/watches/${identifier}`, { method: "DELETE" });
        pushActionEntry({
          kind: "mission delete",
          label: `Deleted ${removedWatch && removedWatch.name ? removedWatch.name : identifier}`,
          detail: "Deletion is reversible from the recent action log.",
          undoLabel: "Restore",
          undo: async () => {
            if (!removedWatch) {
              return;
            }
            const payload = {
              name: String(removedWatch.name || identifier),
              query: String(removedWatch.query || ""),
              schedule: String(removedWatch.schedule || removedWatch.schedule_label || "manual"),
              platforms: Array.isArray(removedWatch.platforms) ? removedWatch.platforms : [],
              alert_rules: removedDetail && Array.isArray(removedDetail.alert_rules) ? removedDetail.alert_rules : [],
            };
            await api("/api/watches", { method: "POST", payload });
            await refreshBoard();
            showToast(`Mission restored: ${payload.name}`, "success");
          },
        });
        await refreshBoard();
      } catch (error) {
        if (removedWatch) {
          state.watches = [removedWatch, ...state.watches];
        }
        if (removedDetail) {
          state.watchDetails[identifier] = removedDetail;
        }
        reportError(error, "Delete mission");
        await refreshBoard();
      } finally {
        button.disabled = false;
      }
    });
  });
  syncWatchUrlState({ defaultWatchId });
  flushWatchUrlFocus();
  renderTopbarContext();
}

async function loadWatch(identifier, { force = false } = {}) {
  const normalizedId = String(identifier || "").trim();
  if (!normalizedId) {
    return null;
  }
  state.selectedWatchId = normalizedId;
  state.loading.watchDetail = true;
  renderWatches();
  renderWatchDetail();
  try {
    if (force || !state.watchDetails[normalizedId]) {
      state.watchDetails[normalizedId] = await api(`/api/watches/${normalizedId}`);
    }
  } finally {
    state.loading.watchDetail = false;
  }
  setContextRouteFromWatch();
  renderWatches();
  renderWatchDetail();
  return state.watchDetails[normalizedId] || null;
}

function renderWatchDetail() {
  const root = $("watch-detail");
  renderFormSuggestionLists();
  const selected = state.selectedWatchId;
  const loadingWatch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected) || null;
  if (state.loading.watchDetail && selected) {
    renderCockpitSectionSummary(loadingWatch);
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    renderTopbarContext();
    return;
  }
  const watch = state.watchDetails[selected] || state.watches.find((candidate) => candidate.id === selected);
  if (!watch) {
    renderCockpitSectionSummary(null);
    const firstWatch = state.watches[0] || null;
    root.innerHTML = `
      ${renderLifecycleGuideCard({
        title: copy("Open one mission to move from draft into live evidence", "打开一个任务，把草稿推进到实时证据"),
        summary: copy(
          "Cockpit is the handoff point between mission setup and downstream review. Open a mission here to run it, inspect recent output, and decide whether triage or delivery needs attention next.",
          "任务详情是“创建任务”和“进入审阅”之间的交接点。先在这里打开一个任务，执行它、查看近期输出，再决定下一步是进入分诊还是补充交付设置。"
        ),
        steps: [
          {
            title: copy("Open Cockpit", "打开任务详情"),
            copy: copy("Pick a mission from the board to inspect its current operating lane.", "先从任务列表里选中一个任务，查看它当前的运行状态。"),
          },
          {
            title: copy("Run Mission", "执行任务"),
            copy: copy("One run is enough to populate results, timeline, and future triage work.", "先执行一次任务，就能填充结果流、时间线和后续分诊工作。"),
          },
          {
            title: copy("Inspect Output", "检查输出"),
            copy: copy("Review result filters, retry guidance, and alert rules before you leave the cockpit.", "离开任务详情前，先看结果筛选、重试建议和告警规则。"),
          },
          {
            title: copy("Follow The Lifecycle", "沿生命周期推进"),
            copy: copy("From here, the next hop is usually Triage, then Stories, then route-backed delivery.", "从这里出发，通常下一站是分诊，然后是故事，最后才是路由交付。"),
          },
        ],
        actions: [
          firstWatch
            ? { label: copy("Open First Mission", "打开第一个任务"), watch: firstWatch.id, primary: true }
            : { label: copy("Open Mission Board", "打开任务列表"), section: "section-board", primary: true },
          { label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "name" },
        ],
      })}
      <div class="empty">${copy("Select one mission from the board to inspect schedule, run history, and alert output.", "从看板中选择一个任务，以查看调度、执行历史和告警输出。")}</div>`;
    wireLifecycleGuideActions(root);
    renderTopbarContext();
    return;
  }
  const recentRuns = Array.isArray(watch.runs) ? watch.runs : [];
  const recentResults = Array.isArray(watch.recent_results) ? watch.recent_results : [];
  const recentAlerts = Array.isArray(watch.recent_alerts) ? watch.recent_alerts : [];
  const lastFailure = watch.last_failure || null;
  const retryAdvice = watch.retry_advice || null;
  const runStats = watch.run_stats || {};
  const resultStats = watch.result_stats || {};
  const visibleResultCount = Number(resultStats.visible_result_count);
  const deliveryStats = watch.delivery_stats || {};
  const resultFilters = watch.result_filters || {};
  const timelineEvents = Array.isArray(watch.timeline_strip) ? watch.timeline_strip : [];
  const stateOptions = Array.isArray(resultFilters.states) ? resultFilters.states : [];
  const sourceOptions = Array.isArray(resultFilters.sources) ? resultFilters.sources : [];
  const domainOptions = Array.isArray(resultFilters.domains) ? resultFilters.domains : [];
  const savedFilters = state.watchResultFilters[watch.id] || {};
  const normalizeFilterValue = (key, options) => {
    const raw = String(savedFilters[key] || "all");
    return raw === "all" || options.some((option) => option.key === raw) ? raw : "all";
  };
  const activeFilters = {
    state: normalizeFilterValue("state", stateOptions),
    source: normalizeFilterValue("source", sourceOptions),
    domain: normalizeFilterValue("domain", domainOptions),
  };
  state.watchResultFilters[watch.id] = activeFilters;
  const runsBlock = recentRuns.length
    ? recentRuns.map((run) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${run.status || "success"}</h3>
              <div class="meta">
                <span>${run.id || "-"}</span>
                <span>${copy("trigger", "触发方式")}=${localizeWord(run.trigger || "manual")}</span>
                <span>${copy("items", "条目")}=${run.item_count || 0}</span>
              </div>
            </div>
            <span class="chip ${run.status === "success" ? "ok" : "hot"}">${localizeWord(run.status || "unknown")}</span>
          </div>
          <div class="meta">
            <span>${copy("started", "开始")}=${run.started_at || "-"}</span>
            <span>${copy("finished", "结束")}=${run.finished_at || "-"}</span>
          </div>
          <div class="panel-sub">${run.error || copy("No recorded error.", "没有记录到错误。")}</div>
        </div>
      `).join("")
    : `
        <div class="card">
          <div class="mono">${copy("no run yet", "尚未执行")}</div>
          <div class="panel-sub">${watch.enabled
            ? copy("Run this mission once to seed the triage queue, story workspace, and alert history with real evidence.", "先执行一次这个任务，分诊队列、故事工作台和告警历史才会开始出现真实证据。")
            : copy("This mission is paused. Enable it first so triage, story, and alert surfaces can start receiving real evidence again.", "这条任务当前已停用。请先启用，再让分诊、故事和告警面开始接收真实证据。")}</div>
          <div class="actions" style="margin-top:12px;">
            ${
              watch.enabled
                ? `<button class="btn-primary" type="button" data-empty-run-watch="${escapeHtml(watch.id)}">${copy("Run Mission Now", "立即执行任务")}</button>`
                : `<button class="btn-primary" type="button" data-watch-toggle="${escapeHtml(watch.id)}" data-watch-enabled="0">${copy("Enable Mission", "启用任务")}</button>`
            }
            <button class="btn-secondary" type="button" data-empty-jump="section-triage">${copy("Open Triage", "打开分诊")}</button>
          </div>
        </div>
      `;
  const alertsBlock = recentAlerts.length
    ? recentAlerts.map((alert) => `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${alert.rule_name}</h3>
              <div class="meta">
                <span>${alert.created_at || "-"}</span>
                <span>${copy("items", "条目")}=${(alert.item_ids || []).length}</span>
              </div>
            </div>
            <span class="chip ${alert.extra && alert.extra.delivery_errors ? "hot" : "ok"}">${(alert.delivered_channels || ["json"]).join(",")}</span>
          </div>
          <div class="panel-sub">${alert.summary || copy("No alert summary captured.", "没有记录到告警摘要。")}</div>
        </div>
      `).join("")
    : `
        <div class="card">
          <div class="mono">${copy("delivery is still quiet", "交付尚未启动")}</div>
          <div class="panel-sub">${copy("No recent alert event is recorded for this mission. Add or tune alert rules here, then attach a named route once the mission should notify downstream.", "这个任务近期还没有告警事件。先在这里补充或调整告警规则，等任务需要通知下游时，再绑定命名路由。")}</div>
          <div class="actions" style="margin-top:12px;">
            <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${copy("Open Route Manager", "打开路由管理")}</button>
            <button class="btn-secondary" type="button" data-empty-jump="section-ops">${copy("Open Delivery Surfaces", "打开交付视图")}</button>
          </div>
        </div>
      `;
  const filteredResults = recentResults.filter((item) => {
    const filters = item.watch_filters || {};
    if (activeFilters.state !== "all" && (filters.state || "new") !== activeFilters.state) {
      return false;
    }
    if (activeFilters.source !== "all" && (filters.source || "unknown") !== activeFilters.source) {
      return false;
    }
    if (activeFilters.domain !== "all" && (filters.domain || "unknown") !== activeFilters.domain) {
      return false;
    }
    return true;
  });
  const filterGroups = [
    { key: "state", label: copy("state", "状态"), options: stateOptions },
    { key: "source", label: copy("source", "来源"), options: sourceOptions },
    { key: "domain", label: copy("domain", "域名"), options: domainOptions },
  ];
  const filterWindowCount = Number(resultFilters.window_count || recentResults.length || 0);
  const filterBlock = filterGroups.map((group) => `
      <div class="stack">
        <div class="panel-sub">${group.label}</div>
        <div class="ui-segment ui-segment-wrap" role="group" aria-label="${escapeHtml(group.key === "state"
          ? copy("Result state filters", "结果状态筛选")
          : group.key === "source"
            ? copy("Result source filters", "结果来源筛选")
            : copy("Result domain filters", "结果域名筛选"))}">
          <button class="ui-segment-button ${activeFilters[group.key] === "all" ? "active" : ""}" type="button" data-filter-group="${group.key}" data-filter-value="all" aria-pressed="${activeFilters[group.key] === "all" ? "true" : "false"}">${copy("all", "全部")} (${filterWindowCount})</button>
          ${group.options.map((option) => `
            <button class="ui-segment-button ${activeFilters[group.key] === option.key ? "active" : ""}" type="button" data-filter-group="${group.key}" data-filter-value="${escapeHtml(option.key)}" aria-pressed="${activeFilters[group.key] === option.key ? "true" : "false"}">${escapeHtml(localizeWord(option.label))} (${option.count || 0})</button>
          `).join("")}
        </div>
      </div>
    `).join("");
  const resultsBlock = filteredResults.length
    ? filteredResults.map((item) => {
        const extra = (item && typeof item.extra === "object" && item.extra) || {};
        const corroborationCount = Number(extra.corroboration_count || 0);
        const corroborationPlatforms = Array.isArray(extra.corroboration_platforms)
          ? extra.corroboration_platforms.join(", ")
          : "";
        const corroborationChip = corroborationCount >= 2
          ? `<span class="chip ok" title="${escapeHtml(corroborationPlatforms)}">${copy("corroborated", "已印证")} ×${corroborationCount}</span>`
          : "";
        return `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${item.title}</h3>
              <div class="meta">
                <span>${item.id}</span>
                <span>${copy("score", "分数")}=${item.score || 0}</span>
                <span>${copy("confidence", "置信度")}=${Number(item.confidence || 0).toFixed(2)}</span>
                <span>${item.source_name || item.source_type || "-"}</span>
              </div>
            </div>
            <div class="stack compact-stack" style="align-items:flex-end;gap:6px;">
              <span class="chip">${localizeWord(item.review_state || "new")}</span>
              ${corroborationChip}
            </div>
          </div>
          <div class="panel-sub">${item.url || "-"}</div>
        </div>
      `;
      }).join("")
    : `<div class="empty">${copy("No persisted result matched the active filter chips in the current mission window.", "当前任务窗口内没有结果匹配所选筛选条件。")}</div>`;
  const timelineBlock = timelineEvents.length
    ? `<div class="timeline-strip">${timelineEvents.map((event) => `
        <div class="timeline-event ${event.tone || ""}">
          <div class="card-top">
            <span class="chip ${event.tone || ""}">${event.kind || "event"}</span>
            <span class="panel-sub">${event.time || "-"}</span>
          </div>
          <div class="mono">${event.label || "-"}</div>
          <div class="panel-sub">${event.detail || "-"}</div>
        </div>
      `).join("")}</div>`
    : `<div class="empty">${copy("No mission timeline event captured yet.", "当前还没有记录到任务时间线事件。")}</div>`;
  const retryCollectors = retryAdvice && Array.isArray(retryAdvice.suspected_collectors)
    ? retryAdvice.suspected_collectors
    : [];
  const retryNotes = retryAdvice && Array.isArray(retryAdvice.notes) ? retryAdvice.notes : [];
  const failureBlock = lastFailure
    ? `
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("latest failure", "最近失败")}</h3>
              <div class="meta">
                <span>${lastFailure.id || "-"}</span>
                <span>${copy("status", "状态")}=${localizeWord(lastFailure.status || "error")}</span>
                <span>${copy("trigger", "触发方式")}=${localizeWord(lastFailure.trigger || "manual")}</span>
                <span>${copy("finished", "结束")}=${lastFailure.finished_at || "-"}</span>
              </div>
            </div>
            <span class="chip hot">${retryAdvice && retryAdvice.failure_class ? retryAdvice.failure_class : localizeWord("error")}</span>
          </div>
          <div class="panel-sub">${lastFailure.error || copy("No failure message captured.", "没有记录到失败信息。")}</div>
        </div>
      `
    : "";
  const retryAdviceBlock = retryAdvice
    ? `
        <div class="card">
          <div class="mono">${copy("retry advice", "重试建议")}</div>
          <div class="meta">
            <span>${copy("retry", "重试")}=${retryAdvice.retry_command || "-"}</span>
            <span>${copy("daemon", "守护进程")}=${retryAdvice.daemon_retry_command || "-"}</span>
          </div>
          <div class="panel-sub">${retryAdvice.summary || copy("No retry guidance recorded.", "没有记录到重试建议。")}</div>
          ${
            retryCollectors.length
              ? `<div class="stack" style="margin-top:12px;">${retryCollectors.map((collector) => `
                  <div class="mini-item">${collector.name} | ${collector.tier || "-"} | ${collector.status || "-"} | available=${collector.available} | ${collector.setup_hint || collector.message || "-"}</div>
                `).join("")}</div>`
              : ""
          }
          ${
            retryNotes.length
              ? `<div class="stack" style="margin-top:12px;">${retryNotes.map((note) => `<div class="mini-item">${note}</div>`).join("")}</div>`
              : ""
          }
        </div>
      `
    : "";
  const triageSignal = getGovernanceSignal("triage_throughput");
  const storySignal = getGovernanceSignal("story_conversion");
  const routeSummary = state.ops?.route_summary || {};
  const missionContinuityBlock = renderLifecycleContinuityCard({
    title: copy("Mission Continuity", "任务连续性"),
    summary: copy(
      "Mission output, review backlog, and downstream delivery facts stay visible together before you leave the cockpit.",
      "在离开任务详情之前，任务输出、审阅积压和下游交付事实会同时保持可见。"
    ),
    stages: [
      {
        kicker: copy("Current", "当前"),
        title: copy("Mission Output", "任务输出"),
        copy: copy(
          "Runs, result filters, and retry context stay attached to the active mission instead of splitting into separate hops.",
          "执行记录、结果筛选和重试上下文会继续附着在当前任务上，而不是被拆成多个跳转。"
        ),
        tone: Number.isFinite(visibleResultCount) && visibleResultCount > 0 ? "ok" : "",
        facts: [
          { label: copy("Visible results", "可见结果"), value: String(Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)) },
          { label: copy("Filtered out", "已过滤"), value: String(resultStats.filtered_result_count || 0) },
          { label: copy("Last run", "最近执行"), value: formatCompactDateTime(watch.last_run_at || recentRuns[0]?.finished_at || "") },
        ],
      },
      {
        kicker: copy("Review", "审阅"),
        title: copy("Review Lane", "审阅工作线"),
        copy: copy(
          "Queue load and story carry-over stay visible here so you can decide whether this mission needs review attention next.",
          "这里直接保留队列压力和故事承接情况，方便判断这个任务下一步是否需要进入审阅。"
        ),
        tone: (state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) > 0 ? "hot" : "ok",
        facts: [
          { label: copy("Open queue", "开放队列"), value: String(state.overview?.triage_open_count ?? triageSignal.open_items ?? 0) },
          { label: copy("Acted on", "已处理"), value: String(state.overview?.triage_acted_on_count ?? triageSignal.acted_on_items ?? 0) },
          { label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) },
        ],
      },
      {
        kicker: copy("Delivery", "交付"),
        title: copy("Delivery Lane", "交付工作线"),
        copy: copy(
          "Alert events, ready stories, and healthy routes stay one glance away from the same mission.",
          "告警事件、待交付故事和健康路由会与同一任务保持一眼可见。"
        ),
        tone: (deliveryStats.recent_alert_count || 0) > 0 || (routeSummary.healthy || 0) > 0 ? "ok" : "",
        facts: [
          { label: copy("Recent alerts", "最近告警"), value: String(deliveryStats.recent_alert_count || 0) },
          { label: copy("Ready stories", "待交付故事"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) },
          { label: copy("Healthy routes", "健康路由"), value: String(routeSummary.healthy || 0) },
        ],
      },
    ],
    actions: [
      { label: copy("Open Triage", "打开分诊"), section: "section-triage", primary: true },
      { label: copy("Open Stories", "打开故事"), section: "section-story" },
      { label: copy("Open Delivery", "打开交付"), section: "section-ops" },
    ],
  });
  const cockpitGuidanceBlock = buildCockpitGuidanceSurface(watch, {
    recentRuns,
    recentResults,
    recentAlerts,
    retryAdvice,
    deliveryStats,
  });
  renderCockpitSectionSummary(watch, {
    recentRuns,
    recentResults,
    retryAdvice,
    lastFailure,
    deliveryStats,
  });

  root.innerHTML = `
    <div class="card">
      <div class="card-top">
        <div>
            <h3 class="card-title">${watch.name}</h3>
            <div class="meta">
              <span>${watch.id}</span>
              <span>${copy("schedule", "频率")}=${watch.schedule_label || watch.schedule || copy("manual", "手动")}</span>
              <span>${copy("next", "下次")}=${watch.next_run_at || "-"}</span>
              <span>${copy("query", "查询")}=${watch.query || "-"}</span>
            </div>
          </div>
        <span class="chip ${watch.enabled ? "ok" : "hot"}">${watch.enabled ? copy("enabled", "已启用") : copy("disabled", "已停用")}</span>
      </div>
      <div class="meta">
        <span>${copy("due", "到点")}=${localizeBoolean(watch.is_due)}</span>
        <span>${copy("alert_rules", "告警规则")}=${watch.alert_rule_count || 0}</span>
        <span>${copy("runs", "执行")}=${runStats.total || 0}</span>
        <span>${copy("success", "成功")}=${runStats.success || 0}</span>
        <span>${copy("errors", "错误")}=${runStats.error || 0}</span>
        <span>${copy("results", "结果")}=${Number.isFinite(visibleResultCount) ? visibleResultCount : (resultStats.stored_result_count || 0)}</span>
        <span>${copy("alerts", "告警")}=${deliveryStats.recent_alert_count || 0}</span>
      </div>
      <div class="actions" style="margin-top:12px;">
        <button class="btn-secondary" type="button" data-watch-edit="${watch.id}">${copy("Edit Mission", "编辑任务")}</button>
        ${
          watch.enabled
            ? `<button class="btn-secondary" type="button" data-empty-run-watch="${escapeHtml(watch.id)}">${copy("Run Mission", "执行任务")}</button>`
            : `<button class="btn-secondary" type="button" data-watch-toggle="${escapeHtml(watch.id)}" data-watch-enabled="0">${copy("Enable Mission", "启用任务")}</button>`
        }
        <button class="btn-secondary" type="button" data-empty-jump="section-triage">${copy("Open Triage", "打开分诊")}</button>
        <button class="btn-secondary" type="button" data-empty-focus="route" data-empty-field="name">${copy("Focus Route Manager", "聚焦路由管理")}</button>
      </div>
      <div class="panel-sub">${watch.last_run_error || copy("Mission history and recent delivery outcomes are visible below.", "下方可查看任务历史和最近交付结果。")}</div>
    </div>
    ${missionContinuityBlock}
    ${cockpitGuidanceBlock}
    ${failureBlock}
    ${retryAdviceBlock}
    <div class="card">
      <div class="mono">${copy("timeline strip", "时间线")}</div>
      <div class="panel-sub">${copy("Recent run, result, and alert events are merged into one server-backed mission timeline.", "最近的运行、结果和告警事件会合并成一条服务端驱动的任务时间线。")}</div>
      <div style="margin-top:12px;">
        ${timelineBlock}
      </div>
    </div>
    <div class="story-columns">
      <div class="stack">
        <div class="mono">${copy("recent runs", "最近执行")}</div>
        ${runsBlock}
      </div>
      <div class="stack">
        <div class="mono">${copy("recent alerts", "最近告警")}</div>
        ${alertsBlock}
      </div>
    </div>
    <div class="stack">
      <div class="mono">${copy("result stream", "结果流")}</div>
      <div class="card">
        <div class="mono">${copy("filter chips", "筛选标签")}</div>
        <div class="panel-sub">${copy("Filter the current persisted result window by review state, source, or domain without leaving the cockpit.", "在不离开驾驶舱的情况下，按审核状态、来源或域名筛选当前结果窗口。")}</div>
        <div class="stack" style="margin-top:12px;">
          ${filterBlock}
        </div>
      </div>
      ${resultsBlock}
    </div>
    <div class="card">
      <div class="card-top">
        <div>
          <div class="mono">${copy("alert rule editor", "告警规则编辑器")}</div>
          <div class="panel-sub">${copy("Edit multiple console threshold rules for this mission, then replace the saved rule set in one write.", "可以在这里为任务编辑多条阈值规则，并一次性替换已保存的规则集。")}</div>
        </div>
        <span class="chip">${(watch.alert_rules || []).length} ${copy("rule(s)", "条规则")}</span>
      </div>
      <form id="watch-alert-form" data-watch-id="${watch.id}">
        <div class="stack" id="watch-alert-rules">
          ${
            ((watch.alert_rules || []).length ? watch.alert_rules : [{}]).map((rule, index) => `
              <div class="card" data-alert-rule-card="${index}">
                <div class="card-top">
                  <div>
                    <div class="mono">${copy("rule", "规则")} ${index + 1}</div>
                    <div class="panel-sub">${copy("Current name", "当前名称")}: ${rule.name || "console-threshold"}</div>
                  </div>
                  <button class="btn-secondary" type="button" data-remove-alert-rule="${index}">${copy("Remove", "移除")}</button>
                </div>
                <div class="field-grid">
                  <label>${copy("Alert Route", "告警路由")}<input name="route" list="route-options-list" placeholder="ops-webhook" value="${(rule.routes || [])[0] || ""}"></label>
                  <label>${copy("Alert Keyword", "告警关键词")}<input name="keyword" list="keyword-options-list" placeholder="launch" value="${(rule.keyword_any || [])[0] || ""}"></label>
                </div>
                <div class="field-grid">
                  <label>${copy("Alert Domain", "告警域名")}<input name="domain" list="domain-options-list" placeholder="openai.com" value="${(rule.domains || [])[0] || ""}"></label>
                  <label>${copy("Min Score", "最低分数")}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric" value="${(rule.min_score || 0) || ""}"></label>
                </div>
                <div class="field-grid">
                  <label>${copy("Min Confidence", "最低置信度")}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal" value="${(rule.min_confidence || 0) || ""}"></label>
                  <div class="stack">
                    <div class="panel-sub">${copy("Channels are still pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}</div>
                  </div>
                </div>
              </div>
            `).join("")
          }
        </div>
        <div class="toolbar">
          <button class="btn-secondary" id="watch-alert-add" type="button">${copy("Add Alert Rule", "新增告警规则")}</button>
          <button class="btn-primary" type="submit">${copy("Save Alert Rules", "保存告警规则")}</button>
          <button class="btn-secondary" id="watch-alert-clear" type="button">${copy("Clear Alert Rules", "清空告警规则")}</button>
        </div>
      </form>
    </div>
  `;

  root.querySelectorAll("[data-filter-group]").forEach((button) => {
    button.addEventListener("click", () => {
      const filterGroup = String(button.dataset.filterGroup || "").trim();
      if (!filterGroup) {
        return;
      }
      const current = state.watchResultFilters[watch.id] || { state: "all", source: "all", domain: "all" };
      current[filterGroup] = String(button.dataset.filterValue || "all");
      state.watchResultFilters[watch.id] = current;
      renderWatchDetail();
    });
  });

  const alertForm = document.getElementById("watch-alert-form");
  const addRuleButton = document.getElementById("watch-alert-add");
  if (addRuleButton) {
    addRuleButton.addEventListener("click", () => {
      const rulesRoot = document.getElementById("watch-alert-rules");
      if (!rulesRoot) {
        return;
      }
      const nextIndex = rulesRoot.querySelectorAll("[data-alert-rule-card]").length;
      rulesRoot.insertAdjacentHTML("beforeend", `
        <div class="card" data-alert-rule-card="${nextIndex}">
          <div class="card-top">
            <div>
              <div class="mono">${copy("rule", "规则")} ${nextIndex + 1}</div>
              <div class="panel-sub">${copy("New console threshold rule.", "新的控制台阈值规则。")}</div>
            </div>
            <button class="btn-secondary" type="button" data-remove-alert-rule="${nextIndex}">${copy("Remove", "移除")}</button>
          </div>
          <div class="field-grid">
            <label>${copy("Alert Route", "告警路由")}<input name="route" list="route-options-list" placeholder="ops-webhook"></label>
            <label>${copy("Alert Keyword", "告警关键词")}<input name="keyword" list="keyword-options-list" placeholder="launch"></label>
          </div>
          <div class="field-grid">
            <label>${copy("Alert Domain", "告警域名")}<input name="domain" list="domain-options-list" placeholder="openai.com"></label>
            <label>${copy("Min Score", "最低分数")}<input name="min_score" list="score-options-list" placeholder="70" inputmode="numeric"></label>
          </div>
          <div class="field-grid">
            <label>${copy("Min Confidence", "最低置信度")}<input name="min_confidence" list="confidence-options-list" placeholder="0.8" inputmode="decimal"></label>
            <div class="stack">
              <div class="panel-sub">${copy("Channels stay pinned to json; named route delivery is configured via Alert Route.", "通道仍固定为 json；命名路由交付通过“告警路由”配置。")}</div>
            </div>
          </div>
        </div>
      `);
      rulesRoot.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {
        button.onclick = () => {
          button.closest("[data-alert-rule-card]")?.remove();
        };
      });
    });
  }
  root.querySelectorAll("[data-remove-alert-rule]").forEach((button) => {
    button.onclick = () => {
      button.closest("[data-alert-rule-card]")?.remove();
    };
  });
  if (alertForm) {
    alertForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const cards = Array.from(document.querySelectorAll("[data-alert-rule-card]"));
      const alertRules = cards.flatMap((card) => {
        return buildAlertRules({
          route: String(card.querySelector('[name=\"route\"]')?.value || "").trim(),
          keyword: String(card.querySelector('[name=\"keyword\"]')?.value || "").trim(),
          domain: String(card.querySelector('[name=\"domain\"]')?.value || "").trim(),
          minScore: Number(card.querySelector('[name=\"min_score\"]')?.value || 0),
          minConfidence: Number(card.querySelector('[name=\"min_confidence\"]')?.value || 0),
        });
      });
      const payload = {
        alert_rules: alertRules,
      };
      if (!payload.alert_rules.length) {
        showToast(copy("Provide at least one route, keyword, domain, or threshold across the rule set.", "请至少提供一个路由、关键词、域名或阈值。"), "error");
        return;
      }
      try {
        await api(`/api/watches/${watch.id}/alert-rules`, {
          method: "PUT",
          payload,
        });
        await refreshBoard();
      } catch (error) {
        reportError(error, copy("Update alert rules", "更新告警规则"));
      }
    });
  }

  const clearButton = document.getElementById("watch-alert-clear");
  if (clearButton) {
    clearButton.addEventListener("click", async () => {
      try {
        await api(`/api/watches/${watch.id}/alert-rules`, {
          method: "PUT",
          payload: { alert_rules: [] },
        });
        await refreshBoard();
      } catch (error) {
        reportError(error, copy("Clear alert rules", "清空告警规则"));
      }
    });
  }

  root.querySelectorAll("[data-watch-edit]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await editMissionInCreateWatch(String(button.dataset.watchEdit || "").trim());
      } catch (error) {
        reportError(error, copy("Edit mission", "编辑任务"));
      } finally {
        button.disabled = false;
      }
    });
  });
  wireLifecycleGuideActions(root);
  renderTopbarContext();
}

function renderAlerts() {
  const root = $("alert-list");
  if (state.loading.board && !state.alerts.length) {
    root.innerHTML = [skeletonCard(3), skeletonCard(3)].join("");
    return;
  }
  if (!state.alerts.length) {
    root.innerHTML = `<div class="empty">${copy("No alert event stored.", "当前没有告警事件。")}</div>`;
    return;
  }
  root.innerHTML = state.alerts.map((alert) => `
    <div class="card">
      <div class="card-top">
        <div>
          <h3 class="card-title">${alert.mission_name}</h3>
          <div class="meta">
            <span>${alert.rule_name}</span>
            <span>${alert.created_at || "-"}</span>
          </div>
        </div>
        <span class="chip hot">${(alert.delivered_channels || ["json"]).join(",")}</span>
      </div>
      <div class="panel-sub">${alert.summary || ""}</div>
    </div>
  `).join("");
}

async function submitRouteDeck(form) {
  const draft = collectRouteDraft(form);
  state.routeDraft = draft;
  const editingId = normalizeRouteName(state.routeEditingId);
  let headers = null;
  try {
    headers = parseRouteHeaders(draft.headers_json);
  } catch (error) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Route draft is blocked by header formatting", "路由草稿被请求头格式阻塞"),
      copy: error.message,
      actionHierarchy: {
        primary: {
          label: copy("Fix Route Headers", "修正路由请求头"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "headers_json" },
        },
      },
    });
    showToast(error.message, "error");
    focusRouteDeck("headers_json");
    return;
  }
  if (!draft.name.trim()) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Route draft still needs a name", "路由草稿仍然缺少名称"),
      copy: copy("Give the route a stable name before it can become a delivery surface.", "先给路由一个稳定名称，它才能成为可复用的交付目标。"),
      actionHierarchy: {
        primary: {
          label: copy("Complete Route Draft", "继续补全路由草稿"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "name" },
        },
      },
    });
    showToast(copy("Provide a route name before saving.", "保存前请先填写路由名称。"), "error");
    focusRouteDeck("name");
    return;
  }
  if (draft.channel === "webhook" && !draft.webhook_url.trim()) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Webhook route needs a destination", "Webhook 路由仍缺少目标地址"),
      copy: copy("Provide the webhook URL before this route can own delivery traffic.", "补上 webhook URL 后，这条路由才能承接交付流量。"),
      actionHierarchy: {
        primary: {
          label: copy("Add Webhook URL", "填写 Webhook URL"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "webhook_url" },
        },
      },
    });
    showToast(copy("Webhook routes need a webhook URL.", "Webhook 路由需要填写 webhook URL。"), "error");
    focusRouteDeck("webhook_url");
    return;
  }
  if (draft.channel === "feishu" && !draft.feishu_webhook.trim()) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Feishu route needs a destination", "飞书路由仍缺少目标地址"),
      copy: copy("Provide the Feishu webhook URL before this route can deliver alerts.", "补上飞书 webhook URL 后，这条路由才能投递告警。"),
      actionHierarchy: {
        primary: {
          label: copy("Add Feishu URL", "填写飞书地址"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "feishu_webhook" },
        },
      },
    });
    showToast(copy("Feishu routes need a webhook URL.", "飞书路由需要填写 webhook URL。"), "error");
    focusRouteDeck("feishu_webhook");
    return;
  }
  if (draft.channel === "telegram" && !draft.telegram_chat_id.trim()) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Telegram route needs a chat target", "Telegram 路由仍缺少会话目标"),
      copy: copy("Provide the chat ID before this route can deliver Telegram messages.", "补上 chat ID 后，这条路由才能投递 Telegram 消息。"),
      actionHierarchy: {
        primary: {
          label: copy("Add Chat ID", "填写 Chat ID"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "telegram_chat_id" },
        },
      },
    });
    showToast(copy("Telegram routes need a chat ID.", "Telegram 路由需要填写 chat ID。"), "error");
    focusRouteDeck("telegram_chat_id");
    return;
  }
  if (draft.channel === "telegram" && !editingId && !draft.telegram_bot_token.trim()) {
    setStageFeedback("deliver", {
      kind: "blocked",
      title: copy("Telegram route needs a bot token", "Telegram 路由仍缺少机器人 token"),
      copy: copy("A new Telegram route needs the bot token before it can become reusable.", "新建 Telegram 路由前必须提供 bot token，它才能成为可复用目标。"),
      actionHierarchy: {
        primary: {
          label: copy("Add Bot Token", "填写 Bot Token"),
          attrs: { "data-empty-focus": "route", "data-empty-field": "telegram_bot_token" },
        },
      },
    });
    showToast(copy("Telegram routes need a bot token when created.", "创建 Telegram 路由时必须填写 bot token。"), "error");
    focusRouteDeck("telegram_bot_token");
    return;
  }
  let timeoutSeconds = null;
  if (draft.timeout_seconds.trim()) {
    timeoutSeconds = Number(draft.timeout_seconds);
    if (!(timeoutSeconds > 0)) {
      setStageFeedback("deliver", {
        kind: "blocked",
        title: copy("Route timeout is invalid", "路由超时时间无效"),
        copy: copy("Set the timeout to a value greater than zero before saving the route.", "保存路由前，请把超时时间设为大于零的值。"),
        actionHierarchy: {
          primary: {
            label: copy("Fix Timeout", "修正超时时间"),
            attrs: { "data-empty-focus": "route", "data-empty-field": "timeout_seconds" },
          },
        },
      });
      showToast(copy("Timeout must be greater than 0.", "超时时间必须大于 0。"), "error");
      focusRouteDeck("timeout_seconds");
      return;
    }
  }

  const payload = {
    channel: draft.channel,
  };
  if (draft.description.trim()) {
    payload.description = draft.description.trim();
  }
  if (timeoutSeconds !== null) {
    payload.timeout_seconds = timeoutSeconds;
  }
  if (draft.channel === "webhook") {
    payload.webhook_url = draft.webhook_url.trim();
    if (draft.authorization.trim()) {
      payload.authorization = draft.authorization.trim();
    }
    if (headers && Object.keys(headers).length) {
      payload.headers = headers;
    }
  }
  if (draft.channel === "feishu") {
    payload.feishu_webhook = draft.feishu_webhook.trim();
  }
  if (draft.channel === "telegram") {
    payload.telegram_chat_id = draft.telegram_chat_id.trim();
    if (draft.telegram_bot_token.trim()) {
      payload.telegram_bot_token = draft.telegram_bot_token.trim();
    }
  }

  const submitButton = form?.querySelector("button[type='submit']");
  if (submitButton) {
    submitButton.disabled = true;
  }
  try {
    if (editingId) {
      const updated = await api(`/api/alert-routes/${editingId}`, {
        method: "PUT",
        payload,
      });
      setContextRouteName(normalizeRouteName(updated.name), "section-ops");
      state.routeAdvancedOpen = null;
      setRouteDraft(defaultRouteDraft(), "");
      pushActionEntry({
        kind: copy("route update", "路由修改"),
        label: state.language === "zh" ? `已更新路由：${updated.name}` : `Updated route: ${updated.name}`,
        detail: state.language === "zh"
          ? `通道：${routeChannelLabel(updated.channel)}`
          : `Channel: ${routeChannelLabel(updated.channel)}`,
      });
      await refreshBoard();
      setStageFeedback("deliver", {
        kind: "completion",
        title: state.language === "zh" ? `路由已更新：${updated.name}` : `Route updated: ${updated.name}`,
        copy: copy(
          "The delivery lane now exposes the updated route posture. Reuse it from monitoring when missions need downstream delivery.",
          "交付阶段现在已经反映更新后的路由姿态；当监测任务需要下游交付时，可以直接复用它。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
          secondary: [
            {
              label: copy("Use In Mission Draft", "用于任务草稿"),
              attrs: { "data-empty-focus": "mission", "data-empty-field": "route" },
            },
          ],
        },
      });
      showToast(
        state.language === "zh" ? `路由已更新：${updated.name}` : `Route updated: ${updated.name}`,
        "success",
      );
      return;
    }
    const created = await api("/api/alert-routes", {
      method: "POST",
      payload: { name: draft.name.trim(), ...payload },
    });
    setContextRouteName(normalizeRouteName(created.name), "section-ops");
    const nextChannel = draft.channel;
    state.routeAdvancedOpen = null;
    setRouteDraft({ ...defaultRouteDraft(), channel: nextChannel }, "");
    pushActionEntry({
      kind: copy("route create", "路由创建"),
      label: state.language === "zh" ? `已创建路由：${created.name}` : `Created route: ${created.name}`,
      detail: copy("The route is now available in mission alert rules and route quick-picks.", "该路由现在已可用于任务告警规则和快捷选择。"),
      undoLabel: copy("Delete route", "删除路由"),
      undo: async () => {
        await api(`/api/alert-routes/${created.name}`, { method: "DELETE" });
        await refreshBoard();
        showToast(
          state.language === "zh" ? `已删除路由：${created.name}` : `Route deleted: ${created.name}`,
          "success",
        );
      },
    });
    await refreshBoard();
    setStageFeedback("deliver", {
      kind: "completion",
      title: state.language === "zh" ? `路由已创建：${created.name}` : `Route created: ${created.name}`,
      copy: copy(
        "The route now belongs to the delivery lane and can be attached from Mission Intake or Cockpit.",
        "这条路由现在已经进入交付阶段，可以直接从任务录入区或驾驶舱里挂接。"
      ),
      actionHierarchy: {
        primary: {
          label: copy("Use In Mission Draft", "用于任务草稿"),
          attrs: { "data-empty-focus": "mission", "data-empty-field": "route" },
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
      state.language === "zh" ? `路由已创建：${created.name}` : `Route created: ${created.name}`,
      "success",
    );
  } catch (error) {
    reportError(error, copy("Save route", "保存路由"));
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}

async function deleteRouteFromBoard(identifier) {
  const normalized = normalizeRouteName(identifier);
  if (!normalized) {
    return;
  }
  const usageNames = getRouteUsageNames(normalized);
  const confirmation = usageNames.length
    ? copy(
        `Delete route ${normalized}? It is referenced by ${usageNames.length} mission(s): ${usageNames.slice(0, 3).join(", ")}.`,
        `确认删除路由 ${normalized}？它仍被 ${usageNames.length} 个任务引用：${usageNames.slice(0, 3).join("、")}。`,
      )
    : copy(
        `Delete route ${normalized}?`,
        `确认删除路由 ${normalized}？`,
      );
  if (!window.confirm(confirmation)) {
    return;
  }
  try {
    const deleted = await api(`/api/alert-routes/${normalized}`, { method: "DELETE" });
    if (normalizeRouteName(state.contextRouteName) === normalized) {
      setContextRouteName("", "");
    }
    if (normalizeRouteName(state.routeEditingId) === normalized) {
      state.routeAdvancedOpen = null;
      setRouteDraft(defaultRouteDraft(), "");
    }
    const createDraftRoute = normalizeRouteName(state.createWatchDraft?.route);
    if (createDraftRoute === normalized) {
      updateCreateWatchDraft({ route: "" });
    }
    pushActionEntry({
      kind: copy("route delete", "路由删除"),
      label: state.language === "zh" ? `已删除路由：${deleted.name}` : `Deleted route: ${deleted.name}`,
      detail: usageNames.length
        ? copy("This route was still referenced by one or more missions. Review mission alert rules before the next run.", "该路由此前仍被任务引用，请在下一次执行前检查相关任务的告警规则。")
        : copy("Unused route removed from the delivery surface.", "未使用路由已从交付面移除。"),
    });
    await refreshBoard();
    setStageFeedback("deliver", usageNames.length
      ? {
          kind: "warning",
          title: state.language === "zh" ? `路由已删除：${deleted.name}` : `Route deleted: ${deleted.name}`,
          copy: copy(
            "The deleted route was still referenced by missions. Review mission alert rules before the next delivery run.",
            "被删除的路由此前仍被任务引用；请在下一次交付前检查相关任务的告警规则。"
          ),
          actionHierarchy: {
            primary: {
              label: copy("Review Mission Drafts", "检查任务草稿"),
              attrs: { "data-empty-focus": "mission", "data-empty-field": "route" },
            },
            secondary: [
              {
                label: copy("Open Delivery Lane", "打开交付工作线"),
                attrs: { "data-empty-jump": "section-ops" },
              },
            ],
          },
        }
      : {
          kind: "completion",
          title: state.language === "zh" ? `路由已删除：${deleted.name}` : `Route deleted: ${deleted.name}`,
          copy: copy(
            "The unused route has been removed from the delivery lane.",
            "这条未使用路由已经从交付阶段移除。"
          ),
          actionHierarchy: {
            primary: {
              label: copy("Create Route", "创建路由"),
              attrs: { "data-empty-focus": "route", "data-empty-field": "name" },
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
      state.language === "zh" ? `路由已删除：${deleted.name}` : `Route deleted: ${deleted.name}`,
      "success",
    );
  } catch (error) {
    reportError(error, copy("Delete route", "删除路由"));
  }
}

function wireRouteSurfaceActions(root) {
  if (!root) {
    return;
  }
  root.querySelectorAll("[data-route-edit]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await editRouteInDeck(String(button.dataset.routeEdit || ""));
      } catch (error) {
        reportError(error, copy("Edit route", "编辑路由"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelectorAll("[data-route-attach]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await applyRouteToMissionDraft(String(button.dataset.routeAttach || ""));
      } catch (error) {
        reportError(error, copy("Apply route", "应用路由"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelectorAll("[data-route-delete]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await deleteRouteFromBoard(String(button.dataset.routeDelete || ""));
      } finally {
        button.disabled = false;
      }
    });
  });
}

function renderRouteDeck() {
  const root = $("route-deck");
  if (!root) {
    return;
  }
  const draft = normalizeRouteDraft(state.routeDraft || defaultRouteDraft());
  const editingId = normalizeRouteName(state.routeEditingId);
  const editing = Boolean(editingId);
  const advancedOpen = isRouteAdvancedOpen(draft);
  const routeName = normalizeRouteName(editing ? editingId : draft.name);
  const usageCount = routeName ? getRouteUsageCount(routeName) : 0;
  const health = routeName ? getRouteHealthRow(routeName) : null;
  const routeGuidanceBlock = buildRouteGuidanceSurface({ draft, editing, health, usageCount });
  const advancedChips = [];
  if (draft.description.trim()) {
    advancedChips.push(copy("description added", "已补充说明"));
  }
  if (draft.authorization.trim()) {
    advancedChips.push(copy("auth attached", "已附带认证"));
  }
  if (draft.headers_json.trim()) {
    advancedChips.push(copy("custom headers", "自定义请求头"));
  }
  if (draft.timeout_seconds.trim()) {
    advancedChips.push(phrase("timeout {value}s", "超时 {value} 秒", { value: draft.timeout_seconds.trim() }));
  }
  if (!advancedChips.length) {
    advancedChips.push(copy("No advanced control yet", "当前没有高级设置"));
  }

  root.innerHTML = `
    <form id="route-form">
      <div class="card-top">
        <div>
          <div class="mono">${editing ? copy("route edit", "路由编辑") : copy("route create", "路由创建")}</div>
          <h3 class="card-title" style="margin-top:10px;">${editing ? escapeHtml(draft.name) : copy("Create Named Route", "创建命名路由")}</h3>
        </div>
        <div style="display:grid; gap:6px; justify-items:end;">
          <span class="chip ${health && health.status === "healthy" ? "ok" : health && health.status && health.status !== "idle" ? "hot" : ""}">${health ? localizeWord(health.status || "idle") : localizeWord(editing ? "editable" : "new")}</span>
          <span class="chip">${copy("used", "已引用")}=${usageCount}</span>
        </div>
      </div>
      <div class="panel-sub">${
        editing
          ? copy("Update the sink in place. Route name stays fixed so existing mission rules do not drift.", "原位更新交付路由。路由名称保持不变，避免已有任务规则漂移。")
          : copy("Add a reusable sink once, then pick it from mission alert rules and quick route chips.", "先把可复用的交付路由配置好，后续在任务告警规则和快捷路由里直接选择。")
      }</div>
      <div class="ui-segment ui-segment-wrap" style="margin-top:4px;" role="group" aria-label="${escapeHtml(copy("Route channel selection", "路由通道选择"))}">
        ${
          routeChannelOptions.map((option) => `
            <button
              class="ui-segment-button ${draft.channel === option.value ? "active" : ""}"
              type="button"
              data-route-channel="${option.value}"
              aria-pressed="${draft.channel === option.value ? "true" : "false"}"
            >${escapeHtml(copy(option.label, option.zhLabel || option.label))}</button>
          `).join("")
        }
      </div>
      <div class="field-grid" style="margin-top:2px;">
        <label>${copy("Route Name", "路由名称")}<input name="name" placeholder="ops-webhook" value="${escapeHtml(draft.name)}" ${editing ? "readonly" : ""}><span class="field-hint">${editing ? copy("Name is fixed during edit so existing mission rules keep resolving.", "编辑时名称固定，避免已有任务规则失效。") : copy("Use a short reusable id, such as ops-webhook or exec-telegram.", "建议使用可复用的简短 ID，例如 ops-webhook 或 exec-telegram。")}</span></label>
        <label>${copy("Channel", "通道")}<input name="channel" value="${escapeHtml(routeChannelLabel(draft.channel))}" readonly><span class="field-hint">${copy("Change channel with the route type chips above.", "通过上方的路由类型按钮切换通道。")}</span></label>
      </div>
      <div class="field-grid">
        ${
          draft.channel === "webhook"
            ? `
                <label>${copy("Webhook URL", "Webhook URL")}<input name="webhook_url" placeholder="https://hooks.example.com/ops" value="${escapeHtml(draft.webhook_url)}"><span class="field-hint">${copy("Paste the receiver endpoint once, then reuse the route everywhere else.", "把接收端地址配置一次，后续在其他地方直接复用。")}</span></label>
                <label>${copy("Destination Preview", "目标预览")}<input value="${escapeHtml(draft.webhook_url.trim() ? summarizeUrlHost(draft.webhook_url) : copy("Waiting for URL", "等待输入 URL"))}" readonly><span class="field-hint">${copy("Only the host preview is shown here to keep scanning fast.", "这里只显示主机预览，方便快速扫描。")}</span></label>
              `
            : draft.channel === "feishu"
              ? `
                <label>${copy("Feishu Webhook", "飞书 Webhook")}<input name="feishu_webhook" placeholder="https://open.feishu.cn/..." value="${escapeHtml(draft.feishu_webhook)}"><span class="field-hint">${copy("Use the bot webhook issued by the target Feishu group.", "填写目标飞书群机器人提供的 webhook。")}</span></label>
                <label>${copy("Destination Preview", "目标预览")}<input value="${escapeHtml(draft.feishu_webhook.trim() ? summarizeUrlHost(draft.feishu_webhook) : copy("Waiting for URL", "等待输入 URL"))}" readonly><span class="field-hint">${copy("Preview keeps the card readable without exposing the full URL at a glance.", "保留预览而不是完整地址，列表浏览时更轻量。")}</span></label>
              `
              : draft.channel === "telegram"
                ? `
                  <label>${copy("Telegram Chat ID", "Telegram Chat ID")}<input name="telegram_chat_id" placeholder="-1001234567890" value="${escapeHtml(draft.telegram_chat_id)}"><span class="field-hint">${copy("The chat id remains visible so you can confirm the destination quickly.", "保留 chat id 可见，便于快速确认目标会话。")}</span></label>
                  <label>${copy("Bot Token", "Bot Token")}<input name="telegram_bot_token" type="password" placeholder="${editing ? copy("Leave blank to keep the current token", "留空则保留当前 token") : "123456:ABCDEF"}" value="${escapeHtml(draft.telegram_bot_token)}"><span class="field-hint">${editing ? copy("Leave blank to keep the existing bot token.", "留空会保留当前 bot token。") : copy("Required when the route is created.", "创建路由时必须填写。")}</span></label>
                `
                : `
                  <label>${copy("Markdown Delivery", "Markdown 交付")}<input value="${copy("Append alert summaries to the local markdown log.", "把告警摘要追加到本地 Markdown 日志。")}" readonly><span class="field-hint">${copy("Use this when operators want a file-backed trail with zero external dependency.", "当你需要零外部依赖的文件留痕时，用这个通道。")}</span></label>
                  <label>${copy("Destination Preview", "目标预览")}<input value="${copy("alerts.md append target", "alerts.md 追加目标")}" readonly><span class="field-hint">${copy("Markdown routes need no extra endpoint fields.", "Markdown 路由不需要额外的目标配置字段。")}</span></label>
                `
        }
      </div>
      <div class="deck-mode-strip">
        <div class="deck-mode-head">
          <div>
            <div class="mono">${copy("advanced controls", "高级设置")}</div>
            <div class="panel-sub">${copy("Keep advanced fields closed until you need auth headers, timeout control, or delivery notes.", "只有在需要认证、超时控制或交付备注时，再展开高级设置。")}</div>
          </div>
          <button class="btn-secondary advanced-toggle" id="route-advanced-toggle" type="button" aria-expanded="${String(advancedOpen)}">${advancedOpen ? copy("Hide Advanced", "收起高级设置") : copy("Show Advanced", "展开高级设置")}</button>
        </div>
        <div class="chip-row advanced-summary">${advancedChips.map((chip) => `<span class="chip">${escapeHtml(chip)}</span>`).join("")}</div>
        <div class="deck-advanced-panel ${advancedOpen ? "" : "collapsed"}" aria-hidden="${String(!advancedOpen)}">
          <div class="field-grid">
            <label>${copy("Description", "说明")}<input name="description" placeholder="${copy("Primary route for on-call ops", "值班运维主路由")}" value="${escapeHtml(draft.description)}"><span class="field-hint">${copy("Use one short note so operators know why this sink exists.", "补一句简短说明，让操作者知道这个路由的用途。")}</span></label>
            <label>${copy("Timeout Seconds", "超时秒数")}<input name="timeout_seconds" inputmode="decimal" placeholder="10" value="${escapeHtml(draft.timeout_seconds)}"><span class="field-hint">${copy("Optional override for slower receivers.", "当接收端偏慢时，可以单独覆盖超时时间。")}</span></label>
          </div>
          ${
            draft.channel === "webhook"
              ? `
                  <div class="field-grid">
                    <label>${copy("Authorization Header", "Authorization 请求头")}<input name="authorization" type="password" placeholder="${editing ? copy("Leave blank to keep current auth", "留空则保留当前认证") : "Bearer ..."}" value="${escapeHtml(draft.authorization)}"><span class="field-hint">${editing ? copy("Leave blank to keep the current secret.", "留空会保留当前密钥。") : copy("Optional bearer token or pre-shared auth header.", "可选的 bearer token 或预共享认证头。")}</span></label>
                    <label>${copy("Custom Headers JSON", "自定义请求头 JSON")}<textarea name="headers_json" rows="4" placeholder='{"X-Env":"prod"}'>${escapeHtml(draft.headers_json)}</textarea><span class="field-hint">${copy("Only include extra headers that are not already captured above.", "这里只填写上方未覆盖的额外请求头。")}</span></label>
                  </div>
                `
              : ""
          }
        </div>
      </div>
      <div class="toolbar">
        <button class="btn-primary" id="route-submit" type="submit">${editing ? copy("Save Route", "保存路由") : copy("Create Route", "创建路由")}</button>
        <button class="btn-secondary" id="route-clear" type="button">${editing ? copy("Cancel Edit", "取消编辑") : copy("Reset Draft", "清空草稿")}</button>
        ${
          editing
            ? `<button class="btn-secondary" id="route-apply" type="button">${copy("Use In Mission", "用于任务草稿")}</button>`
            : ""
        }
      </div>
    </form>
    ${routeGuidanceBlock}
  `;

  const form = $("route-form");
  form?.addEventListener("input", () => {
    state.routeDraft = collectRouteDraft(form);
  });
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitRouteDeck(form);
  });
  $("route-advanced-toggle")?.addEventListener("click", () => {
    state.routeDraft = collectRouteDraft(form);
    state.routeAdvancedOpen = !isRouteAdvancedOpen(state.routeDraft || defaultRouteDraft());
    renderRouteDeck();
  });
  root.querySelectorAll("[data-route-channel]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextChannel = String(button.dataset.routeChannel || "webhook").trim().toLowerCase();
      state.routeDraft = {
        ...collectRouteDraft(form),
        channel: nextChannel,
      };
      if (nextChannel !== "markdown") {
        state.routeAdvancedOpen = true;
      }
      renderRouteDeck();
    });
  });
  $("route-clear")?.addEventListener("click", () => {
    const wasEditing = Boolean(normalizeRouteName(state.routeEditingId));
    state.routeAdvancedOpen = null;
    setRouteDraft(defaultRouteDraft(), "");
    showToast(
      wasEditing
        ? copy("Route edit cancelled", "已取消路由编辑")
        : copy("Route draft cleared", "已清空路由草稿"),
      "success",
    );
  });
  root.querySelectorAll("[data-route-apply], #route-apply").forEach((button) => {
    button.addEventListener("click", async () => {
      await applyRouteToMissionDraft(String(button.dataset.routeApply || draft.name || "").trim());
    });
  });
  wireLifecycleGuideActions(root);
}

function renderRouteHealth() {
  const root = $("route-health");
  if (state.loading.board && !state.routeHealth.length) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
    return;
  }
  if (!state.routeHealth.length) {
    root.innerHTML = `
      ${renderLifecycleGuideCard({
        title: copy("Delivery health appears after one named-route alert lands", "至少触发一次命名路由告警后，才会看到交付健康"),
        summary: copy(
          "Create a named route, attach it from Mission Intake or Cockpit alert rules, then let one alert flow through so this panel can report delivery quality.",
          "先创建命名路由，再从任务创建区或任务详情的告警规则里把它接上，等至少一条告警流过后，这里就会开始显示交付质量。"
        ),
        steps: [
          {
            title: copy("Create Route", "创建路由"),
            copy: copy("Route Manager stores reusable delivery sinks inside the browser shell.", "路由管理会把可复用的交付目标直接保存在浏览器工作流里。"),
          },
          {
            title: copy("Attach To Mission", "绑定到任务"),
            copy: copy("Use Mission Intake or Cockpit alert rules to attach the named route.", "在任务创建区或任务详情的告警规则里绑定这个命名路由。"),
          },
          {
            title: copy("Trigger Alert", "触发告警"),
            copy: copy("One route-backed alert is enough to seed health and timeline facts.", "只要有一次带路由的告警，就足以开始沉淀健康和时间线事实。"),
          },
        ],
        actions: [
          { label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true },
          { label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" },
        ],
      })}
      <div class="empty">${copy("No route health signal yet. Trigger named-route alerts to populate delivery quality.", "当前还没有路由健康信号。触发命名路由告警后会出现交付质量数据。")}</div>`;
    wireLifecycleGuideActions(root);
    return;
  }
  root.innerHTML = state.routeHealth.map((route) => {
    const usageCount = Array.isArray(route.mission_ids) && route.mission_ids.length
      ? route.mission_ids.length
      : getRouteUsageCount(route.name);
    const actionHierarchy = getRouteCardActionHierarchy(route, route, usageCount);
    return `
      <div class="card">
        <div class="card-top">
          <div>
            <h3 class="card-title">${route.name}</h3>
            <div class="meta">
              <span>${copy("channel", "通道")}=${routeChannelLabel(route.channel || "unknown")}</span>
              <span>${copy("status", "状态")}=${localizeWord(route.status || "idle")}</span>
              <span>${copy("rate", "成功率")}=${formatRate(route.success_rate)}</span>
            </div>
          </div>
          <span class="chip ${route.status === "healthy" ? "ok" : route.status === "idle" ? "" : "hot"}">${localizeWord(route.status || "idle")}</span>
        </div>
        <div class="meta">
          <span>${copy("events", "事件")}=${route.event_count || 0}</span>
          <span>${copy("delivered", "送达")}=${route.delivered_count || 0}</span>
          <span>${copy("failed", "失败")}=${route.failure_count || 0}</span>
          <span>${copy("last", "最近")}=${route.last_event_at || "-"}</span>
        </div>
        <div class="panel-sub">${route.last_error || route.last_summary || copy("No recent route delivery attempt recorded.", "近期没有记录到路由投递尝试。")}</div>
        ${renderCardActionHierarchy(actionHierarchy)}
      </div>
    `;
  }).join("");
  wireRouteSurfaceActions(root);
}

function renderRoutes() {
  const root = $("route-list");
  renderRouteDeck();
  if (state.loading.board && !state.routes.length) {
    root.innerHTML = skeletonCard(3);
    return;
  }
  const searchValue = String(state.routeSearch || "");
  const searchQuery = searchValue.trim().toLowerCase();
  const filteredRoutes = state.routes.filter((route) => {
    if (!searchQuery) {
      return true;
    }
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
  });
  const toolbox = `
    <div class="card section-toolbox">
      <div class="section-toolbox-head">
        <div>
          <div class="mono">${copy("route search", "路由搜索")}</div>
          <div class="panel-sub">${copy("Search by name, channel, destination, or attached mission before you edit or delete a route.", "可按名称、通道、目标地址或引用任务快速定位路由。")}</div>
        </div>
        <div class="section-toolbox-meta">
          <span class="chip">${copy("shown", "显示")}=${filteredRoutes.length}</span>
          <span class="chip">${copy("total", "总数")}=${state.routes.length}</span>
        </div>
      </div>
      <div class="search-shell">
        <input type="search" value="${escapeHtml(searchValue)}" data-route-search placeholder="${copy("Search routes", "搜索路由")}">
        <button class="btn-secondary" type="button" data-route-search-clear ${searchValue.trim() ? "" : "disabled"}>${copy("Clear", "清空")}</button>
      </div>
    </div>
  `;
  if (!filteredRoutes.length) {
    root.innerHTML = `${toolbox}${
      state.routes.length
        ? ""
        : renderLifecycleGuideCard({
            title: copy("Create one reusable route before missions need delivery", "在任务需要交付前，先准备一个可复用路由"),
            summary: copy(
              "Routes are browser-managed delivery sinks. Create one here once, then attach it from Mission Intake or Cockpit alert rules instead of retyping destination details each time.",
              "路由是浏览器内管理的交付目标。先在这里建一次，后续在任务创建区或任务详情的告警规则里直接绑定，不必每次重复填写目标信息。"
            ),
            steps: [
              {
                title: copy("Create Named Sink", "创建命名目标"),
                copy: copy("Give the route a stable name such as ops-webhook or exec-telegram.", "先给路由一个稳定的名字，比如 ops-webhook 或 exec-telegram。"),
              },
              {
                title: copy("Attach In Mission", "在任务里绑定"),
                copy: copy("Mission Intake and Cockpit reuse the route through Alert Route fields.", "任务创建区和任务详情会通过“告警路由”字段复用它。"),
              },
              {
                title: copy("Monitor Health", "观察健康状态"),
                copy: copy("Distribution Health and Alert Stream show whether downstream delivery is behaving.", "分发健康和告警动态会继续告诉你下游投递是否正常。"),
              },
            ],
            actions: [
              { label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true },
              { label: copy("Focus Mission Draft", "聚焦任务草稿"), focus: "mission", field: "route" },
            ],
          })
    }<div class="empty">${state.routes.length ? copy("No route matched the current search.", "没有路由匹配当前搜索。") : copy("No named alert route configured yet. Start with one route so mission alerts can attach to a reusable sink.", "当前还没有配置命名告警路由。先创建一个路由，任务告警才能直接复用。")}</div>`;
    wireLifecycleGuideActions(root);
    root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {
      state.routeSearch = event.target.value;
      renderRoutes();
    });
    root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {
      state.routeSearch = "";
      renderRoutes();
    });
    return;
  }
  root.innerHTML = `${toolbox}${filteredRoutes.map((route) => {
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
            <h3 class="card-title">${escapeHtml(route.name || "unnamed-route")}</h3>
            <div class="meta">
              <span>${copy("channel", "通道")}=${escapeHtml(routeChannelLabel(route.channel))}</span>
              <span>${copy("used", "已引用")}=${usageCount}</span>
              <span>${copy("status", "状态")}=${escapeHtml(localizeWord(health?.status || "idle"))}</span>
            </div>
          </div>
          <div style="display:grid; gap:6px; justify-items:end;">
            <span class="chip ${healthTone}">${escapeHtml(localizeWord(health?.status || "idle"))}</span>
            <span class="chip">${escapeHtml(routeChannelLabel(route.channel))}</span>
          </div>
        </div>
        <div class="panel-sub">${escapeHtml(route.description || destination)}</div>
        <div class="meta">
          <span>${copy("destination", "目标")}=${escapeHtml(destination)}</span>
          <span>${copy("rate", "成功率")}=${formatRate(health?.success_rate)}</span>
          <span>${copy("last", "最近")}=${escapeHtml(health?.last_event_at || "-")}</span>
        </div>
        ${
          usageCount
            ? `<div class="panel-sub">${copy("Used by", "正在被这些任务引用")}: ${escapeHtml(usageNames.slice(0, 3).join(", "))}${usageCount > 3 ? " ..." : ""}</div>`
            : ""
        }
        ${renderCardActionHierarchy(actionHierarchy)}
      </div>
    `;
  }).join("")}`;
  root.querySelector("[data-route-search]")?.addEventListener("input", (event) => {
    state.routeSearch = event.target.value;
    renderRoutes();
  });
  root.querySelector("[data-route-search-clear]")?.addEventListener("click", () => {
    state.routeSearch = "";
    renderRoutes();
  });
  wireRouteSurfaceActions(root);
}

function renderDeliveryWorkspace() {
  const root = $("delivery-workspace-shell");
  if (!root) {
    return;
  }
  syncDeliveryDraft();
  syncDigestProfileDraft();
  syncDeliverySelectionState();
  if (state.loading.board && !state.deliverySubscriptions.length) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4)].join("");
    return;
  }

  const draft = normalizeDeliveryDraft(state.deliveryDraft || defaultDeliveryDraft());
  state.deliveryDraft = draft;
  const digestConsole = state.digestConsole && typeof state.digestConsole === "object" ? state.digestConsole : {};
  const digestProjection = digestConsole.prepared_payload && typeof digestConsole.prepared_payload === "object"
    ? digestConsole.prepared_payload
    : {};
  const digestProfileShell = digestConsole.profile && typeof digestConsole.profile === "object"
    ? digestConsole.profile
    : {};
  const digestProfileDraft = normalizeDigestProfileDraft(state.digestProfileDraft || defaultDigestProfileDraft());
  state.digestProfileDraft = digestProfileDraft;
  const digestBundle = digestProjection.content?.feed_bundle && typeof digestProjection.content.feed_bundle === "object"
    ? digestProjection.content.feed_bundle
    : {};
  const digestPromptConfig = digestProjection.prompts && typeof digestProjection.prompts === "object"
    ? digestProjection.prompts
    : {};
  const digestStats = digestProjection.stats && typeof digestProjection.stats === "object"
    ? digestProjection.stats
    : {};
  const digestProfile = digestProjection.config?.digest_profile && typeof digestProjection.config.digest_profile === "object"
    ? digestProjection.config.digest_profile
    : digestProfileDraft;
  const digestTarget = digestProfile.default_delivery_target && typeof digestProfile.default_delivery_target === "object"
    ? digestProfile.default_delivery_target
    : {};
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
        <div class="mini-item">${row.route_label || row.route_name || "-"} | ${localizeWord(row.status || "pending")} | ${row.package_profile_id || copy("default", "默认")}</div>
        <div class="panel-sub">${row.error || row.package_id || copy("No package audit detail.", "当前没有包审计详情。")}</div>
      `).join("")
    : `<div class="empty">${copy("No dispatch audit recorded for the current selection.", "当前选中的订阅还没有 dispatch 审计记录。")}</div>`;
  const inventoryRows = state.deliverySubscriptions.length
    ? state.deliverySubscriptions.map((subscription) => {
        const subscriptionId = String(subscription.id || "").trim();
        const isSelected = subscriptionId === selectedSubscriptionId;
        const routeNames = Array.isArray(subscription.route_names) ? subscription.route_names : [];
        const auditCount = getDeliveryDispatchRowsForSubscription(subscriptionId).length;
        return `
          <div class="card">
            <div class="card-top">
              <div>
                <h3 class="card-title">${escapeHtml(summarizeDeliverySubject(subscription) || subscriptionId)}</h3>
                <div class="meta">
                  <span>${formatDeliverySubjectKind(subscription.subject_kind)}</span>
                  <span>${formatDeliveryOutputKind(subscription.output_kind)}</span>
                  <span>${localizeWord(subscription.delivery_mode || "pull")}</span>
                </div>
              </div>
              <span class="chip ${reportStatusTone(subscription.status)}">${escapeHtml(localizeWord(subscription.status || "active"))}</span>
            </div>
            <div class="panel-sub">${escapeHtml(subscription.subject_ref || copy("No subject ref.", "没有 subject ref。"))}</div>
            <div class="meta">
              <span>${copy("routes", "路由")}=${routeNames.length ? routeNames.join(", ") : copy("none", "无")}</span>
              <span>${copy("cursor", "游标")}=${subscription.cursor_or_since || "-"}</span>
              <span>${copy("audit", "审计")}=${auditCount}</span>
            </div>
            <div class="actions">
              <button class="btn-secondary" type="button" data-delivery-select="${escapeHtml(subscriptionId)}">${isSelected ? copy("Inspecting", "查看中") : copy("Inspect", "查看")}</button>
              <button class="btn-secondary" type="button" data-delivery-toggle-status="${escapeHtml(subscriptionId)}" data-next-status="${subscription.status === "active" ? "paused" : "active"}">${subscription.status === "active" ? copy("Pause", "暂停") : copy("Resume", "恢复")}</button>
              <button class="btn-secondary" type="button" data-delivery-delete="${escapeHtml(subscriptionId)}">${copy("Delete", "删除")}</button>
            </div>
          </div>
        `;
      }).join("")
    : `${renderLifecycleGuideCard({
          title: copy("Create one persisted subscription before delivery turns into habit", "在交付进入常态前，先创建一个持久化订阅"),
          summary: copy(
            "Use the same Reader-backed delivery objects the API, CLI, and MCP already share. The browser should only project those persisted nouns.",
            "直接复用 API、CLI 和 MCP 已共享的 Reader-backed 交付对象。浏览器只负责投影这些持久化名词。"
          ),
          steps: [
            {
              title: copy("Pick Subject", "选择主体"),
              copy: copy("Reports, stories, watch missions, and profile feeds all stay under one delivery contract.", "报告、故事、监控任务和配置订阅都共用同一套交付契约。"),
            },
            {
              title: copy("Bind Route", "绑定路由"),
              copy: copy("Push delivery stays attached to named routes instead of ad hoc browser state.", "推送交付继续绑定命名路由，而不是浏览器私有状态。"),
            },
            {
              title: copy("Inspect Package", "检查包"),
              copy: copy("Report subscriptions can preview the exact package before dispatch.", "报告订阅可以在 dispatch 前预览准确的输出包。"),
            },
          ],
          actions: [
            { label: copy("Open Report Studio", "打开报告工作台"), section: "section-report-studio", primary: true },
            { label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name" },
          ],
        })}`;
  const recentDispatchRows = state.deliveryDispatchRecords.length
    ? state.deliveryDispatchRecords.slice(0, 8).map((row) => `
        <div class="mini-item">${row.route_label || row.route_name || "-"} | ${localizeWord(row.status || "pending")} | ${formatDeliveryOutputKind(row.output_kind)}</div>
        <div class="panel-sub">${row.subject_ref || "-"} | ${row.package_id || copy("No package id.", "没有 package id。")}</div>
      `).join("")
    : `<div class="empty">${copy("No delivery dispatch audit recorded yet.", "当前还没有记录到交付 dispatch 审计。")}</div>`;

  root.innerHTML = `
    <div class="story-columns">
      <div class="stack">
        <div class="card" id="digest-console-card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Digest Command Surface", "摘要控制面")}</h3>
              <div class="panel-sub">${copy("Edit the shared digest profile, inspect the replayable feed bundle, and surface prompt-pack plus route diagnostics over Reader-backed truth.", "直接编辑共享 digest_profile，查看可回放 feed_bundle，并把 prompt-pack 与路由诊断建立在 Reader 真实状态上。")}</div>
            </div>
            <span class="chip ${digestProfileShell.onboarding_status === "ready" ? "ok" : "hot"}">${digestProfileShell.onboarding_status === "ready" ? copy("Shared profile", "共享配置") : copy("Onboarding", "待初始化")}</span>
          </div>
          <form id="digest-profile-form" style="margin-top:12px;">
            <div class="field-grid">
              <label>${copy("Language", "语言")}<input name="language" value="${escapeHtml(digestProfileDraft.language)}" placeholder="en"></label>
              <label>${copy("Timezone", "时区")}<input name="timezone" value="${escapeHtml(digestProfileDraft.timezone)}" placeholder="UTC"></label>
            </div>
            <div class="field-grid">
              <label>${copy("Frequency", "频率")}<input name="frequency" value="${escapeHtml(digestProfileDraft.frequency)}" placeholder="@daily"></label>
              <label>${copy("Default Route", "默认路由")}
                <select name="default_delivery_target_ref">
                  <option value="">${copy("Select route", "选择路由")}</option>
                  ${state.routes.map((route) => {
                    const routeName = normalizeRouteName(route.name);
                    return `<option value="${escapeHtml(routeName)}" ${routeName === digestProfileDraft.default_delivery_target.ref ? "selected" : ""}>${escapeHtml(routeName)}</option>`;
                  }).join("")}
                </select>
              </label>
            </div>
            <div class="meta">
              <span>${copy("status", "状态")}=${localizeWord(digestProfileShell.onboarding_status || "needs_setup")}</span>
              <span>${copy("path", "路径")}=${escapeHtml(summarizePathTail(digestProfileShell.profile_path || "", 3) || "-")}</span>
              <span>${copy("route", "路由")}=${escapeHtml(digestRouteName || copy("unset", "未设置"))}</span>
            </div>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${copy("Save Shared Defaults", "保存共享默认值")}</button>
              <button class="btn-secondary" type="button" data-digest-refresh>${copy("Refresh Preview", "刷新预览")}</button>
              <button class="btn-secondary" type="button" data-digest-dispatch ${digestRouteName ? "" : "disabled"}>${copy("Dispatch Digest", "发送摘要")}</button>
            </div>
          </form>
          <div class="graph-meta" style="margin-top:14px;">
            <div class="mini-list" id="digest-preview-feed">
              <div class="mono">${copy("Feed Bundle Preview", "Feed Bundle 预览")}</div>
              <div class="meta">
                <span>${copy("items", "条目")}=${digestStats.feed_bundle?.items_selected ?? digestBundle.stats?.items_selected ?? 0}</span>
                <span>${copy("sources", "来源")}=${digestStats.feed_bundle?.sources_selected ?? digestBundle.stats?.sources_selected ?? 0}</span>
                <span>${copy("window end", "窗口结束")}=${escapeHtml(digestBundle.window?.end_at || "-")}</span>
              </div>
              ${digestBundleItems.length
                ? digestBundleItems.map((item) => `<div class="mini-item">${escapeHtml(item.title || item.id || "-")}</div><div class="panel-sub">${escapeHtml(item.source_name || item.url || "-")}</div>`).join("")
                : `<div class="empty">${copy("No feed-bundle item projected yet.", "当前还没有投影出 feed-bundle 条目。")}</div>`}
            </div>
            <div class="mini-list" id="digest-preview-prompts">
              <div class="mono">${copy("Prompt Readiness", "Prompt 就绪度")}</div>
              <div class="meta">
                <span>${copy("pack", "包")}=${escapeHtml(digestPromptConfig.repo_default_pack || "-")}</span>
                <span>${copy("overrides", "覆盖")}=${digestPromptOverrides.length || 0}</span>
                <span>${copy("files", "文件")}=${digestPromptFiles.length || 0}</span>
              </div>
              <div class="panel-sub">${escapeHtml((digestPromptConfig.override_order || []).join(" -> ") || copy("No prompt order projected.", "当前没有 prompt 顺序信息。"))}</div>
              ${digestPromptFiles.length
                ? digestPromptFiles.map((path) => `<div class="mini-item">${escapeHtml(summarizePathTail(path, 3))}</div>`).join("")
                : `<div class="empty">${copy("No prompt provenance file projected yet.", "当前还没有投影出 prompt 来源文件。")}</div>`}
            </div>
          </div>
          <div class="graph-meta" style="margin-top:14px;">
            <div class="mini-list" id="digest-route-diagnostics">
              <div class="mono">${copy("Route Diagnostics", "路由诊断")}</div>
              <div class="meta">
                <span>${copy("route", "路由")}=${escapeHtml(digestRouteName || copy("unset", "未设置"))}</span>
                <span>${copy("health", "健康")}=${escapeHtml(localizeWord(digestRouteHealth?.status || "idle"))}</span>
                <span>${copy("report audit", "报告审计")}=${digestRouteDispatchRows.length}</span>
              </div>
              ${digestDispatchRows.length
                ? digestDispatchRows.map((row) => `<div class="mini-item">${escapeHtml(row.route_label || row.route_name || "-")} | ${escapeHtml(localizeWord(row.status || "pending"))}</div><div class="panel-sub">${escapeHtml(row.governance?.delivery_diagnostics?.rendering?.selected_format || copy("Digest dispatch completed.", "摘要发送已完成。"))}</div>`).join("")
                : digestRouteDispatchRows.length
                  ? digestRouteDispatchRows.map((row) => `<div class="mini-item">${escapeHtml(row.route_label || row.route_name || "-")} | ${escapeHtml(localizeWord(row.status || "pending"))}</div><div class="panel-sub">${escapeHtml(row.package_id || row.error || "-")}</div>`).join("")
                  : `<div class="empty">${escapeHtml(state.digestDispatchError || copy("No route-backed diagnostic row is visible yet. Dispatch once or inspect report-backed audit on the same route.", "当前还没有看到路由诊断记录。先发送一次摘要，或查看同一路由上的报告审计。"))}</div>`}
            </div>
            <div class="mini-list" id="digest-preview-errors">
              <div class="mono">${copy("Projection Notes", "投影说明")}</div>
              <div class="meta">
                <span>${copy("exists", "已持久化")}=${digestProfileShell.exists ? copy("yes", "是") : copy("no", "否")}</span>
                <span>${copy("missing", "缺字段")}=${(digestProfileShell.missing_fields || []).length || 0}</span>
                <span>${copy("errors", "错误")}=${digestProjectionErrors.length}</span>
              </div>
              <div class="panel-sub">${escapeHtml((digestProfileShell.missing_fields || []).join(", ") || copy("Shared digest defaults are projected from the persisted profile.", "共享 digest 默认值正从持久化 profile 投影而来。"))}</div>
              ${digestProjectionErrors.length
                ? digestProjectionErrors.map((error) => `<div class="mini-item">${escapeHtml(error.code || "error")}</div><div class="panel-sub">${escapeHtml(error.message || "")}</div>`).join("")
                : `<div class="mini-item">${copy("Route-backed digest dispatch stays on the same Reader nouns as CLI and MCP.", "摘要路由发送继续复用与 CLI / MCP 相同的 Reader 名词。")}</div>`}
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Subscription Intake", "订阅创建")}</h3>
              <div class="panel-sub">${copy("Create one persisted delivery subscription in the same shell. No browser-only delivery state is introduced here.", "直接在同一个 shell 里创建持久化交付订阅；这里不会引入浏览器私有状态。")}</div>
            </div>
            <span class="chip ok">${copy("persisted", "持久化")}</span>
          </div>
          <form id="delivery-subscription-form" style="margin-top:12px;">
            <div class="field-grid">
              <label>${copy("Subject Kind", "主体类型")}
                <select name="subject_kind">
                  ${deliverySubjectOptions.map((value) => `<option value="${value}" ${draft.subject_kind === value ? "selected" : ""}>${escapeHtml(formatDeliverySubjectKind(value))}</option>`).join("")}
                </select>
              </label>
              <label>${copy("Subject Ref", "主体对象")}
                <select name="subject_ref">
                  ${subjectOptions.map((option) => `<option value="${escapeHtml(option.value)}" ${draft.subject_ref === option.value ? "selected" : ""}>${escapeHtml(option.label || option.value)}</option>`).join("")}
                </select>
              </label>
            </div>
            <div class="field-grid">
              <label>${copy("Output Kind", "输出类型")}
                <select name="output_kind">
                  ${outputOptions.map((option) => `<option value="${option.value}" ${draft.output_kind === option.value ? "selected" : ""}>${escapeHtml(option.label)}</option>`).join("")}
                </select>
              </label>
              <label>${copy("Delivery Mode", "交付模式")}
                <select name="delivery_mode">
                  ${deliveryModeOptions.map((value) => `<option value="${value}" ${draft.delivery_mode === value ? "selected" : ""}>${escapeHtml(localizeWord(value))}</option>`).join("")}
                </select>
              </label>
            </div>
            <div class="field-grid">
              <label>${copy("Status", "状态")}
                <select name="status">
                  ${deliveryStatusOptions.map((value) => `<option value="${value}" ${draft.status === value ? "selected" : ""}>${escapeHtml(localizeWord(value))}</option>`).join("")}
                </select>
              </label>
              <label>${copy("Cursor Or Since", "游标或起点")}<input name="cursor_or_since" placeholder="2026-03-01T00:00:00Z" value="${escapeHtml(draft.cursor_or_since)}"></label>
            </div>
            <label>${copy("Route Names", "路由名称")}<input name="route_names" placeholder="ops-webhook, exec-telegram" value="${escapeHtml(routeInputValue)}"><span class="field-hint">${copy("Push delivery should reference one or more named routes. Pull delivery can leave this blank.", "推送交付应绑定一个或多个命名路由；拉取模式可以留空。")}</span></label>
            <div class="ui-segment ui-segment-wrap" style="margin-top:4px;" role="group" aria-label="${escapeHtml(copy("Delivery route selection", "交付路由选择"))}">
              ${state.routes.map((route) => {
                const routeName = normalizeRouteName(route.name);
                const active = draft.route_names.includes(routeName);
                return `<button class="ui-segment-button ${active ? "active" : ""}" type="button" data-delivery-route-toggle="${escapeHtml(routeName)}" aria-pressed="${active ? "true" : "false"}">${escapeHtml(routeName)}</button>`;
              }).join("") || `<span class="chip">${copy("No route available yet", "当前还没有路由")}</span>`}
            </div>
            <div class="toolbar">
              <button class="btn-primary" type="submit">${copy("Create Subscription", "创建订阅")}</button>
              <button class="btn-secondary" type="button" data-delivery-reset>${copy("Reset Draft", "重置草稿")}</button>
              <button class="btn-secondary" type="button" data-delivery-jump-report>${copy("Open Report Studio", "打开报告工作台")}</button>
            </div>
          </form>
        </div>

        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Report Package Audit", "报告包审计")}</h3>
              <div class="panel-sub">${copy("Inspect the exact Reader-backed package before dispatch. This stays tied to the selected persisted subscription.", "在 dispatch 前检查准确的 Reader-backed 输出包，并始终绑定到当前选中的持久化订阅。")}</div>
            </div>
            <span class="chip ${selectedSubscription ? "ok" : ""}">${selectedSubscription ? escapeHtml(formatDeliveryOutputKind(selectedSubscription.output_kind)) : copy("No selection", "未选择")}</span>
          </div>
          ${selectedSubscription
            ? `
              <div class="field-grid" style="margin-top:12px;">
                <label>${copy("Selected Subscription", "当前订阅")}
                  <select id="delivery-subscription-select">
                    ${state.deliverySubscriptions.map((subscription) => `<option value="${escapeHtml(subscription.id)}" ${String(subscription.id || "").trim() === selectedSubscriptionId ? "selected" : ""}>${escapeHtml(summarizeDeliverySubject(subscription) || subscription.id)}</option>`).join("")}
                  </select>
                </label>
                <label>${copy("Package Profile", "包配置")}
                  <select id="delivery-package-profile-select" ${String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report" ? "" : "disabled"}>
                    <option value="">${copy("Default package", "默认包")}</option>
                    ${selectedReportProfiles.map((profile) => `<option value="${escapeHtml(profile.id)}" ${String(profile.id || "").trim() === selectedProfileId ? "selected" : ""}>${escapeHtml(profile.name || profile.id)}</option>`).join("")}
                  </select>
                </label>
              </div>
              <div class="meta">
                <span>${formatDeliverySubjectKind(selectedSubscription.subject_kind)}</span>
                <span>${escapeHtml(summarizeDeliverySubject(selectedSubscription))}</span>
                <span>${copy("routes", "路由")}=${(selectedSubscription.route_names || []).join(", ") || copy("none", "无")}</span>
              </div>
              ${String(selectedSubscription.subject_kind || "").trim().toLowerCase() === "report"
                ? `
                  <div class="actions">
                    <button class="btn-secondary" type="button" data-delivery-package-refresh="${escapeHtml(selectedSubscriptionId)}">${copy("Refresh Package", "刷新输出包")}</button>
                    <button class="btn-primary" type="button" data-delivery-dispatch="${escapeHtml(selectedSubscriptionId)}">${copy("Dispatch Now", "立即 dispatch")}</button>
                    <button class="btn-secondary" type="button" data-delivery-open-report="${escapeHtml(selectedSubscription.subject_ref || "")}">${copy("Open Report Studio", "打开报告工作台")}</button>
                  </div>
                  ${
                    selectedPackage
                      ? `
                        <div class="meta">
                          <span>${copy("package", "输出包")}=${escapeHtml(selectedPackage.package_id || "-")}</span>
                          <span>${copy("signature", "签名")}=${escapeHtml(selectedPackage.package_signature || "-")}</span>
                          <span>${copy("profile", "配置")}=${escapeHtml(selectedPackage.profile_id || copy("default", "默认"))}</span>
                        </div>
                        <pre class="text-block">${escapeHtml(JSON.stringify(selectedPackage.payload || {}, null, 2))}</pre>
                      `
                      : selectedPackageError
                        ? `<div class="empty">${escapeHtml(selectedPackageError)}</div>`
                        : `<div class="empty">${copy("Load one report-backed package to inspect the payload before dispatch.", "先加载一次报告输出包，再在 dispatch 前检查具体载荷。")}</div>`
                  }
                `
                : `
                  <div class="empty">${copy("Package audit is only available for report subscriptions. The selected subscription remains persisted and auditable through dispatch records below.", "当前只有报告订阅支持 package 审计；已选中的其他订阅仍会通过下方 dispatch 记录保持可审计。")}</div>
                `}
            `
            : `<div class="empty">${copy("Select one subscription from the inventory on the right to inspect its package and dispatch audit.", "先从右侧库存里选中一个订阅，再查看它的输出包和 dispatch 审计。")}</div>`}
        </div>
      </div>

      <div class="stack">
        <div class="meta">
          <span class="mono">${copy("subscription inventory", "订阅库存")}</span>
          <span class="chip ok">${copy("count", "数量")}=${state.deliverySubscriptions.length}</span>
          <span class="chip">${copy("dispatch", "dispatch")}=${state.deliveryDispatchRecords.length}</span>
        </div>
        ${inventoryRows}
        <div class="card">
          <div class="card-top">
            <div>
              <h3 class="card-title">${copy("Dispatch Audit", "Dispatch 审计")}</h3>
              <div class="panel-sub">${copy("Route-backed dispatch stays attributable to one subscription and one package signature.", "路由驱动的 dispatch 会继续精确归因到具体订阅和具体包签名。")}</div>
            </div>
            <span class="chip">${selectedSubscription ? copy("selected focus", "当前聚焦") : copy("recent", "最近记录")}</span>
          </div>
          <div class="mini-list">${selectedSubscription ? dispatchTimeline : recentDispatchRows}</div>
        </div>
      </div>
    </div>
  `;

  wireLifecycleGuideActions(root);
  const digestForm = root.querySelector("#digest-profile-form");
  digestForm?.addEventListener("input", () => {
    state.digestProfileDraft = collectDigestProfileDraft(digestForm);
  });
  digestForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = digestForm.querySelector("button[type='submit']");
    const nextDraft = collectDigestProfileDraft(digestForm);
    state.digestProfileDraft = nextDraft;
    if (!nextDraft.default_delivery_target.ref) {
      setStageFeedback("deliver", {
        kind: "blocked",
        title: copy("Shared digest defaults still need a named route", "共享 digest 默认值仍缺少命名路由"),
        copy: copy("Pick one named route before this delivery default can persist on the stage-owned surface.", "请先选择一个命名路由，这组交付默认值才能持久化到当前阶段。"),
        actionHierarchy: {
          primary: {
            label: copy("Focus Route Draft", "聚焦路由草稿"),
            attrs: { "data-empty-focus": "route", "data-empty-field": "name" },
          },
          secondary: [
            {
              label: copy("Open Delivery Lane", "打开交付工作线"),
              attrs: { "data-empty-jump": "section-ops" },
            },
          ],
        },
      });
      showToast(copy("Choose one named route before saving shared digest defaults.", "保存共享 digest 默认值前请先选择一个命名路由。"), "error");
      return;
    }
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      const updated = await api("/api/digest-profile", {
        method: "PUT",
        payload: nextDraft,
      });
      state.digestProfileDraft = normalizeDigestProfileDraft(updated?.profile || nextDraft);
      await loadDigestConsole({ preserveDraft: false });
      setStageFeedback("deliver", {
        kind: "completion",
        title: copy("Shared digest defaults saved", "共享 digest 默认值已保存"),
        copy: copy(
          "The delivery lane now keeps the shared digest route on the owned surface instead of leaving it in toast history.",
          "交付阶段现在已经把共享 digest 路由保留在拥有它的面板上，而不是只留在 toast 历史里。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Refresh Digest Preview", "刷新摘要预览"),
            attrs: { "data-digest-refresh": true },
          },
        },
      });
      showToast(copy("Shared digest defaults saved.", "共享 digest 默认值已保存。"), "success");
    } catch (error) {
      reportError(error, copy("Save digest profile", "保存 digest 配置"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelector("[data-digest-refresh]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await loadDigestConsole({ preserveDraft: false });
      showToast(copy("Digest preview refreshed.", "摘要预览已刷新。"), "success");
    } catch (error) {
      reportError(error, copy("Refresh digest preview", "刷新摘要预览"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-digest-dispatch]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    state.digestDispatchError = "";
    try {
      state.digestDispatchResult = await api("/api/digest/dispatch", {
        method: "POST",
        payload: { profile: "default", limit: 8 },
      });
      renderDeliveryWorkspace();
      showToast(copy("Digest dispatch completed.", "摘要发送已完成。"), "success");
    } catch (error) {
      state.digestDispatchResult = [];
      state.digestDispatchError = error.message;
      renderDeliveryWorkspace();
      reportError(error, copy("Dispatch digest", "发送摘要"));
    } finally {
      button.disabled = false;
    }
  });
  const form = root.querySelector("#delivery-subscription-form");
  form?.addEventListener("input", () => {
    state.deliveryDraft = collectDeliveryDraft(form);
  });
  form?.addEventListener("change", (event) => {
    state.deliveryDraft = collectDeliveryDraft(form);
    const fieldName = String(event.target?.name || "").trim();
    if (fieldName === "subject_kind" || fieldName === "subject_ref" || fieldName === "delivery_mode") {
      renderDeliveryWorkspace();
    }
  });
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = form.querySelector("button[type='submit']");
    const nextDraft = collectDeliveryDraft(form);
    state.deliveryDraft = nextDraft;
    if (!nextDraft.subject_ref) {
      setStageFeedback("deliver", {
        kind: "blocked",
        title: copy("Delivery subscription still needs a subject", "交付订阅仍缺少主体对象"),
        copy: copy("Pick the report, story, profile, or mission that this delivery lane should own.", "请选择这条交付工作线要负责的报告、故事、配置或任务对象。"),
        actionHierarchy: {
          primary: {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        },
      });
      showToast(copy("Pick one subject before saving the subscription.", "保存订阅前请先选择一个主体对象。"), "error");
      return;
    }
    if (nextDraft.delivery_mode === "push" && !nextDraft.route_names.length) {
      setStageFeedback("deliver", {
        kind: "blocked",
        title: copy("Push delivery still needs a named route", "推送交付仍缺少命名路由"),
        copy: copy("Attach at least one named route before this subscription can dispatch downstream.", "请至少绑定一个命名路由，这条订阅才能向下游发送。"),
        actionHierarchy: {
          primary: {
            label: copy("Focus Route Draft", "聚焦路由草稿"),
            attrs: { "data-empty-focus": "route", "data-empty-field": "name" },
          },
          secondary: [
            {
              label: copy("Open Delivery Lane", "打开交付工作线"),
              attrs: { "data-empty-jump": "section-ops" },
            },
          ],
        },
      });
      showToast(copy("Push delivery needs at least one named route.", "推送交付至少需要绑定一个命名路由。"), "error");
      return;
    }
    if (submitButton) {
      submitButton.disabled = true;
    }
    try {
      const created = await api("/api/delivery-subscriptions", {
        method: "POST",
        payload: nextDraft,
      });
      state.selectedDeliverySubscriptionId = String(created.id || "").trim();
      state.deliveryDraft = defaultDeliveryDraft();
      pushActionEntry({
        kind: copy("delivery create", "交付创建"),
        label: state.language === "zh"
          ? `已创建订阅：${summarizeDeliverySubject(created) || created.id}`
          : `Created subscription: ${summarizeDeliverySubject(created) || created.id}`,
        detail: state.language === "zh"
          ? `输出：${formatDeliveryOutputKind(created.output_kind)}`
          : `Output: ${formatDeliveryOutputKind(created.output_kind)}`,
      });
      await refreshBoard();
      setStageFeedback("deliver", {
        kind: "completion",
        title: copy("Delivery subscription created", "交付订阅已创建"),
        copy: copy(
          "The delivery lane now owns a persisted subscription record. Inspect its package or dispatch it next.",
          "交付阶段现在已经拥有持久化订阅记录；下一步可以检查输出包，或直接执行 dispatch。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        },
      });
      showToast(copy("Delivery subscription created.", "交付订阅已创建。"), "success");
    } catch (error) {
      reportError(error, copy("Create delivery subscription", "创建交付订阅"));
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  });
  root.querySelectorAll("[data-delivery-route-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const routeName = normalizeRouteName(button.dataset.deliveryRouteToggle || "");
      const draftRoutes = state.deliveryDraft?.route_names || [];
      state.deliveryDraft = normalizeDeliveryDraft({
        ...(state.deliveryDraft || draft),
        route_names: draftRoutes.includes(routeName)
          ? draftRoutes.filter((value) => value !== routeName)
          : [...draftRoutes, routeName],
      });
      renderDeliveryWorkspace();
    });
  });
  root.querySelector("[data-delivery-reset]")?.addEventListener("click", () => {
    state.deliveryDraft = defaultDeliveryDraft();
    renderDeliveryWorkspace();
    showToast(copy("Delivery draft reset.", "交付草稿已重置。"), "success");
  });
  root.querySelector("[data-delivery-jump-report]")?.addEventListener("click", () => {
    jumpToSection("section-report-studio");
  });
  root.querySelector("#delivery-subscription-select")?.addEventListener("change", async (event) => {
    state.selectedDeliverySubscriptionId = String(event.target.value || "").trim();
    renderDeliveryWorkspace();
    const subscription = getSelectedDeliverySubscription();
    if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {
      try {
        await loadDeliveryPackageAudit(subscription.id, {
          profileId: String(state.deliveryPackageProfileIds[subscription.id] || "").trim(),
        });
      } catch (error) {
        reportError(error, copy("Load report package", "加载报告输出包"));
      }
    }
  });
  root.querySelector("#delivery-package-profile-select")?.addEventListener("change", async (event) => {
    const subscription = getSelectedDeliverySubscription();
    if (!subscription) {
      return;
    }
    const profileId = String(event.target.value || "").trim();
    state.deliveryPackageProfileIds[String(subscription.id || "").trim()] = profileId;
    try {
      await loadDeliveryPackageAudit(subscription.id, { profileId });
    } catch (error) {
      reportError(error, copy("Load report package", "加载报告输出包"));
    }
  });
  root.querySelector("[data-delivery-package-refresh]")?.addEventListener("click", async (event) => {
    const subscriptionId = String(event.currentTarget.dataset.deliveryPackageRefresh || "").trim();
    const button = event.currentTarget;
    button.disabled = true;
    try {
      await loadDeliveryPackageAudit(subscriptionId, {
        profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
      });
      showToast(copy("Report package refreshed.", "报告输出包已刷新。"), "success");
    } catch (error) {
      reportError(error, copy("Refresh report package", "刷新报告输出包"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-delivery-dispatch]")?.addEventListener("click", async (event) => {
    const subscriptionId = String(event.currentTarget.dataset.deliveryDispatch || "").trim();
    const button = event.currentTarget;
    button.disabled = true;
    try {
      const profileId = String(state.deliveryPackageProfileIds[subscriptionId] || "").trim();
      await api(`/api/delivery-subscriptions/${subscriptionId}/dispatch`, {
        method: "POST",
        payload: { profile_id: profileId || null },
      });
      pushActionEntry({
        kind: copy("delivery dispatch", "交付执行"),
        label: state.language === "zh"
          ? `已执行 dispatch：${subscriptionId}`
          : `Dispatched subscription: ${subscriptionId}`,
        detail: state.language === "zh"
          ? `配置：${profileId || "default"}`
          : `Profile: ${profileId || "default"}`,
      });
      await refreshBoard();
      setStageFeedback("deliver", {
        kind: "completion",
        title: copy("Delivery dispatch completed", "交付 dispatch 已完成"),
        copy: copy(
          "Dispatch results are now part of the delivery lane history. Inspect the audit timeline or route posture next.",
          "dispatch 结果现在已经进入交付阶段历史；下一步可以查看审计时间线或路由姿态。"
        ),
        actionHierarchy: {
          primary: {
            label: copy("Open Delivery Lane", "打开交付工作线"),
            attrs: { "data-empty-jump": "section-ops" },
          },
        },
      });
      showToast(copy("Delivery dispatch completed.", "交付 dispatch 已完成。"), "success");
    } catch (error) {
      reportError(error, copy("Dispatch delivery subscription", "执行交付订阅"));
    } finally {
      button.disabled = false;
    }
  });
  root.querySelector("[data-delivery-open-report]")?.addEventListener("click", async (event) => {
    const reportId = String(event.currentTarget.dataset.deliveryOpenReport || "").trim();
    if (reportId) {
      await selectReport(reportId);
    }
    jumpToSection("section-report-studio");
  });
  root.querySelectorAll("[data-delivery-select]").forEach((button) => {
    button.addEventListener("click", async () => {
      const subscriptionId = String(button.dataset.deliverySelect || "").trim();
      state.selectedDeliverySubscriptionId = subscriptionId;
      renderDeliveryWorkspace();
      const subscription = getDeliverySubscriptionRecord(subscriptionId);
      if (subscription && String(subscription.subject_kind || "").trim().toLowerCase() === "report") {
        try {
          await loadDeliveryPackageAudit(subscriptionId, {
            profileId: String(state.deliveryPackageProfileIds[subscriptionId] || "").trim(),
          });
        } catch (error) {
          reportError(error, copy("Load report package", "加载报告输出包"));
        }
      }
    });
  });
  root.querySelectorAll("[data-delivery-toggle-status]").forEach((button) => {
    button.addEventListener("click", async () => {
      const subscriptionId = String(button.dataset.deliveryToggleStatus || "").trim();
      const nextStatus = String(button.dataset.nextStatus || "active").trim().toLowerCase();
      button.disabled = true;
      try {
        await api(`/api/delivery-subscriptions/${subscriptionId}`, {
          method: "PUT",
          payload: { status: nextStatus },
        });
        await refreshBoard();
        setStageFeedback("deliver", nextStatus === "paused"
          ? {
              kind: "warning",
              title: copy("Delivery subscription paused", "交付订阅已暂停"),
              copy: copy("This subscription will stop dispatching until it is resumed from the delivery lane.", "这条订阅会停止 dispatch，直到在交付阶段重新恢复。"),
              actionHierarchy: {
                primary: {
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: { "data-empty-jump": "section-ops" },
                },
              },
            }
          : {
              kind: "completion",
              title: copy("Delivery subscription resumed", "交付订阅已恢复"),
              copy: copy("The subscription is back in the delivery lane and can dispatch again.", "这条订阅已经重新回到交付阶段，可以再次 dispatch。"),
              actionHierarchy: {
                primary: {
                  label: copy("Open Delivery Lane", "打开交付工作线"),
                  attrs: { "data-empty-jump": "section-ops" },
                },
              },
            });
        showToast(
          nextStatus === "paused"
            ? copy("Delivery subscription paused.", "交付订阅已暂停。")
            : copy("Delivery subscription resumed.", "交付订阅已恢复。"),
          "success",
        );
      } catch (error) {
        reportError(error, copy("Update delivery subscription", "更新交付订阅"));
      } finally {
        button.disabled = false;
      }
    });
  });
  root.querySelectorAll("[data-delivery-delete]").forEach((button) => {
    button.addEventListener("click", async () => {
      const subscriptionId = String(button.dataset.deliveryDelete || "").trim();
      if (!subscriptionId) {
        return;
      }
      const confirmed = window.confirm(copy(
        `Delete delivery subscription ${subscriptionId}?`,
        `确认删除交付订阅 ${subscriptionId}？`,
      ));
      if (!confirmed) {
        return;
      }
      button.disabled = true;
      try {
        await api(`/api/delivery-subscriptions/${subscriptionId}`, { method: "DELETE" });
        if (state.selectedDeliverySubscriptionId === subscriptionId) {
          state.selectedDeliverySubscriptionId = "";
        }
        await refreshBoard();
        setStageFeedback("deliver", {
          kind: "completion",
          title: copy("Delivery subscription deleted", "交付订阅已删除"),
          copy: copy("The selected subscription has been removed from the delivery lane inventory.", "当前选中的订阅已经从交付阶段库存中移除。"),
          actionHierarchy: {
            primary: {
              label: copy("Open Delivery Lane", "打开交付工作线"),
              attrs: { "data-empty-jump": "section-ops" },
            },
          },
        });
        showToast(copy("Delivery subscription deleted.", "交付订阅已删除。"), "success");
      } catch (error) {
        reportError(error, copy("Delete delivery subscription", "删除交付订阅"));
      } finally {
        button.disabled = false;
      }
    });
  });
}

function renderAiSurfaces() {
  const root = $("ai-surface-shell");
  if (!root) {
    return;
  }
  const hasPrechecks = Object.keys(state.aiSurfacePrechecks || {}).length > 0;
  if (state.loading.board && !hasPrechecks) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    return;
  }
  const surfaces = [
    {
      id: "mission_suggest",
      title: copy("Mission Suggest", "任务建议"),
      subjectLabel: copy("watch", "任务"),
      section: "section-board",
    },
    {
      id: "triage_assist",
      title: copy("Triage Assist", "分诊辅助"),
      subjectLabel: copy("evidence", "证据"),
      section: "section-triage",
    },
    {
      id: "claim_draft",
      title: copy("Claim Draft", "主张草稿"),
      subjectLabel: copy("story", "故事"),
      section: "section-story",
    },
  ];
  root.innerHTML = surfaces.map((surface) => {
    const precheck = getAiSurfacePrecheck(surface.id);
    const projection = getAiSurfaceProjection(surface.id);
    const runtime = projection?.runtime_facts && typeof projection.runtime_facts === "object" ? projection.runtime_facts : {};
    const subject = projection?.subject && typeof projection.subject === "object" ? projection.subject : {};
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
            <div class="mono">${escapeHtml(surface.id)}</div>
            <h3 class="card-title" style="margin-top:10px;">${escapeHtml(surface.title)}</h3>
          </div>
          <span class="chip ${tone}">${escapeHtml(localizeWord(runtime.status || precheck.mode_status || "pending"))}</span>
        </div>
        <div class="meta">
          <span>${copy("mode", "模式")}=${escapeHtml(precheck.mode || "assist")}</span>
          <span>${copy("subject", "对象")}=${escapeHtml(subject.id || "-")}</span>
          <span>${copy("contract", "契约")}=${escapeHtml(precheck.contract_id || "-")}</span>
        </div>
        <div class="panel-sub">${escapeHtml(summarizeAiSurfaceProjection(surface.id, projection))}</div>
        <div class="meta" style="margin-top:10px;">
          <span>${copy("alias", "别名")}=${escapeHtml(precheck.alias || "-")}</span>
          <span>${copy("fallback", "回退")}=${escapeHtml(localizeWord(precheck.manual_fallback || "-"))}</span>
          <span>${copy("gaps", "缺口")}=${rejectableGaps.length}</span>
          <span>${copy("runtime facts", "运行事实")}=${mustExposeFacts.length}</span>
        </div>
        <div class="panel-sub">${escapeHtml(runtime.request_id || copy("No runtime request id yet.", "当前还没有运行请求 ID。"))}</div>
        <div class="actions" style="margin-top:12px;">
          <button class="btn-secondary" type="button" data-empty-jump="${escapeHtml(surface.section)}">${copy("Open Surface", "打开对应界面")}</button>
        </div>
      </div>
    `;
  }).join("");
  wireLifecycleGuideActions(root);
}

function renderStatus() {
  const root = $("status-card");
  renderOpsSectionSummary();
  if (state.loading.board && !state.status && !state.ops) {
    root.innerHTML = [skeletonCard(4), skeletonCard(4), skeletonCard(4)].join("");
    return;
  }
  const ops = state.ops || {};
  const status = ops.daemon || state.status || {};
  const metrics = status.metrics || {};
  const collectorSummary = ops.collector_summary || {};
  const collectorTiers = ops.collector_tiers || {};
  const collectorDrilldown = Array.isArray(ops.collector_drilldown) ? ops.collector_drilldown : [];
  const watchMetrics = ops.watch_metrics || {};
  const watchSummary = ops.watch_summary || {};
  const watchHealth = Array.isArray(ops.watch_health) ? ops.watch_health : [];
  const routeSummary = ops.route_summary || {};
  const routeDrilldown = Array.isArray(ops.route_drilldown) ? ops.route_drilldown : [];
  const routeTimeline = Array.isArray(ops.route_timeline) ? ops.route_timeline : [];
  const degradedCollectors = ops.degraded_collectors || [];
  const recentFailures = ops.recent_failures || [];
  const isError = status.state === "error";
  const tierBlock = Object.entries(collectorTiers).length
    ? Object.entries(collectorTiers).map(([tierName, tier]) => `
        <div class="mini-item">${tierName} | total=${tier.total || 0} | ok=${tier.ok || 0} | warn=${tier.warn || 0} | error=${tier.error || 0}</div>
      `).join("")
    : `<div class="empty">${copy("No collector tier breakdown available.", "没有采集器层级拆分数据。")}</div>`;
  const watchBlock = watchHealth.length
    ? watchHealth.slice(0, 5).map((mission) => `
        <div class="mini-item">${mission.id} | ${mission.status || "idle"} | due=${mission.is_due ? "yes" : "no"} | rate=${formatRate(mission.success_rate)}</div>
      `).join("")
    : `<div class="empty">${copy("No watch mission health record yet.", "当前没有任务健康记录。")}</div>`;
  const collectorBlock = degradedCollectors.length
    ? degradedCollectors.slice(0, 4).map((collector) => `
        <div class="mini-item">${collector.name} | ${collector.tier} | ${collector.status} | available=${collector.available}</div>
      `).join("")
    : `<div class="empty">${copy("No degraded collector currently reported.", "当前没有降级采集器。")}</div>`;
  const collectorDrilldownBlock = collectorDrilldown.length
    ? collectorDrilldown.slice(0, 8).map((collector) => `
        <div class="mini-item">${collector.name} | ${collector.tier || "-"} | ${collector.status || "ok"} | available=${collector.available}</div>
        <div class="panel-sub">${collector.setup_hint || collector.message || copy("No remediation note.", "没有修复说明。")}</div>
      `).join("")
    : `<div class="empty">${copy("No collector drill-down entry available.", "没有采集器下钻条目。")}</div>`;
  const routeDrilldownBlock = routeDrilldown.length
    ? routeDrilldown.slice(0, 8).map((route) => `
        <div class="mini-item">${route.name} | channel=${route.channel || "unknown"} | status=${route.status || "idle"} | rate=${formatRate(route.success_rate)}</div>
        <div class="panel-sub">missions=${route.mission_count || 0} | rules=${route.rule_count || 0} | events=${route.event_count || 0} | failed=${route.failure_count || 0}</div>
        <div class="panel-sub">${route.last_error || route.last_summary || copy("No recent route detail.", "没有最近路由详情。")}</div>
      `).join("")
    : `<div class="empty">${copy("No route drill-down entry available.", "没有路由下钻条目。")}</div>`;
  const routeTimelineBlock = routeTimeline.length
    ? routeTimeline.slice(0, 8).map((event) => `
        <div class="mini-item">${event.created_at || "-"} | ${event.route || "-"} | ${event.status || "pending"} | ${event.mission_name || event.mission_id || "-"}</div>
        <div class="panel-sub">${event.error || event.summary || copy("No route event detail.", "没有路由事件详情。")}</div>
      `).join("")
    : `<div class="empty">${copy("No route delivery timeline event available.", "没有路由投递时间线事件。")}</div>`;
  const failureBlock = recentFailures.length
    ? recentFailures.slice(0, 4).map((failure) => `
        <div class="mini-item">${failure.kind} | ${failure.mission_name || failure.name || "-"} | ${localizeWord(failure.status || "error")} | ${failure.error || "-"}</div>
      `).join("")
    : `<div class="empty">${copy("No recent failure captured.", "近期没有失败记录。")}</div>`;
  const overflowEvidence = state.consoleOverflowEvidence || defaultConsoleOverflowEvidence();
  const overflowSampledAt = overflowEvidence.updated_at
    ? formatCompactDateTime(overflowEvidence.updated_at)
    : copy("not sampled yet", "尚未采样");
  const overflowResidualBlock = Array.isArray(overflowEvidence.residual_surfaces) && overflowEvidence.residual_surfaces.length
    ? overflowEvidence.residual_surfaces.map((surface) => {
        const samples = Array.isArray(surface.sample_labels) ? surface.sample_labels : [];
        const sampleLine = samples.length
          ? `<div class="panel-sub">${samples.map((label) => escapeHtml(label)).join(" | ")}</div>`
          : `<div class="panel-sub">${copy("No residual sample label captured.", "没有残余样本文本。")}</div>`;
        return `
          <div class="mini-item" data-overflow-surface="${escapeHtml(surface.surface_id || "")}">
            ${escapeHtml(surface.surface_id || "unknown")} | survivors=${surface.survivor_count || 0} | fitted=${surface.fitted_sample_count || 0}/${surface.checked_sample_count || 0}
          </div>
          ${sampleLine}
        `;
      }).join("")
    : `<div class="empty" data-overflow-surface-empty="true">${copy("No residual overflow survivors captured in this runtime session.", "当前运行会话没有捕获到残余溢出样本。")}</div>`;
  const alertSignal = getGovernanceSignal("alert_yield");
  const storySignal = getGovernanceSignal("story_conversion");
  const deliveryContinuityBlock = renderLifecycleContinuityCard({
    title: copy("Delivery Continuity", "交付连续性"),
    summary: copy(
      "Alerting missions, ready stories, and route-backed delivery health stay in one lane so downstream status is visible without backtracking.",
      "触发告警的任务、待交付故事和路由健康会保持在同一条工作线里，让下游状态无需回跳即可看清。"
    ),
    stages: [
      {
        kicker: copy("Mission", "任务"),
        title: copy("Alerting Missions", "触发告警任务"),
        copy: copy(
          "Mission-side alert load stays visible here so delivery work starts from real upstream pressure instead of guesswork.",
          "这里会持续展示任务侧的告警压力，让交付工作基于真实上游负载，而不是靠猜测。"
        ),
        tone: (state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) > 0 ? "ok" : "",
        facts: [
          { label: copy("Alerting missions", "触发告警任务"), value: String(state.overview?.alerting_mission_count ?? alertSignal.alerting_missions ?? 0) },
          { label: copy("Recent alerts", "最近告警"), value: String(alertSignal.alert_count ?? state.alerts.length ?? 0) },
          { label: copy("Successful runs", "成功执行"), value: String(alertSignal.successful_runs ?? metrics.runs_total ?? 0) },
        ],
      },
      {
        kicker: copy("Story", "故事"),
        title: copy("Story Readiness", "故事就绪度"),
        copy: copy(
          "Ready stories stay visible beside delivery operations so handoff decisions do not require a separate story audit pass.",
          "待交付故事会与交付操作并排可见，避免为了判断交接是否成立再单独回去审计故事。"
        ),
        tone: (state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) > 0 ? "ok" : "",
        facts: [
          { label: copy("Stories", "故事"), value: String(state.overview?.story_count ?? storySignal.story_count ?? state.stories.length) },
          { label: copy("Ready", "已就绪"), value: String(state.overview?.story_ready_count ?? storySignal.ready_story_count ?? 0) },
          { label: copy("Converted items", "已转化条目"), value: String(storySignal.converted_item_count ?? 0) },
        ],
      },
      {
        kicker: copy("Route", "路由"),
        title: copy("Route Delivery", "路由交付"),
        copy: copy(
          "Route health and the latest delivery event stay close to the editor so fix-or-forward decisions happen in one place.",
          "路由健康和最新投递事件会贴近编辑器展示，让修复或继续推进都能在同一位置完成。"
        ),
        tone: (routeSummary.degraded || 0) > 0 ? "hot" : "ok",
        facts: [
          { label: copy("Healthy", "健康"), value: String(routeSummary.healthy || 0) },
          { label: copy("Degraded", "降级"), value: String(routeSummary.degraded || 0) },
          { label: copy("Last event", "最近事件"), value: formatCompactDateTime(routeTimeline[0]?.created_at || "") },
        ],
      },
    ],
    actions: [
      { label: copy("Focus Route Deck", "聚焦路由草稿"), focus: "route", field: "name", primary: true },
      { label: copy("Open Mission Board", "打开任务列表"), section: "section-board" },
      { label: copy("Open Stories", "打开故事"), section: "section-story" },
    ],
  });
  root.innerHTML = `
    ${deliveryContinuityBlock}
    <div class="state-banner ${isError ? "error" : ""}">
      <div class="eyebrow"><span class="dot"></span> ${copy("daemon", "守护进程")} / ${localizeWord(status.state || "idle")}</div>
      <h3 class="card-title" style="margin-top:12px;">${copy("Heartbeat", "心跳")}: ${status.heartbeat_at || "-"}</h3>
      <div class="meta">
        <span>${copy("cycles", "轮次")}=${metrics.cycles_total || 0}</span>
        <span>${copy("runs", "执行")}=${metrics.runs_total || 0}</span>
        <span>${copy("alerts", "告警")}=${metrics.alerts_total || 0}</span>
        <span>${copy("errors", "错误")}=${metrics.error_total || 0}</span>
        <span>${copy("success", "成功")}=${metrics.success_total || 0}</span>
      </div>
    </div>
    <div class="card">
      <div class="mono">${copy("collector health", "采集器健康")}</div>
      <div class="meta">
        <span>total=${collectorSummary.total || 0}</span>
        <span>ok=${collectorSummary.ok || 0}</span>
        <span>warn=${collectorSummary.warn || 0}</span>
        <span>error=${collectorSummary.error || 0}</span>
        <span>unavailable=${collectorSummary.unavailable || 0}</span>
      </div>
    </div>
    <div class="card">
      <div class="mono">${copy("route health", "路由健康")}</div>
      <div class="meta">
        <span>healthy=${routeSummary.healthy || 0}</span>
        <span>degraded=${routeSummary.degraded || 0}</span>
        <span>missing=${routeSummary.missing || 0}</span>
        <span>idle=${routeSummary.idle || 0}</span>
      </div>
    </div>
    <div class="card">
      <div class="mono">${copy("watch health", "任务健康")}</div>
      <div class="meta">
        <span>total=${watchSummary.total || 0}</span>
        <span>enabled=${watchSummary.enabled || 0}</span>
        <span>healthy=${watchSummary.healthy || 0}</span>
        <span>degraded=${watchSummary.degraded || 0}</span>
        <span>idle=${watchSummary.idle || 0}</span>
        <span>disabled=${watchSummary.disabled || 0}</span>
        <span>due=${watchSummary.due || 0}</span>
        <span>rate=${formatRate(watchMetrics.success_rate)}</span>
      </div>
    </div>
    <div class="card" id="console-overflow-evidence-card">
      <div class="mono">${copy("text overflow evidence", "文本溢出证据")}</div>
      <div class="meta" data-console-overflow-summary>
        <span>surfaces=${overflowEvidence.surface_count || 0}</span>
        <span>checked=${overflowEvidence.checked_sample_count || 0}</span>
        <span>fitted=${overflowEvidence.fitted_sample_count || 0}</span>
        <span>survivors=${overflowEvidence.survivor_count || 0}</span>
        <span>hotspots=${overflowEvidence.residual_surface_count || 0}</span>
        <span>sampled=${overflowSampledAt}</span>
      </div>
      <div class="panel-sub">${copy(
        "Session-scoped evidence for data-fit console text surfaces after the current truncation and canvas-fit layers run.",
        "会话级证据，覆盖当前截断与 canvas-fit 层运行后的 data-fit 控制台文本表面。"
      )}</div>
      <div class="mini-list" style="margin-top:12px;" data-console-overflow-hotspots>
        <div class="mono">${copy("residual hotspots", "残余热点")}</div>
        ${overflowResidualBlock}
      </div>
    </div>
    <div class="card">
      <div class="mono">${copy("last_error", "最近错误")}</div>
      <div>${status.last_error || "-"}</div>
    </div>
    <div class="graph-meta">
      <div class="mini-list">
        <div class="mono">${copy("collector tiers", "采集器层级")}</div>
        ${tierBlock}
      </div>
      <div class="mini-list">
        <div class="mono">${copy("watch board", "任务面板")}</div>
        ${watchBlock}
      </div>
    </div>
    <div class="graph-meta">
      <div class="mini-list">
        <div class="mono">${copy("degraded collectors", "降级采集器")}</div>
        ${collectorBlock}
      </div>
      <div class="mini-list">
        <div class="mono">${copy("collector drill-down", "采集器下钻")}</div>
        ${collectorDrilldownBlock}
      </div>
    </div>
    <div class="graph-meta">
      <div class="mini-list">
        <div class="mono">${copy("route drill-down", "路由下钻")}</div>
        ${routeDrilldownBlock}
      </div>
      <div class="mini-list">
        <div class="mono">${copy("recent failures", "最近失败")}</div>
        ${failureBlock}
      </div>
    </div>
    <div class="graph-meta">
      <div class="mini-list">
        <div class="mono">${copy("route timeline", "路由时间线")}</div>
        ${routeTimelineBlock}
      </div>
      <div class="mini-list">
        <div class="mono">${copy("degraded collectors", "降级采集器")}</div>
        ${collectorBlock}
      </div>
    </div>`;
  wireLifecycleGuideActions(root);
}
