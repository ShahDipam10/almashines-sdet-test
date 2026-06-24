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

## BUG-004: Page Refresh on OTP Step Causes Intermittent Infinite Loading on Email Submission

**Severity:** High  
**Priority:** High  
**Type:** Functional / State Management / Race Condition  
**Status:** Open  
**Evidence:** Screenshot shared during manual testing — email field stuck in loading state with red border after refresh-triggered navigation

### Description

When a user refreshes the browser while on the OTP verification step, the platform loses its Angular in-memory session state and redirects the user back to the email entry page. At this point the URL gains a `?cid=1771` institution ID parameter that was not present in the original flow. When the user enters their email and clicks Next from this state, the behavior is **intermittent**:

- Sometimes: the email submission triggers **infinite loading** — the Next button spins indefinitely and nothing happens. No error message, no navigation, no way forward except closing and reopening the tab.
- Sometimes: the submission works correctly and proceeds to the sign up / login form as expected.

The same URL, same parameter, same action — two different outcomes. This inconsistency is the core of the bug and points to a **race condition** rather than a simple broken state.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Submit a new email, fill the registration form, click Sign Up — reach the OTP verification step
3. **Refresh the browser** (F5 or browser refresh button) while on the OTP step
4. The platform redirects to the email entry page — note the URL now shows `?cid=1771` appended
5. Enter the email again and click **Next**

### Actual Result

**Intermittent outcome A (bug):** The Next button enters a loading/spinning state and stays there indefinitely. The email field shows a red border. No error message is displayed. No navigation occurs. The user has no indication of what went wrong or what to do next. The only recovery is to close the tab and start fresh.

**Intermittent outcome B (works):** On a subsequent refresh with the same URL and parameter still present, the submission goes through correctly and the platform navigates to the appropriate next step.

### Expected Result

Refreshing the browser during any step of the sign up flow should result in one of these clean, predictable outcomes:
- The platform restores the session state and returns the user to where they were, OR
- The platform cleanly resets to the beginning of the flow with a clear message (e.g. *"Your session expired. Please start again."*)

Under no circumstance should refreshing result in a silent infinite loading state with no recovery path.

### Why Intermittent Bugs Are Particularly Serious

Unlike a consistently broken feature, intermittent behavior is harder to catch, harder to reproduce, and tends to be dismissed until it is properly documented. The inconsistency here strongly suggests a **timing/race condition** — the Angular app sometimes initializes its state fast enough to handle the incoming email submission and sometimes does not. This type of issue typically worsens under server load, meaning more users hitting the platform simultaneously increases the frequency of the broken outcome.

### Impact

- Users who refresh during the OTP step (a completely normal action — refreshing is standard browser behaviour) can get permanently stuck with no error or guidance
- No recovery path is available from within the page — the user must close and reopen the tab
- The intermittent nature means it will appear to "work" during some QA passes and only surface in production

### Root Cause (Hypothesis)

When the browser refreshes on the OTP step, Angular's in-memory session context (signup state, email, form data) is wiped. The URL picks up the `?cid=1771` institution ID as a query parameter. When the user submits an email from this state, the Angular controller or the backend API call may attempt to reference session data that no longer exists, leading to a hanging promise or unresolved API call. The intermittency suggests the backend sometimes has the context cached (works) and sometimes does not (hangs).

### Recommended Fix

1. Implement proper session persistence (localStorage or server-side session) so that a page refresh during sign up restores state gracefully
2. Add a timeout on all API calls within the sign up flow — if a call does not resolve within a reasonable window (e.g. 10 seconds), surface an error message to the user
3. Strip or sanitise unexpected URL parameters (like `?cid=1771`) on page load to avoid the Angular router entering a confused state
4. At minimum, add a global error handler that catches hanging/unresolved states and shows the user a clear message with a "Start over" action

---

## BUG-005: Back Button on OTP Step Returns to Email Entry Instead of Registration Form

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

## BUG-006: Password Field Retained in Sensitive Situations — Account Lockout and Post-Navigation

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
3. On the OTP step, click **Back** — lands on email entry (see BUG-005)
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

---

## BUG-007: 250-Character Email Silently Rejected With Only a Red Border — No Error Message

**Severity:** Medium  
**Priority:** Medium  
**Type:** UX / Validation  
**Status:** Open

### Description

