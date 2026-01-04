from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Handles bcrypt's 72-byte limit gracefully by truncating.
    """
    if not plain_password or not hashed_password:
        return False

    
    password_bytes = plain_password.encode('utf-8')
    
    
    if len(password_bytes) > 71:
        plain_password = password_bytes[:71].decode('utf-8', errors='ignore')
        
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password with length safety"""
    if not password:
        raise ValueError("Password cannot be empty")
        
    password_bytes = password.encode('utf-8')
    
    
    if len(password_bytes) > 71:
        password = password_bytes[:71].decode('utf-8', errors='ignore')
        
    return pwd_context.hash(password)