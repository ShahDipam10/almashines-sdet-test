from pages.base_page import BasePage


class SignupPage(BasePage):
    """Represents the initial email-entry step of the Sign Up / Login page."""

    EMAIL_INPUT = "#email"
    SUBMIT_BTN = "#emailBtn"
    HEADING = "h2"

    def enter_email(self, email: str):
        self.page.fill(self.EMAIL_INPUT, email)

    def click_submit(self):
        self.page.click(self.SUBMIT_BTN)

    def submit_email(self, email: str):
        self.enter_email(email)
        self.click_submit()
        self.page.wait_for_timeout(1500)

    def is_on_email_step(self) -> bool:
        # #emailBtn lives in the ng-hide container that disappears once signup/login
        # sections appear — more reliable than #email which is duplicated in the
        # registration form and stays visible.
        return self.page.locator(self.SUBMIT_BTN).is_visible()

    def get_email_value(self) -> str:
        return self.page.locator(self.EMAIL_INPUT).input_value()
