"""Simple local multi-user authentication for the Streamlit demo.

Passwords are stored as salted PBKDF2-HMAC hashes in users.json, not plaintext.
For a production deployment, use an external identity provider/database.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path
from typing import Dict

USERS_FILE = Path(__file__).with_name("users.json")
ITERATIONS = 210_000


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        ).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def load_users() -> Dict[str, Dict[str, str]]:
    if not USERS_FILE.exists():
        return {}
    with USERS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def authenticate(username: str, password: str) -> bool:
    username = username.strip()
    users = load_users()
    user = users.get(username)
    return bool(user and verify_password(password, user.get("password_hash", "")))
