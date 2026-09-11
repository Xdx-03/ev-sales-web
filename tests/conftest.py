"""Shared browser lifecycle, configuration and failure evidence."""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from typing import Any

import allure
import pytest
from ev_web.config import PROJECT_ROOT, WebSettings, load_settings
from ev_web.flows.auth_flow import AuthFlow
from ev_web.flows.mobile_auth_flow import MobileAuthFlow
from ev_web.run_context import create_run_id
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

MOBILE_DEVICE_PROFILES = (
    pytest.param("Pixel 7", id="android-pixel-7"),
    pytest.param("iPhone 13", id="iphone-13"),
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ev-sales-web")
    group.addoption("--web-config", action="store", help="YAML 环境配置路径")
    group.addoption("--web-env", action="store", help="YAML 中的环境名称")


def pytest_configure(config: pytest.Config) -> None:
    run_id = create_run_id()
    os.environ["EV_TEST_RUN_ID"] = run_id


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> WebSettings:
    return load_settings(
        config_path=pytestconfig.getoption("--web-config"),
        environment=pytestconfig.getoption("--web-env"),
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(
    settings: WebSettings,
    pytestconfig: pytest.Config,
) -> dict[str, object]:
    launch_options: dict[str, object] = {"headless": settings.headless}
    if pytestconfig.getoption("--headed"):
        launch_options["headless"] = False
    if channel := pytestconfig.getoption("--browser-channel"):
        launch_options["channel"] = channel
    if slow_mo := pytestconfig.getoption("--slowmo"):
        launch_options["slow_mo"] = slow_mo
    return launch_options


@pytest.fixture(scope="session")
def browser_context_args(settings: WebSettings) -> dict[str, object]:
    return {
        "viewport": {
            "width": settings.viewport_width,
            "height": settings.viewport_height,
        },
        "locale": "zh-CN",
    }


@pytest.fixture
def ui_page(
    browser: Browser,
    browser_context_args: dict[str, object],
    settings: WebSettings,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    context, page = _new_page(browser, settings, browser_context_args)

    try:
        yield page
    finally:
        try:
            _capture_failure_evidence(page, request, "admin")
        finally:
            context.close()


@pytest.fixture(params=MOBILE_DEVICE_PROFILES)
def mobile_device_name(request: pytest.FixtureRequest) -> str:
    """Select an explicit mobile browser device profile for every H5 scenario."""
    return str(request.param)


@pytest.fixture
def mobile_page(
    browser: Browser,
    playwright: Playwright,
    settings: WebSettings,
    request: pytest.FixtureRequest,
    mobile_device_name: str,
) -> Generator[Page, None, None]:
    device_options = dict(playwright.devices[mobile_device_name])
    device_options.pop("default_browser_type", None)
    context, page = _new_page(browser, settings, device_options)

    try:
        yield page
    finally:
        try:
            _capture_failure_evidence(page, request, "mobile")
        finally:
            context.close()


@pytest.fixture
def authenticated_mobile_page(mobile_page: Page, settings: WebSettings) -> Page:
    MobileAuthFlow(mobile_page, settings).login_as_customer()
    return mobile_page


@pytest.fixture
def authenticated_page(ui_page: Page, settings: WebSettings) -> Page:
    settings.require_admin()
    AuthFlow(ui_page, settings).login_as_admin()
    return ui_page


def _new_page(
    browser: Browser,
    settings: WebSettings,
    context_options: dict[str, Any],
) -> tuple[BrowserContext, Page]:
    """Create an isolated page with the project's timeout policy."""
    context = browser.new_context(**context_options)
    try:
        context.set_default_timeout(settings.action_timeout_ms)
        context.set_default_navigation_timeout(settings.navigation_timeout_ms)
        return context, context.new_page()
    except BaseException:
        context.close()
        raise


def _capture_failure_evidence(
    page: Page,
    request: pytest.FixtureRequest,
    client_name: str,
) -> None:
    reports = (
        getattr(request.node, "report_call", None),
        getattr(request.node, "report_setup", None),
    )
    if not any(report and report.failed for report in reports):
        return
    try:
        run_id = os.environ["EV_TEST_RUN_ID"]
        evidence_dir = PROJECT_ROOT / "artifacts" / run_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
        screenshot_path = evidence_dir / f"{client_name}-{safe_name}.png"
        html_path = evidence_dir / f"{client_name}-{safe_name}.html"
        _redact_sensitive_inputs(page)
        page.screenshot(path=str(screenshot_path), full_page=True)
        html_path.write_text(page.content(), encoding="utf-8")
        allure.attach.file(
            str(screenshot_path),
            name=f"{client_name} 失败页面截图",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach.file(
            str(html_path),
            name=f"{client_name} 失败页面源码",
            attachment_type=allure.attachment_type.HTML,
        )
    except Exception:  # Neither filesystem nor Allure errors may hide the test failure.
        print(f"{client_name} failure evidence unavailable (details omitted).", file=sys.stderr)


def _redact_sensitive_inputs(page: Page) -> None:
    """Clear credential-like inputs before screenshots or HTML leave the page."""
    selector = ", ".join(
        (
            'input[type="password"]',
            'input[type="tel"]',
            'input[autocomplete="username"]',
            'input[autocomplete="current-password"]',
            'input[autocomplete="one-time-code"]',
            'input[name="username"]',
            'input[placeholder*="用户名"]',
            'input[placeholder*="账号"]',
            'input[type="number"][maxlength="11"]',
        )
    )
    page.locator(selector).evaluate_all(
        """
        elements => elements.forEach(element => {
            element.value = '';
            element.setAttribute('value', '');
            element.setAttribute('data-redacted', 'true');
        })
        """
    )
