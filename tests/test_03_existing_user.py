"""
Test 03 — Existing User Path

When a registered email is submitted, the platform should prompt the user
to log in rather than creating a new account.

Prerequisite: EXISTING_EMAIL env var must point to an already-registered account.
Default: dipamshahaliantesting1@gmail.com
"""

import pytest


@pytest.mark.regression
def test_existing_email_shows_login_form(login_form_page):
    """Registered email → login form should appear, not the signup form."""
    assert login_form_page.is_visible(), \
        "Login form (password field) should be visible for a registered email"


@pytest.mark.regression
def test_login_form_section_heading(login_form_page):
    heading = login_form_page.page.locator("text=E-mail login")
    assert heading.is_visible(), "Section heading 'E-mail login' should be displayed"


@pytest.mark.regression
def test_existing_email_is_prefilled_in_login_form(login_form_page):
    """Email should be pre-populated so the user doesn't have to re-type it."""
    import os
    expected = os.getenv("EXISTING_EMAIL", "dipamshahaliantesting1@gmail.com")
    prefilled = login_form_page.get_prefilled_email()
    assert prefilled == expected, \
        f"Email field should be pre-filled with '{expected}', got '{prefilled}'"


@pytest.mark.regression
def test_login_button_is_visible(login_form_page):
    login_btn = login_form_page.page.locator(login_form_page.LOGIN_BTN)
    assert login_btn.is_visible(), "Login button should be visible"


@pytest.mark.regression
def test_login_with_otp_link_is_visible(login_form_page):
    assert login_form_page.is_login_with_otp_visible(), \
        "'Login with OTP' link should be present as an alternative"


@pytest.mark.regression
def test_forgot_password_link_is_visible(login_form_page):
    assert login_form_page.is_forgot_password_visible(), \
        "'Forgot password?' link should be present"


@pytest.mark.regression
def test_back_button_returns_to_email_step(login_form_page):
    """BACK should bring the user back to the initial email entry field."""
    login_form_page.click_back()
    from pages.signup_page import SignupPage
    sp = SignupPage(login_form_page.page)
    assert sp.is_on_email_step(), "BACK from login form should return to email entry"


@pytest.mark.regression
def test_signup_form_is_not_shown_for_existing_email(login_form_page):
    """Registration fields (first name etc.) should NOT appear for a known email."""
    assert not login_form_page.page.locator("#fname").is_visible(), \
        "Registration form should not be shown when email already has an account"
