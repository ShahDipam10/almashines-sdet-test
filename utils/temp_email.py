"""
Guerrilla Mail helper for E2E tests.

How it works:
  1. Call get_temp_email() → get a disposable inbox + session token
  2. Use that email to sign up on AlmaShines
  3. Call wait_for_otp(sid_token) → polls the inbox until the OTP email arrives
  4. The OTP (4-8 digit code) is extracted and returned

API docs: https://www.guerrillamail.com/GuerrillaMailAPI.html
"""

import re
import time
import requests

_API = "https://api.guerrillamail.com/ajax.php"
_HEADERS = {"User-Agent": "AlmaShines-SDET-Test/1.0"}


def get_temp_email() -> tuple[str, str]:
    """
    Returns (email_address, sid_token).
    The sid_token is required for all subsequent calls to the same inbox.
    """
    resp = requests.get(_API, params={"f": "get_email_address"}, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["email_addr"], data["sid_token"]


def _fetch_email_body(mail_id: str, sid_token: str) -> str:
    resp = requests.get(
        _API,
        params={"f": "fetch_email", "email_id": mail_id, "sid_token": sid_token},
        headers=_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("mail_body", "")


def _extract_otp(text: str) -> str | None:
    """Finds the first 4-8 digit number in the email body — that is the OTP."""
    matches = re.findall(r"\b(\d{4,8})\b", text)
    return matches[0] if matches else None


def wait_for_otp(sid_token: str, timeout: int = 90, poll_interval: int = 5) -> str | None:
    """
    Polls the Guerrilla Mail inbox until an OTP email arrives or timeout is reached.
    Returns the OTP string, or None if no email came in time.
    """
    deadline = time.time() + timeout
    seq = 0

    while time.time() < deadline:
        try:
            resp = requests.get(
                _API,
                params={"f": "check_email", "seq": seq, "sid_token": sid_token},
                headers=_HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            emails = data.get("list", [])

            for mail in emails:
                body = _fetch_email_body(mail["mail_id"], sid_token)
                otp = _extract_otp(body)
                if otp:
                    return otp
                seq = max(seq, int(mail.get("mail_id", seq)))

        except requests.RequestException:
            pass  # network hiccup — keep polling

        time.sleep(poll_interval)

    return None
