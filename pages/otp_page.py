import re
from playwright.sync_api import Page


class OtpPage:
    """
    OTP verification step shown after a successful registration form submission.
    Wrong OTP triggers a SweetAlert2 dialog.
    """

    OTP_INPUT = "#otp_input"
    VERIFY_BTN = 'button:has-text("Verify")'
    RESEND_BTN = '[ng-click="requestOTP(field)"]'
    BACK_BTN = 'button[ng-click="hideDetailsForm()"]'
    SECTION_HEADING = "text=Verify OTP"
    EMAIL_HINT = "text=We have just sent you One Time Password"

    # SweetAlert dialog elements (shown on wrong OTP)
    SWAL_TITLE = ".swal-title"
    SWAL_TEXT = ".swal-text"
    SWAL_CONFIRM = ".swal-button--confirm"

    def __init__(self, page: Page):
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(self.OTP_INPUT).is_visible()

    def enter_otp(self, code: str):
        self.page.fill(self.OTP_INPUT, code)

    def click_verify(self):
        self.page.locator(self.VERIFY_BTN).click()

    def click_resend(self):
        self.page.click(self.RESEND_BTN)
        self.page.wait_for_timeout(1000)

    def click_back(self):
        self.page.locator(self.BACK_BTN).first.click()
        self.page.wait_for_timeout(500)

    def get_error_title(self) -> str:
        self.page.wait_for_selector(self.SWAL_TITLE, timeout=6000)
        return self.page.locator(self.SWAL_TITLE).text_content().strip()

    def get_error_text(self) -> str:
        return self.page.locator(self.SWAL_TEXT).text_content().strip()

    def dismiss_error(self):
        self.page.click(self.SWAL_CONFIRM)
        self.page.wait_for_timeout(500)

    def get_hint_email(self) -> str:
        """Extracts the email address shown in the OTP hint, e.g. '(user@example.com)'."""
        hint = self.page.locator(self.EMAIL_HINT).text_content()
        match = re.search(r"\(([^)]+)\)", hint)
        return match.group(1) if match else ""
