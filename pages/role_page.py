from playwright.sync_api import Page


class RolePage:
    """
    Role selection page shown after OTP verification during signup.
    URL pattern: /dtc/switch?signup=<id>&redirect=undefined&source=account
    """

    ROLE_SELECT = 'select[name="role"]'
    YOJ_SELECT = 'select[name="yoj"]'       # Year of Joining
    YOP_SELECT = 'select[name="yop"]'       # Year of Graduation (year of passing)
    # MDL (Material Design Lite) checkboxes: the <input> has opacity:0 so
    # is_visible() returns False. Use labels for presence checks; use
    # check(force=True) to interact with the hidden-but-laid-out input.
    PRIVACY_CHECKBOX = "#privacy-terms"
    CONSENT_CHECKBOX = "#consent-form"
    PRIVACY_LABEL = 'label[for="privacy-terms"]'
    CONSENT_LABEL = 'label[for="consent-form"]'
    PRIVACY_LINK = 'label[for="privacy-terms"] a'
    CONSENT_LINK = 'label[for="consent-form"] a'
    JOIN_BTN = "#btn3_sgnup"
    PAGE_HEADING = "text=Add your role details in"

    ROLE_CURRENT_STUDENT = "Current Student"
    ROLE_ALUMNI = "Alumni (Past Student)"
    ROLE_STAFF = "Staff / Faculty"

    def __init__(self, page: Page):
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(self.JOIN_BTN).is_visible()

    def get_heading_text(self) -> str:
        return self.page.locator(self.PAGE_HEADING).first.text_content().strip()

    def select_role(self, role_text: str):
        self.page.locator(self.ROLE_SELECT).select_option(label=role_text)
        self.page.wait_for_timeout(600)

    def get_selected_role(self) -> str:
        return self.page.locator(self.ROLE_SELECT).input_value()

    def is_yoj_visible(self) -> bool:
        return self.page.locator(self.YOJ_SELECT).is_visible()

    def is_yop_visible(self) -> bool:
        return self.page.locator(self.YOP_SELECT).is_visible()

    def select_yoj(self, year: str):
        self.page.locator(self.YOJ_SELECT).select_option(label=year)

    def select_yop(self, year: str):
        self.page.locator(self.YOP_SELECT).select_option(label=year)

    def check_privacy_terms(self):
        # MDL positions the opacity-0 input outside Playwright's scroll reach;
        # .evaluate("click") fires the native DOM click directly, triggering Angular's handler.
        self.page.locator(self.PRIVACY_CHECKBOX).evaluate("el => el.click()")

    def check_consent_form(self):
        self.page.locator(self.CONSENT_CHECKBOX).evaluate("el => el.click()")

    def is_privacy_checked(self) -> bool:
        return self.page.locator(self.PRIVACY_CHECKBOX).is_checked()

    def is_consent_checked(self) -> bool:
        return self.page.locator(self.CONSENT_CHECKBOX).is_checked()

    def click_join(self):
        self.page.locator(self.JOIN_BTN).click()
        self.page.wait_for_timeout(1000)

    def get_role_options(self) -> list[str]:
        options = self.page.locator(f"{self.ROLE_SELECT} option").all()
        return [o.text_content().strip() for o in options if o.text_content().strip()]

    def get_privacy_link_href(self) -> str:
        return self.page.locator(self.PRIVACY_LINK).get_attribute("href") or ""

    def get_consent_link_href(self) -> str:
        return self.page.locator(self.CONSENT_LINK).get_attribute("href") or ""
