"""Shared browser operations; business assertions remain in tests and flows."""

from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Page

from ev_web.config import WebSettings


class BasePage:
    def __init__(self, page: Page, settings: WebSettings) -> None:
        self.page = page
        self.settings = settings

    def open_path(self, path: str) -> None:
        url = urljoin(f"{self.settings.base_url}/", path.lstrip("/"))
        self.page.goto(url, wait_until="domcontentloaded")
