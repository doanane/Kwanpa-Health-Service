import hashlib
import secrets
from typing import Tuple

def hash_password(password: str) -> Tuple[str, str]:
    """Hash a password with a random salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode())
    hashed = hash_obj.hexdigest()
    return f"{salt}${hashed}", salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash and salt"""
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode())
    return hash_obj.hexdigest() == hashed_password.split('$')[1]