"""Customer mobile H5 phone login page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.mobile.base_page import MobileBasePage


class MobileLoginPage(MobileBasePage):
    ROUTE = "/pages/login/index"

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.app_name = page.get_by_text("EV Car Sales", exact=True)
        self.phone = page.get_by_role("spinbutton")
        self.phone_login = page.locator(".btn-login")
        self.wechat_login = page.locator(".btn-wechat")
        self.success_toast = page.get_by_text("登录成功", exact=True)

    def open(self) -> None:
        self.open_route(self.ROUTE)

    def assert_loaded(self) -> None:
        expect(self.app_name).to_be_visible()
        expect(self.phone).to_be_visible()
        expect(self.phone_login).to_be_visible()
        expect(self.wechat_login).to_be_visible()

    def submit_phone(self, phone: str) -> None:
        self.phone.fill(phone)
        self.phone_login.click()

    def assert_login_succeeded(self) -> None:
        expect(self.success_toast).to_be_visible()

    def wait_until_login_feedback_finishes(self) -> None:
        """Wait for the application's post-login callback without fixed sleeps."""
        expect(self.success_toast).not_to_be_visible(timeout=self.settings.action_timeout_ms)

    def assert_invalid_phone_toast(self) -> None:
        expect(self.page.get_by_text("请输入正确手机号", exact=True)).to_be_visible()
