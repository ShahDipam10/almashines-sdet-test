# Manual Test Cases — AlmaShines Sign Up / Login Flow

**Scope:** Sign Up and Login flow at `https://www.almashines.com/dtc/account`
**Tester:** Dipam Shah
**Date:** 2026-06-23
**Platform:** AlmaShines (Test Environment)

---

## Why Manual?

The automated suite covers happy-path and common-error scenarios for the email entry, registration, OTP, and role-selection steps. The cases below are **intentionally left as manual** because:

- They verify non-deterministic time-based behaviour (OTP expiry, email delivery latency)
- They check purely visual / sensory attributes (layout, accessibility, responsive breakpoints)
- They require observation of browser-specific quirks outside a single Chromium runner

---

## TC-M-01: OTP Expiry Validation

**Category:** OTP Security  
**Priority:** High

**Steps:**
1. Complete the registration form with a valid new email
2. When the OTP input appears, do **not** enter the OTP
3. Wait for the OTP to expire (expected window: 5–15 minutes — confirm with the platform spec)
4. Enter any OTP code and click **Verify**

**Expected Result:** Platform shows an error message indicating the OTP has expired and prompts the user to request a new one.

**Why Manual:** Waiting for OTP expiry requires a real-time delay that would make automated tests prohibitively slow (potentially 10+ minutes of wall time). The test is quick to verify manually but impractical to automate in a standard CI pipeline.

---

## TC-M-02: Resend OTP Functionality

**Category:** OTP Flow  
**Priority:** Medium

**Steps:**
1. Complete registration form with a new email and arrive at the OTP step
2. Without entering an OTP, click **Resend OTP**
3. Check the email inbox for a new OTP
4. Verify the new OTP code works

**Expected Result:**
- A new OTP is delivered to the inbox
- The previous OTP is invalidated (entering the old code after resend should fail)

**Why Manual:** Verifying that the old OTP is invalidated requires sequential time-dependent checks. Guerrilla Mail polling would not reliably distinguish "new" vs "old" OTP messages without parsing delivery timestamps.

---

## TC-M-03: Responsive Layout on Mobile Viewports

**Category:** UI / Accessibility  
**Priority:** Medium

**Steps:**
1. Open the sign up page on a mobile device (or Chrome DevTools with iPhone 12 preset — 390×844)
2. Check that all elements (email input, submit button, social login buttons) are visible and usable without horizontal scrolling
3. Check OTP input and Verify button on the OTP step
4. Check the role selection form including dropdown and checkboxes

**Expected Result:** All interactive elements are accessible within the mobile viewport; no horizontal overflow; touch targets are at least 44×44 px.

**Why Manual:** Visual layout checks and touch usability judgements are subjective and hard to assert in automated tests. While viewport resizing is possible in Playwright, confirming that elements don't overflow or that tap targets are comfortable requires human evaluation.

---

## TC-M-04: Cross-Browser Compatibility

**Category:** Browser Compatibility  
**Priority:** Medium

**Steps:**
1. Run the core sign up flow (email entry → registration → OTP) in:
   - Firefox (latest)
   - Safari (latest macOS)
   - Edge (latest)
2. Confirm all steps work identically to the Chromium baseline

**Expected Result:** No browser-specific rendering or JavaScript errors; flow completes successfully in all browsers.

**Why Manual (partially):** The automated suite only targets Chromium to keep CI fast. Full cross-browser runs are better suited to a nightly schedule or pre-release gate. Safari in particular requires a macOS runner which is not configured in the current CI workflow.

---

## TC-M-05: Deep Link Redirect After Login

**Category:** Navigation / Authentication  
**Priority:** Medium

**Steps:**
1. While logged out, navigate directly to a protected URL (e.g., `https://www.almashines.com/dtc/switch?signup=1&redirect=/dashboard`)
2. Complete login
3. Observe where the user is redirected post-login

**Expected Result:** After login, the user is redirected to the originally intended destination (the `redirect` query parameter is honoured).

**Why Manual:** Testing deep link handling requires knowing a valid protected URL that exists in the test environment. This is environment-specific and cannot be reliably verified without access to the platform's routing configuration.
