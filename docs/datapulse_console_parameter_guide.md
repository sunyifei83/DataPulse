# DataPulse 浏览器控制台参数填写说明

![DataPulse 浏览器控制台预览](datapulse_console.png)

## 适用范围

本文档说明 `datapulse-console` 当前浏览器表单 `Deploy Mission` 与 `Mission Cockpit` 中 alert rule editor 的参数含义、填写建议，以及它们最终映射到的后端字段。

当前说明基于仓内已实现行为，不描述尚未开放的理想字段。`Mission Cockpit` 中的 alert rule editor 复用同一组 alert 字段，只是提交到更新接口而不是创建接口。

本文档也记录 `L19.3` 冻结后的跨控制面约定：后续 digest onboarding 即使进入浏览器，也必须和 CLI / MCP 共享同一份 `digest_profile` 与 prompt-pack 解析顺序，而不是新增浏览器专用状态。

## 当前表单范围

浏览器表单当前用于创建一个 watch mission，并可选附带一条基础 alert rule。`Mission Cockpit` 中的 alert rule editor 用于替换或清空该 mission 的当前基础规则。

当前支持：

- mission 基本信息：`name`、`query`、`schedule`、`platform`
- alert 基础过滤：`route`、`keyword`、`domain`、`min_score`、`min_confidence`
- alert rule 更新动作：保存替换、清空规则

当前未在浏览器表单暴露，但 CLI / MCP / API 已支持：

- `sites`
- `top_n`
- 多平台输入
- 多条 `alert_rules`
- `required_tags` / `excluded_tags`
- `source_types`
- `max_age_minutes`
- 非 `json` 直配 channel

当前未在浏览器表单暴露，且仍属于后续实现的共享 digest 约定：

- `digest_profile.language`
- `digest_profile.timezone`
- `digest_profile.frequency`
- `digest_profile.default_delivery_target`
- resolved `prompt_pack` / override provenance

## 浏览器生命周期快路径

控制台现在默认按浏览器内的真实操作路径组织，不需要先从 CLI 文档入手：

1. `Quick Start / Deploy Mission`

先填 `Name + Query` 创建 mission；需要时再补 `Schedule`、`Platform`、`Alert Route` 等范围或交付条件。

2. `Mission Board / Mission Cockpit`

创建后先在浏览器里执行 mission，确认最近 runs、结果流、时间线和 alert rule editor 是否符合预期。

3. `Triage Queue`

mission run 写入 inbox 后，证据会在这里进入分诊。你可以直接完成核验、去重、备注，并使用 `Create Story` 做故事提升。

4. `Story Workspace`

故事既可以从 triage 直接提升，也可以先在 `Story Intake` 手工补录。标题、摘要、状态和证据回查都在浏览器里继续完成。

5. `Route Manager / Distribution Health`

命名 route 先在 `Route Manager` 创建，再从 `Deploy Mission` 或 `Mission Cockpit` 的 alert rule editor 绑定；交付表现则在 `Distribution Health` 继续观察。

## `L24.2` 冻结后的工作区恢复与说明文案约定

这部分记录当前控制台在 `L24.2` 落地后的共享 contract：哪些上下文属于可分享/可恢复 URL，哪些说明文案归静态参数文档，哪些解释必须继续绑定运行时事实。

### 哪些控制台上下文属于 URL state

