"""Anonymous access must be redirected by the real front-end route guard."""

import pytest
from ev_web.config import WebSettings
from ev_web.pages.auth.login_page import LoginPage
from ev_web.pages.base_page import BasePage
from playwright.sync_api import Page, expect

pytestmark = [
    pytest.mark.ui,
    pytest.mark.live,
    pytest.mark.permission,
    pytest.mark.smoke,
    pytest.mark.critical,
]


@pytest.mark.parametrize(
    "protected_path",
    [
        pytest.param("/car/model", id="vehicle-models"),
        pytest.param("/sales", id="sales-orders"),
        pytest.param("/after-sales/ticket", id="after-sales-tickets"),
        pytest.param("/sys/user", id="system-users"),
    ],
)
def test_anonymous_user_is_redirected_to_login(
    ui_page: Page,
    settings: WebSettings,
    protected_path: str,
) -> None:
    BasePage(ui_page, settings).open_path(protected_path)

    LoginPage(ui_page, settings).assert_loaded()
    expect(ui_page).to_have_url(f"{settings.base_url}/login")
