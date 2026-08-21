"""Authentication business flow composed from Page Objects."""

from __future__ import annotations

from playwright.sync_api import Page

from ev_web.config import WebSettings
from ev_web.pages.auth.login_page import LoginPage
from ev_web.pages.shared.layout_page import LayoutPage


class AuthFlow:
    def __init__(self, page: Page, settings: WebSettings) -> None:
        self.login_page = LoginPage(page, settings)
        self.layout = LayoutPage(page, settings)

    def login_as_admin(self) -> None:
        credentials = self.login_page.settings.require_admin()
        self.login_page.open()
        self.login_page.login(credentials.username, credentials.password)
        self.layout.assert_loaded()
