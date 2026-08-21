"""Login page interactions and stable semantic locators."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.title = page.get_by_role("heading", name="EV Sales Admin")
        self.username = page.get_by_placeholder("请输入用户名")
        self.password = page.get_by_placeholder("请输入密码")
        self.submit = page.get_by_role("button", name=re.compile("立即登录"))

    def open(self) -> None:
        self.open_path(self.PATH)

    def assert_loaded(self) -> None:
        expect(self.title).to_be_visible()
        expect(self.username).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.submit).to_be_enabled()

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    def submit_blank(self) -> None:
        self.username.clear()
        self.password.clear()
        self.submit.click()

    def assert_required_errors(self) -> None:
        expect(self.page.locator(".el-form-item__error", has_text="请输入用户名")).to_be_visible()
        expect(self.page.locator(".el-form-item__error", has_text="请输入密码")).to_be_visible()

    def assert_invalid_credentials_error(self) -> None:
        error = self.page.locator(".el-message--error").last
        expect(error).to_be_visible()
        expect(error).to_contain_text(re.compile("用户名|密码|账号|无效|错误|失败"))
