"""Administrative endpoints for data management and scheduler control."""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from core.data_refresh import refresh_pipeline
from core.scheduler import (
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
    scheduler,
)
from core.auth import verify_admin_token

router = APIRouter()


@router.post("/data/refresh")
async def trigger_data_refresh(admin_token: str = Depends(verify_admin_token)):
    """
    Manually trigger the data refresh pipeline.

    This runs the full pipeline:
    1. Check for fresh data
    2. Generate indicators
    3. Create signals
    4. Evaluate signals
    5. Reload backend
    """
    return {
        "message": "Data refresh started",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": refresh_pipeline.run_full_pipeline(),
    }


@router.get("/data/refresh-status")
async def get_refresh_status(admin_token: str = Depends(verify_admin_token)):
    """Get the status of the last data refresh."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": refresh_pipeline.get_status(),
    }


@router.post("/scheduler/start")
async def start_scheduler_endpoint(admin_token: str = Depends(verify_admin_token)):
    """Start the background scheduler for periodic data refresh."""
    if scheduler.running:
        raise HTTPException(
            status_code=400,
            detail="Scheduler is already running",
        )

    start_scheduler()
    return {
        "message": "Scheduler started",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ],
    }


@router.post("/scheduler/stop")
async def stop_scheduler_endpoint(admin_token: str = Depends(verify_admin_token)):
    """Stop the background scheduler."""
    if not scheduler.running:
        raise HTTPException(
            status_code=400,
            detail="Scheduler is not running",
        )

    stop_scheduler()
    return {
        "message": "Scheduler stopped",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/scheduler/status")
async def scheduler_status(admin_token: str = Depends(verify_admin_token)):
    """Get the current scheduler status and next run times."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scheduler": get_scheduler_status(),
    }


@router.get("/system/health-detailed")
async def detailed_health(admin_token: str = Depends(verify_admin_token)):
    """Get detailed system health information."""
    from core.data_service import data_service

    data_status = data_service.get_data_status()
    refresh_status = refresh_pipeline.get_status()
    scheduler_info = get_scheduler_status()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "is_loaded": data_status["is_loaded"],
            "data_type": data_status["data_type"],
            "intervals": data_status["intervals"],
            "candle_counts": data_status["candle_counts"],
            "data_age_hours": data_status["data_age_hours"],
        },
        "refresh": {
            "status": refresh_status["status"],
            "last_refresh": refresh_status.get("last_refresh"),
            "duration_seconds": refresh_status.get("duration_seconds"),
        },
        "scheduler": {
            "running": scheduler_info["running"],
            "next_runs": [
                {
                    "job": job["name"],
                    "next_run": job["next_run_time"],
                }
                for job in scheduler_info["jobs"]
            ],
        },
    }
