"""Shared candle schema / validations. Standard library only."""
from __future__ import annotations

import csv
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ["timestamp_utc", "open", "high", "low", "close", "volume", "source", "instrument", "interval", "bar_complete"]
INTERVAL_SECONDS = {"5min": 300, "15min": 900, "1h": 3600, "4h": 14400}


def to_utc(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_utc(s: str) -> str:
    return to_utc(s).isoformat(timespec="seconds").replace("+00:00", "Z")


def check_candle(row: dict) -> None:
    t = to_utc(row["timestamp_utc"])
    if row["interval"] not in INTERVAL_SECONDS:
        raise ValueError(f"Unsupported candle interval: {row['interval']}")
    if row["instrument"] != "XAU/USD":
        raise ValueError("Wrong instrument")
    vals = [float(row[x]) for x in ("open", "high", "low", "close")]
    if not all(math.isfinite(x) and x > 0 for x in vals):
        raise ValueError(f"Invalid OHLC price at {t}")
    o, h, l, c = vals
    if l > min(o, c) or h < max(o, c) or l > h:
        raise ValueError(f"Invalid OHLC ordering at {t}")
    if row.get("volume") not in ("", None):
        v = float(row["volume"])
        if not math.isfinite(v) or v < 0:
            raise ValueError("Invalid volume")
    if str(row["bar_complete"]).lower() not in ("true", "false"):
        raise ValueError("bar_complete must be True/False")


def save_candles(filepath: Path, rows: list[dict], merge: bool = False) -> int:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    by_stamp: dict[str, dict] = {}
    if merge and filepath.exists():
        with filepath.open("r", encoding="utf-8-sig", newline="") as fp:
            for row in csv.DictReader(fp):
                check_candle(row)
                by_stamp[row["timestamp_utc"]] = row
    for row in rows:
        row = {k: row.get(k, "") for k in HEADERS}
        row["timestamp_utc"] = iso_utc(str(row["timestamp_utc"]))
        check_candle(row)
        by_stamp[row["timestamp_utc"]] = row
    ordered = [by_stamp[k] for k in sorted(by_stamp)]
    with filepath.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(ordered)
    return len(ordered)
