from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Setup the password context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Handles bcrypt's 72-byte limit gracefully.
    """
    if not plain_password or not hashed_password:
        return False

    # Bcrypt has a strict limit of 72 bytes. 
    # If the input is longer, it causes a server crash (ValueError).
    # We check length first to prevent the crash.
    if len(plain_password.encode('utf-8')) > 72:
        logger.warning("Password too long for bcrypt (max 72 bytes). Verification failed.")
        return False
        
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Log the specific error but don't crash the server
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    if not password:
        raise ValueError("Password cannot be empty")
        
    # Check length before hashing to prevent crash
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password is too long (must be under 72 bytes)")
        
    return pwd_context.hash(password)