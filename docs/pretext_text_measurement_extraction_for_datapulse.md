# Pretext 文本测量引擎摘取（供 Datapulse 落库）

## 结论（高价值结论）
`Pretext` 的高价值不是“另一个 truncate”，而是“**两阶段测量 + 多语言排版规则 + 缓存化**”。
在本仓库（Datapulse）可优先吸收的能力主要是：

1. **前端文本布局性能模板**：`prepare(text, font)` 只做一次预处理+测量，后续 `layout(...)` 只做纯算术。
2. **多语言/多脚本分段策略**：Intl.Segmenter + CJK/阿拉伯/符号规则，减少宽度误判。
3. **换行/回车/破词策略显式模型化**：`space/preserved-space/tab/zero-width-break/soft-hyphen/hard-break` 等类型。
4. **字符级宽度回退（break-word）路径**：可测每个 grapheme 的宽度并做超窄容器下字符级切分。
5. **emoji 校正与 UA profile**：`measureText` 与真实 DOM 渲染误差通过 correction 缓存修正。

## 相关源码入口（摘自 chenglou/pretext）

- `src/layout.ts`：`prepare`、`prepareWithSegments`、`layout`、`layoutWithLines`、`walkLineRanges`、`layoutNextLine`、`clearCache`、`setLocale`。
- `src/measurement.ts`：`getMeasureContext`、`getSegmentMetrics`、`getCorrectedSegmentWidth`、`getSegmentGraphemeWidths`、`getSegmentGraphemePrefixWidths`、`clearMeasurementCaches`。
- `src/analysis.ts`：`analyzeText`（空白规则、段类型标注、URL/数字/标点合并逻辑）
- `src/line-break.ts`：`walkPreparedLines`、`countPreparedLines`、`fitSoftHyphenBreak`。

## 可直接补强 Datapulse 的优先级

### P0（立刻可落地）
- 新增“**多脚本友好字符串截断**”辅助函数：不只按字符数切分，至少按 Unicode grapheme 级别切断，避免 emoji/合字断裂。
- 在 `datapulse/core/utils.py` 增加 `truncate_text_preserving_graphemes(text, max_units, suffix='…')` 供 `report`、`console` 卡片摘要统一调用。

### P1（前端增强）
- 在 `datapulse/console_markup.py` 中补充轻量 canvas 文本测量缓存：
  - `getTextWidth(text, font)` + 按 `font+segment` 缓存。
  - `fitTextToWidth(text, maxPx, font)`。
- 用于前端导航/卡片/徽标行超长文案的“真实像素级收缩”，替代 CSS `text-overflow` 在复杂字符场景下的不一致。

### P2（结构性增强）
- 抽一个 mini 版 `pretext` 的“prepare/layout 思想”到独立模块：
  - 阶段1：文本归一化 + 分段
  - 阶段2：缓存测量结果 + 快速重排
- 将其用在可能有大量动态卡片的界面刷新场景（story/trx/route 列表），避免每次 resize 时重复测量导致布局抖动。

## 为什么这部分是“高价值”

- 与 Datapulse 现状相比，当前主要为字符截断（`utils.generate_excerpt`），对表情、CJK 与混合脚本场景容易误差明显。
- console 的信息密度高，未来若要做移动端卡片压缩、行高计算、虚拟滚动/预排版，`pretext` 的分层测量模型会直接降低回流与抖动风险。
- 该能力可以先在 **前端** 落地（不改动采集链路），再视场景逐步下沉到后端输出层。

## 落库建议

- 本条目可直接转入 `Obsidian`（或任何 Markdown 知识库）后，作为 `Datapulse` 的前端性能与文本可视化优化子任务。
- 建议新建任务：`feat(ui): add grapheme-aware text clamp utilities`，再补一条子任务：`feat(ui): adopt pre-measurement layout cache for dense panels`。
