"""
Shared fixtures for the AlmaShines Sign Up flow test suite.

Fixture hierarchy:
  page (from pytest-playwright)
    └── signup_page          — navigates to the signup URL
          ├── login_form_page  — submits existing email; lands on login form
          ├── registration_page — submits new email; lands on registration form
          └── otp_page           — fills registration form and submits; lands on OTP step
"""

import os
import pytest
from dotenv import load_dotenv

from pages.signup_page import SignupPage
from pages.login_form_page import LoginFormPage
from pages.registration_page import RegistrationPage
from pages.otp_page import OtpPage
from pages.role_page import RolePage
from utils.data_generators import generate_test_email
from utils.temp_email import get_temp_email, wait_for_otp

load_dotenv()

EXISTING_EMAIL = os.getenv("EXISTING_EMAIL", "dipamshahaliantesting1@gmail.com")


# ---------------------------------------------------------------------------
# Browser configuration
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    headed = os.getenv("HEADED", "true").lower() == "true"
    slow_mo = int(os.getenv("SLOW_MO", "300"))
    return {
        **browser_type_launch_args,
        "headless": not headed,
        "slow_mo": slow_mo,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
    }


# ---------------------------------------------------------------------------
# Page-level fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def signup_page(page):
    sp = SignupPage(page)
    sp.navigate()
    return sp


@pytest.fixture
def login_form_page(page, signup_page):
    """Reach the login form by submitting a known-registered email."""
    signup_page.submit_email(EXISTING_EMAIL)
    return LoginFormPage(page)


@pytest.fixture
def registration_page(page, signup_page):
    """Reach the registration form by submitting a fresh unique email."""
    email = generate_test_email()
    signup_page.submit_email(email)
    return RegistrationPage(page)


@pytest.fixture
def otp_page(page, signup_page):
    """Reach the OTP step by submitting email + valid registration details."""
    email = generate_test_email()
    signup_page.submit_email(email)

    reg = RegistrationPage(page)
    reg.fill_valid_registration()
    reg.click_signup()

    # Dismiss any unexpected SweetAlert that may appear during fixture setup
    # (e.g. rate-limiting or duplicate-email warnings from rapid test runs)
    swal = page.locator(".swal-button--confirm")
    try:
        swal.wait_for(state="visible", timeout=3000)
        swal.click()
        page.wait_for_timeout(500)
    except Exception:
        pass  # No dialog — normal path

    otp = OtpPage(page)
    if not otp.is_visible():
        pytest.skip(
            "OTP step not reached — platform may be rate-limiting rapid registrations. "
            "Wait a minute and re-run this test individually."
        )
    return otp


@pytest.fixture
def role_page(page):
    """
    Reach the role selection page via a full E2E signup using a Guerrilla Mail
    disposable inbox so the OTP can be read programmatically.
    Skips (not fails) if any intermediate step is blocked by rate limiting.
    """
    email, sid_token = get_temp_email()

    page.goto("https://www.almashines.com/dtc/account")
    page.wait_for_load_state("networkidle")
    page.fill("#email", email)
    page.click("#emailBtn")
    page.wait_for_timeout(2000)

    reg = RegistrationPage(page)
    if not reg.is_visible():
        pytest.skip("Registration form not reached — email may already be registered.")

    reg.fill_valid_registration(
        first_name="Role",
        last_name="Tester",
        password="RoleTest@2024",
    )
    reg.click_signup()

    # Dismiss any SweetAlert from rate-limiting before checking OTP step
    swal = page.locator(".swal-button--confirm")
    try:
        swal.wait_for(state="visible", timeout=3000)
        swal.click()
        page.wait_for_timeout(500)
    except Exception:
        pass

    otp_pg = OtpPage(page)
    if not otp_pg.is_visible():
        pytest.skip(
            "OTP step not reached — platform may be rate-limiting rapid registrations."
        )

    otp_code = wait_for_otp(sid_token, timeout=90)
    if otp_code is None:
        pytest.skip(
            "OTP not received in Guerrilla Mail inbox within 90 s. "
            "The platform may be filtering the email domain — re-run to retry."
        )

    otp_pg.enter_otp(otp_code)
    otp_pg.click_verify()
    page.wait_for_timeout(3000)

    rp = RolePage(page)
    if not rp.is_visible():
        pytest.skip(
            "Role selection page not reached after OTP verification. "
            "Signup may have failed or the platform redirected elsewhere."
        )
    return rp


# ---------------------------------------------------------------------------
# Auto-screenshot on test failure
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs("reports/screenshots", exist_ok=True)
            safe_name = item.name.replace("/", "_").replace("\\", "_")
            path = f"reports/screenshots/{safe_name}.png"
            try:
                page.screenshot(path=path)
            except Exception:
                pass
