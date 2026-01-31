import re
from urllib.parse import urlparse

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)
PHONE_RE = re.compile(
    r"(?:\+?\d[\d\s\-()]{7,}\d|8[\d\s\-()]{9,}\d)"
)

DEFAULT_TIMEOUT = 15
DEFAULT_MAX_PAGES = 100
DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; ContactParser/1.0)"


def get_domain(netloc: str) -> str:
    parts = netloc.lower().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:]) if len(parts) == 2 else ".".join(parts[-3:])
    return netloc


def same_domain(url: str, base_netloc: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return True
    return get_domain(parsed.netloc) == get_domain(base_netloc)


PHONE_DIGITS = 11
PHONE_PREFIX = ("7", "8")
PHONE_SECOND_DIGIT = ("3", "4", "5", "8", "9")


def is_valid_phone(digits: str) -> bool:
    if len(digits) != PHONE_DIGITS:
        return False
    if digits[0] not in PHONE_PREFIX:
        return False
    if digits[1] not in PHONE_SECOND_DIGIT:
        return False
    if len(set(digits)) == 1:
        return False
    return True


def to_canonical_digits(digits: str) -> str:
    if digits[0] == "8":
        return "7" + digits[1:]
    return digits


def format_phone(digits: str) -> str:
    d = to_canonical_digits(digits)
    return f"+7 ({d[1:4]}) {d[4:7]}-{d[7:9]}-{d[9:11]}"


def normalize_phone(s: str) -> str:
    raw = s.strip()
    digits = re.sub(r"\D", "", raw)
    if is_valid_phone(digits):
        return format_phone(digits)
    return ""


def extract_phones(text: str) -> set:
    found = set()
    for m in PHONE_RE.findall(text):
        raw = m.strip()
        digits = re.sub(r"\D", "", raw)
        if not is_valid_phone(digits):
            continue
        found.add(format_phone(digits))
    return found


def extract_emails(text: str) -> set:
    return set(EMAIL_RE.findall(text))