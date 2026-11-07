"""Check local demo login credentials from this project folder."""
from auth import authenticate, USERS_FILE
print(f"Users file: {USERS_FILE}")
print("saniya / saniya234:", "OK" if authenticate("saniya", "saniya234") else "FAILED")
print("admin / admin123:", "OK" if authenticate("admin", "admin123") else "FAILED")
