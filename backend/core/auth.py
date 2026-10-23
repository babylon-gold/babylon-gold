"""Authentication and authorization for Babylon AI Gold Intelligence."""
import os
import hmac
import hashlib
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

# Get admin API key from environment
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

if not ADMIN_API_KEY:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("ADMIN_API_KEY environment variable not set. Admin endpoints require valid token.")


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
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authentication not configured",
        )

    # Use constant-time comparison to prevent timing attacks
    if not _constant_time_compare(credentials.credentials, ADMIN_API_KEY):
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
