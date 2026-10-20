"""Data service for loading and managing OHLC candles."""
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict
import logging

from core.models import Candle
from core.config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for loading and querying OHLC candle data."""

    def __init__(self):
        self.candles: Dict[str, List[Candle]] = {}  # interval -> candles
        self._last_update: Optional[datetime] = None
        self._load_demo_data()

    def _load_demo_data(self):
        """Load demo synthetic data from CSV files."""
        try:
            demo_dir = Path(settings.DEMO_DATA_DIR)
            if not demo_dir.exists():
                logger.warning(f"Demo data directory not found: {demo_dir}")
                return

            for interval in ["5min", "15min", "1h", "4h"]:
                csv_file = demo_dir / f"XAUUSD_{interval}_SYNTHETIC.csv"
                if csv_file.exists():
                    self.candles[interval] = self._load_csv(csv_file)
                    logger.info(f"Loaded {len(self.candles[interval])} {interval} candles from demo data")

            self._last_update = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Error loading demo data: {e}")

    def _load_csv(self, filepath: Path) -> List[Candle]:
        """Load candles from a CSV file."""
        candles = []
        try:
            with filepath.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ts = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00"))
                        candle = Candle(
                            timestamp_utc=ts,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row["volume"]) if row.get("volume") else None,
                            source=row["source"],
                            instrument=row["instrument"],
                            interval=row["interval"],
                            bar_complete=row["bar_complete"].lower() == "true",
                        )
                        candles.append(candle)
                    except Exception as e:
                        logger.warning(f"Skipped invalid row in {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error reading CSV {filepath}: {e}")

        return sorted(candles, key=lambda c: c.timestamp_utc)

    def get_candles(
        self,
        interval: str,
        limit: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Candle]:
        """Get candles for a specific interval with optional filtering."""
        if interval not in self.candles:
            return []

        candles = self.candles[interval]

        # Filter by time range if provided
        if start_time:
            candles = [c for c in candles if c.timestamp_utc >= start_time]
        if end_time:
            candles = [c for c in candles if c.timestamp_utc <= end_time]

        # Return most recent N candles if limit specified
        if limit and len(candles) > limit:
            candles = candles[-limit:]

        return candles

    def get_latest_candle(self, interval: str) -> Optional[Candle]:
        """Get the most recent complete candle for an interval."""
        candles = [c for c in self.get_candles(interval) if c.bar_complete]
        return candles[-1] if candles else None

    def get_candles_since(self, interval: str, timestamp: datetime) -> List[Candle]:
        """Get all candles since a specific timestamp."""
        return [c for c in self.get_candles(interval) if c.timestamp_utc >= timestamp]

    def reload_data(self):
        """Reload data from disk (useful for live updates)."""
        self.candles.clear()
        self._load_demo_data()
        logger.info("Data reloaded")

    def get_last_update_time(self) -> Optional[datetime]:
        """Get the timestamp of the last data load."""
        return self._last_update

    def get_data_status(self) -> Dict:
        """Get status information about loaded data."""
        return {
            "is_loaded": len(self.candles) > 0,
            "intervals": list(self.candles.keys()),
            "candle_counts": {interval: len(candles) for interval, candles in self.candles.items()},
            "last_update": self._last_update,
            "last_candle_times": {
                interval: self.get_latest_candle(interval).timestamp_utc.isoformat()
                for interval in self.candles.keys()
                if self.get_latest_candle(interval)
            },
        }


# Global data service instance
data_service = DataService()
