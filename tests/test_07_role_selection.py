"""
Test 07 — Role Selection Page

After OTP verification the platform shows a role selection form
at /dtc/switch?signup=<id>. These E2E tests cover:
  - Page presence and heading
  - Role dropdown options
  - Dynamic year fields (appear only after a role is chosen)
  - Terms & consent checkboxes
  - Validation: cannot join without role or without accepting terms

All tests require the `role_page` fixture which performs a full signup
via Guerrilla Mail — mark: e2e.
"""

import pytest


# ---------------------------------------------------------------------------
# Page presence & structure
# ---------------------------------------------------------------------------

@pytest.mark.e2e
def test_role_page_heading_is_visible(role_page):
    heading = role_page.page.locator(role_page.PAGE_HEADING).first
    assert heading.is_visible(), \
        "Role selection page heading should be visible after OTP verification"


@pytest.mark.e2e
def test_role_page_heading_text(role_page):
    text = role_page.get_heading_text()
    assert "role" in text.lower() or "details" in text.lower(), \
        f"Heading should mention role/details, got: '{text}'"


@pytest.mark.e2e
def test_role_dropdown_is_visible(role_page):
    assert role_page.page.locator(role_page.ROLE_SELECT).is_visible(), \
        "Role dropdown should be present on role selection page"


@pytest.mark.e2e
def test_join_button_is_visible(role_page):
    assert role_page.page.locator(role_page.JOIN_BTN).is_visible(), \
        "'Join Alumni Network' button should be visible"


@pytest.mark.e2e
def test_privacy_checkbox_is_present(role_page):
    assert role_page.page.locator(role_page.PRIVACY_CHECKBOX).is_visible(), \
        "Privacy Policy checkbox should be present"


@pytest.mark.e2e
def test_consent_checkbox_is_present(role_page):
    assert role_page.page.locator(role_page.CONSENT_CHECKBOX).is_visible(), \
        "Consent Form checkbox should be present"


# ---------------------------------------------------------------------------
# Role dropdown options
# ---------------------------------------------------------------------------

@pytest.mark.e2e
def test_role_dropdown_contains_current_student(role_page):
    options = role_page.get_role_options()
    assert role_page.ROLE_CURRENT_STUDENT in options, \
        f"'Current Student' option missing from role dropdown. Got: {options}"


@pytest.mark.e2e
def test_role_dropdown_contains_alumni(role_page):
    options = role_page.get_role_options()
    assert role_page.ROLE_ALUMNI in options, \
        f"'Alumni (Past Student)' option missing from role dropdown. Got: {options}"


@pytest.mark.e2e
def test_role_dropdown_contains_staff(role_page):
    options = role_page.get_role_options()
    assert role_page.ROLE_STAFF in options, \
        f"'Staff / Faculty' option missing from role dropdown. Got: {options}"


# ---------------------------------------------------------------------------
# Dynamic year fields
# ---------------------------------------------------------------------------

@pytest.mark.e2e
def test_year_fields_hidden_before_role_selection(role_page):
    """Year of Joining and Year of Graduation should not be visible until a role is chosen."""
    assert not role_page.is_yoj_visible(), \
        "Year of Joining field should be hidden before any role is selected"
    assert not role_page.is_yop_visible(), \
        "Year of Graduation field should be hidden before any role is selected"


@pytest.mark.e2e
def test_year_fields_appear_after_role_selection(role_page):
    """Selecting any role should reveal year input fields."""
    role_page.select_role(role_page.ROLE_CURRENT_STUDENT)
    assert role_page.is_yoj_visible(), \
        "Year of Joining should appear after selecting 'Current Student'"
    assert role_page.is_yop_visible(), \
        "Year of Graduation should appear after selecting 'Current Student'"


@pytest.mark.e2e
def test_year_fields_appear_for_alumni_role(role_page):
    role_page.select_role(role_page.ROLE_ALUMNI)
    assert role_page.is_yoj_visible() and role_page.is_yop_visible(), \
        "Year fields should appear after selecting 'Alumni (Past Student)'"


@pytest.mark.e2e
def test_year_fields_appear_for_staff_role(role_page):
    role_page.select_role(role_page.ROLE_STAFF)
    assert role_page.is_yoj_visible() and role_page.is_yop_visible(), \
        "Year fields should appear after selecting 'Staff / Faculty'"


# ---------------------------------------------------------------------------
# Checkbox interaction
# ---------------------------------------------------------------------------

@pytest.mark.e2e
def test_privacy_checkbox_can_be_checked(role_page):
    role_page.check_privacy_terms()
    assert role_page.is_privacy_checked(), \
        "Privacy Policy checkbox should be checkable by the user"


@pytest.mark.e2e
def test_consent_checkbox_can_be_checked(role_page):
    role_page.check_consent_form()
    assert role_page.is_consent_checked(), \
        "Consent Form checkbox should be checkable by the user"


# ---------------------------------------------------------------------------
# Validation — incomplete submissions stay on page
# ---------------------------------------------------------------------------

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
    # Deliberately leave checkboxes unchecked
    role_page.click_join()
    assert role_page.is_visible(), \
        "Without accepting terms, clicking Join should keep user on the role page"
