# Issue #47/#48 高置信 HA 交付事实（Decisive）

- 交付时间（UTC）：`2026-03-09`
- 关联 Issue：
  - `https://github.com/sunyifei83/DataPulse/issues/47`
  - `https://github.com/sunyifei83/DataPulse/issues/48`
- 交付结论：`HA-DONE / DECISIVE`

## 1. 事实输入（Issue 复核）

- #47：仓库根目录缺少 OpenClaw skill 发现所需的 `SKILL.md`，且缺少 YAML frontmatter，导致 skill 不被识别。
- #48：通过 `datapulse_skill.run()` 读取 HTTPS URL 时，`GenericCollector` 首次请求可能触发 `SSL CERTIFICATE_VERIFY_FAILED` warning，虽然 Jina fallback 最终能成功返回结果。

## 2. 实现事实（代码）

- `SKILL.md`
  - 在仓库根目录新增 OpenClaw 可识别的 skill 描述文件。
  - 补齐 YAML frontmatter：`name`、`description`、`metadata.openclaw.requires.bins=["python3"]`。
  - 补齐最小可用说明：适用场景、Python 入口、能力说明、环境备注。

- `datapulse/collectors/generic.py`
  - 新增 `_build_ssl_context()`：
    - 显式加载系统默认信任根；
    - 叠加 `requests` 自带 CA bundle；
    - 可选叠加 `DATAPULSE_CA_BUNDLE` 指向的自定义 CA。
  - 新增 `_build_http_session()`：
    - 通过自定义 `HTTPAdapter` 将合并后的 `ssl_context` 绑定到 `requests.Session`。
  - `_fetch_html()` 改为使用该 session 发起请求，避免 `requests` 仅依赖单一证书来源导致的 HTTPS 验证失败。

## 3. 测试与复现事实

- 新增测试：`tests/test_skill_packaging.py`
  - 覆盖：仓库根 `SKILL.md` 存在且包含 OpenClaw 所需 frontmatter。

- 新增测试：`tests/test_generic_collector_ssl.py`
  - 覆盖：
    - SSL context 加载系统 trust roots 与 `requests` CA bundle；
    - `DATAPULSE_CA_BUNDLE` 自定义 CA 覆盖；
    - `GenericCollector._fetch_html()` 使用显式 session 请求链路。

- 自动化验证：
  - `uv run pytest tests/test_generic_collector_ssl.py tests/test_skill_packaging.py -q` → `4 passed`
  - `uv run pytest tests/test_collectors.py tests/test_doctor.py tests/test_generic_collector_ssl.py tests/test_skill_packaging.py -q` → `93 passed`
  - `uv run ruff check datapulse/collectors/generic.py tests/test_generic_collector_ssl.py tests/test_skill_packaging.py datapulse_skill/__init__.py` → `All checks passed`

- 实链复现：
  - 命令：
    - `DATAPULSE_LOG_LEVEL=INFO uv run python - <<'PY'`
    - `from datapulse_skill import run`
    - `print(run("read https://example.com"))`
    - `PY`
  - 结果：
    - `Routing with generic for https://example.com`
    - 返回标题 `Example Domain`
    - 未再出现 `SSL CERTIFICATE_VERIFY_FAILED` warning
    - `GenericCollector` 直接成功，不再依赖 Jina fallback 才拿到结果

## 4. Decisive 判定

- 判定标准（本次 issue 级）：
  - 问题陈述可复现；
  - 根因已落到代码修复；
  - 自动化测试覆盖新增行为；
  - 实链复现与 issue 预期一致。
- 结论：`DECISIVE`
  - #47：OpenClaw skill 发现入口已恢复；
  - #48：`datapulse_skill.run()` 的标准 HTTPS 读取路径已恢复到 `GenericCollector` 直连成功，无 SSL warning 噪音。

## 5. Inescapable 交付与 Assured 部署说明

- Inescapable 交付：
  - skill 包装契约与 HTTPS 读取路径均被代码、测试、实链复现三者同时覆盖。
- Assured 部署：
  - 根目录 `SKILL.md` 现已满足 OpenClaw 发现前提；
  - HTTPS 读取链路已改为系统 trust roots + requests CA bundle + optional custom CA 的合并方案；
  - 若环境存在企业私有 CA，可通过 `DATAPULSE_CA_BUNDLE` 继续追加，不影响默认链路。
