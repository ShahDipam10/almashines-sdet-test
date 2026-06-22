"""
Test 02 — Email Entry Step

Covers input validation at the very first step:
  - Empty submission
  - Various invalid email formats
  - Valid formats (including Gmail alias with +)

None of these tests proceed past the email step.
"""

import pytest


@pytest.mark.regression
def test_empty_email_does_not_proceed(signup_page):
    """Clicking submit with an empty field should keep the user on the email step."""
    signup_page.click_submit()
    signup_page.page.wait_for_timeout(1000)
    assert signup_page.is_on_email_step(), "Should stay on email step when email is empty"


@pytest.mark.regression
def test_invalid_email_no_at_sign(signup_page):
    """'notanemail' is not a valid email — page should not advance."""
    signup_page.submit_email("notanemail")
    assert signup_page.is_on_email_step(), "Should stay on email step for email missing '@'"


@pytest.mark.regression
def test_invalid_email_no_domain(signup_page):
    """'user@' has no domain — page should not advance."""
    signup_page.submit_email("user@")
    assert signup_page.is_on_email_step(), "Should stay on email step for email missing domain"


@pytest.mark.regression
def test_invalid_email_no_tld(signup_page):
    """'user@domain' has no TLD — page should not advance."""
    signup_page.submit_email("user@domain")
    assert signup_page.is_on_email_step(), "Should stay on email step for email missing TLD"


@pytest.mark.regression
def test_invalid_email_with_spaces(signup_page):
    """Spaces inside an email address are not valid."""
    signup_page.submit_email("user @gmail.com")
    assert signup_page.is_on_email_step(), "Should stay on email step for email with spaces"


@pytest.mark.regression
def test_invalid_email_double_at(signup_page):
    """'user@@gmail.com' is malformed."""
    signup_page.submit_email("user@@gmail.com")
    assert signup_page.is_on_email_step(), "Should stay on email step for double-@ email"


@pytest.mark.regression
def test_valid_email_proceeds_to_next_step(signup_page):
    """A properly formatted email should leave the email step (go to login or registration form)."""
    from utils.data_generators import generate_test_email
    signup_page.submit_email(generate_test_email())
    # After submit the page should show either the login form or registration form
    assert not signup_page.is_on_email_step() or \
        signup_page.page.locator("#fname").is_visible() or \
        signup_page.page.locator("#passwordLogin").is_visible(), \
        "A valid email should advance past the email step"


@pytest.mark.regression
def test_gmail_plus_alias_is_accepted(signup_page):
    """Gmail alias (user+tag@gmail.com) is a valid email format."""
    from utils.data_generators import generate_test_email
    alias = generate_test_email()   # already uses +alias format
    signup_page.submit_email(alias)
    assert not signup_page.is_on_email_step(), \
        "Gmail +alias emails should be accepted as valid"
