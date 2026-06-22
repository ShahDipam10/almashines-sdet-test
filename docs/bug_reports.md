# Bug Reports — AlmaShines Sign Up / Login Flow

**Reporter:** SDET Candidate  
**Date:** 2026-06-23  
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

## BUG-002: Rate Limiting During Registration Produces No User-Facing Feedback

**Severity:** Medium  
**Priority:** Medium  
**Type:** UX / Error Handling  
**Status:** Open  
**Automated test:** `conftest.py::otp_page` fixture (skips with diagnostic message when triggered)

### Description

When multiple registrations are submitted in quick succession from the same IP address, the platform silently blocks further registrations. Instead of showing a clear, user-facing message explaining the restriction, it either:
- Shows a generic SweetAlert dialog with no description, or
- Allows the registration form to submit but never navigates to the OTP step (the user is left on a blank state with no indication of what went wrong)

### Steps to Reproduce

1. Navigate to `https://www.almashines.com/dtc/account`
2. Submit a new email and complete the registration form → observe OTP step
3. Immediately repeat steps 1–2 three to five times in rapid succession (within ~60 seconds)

### Actual Result

On the fourth or fifth attempt, one of the following occurs:
- A SweetAlert dialog appears with a title and/or body message that provides insufficient context (e.g., no mention of rate limiting, no guidance on how long to wait)
- The registration form submits successfully (no error shown) but the OTP step never appears, leaving the user on a blank screen

### Expected Result

The platform should display a clear, informative message such as:
> *"Too many registration attempts. Please wait a few minutes before trying again."*

The user should also be informed how long the block lasts, if possible.

### Impact

- Legitimate users who accidentally submit the form multiple times (double-click, network retry) will be silently blocked with no recovery path shown
- QA teams running automated test suites hit this limit and receive no actionable diagnostic — making test failures ambiguous between a product bug and a rate-limit side effect

### Root Cause (Hypothesis)

The server-side rate limit is enforced but the corresponding HTTP error response is either not mapped to a user-friendly UI message, or the AngularJS error handler swallows the response body without rendering it.

### Recommended Fix

1. Map the rate-limit HTTP response (likely 429 Too Many Requests) to a dedicated SweetAlert or inline error with a clear message and a countdown timer
2. Include a `Retry-After` header in the API response and display the wait time to the user

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
