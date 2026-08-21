"""Vehicle model management page."""

from ev_web.pages.management_page import ManagementPage


class CarModelPage(ManagementPage):
    PATH = "/car/model"
    HEADING = "车型库管理"