| 场景 | 当前 URL contract | 为什么属于 URL | 不进入 URL 的内容 |
| --- | --- | --- | --- |
| 当前 section | `#section-intake` / `#section-board` / `#section-cockpit` / `#section-triage` / `#section-story` / `#section-claims` / `#section-report-studio` / `#section-ops` | 这是当前工作区位置，本来就需要可刷新、可分享 | 单独的 workspace-mode 参数；workspace mode 继续从 section 派生 |
| Mission 工作区 | `watch_search`、`watch_id` | 用于恢复 mission 搜索词和当前选中的 mission | `Deploy Mission` 未提交草稿、卡片展开状态、toast 成功提示 |
| Triage 工作区 | `triage_filter`、`triage_search`、`triage_id` | 用于恢复分诊队列范围和当前查看项 | 临时键盘焦点、note 输入光标、一次性 modal 状态 |
| Story 工作区 | `story_view`、`story_filter`、`story_sort`、`story_search`、`story_id`、`story_mode` | 用于恢复 story board / editor 上下文 | 未保存编辑文本、临时预览开关、局部 inspector 展开态 |
| Saved View / Deep Link | 保存和分享的是完整 canonical URL | 保持一份唯一可分享 contract，而不是额外发明一套分享 payload | pinned 状态、saved-view 名称、最近分享历史等本地管理字段 |

补充约束：

- `Deploy Mission` 草稿继续属于本地草稿，不属于 shareable URL state。
- command palette 查询词/最近记录、context link history、saved-view catalog、语言偏好继续走本地存储。
- reversible action history、toast、dismissible helper banner、modal 开关都不是 repo truth，不应进入 URL。

### Operator Guidance / Explanation Copy 归属

| 内容类型 | canonical owner | 当前示例 | 不允许出现的漂移 |
| --- | --- | --- | --- |
| 参数语义与填写建议 | 本文档 `docs/datapulse_console_parameter_guide.md` | `Alert Route`、`Alert Domain`、`digest_profile` 默认字段、prompt-pack 解析顺序 | 浏览器里的零散 label 变成唯一规格来源 |
| 运行时解释与下一步建议 | Reader / API 投影到控制台的事实型 guidance | retry guidance、duplicate explain、route health remediation、mission suggestion | 浏览器基于本地 heuristics 重新编一套不同原因 |
| section 级 success / blocker framing | `docs/governance/datapulse-console-interaction-clarity-blueprint.md` 当前冻结，`L24.4` 已在 `datapulse/console_markup.py` 做共享实现 | 各 lane 的 objective、success card、blocker card 标题和语气 | 每个 lane 各写各的解释文案，或只靠 toast 告知下一步 |

补充约束：

- toast、临时 helper、palette hint 可以复述 canonical guidance，但不能成为唯一 owner。
- 浏览器如果后续补更多 onboarding，只能编辑或投影同一份共享 contract，不能发明 GUI-only 解释语义。
- 本文档负责静态参数和填写边界，不负责替代运行时事实卡片。

当前共享实现约定：

- `Mission Intake` / `Mission Cockpit`、`Triage`、`Story Workspace`、`Route Manager` 现在都通过同一套 operator-guidance surface 输出“动作原因 / 下一步 / 解释归属”。
- 运行时原因继续复用 mission suggestion、retry advice、duplicate explain、story delivery status、route health 等现有事实源，而不是在浏览器端重新推导一套解释。
- 参数语义仍只以本文档为准；这些 shared surface 只负责引用和投影，不负责重新定义字段含义。

## 跨控制面的 Digest 默认配置约定

这部分不是当前浏览器表单已落地字段，而是仓内已冻结的后续共享 contract。等浏览器补入 digest onboarding 时，字段语义必须与 CLI / MCP 一致。

| 共享字段 | 共享 noun | 含义 | 示例 |
| --- | --- | --- | --- |
| `Digest Language` | `digest_profile.language` | 摘要默认语言/本地化偏好 | `en` / `zh-CN` |
| `Digest Timezone` | `digest_profile.timezone` | 摘要时间解释与展示时区 | `UTC` / `Asia/Shanghai` |
| `Digest Frequency` | `digest_profile.frequency` | 默认 digest 运行节奏 | `@daily` |
| `Default Delivery Target` | `digest_profile.default_delivery_target` | 默认交付去向；优先使用命名 route 引用 | `route:ops-webhook` |

约束：

