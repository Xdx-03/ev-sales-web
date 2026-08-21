"""Customer mobile H5 showroom page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.mobile.base_page import MobileBasePage


class MobileHomePage(MobileBasePage):
    ROUTE = "/pages/index/index"

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.showroom_title = page.get_by_text("EV 领航智能展厅", exact=True)
        self.promotion_title = page.get_by_text("限时礼遇", exact=True)
        self.models_title = page.get_by_text("热门车型", exact=True)
        self.ai_entry = page.get_by_text("智能咨询", exact=True)

    def open(self) -> None:
        self.open_route(self.ROUTE)

    def assert_loaded(self) -> None:
        expect(self.showroom_title).to_be_visible()
        expect(self.promotion_title).to_be_visible()
        expect(self.models_title).to_be_visible()
        expect(self.ai_entry).to_be_visible()

    def open_ai_advisor(self) -> None:
        self.ai_entry.click()
