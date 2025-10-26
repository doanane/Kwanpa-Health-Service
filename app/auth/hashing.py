from passlib.context import CryptContext
import hashlib
import secrets

# Try bcrypt first, fallback to sha256_crypt if bcrypt has issues
try:
    pwd_context = CryptContext(
        schemes=["bcrypt", "sha256_crypt"],
        deprecated="auto",
        bcrypt__rounds=12
    )
    # Test bcrypt to ensure it works
    pwd_context.hash("test")
    BC_WORKING = True
except Exception:
    # Fallback to sha256_crypt if bcrypt fails
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    BC_WORKING = False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback verification if there's an issue
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Ultimate fallback - use a simple hash (not recommended for production)
        salt = secrets.token_hex(16)
        return f"sha256${salt}${hashlib.sha256((password + salt).encode()).hexdigest()}"
    
