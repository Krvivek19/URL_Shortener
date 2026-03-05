# ----- app/utils.py -----
# Utility functions: Base62 encoding + URL validation helpers.

import string
import random

# ── Base62 Character Set ─────────────────────────────────
# 62 characters: 0-9, a-z, A-Z
# Used to convert numeric IDs into short, URL-safe strings.
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_CHARS)  # = 62


def encode_base62(num: int) -> str:
    """
    Convert a positive integer to a Base62 string.

    How it works:
    - Imagine converting decimal to hex, but with 62 chars instead of 16.
    - 0  → "0"
    - 61 → "Z"
    - 62 → "10"
    - Example: 123456 → "W7e"

    This is used to turn the auto-increment DB id into a short code.
    """
    if num == 0:
        return BASE62_CHARS[0]

    result = []
    while num > 0:
        remainder = num % BASE
        result.append(BASE62_CHARS[remainder])
        num //= BASE

    return "".join(reversed(result))


def decode_base62(short_code: str) -> int:
    """
    Convert a Base62 string back to an integer.

    Reverse of encode_base62.
    Example: "W7e" → 123456
    """
    num = 0
    for char in short_code:
        num = num * BASE + BASE62_CHARS.index(char)
    return num


def generate_random_code(length: int = 6) -> str:
    """
    Generate a random short code of given length.

    Used as fallback if Base62 encoding is not desired,
    or for collision retry.

    Example: "aB3xZ1"
    """
    return "".join(random.choices(BASE62_CHARS, k=length))
