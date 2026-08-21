"""Sales order management page."""

from ev_web.pages.management_page import ManagementPage


class SalesPage(ManagementPage):
    PATH = "/sales"
    HEADING = "销售订单管理"
