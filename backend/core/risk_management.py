"""Risk management engine."""
from typing import Optional
from datetime import datetime, timezone
import logging

from core.models import Signal, RiskAssessment
from core.config import settings

logger = logging.getLogger(__name__)


class RiskManager:
    """Manage and assess trading risks."""

    def __init__(self, account_size: float = 10000.0):
        self.account_size = account_size
        self.current_exposure = 0.0

    def assess_risk(
        self,
        signal: Signal,
        current_price: float,
        account_size: Optional[float] = None,
    ) -> RiskAssessment:
        """Assess risk for a given signal."""
        if account_size:
            self.account_size = account_size

        # Calculate position size based on signal
        position_size_pct = self._calculate_position_size(signal)

        # Calculate account risk
        if signal.stop_loss and signal.entry_price:
            stop_distance = abs(signal.entry_price - signal.stop_loss)
            risk_per_pip = (self.account_size * position_size_pct / 100) / 100
            account_risk_pct = (stop_distance * risk_per_pip) / self.account_size * 100
        else:
            account_risk_pct = 0.0

        # Calculate stop loss in pips
        stop_loss_distance_pips = (
            abs(signal.entry_price - signal.stop_loss) / 0.01  # 1 pip = 0.01 for gold
            if signal.stop_loss else 0.0
        )

        # Check if trade should be blocked
        is_blocked = account_risk_pct > settings.MAX_LOSS_PER_TRADE
        block_reason = None
        recommendation = "PROCEED"

        if is_blocked:
            block_reason = f"Account risk {account_risk_pct:.2f}% exceeds max {settings.MAX_LOSS_PER_TRADE}%"
            recommendation = "WAIT"
        elif account_risk_pct > settings.MAX_LOSS_PER_TRADE * 0.7:
            recommendation = "REDUCE"

        return RiskAssessment(
            timestamp_utc=datetime.now(timezone.utc),
            position_size_pct=position_size_pct,
            account_risk_pct=account_risk_pct,
            stop_loss_distance_pips=stop_loss_distance_pips,
            is_blocked=is_blocked,
            block_reason=block_reason,
            recommendation=recommendation,
        )

    def _calculate_position_size(self, signal: Signal) -> float:
        """Calculate appropriate position size based on signal confidence."""
        # Base position size
        base_size = settings.MAX_POSITION_SIZE / 2  # Start with half max

        # Adjust based on confidence
        if signal.state.value == "CONFIRMED":
            multiplier = 1.2  # Increase for confirmed signals
        elif signal.state.value == "WATCH":
            multiplier = 0.8  # Reduce for watch signals
        else:
            multiplier = 0.0  # No position for invalidated/risk block

        position_size = base_size * multiplier * signal.confidence

        return min(position_size, settings.MAX_POSITION_SIZE)

    def update_exposure(self, size_change: float):
        """Update current exposure."""
        self.current_exposure += size_change
        self.current_exposure = max(0, self.current_exposure)

    def can_open_position(self, signal: Signal) -> bool:
        """Check if a new position can be opened based on risk limits."""
        if signal.state.value == "RISK_BLOCK" or signal.state.value == "INVALIDATED":
            return False

        if signal.state.value == "WATCH":
            return True  # Allow watch signals with small position

        return True  # Allow confirmed signals

    def get_max_position_size(self) -> float:
        """Get maximum allowed position size."""
        available = settings.MAX_POSITION_SIZE - self.current_exposure
        return max(0, available)


risk_manager = RiskManager()
