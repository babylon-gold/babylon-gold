"""Core data models for Babylon AI Gold Intelligence."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum


class SignalState(str, Enum):
    """Signal states enum."""
    WATCH = "WATCH"
    CONFIRMED = "CONFIRMED"
    INVALIDATED = "INVALIDATED"
    RISK_BLOCK = "RISK_BLOCK"


class Candle(BaseModel):
    """OHLC candle data model."""
    timestamp_utc: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: Optional[float] = None
    source: str
    instrument: str = "XAU/USD"
    interval: Literal["5min", "15min", "1h", "4h"]
    bar_complete: bool = True

    class Config:
        use_enum_values = True


class IndicatorValues(BaseModel):
    """Technical indicator values."""
    timestamp_utc: datetime
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    rsi: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    market_regime: Optional[str] = None  # "uptrend", "downtrend", "ranging"


class Signal(BaseModel):
    """Trading signal model."""
    timestamp_utc: datetime
    symbol: str = "XAU/USD"
    interval: Literal["5min", "15min", "1h", "4h"]
    direction: Literal["BUY", "SELL", "NEUTRAL"]
    state: SignalState
    confidence: float = Field(..., ge=0.0, le=1.0)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    evidence: List[str] = []  # Evidence supporting the signal
    risks: List[str] = []  # Risks/uncertainties


class RiskAssessment(BaseModel):
    """Risk assessment model."""
    timestamp_utc: datetime
    position_size_pct: float
    account_risk_pct: float
    stop_loss_distance_pips: float
    is_blocked: bool
    block_reason: Optional[str] = None
    recommendation: str  # "PROCEED", "REDUCE", "WAIT"


class Analysis(BaseModel):
    """Complete market analysis."""
    timestamp_utc: datetime
    interval: Literal["5min", "15min", "1h", "4h"]
    current_price: float
    indicators: IndicatorValues
    signal: Signal
    risk_assessment: RiskAssessment
    arabic_summary: str  # AI explanation in Arabic (no fabricated data)


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    backend_version: str
    data_loaded: bool
    last_data_update: Optional[datetime] = None


class GoldQuote(BaseModel):
    """Validated Gold API spot reference quote (not an OHLC candle)."""
    observed_at_utc: datetime
    provider_updated_at_utc: datetime
    symbol: str
    currency: str
    price_usd_per_troy_oz: float = Field(..., gt=0)
    source: str
    quote_type: str
    age_seconds: int = Field(..., ge=0)
    stale: bool


class CandleWithIndicators(BaseModel):
    """OHLC candle enriched with technical indicators."""
    timestamp_utc: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    rsi14: Optional[float] = None
    atr14: Optional[float] = None
    adx14: Optional[float] = None
    interval: Literal["5min", "15min", "1h", "4h"]


class SignalRecord(BaseModel):
    """Historical signal record from analysis."""
    signal_id: str
    strategy: str
    direction: str
    created_utc: datetime
    state: str
    level: Optional[float] = None
    invalidation: Optional[float] = None
    confirmed_utc: Optional[datetime] = None
    entry: Optional[float] = None
    target: Optional[float] = None
    result: str
    r_multiple: Optional[float] = None
    notes: str


class EvaluatedSignal(BaseModel):
    """Evaluated signal with performance metrics."""
    strategy: str
    direction: str
    created_utc: datetime
    confirmed_utc: Optional[datetime] = None
    regime: str
    session: str
    year: int
    risk_usd: Optional[float] = None
    result: str
    gross_r: Optional[float] = None
    cost_r: Optional[float] = None
    net_r: Optional[float] = None
