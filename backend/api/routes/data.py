"""Data endpoints for OHLC candles."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional
from datetime import datetime

from core.models import Candle
from core.data_service import data_service

router = APIRouter()


@router.get("/candles/{interval}", response_model=List[Candle])
async def get_candles(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
    limit: Optional[int] = Query(None, description="Limit number of candles"),
    start_time: Optional[str] = Query(None, description="Start time ISO 8601"),
    end_time: Optional[str] = Query(None, description="End time ISO 8601"),
):
    """Get OHLC candles for specified interval."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    start = None
    end = None

    if start_time:
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format")

    if end_time:
        try:
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format")

    candles = data_service.get_candles(interval, limit, start, end)

    if not candles:
        raise HTTPException(status_code=404, detail="No candles found for this interval")

    return candles


@router.get("/status")
async def data_status():
    """Get data loading status."""
    return data_service.get_data_status()


@router.post("/reload")
async def reload_data():
    """Reload data from disk."""
    try:
        data_service.reload_data()
        return {
            "status": "success",
            "message": "Data reloaded",
            "data": data_service.get_data_status(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