When a user enters an email address that is exactly 250 characters long (including the `@gmail.com` domain portion) and clicks **Next**, the platform silently rejects the input by turning the email field red. No error message, tooltip, or inline text is shown to explain what went wrong. The user has no idea whether the issue is the length, an invalid character, or something else entirely.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Construct an email with a very long local part so the total length reaches 250 characters (e.g. `aaaa...aaa@gmail.com`)
3. Paste it into the email field and click **Next**

### Actual Result

The email input field turns red (error state). No error message is displayed anywhere on the page. No navigation occurs. The user receives zero explanation.

### Expected Result

A clear, inline validation message should appear, for example:
> *"Email address is too long. Please use an address with fewer than X characters."*

The maximum allowed length should be enforced and communicated upfront, not silently after submission.

### Impact

- Users with legitimate long email addresses (uncommon but valid per RFC) cannot sign up and receive no guidance on what to fix
- Silent red border alone is not accessible — screen readers and users with colour blindness get no signal at all
- Creates confusion: the user may assume the platform is broken rather than understanding it is a length restriction

### Root Cause (Hypothesis)

The AngularJS model or the backend API enforces a character limit on the email field but the error handler only triggers the red-border CSS class without populating an error message string in the template.

### Recommended Fix

1. Define and document the maximum allowed email length
2. Show an explicit inline error message when the limit is exceeded
3. Optionally enforce the limit client-side with `maxlength` on the input so the user cannot even type past the limit

---

## BUG-008: Long Password Text Overlaps the Show/Hide Eye Icon

**Severity:** Low  
**Priority:** Low  
**Type:** UI / Layout  
**Status:** Open  
**Evidence:** Screenshot captured during manual testing — password text visually overlaps the eye icon in the password field  
**Screenshot:** https://prnt.sc/_cIJnjX2wKgS

### Description

When a sufficiently long password is typed into the password field on the registration form, the text content overflows and visually overlaps with the show/hide password toggle icon (the eye icon) on the right side of the field. The icon becomes partially or fully obscured, making it difficult to click.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a new email and proceed to the registration form
3. In the **Password** field, type a long string (approximately 30+ characters)
4. Observe the right end of the password field

### Actual Result

The password text bleeds into the eye icon area. The icon is visually covered by the text, making the toggle hard to see and harder to click accurately.

### Expected Result

The password input field should have sufficient right-side padding to ensure the typed text never overlaps the eye icon, regardless of password length.

### Impact

- Users who type long passwords (a security best practice) cannot easily toggle password visibility
- Pure cosmetic/layout issue but it degrades the experience for security-conscious users who rely on the toggle to verify what they typed

### Root Cause (Hypothesis)

The password `<input>` element does not have a `padding-right` value large enough to account for the absolutely-positioned eye icon overlay. Long text simply runs to the end of the input's text area without being clipped before the icon.

### Recommended Fix

Add sufficient `padding-right` to the password input so text never reaches the icon area:
```css
input[type="password"] {
  padding-right: 40px; /* adjust to match eye icon width */
}
```

---

## BUG-009: Very Long Name and Password Values Silently Block Sign Up

**Severity:** High  
**Priority:** High  
**Type:** Functional / Validation  
**Status:** Open  
**Evidence:** Screenshot captured during manual testing — Sign Up button clicked with no response after entering extremely long field values  
**Screenshot:** https://prnt.sc/FiYUiUeoINRi

### Description

When excessively long values are entered in the First Name, Last Name, and/or Password fields on the registration form and the user clicks **Sign Up**, nothing happens. No error message, no navigation to the OTP step, no visible feedback of any kind. The button appears to do nothing at all.

This is a silent failure on what should be a clearly communicated input validation error.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a valid new email and click **Next**
3. On the registration form, enter an extremely long string in **First Name** (e.g. 200+ characters), repeat for **Last Name** and **Password**
4. Click **Sign Up**

### Actual Result

The Sign Up button does nothing — no loading state, no error message, no navigation. The form stays exactly as it was. The user has no indication that field length is the problem.

### Expected Result

The platform should either:
- Enforce a `maxlength` attribute on the input so the user cannot type beyond the limit, OR
- Display a clear validation error on submit, such as *"First name must be 50 characters or fewer"*

Under no circumstance should clicking Sign Up result in complete silence.

### Impact

- Users who paste long values (e.g. accidentally paste the wrong content) are permanently stuck on the form with no guidance
- Indistinguishable from BUG-002 (rate limiting silent failure) from the user's perspective — both result in Sign Up doing nothing
- Potentially a server-side rejection that is not surfaced to the frontend

### Root Cause (Hypothesis)

