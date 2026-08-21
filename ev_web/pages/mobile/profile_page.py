"""Anonymous customer profile and protected-entry behavior."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.mobile.base_page import MobileBasePage


class MobileProfilePage(MobileBasePage):
    ROUTE = "/pages/user/index"

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.title = page.get_by_text("个人中心", exact=True).first
        self.login_entry = page.get_by_text("点击登录", exact=True)
        self.orders = page.get_by_text("我的订单", exact=True)
        self.test_drives = page.get_by_text("预约试驾", exact=True)
        self.member_badge = page.get_by_text("已激活专享权益", exact=True)
        self.logout_entry = page.get_by_text("退出登录", exact=True)

    def open(self) -> None:
        self.open_route(self.ROUTE)

    def assert_anonymous_state(self) -> None:
        expect(self.title).to_be_visible()
        expect(self.login_entry).to_be_visible()
        expect(self.orders).to_be_visible()
        expect(self.test_drives).to_be_visible()

    def assert_authenticated_state(self) -> None:
        expect(self.title).to_be_visible()
        expect(self.member_badge).to_be_visible()
        expect(self.logout_entry).to_be_visible()
        expect(self.login_entry).not_to_be_visible()

    def open_orders(self) -> None:
        self.orders.click()

    def assert_login_prompt(self) -> None:
        expect(self.page.get_by_text("请先登录以查看该内容", exact=True)).to_be_visible()

    def confirm_login(self) -> None:
        self.page.get_by_text("去登录", exact=True).click()
