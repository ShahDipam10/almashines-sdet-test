from playwright.sync_api import Page

BASE_URL = "https://www.almashines.com/dtc/account"


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto(BASE_URL)
        self.page.wait_for_load_state("networkidle")

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url
