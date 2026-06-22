from playwright.sync_api import Page


class LoginFormPage:
    """
    Appears on the same URL after submitting an already-registered email.
    Shows: email (pre-filled), password input, Login button, OTP login link.
    """

    EMAIL_FIELD = "#emailLogin"
    PASSWORD_FIELD = "#passwordLogin"
    LOGIN_BTN = "button.ladda-button-primary"
    LOGIN_WITH_OTP = "a:has-text('Login with OTP')"
    FORGOT_PASSWORD = "text=Forgot password?"
    # Two BACK buttons share the same ng-click; use .first()
    BACK_BTN = 'button[ng-click="hideDetailsForm()"]'
    SECTION_HEADING = "text=E-mail login"

    def __init__(self, page: Page):
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(self.PASSWORD_FIELD).is_visible()

    def get_prefilled_email(self) -> str:
        return self.page.locator(self.EMAIL_FIELD).input_value()

    def enter_password(self, password: str):
        self.page.fill(self.PASSWORD_FIELD, password)

    def click_login(self):
        self.page.click(self.LOGIN_BTN)

    def is_login_with_otp_visible(self) -> bool:
        # Two duplicate links exist (desktop + mobile layouts); .first picks either visible one
        return self.page.locator(self.LOGIN_WITH_OTP).first.is_visible()

    def is_forgot_password_visible(self) -> bool:
        return self.page.locator(self.FORGOT_PASSWORD).is_visible()

    def click_back(self):
        self.page.locator(self.BACK_BTN).first.click()
        self.page.wait_for_timeout(500)
