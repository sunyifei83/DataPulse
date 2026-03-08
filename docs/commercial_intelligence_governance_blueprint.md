# 商业情报收集与治理蓝图（DataPulse Repo 适配版）

## 目的

这份文档不是对“商业行业情报收集与情报治理范式”原文的复述，而是把其中可落入 DataPulse 仓库的部分压成可执行蓝图。

适配后的核心判断只有一条：

- DataPulse 当前更像一个“公开来源情报采集、处置、证据化、分发与治理底座”，而不是一个覆盖付费数据库采购、线下访谈、人脉网络经营、ERP/CRM 深集成的完整企业情报中台。

因此，原文中真正 repo-relevant 的部分，应被重写为：

1. 什么来源与收集方式属于仓内可治理范围
2. 这些来源如何映射到现有对象与流程
3. 仓内还缺哪几层治理与契约
4. 哪些 follow-up slices 值得进入蓝图并交给后续 loop 点火

## Repo 边界

### 当前可承接的情报能力

- 公开网页、RSS、论坛、社媒、视频平台、热搜趋势等公开来源采集
- 通过 `SearchGateway` 统一接入 Web 搜索 provider
- 通过 `SourceCatalog` 管理来源目录、pack 和 profile 订阅
- 通过 `WatchMission` 持久化情报需求、调度策略与告警规则
- 通过 `DataPulseItem -> triage -> Story -> AlertEvent/route` 形成从信号到证据包再到分发的链路
- 通过仓内治理蓝图与 slice loop 管理路线推进
- 通过外部 fact intake 将分析师笔记或外部事实显式转入 repo blueprints

### 当前不应伪装为已承接的能力

- 付费商业数据库直接接入与合规采购治理
- 线下人脉、专家访谈、客户/供应商访谈管理
- 企业内部 ERP / CRM / OA 深度集成
- 涉及个人隐私、员工监控或非公开数据的情报采集
- 对网站抓取合法性作自动法律判断

仓内更合理的姿态是：

- 对公开来源情报给出“采集边界、治理边界、证据边界、分发边界”
- 对外部私有情报保留“人工导入后的事实引用能力”
- 不把 repo 误包装成全栈企业情报平台

## 原文到 Repo 的对象映射

| 原文维度 | DataPulse 对应层 | 当前锚点 |
| --- | --- | --- |
| 情报来源 | 来源目录、订阅范围、搜索/抓取入口 | `datapulse/core/source_catalog.py`、`datapulse/core/search_gateway.py`、各 collector |
| 收集方法 | URL 解析、搜索、watch 调度、外部事实导入 | `datapulse/reader.py`、`datapulse/core/watchlist.py`、`scripts/governance/intake_external_fact_to_working_slice.py` |
| 数据处理 | 去重、评分、归档、review state | `datapulse/core/models.py`、`datapulse/core/triage.py` |
| 分析生产 | digest、story、entity graph、export | `datapulse/core/story.py`、`datapulse/reader.py` |
| 分发传播 | alert、named route、feed、story export | `datapulse/core/alerts.py`、`docs/intelligence_delivery_contract.md` |
| 治理范式 | blueprint plan、slice catalog、promotion loop | `docs/governance/*`、`scripts/governance/*` |

这意味着，原文里的“商业情报治理”在仓内应被理解为：

`source policy -> mission intent -> collection -> normalization -> triage -> story/evidence -> delivery -> feedback`

而不是只有“采集更多数据”。

## 升维后的治理判断

### 1. DataPulse 缺的不是更多 collector，而是来源治理层

仓内已经具备较丰富的公开来源采集能力，但还缺少一套明确的来源治理契约，至少应回答：

- 这个来源是公开网页、平台 API、搜索网关、人工导入，还是外部事实引用
- 这个来源的收集模式是直接抓取、API、搜索聚合、人工录入，还是混合
- 这个来源的可信度、时效预期、抓取脆弱度、敏感度、合规风险如何标注
- 哪些来源允许自动化任务化采集，哪些只允许人工或半人工使用

如果没有这一层，`SourceCatalog` 只是“可用源列表”，还不是“可治理的情报源目录”。

### 2. DataPulse 缺的不是搜索入口，而是需求定向层

原文里的 `KITs / KIQs` 对应到仓内，不应直接抄术语，而应落成 mission 级“需求定向契约”：

- 这条 `WatchMission` 服务什么问题
- 预期观测哪些竞争对象、主题、区域、时间窗
- 对 freshness、coverage、precision 的最低要求是什么
- 哪些 alert 代表“值得升级为 triage 或 story”

如果没有这层，`WatchMission` 更像“保存查询”，还不是“面向决策问题的情报任务”。

### 3. DataPulse 缺的不是 story 能力，而是证据治理闭环

