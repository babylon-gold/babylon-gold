"""Authentication and authorization for Babylon AI Gold Intelligence."""
import os
import hmac
import hashlib
import logging
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
logger = logging.getLogger(__name__)


def _get_admin_api_key() -> str:
    """Get admin API key from environment (dynamic, testable)."""
    key = os.getenv("ADMIN_API_KEY")
    if not key:
        logger.warning("ADMIN_API_KEY environment variable not set. Admin endpoints require valid token.")
    return key


def _constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(a.encode(), b.encode())


async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify admin bearer token for protected endpoints.
    Fails closed if ADMIN_API_KEY is not configured.

    Usage in route:
    ```
    @router.post("/admin/endpoint")
    async def protected_endpoint(admin_token: str = Depends(verify_admin_token)):
        # admin_token is verified
    ```
    """
    admin_api_key = _get_admin_api_key()

    if not admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authentication not configured",
        )

    # Use constant-time comparison to prevent timing attacks
    if not _constant_time_compare(credentials.credentials, admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    return credentials.credentials


def require_admin_auth(func):
    """
    Decorator for admin-only endpoints.
    Requires Authorization: Bearer <ADMIN_API_KEY> header.
    """
    async def wrapper(*args, **kwargs):
        admin_token = await verify_admin_token()
        return await func(*args, **kwargs)
    return wrapper
