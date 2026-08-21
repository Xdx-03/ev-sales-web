"""Base operations for uni-app H5 hash routes."""

from __future__ import annotations

from ev_web.pages.base_page import BasePage


class MobileBasePage(BasePage):
    def open_route(self, route: str) -> None:
        normalized_route = route if route.startswith("/") else f"/{route}"
        self.page.goto(
            f"{self.settings.h5_base_url}/#{normalized_route}",
            wait_until="domcontentloaded",
        )
