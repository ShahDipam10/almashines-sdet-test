"""
Test 05 — OTP Verification Step

After a successful registration form submission an OTP is sent to the
registered email. These tests cover the OTP step UI and error handling
without needing to read an actual inbox.
"""

import pytest


@pytest.mark.regression
def test_otp_step_is_shown_after_registration(otp_page):
    assert otp_page.is_visible(), \
        "OTP input should appear after submitting the registration form"


@pytest.mark.regression
def test_verify_otp_heading_is_visible(otp_page):
    heading = otp_page.page.locator("text=Verify OTP")
    assert heading.is_visible(), "Section heading 'Verify OTP' should be displayed"


@pytest.mark.regression
def test_otp_hint_message_is_visible(otp_page):
    hint = otp_page.page.locator(otp_page.EMAIL_HINT)
    assert hint.is_visible(), "OTP hint message should inform user where the code was sent"


@pytest.mark.regression
def test_otp_hint_contains_registered_email(otp_page):
    """The hint text must show the email address the OTP was sent to."""
    email = otp_page.get_hint_email()
    assert "@" in email and len(email) > 5, \
        f"Hint should contain a valid email address, got: '{email}'"


@pytest.mark.regression
def test_resend_otp_link_is_visible(otp_page):
    resend = otp_page.page.locator(otp_page.RESEND_BTN)
    assert resend.is_visible(), "'Resend OTP' link should be present on OTP step"


@pytest.mark.regression
def test_verify_button_is_visible(otp_page):
    verify_btn = otp_page.page.locator(otp_page.VERIFY_BTN)
    assert verify_btn.is_visible(), "Verify button should be present on OTP step"


@pytest.mark.regression
def test_wrong_otp_shows_error_dialog(otp_page):
    """Submitting an incorrect OTP should trigger a SweetAlert error dialog."""
    otp_page.enter_otp("000000")
    otp_page.click_verify()
    title = otp_page.get_error_title()
    assert title != "", "An error dialog title should appear after a wrong OTP"


@pytest.mark.regression
def test_wrong_otp_error_title_text(otp_page):
    otp_page.enter_otp("111111")
    otp_page.click_verify()
    title = otp_page.get_error_title()
    assert "OTP" in title or "verification" in title.lower() or "failed" in title.lower(), \
        f"Error title should mention OTP failure, got: '{title}'"


@pytest.mark.regression
def test_wrong_otp_error_body_text(otp_page):
    otp_page.enter_otp("222222")
    otp_page.click_verify()
    otp_page.get_error_title()          # wait for dialog to appear
    body = otp_page.get_error_text()
    assert "invalid" in body.lower() or "code" in body.lower() or "incorrect" in body.lower(), \
        f"Error body should indicate an invalid code, got: '{body}'"


@pytest.mark.regression
def test_error_dialog_can_be_dismissed(otp_page):
    """After dismissing the error, user should remain on the OTP step."""
    otp_page.enter_otp("333333")
    otp_page.click_verify()
    otp_page.get_error_title()    # wait for dialog
    otp_page.dismiss_error()
    assert otp_page.is_visible(), \
        "After dismissing error dialog, OTP input should still be visible"


@pytest.mark.regression
def test_empty_otp_shows_validation_message(otp_page):
    """Clicking Verify with an empty OTP should show a 'Please enter OTP' alert."""
    otp_page.click_verify()
    # Platform shows a SweetAlert with only swal-text (no title) for empty OTP
    otp_page.page.wait_for_selector(".swal-text", timeout=5000)
    msg = otp_page.page.locator(".swal-text").text_content().strip()
    assert "otp" in msg.lower() or "enter" in msg.lower(), \
        f"Expected 'Please enter OTP' alert, got: '{msg}'"
    # Dismiss the alert — OTP step should remain
    otp_page.dismiss_error()
    assert otp_page.is_visible(), \
        "After dismissing empty-OTP alert, OTP input should still be visible"


@pytest.mark.regression
def test_back_button_from_otp_returns_to_email_step(otp_page):
    """BACK from OTP step goes back to the email entry step (not registration form).
    This is the platform's intended navigation: hideDetailsForm() resets the entire flow.
    """
    otp_page.click_back()
    from pages.signup_page import SignupPage
    sp = SignupPage(otp_page.page)
    assert sp.is_on_email_step(), \
        "BACK from OTP step should return to the email entry step"
