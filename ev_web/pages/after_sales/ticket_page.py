"""After-sales ticket management page."""

from ev_web.pages.management_page import ManagementPage


class TicketPage(ManagementPage):
    PATH = "/after-sales/ticket"
    HEADING = "售后维保工单"
