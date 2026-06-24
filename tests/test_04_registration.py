"""
Test 04 — Registration Form (New User Path)

After submitting a new email the platform shows the registration form.
These tests cover:
  - Form presence
  - Required field validation
  - Password constraints
  - Password confirmation mismatch
  - Back navigation
"""

import pytest


@pytest.mark.regression
def test_new_email_shows_registration_form(registration_page):
    assert registration_page.is_visible(), \
        "Registration form should appear after submitting an unregistered email"


@pytest.mark.regression
def test_registration_section_heading(registration_page):
    # Multiple elements contain "Sign Up" text (button + heading); .first() picks heading
    heading = registration_page.page.locator("text=Sign Up").first
    assert heading.is_visible(), "Section heading 'Sign Up' should be displayed"


@pytest.mark.regression
def test_first_name_field_is_present(registration_page):
    assert registration_page.page.locator(registration_page.FIRST_NAME).is_visible()


@pytest.mark.regression
def test_last_name_field_is_present(registration_page):
    assert registration_page.page.locator(registration_page.LAST_NAME).is_visible()


@pytest.mark.regression
def test_password_field_is_present(registration_page):
    assert registration_page.page.locator(registration_page.PASSWORD).is_visible()


@pytest.mark.regression
def test_confirm_password_field_is_present(registration_page):
    assert registration_page.page.locator(registration_page.CONFIRM_PASSWORD).is_visible()


@pytest.mark.regression
def test_email_is_prefilled_in_registration_form(registration_page):
    """The email entered at step 1 should be pre-filled (read-only reference)."""
    # The page has a duplicate #email id — the second one is inside the signup form
    email_fields = registration_page.page.locator("#email")
    # At least one email field should have a non-empty value
    found = any(
        email_fields.nth(i).input_value().strip() != ""
        for i in range(email_fields.count())
    )
    assert found, "Email should be pre-filled in the registration form"


@pytest.mark.regression
def test_password_too_short_shows_error(registration_page):
    """Password under 8 characters should trigger a validation error."""
    registration_page.enter_first_name("Test")
    registration_page.enter_password("short")        # 5 chars — below minimum
    registration_page.enter_confirm_password("short")
    registration_page.click_signup()

    errors = registration_page.get_visible_errors()
    has_length_error = any("8" in e or "minimum" in e.lower() or "characters" in e.lower()
                           for e in errors)
    assert has_length_error, \
        f"Expected minimum-length error, got errors: {errors}"


@pytest.mark.regression
def test_password_exactly_8_chars_is_accepted(registration_page):
    """Exactly 8 characters should meet the minimum and not show a length error."""
    registration_page.enter_first_name("Test")
    registration_page.enter_password("Abcd@123")    # exactly 8 chars
    registration_page.enter_confirm_password("Abcd@123")
    registration_page.click_signup()

    errors = registration_page.get_visible_errors()
    has_length_error = any("8" in e or "minimum" in e.lower() for e in errors)
    assert not has_length_error, \
        "8-character password should not trigger a length error"


@pytest.mark.regression
def test_password_mismatch_does_not_proceed_to_otp(registration_page):
    """If password and confirm-password don't match, OTP step should NOT appear."""
    registration_page.enter_first_name("Test")
    registration_page.enter_password("TestPass@123")
    registration_page.enter_confirm_password("DifferentPass@456")
    registration_page.click_signup()

    # Should still be on registration form (OTP input should not be visible)
    assert not registration_page.page.locator("#otp_input").is_visible(), \
        "Mismatched passwords should not allow progression to OTP step"


@pytest.mark.regression
def test_empty_form_submission_stays_on_registration(registration_page):
    """Clicking Sign Up with all fields empty should not advance the flow."""
    registration_page.click_signup()
    assert registration_page.is_visible(), \
        "Empty form submission should keep the user on the registration form"


@pytest.mark.regression
def test_back_button_returns_to_email_step(registration_page):
    registration_page.click_back()
    from pages.signup_page import SignupPage
    sp = SignupPage(registration_page.page)
    assert sp.is_on_email_step(), \
        "BACK from registration form should return to email entry step"


@pytest.mark.regression
def test_very_long_field_values_show_error(registration_page):
    """BUG-009: Extremely long name/password values silently block Sign Up with no feedback.
    This test intentionally fails to document this bug."""
    long_string = "A" * 200
    registration_page.enter_first_name(long_string)
    registration_page.enter_last_name(long_string)
    registration_page.enter_password(long_string + "@1")
    registration_page.enter_confirm_password(long_string + "@1")
    registration_page.click_signup()

    otp_visible = registration_page.page.locator("#otp_input").is_visible()
    errors = registration_page.get_visible_errors()
    assert otp_visible or any(errors), \
        "BUG-009: Very long field values silently block Sign Up — no error shown, no OTP step reached"


@pytest.mark.regression
def test_weak_password_without_complexity_is_rejected(registration_page):
    """BUG-011: Platform accepts passwords with no uppercase, special char, or numeric characters.
    This test intentionally fails to document the missing complexity validation."""
    registration_page.enter_first_name("Test")
    registration_page.enter_last_name("User")
    registration_page.enter_password("abcdefgh")   # 8 chars, all lowercase, no complexity
    registration_page.enter_confirm_password("abcdefgh")
    registration_page.click_signup()

    errors = registration_page.get_visible_errors()
    has_complexity_error = any(
        keyword in e.lower()
        for e in errors
        for keyword in ("uppercase", "special", "number", "strong", "complexity")
    )
    assert has_complexity_error, \
        "BUG-011: Weak password 'abcdefgh' was accepted — platform should enforce complexity requirements"


@pytest.mark.regression
def test_login_form_does_not_appear_for_new_email(registration_page):
    """Login password field should NOT appear for a new (unregistered) email."""
    assert not registration_page.page.locator("#passwordLogin").is_visible(), \
        "Login form should not be shown for a new email"
