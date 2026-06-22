from playwright.sync_api import Page
from typing import List


class RegistrationPage:
    """
    Shown after a new (unregistered) email is submitted.
    Fields: First Name*, Last Name, Email (pre-filled), Password (min 8), Confirm Password.
    """

    FIRST_NAME = "#fname"
    LAST_NAME = "#lname"
    PASSWORD = "#password"
    CONFIRM_PASSWORD = "#re-password"
    SIGNUP_BTN = 'button[ng-click="validationFirstStep($event,formBasic)"]'
    BACK_BTN = 'button[ng-click="hideDetailsForm()"]'
    SECTION_HEADING = "text=Sign Up"
    # Validation error spans rendered by AngularJS MDL
    ERROR_SPANS = "span.mdl-textfield__error"

    def __init__(self, page: Page):
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(self.FIRST_NAME).is_visible()

    def enter_first_name(self, name: str):
        self.page.fill(self.FIRST_NAME, name)

    def enter_last_name(self, name: str):
        self.page.fill(self.LAST_NAME, name)

    def enter_password(self, password: str):
        self.page.fill(self.PASSWORD, password)

    def enter_confirm_password(self, password: str):
        self.page.fill(self.CONFIRM_PASSWORD, password)

    def click_signup(self):
        self.page.click(self.SIGNUP_BTN)
        self.page.wait_for_timeout(2000)

    def click_back(self):
        self.page.locator(self.BACK_BTN).first.click()
        self.page.wait_for_timeout(500)

    def get_visible_errors(self) -> List[str]:
        spans = self.page.locator(self.ERROR_SPANS)
        errors = []
        for i in range(spans.count()):
            span = spans.nth(i)
            if span.is_visible():
                errors.append(span.text_content().strip())
        return errors

    def fill_valid_registration(
        self,
        first_name: str = "Test",
        last_name: str = "User",
        password: str = "TestPass@123",
    ):
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_password(password)
        self.enter_confirm_password(password)
