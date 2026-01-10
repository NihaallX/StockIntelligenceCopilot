"""Security middleware for the application"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import hashlib
import secrets

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse
    - Global rate limit per IP
    - Endpoint-specific limits
    - Sliding window algorithm
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()
        
        # Endpoint-specific limits (stricter for auth)
        self.endpoint_limits = {
            "/api/v1/auth/login": 5,  # 5 per minute
            "/api/v1/auth/register": 3,  # 3 per minute
            "/api/v1/auth/refresh": 10,  # 10 per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health", "/"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if self._is_blocked(client_ip):
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."}
            )
        
        # Clean up old records periodically
        self._cleanup_old_records()
        
        # Check rate limit
        endpoint = request.url.path
        limit = self.endpoint_limits.get(endpoint, self.requests_per_minute)
        
        if not self._check_rate_limit(client_ip, endpoint, limit):
            logger.warning(f"Rate limit exceeded: {client_ip} - {endpoint}")
            
            # Block IP temporarily if excessive requests
            if self._count_recent_requests(client_ip) > limit * 3:
                self._block_ip(client_ip)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Record request
        self._record_request(client_ip, endpoint)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit - self._count_recent_requests(client_ip))
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request, considering proxies"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str, endpoint: str, limit: int) -> bool:
        """Check if request is within rate limit"""
        key = f"{client_ip}:{endpoint}"
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Get recent requests
        recent = [ts for ts in self.request_history.get(key, []) if ts > cutoff]
        
        return len(recent) < limit
    
    def _record_request(self, client_ip: str, endpoint: str):
        """Record request timestamp"""
        key = f"{client_ip}:{endpoint}"
        self.request_history[key].append(datetime.utcnow())
    
    def _count_recent_requests(self, client_ip: str) -> int:
        """Count all recent requests from IP"""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        total = 0
        
        for key, timestamps in self.request_history.items():
            if key.startswith(client_ip):
                total += len([ts for ts in timestamps if ts > cutoff])
        
        return total
    
    def _is_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked"""
        if client_ip in self.blocked_ips:
            block_until = self.blocked_ips[client_ip]
            if datetime.utcnow() < block_until:
                return True
            else:
                del self.blocked_ips[client_ip]
        return False
    
    def _block_ip(self, client_ip: str):
        """Temporarily block an IP"""
        block_duration = timedelta(minutes=15)
        self.blocked_ips[client_ip] = datetime.utcnow() + block_duration
        logger.warning(f"IP blocked for 15 minutes: {client_ip}")
    
    def _cleanup_old_records(self):
        """Periodically clean up old request records"""
        now = datetime.utcnow()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff = now - timedelta(minutes=5)
        
        # Clean request history
        for key in list(self.request_history.keys()):
            self.request_history[key] = [
                ts for ts in self.request_history[key] if ts > cutoff
            ]
            if not self.request_history[key]:
                del self.request_history[key]
        
        # Clean expired blocks
        for ip in list(self.blocked_ips.keys()):
            if self.blocked_ips[ip] < now:
                del self.blocked_ips[ip]
        
        self.last_cleanup = now


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    - Prevent XSS
    - Prevent clickjacking
    - Enforce HTTPS
    - Content type sniffing
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://*.vercel.app"
        )
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection for state-changing operations
    - Generate CSRF tokens
    - Validate tokens on POST/PUT/DELETE/PATCH
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.csrf_tokens: Dict[str, datetime] = {}
        self.token_lifetime = timedelta(hours=1)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection"""
        
        # Skip for read-only methods and auth endpoints
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            # Add CSRF token to response for future requests
            csrf_token = self._generate_csrf_token()
            response.headers["X-CSRF-Token"] = csrf_token
            return response
        
        # Skip CSRF for public endpoints (login, register)
        if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            return await call_next(request)
        
        # Validate CSRF token for state-changing requests
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token or not self._validate_csrf_token(csrf_token):
            logger.warning(f"CSRF validation failed: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF validation failed"}
            )
        
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = datetime.utcnow() + self.token_lifetime
        self._cleanup_expired_tokens()
        return token
    
    def _validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token"""
        if token not in self.csrf_tokens:
            return False
        
        expiry = self.csrf_tokens[token]
        if datetime.utcnow() > expiry:
            del self.csrf_tokens[token]
            return False
        
        return True
    
    def _cleanup_expired_tokens(self):
        """Remove expired tokens"""
        now = datetime.utcnow()
        expired = [token for token, expiry in self.csrf_tokens.items() if now > expiry]
        for token in expired:
            del self.csrf_tokens[token]


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Sanitize and validate input data
    - Prevent SQL injection
    - Prevent XSS
    - Validate content length
    """
    
    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
    
    async def dispatch(self, request: Request, call_next):
        """Process request with input sanitization"""
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body too large"}
            )
        
        # Check for suspicious patterns in URL
        if self._contains_suspicious_patterns(request.url.path):
            logger.warning(f"Suspicious pattern in URL: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"}
            )
        
        return await call_next(request)
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check for common attack patterns"""
        suspicious = [
            "<script",
            "javascript:",
            "onerror=",
            "onload=",
            "../",
            "..\\",
            "union select",
            "drop table",
            "'; drop",
            "1=1",
            "admin'--",
            "' or '1'='1"
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in suspicious)


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data for logging/storage
    Uses SHA-256 for one-way hashing
    """
    return hashlib.sha256(data.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)
