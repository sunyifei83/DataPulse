---
title: Test Facts
---

<a id="top"></a>

# Test Facts / 测试事实

[🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md) | [⬆️ 回到顶部](#top)

## Fact 1: Configuration policy / 配置规范

本仓库不公开本地测试环境和模型端点明文；敏感项仅允许在私有运行时注入。
- Repository policy: no plaintext local test environment/model endpoint values are published in-repo.

## Fact 2: Functionality verification / 功能验证

建议先执行 `datapulse` CLI 单测 → 批量测试 → `datapulse-smoke --list/--platforms` 验证平台适配度。
- Recommended order: CLI single URL checks → batch checks → `datapulse-smoke --list/--platforms`.

[⬆️ Back to top / 返回顶部](#top) | [🔙 返回主 README](../README.md) | [🔄 中文对照/English](../README_CN.md)
