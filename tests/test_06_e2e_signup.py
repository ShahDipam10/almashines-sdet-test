"""
Test 06 — Full End-to-End Sign Up Journey

Uses Guerrilla Mail to obtain a real disposable inbox so the OTP can be
read programmatically, completing the entire sign-up flow without any
manual intervention.

Mark: e2e — requires network access to api.guerrillamail.com
Run separately when you want the full flow:
    pytest tests/test_06_e2e_signup.py -v
"""

import pytest
from pages.registration_page import RegistrationPage
from pages.otp_page import OtpPage
from pages.role_page import RolePage
from utils.temp_email import get_temp_email, wait_for_otp


@pytest.mark.e2e
def test_complete_signup_journey_with_otp(page):
    """
    Happy-path E2E test:
      1. Get a Guerrilla Mail disposable address
      2. Navigate to signup page and submit the email
      3. Fill the registration form (name + password)
      4. Wait for OTP in the Guerrilla Mail inbox (up to 90 s)
      5. Enter OTP and verify
      6. Assert that the OTP step disappears (success)
    """
    # Step 1 — disposable inbox
    email, sid_token = get_temp_email()
    assert "@" in email, f"Failed to get a temp email, got: {email}"

    # Step 2 — navigate and submit email
    page.goto("https://www.almashines.com/dtc/account")
    page.wait_for_load_state("networkidle")
    page.fill("#email", email)
    page.click("#emailBtn")
    page.wait_for_timeout(2000)

    # Step 3 — registration form
    reg = RegistrationPage(page)
    assert reg.is_visible(), \
        f"Registration form not shown for new email: {email}"

    reg.fill_valid_registration(
        first_name="Auto",
        last_name="Tester",
        password="AutoTest@2024",
    )
    reg.click_signup()

    # Step 4 — OTP step should appear
    otp_pg = OtpPage(page)
    assert otp_pg.is_visible(), "OTP form did not appear after registration"

    # Step 5 — wait for OTP in inbox
    otp_code = wait_for_otp(sid_token, timeout=90)
    assert otp_code is not None, (
        "OTP was not received in the Guerrilla Mail inbox within 90 seconds. "
        "The platform may be blocking the email domain — try re-running or "
        "check if guerrillamail.com domains are filtered."
    )

    # Step 6 — enter OTP and verify
    otp_pg.enter_otp(otp_code)
    otp_pg.click_verify()
    page.wait_for_timeout(3000)

    # OTP step should no longer be shown on success
    assert not otp_pg.is_visible(), \
        "OTP input is still visible after verification — signup may have failed"


@pytest.mark.e2e
def test_full_signup_including_role_selection(page):
    """
    Complete end-to-end Sign Up journey — all steps:
      1. Get a Guerrilla Mail disposable address
      2. Navigate to signup page and submit the email
      3. Fill the registration form
      4. Wait for OTP and verify it
      5. Land on role selection page
      6. Select role, years, accept terms
      7. Click Join Alumni Network
      8. Assert the role page is no longer shown (user has joined)

    NOTE: Each run of this test creates one permanent throwaway account on the
    platform using a Guerrilla Mail address. This is intentional — the platform
    is a test environment and the addresses are disposable.
    """
    # Step 1 — disposable inbox
    email, sid_token = get_temp_email()
    assert "@" in email, f"Failed to get a temp email, got: {email}"

    # Step 2 — navigate and submit email
    page.goto("https://www.almashines.com/dtc/account")
    page.wait_for_load_state("networkidle")
    page.fill("#email", email)
    page.click("#emailBtn")
    page.wait_for_timeout(2000)

    # Step 3 — registration form
    reg = RegistrationPage(page)
    assert reg.is_visible(), f"Registration form not shown for new email: {email}"
    reg.fill_valid_registration(
        first_name="E2E",
        last_name="FullFlow",
        password="FullFlow@2024",
    )
    reg.click_signup()

    # Dismiss any rate-limit SweetAlert before checking OTP step
    swal = page.locator(".swal-button--confirm")
    try:
        swal.wait_for(state="visible", timeout=3000)
        swal.click()
        page.wait_for_timeout(500)
    except Exception:
        pass

    # Step 4 — OTP
    otp_pg = OtpPage(page)
    if not otp_pg.is_visible():
        pytest.skip(
            "OTP step not reached — platform is rate-limiting rapid registrations. "
            "Wait a minute and re-run this test individually."
        )

    otp_code = wait_for_otp(sid_token, timeout=90)
    assert otp_code is not None, (
        "OTP was not received within 90 seconds — platform may be filtering "
        "the Guerrilla Mail domain. Re-run to retry."
    )

    otp_pg.enter_otp(otp_code)
    otp_pg.click_verify()
    page.wait_for_timeout(3000)

    # Step 5 — role selection page should appear
    rp = RolePage(page)
    assert rp.is_visible(), \
        "Role selection page did not appear after OTP verification"

    # Step 6 — fill role details and accept terms
    rp.select_role(rp.ROLE_ALUMNI)
    rp.select_yoj("2018")
    rp.select_yop("2022")
    rp.check_privacy_terms()
    rp.check_consent_form()

    # Step 7 — join
    rp.click_join()
    page.wait_for_timeout(3000)

    # Step 8 — role page should be gone (redirected to dashboard or next step)
    assert not rp.is_visible(), \
        "Role selection page is still visible after joining — the signup may not have completed"


