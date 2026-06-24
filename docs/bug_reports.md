# Bug Reports — AlmaShines Sign Up / Login Flow

**Reporter:** Dipam Shah  
**Date:** 2026-06-23 (BUG-001 to BUG-003) · 2026-06-24 (BUG-004 to BUG-011)  
**Environment:** `https://www.almashines.com/dtc/account` (Production / Test Platform)  
**Browser:** Chromium 124 (via Playwright 1.44.0)

---

## BUG-001: Email Without Top-Level Domain (TLD) Is Accepted as Valid

**Severity:** High  
**Priority:** High  
**Type:** Functional / Validation  
**Status:** Open  
**Automated test:** `tests/test_02_email_step.py::test_invalid_email_no_tld` *(intentional fail — documents this bug)*

### Description

The email submission form on the sign-up page accepts `user@domain` (a string with an `@` symbol but no TLD such as `.com` or `.org`) as a valid email address, even though no such email can receive messages. The platform proceeds to show the registration form for this address.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Type `user@domain` in the email field (no dot after the domain)
3. Click the **Continue** button

### Actual Result

- The form accepts the input and transitions to the next step (registration form for a new address, or login form if already registered)
- No validation error is displayed

### Expected Result

- The form should display a validation error such as *"Please enter a valid email address"*
- The user should remain on the email entry step until a syntactically valid address is provided

### Impact

- Users can create accounts with unreachable email addresses, meaning OTP codes will never be delivered
- This breaks the core account-creation flow silently (user is stuck at OTP step with no way to proceed)
- Could be exploited to register accounts that bypass email verification by exhausting the OTP retry window

### Root Cause (Hypothesis)

The client-side AngularJS validation uses a regex pattern that checks for the presence of `@` but does not enforce the requirement for at least one dot after the `@`. A stricter RFC-5321 compliant regex or the HTML5 `type="email"` attribute would reject this input.

### Recommended Fix

Apply a stricter email regex on both client and server side, for example:
```
/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
```
Or rely on the HTML `<input type="email">` attribute which natively rejects missing TLDs in modern browsers.

---

## BUG-002: Registration Sign Up Button Silently Does Nothing When Rate Limited

**Severity:** High  
**Priority:** High  
**Type:** UX / Error Handling  
**Status:** Open  
**Automated test:** `conftest.py::otp_page` fixture (skips with diagnostic message when triggered)

### Description

When multiple registrations are submitted in quick succession from the same IP address, the platform enforces a rate limit — but gives the user **zero feedback** that this has happened. Clicking the Sign Up button shows a brief loading state and then stops. No error message, no dialog, no redirect. The page looks exactly the same as before the click, making it appear as though the button is broken or the page has frozen.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Submit a new email, fill the registration form, reach the OTP step — note the flow works
3. Navigate back and immediately repeat with a fresh email two to three more times (within ~60 seconds)
4. On the third or fourth attempt, fill the registration form and click **Sign Up**

### Actual Result

- The Sign Up button shows a loading/spinner state briefly
- Then returns to its normal state
- **Nothing else happens** — no error message, no SweetAlert dialog, no navigation to the OTP step
- The user has no indication that they have been rate limited, how long to wait, or what to do next
- The only way to diagnose this is to inspect the Network tab in DevTools and observe the API response

### Expected Result

The platform should display a clear, user-facing message, for example:
> *"Too many registration attempts. Please wait a few minutes before trying again."*

At minimum, any error response from the server should be surfaced to the user rather than silently swallowed.

### Observed Behaviour History

An earlier version of this behaviour showed a generic SweetAlert dialog on rate limiting. That dialog has since disappeared, making the current failure **strictly worse** — at least a vague dialog gave the user a signal that something went wrong.

### Impact

- **Regular users**: Anyone who double-clicks the button, has a slow connection and retries, or refreshes and resubmits will be silently blocked with no way to know why or how to recover
- **QA / automation**: Test suites that run multiple signups hit this limit and see the button silently do nothing — making it ambiguous whether the failure is a product bug or a rate-limit side effect, adding debugging overhead

### Root Cause (Hypothesis)

The server returns an error response (likely HTTP 429 Too Many Requests) when the rate limit is hit, but the AngularJS error handler either swallows the response body entirely or maps it to no UI output. The button's loading state completes without any success or failure branch being rendered.

### Recommended Fix

1. Map the rate-limit API response to a user-facing error — a SweetAlert, an inline message, or a toast notification
2. Include a `Retry-After` value in the response and show the user how long to wait
3. Disable or debounce the Sign Up button after the first click to prevent accidental rapid resubmission

---

## BUG-003: Sequential Numeric Signup IDs in URL Allow Account Enumeration

**Severity:** Medium  
**Priority:** High  
**Type:** Security  
**Status:** Open  
**Evidence URL:** `https://www.almashines.com/dtc/switch?signup=1771&redirect=undefined&source=account`

### Description

After successful OTP verification, the platform redirects the user to the role selection page at:

```
/dtc/switch?signup=<numeric_id>&redirect=undefined&source=account
```

The `signup` parameter is a small, incrementing integer (e.g., `1771`). Sequential numeric IDs in URLs are a well-known security anti-pattern because they allow:

1. **Account enumeration** — an attacker can iterate `signup=1`, `signup=2`, … to discover how many accounts exist and potentially access role-selection pages for other users' incomplete signups
2. **Information disclosure** — the total account count is visible from the highest observed ID, which may be considered business-sensitive data
3. **Incomplete signup hijack** — if the role-selection page does not verify that the authenticated session owns the `signup` ID, an attacker could complete or manipulate another user's pending signup

### Steps to Reproduce

