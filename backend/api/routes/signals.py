"""Trading signal endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional

from core.models import Signal, SignalState
from core.data_service import data_service
from core.indicators import indicator_calculator
from core.signal_engine import signal_engine
from core.risk_management import risk_manager

router = APIRouter()


@router.get("/generate/{interval}", response_model=Signal)
async def generate_signal(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
    lookback: int = Query(100, ge=1, le=5000, description="Number of historical candles to analyze"),
):
    """Generate a trading signal for the specified interval."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    candles = data_service.get_candles(interval, limit=lookback)

    if not candles:
        raise HTTPException(status_code=404, detail="No candles available for this interval")

    try:
        # Calculate indicators
        indicators = indicator_calculator.calculate_all(candles)
        if not indicators:
            raise HTTPException(status_code=500, detail="Failed to calculate indicators")

        # Generate signal
        signal = signal_engine.generate_signal(candles, indicators, interval)
        if not signal:
            raise HTTPException(status_code=500, detail="Failed to generate signal")

        return signal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signal-history/{interval}")
async def get_signal_history(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
    limit: int = Query(10, ge=1, le=100, description="Number of signals to return"),
):
    """Get recent signal history for an interval."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    candles = data_service.get_candles(interval)

    if not candles:
        raise HTTPException(status_code=404, detail="No candles available")

    try:
        signals = []
        # Generate signals for recent periods
        step = max(1, len(candles) // limit)

        for i in range(0, min(limit * step, len(candles)), step):
            candle_subset = candles[:i+1] if i > 0 else candles[:1]
            if len(candle_subset) > 1:
                # Early subsets may not contain enough candles for every
                # indicator. Skip those snapshots rather than failing the
                # whole history request.
                try:
                    indicators = indicator_calculator.calculate_all(candle_subset)
                    if indicators:
                        signal = signal_engine.generate_signal(candle_subset, indicators, interval)
                        if signal:
                            signals.append(signal)
                except (TypeError, ValueError, IndexError):
                    continue

        return {
            "interval": interval,
            "signal_count": len(signals),
            "signals": signals[-limit:] if signals else [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess-risk/{interval}")
async def assess_risk(
    interval: str = Path(..., description="Candle interval"),
    account_size: float = Query(10000.0, gt=0, description="Account size in USD"),
):
    """Assess risk for current signal."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    # Use enough history for the long EMA when the source provides it;
    # the indicator engine still degrades gracefully for shorter series.
    candles = data_service.get_candles(interval, limit=300)

    if not candles:
        raise HTTPException(status_code=404, detail="No candles available")

    try:
        indicators = indicator_calculator.calculate_all(candles)
        signal = signal_engine.generate_signal(candles, indicators, interval)

        if not signal:
            raise HTTPException(status_code=500, detail="Failed to generate signal")

        risk = risk_manager.assess_risk(signal, candles[-1].close, account_size)

        return {
            "signal": signal,
            "risk_assessment": risk,
            "can_trade": risk_manager.can_open_position(signal),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
