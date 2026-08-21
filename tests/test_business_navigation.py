"""Representative authenticated navigation across core business modules."""

import pytest
from ev_web.config import WebSettings
from ev_web.pages.after_sales.ticket_page import TicketPage
from ev_web.pages.car.model_page import CarModelPage
from ev_web.pages.order.sales_page import SalesPage
from ev_web.pages.shared.layout_page import LayoutPage
from playwright.sync_api import Page

pytestmark = [pytest.mark.ui, pytest.mark.live, pytest.mark.regression]


@pytest.mark.critical
def test_admin_opens_vehicle_model_management(
    authenticated_page: Page,
    settings: WebSettings,
) -> None:
    LayoutPage(authenticated_page, settings).navigate("车辆管理", "车型列表")

    CarModelPage(authenticated_page, settings).assert_loaded()


@pytest.mark.critical
def test_admin_opens_sales_order_management(
    authenticated_page: Page,
    settings: WebSettings,
) -> None:
    LayoutPage(authenticated_page, settings).navigate("销售业务", "销售订单")

    SalesPage(authenticated_page, settings).assert_loaded()


@pytest.mark.critical
def test_admin_opens_after_sales_ticket_management(
    authenticated_page: Page,
    settings: WebSettings,
) -> None:
    LayoutPage(authenticated_page, settings).navigate("售后服务", "工单管理")

    TicketPage(authenticated_page, settings).assert_loaded()