1. Complete a full signup up to the role selection page; note the `signup=N` value in the URL
2. Manually change the `signup` parameter to `N-1`, `N-2`, etc.
3. Observe whether the page loads with another user's pending signup context

### Actual Result

The `signup=1771` ID is clearly sequential and integer-based, as confirmed during testing. The behaviour when modifying the ID (whether it loads another user's context or correctly rejects the request) requires further investigation with a second test account.

### Expected Result

One or more of the following mitigations should be in place:
- The `signup` parameter should use a non-guessable token (e.g., a UUID or signed JWT) rather than a sequential integer
- The server should verify that the authenticated session's user ID matches the owner of the `signup` record before rendering the role selection page
- The parameter should expire after a short time window

### Recommended Fix

Replace the integer `signup` ID with a cryptographically random, single-use token (UUID v4 or HMAC-signed value) generated at the time of OTP verification and tied to the user's session. This eliminates guessability without changing the page's functional behaviour.

---

## BUG-004: Back Button on OTP Step Returns to Email Entry Instead of Registration Form

**Severity:** Medium  
**Priority:** Medium  
**Type:** UX / Navigation  
**Status:** Open  
**Automated test:** `tests/test_05_otp_step.py::test_back_button_from_otp_returns_to_email_step` *(test documents current behaviour — back lands on email step, not registration form)*

### Description

When a user is on the OTP verification step and clicks the **Back** button, the platform navigates them all the way back to the initial email entry page instead of the registration form they just filled out. The email entry page is the very first step of the flow — it makes no sense to reset to this point when the user has already submitted their email, filled all their registration details, and had the OTP sent to their inbox.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a new (unregistered) email and click **Next**
3. Fill in the registration form (First Name, Last Name, Password, Confirm Password) and click **Sign Up**
4. The OTP verification step appears — at this point click the **Back** button

### Actual Result

The user is taken back to the **email entry page** (step 1 of the flow). The email field is pre-filled from the session, but the user still has to click Next again to get back to the registration form.

### Expected Result

The **Back** button on the OTP step should return the user to the **registration form** (the immediately preceding step) so they can review or correct their details without unnecessary navigation overhead.

### Why This Is a Problem

The OTP has already been sent to the user's email by the time they are on the OTP step. There is no functional reason to go back to email entry — the email is already known and pre-filled. The user may want to go back simply to fix a typo in their name or check their password. Instead, the platform forces them through an extra unnecessary step (email entry → click Next → registration form reappears) before they can do so.

### Impact

- Poor navigation experience — every Back action from OTP forces an extra redundant click through email entry
- Users who don't notice the email is pre-filled may think they need to start the entire flow again
- Counterintuitive for users who expect Back to mean "previous step"

### Root Cause (Hypothesis)

The Back button triggers Angular's `hideDetailsForm()` function which resets the entire form state to step 1 (email entry) rather than stepping back one level to the registration form. This is a single flat reset rather than a step-by-step back navigation.

### Recommended Fix

Implement step-aware back navigation. The Back button on the OTP step should call a function that returns specifically to the registration form state, not reset the entire flow. Alternatively, maintain a navigation stack so Back always goes to the previous visible step.

---

## BUG-005: Password Field Retained in Sensitive Situations — Account Lockout and Post-Navigation

**Severity:** Medium  
**Priority:** High  
**Type:** Security / UX  
**Status:** Open

### Description

The platform never clears the password field in situations where it should — specifically after an account lockout due to multiple failed login attempts, and after navigating back through the sign up flow. In both cases, the password remains visible and filled in the input field, which is a security concern.

This is not one isolated incident but a pattern: the platform treats the password field the same as any other text field and never proactively clears it regardless of what security event just occurred.

### Scenario A — Password Retained After Account Lockout

#### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a registered email and click **Next** — the login form appears
3. Enter the **wrong password** multiple times until the account is locked (the platform blocks login for 30 minutes)
4. Navigate back to the main page and return to the login form
5. Click **Next** on the pre-filled email

#### Actual Result

The password field is still filled with the previously entered (wrong) password. The user is shown a lockout message but the password value was never wiped from the input.

#### Expected Result

After a lockout event, the password field should be cleared. Retaining a password (even a wrong one) in a field after a security block is poor practice — it exposes what the user was typing and gives no signal that the field should be re-entered fresh.

### Scenario B — Password Retained When Navigating Back from OTP Step

#### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a new email, fill the registration form including a password, and click **Sign Up**
3. On the OTP step, click **Back** — lands on email entry (see BUG-004)
4. Click **Next** on the pre-filled email — registration form reappears

#### Actual Result

The password and confirm-password fields are still filled with the previously entered values. The form looks exactly as the user left it.

#### Expected Result

Returning to the registration form via Back/navigation reset should clear the password fields. While pre-filling name fields is helpful and acceptable, password fields should always be cleared on any navigation reset as a security best practice. The user should re-enter their password intentionally.

### Combined Impact

- A user who walks away from the screen after a lockout has their (attempted) password exposed in plain sight if password visibility was toggled on
- Automating or scripting an attack is slightly easier since the platform retains typed values
- Inconsistent with industry-standard behaviour where password fields are cleared after failed authentication or page transitions

### Root Cause (Hypothesis)

Angular's two-way data binding (`ng-model`) keeps the password value in the scope model even after navigation events. There is no explicit `$scope.formData.password = ''` call triggered on lockout or on back navigation reset.

### Recommended Fix

1. On lockout: explicitly clear the password field value in the lockout handler before showing the blocking message
2. On `hideDetailsForm()` (back navigation reset): clear all password-related fields from the scope model as part of the reset
3. As a general rule: password fields should never retain their value across any authentication failure or navigation reset event
