"""Password hashing utilities with enhanced security"""

from passlib.context import CryptContext
import hashlib
import secrets

# bcrypt context with cost factor 14 (higher = more secure, slower)
# Using bcrypt which automatically handles salting
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=14,  # Increased from 12 for better security
    bcrypt__ident="2b"   # Use 2b variant (more secure)
)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with automatic salting
    
    bcrypt automatically:
    - Generates a random salt for each password
    - Incorporates the salt into the hash
    - Uses multiple rounds of hashing (cost factor 14 = 2^14 iterations)
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password with embedded salt
    """
    # Pre-hash with SHA-256 to handle long passwords
    # (bcrypt has 72-byte limit)
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # Hash with bcrypt (includes automatic salting)
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Extracts salt from stored hash and verifies password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Pre-hash the input password same way as during hashing
        prehashed = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        
        # Verify with bcrypt (automatically extracts salt from hash)
        return pwd_context.verify(prehashed, hashed_password)
    except Exception:
        # If verification fails for any reason, return False
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    
    Args:
        length: Token length in bytes
    
    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)

