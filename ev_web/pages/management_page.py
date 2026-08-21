"""Reusable contract for management pages identified by route and heading."""

from __future__ import annotations

from typing import ClassVar

from playwright.sync_api import Page, expect

from ev_web.config import WebSettings
from ev_web.pages.base_page import BasePage


class ManagementPage(BasePage):
    """Share stable loading checks while keeping each module independently named."""

    PATH: ClassVar[str]
    HEADING: ClassVar[str]

    def __init__(self, page: Page, settings: WebSettings) -> None:
        super().__init__(page, settings)
        self.heading = page.get_by_text(self.HEADING, exact=True)

    def assert_loaded(self) -> None:
        expect(self.page).to_have_url(f"{self.settings.base_url}{self.PATH}")
        expect(self.heading).to_be_visible()
