"""Generate clearly labeled SYNTHETIC candles; NEVER real prices or backtest evidence."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from common import ROOT, save_candles


def make_demo() -> None:
    randomizer = random.Random(8012026)
    at = datetime(2024, 1, 8, tzinfo=timezone.utc)
    price = 2000.0
    candles = []
    while at < datetime(2024, 2, 3, tzinfo=timezone.utc):
        # Illustrative Monday-Friday 24h grid, NOT actual market session/calendar.
        if at.weekday() < 5:
            drift = 0.02 * (1 if at.day % 3 else -1)
            movement = randomizer.gauss(drift, 1.15)
            o = price
            c = max(500, o + movement)
            h = max(o, c) + abs(randomizer.gauss(0, 0.55))
            l = min(o, c) - abs(randomizer.gauss(0, 0.55))
            candles.append({
                "timestamp_utc": at.isoformat(), "open": round(o, 4),
                "high": round(h, 4), "low": round(l, 4), "close": round(c, 4),
                "volume": "", "source": "SYNTHETIC_DEMO_NOT_REAL",
                "instrument": "XAU/USD", "interval": "5min", "bar_complete": "True",
            })
            price = c
        at += timedelta(minutes=5)

    root = ROOT / "data" / "demo"
    base = save_candles(root / "XAUUSD_5min_SYNTHETIC.csv", candles)
    print(f"5min: {base} synthetic candles")
    for interval, n in [("15min", 3), ("1h", 12), ("4h", 48)]:
        grouped = {}
        for row in candles:
            ts = datetime.fromisoformat(row["timestamp_utc"])
            idx = int(ts.timestamp()) // (n * 300)
            grouped.setdefault(idx, []).append(row)
        rows = []
        for key, batch in sorted(grouped.items()):
            # Skip incomplete groups (may arise from custom demo date range)
            if len(batch) != n:
                continue
            rows.append({
                "timestamp_utc": datetime.fromtimestamp(key * n * 300, tz=timezone.utc).isoformat(),
                "open": batch[0]["open"], "high": max(float(x["high"]) for x in batch),
                "low": min(float(x["low"]) for x in batch), "close": batch[-1]["close"],
                "volume": "", "source": "SYNTHETIC_DEMO_NOT_REAL", "instrument": "XAU/USD",
                "interval": interval, "bar_complete": "True",
            })
        count = save_candles(root / f"XAUUSD_{interval}_SYNTHETIC.csv", rows)
        print(f"{interval}: {count} synthetic candles")


if __name__ == "__main__":
    make_demo()
