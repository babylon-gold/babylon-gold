"""Authentication and authorization for Babylon AI Gold Intelligence."""
import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

# Get admin API key from environment
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

if not ADMIN_API_KEY:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ ADMIN_API_KEY environment variable not set. Admin endpoints will be disabled.")


async def verify_admin_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Verify admin bearer token for protected endpoints.

    Usage in route:
    ```
    @router.post("/admin/endpoint")
    async def protected_endpoint(admin_token: str = Depends(verify_admin_token)):
        # admin_token is verified
    ```
    """
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API key not configured. Contact administrator.",
        )

    if credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing admin credentials",
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
