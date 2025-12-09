# app/auth/hashing.py
from passlib.context import CryptContext

# Create password context with bcrypt as primary, sha256_crypt as fallback
pwd_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback: try sha256_crypt directly if bcrypt fails
        if pwd_context._default_scheme() == "bcrypt":
            try:
                from passlib.hash import sha256_crypt
                return sha256_crypt.verify(plain_password, hashed_password)
            except:
                return False
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Fallback to sha256_crypt if bcrypt fails
        from passlib.hash import sha256_crypt
        return sha256_crypt.hash(password)