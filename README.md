# AlmaShines — Sign Up Flow Test Suite

This is my submission for the AlmaShines SDET take-home assignment. I built an end-to-end automated test suite for the Sign Up flow at [almashines.com/dtc/account](https://www.almashines.com/dtc/account) using Python, Playwright, and pytest.

**— Dipam Shah**

**Stack:** Python · Playwright · pytest · pytest-html

---

## What I Tested

The suite covers the full Sign Up journey across 7 test modules:

| Step | File | Tests |
|------|------|-------|
| Page load & structure | `test_01_page_load.py` | 5 smoke |
| Email input validation | `test_02_email_step.py` | 8 regression |
| Existing user → login form | `test_03_existing_user.py` | 8 regression |
| Registration form | `test_04_registration.py` | 13 regression |
| OTP verification | `test_05_otp_step.py` | 12 regression |
| Full E2E signup with real OTP | `test_06_e2e_signup.py` | 1 e2e |
| Role selection (post-OTP) | `test_07_role_selection.py` | 8 e2e |

**Total: 55 tests**

---

## Project Structure

```
├── pages/                     Page Object Model — one class per step
│   ├── base_page.py           URL constant + shared helpers
│   ├── signup_page.py         Email entry (step 1)
│   ├── login_form_page.py     Login form shown for existing emails
│   ├── registration_page.py   Name + password form (new users)
│   ├── otp_page.py            OTP verification step
│   └── role_page.py           Role selection page (post-OTP)
│
├── tests/
│   ├── test_01_page_load.py        Smoke — page loads correctly
│   ├── test_02_email_step.py       Email validation (empty, invalid formats)
│   ├── test_03_existing_user.py    Existing email → login redirect
│   ├── test_04_registration.py     Registration form validations
│   ├── test_05_otp_step.py         OTP step UI + wrong OTP error handling
│   ├── test_06_e2e_signup.py       Full signup with real OTP via Guerrilla Mail
│   └── test_07_role_selection.py   Role selection page (dynamic fields, validation)
│
├── utils/
│   ├── data_generators.py    Generates unique Gmail alias emails per test
│   └── temp_email.py         Guerrilla Mail API wrapper for real OTP reading
│
├── docs/
│   ├── manual_test_cases.md   Task 2 — test cases not automated (with rationale)
│   └── bug_reports.md         Task 3 — 3 bug reports found during testing
│
├── reports/                   Auto-generated HTML report + failure screenshots
├── conftest.py                Shared pytest fixtures
├── pytest.ini                 Test config + markers
└── requirements.txt
```

---

## Setup

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
# Email already registered on the platform (used for existing-user tests)
EXISTING_EMAIL=dipamshahaliantesting1@gmail.com

# Show the browser window while tests run (useful for watching/debugging)
HEADED=true

# Slow down each Playwright action by N ms (0 = no slow-mo)
SLOW_MO=300
```

> **Note:** `EXISTING_EMAIL` must point to an account that has already completed sign-up on `https://www.almashines.com/dtc/account`.

---

## Running Tests

### Smoke tests only (fastest, ~30 s)

```bash
pytest -m smoke
```

### Full regression suite (no real email inbox needed, ~3 min)

```bash
pytest -m "smoke or regression"
```

### E2E tests with real OTP (requires internet, ~2–3 min per test)

```bash
pytest -m e2e -v
```

### Everything

```bash
pytest
```

### Headless / CI mode

```bash
HEADED=false SLOW_MO=0 pytest -m "smoke or regression"
```

---

## Test Report

After each run an HTML report is generated at:

```
reports/report.html
```

Open it in any browser. Failed tests also save a screenshot to `reports/screenshots/`.

---

## Test Markers

| Marker       | Count | What it covers |
|--------------|-------|----------------|
| `smoke`      | 5     | Page loads, key elements present |
| `regression` | 41    | All form validations, paths, error messages |
| `e2e`        | 9     | Full signup with real OTP (Guerrilla Mail) + role selection |

---

## How the E2E OTP Tests Work

1. Call the [Guerrilla Mail API](https://www.guerrillamail.com) to get a free disposable inbox (e.g. `abc123@sharklasers.com`)
2. Register on AlmaShines with that address
3. Poll the inbox every 5 seconds (up to 90 s) for the OTP email
4. Extract the 6-digit code with regex and enter it on the page
5. After OTP verification, proceed to the role selection page and run role-specific assertions

No Gmail credentials or OAuth setup required.

---

## Bugs Found

I documented 3 bugs in [`docs/bug_reports.md`](docs/bug_reports.md):

- **BUG-001 (High):** Email without TLD (`user@domain`) is accepted — backed by an intentionally failing automated test in `test_02_email_step.py`
- **BUG-002 (Medium):** Rate limiting during rapid registrations shows no user-facing feedback
- **BUG-003 (Security):** Sequential numeric signup IDs in the URL enable account enumeration

---

## Manual Test Cases

Cases I chose not to automate (social OAuth, OTP expiry, mobile layout, cross-browser, etc.) are documented with rationale in [`docs/manual_test_cases.md`](docs/manual_test_cases.md).
