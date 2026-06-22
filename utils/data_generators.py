import uuid


BASE_ALIAS = "dipampshah"
GMAIL_DOMAIN = "gmail.com"


def generate_test_email() -> str:
    """
    Returns a unique Gmail alias that lands in dipampshah@gmail.com inbox.
    Each call produces a different address so tests stay independent.
    """
    short_id = uuid.uuid4().hex[:8]
    return f"{BASE_ALIAS}+auto{short_id}@{GMAIL_DOMAIN}"
