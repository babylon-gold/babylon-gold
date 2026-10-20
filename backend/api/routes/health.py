"""Health check endpoint."""
from fastapi import APIRouter
from core.models import HealthCheck
from core.data_service import data_service

router = APIRouter()


@router.get("", response_model=HealthCheck)
async def health_check():
    """Check backend health and data status."""
    status = data_service.get_data_status()

    return HealthCheck(
        status="healthy" if status["is_loaded"] else "degraded",
        backend_version="0.1.0",
        data_loaded=status["is_loaded"],
        last_data_update=status["last_update"],
    )