The backend likely enforces field length limits and returns a validation error, but the AngularJS form handler either ignores the error response or the `ng-maxlength` directive silently prevents submission without triggering a visible error template.

### Recommended Fix

1. Add `maxlength` attributes to all text inputs with clearly defined limits
2. Show inline validation errors when limits are exceeded, before the user even clicks Sign Up
3. Ensure any server-side length rejection is mapped to a user-facing error message

---

## BUG-010: Browser Autofill Causes Placeholder Text to Overlap With Field Content

**Severity:** Low  
**Priority:** Low  
**Type:** UI / Compatibility  
**Status:** Open  
**Evidence:** Screenshots captured during manual testing — placeholder text visible on top of autofilled email and browser-suggested password  
**Screenshot (email autofill):** https://prnt.sc/lYCpyB116r_U  
**Screenshot (password suggestion):** https://prnt.sc/NU9hLxFRrzZK

### Description

When the browser autofills the email field (from saved login credentials) or suggests a password (via the browser's built-in password manager), the AngularJS-controlled placeholder text does not clear. This results in the placeholder label visually overlapping with the autofilled content — two pieces of text occupy the same space simultaneously.

This affects two fields:
- **Email field**: Autofilled email + placeholder label overlap
- **Password field**: Browser-suggested password + placeholder label overlap

### Steps to Reproduce

**Scenario A — Email autofill:**
1. Save login credentials for `almashines.com` in the browser
2. Navigate to `https://www.almashines.com/dtc/account`
3. Observe the email field — the browser autofills the saved email

**Scenario B — Password suggestion:**
1. Navigate to the registration form
2. Click on the Password field — the browser suggests a saved or auto-generated password
3. Accept the browser suggestion

### Actual Result

In both cases: the browser fills the input value, but the AngularJS floating placeholder/label does not move or disappear. The placeholder text and the actual field content are shown on top of each other, making both unreadable.

### Expected Result

The placeholder or floating label should detect that the field has a value (including browser-injected values) and move or hide accordingly, exactly as it does when the user types manually.

### Impact

- Affects any returning user whose browser has saved credentials — a common real-world scenario
- Makes the filled value unreadable, which may cause users to clear and retype credentials they didn't need to
- A known and well-documented issue with AngularJS `ng-model` and browser autofill — it is fixable and commonly fixed in production apps

### Root Cause (Hypothesis)

Browser autofill injects values directly into the DOM without firing the JavaScript `input` or `change` events that AngularJS `ng-model` listens to. As a result, Angular's scope model does not update, the placeholder considers the field empty, and the floating label stays in the "empty" position.

### Recommended Fix

1. Listen for the `animationstart` event triggered by autofill CSS (a common cross-browser detection technique) and manually trigger an Angular digest cycle to sync the model
2. Alternatively, use a `MutationObserver` on the input to detect when the browser injects a value
3. Apply the CSS fix: use `:autofill` / `:-webkit-autofill` pseudo-class to force the label into the "filled" position whenever the browser autofill state is active

---

## BUG-011: Password Field Has No Strength Validation

**Severity:** Low  
**Priority:** Medium  
**Type:** Security / Validation  
**Status:** Open

### Description

The password field on the registration form accepts any string as a valid password — including single characters, dictionary words, and trivially guessable values like `abc` or `123`. There is no minimum length requirement and no complexity check for uppercase letters, lowercase letters, numbers, or special characters.

For a platform that stores personal academic and professional data, accepting weak passwords is a security gap and goes against standard industry practice.

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Enter a new email and proceed to the registration form
3. Enter a very weak password (e.g. `abc`) in the Password field
4. Click **Sign Up**

### Actual Result

The form accepts the weak password without any validation error and proceeds to send the OTP. The account is created with a trivially guessable password.

### Expected Result

The platform should enforce a minimum password policy, for example:
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (e.g. `@`, `#`, `!`)

An inline error message should be shown if the entered password does not meet the policy, before the user can submit.

### Impact

- Users can create accounts with extremely weak passwords, making them vulnerable to brute-force and credential-stuffing attacks
- No visual strength indicator means users have no guidance on what makes a good password

### Root Cause (Hypothesis)

The AngularJS form validation for the password field only checks that the field is non-empty (`ng-required`). No `ng-pattern` or custom validator enforcing complexity rules has been applied.

### Recommended Fix

1. Define a password policy and add an `ng-pattern` directive with a regex that enforces it
2. Show real-time inline feedback as the user types (e.g. a strength meter or a checklist of requirements)
3. Enforce the same policy server-side so it cannot be bypassed via direct API calls