- 这四个字段组成一份共享的 first-run `digest_profile`，不是 CLI 一套、浏览器一套。
- 浏览器如果后续提供 onboarding，只是编辑同一份共享 profile，而不是发明 GUI-only digest setup。
- `Default Delivery Target` 应优先指向命名 route；channel secrets 仍属于 route 配置，不进入 first-run digest onboarding。
- 如果共享 `digest_profile` 已存在，浏览器应把它当作可编辑默认值，而不是重新弹出一套独立新手流程。

## Prompt Pack 解析顺序约定

后续 digest 渲染必须使用显式、可观察的 prompt 解析顺序：

1. `repo_default_pack`
2. `local_prompt_overrides`
3. `per_run_overrides`

补充说明：

- repo 默认 digest pack 名称固定为 `digest_delivery_default`。
- `local_prompt_overrides` 指 operator 本地显式文件，例如 `~/.datapulse/prompts/...`，不是浏览器本地存储里的隐式状态。
- `per_run_overrides` 指某次 CLI / MCP / 未来浏览器动作显式提供的覆盖，只影响当前一次 digest 准备。
- 浏览器后续如果显示 prompt readiness，应显示解析后的 pack / file provenance，而不是单独维护一份前端 prompt 状态。

## First-Run Onboarding 语义

共享 `digest_profile` 的首次建立应遵循同一顺序：

1. 当前 run 如果已经显式提供 `language`、`timezone`、`frequency`、`default_delivery_target`，则直接使用，不额外开启 onboarding。
2. 如果仓内已存在共享 `digest_profile`，则复用其值作为默认配置。
3. 只有在没有共享 profile 且当前 run 也没给全字段时，CLI / MCP / 浏览器才需要补采这四项。
4. 浏览器语言或系统时区只能作为预填建议，用户确认前不算 repo truth。

## 字段说明

| 控制台字段 | 是否必填 | 实际写入字段 | 填写建议 | 示例 |
| --- | --- | --- | --- | --- |
| `Name` | 是 | `name` | 任务名称，建议写成稳定、可辨识的 mission 名称 | `Launch Ops` |
| `Schedule` | 否 | `schedule` | 留空即 `manual`；支持 `@hourly` / `@daily` / `@weekly` / `interval:15m` / `every:30m` | `@hourly` |
| `Query` | 是 | `query` | 任务主查询词；建议写主题、公司、人物、产品名 | `OpenAI launch` |
| `Platform` | 否 | `platforms[0]` | 当前表单只支持单个平台；留空表示不限定平台 | `twitter` |
| `Alert Domain` | 否 | `alert_rules[0].domains[0]` | 这是==告警过滤域名==，不是 mission 的 `sites` 搜索范围 | `openai.com` |
| `Alert Route` | 否 | `alert_rules[0].routes[0]` | 对应命名告警路由，需先在 `DATAPULSE_ALERT_ROUTING_PATH` 配置 | `ops-webhook` |
| `Alert Keyword` | 否 | `alert_rules[0].keyword_any[0]` | 告警命中时要求结果文本至少包含该关键词之一 | `launch` |
| `Min Score` | 否 | `alert_rules[0].min_score` | 告警最低分阈值；建议从 `60~80` 起试 | `70` |
| `Min Confidence` | 否 | `alert_rules[0].min_confidence` | 告警最低置信度阈值；通常填 `0.6~0.9` | `0.8` |

## 关键行为说明

### 1. 什么情况下会创建 alert rule

当前控制台只有在以下任一字段被填写时，才会自动创建 `console-threshold` 这条 alert rule：

- `Alert Route`
- `Alert Keyword`
- `Alert Domain`
- `Min Score > 0`
- `Min Confidence > 0`

如果这些字段全部留空，则只创建 watch mission，不创建 alert rule。

### 2. `Alert Domain` 不是搜索站点范围

当前浏览器表单里的 `Alert Domain` 写入的是：

