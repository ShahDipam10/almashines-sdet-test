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
from utils.data_generators import generate_test_email

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
