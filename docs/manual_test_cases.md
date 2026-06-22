# Manual Test Cases — AlmaShines Sign Up / Login Flow

**Scope:** Sign Up and Login flow at `https://www.almashines.com/dtc/account`
**Tester:** SDET Candidate
**Date:** 2026-06-23
**Platform:** AlmaShines (Test Environment)

---

## Why Manual?

The automated suite covers happy-path and common-error scenarios for the email entry, registration, OTP, and role-selection steps. The cases below are **intentionally left as manual** because:

- They rely on OAuth providers (social login) that cannot be automated without real credentials or a controlled IdP
- They verify non-deterministic time-based behaviour (OTP expiry, email delivery latency)
- They check purely visual / sensory attributes (layout, accessibility, responsive breakpoints)
- They involve side-effects that are hard to undo in automation (completed profile, joined network)
- They require observation of browser-specific quirks outside a single Chromium runner

---

## TC-M-01: Facebook OAuth Login

**Category:** Social Login  
**Priority:** High

**Steps:**
1. Navigate to `https://www.almashines.com/dtc/account`
2. Click **Continue with Facebook**
3. Complete Facebook OAuth login with a valid Facebook account
4. Observe redirect back to AlmaShines

**Expected Result:** User is authenticated and redirected to the dashboard or role selection page.

**Why Manual:** Automating OAuth requires real Facebook credentials or a mock IdP. Both introduce security risk or infrastructure overhead beyond the assignment scope. Facebook's bot-detection would also block headless automation.

---

## TC-M-02: Google OAuth Login

**Category:** Social Login  
**Priority:** High

**Steps:**
1. Navigate to `https://www.almashines.com/dtc/account`
2. Click **Continue with Google**
3. Complete Google OAuth login with a valid Google account
4. Observe redirect back to AlmaShines

**Expected Result:** User is authenticated and redirected to the dashboard or role selection page.

**Why Manual:** Same rationale as TC-M-01. Google's reCAPTCHA and account-activity checks actively block headless browsers.

---

## TC-M-03: LinkedIn OAuth Login

**Category:** Social Login  
**Priority:** Medium

**Steps:**
1. Navigate to `https://www.almashines.com/dtc/account`
2. Click **Continue with LinkedIn**
3. Complete LinkedIn OAuth login
4. Observe redirect back to AlmaShines

**Expected Result:** User is authenticated and redirected to dashboard or role selection page.

**Why Manual:** Same rationale as TC-M-01/02. LinkedIn rate-limits OAuth flows aggressively.

---

## TC-M-04: OTP Expiry Validation

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

## TC-M-05: Resend OTP Functionality

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

## TC-M-06: Forgot Password Flow

**Category:** Authentication Recovery  
**Priority:** High

**Steps:**
1. Enter a registered email and arrive at the login form
2. Click **Forgot password?**
3. Observe the recovery flow (email link or OTP)
4. Complete password reset
5. Log in with the new password

**Expected Result:** User can reset their password and log in successfully with the new credentials.

**Why Manual:** The forgot-password flow likely sends an email to the registered inbox. Automating this would require a real inbox that accepts password-reset emails — our `dipamshahaliantesting1@gmail.com` test account would need its password changed, breaking subsequent test runs. Manual execution preserves the stable test account.

---

## TC-M-07: Responsive Layout on Mobile Viewports

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

## TC-M-08: Cross-Browser Compatibility

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

## TC-M-09: Complete Role Selection and Join Network

**Category:** End-to-End Happy Path  
**Priority:** Critical

**Steps:**
1. Complete full signup (email → registration → OTP verification) with a brand-new email
2. On the role selection page, select **Alumni (Past Student)**
3. Select Year of Joining: **2018**
4. Select Year of Graduation: **2022**
5. Check both the Privacy Policy and Consent Form checkboxes
6. Click **Join Alumni Network**
7. Observe the resulting page

**Expected Result:** User successfully joins the network and is redirected to the alumni dashboard or a welcome/profile-completion screen.

**Why Manual:** This test has an irreversible side-effect — it actually creates a permanent account tied to the email. In automation this would litter the platform with test accounts. Manual execution lets the tester decide when to commit the action and can use a controlled email address whose cleanup is managed separately.

---

## TC-M-10: Session Persistence After Browser Restart

**Category:** Session / Authentication  
**Priority:** Low

**Steps:**
1. Complete login (email + password) on the sign in form
2. Close the browser entirely
3. Reopen the browser and navigate to `https://www.almashines.com/dtc/account`

**Expected Result:** The user remains logged in (session cookie persisted) OR is redirected to the login page (session not persisted) — either behaviour should be consistent and documented.

**Why Manual:** Automated tests use a fresh browser context per test run. Verifying cross-session persistence requires real browser state to survive process restart, which doesn't happen in automated Playwright contexts.

---

## TC-M-11: Password Visibility Toggle

**Category:** Usability  
**Priority:** Low

**Steps:**
1. Navigate to sign up and submit a new email to reach the registration form
2. Click the eye icon (if present) next to the Password field
3. Verify that the password text becomes readable
4. Click again to hide it

**Expected Result:** Password visibility toggles correctly between `type="password"` and `type="text"`.

**Why Manual:** The toggle exists in many login forms and is a quick manual check. The current registration form on this platform was observed without a toggle icon during testing — this case is listed to confirm its absence is intentional.

---

## TC-M-12: Deep Link Redirect After Login

**Category:** Navigation / Authentication  
**Priority:** Medium

**Steps:**
1. While logged out, navigate directly to a protected URL (e.g., `https://www.almashines.com/dtc/switch?signup=1&redirect=/dashboard`)
2. Complete login
3. Observe where the user is redirected post-login

**Expected Result:** After login, the user is redirected to the originally intended destination (the `redirect` query parameter is honoured).

**Why Manual:** Testing deep link handling requires knowing a valid protected URL that exists in the test environment. This is environment-specific and cannot be reliably verified without access to the platform's routing configuration.
