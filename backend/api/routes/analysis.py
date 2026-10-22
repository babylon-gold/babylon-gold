"""Market analysis endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional

from core.models import Analysis
from core.data_service import data_service
from core.indicators import indicator_calculator
from core.signal_engine import signal_engine
from core.risk_management import risk_manager

router = APIRouter()


def _format_value(value, decimals: int = 2, prefix: str = "") -> str:
    """Format optional numeric values without turning missing data into errors."""
    if value is None:
        return "غ.م"
    return f"{prefix}{value:.{decimals}f}"


def _generate_arabic_summary(
    indicators,
    signal,
    risk_assessment,
    current_price: float,
) -> str:
    """Generate Arabic summary of market analysis."""
    summary = f"""
تحليل السوق - XAU/USD

السعر الحالي: {_format_value(current_price, 2, '$')}

🔍 المؤشرات الفنية:
• المتوسطات المتحركة (EMA):
  - EMA20: {_format_value(indicators.ema_20, 2, '$')}
  - EMA50: {_format_value(indicators.ema_50, 2, '$')}
  - EMA200: {_format_value(indicators.ema_200, 2, '$')}

• مؤشر القوة النسبية (RSI): {_format_value(indicators.rsi, 1)}
• متوسط النطاق الحقيقي (ATR): {_format_value(indicators.atr, 2)}
• مؤشر الاتجاه (ADX): {_format_value(indicators.adx, 1)}
• نوع السوق: {indicators.market_regime or 'غير محدد'}

📊 مستويات الدعم والمقاومة:
• الدعم: {_format_value(indicators.support_level, 2, '$')}
• المقاومة: {_format_value(indicators.resistance_level, 2, '$')}

🎯 الإشارة:
• الاتجاه المقترح: {signal.direction}
• حالة الإشارة: {signal.state.value}
• درجة الثقة: {signal.confidence*100:.1f}%
• سعر الدخول: {_format_value(signal.entry_price, 2, '$')}
• وقف الخسارة: {_format_value(signal.stop_loss, 2, '$')}
• جني الأرباح: {_format_value(signal.take_profit, 2, '$')}

⚠️ إدارة المخاطر:
• حجم الموضع: {risk_assessment.position_size_pct:.2f}%
• مخاطر الحساب: {risk_assessment.account_risk_pct:.2f}%
• التوصية: {risk_assessment.recommendation}

📌 ملاحظات مهمة:
• هذا التحليل يعتمد على بيانات تاريخية/تجريبية قد تكون اصطناعية
• لا يتضمن التحليل تنبؤات بحركة السعر المستقبلية
• استخدم دائماً وقف الخسارة وأدوات إدارة المخاطر
• التداول ينطوي على مخاطر عالية وقد تخسر رأس المال
"""
    return summary.strip()


@router.get("")
async def get_analysis(
    timeframe: str = Query(..., description="Timeframe: 5min, 15min, 1h, 4h"),
    account_size: float = Query(10000.0, description="Account size for risk assessment"),
):
    """Get analysis for specified timeframe."""
    if timeframe not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid timeframe. Must be one of: 5min, 15min, 1h, 4h")

    candles = data_service.get_candles(timeframe, limit=300)

    if not candles:
        raise HTTPException(status_code=404, detail="No data available for this timeframe")

    try:
        indicators = indicator_calculator.calculate_all(candles)
        signal = signal_engine.generate_signal(candles, indicators, timeframe)
        current_price = candles[-1].close
        risk_assessment = risk_manager.assess_risk(signal, current_price, account_size)

        arabic_summary = _generate_arabic_summary(indicators, signal, risk_assessment, current_price)

        return {
            "timestamp_utc": indicators.timestamp_utc,
            "timeframe": timeframe,
            "current_price": current_price,
            "indicators": indicators.dict() if hasattr(indicators, 'dict') else indicators,
            "signal": signal.dict() if hasattr(signal, 'dict') else signal,
            "risk_assessment": risk_assessment.dict() if hasattr(risk_assessment, 'dict') else risk_assessment,
            "arabic_summary": arabic_summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complete/{interval}", response_model=Analysis)
async def complete_analysis(
    interval: str = Path(..., description="Candle interval: 5min, 15min, 1h, 4h"),
    account_size: float = Query(10000.0, description="Account size for risk assessment"),
):
    """Get complete market analysis for specified interval."""
    if interval not in ["5min", "15min", "1h", "4h"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    candles = data_service.get_candles(interval, limit=300)

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

        # Assess risk
        current_price = candles[-1].close
        risk_assessment = risk_manager.assess_risk(signal, current_price, account_size)

        # Generate Arabic summary (no fabricated forecasts)
        arabic_summary = _generate_arabic_summary(
            indicators,
            signal,
            risk_assessment,
            current_price,
        )

        analysis = Analysis(
            timestamp_utc=indicators.timestamp_utc,
            interval=interval,
            current_price=current_price,
            indicators=indicators,
            signal=signal,
            risk_assessment=risk_assessment,
            arabic_summary=arabic_summary,
        )

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-timeframe")
async def multi_timeframe_analysis(
    account_size: float = Query(10000.0, description="Account size for risk assessment"),
):
    """Get analysis across all timeframes for comparison."""
    try:
        results = {}

        for interval in ["5min", "15min", "1h", "4h"]:
            candles = data_service.get_candles(interval, limit=300)

            if not candles:
                results[interval] = {"status": "no_data"}
                continue

            try:
                indicators = indicator_calculator.calculate_all(candles)
                signal = signal_engine.generate_signal(candles, indicators, interval)
                risk = risk_manager.assess_risk(signal, candles[-1].close, account_size)

                results[interval] = {
                    "status": "ok",
                    "signal": signal.direction,
                    "confidence": signal.confidence,
                    "state": signal.state.value,
                    "risk_recommendation": risk.recommendation,
                }
            except Exception as e:
                results[interval] = {"status": "error", "error": str(e)}

        return {
            "symbol": "XAU/USD",
            "account_size": account_size,
            "analysis": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
