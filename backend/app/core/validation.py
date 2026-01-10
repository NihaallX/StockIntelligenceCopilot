"""Enhanced input validation and sanitization"""

import re
import html
from typing import Any
from fastapi import HTTPException, status


class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Common attack patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(;.*-{2})",
        r"('.*or.*'.*=.*')",
        r"(1.*=.*1)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        - Remove HTML tags
        - Escape special characters
        - Limit length
        """
        if not value:
            return value
        
        # Check length
        if len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long (max {max_length} characters)"
            )
        
        # Check for XSS patterns
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_no_sql_injection(value: str) -> str:
        """Check for SQL injection patterns"""
        if not value:
            return value
        
        value_lower = value.lower()
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        # More strict email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Prevent email header injection
        if '\n' in email or '\r' in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        return email.lower().strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength
        - Minimum 8 characters
        - At least 1 uppercase
        - At least 1 lowercase
        - At least 1 digit
        - At least 1 special character
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if len(password) > 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long (max 128 characters)"
            )
        
        checks = {
            'uppercase': r'[A-Z]',
            'lowercase': r'[a-z]',
            'digit': r'[0-9]',
            'special': r'[!@#$%^&*(),.?":{}|<>]'
        }
        
        missing = []
        for check_name, pattern in checks.items():
            if not re.search(pattern, password):
                missing.append(check_name)
        
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must contain: {', '.join(missing)}"
            )
        
        # Check for common passwords
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome'
        ]
        
        if password.lower() in common_passwords:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too common. Please choose a stronger password."
            )
        
        return True
    
    @staticmethod
    def sanitize_ticker(ticker: str) -> str:
        """Sanitize stock ticker symbol"""
        # Allow only alphanumeric and basic symbols
        if not re.match(r'^[A-Z0-9\.\-]{1,10}$', ticker.upper()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticker symbol"
            )
        
        return ticker.upper().strip()
    
    @staticmethod
    def sanitize_dict(data: dict, max_depth: int = 5, current_depth: int = 0) -> dict:
        """
        Recursively sanitize dictionary values
        Prevents deeply nested objects (DoS attack)
        """
        if current_depth > max_depth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input structure too complex"
            )
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = InputValidator.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = InputValidator.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = InputValidator.sanitize_dict(
                    value, max_depth, current_depth + 1
                )
            elif isinstance(value, (list, tuple)):
                if len(value) > 1000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Array too large"
                    )
                sanitized[clean_key] = value
            else:
                sanitized[clean_key] = value
        
        return sanitized
