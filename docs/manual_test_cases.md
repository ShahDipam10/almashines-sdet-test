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
3. Wait for the OTP to expire (expected window: 10 minutes as mentioned in the OTP email)
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

---

## TC-M-06: Sequential Signup ID Enumeration (BUG-003)

**Category:** Security  
**Priority:** High

**Steps:**
1. Complete a full signup up to the role selection page
2. Note the `signup=N` value in the URL (e.g. `?signup=1771`)
3. Manually edit the URL — try `signup=1770`, `signup=1769`, etc.
4. Observe whether the page loads another user's pending signup context or correctly rejects the request

**Expected Result:** The platform should reject any `signup` ID that does not belong to the currently authenticated session — either redirecting to an error page or returning to the start of the flow.

**Why Manual:** Verifying server-side authorisation requires manually manipulating the URL and observing the response. Automating this safely would require two separate test accounts and the ability to inspect which session owns which ID — beyond the scope of this test environment.

---

## TC-M-07: Page Refresh During OTP Step (BUG-004)

**Category:** State Management / Reliability  
**Priority:** High

**Steps:**
1. Complete the registration form and reach the OTP verification step
2. Refresh the browser (F5) while on the OTP step
3. The platform redirects to the email entry page — note the URL now contains `?cid=XXXX`
4. Enter the email again and click **Next**
5. Repeat steps 2–4 several times to observe the intermittent behaviour

**Expected Result:** After a refresh, the platform should either restore the session state cleanly or reset to the beginning of the flow with a clear message. Under no circumstance should the email submission result in an infinite loading state.

**Why Manual:** The bug is intermittent — it only triggers sometimes due to a race condition. Automated tests would give non-deterministic results and could not reliably assert the failure state. Manual observation across multiple attempts is the only reliable way to reproduce and confirm the bug.

---

## TC-M-08: Password Field Retained After Account Lockout and Back Navigation (BUG-006)

**Category:** Security / UX  
**Priority:** Medium

**Steps:**
**Scenario A — After lockout:**
1. Enter a registered email and proceed to the login form
2. Enter the wrong password multiple times until the account is locked
3. Navigate away and return to the login form
4. Observe whether the password field is still populated

**Scenario B — After back navigation from OTP:**
1. Complete the registration form and reach the OTP step
2. Click **Back** — lands on email entry page
3. Click **Next** on the pre-filled email — registration form reappears
4. Observe whether the password field is still populated

**Expected Result:** In both scenarios the password field should be cleared. Retaining a password after a security event or navigation reset is a security anti-pattern.

**Why Manual:** Triggering an account lockout requires multiple failed login attempts against a real account, which is destructive to test data and unsuitable for automation. The back-navigation scenario involves the locked account state which cannot be easily replicated in isolation.

---

## TC-M-09: Long Password Overlaps Show/Hide Eye Icon (BUG-008)

**Category:** UI / Layout  
**Priority:** Low

**Steps:**
1. Navigate to the registration form with a new email
2. In the **Password** field, type or paste a string of 40+ characters
3. Observe the right end of the password input field

**Expected Result:** The typed text should stop before reaching the eye icon. The icon should remain fully visible and clickable at all times regardless of password length.

**Why Manual:** This is a purely visual layout defect. Playwright can resize viewports and fill fields but cannot reliably assert that two elements are not visually overlapping — that judgement requires human observation.

---

## TC-M-10: Browser Autofill Causes Placeholder Overlap (BUG-010)

**Category:** UI / Browser Compatibility  
**Priority:** Low

**Steps:**
**Scenario A — Email field:**
1. Ensure login credentials for `almashines.com` are saved in the browser
2. Navigate to `https://www.almashines.com/dtc/account`
3. Observe the email field — the browser should autofill the saved address
4. Check whether the placeholder label overlaps with the autofilled value

**Scenario B — Password field:**
1. Navigate to the registration form
2. Click the Password field — the browser may suggest a saved or auto-generated password
3. Accept the browser suggestion
4. Check whether the placeholder label overlaps with the suggested value

**Expected Result:** The floating placeholder label should move out of the way (or disappear) as soon as the browser fills the field, exactly as it does when the user types manually.

**Why Manual:** Browser autofill behaviour is browser-specific and session-dependent (requires saved credentials in the browser profile). Playwright's `page.fill()` fires synthetic input events that do not trigger the autofill path — the real autofill behaviour can only be observed in an interactive browser session.
