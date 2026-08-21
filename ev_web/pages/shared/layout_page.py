"""Authenticated layout and navigation component."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.base_page import BasePage


class LayoutPage(BasePage):
    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.brand = page.get_by_text("EV Sales Pro", exact=True)

    def assert_loaded(self) -> None:
        expect(self.brand).to_be_visible()
        expect(self.page).not_to_have_url(f"{self.settings.base_url}/login")

    def navigate(self, group_name: str, item_name: str) -> None:
        group = self.page.get_by_text(group_name, exact=True)
        group.click()
        item = self.page.get_by_role("menuitem", name=item_name, exact=True)
        expect(item).to_be_visible()
        item.click()

    def logout(self) -> None:
        self.page.locator(".user-info").click()
        self.page.get_by_text("退出登录", exact=True).click()
        self.page.get_by_role("button", name="确定", exact=True).click()
