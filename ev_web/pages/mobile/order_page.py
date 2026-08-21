"""Authenticated customer order list in the mobile H5 client."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.mobile.base_page import MobileBasePage


class MobileOrderPage(MobileBasePage):
    ROUTE = "/pages/order/list"

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        tabs = page.locator(".tabs")
        self.all_orders = tabs.get_by_text("全部", exact=True)
        self.pending_payment = tabs.get_by_text("待支付", exact=True)
        self.delivered = tabs.get_by_text("已交付", exact=True)
        self.loading = page.locator(".order-list .loading-more")
        self.result = page.locator(".order-item").first.or_(
            page.get_by_text("暂无相关订单", exact=True)
        )

    def assert_loaded(self) -> None:
        expect(self.page).to_have_url(f"{self.settings.h5_base_url}/#{self.ROUTE}")
        expect(self.all_orders).to_be_visible()
        expect(self.pending_payment).to_be_visible()
        expect(self.delivered).to_be_visible()
        expect(self.loading).not_to_be_visible()
        expect(self.result).to_be_visible()