仓内已经有 triage 和 story，但还缺少更完整的治理语义：

- 来源可信度与 review state 如何共同影响证据等级
- 敏感信息、未证实信号、冲突信号如何标注
- story export 和 alert route 在分发前应保留哪些 provenance 与风险提示
- 哪些运维指标真正代表“情报产品有效”，而不仅是“抓到了多少条”

如果没有这一层，story 只是证据聚合器，还不是“可被治理的情报产品”。

### 4. AI 在本仓更适合作为治理加速器，而不是越权代理

原文提到 AI 驱动的主动推送、预测与生成，这在 DataPulse 内更合理的落点是：

- 生成 mission 建议、补全 query / platform / site 组合
- 生成 triage explain、story 初稿、route 摘要
- 发现重复任务、来源覆盖空洞、告警噪声异常

不合理的落点是：

- 自动越过来源边界或合规边界
- 自动把未证实信号提升为高可信结论
- 自动替代人工对敏感性、合法性、业务价值的判断

仓内应先把 AI 放进治理护栏内，再谈更强自动化。

## 对中国本土实践的 Repo 解释

原文中的“中国本土实践”在仓内可转写为三类要求：

1. 平台现实
   `wechat / xhs / bilibili / telegram` 等平台采集脆弱度、会话依赖与 fallback 机制需要被视作来源治理的一部分，而不是采集实现细节。

2. 合规现实
   公开来源自动化采集必须保留“公开性、协议、速率、敏感性”的显式边界，不能把“技术上可抓”误等同于“治理上可用”。

3. 部署现实
   本地化环境、国产化替代、密钥与代理配置治理，需要继续通过运行时配置、secret redaction、route health 来实现，而不是散落在脚本里。

## 建议纳入仓内蓝图的 Follow-up Slices

### L8.1 已落地基线

- 产物：`docs/commercial_intelligence_governance_blueprint.md`
- 作用：把原文压成 repo 适配后的总纲，而不是让外部商业情报方法论直接绕过蓝图进入实现层

### L8.2 来源治理契约

目标：
为公开来源情报建立 `source class / collection mode / authority / sensitivity / compliance hint` 的统一契约。

repo 锚点：

- `datapulse/core/source_catalog.py`
- `datapulse/core/models.py`
- `docs/search_gateway_config.md`

预期结果：

- `SourceCatalog` 从“来源列表”升级为“可治理来源目录”
- 后续 collector、search gateway、triage 都能复用统一来源语义

### L8.3 需求定向与任务语义升级

目标：
把原文中的 `KIT/KIQ` 思路投影到 `WatchMission`，形成更强的需求定向层。

repo 锚点：

- `datapulse/core/watchlist.py`
- `datapulse/reader.py`
- `docs/intelligence_lifecycle_contract.md`

预期结果：

- mission 不再只是 query 保存器
- watch / alert / story 能围绕“问题定义、覆盖目标、时效目标”形成统一语义

### L8.4 证据与分发治理契约

目标：
把来源可信度、review state、story provenance、route delivery 风险提示串成一套证据治理语义。

repo 锚点：

- `datapulse/core/triage.py`
- `datapulse/core/story.py`
- `datapulse/core/alerts.py`
- `docs/intelligence_delivery_contract.md`

预期结果：

- triage、story、delivery 不再只共享对象名，也共享治理级别与风险边界
- 分发层能够保留“证据级别”和“可操作但未最终证实”的区别

### L8.5 治理反馈与运营记分板

目标：
把情报体系的“评估与反馈”落成 repo 级 scorecard，而不是只看抓取成功率。

repo 锚点：

- `datapulse/reader.py`
- `datapulse/console_server.py`
- `docs/gui_intelligence_console_plan.md`

预期结果：

- ops 面能看到 coverage、freshness、alert yield、source mix、triage throughput、story conversion 一类治理指标
- 后续 AI 建议与 loop 优先级有可依赖的反馈面

## 切片排序原则

建议顺序如下：

1. 先定义来源治理契约，再改模型或 collector
2. 先把 mission 的需求定向层补齐，再扩展 alert 和 story 的升级逻辑
3. 先明确证据与分发治理边界，再做更主动的 AI 推荐或自动推送
4. 最后再补运营 scorecard，让反馈指标建立在前述统一语义之上

## 结论

这份外部材料对 DataPulse 最有价值的，不是“再加一些抓取源”，而是推动仓内完成四件事：

- 给来源加治理语义
- 给 mission 加需求语义
- 给 evidence/delivery 加风险与 provenance 语义
- 给 ops 面加情报价值反馈语义

只有这样，DataPulse 才会从“公开来源情报工具箱”继续向“可治理的商业情报底座”演进。
