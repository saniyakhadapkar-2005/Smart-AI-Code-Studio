"""Add local users to users.json.
Usage: python manage_users.py
"""
from getpass import getpass
import json
from auth import USERS_FILE, hash_password, load_users

username = input("Username: ").strip()
display_name = input("Display name: ").strip() or username
password = getpass("Password: ")
if not username or not password:
    raise SystemExit("Username and password are required.")
users = load_users()
users[username] = {"display_name": display_name, "password_hash": hash_password(password)}
with USERS_FILE.open("w", encoding="utf-8") as f:
    json.dump(users, f, indent=2)
print(f"User '{username}' saved to {USERS_FILE.name}.")
