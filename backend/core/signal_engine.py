"""Signal generation engine based on technical analysis."""
from typing import List, Tuple, Optional
from datetime import datetime, timezone
import logging

from core.models import Candle, IndicatorValues, Signal, SignalState
from core.config import settings
from core.indicators import IndicatorCalculator

logger = logging.getLogger(__name__)


class SignalEngine:
    """Generate trading signals based on technical indicators."""

    @staticmethod
    def generate_signal(
        candles: List[Candle],
        indicators: IndicatorValues,
        interval: str,
    ) -> Optional[Signal]:
        """Generate a trading signal based on current market conditions."""
        if not candles or not indicators:
            return None

        latest = candles[-1]

        # Calculate signal components
        ema_signal = SignalEngine._analyze_ema(indicators)
        rsi_signal = SignalEngine._analyze_rsi(indicators)
        atr_signal = SignalEngine._analyze_atr(indicators, latest.close)
        regime_signal = SignalEngine._analyze_regime(indicators)
        support_resistance_signal = SignalEngine._analyze_support_resistance(indicators, latest.close)

        # Combine signals
        direction, confidence, evidence, risks = SignalEngine._combine_signals(
            ema_signal,
            rsi_signal,
            atr_signal,
            regime_signal,
            support_resistance_signal,
        )

        # Determine state based on confidence
        if confidence >= settings.CONFIRMED_THRESHOLD:
            state = SignalState.CONFIRMED
        elif confidence >= settings.WATCH_THRESHOLD:
            state = SignalState.WATCH
        else:
            state = SignalState.INVALIDATED

        # Calculate entry/exit levels
        entry_price = latest.close
        stop_loss, take_profit, rrr = SignalEngine._calculate_levels(
            direction=direction,
            entry=entry_price,
            atr=indicators.atr,
            support=indicators.support_level,
            resistance=indicators.resistance_level,
        )

        return Signal(
            timestamp_utc=datetime.now(timezone.utc),
            symbol="XAU/USD",
            interval=interval,
            direction=direction,
            state=state,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=rrr,
            evidence=evidence,
            risks=risks,
        )

    @staticmethod
    def _analyze_ema(indicators: IndicatorValues) -> Tuple[str, float]:
        """Analyze EMA structure and trend."""
        if not indicators.ema_20 or not indicators.ema_50:
            return "NEUTRAL", 0.0

        evidence = []
        score = 0.0

        # EMA ordering indicates trend
        if indicators.ema_20 > indicators.ema_50 and indicators.ema_50 > indicators.ema_200:
            evidence.append("EMA 20 > 50 > 200: Strong uptrend")
            score += 0.4
            direction = "BUY"
        elif indicators.ema_20 < indicators.ema_50 and indicators.ema_50 < indicators.ema_200:
            evidence.append("EMA 20 < 50 < 200: Strong downtrend")
            score += 0.4
            direction = "SELL"
        else:
            evidence.append("EMAs not aligned: Mixed trend")
            score += 0.1
            direction = "NEUTRAL"

        return direction, score

    @staticmethod
    def _analyze_rsi(indicators: IndicatorValues) -> Tuple[str, float]:
        """Analyze RSI momentum."""
        if indicators.rsi is None:
            return "NEUTRAL", 0.0

        evidence = []
        score = 0.0
        direction = "NEUTRAL"

        if indicators.rsi > settings.RSI_OVERBOUGHT:
            evidence.append(f"RSI {indicators.rsi:.1f} > {settings.RSI_OVERBOUGHT}: Overbought")
            direction = "SELL"
            score += 0.2
        elif indicators.rsi < settings.RSI_OVERSOLD:
            evidence.append(f"RSI {indicators.rsi:.1f} < {settings.RSI_OVERSOLD}: Oversold")
            direction = "BUY"
            score += 0.2
        else:
            evidence.append(f"RSI {indicators.rsi:.1f}: Neutral zone")
            direction = "NEUTRAL"
            score += 0.05

        return direction, score

    @staticmethod
    def _analyze_atr(indicators: IndicatorValues, current_price: float) -> Tuple[str, float]:
        """Analyze volatility using ATR."""
        if not indicators.atr:
            return "NEUTRAL", 0.0

        evidence = []
        score = 0.0

        # ATR indicates volatility; can be used for position sizing
        atr_pct = (indicators.atr / current_price) * 100

        if atr_pct > 0.5:
            evidence.append(f"ATR {atr_pct:.2f}%: High volatility - Use smaller positions")
            score += 0.1
        elif atr_pct < 0.2:
            evidence.append(f"ATR {atr_pct:.2f}%: Low volatility - Can increase size")
            score += 0.1
        else:
            evidence.append(f"ATR {atr_pct:.2f}%: Normal volatility")
            score += 0.05

        return "NEUTRAL", score

    @staticmethod
    def _analyze_regime(indicators: IndicatorValues) -> Tuple[str, float]:
        """Analyze market regime."""
        if not indicators.market_regime:
            return "NEUTRAL", 0.0

        evidence = []
        score = 0.0

        if indicators.market_regime == "uptrend":
            evidence.append("Market regime: Uptrend")
            score += 0.15
            direction = "BUY"
        elif indicators.market_regime == "downtrend":
            evidence.append("Market regime: Downtrend")
            score += 0.15
            direction = "SELL"
        else:
            evidence.append("Market regime: Ranging")
            score += 0.05
            direction = "NEUTRAL"

        return direction, score

    @staticmethod
    def _analyze_support_resistance(indicators: IndicatorValues, current_price: float) -> Tuple[str, float]:
        """Analyze support/resistance levels."""
        if not indicators.support_level or not indicators.resistance_level:
            return "NEUTRAL", 0.0

        evidence = []
        score = 0.0
        distance_to_support = current_price - indicators.support_level
        distance_to_resistance = indicators.resistance_level - current_price

        if distance_to_support < distance_to_resistance:
            evidence.append(f"Price near support ({distance_to_support:.2f}): Potential bounce")
            score += 0.1
            direction = "BUY"
        elif distance_to_resistance < distance_to_support:
            evidence.append(f"Price near resistance ({distance_to_resistance:.2f}): Potential reversal")
            score += 0.1
            direction = "SELL"
        else:
            evidence.append("Price mid-range between support/resistance")
            score += 0.05
            direction = "NEUTRAL"

        return direction, score

    @staticmethod
    def _combine_signals(
        ema_sig: Tuple[str, float],
        rsi_sig: Tuple[str, float],
        atr_sig: Tuple[str, float],
        regime_sig: Tuple[str, float],
        sr_sig: Tuple[str, float],
    ) -> Tuple[str, float, List[str], List[str]]:
        """Combine individual signals into final recommendation."""
        directions = [ema_sig[0], rsi_sig[0], regime_sig[0], sr_sig[0]]
        scores = [ema_sig[1], rsi_sig[1], atr_sig[1], regime_sig[1], sr_sig[1]]

        confidence = sum(scores) / len(scores) if scores else 0.0
        confidence = min(confidence, 1.0)

        # Count directional votes
        buy_votes = sum(1 for d in directions if d == "BUY")
        sell_votes = sum(1 for d in directions if d == "SELL")

        if buy_votes > sell_votes:
            direction = "BUY"
        elif sell_votes > buy_votes:
            direction = "SELL"
        else:
            direction = "NEUTRAL"

        # Collect evidence and risks
        evidence = [
            f"EMA Signal: {ema_sig[0]}",
            f"RSI Signal: {rsi_sig[0]}",
            f"Regime: {regime_sig[0]}",
            f"Support/Resistance: {sr_sig[0]}",
        ]

        risks = [
            "Do not rely on signals alone; always use stop losses",
            "Sample data is synthetic and does not reflect real market conditions",
            "Past performance does not indicate future results",
        ]

        return direction, confidence, evidence, risks

    @staticmethod
    def _calculate_levels(
        direction: str,
        entry: float,
        atr: Optional[float],
        support: Optional[float],
        resistance: Optional[float],
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate stop loss and take profit levels."""
        if atr is None or atr == 0:
            return None, None, None

        if direction == "BUY":
            stop_loss = entry - atr
            take_profit = entry + (atr * 2)  # 1:2 risk/reward
        elif direction == "SELL":
            stop_loss = entry + atr
            take_profit = entry - (atr * 2)
        else:
            return None, None, None

        rrr = abs(take_profit - entry) / abs(stop_loss - entry) if abs(stop_loss - entry) > 0 else 0

        return stop_loss, take_profit, rrr


signal_engine = SignalEngine()
