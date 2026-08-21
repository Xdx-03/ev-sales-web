"""Authentication scenarios through the real management UI."""

import pytest
from ev_web.config import WebSettings
from ev_web.flows.auth_flow import AuthFlow
from ev_web.pages.auth.login_page import LoginPage
from ev_web.pages.shared.layout_page import LayoutPage
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.ui, pytest.mark.live, pytest.mark.auth]


@pytest.mark.smoke
def test_login_page_displays_required_controls(ui_page: Page, settings: WebSettings) -> None:
    login = LoginPage(ui_page, settings)

    login.open()

    login.assert_loaded()


@pytest.mark.smoke
def test_blank_credentials_show_required_validation(ui_page: Page, settings: WebSettings) -> None:
    login = LoginPage(ui_page, settings)
    login.open()

    login.submit_blank()

    login.assert_required_errors()
    expect(ui_page).to_have_url(f"{settings.base_url}/login")


@pytest.mark.regression
def test_invalid_credentials_are_rejected(ui_page: Page, settings: WebSettings) -> None:
    login = LoginPage(ui_page, settings)
    login.open()

    login.login("invalid_auto_user", "invalid-auto-password")

    login.assert_invalid_credentials_error()
    expect(ui_page).to_have_url(f"{settings.base_url}/login")


@pytest.mark.smoke
@pytest.mark.critical
def test_admin_can_log_in(ui_page: Page, settings: WebSettings) -> None:
    settings.require_admin()

    AuthFlow(ui_page, settings).login_as_admin()

    LayoutPage(ui_page, settings).assert_loaded()


@pytest.mark.regression
@pytest.mark.critical
def test_admin_can_log_out(authenticated_page: Page, settings: WebSettings) -> None:
    layout = LayoutPage(authenticated_page, settings)

    layout.logout()

    LoginPage(authenticated_page, settings).assert_loaded()
    expect(authenticated_page).to_have_url(f"{settings.base_url}/login")
