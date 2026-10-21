"""Data service for loading and managing OHLC candles and analysis data."""
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import logging

from core.models import Candle, CandleWithIndicators, SignalRecord, EvaluatedSignal
from core.config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for loading and querying OHLC candle data and analysis results."""

    def __init__(self):
        self.candles: Dict[str, List[Candle]] = {}  # interval -> candles
        self.enriched_candles: Dict[str, List[CandleWithIndicators]] = {}  # interval -> enriched
        self.signals_history: List[SignalRecord] = []
        self.evaluated_signals: List[EvaluatedSignal] = []
        self._last_update: Optional[datetime] = None
        self._data_mode = str(settings.DATA_MODE).lower()
        self._data_dir: Optional[Path] = None
        self._real_data_dir = Path(__file__).parent.parent.parent / "data"  # /data folder
        self._load_data()

    def _load_data(self):
        """Load real historical data from /data folder and enriched indicators."""
        try:
            # Try loading real data first
            if self._real_data_dir.exists():
                self._load_real_data()
                self._load_enriched_data()
                self._load_signals_history()
                self._load_evaluated_signals()
                self._last_update = datetime.now(timezone.utc)
                return

            # Fallback to demo/live data
            if self._data_mode == "live":
                data_dir = Path(settings.LIVE_DATA_DIR)
                filename_suffix = "twelvedata"
            else:
                data_dir = Path(settings.DEMO_DATA_DIR)
                filename_suffix = "SYNTHETIC"

            self._data_dir = data_dir
            if not data_dir.exists():
                logger.warning(f"{self._data_mode} data directory not found: {data_dir}")
                return

            for interval in ["5min", "15min", "1h", "4h"]:
                csv_file = data_dir / f"XAUUSD_{interval}_{filename_suffix}.csv"
                if csv_file.exists():
                    loaded = self._load_csv_legacy(csv_file)
                    if loaded:
                        self.candles[interval] = loaded
                    logger.info(
                        "Loaded %s %s complete candles from %s data",
                        len(loaded), interval, self._data_mode,
                    )

            if self.candles:
                self._last_update = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Error loading data: {e}")

    def _load_real_data(self):
        """Load real OHLC data from /data/xauusd_*.csv."""
        for interval in ["5min", "15min", "1h", "4h"]:
            csv_file = self._real_data_dir / f"xauusd_{interval}.csv"
            if csv_file.exists():
                candles = self._load_real_csv(csv_file, interval)
                if candles:
                    self.candles[interval] = candles
                    logger.info(f"Loaded {len(candles)} {interval} real candles")
            else:
                logger.warning(f"Real data file not found: {csv_file}")

    def _load_real_csv(self, filepath: Path, interval: str) -> List[Candle]:
        """Load candles from real OHLC CSV (datetime_utc format)."""
        candles = []
        try:
            with filepath.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ts_str = row["datetime_utc"].strip()
                        ts = datetime.fromisoformat(ts_str)
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        candle = Candle(
                            timestamp_utc=ts,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row.get("volume", 0)) if row.get("volume") else None,
                            source="historical",
                            instrument="XAU/USD",
                            interval=interval,
                            bar_complete=True,
                        )
                        candles.append(candle)
                    except Exception as e:
                        logger.debug(f"Skipped row in {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error reading real CSV {filepath}: {e}")
        return sorted(candles, key=lambda c: c.timestamp_utc)

    def _load_enriched_data(self):
        """Load enriched candles with indicators from /data/enriched/."""
        try:
            enriched_dir = self._real_data_dir / "enriched"
            if not enriched_dir.exists():
                logger.warning(f"Enriched data directory not found: {enriched_dir}")
                return

            for interval in ["5min", "15min", "1h", "4h"]:
                try:
                    csv_file = enriched_dir / f"xauusd_{interval}_indicators.csv"
                    if csv_file.exists():
                        enriched = self._load_enriched_csv(csv_file, interval)
                        if enriched:
                            self.enriched_candles[interval] = enriched
                            logger.info(f"Loaded {len(enriched)} {interval} enriched candles")
                except Exception as e:
                    logger.warning(f"Error loading enriched {interval}: {e}")
        except Exception as e:
            logger.error(f"Error in _load_enriched_data: {e}")

    def _load_enriched_csv(self, filepath: Path, interval: str) -> List[CandleWithIndicators]:
        """Load enriched candles with technical indicators."""
        enriched = []
        try:
            if not filepath.exists():
                logger.warning(f"File does not exist: {filepath}")
                return enriched

            with filepath.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader:
                    return enriched

                for row in reader:
                    if not row:
                        continue
                    try:
                        ts_str = row.get("datetime_utc", "").strip()
                        if not ts_str:
                            continue
                        ts = datetime.fromisoformat(ts_str)
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)

                        def parse_float(val):
                            if not val:
                                return None
                            val_str = str(val).strip()
                            if not val_str or val_str == "":
                                return None
                            return float(val_str)

                        candle_with_ind = CandleWithIndicators(
                            timestamp_utc=ts,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            ema20=parse_float(row.get("ema20")),
                            ema50=parse_float(row.get("ema50")),
                            ema200=parse_float(row.get("ema200")),
                            rsi14=parse_float(row.get("rsi14")),
                            atr14=parse_float(row.get("atr14")),
                            adx14=parse_float(row.get("adx14")),
                            interval=interval,
                        )
                        enriched.append(candle_with_ind)
                    except (ValueError, KeyError, TypeError) as e:
                        logger.debug(f"Skipped row: {e}")
        except Exception as e:
            logger.error(f"Error reading enriched CSV {filepath}: {e}")
        return sorted(enriched, key=lambda c: c.timestamp_utc)

    def _load_signals_history(self):
        """Load signal history from /data/signals_history.csv."""
        csv_file = self._real_data_dir / "signals_history.csv"
        if not csv_file.exists():
            logger.warning(f"Signals history file not found: {csv_file}")
            return

        try:
            with csv_file.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        def parse_float(val):
                            return float(val) if val and val.strip() else None

                        signal = SignalRecord(
                            signal_id=row.get("signal_id", ""),
                            strategy=row.get("strategy", ""),
                            direction=row.get("direction", ""),
                            created_utc=datetime.fromisoformat(row["created_utc"].strip()),
                            state=row.get("state", ""),
                            level=parse_float(row.get("level")),
                            invalidation=parse_float(row.get("invalidation")),
                            confirmed_utc=datetime.fromisoformat(row["confirmed_utc"].strip()) if row.get("confirmed_utc") else None,
                            entry=parse_float(row.get("entry")),
                            target=parse_float(row.get("target")),
                            result=row.get("result", ""),
                            r_multiple=parse_float(row.get("r_multiple")),
                            notes=row.get("notes", ""),
                        )
                        self.signals_history.append(signal)
                    except Exception as e:
                        logger.debug(f"Skipped signal row: {e}")
            logger.info(f"Loaded {len(self.signals_history)} signal records")
        except Exception as e:
            logger.error(f"Error reading signals history: {e}")

    def _load_evaluated_signals(self):
        """Load evaluated signals performance from /data/signals_evaluated.csv."""
        csv_file = self._real_data_dir / "signals_evaluated.csv"
        if not csv_file.exists():
            logger.warning(f"Evaluated signals file not found: {csv_file}")
            return

        try:
            with csv_file.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        def parse_float(val):
                            return float(val) if val and val.strip() else None

                        eval_sig = EvaluatedSignal(
                            strategy=row.get("strategy", ""),
                            direction=row.get("direction", ""),
                            created_utc=datetime.fromisoformat(row["created_utc"].strip()),
                            confirmed_utc=datetime.fromisoformat(row["confirmed_utc"].strip()) if row.get("confirmed_utc") else None,
                            regime=row.get("regime", ""),
                            session=row.get("session", ""),
                            year=int(row.get("year", 0)) if row.get("year") else 0,
                            risk_usd=parse_float(row.get("risk_usd")),
                            result=row.get("result", ""),
                            gross_r=parse_float(row.get("gross_r")),
                            cost_r=parse_float(row.get("cost_r")),
                            net_r=parse_float(row.get("net_r")),
                        )
                        self.evaluated_signals.append(eval_sig)
                    except Exception as e:
                        logger.debug(f"Skipped evaluated signal row: {e}")
            logger.info(f"Loaded {len(self.evaluated_signals)} evaluated signals")
        except Exception as e:
            logger.error(f"Error reading evaluated signals: {e}")

    def _load_csv_legacy(self, filepath: Path) -> List[Candle]:
        """Load candles from legacy demo/live CSV format."""
        candles = []
        try:
            with filepath.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ts = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00"))
                        bar_complete = row.get("bar_complete", "true").lower() == "true"
                        # Never feed a still-forming provider bar to analysis.
                        if not bar_complete:
                            continue
                        candle = Candle(
                            timestamp_utc=ts,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row.get("volume", 0)) if row.get("volume") else None,
                            source=row.get("source", "unknown"),
                            instrument=row.get("instrument", "XAU/USD"),
                            interval=row.get("interval", "unknown"),
                            bar_complete=bar_complete,
                        )
                        candles.append(candle)
                    except Exception as e:
                        logger.debug(f"Skipped invalid row in {filepath}: {e}")
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

    def get_enriched_candles(
        self, interval: str, limit: Optional[int] = None
    ) -> List[CandleWithIndicators]:
        """Get enriched candles with indicators for an interval."""
        if interval not in self.enriched_candles:
            return []
        enriched = self.enriched_candles[interval]
        if limit and len(enriched) > limit:
            enriched = enriched[-limit:]
        return enriched

    def get_latest_enriched(self, interval: str) -> Optional[CandleWithIndicators]:
        """Get the latest enriched candle for an interval."""
        enriched = self.get_enriched_candles(interval)
        return enriched[-1] if enriched else None

    def get_signals_history(self, limit: Optional[int] = None) -> List[SignalRecord]:
        """Get signal history, optionally limited to most recent N."""
        signals = self.signals_history
        if limit and len(signals) > limit:
            signals = signals[-limit:]
        return signals

    def get_evaluated_signals(self, limit: Optional[int] = None) -> List[EvaluatedSignal]:
        """Get evaluated signals, optionally limited to most recent N."""
        signals = self.evaluated_signals
        if limit and len(signals) > limit:
            signals = signals[-limit:]
        return signals

    def reload_data(self):
        """Reload data from disk (useful for live updates)."""
        self.candles.clear()
        self.enriched_candles.clear()
        self.signals_history.clear()
        self.evaluated_signals.clear()
        self._last_update = None
        self._load_data()
        logger.info("Data reloaded")

    def get_last_update_time(self) -> Optional[datetime]:
        """Get the timestamp of the last data load."""
        return self._last_update

    def get_data_status(self) -> Dict[str, Any]:
        """Get status information about loaded data."""
        return {
            "mode": "real" if self._real_data_dir.exists() else self._data_mode,
            "data_type": "historical" if self.enriched_candles else self._data_mode,
            "is_loaded": len(self.candles) > 0,
            "intervals": list(self.candles.keys()),
            "candle_counts": {interval: len(candles) for interval, candles in self.candles.items()},
            "enriched_candle_counts": {interval: len(candles) for interval, candles in self.enriched_candles.items()},
            "signals_count": len(self.signals_history),
            "evaluated_signals_count": len(self.evaluated_signals),
            "sources": {
                interval: sorted({candle.source for candle in candles})
                for interval, candles in self.candles.items()
            },
            "last_update": self._last_update,
            "last_candle_times": {
                interval: self.get_latest_candle(interval).timestamp_utc.isoformat()
                for interval in self.candles.keys()
                if self.get_latest_candle(interval)
            },
            "data_age_hours": self._get_data_age_hours(),
        }

    def _get_data_age_hours(self) -> Optional[float]:
        """Calculate how old the data is in hours."""
        if not self.candles:
            return None
        latest = max(
            (self.get_latest_candle(interval).timestamp_utc
             for interval in self.candles.keys()
             if self.get_latest_candle(interval)),
            default=None
        )
        if latest:
            age = (datetime.now(timezone.utc) - latest).total_seconds() / 3600
            return round(age, 1)
        return None


# Global data service instance
data_service = DataService()
