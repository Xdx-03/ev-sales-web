# EV Sales Web 与移动 H5 自动化测试框架

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-8%2F9-0A9EDC)](https://pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-2EAD33)](https://playwright.dev/python/)
[![Suite Validation](https://github.com/Xdx-03/ev-sales-web/actions/workflows/suite-validation.yml/badge.svg)](https://github.com/Xdx-03/ev-sales-web/actions/workflows/suite-validation.yml)

面向新能源汽车销售管理端 Web 与客户移动 H5 的 Python 黑盒 UI 自动化项目。框架使用 pytest + Playwright，按客户端和业务功能组织，强调场景可读性、页面定位集中维护、环境与凭据分离，以及经过用户名、密码和手机号脱敏的失败证据。

## 当前覆盖

| 客户端 | 代表性场景 | 数量 |
| --- | --- | ---: |
| 管理端 Web | 登录/退出、4 个受保护路由、车型/订单/售后导航 | 12 |
| 移动 H5 | 展厅、登录校验、匿名权限、客户登录态、本人订单列表 | 16 |
| 合计 | 可收集的真实浏览器 UI 场景 | 28 |

移动 H5 的 8 个业务场景分别使用 Pixel 7 和 iPhone 13 浏览器设备参数执行，因此形成 16 个独立结果。iPhone 13 参数仅表示 Chromium 中的视口、触控和 User-Agent 仿真，不代表真实 iOS、Safari、原生 App 或 Appium 测试。

项目不包含被测产品的源码级单元测试或 Mock 业务接口测试。独立的 `framework_checks/` 使用临时 pytest 套件和受控 BrowserContext 替身验证测试框架的清理与结果契约，单独统计。Android/iOS Appium 和微信小程序自动化均暂未开始。

## 当前验证状态

| 检查项 | 状态 | 真实结果 |
| --- | --- | --- |
| Ruff、格式、Mypy、Python 编译 | 已通过 | 本地实际执行 |
| pytest 场景收集 | 已通过 | 28 collected |
| 框架契约检查 | 本地已通过 | 2026-09-11：31 passed、0 failed、0 skipped；合成结果，不包含浏览器业务 |
| 管理端 Web 隔离回归 | 已通过 | 2026-08-22：同次完整回归中 12/12 通过 |
| 移动 H5 隔离回归 | 已通过 | 2026-08-22：同次完整回归中 16/16 通过 |
| Web + H5 完整回归 | 已通过 | 2026-08-22：28 passed、0 failed、0 skipped，45.64 秒 |
| Jenkins 参数化流水线 | 代码已完成，暂未实跑 | 需在真实 Jenkins 配置凭据和执行节点后验证 |
| Android/iOS Appium | 暂未开始 | 当前没有 APK/IPA、应用标识和设备环境 |

历史完整回归运行 ID 为 `web-20260821T163540Z-2fc867d4`，使用本地 Docker 隔离环境和 Chromium 驱动 + 本机 Chrome 通道。本轮框架改进未复跑真实浏览器业务；`pytest --collect-only` 只代表场景可被发现。执行器拒绝零用例、跳过、失败/错误以及缺失或损坏的 JUnit，并保留 pytest 非零退出码。每条业务场景的步骤、预期和历史执行结果见 [测试用例清单](evidence/test-cases.csv)。

## 无需浏览器的可复现验证

以下命令实际执行框架检查，不需要安装 Chromium、启动 Web/H5 服务或配置账号：

```bash
python -m pip install -r requirements-dev.txt
python -m pytest framework_checks -q --junitxml=reports/framework-checks.xml
```

| 可核验能力 | 检查方式 | 能证明的边界 |
| --- | --- | --- |
| 资源释放 | 真正的 pytest 进程使用受控 BrowserContext 替身 | 页面或超时初始化失败、采证失败后仍关闭管理端/H5上下文 |
| 故障证据 | 合成目录错误、截图错误和 Allure 错误 | 采证故障不覆盖原测试失败，异常诊断不输出敏感原文 |
| 清理与退出状态 | 临时目录中的合成 pytest 套件、受控链接属性 | 报告路径先验证再清理，报告参数由 runner 固定，异常结果不能误报成功 |

默认 `pytest.ini` 继续收集 28 条业务场景；框架检查使用显式目录执行，JUnit 与真实 UI 回归分开。Actions 上传 `web-framework-checks-junit` 合成结果产物，框架检查成功不代表浏览器业务通过。

上述本地框架检查使用 Windows / Python 3.11，包括真实 Windows junction 拒绝检查；Linux CI 将使用符号链接检查同一清理边界。线上执行状态以 Actions 为准。

## 架构

```text
tests（业务场景与断言）
  |
flows（跨页面业务流程）
  |
pages（按客户端和功能组织的 Page Object）
  |
Playwright（浏览器驱动、设备参数、条件等待）
  |
隔离的管理端 Web / 客户移动 H5 测试环境
```

- `tests/`：只描述业务场景、步骤和预期结果。
- `framework_checks/`：框架契约与资源生命周期检查，不启动真实浏览器。
- `ev_web/flows/`：复用登录等跨页面流程，避免测试复制操作细节。
- `ev_web/pages/`：集中维护定位器和页面交互，按管理端和移动端功能拆分。
- `ev_web/config.py`：统一加载环境地址、超时和测试账号，并执行启动校验。
- `tests/conftest.py`：管理浏览器上下文、设备参数和失败证据。
- `run_web_tests.py`：清理旧结果、透传 pytest 参数并保留真实退出码。
- `Jenkinsfile`：参数化选择环境、测试范围和浏览器来源。
- `artifacts/`、`allure-results/`、`reports/`：运行产物，全部排除在 Git 之外。
- `evidence/`：可公开复核的测试用例清单，不包含账号、Token 或真实业务数据。

## 本地运行

要求 Python 3.11+。首次安装依赖和 Playwright Chromium：

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

复制空配置模板，真实环境信息只写入被 Git 忽略的本地文件：

```bash
cp config/env.example.yaml config/env.yaml
```

运行冒烟、H5 或完整 UI 场景：

```bash
python run_web_tests.py --config config/env.yaml --env default -m smoke --browser chromium
python run_web_tests.py --config config/env.yaml --env default -m "mobile and h5" --browser chromium
python run_web_tests.py --config config/env.yaml --env default -m "ui and live" --browser chromium
```

本地节点已有 Google Chrome 时可以显式使用其通道：

```bash
python run_web_tests.py --config config/env.yaml --env default -m h5 --browser chromium --browser-channel chrome
```

`--slowmo` 只用于人工调试，不进入 CI。测试代码禁止固定 `sleep`，等待由 Playwright 的定位器和断言完成。

## 环境配置

配置优先级为“环境变量 > 所选 YAML 环境”。默认读取 `config/env.yaml` 的 `default`；也可通过 `--config` 和 `--env` 选择其他配置文件及环境。

| 环境变量 | 作用 |
| --- | --- |
| `EV_TEST_ENV` | 选择 YAML 环境，默认 `default` |
| `EV_WEB_BASE_URL` | 管理端地址 |
| `EV_H5_BASE_URL` | 客户移动 H5 地址 |
| `EV_WEB_ADMIN_USERNAME` | 隔离环境管理员账号 |
| `EV_WEB_ADMIN_PASSWORD` | 隔离环境管理员密码 |
| `EV_H5_CUSTOMER_PHONE` | 隔离环境客户测试手机号 |
| `EV_WEB_HEADLESS` | 是否无头运行 |
| `EV_WEB_NAVIGATION_TIMEOUT_MS` | 页面导航超时 |
| `EV_WEB_ACTION_TIMEOUT_MS` | 页面操作和断言超时 |

非本地地址携带测试账号执行时强制要求 HTTPS。禁止连接生产环境，禁止使用个人账号或生产数据。

## Jenkins 环境选择

Jenkins 参数用于选择已经维护好的配置，不在构建页面重复输入真实地址和账号：

| 参数 | 可选值 | 用途 |
| --- | --- | --- |
| `TEST_ENV` | `test` / `staging` | 选择隔离测试环境 |
| `TEST_SUITE` | `smoke` / `critical` / `mobile-h5` / `all-ui` | 选择测试范围 |
| `BROWSER_SOURCE` | `playwright-chromium` / `system-chrome` | 选择浏览器来源 |
| `RUN_LIVE_TESTS` | `false` / `true` | 显式控制是否连接真实测试环境 |

在 Jenkins Credentials 中分别创建 Secret File：

- `ev-sales-web-test-config`
- `ev-sales-web-staging-config`

测试环境的 Secret File 使用 `test` 作为顶层键，预发布环境使用 `staging`。文件结构如下，尖括号内容由环境维护者填写：

```yaml
test:
  web:
    base_url: "<https-management-test-url>"
    h5_base_url: "<https-h5-test-url>"
    navigation_timeout_ms: 15000
    action_timeout_ms: 8000
    headless: true
    viewport_width: 1440
    viewport_height: 900
  accounts:
    admin:
      username: "<dedicated-test-admin>"
      password: "<rotatable-test-password>"
    mobile_customer:
      phone: "<synthetic-test-phone>"
```

地址、账号或密码变化时只更新对应 Jenkins Secret File，不修改测试代码。`RUN_LIVE_TESTS=false` 时流水线只做 Ruff、格式、Mypy、编译和 28 条场景收集；开启后才安装/选择浏览器并运行所选环境。所选套件缺少必需账号或出现任何跳过场景时构建失败，避免把静态检查或不完整执行误报成真实回归。

## 测试标记

| Marker | 含义 |
| --- | --- |
| `ui` | 浏览器 UI 黑盒场景 |
| `live` | 需要已运行的完整测试环境 |
| `smoke` | 快速高价值检查 |
| `regression` | 较完整的功能回归 |
| `critical` | 发布阻断级关键链路 |
| `auth` | 登录认证 |
| `permission` | 访问控制与路由守卫 |
| `mobile` | 移动设备参数下的浏览器场景 |
| `h5` | uni-app H5 场景 |

## 失败证据与质量门禁

失败时保存全页截图和页面 HTML，并附加到 Allure 结果。敏感输入在证据采集前清空；报告只允许使用隔离环境的虚构测试数据，并由受控 CI 保存，禁止提交公开仓库。

- GitHub Actions `Suite Validation`：push/PR 执行 Ruff、格式、Mypy、编译、合成框架检查和业务场景收集，上传独立框架 JUnit。
- GitHub Actions `Live UI Regression`：仅手动触发，通过 Secrets 注入隔离环境账号并执行真实 UI 场景。
- Jenkins：通过 Secret File 管理多个环境，通过参数选择环境、套件和浏览器，默认不执行 Live 回归。

| 质量属性 | 项目约束 | 自动检查 |
| --- | --- | --- |
| 可维护性 | 用例、Flow、Page Object、配置和运行器职责分离 | Ruff、Mypy、场景收集 |
| 可读性 | 使用业务命名；单个测试表达一个可识别行为 | Ruff 命名与格式规则 |
| 可扩展性 | 新客户端使用独立 fixture/Page Object；新模块按功能目录增加 | 分层目录、严格 Marker |
| 灵活性 | 地址、凭据、浏览器和超时由 YAML、环境变量及命令行注入 | 配置启动校验 |
| 简洁性 | 只抽取已经重复且稳定的行为；圈复杂度不超过 10 | Ruff C90、PLR |
| 可复用性 | 跨页面流程进入 Flow；同类页面复用公共契约 | 代码审查、静态检查 |
| 可测试性 | BrowserContext 隔离；禁止顺序依赖、固定等待和静默重试 | pytest 严格 Marker、CI |

定位器只放在 Page Object；跨页面动作放在 Flow；测试保留业务结果断言；凭据不得进入源码。没有稳定复用需求时不新增抽象层，避免为“可扩展”制造复杂度。
