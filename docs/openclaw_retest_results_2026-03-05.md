# OpenClaw 线索复测结果（补修复后）

- 复测日期：`2026-03-05`
- 目标：上轮未通过 case
  - `#19_search_runtime_smoke`
  - `#21_twitter_content_fallback`

## 复测结论

1. `#19_search_runtime_smoke`：`PASS`
- 现象：`provider=auto` 在 Jina key 缺失时不再直接抛异常，触发自动降级后返回列表结果（本次 `count=2`）。
- 关键日志：`Auto search fallback triggered: Jina API key required for search...`
- 修复点：`datapulse/reader.py` 自动降级路径兼容缺 key 场景。

1. `#21_twitter_content_fallback`：`PASS`
- 现象：目标推文读取结果 `parser=twitter+jina_fallback`，`content_len=8317`，`thin_content` 因子已消除。
- 关键字段：`fallback_parser=jina_reader_t8`
- 修复点：
  - `datapulse/reader.py` 增加多级回填（Jina timeout 扩展 + direct r.jina.ai）
  - `datapulse/collectors/twitter.py` 增加 FxTwitter 文本字段兜底。

## 代码提交锚点

- 对应提交：待本次提交落盘后补充 commit id
- 影响文件：
  - `datapulse/reader.py`
  - `datapulse/collectors/twitter.py`
