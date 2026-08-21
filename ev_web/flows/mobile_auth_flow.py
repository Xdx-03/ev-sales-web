"""Customer H5 authentication flow composed from mobile Page Objects."""

from __future__ import annotations

from playwright.sync_api import Page

from ev_web.config import WebSettings
from ev_web.pages.mobile.login_page import MobileLoginPage
from ev_web.pages.mobile.profile_page import MobileProfilePage


class MobileAuthFlow:
    def __init__(self, page: Page, settings: WebSettings) -> None:
        self.login_page = MobileLoginPage(page, settings)
        self.profile_page = MobileProfilePage(page, settings)

    def login_as_customer(self) -> None:
        customer = self.login_page.settings.require_mobile_customer()
        self.login_page.open()
        self.login_page.submit_phone(customer.phone)
        self.login_page.assert_login_succeeded()
        self.login_page.wait_until_login_feedback_finishes()
        self.profile_page.open()
        self.profile_page.assert_authenticated_state()
