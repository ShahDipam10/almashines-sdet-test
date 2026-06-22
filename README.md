# AlmaShines — Sign Up Flow Automation Suite

Automated test suite for the Sign Up flow at [almashines.com/dtc/account](https://www.almashines.com/dtc/account).

**Stack:** Python · Playwright · pytest · pytest-html

---

## Project Structure

```
├── pages/                  Page Object Model — one class per step
│   ├── base_page.py        URL constant + shared helpers
│   ├── signup_page.py      Email entry (step 1)
│   ├── login_form_page.py  Login form shown for existing emails
│   ├── registration_page.py  Name + password form (new users)
│   └── otp_page.py         OTP verification step
│
├── tests/
│   ├── test_01_page_load.py       Smoke — page loads correctly
│   ├── test_02_email_step.py      Email validation (empty, invalid formats)
│   ├── test_03_existing_user.py   Existing email → login redirect
│   ├── test_04_registration.py    Registration form validations
│   ├── test_05_otp_step.py        OTP step UI + wrong OTP error
│   └── test_06_e2e_signup.py      Full end-to-end flow (Guerrilla Mail)
│
├── utils/
│   ├── data_generators.py  Generates unique Gmail alias emails per test
│   └── temp_email.py       Guerrilla Mail API wrapper for real OTP reading
│
├── docs/
│   ├── manual_test_cases.md   Task 2 — test cases not automated
│   └── bug_reports.md         Task 3 — bug reports
│
├── reports/                   Auto-generated HTML report + screenshots
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

> **Note:** `EXISTING_EMAIL` must point to an account that has already completed sign-up on `https://www.almashines.com/dtc/account`. By default it is `dipamshahaliantesting1@gmail.com`.

---

## Running Tests

### All smoke tests (fastest, ~30 s)

```bash
pytest -m smoke
```

### Full regression suite (no real email inbox needed, ~3 min)

```bash
pytest -m "smoke or regression"
```

### End-to-end test with real OTP (requires internet, ~2 min)

```bash
pytest tests/test_06_e2e_signup.py -v
```

### Everything

```bash
pytest
```

### Headless mode (e.g. for CI)

```bash
HEADED=false SLOW_MO=0 pytest -m "smoke or regression"
```

---

## Test Report

After each run, an HTML report is generated at:

```
reports/report.html
```

Open it in any browser. Failed tests also save a screenshot to `reports/screenshots/`.

---

## Test Markers

| Marker       | What it covers                                              |
|--------------|-------------------------------------------------------------|
| `smoke`      | 8 tests — page loads, key elements present                  |
| `regression` | 30+ tests — all form validations, paths, error messages     |
| `e2e`        | 1 test — full signup with real OTP via Guerrilla Mail       |

---

## How the E2E OTP Test Works

1. Calls [Guerrilla Mail API](https://www.guerrillamail.com) to get a free disposable email address (e.g. `abc123@sharklasers.com`)
2. Registers with that address on AlmaShines
3. Polls the Guerrilla Mail inbox every 5 seconds (up to 90 s) for the OTP email
4. Extracts the 6-digit OTP from the email body using regex
5. Enters the OTP on the page and asserts success

No Gmail credentials or OAuth setup required.

---

## Known Limitations

- **Role selection step** (post-OTP) is loaded dynamically and is not yet automated — see `docs/manual_test_cases.md` for manual coverage.
- The E2E test depends on AlmaShines not blocking Guerrilla Mail domains. If it fails with "OTP not received", the platform may be filtering that domain — re-run or contact support.
- Tests run against the live platform. Parallel test runs using the same email prefix may conflict.
