"""
Test 07 — Role Selection Page

After OTP verification the platform shows a role selection form
at /dtc/switch?signup=<id>. These E2E tests cover:
  - Page presence and heading
  - Role dropdown options
  - Dynamic year fields (appear only after a role is chosen)
  - Terms & consent checkboxes
  - Validation: cannot join without role or without accepting terms

Each test uses the `role_page` fixture which performs a full signup
via Guerrilla Mail — mark: e2e.
"""

import pytest


@pytest.mark.e2e
def test_role_page_loads_correctly(role_page):
    """Page heading is visible and contains expected text after OTP verification."""
    heading = role_page.page.locator(role_page.PAGE_HEADING).first
    assert heading.is_visible(), "Role selection page heading should be visible"
    text = role_page.get_heading_text()
    assert "role" in text.lower() or "details" in text.lower(), \
        f"Heading should mention role/details, got: '{text}'"


@pytest.mark.e2e
def test_role_page_key_elements_present(role_page):
    """Role dropdown, Join button, and both checkboxes must all be on the page."""
    assert role_page.page.locator(role_page.ROLE_SELECT).is_visible(), \
        "Role dropdown should be present"
    assert role_page.page.locator(role_page.JOIN_BTN).is_visible(), \
        "'Join Alumni Network' button should be present"
    assert role_page.page.locator(role_page.PRIVACY_LABEL).is_visible(), \
        "Privacy Policy checkbox label should be present"
    assert role_page.page.locator(role_page.CONSENT_LABEL).is_visible(), \
        "Consent Form checkbox label should be present"


@pytest.mark.e2e
def test_role_dropdown_has_all_options(role_page):
    """All three role options must be available in the dropdown."""
    options = role_page.get_role_options()
    for expected in (role_page.ROLE_CURRENT_STUDENT, role_page.ROLE_ALUMNI, role_page.ROLE_STAFF):
        assert expected in options, \
            f"'{expected}' missing from role dropdown. Got: {options}"


@pytest.mark.e2e
def test_year_fields_hidden_before_role_selection(role_page):
    """Year of Joining and Year of Graduation should be hidden until a role is chosen."""
    assert not role_page.is_yoj_visible(), \
        "Year of Joining should be hidden before any role is selected"
    assert not role_page.is_yop_visible(), \
        "Year of Graduation should be hidden before any role is selected"


@pytest.mark.e2e
def test_year_fields_appear_after_role_selection(role_page):
    """Selecting a role reveals both year fields (behaviour is the same for all 3 roles)."""
    role_page.select_role(role_page.ROLE_CURRENT_STUDENT)
    assert role_page.is_yoj_visible(), \
        "Year of Joining should appear after selecting a role"
    assert role_page.is_yop_visible(), \
        "Year of Graduation should appear after selecting a role"


@pytest.mark.e2e
def test_checkboxes_are_interactive(role_page):
    """Both Privacy Policy and Consent Form checkboxes should be checkable."""
    role_page.check_privacy_terms()
    role_page.check_consent_form()
    assert role_page.is_privacy_checked(), "Privacy Policy checkbox should be checkable"
    assert role_page.is_consent_checked(), "Consent Form checkbox should be checkable"


@pytest.mark.e2e
def test_join_without_role_stays_on_role_page(role_page):
    """Submitting without selecting a role should not advance the flow."""
    role_page.check_privacy_terms()
    role_page.check_consent_form()
    role_page.click_join()
    assert role_page.is_visible(), \
        "Without a role selected, clicking Join should keep user on the role page"


@pytest.mark.e2e
def test_join_without_terms_stays_on_role_page(role_page):
    """Submitting without accepting terms should not advance the flow."""
    role_page.select_role(role_page.ROLE_ALUMNI)
    role_page.select_yoj("2018")
    role_page.select_yop("2022")
    role_page.click_join()
    assert role_page.is_visible(), \
        "Without accepting terms, clicking Join should keep user on the role page"