```json
{
  "alert_rules": [
    {
      "domains": ["openai.com"]
    }
  ]
}
```

它只影响告警命中条件，不会把 mission 的搜索/抓取范围限制到该域名。

如果你需要真正的站点范围限定，请暂时使用：

- CLI：`--watch-site`
- MCP / API：`sites`

### 3. `Platform` 当前只支持单值

浏览器表单当前只有一个 `Platform` 输入框，因此最终会生成单元素数组：

```json
{
  "platforms": ["twitter"]
}
```

如果你需要一个 mission 同时覆盖多个平台，请暂时使用 CLI / MCP / API。

### 4. 默认 alert channel

浏览器表单当前创建的 alert rule 默认包含：

```json
{
  "channels": ["json"]
}
```

这意味着：

- 告警事件会先写入本地 alert store
- 如果额外填写了 `Alert Route`，会再尝试走命名 route 分发

### 5. Mission Cockpit 如何更新规则

浏览器里有两条写路径：

- `Deploy Mission`：`POST /api/watches`
- `Mission Cockpit -> Save Alert Rule / Clear Alert Rules`：`PUT /api/watches/{id}/alert-rules`

其中 `Save Alert Rule` 会用当前表单内容整体替换这个 mission 的规则列表；`Clear Alert Rules` 会提交空数组 `[]`。

## 推荐填写模板

### 模板 A：只建 mission，不发告警

适合先观察结果、暂不触发任何告警。

- `Name`: `AI Radar`
- `Schedule`: `@hourly`
- `Query`: `OpenAI agents`
- `Platform`: `twitter`
- 其余 alert 字段全部留空

结果：

- 创建 watch mission
- 不创建 alert rule

### 模板 B：定时监控 + 基础阈值告警

- `Name`: `Launch Ops`
- `Schedule`: `@hourly`
- `Query`: `OpenAI launch`
- `Platform`: `twitter`
- `Alert Route`: `ops-webhook`
- `Alert Keyword`: `launch`
- `Alert Domain`: `openai.com`
- `Min Score`: `70`
- `Min Confidence`: `0.8`

适合高价值主题监控。

### 模板 C：人工触发的临时观察任务

- `Name`: `Infra Manual Review`
- `Schedule`: 留空
- `Query`: `LLM inference infra`
- `Platform`: 留空
- alert 字段按需填写

结果：

- mission 为 `manual`
- 只会在你手动点击 `Run Mission` 或通过其他控制面执行时运行

## 对应 API payload 示例

当你填写：

- `Name = Launch Ops`
- `Schedule = @hourly`
- `Query = OpenAI launch`
- `Platform = twitter`
- `Alert Route = ops-webhook`
- `Alert Keyword = launch`
- `Alert Domain = openai.com`
- `Min Score = 70`
- `Min Confidence = 0.8`

浏览器当前会生成等价请求：

```json
{
  "name": "Launch Ops",
  "query": "OpenAI launch",
  "schedule": "@hourly",
  "platforms": ["twitter"],
  "alert_rules": [
    {
      "name": "console-threshold",
      "min_score": 70,
      "min_confidence": 0.8,
      "channels": ["json"],
      "routes": ["ops-webhook"],
      "keyword_any": ["launch"],
      "domains": ["openai.com"]
    }
  ]
}
```

## 与其他控制面的关系

浏览器表单适合：

- 快速建一个 mission
- 快速附加一个基础告警条件
- 在浏览器里完成 mission -> triage -> story -> route 的首轮操作路径
- 本地单用户试运行

CLI / MCP / API 更适合：

- 批量创建 mission
- 多平台 / 多规则配置
- 精细 alert filter
- 更复杂的自动化编排

## 相关文档

- [GUI 控制台规划](gui_intelligence_console_plan.md)
- [数据源与订阅化增强计划](source_feed_enhancement_plan.md)
- [README](../README.md)
