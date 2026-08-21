"""Customer-facing uni-app H5 scenarios under a real mobile browser context."""

import pytest
from ev_web.config import WebSettings
from ev_web.pages.mobile.home_page import MobileHomePage
from ev_web.pages.mobile.login_page import MobileLoginPage
from ev_web.pages.mobile.order_page import MobileOrderPage
from ev_web.pages.mobile.profile_page import MobileProfilePage
from playwright.sync_api import Page, expect

pytestmark = [
    pytest.mark.ui,
    pytest.mark.live,
    pytest.mark.mobile,
    pytest.mark.h5,
    pytest.mark.smoke,
]


def test_mobile_showroom_displays_core_sections(
    mobile_page: Page,
    settings: WebSettings,
) -> None:
    home = MobileHomePage(mobile_page, settings)

    home.open()

    home.assert_loaded()


def test_mobile_login_displays_phone_and_wechat_entries(
    mobile_page: Page,
    settings: WebSettings,
) -> None:
    login = MobileLoginPage(mobile_page, settings)

    login.open()

    login.assert_loaded()


@pytest.mark.parametrize("invalid_phone", ["", "1380013"], ids=["blank", "too-short"])
def test_mobile_login_rejects_invalid_phone(
    mobile_page: Page,
    settings: WebSettings,
    invalid_phone: str,
) -> None:
    login = MobileLoginPage(mobile_page, settings)
    login.open()

    login.submit_phone(invalid_phone)

    login.assert_invalid_phone_toast()


def test_mobile_profile_displays_anonymous_state(
    mobile_page: Page,
    settings: WebSettings,
) -> None:
    profile = MobileProfilePage(mobile_page, settings)

    profile.open()

    profile.assert_anonymous_state()


@pytest.mark.critical
@pytest.mark.permission
def test_mobile_protected_orders_guide_anonymous_user_to_login(
    mobile_page: Page,
    settings: WebSettings,
) -> None:
    profile = MobileProfilePage(mobile_page, settings)
    profile.open()

    profile.open_orders()
    profile.assert_login_prompt()
    profile.confirm_login()

    MobileLoginPage(mobile_page, settings).assert_loaded()
    expect(mobile_page).to_have_url(f"{settings.h5_base_url}/#/pages/login/index")


@pytest.mark.auth
@pytest.mark.critical
def test_mobile_customer_can_log_in_and_view_authenticated_profile(
    authenticated_mobile_page: Page,
    settings: WebSettings,
) -> None:
    profile = MobileProfilePage(authenticated_mobile_page, settings)

    profile.assert_authenticated_state()


@pytest.mark.auth
@pytest.mark.critical
def test_mobile_customer_can_open_own_order_list(
    authenticated_mobile_page: Page,
    settings: WebSettings,
) -> None:
    profile = MobileProfilePage(authenticated_mobile_page, settings)

    profile.open_orders()

    MobileOrderPage(authenticated_mobile_page, settings).assert_loaded()
