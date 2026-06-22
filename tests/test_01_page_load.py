"""
Test 01 — Page Load (Smoke Tests)

Verifies that the Sign Up / Login page loads correctly and all key
elements are present before any interaction.
"""

import pytest


@pytest.mark.smoke
def test_page_title_is_correct(signup_page):
    assert signup_page.get_title() == "Sign In / Sign Up"


@pytest.mark.smoke
def test_page_url_is_correct(signup_page):
    assert "almashines.com/dtc/account" in signup_page.get_url()


@pytest.mark.smoke
def test_email_input_is_visible(signup_page):
    assert signup_page.page.locator(signup_page.EMAIL_INPUT).is_visible()


@pytest.mark.smoke
def test_submit_button_is_visible(signup_page):
    assert signup_page.page.locator(signup_page.SUBMIT_BTN).is_visible()


@pytest.mark.smoke
def test_facebook_button_is_visible(signup_page):
    assert signup_page.page.locator(signup_page.FB_BTN).is_visible()


@pytest.mark.smoke
def test_google_button_is_visible(signup_page):
    assert signup_page.page.locator(signup_page.GOOGLE_BTN).is_visible()


@pytest.mark.smoke
def test_linkedin_button_is_visible(signup_page):
    assert signup_page.page.locator(signup_page.LINKEDIN_BTN).is_visible()


@pytest.mark.smoke
def test_signup_login_heading_visible(signup_page):
    heading = signup_page.page.locator("h2", has_text="Signup / Login")
    assert heading.is_visible()
