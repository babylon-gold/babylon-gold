"""Technical indicator calculations for market analysis."""
from typing import List, Tuple, Optional
import math
import logging

from core.models import Candle, IndicatorValues
from core.config import settings

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators."""

    @staticmethod
    def calculate_ema(values: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if not values or period < 1 or len(values) < period:
            return [None] * len(values)

        ema = [None] * (period - 1)
        multiplier = 2.0 / (period + 1)

        # Simple MA for first EMA value
        sma = sum(values[:period]) / period
        ema.append(sma)

        # Calculate remaining EMAs
        for i in range(period, len(values)):
            ema_val = (values[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_val)

        return ema

    @staticmethod
    def calculate_rsi(values: List[float], period: int = 14) -> List[Optional[float]]:
        """Calculate Relative Strength Index."""
        if not values or period < 2 or len(values) < period + 1:
            return [None] * len(values)

        rsi = [None] * (period)

        # Calculate price changes
        deltas = [values[i] - values[i-1] for i in range(1, len(values))]

        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        # Initial average gain/loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # Calculate RSI
        if avg_gain + avg_loss != 0:
            rs = avg_gain / (avg_loss + 1e-10)
            rsi.append(100 - (100 / (1 + rs)))
        else:
            rsi.append(50)

        # Subsequent RSI values using smoothed averages
        for i in range(period + 1, len(values)):
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period

            if avg_gain + avg_loss != 0:
                rs = avg_gain / (avg_loss + 1e-10)
                rsi.append(100 - (100 / (1 + rs)))
            else:
                rsi.append(50)

        return rsi

    @staticmethod
    def calculate_atr(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
        """Calculate Average True Range."""
        if not candles or len(candles) < period + 1:
            return [None] * len(candles)

        atr = [None] * period

        # Calculate true ranges
        tr_values = []
        for i in range(len(candles)):
            high = candles[i].high
            low = candles[i].low
            close_prev = candles[i-1].close if i > 0 else candles[i].close

            tr = max(
                high - low,
                abs(high - close_prev),
                abs(low - close_prev)
            )
            tr_values.append(tr)

        # Calculate ATR
        atr_val = sum(tr_values[:period]) / period
        atr.append(atr_val)

        for i in range(period + 1, len(candles)):
            atr_val = (atr_val * (period - 1) + tr_values[i]) / period
            atr.append(atr_val)

        return atr

    @staticmethod
    def calculate_adx(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
        """Calculate Average Directional Index (simplified)."""
        if not candles or len(candles) < period * 2:
            return [None] * len(candles)

        adx = [None] * (period * 2 - 1)

        # Calculate directional movements
        plus_dm = [0] * len(candles)
        minus_dm = [0] * len(candles)

        for i in range(1, len(candles)):
            up = candles[i].high - candles[i-1].high
            down = candles[i-1].low - candles[i].low

            if up > down and up > 0:
                plus_dm[i] = up
            if down > up and down > 0:
                minus_dm[i] = down

        # Calculate true range and directional indicators
        tr_sum = 0
        plus_di_sum = 0
        minus_di_sum = 0

        for i in range(period * 2 - 1, len(candles)):
            # True range sum for period
            if i == period * 2 - 1:
                tr_sum = sum([
                    max(
                        candles[j].high - candles[j].low,
                        abs(candles[j].high - candles[j-1].close if j > 0 else 0),
                        abs(candles[j].low - candles[j-1].close if j > 0 else 0)
                    )
                    for j in range(i - period + 1, i + 1)
                ])
                plus_dm_sum = sum(plus_dm[i - period + 1:i + 1])
                minus_dm_sum = sum(minus_dm[i - period + 1:i + 1])

            if tr_sum > 0:
                plus_di = 100 * plus_dm_sum / tr_sum
                minus_di = 100 * minus_dm_sum / tr_sum
                di_diff = abs(plus_di - minus_di)
                di_sum = plus_di + minus_di

                if di_sum > 0:
                    dx = 100 * di_diff / di_sum
                    adx_val = dx  # Simplified; full ADX requires EMA of DX
                    adx.append(adx_val)

        return adx

    @staticmethod
    def detect_support_resistance(
        candles: List[Candle],
        lookback: int = 20,
    ) -> Tuple[Optional[float], Optional[float]]:
        """Detect support and resistance levels."""
        if not candles or len(candles) < lookback:
            return None, None

        recent = candles[-lookback:]
        lows = [c.low for c in recent]
        highs = [c.high for c in recent]

        support = min(lows)
        resistance = max(highs)

        return support, resistance

    @staticmethod
    def detect_market_regime(
        candles: List[Candle],
        ema_20: List[Optional[float]],
        ema_50: List[Optional[float]],
        lookback: int = 10,
    ) -> Optional[str]:
        """Detect market regime: uptrend, downtrend, or ranging."""
        if not candles or not ema_20 or not ema_50:
            return None

        recent_candles = candles[-lookback:]
        recent_ema20 = ema_20[-lookback:]
        recent_ema50 = ema_50[-lookback:]

        # Filter out None values
        valid_indices = [
            i for i in range(len(recent_ema20))
            if recent_ema20[i] is not None and recent_ema50[i] is not None
        ]

        if len(valid_indices) < 3:
            return None

        # Check EMA ordering and price position
        last_idx = valid_indices[-1]
        ema20_val = recent_ema20[last_idx]
        ema50_val = recent_ema50[last_idx]
        close_val = recent_candles[last_idx].close

        if ema20_val > ema50_val and close_val > ema20_val:
            return "uptrend"
        elif ema20_val < ema50_val and close_val < ema20_val:
            return "downtrend"
        else:
            return "ranging"

    @staticmethod
    def calculate_all(candles: List[Candle]) -> Optional[IndicatorValues]:
        """Calculate all indicators for the latest candle."""
        if not candles:
            return None

        latest = candles[-1]
        closes = [c.close for c in candles]

        # Calculate EMAs
        ema_20 = IndicatorCalculator.calculate_ema(closes, settings.EMA_SHORT)
        ema_50 = IndicatorCalculator.calculate_ema(closes, settings.EMA_MEDIUM)
        ema_200 = IndicatorCalculator.calculate_ema(closes, settings.EMA_LONG)

        # Calculate RSI
        rsi_values = IndicatorCalculator.calculate_rsi(closes, settings.RSI_PERIOD)

        # Calculate ATR
        atr_values = IndicatorCalculator.calculate_atr(candles, settings.ATR_PERIOD)

        # Calculate ADX
        adx_values = IndicatorCalculator.calculate_adx(candles, settings.ADX_PERIOD)

        # Support/Resistance
        support, resistance = IndicatorCalculator.detect_support_resistance(candles)

        # Market regime
        regime = IndicatorCalculator.detect_market_regime(candles, ema_20, ema_50)

        return IndicatorValues(
            timestamp_utc=latest.timestamp_utc,
            ema_20=ema_20[-1] if ema_20[-1] is not None else None,
            ema_50=ema_50[-1] if ema_50[-1] is not None else None,
            ema_200=ema_200[-1] if ema_200[-1] is not None else None,
            rsi=rsi_values[-1],
            atr=atr_values[-1],
            adx=adx_values[-1] if adx_values[-1] is not None else None,
            support_level=support,
            resistance_level=resistance,
            market_regime=regime,
        )


indicator_calculator = IndicatorCalculator()
