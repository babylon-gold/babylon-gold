"""Routes for historical data, signals, and performance evaluation."""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
from datetime import datetime, timezone

from core.data_service import data_service
from core.models import CandleWithIndicators, SignalRecord, EvaluatedSignal

router = APIRouter()


@router.get("/candles-with-indicators/{interval}", response_model=List[CandleWithIndicators])
async def get_candles_with_indicators(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
    limit: int = Query(100, ge=1, le=5000, description="Max candles to return"),
):
    """Get historical candles with technical indicators."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    candles = data_service.get_enriched_candles(interval, limit=limit)
    if not candles:
        raise HTTPException(status_code=404, detail="No enriched candles available")

    return candles


@router.get("/latest-analysis/{interval}")
async def get_latest_analysis(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
):
    """Get latest analysis summary with indicators and data age."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    enriched = data_service.get_latest_enriched(interval)
    if not enriched:
        raise HTTPException(status_code=404, detail="No data available")

    # Calculate data age
    age_hours = data_service._get_data_age_hours()
    is_recent = age_hours is not None and age_hours < 24

    return {
        "interval": interval,
        "timestamp_utc": enriched.timestamp_utc.isoformat(),
        "close_price": enriched.close,
        "indicators": {
            "ema20": enriched.ema20,
            "ema50": enriched.ema50,
            "ema200": enriched.ema200,
            "rsi14": enriched.rsi14,
            "atr14": enriched.atr14,
            "adx14": enriched.adx14,
        },
        "data_type": "تاريخية - Historical",
        "data_age_hours": age_hours,
        "is_recent": is_recent,
        "last_update_utc": data_service.get_last_update_time().isoformat() if data_service.get_last_update_time() else None,
    }


@router.get("/signals-history", response_model=dict)
async def get_signals_history(
    limit: int = Query(50, ge=1, le=500, description="Max signals to return"),
):
    """Get historical trading signals with states and outcomes."""
    signals = data_service.get_signals_history(limit=limit)
    if not signals:
        raise HTTPException(status_code=404, detail="No signals available")

    return {
        "total_signals": len(data_service.signals_history),
        "returned": len(signals),
        "signals": signals,
        "note": "بيانات تاريخية - Historical data only - No live signals",
    }


@router.get("/performance-stats", response_model=dict)
async def get_performance_stats():
    """Get overall performance statistics from evaluated signals."""
    evaluated = data_service.evaluated_signals
    if not evaluated:
        raise HTTPException(status_code=404, detail="No evaluated signals available")

    # Calculate stats
    total = len(evaluated)
    wins = len([s for s in evaluated if s.result == "WIN"])
    losses = len([s for s in evaluated if s.result == "LOSS"])
    win_rate = (wins / total * 100) if total > 0 else 0

    # Calculate expectancy
    total_net_r = sum(s.net_r for s in evaluated if s.net_r)
    expectancy = total_net_r / total if total > 0 else 0

    # Group by strategy
    by_strategy = {}
    for sig in evaluated:
        if sig.strategy not in by_strategy:
            by_strategy[sig.strategy] = []
        by_strategy[sig.strategy].append(sig)

    strategy_stats = {}
    for strat, sigs in by_strategy.items():
        strat_wins = len([s for s in sigs if s.result == "WIN"])
        strat_total = len(sigs)
        strat_net_r = sum(s.net_r for s in sigs if s.net_r)
        strategy_stats[strat] = {
            "signals": strat_total,
            "wins": strat_wins,
            "losses": strat_total - strat_wins,
            "win_rate_pct": round((strat_wins / strat_total * 100) if strat_total > 0 else 0, 1),
            "net_expectancy_r": round(strat_net_r, 2),
        }

    # Group by regime
    by_regime = {}
    for sig in evaluated:
        if sig.regime not in by_regime:
            by_regime[sig.regime] = []
        by_regime[sig.regime].append(sig)

    regime_stats = {}
    for regime, sigs in by_regime.items():
        regime_wins = len([s for s in sigs if s.result == "WIN"])
        regime_total = len(sigs)
        regime_net_r = sum(s.net_r for s in sigs if s.net_r)
        regime_stats[regime] = {
            "signals": regime_total,
            "wins": regime_wins,
            "losses": regime_total - regime_wins,
            "win_rate_pct": round((regime_wins / regime_total * 100) if regime_total > 0 else 0, 1),
            "net_expectancy_r": round(regime_net_r, 2),
        }

    return {
        "data_type": "تاريخية - Historical",
        "disclaimer": "Past performance does not guarantee future results. All data is historical simulation.",
        "overall_stats": {
            "total_signals": total,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": round(win_rate, 1),
            "net_expectancy_r": round(expectancy, 2),
        },
        "by_strategy": strategy_stats,
        "by_regime": regime_stats,
        "last_update_utc": data_service.get_last_update_time().isoformat() if data_service.get_last_update_time() else None,
    }


@router.get("/data-refresh-info")
async def get_refresh_info():
    """Get information about when and how data was last updated."""
    return {
        "last_update_utc": data_service.get_last_update_time().isoformat() if data_service.get_last_update_time() else None,
        "data_age_hours": data_service._get_data_age_hours(),
        "refresh_process": "Refresh requires: twelvedata_downloader.py → analyze_gold.py → signal_engine.py → evaluate_signals.py",
        "note": "Data is read-only from CSV files. To update, run the Python pipeline scripts in order.",
        "location": "Data files: /data/xauusd_*.csv, /data/enriched/*, /data/signals_history.csv, /data/signals_evaluated.csv",
    }
