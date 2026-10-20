"""Fetch historical XAU/USD real OHLC candles using your own Twelve Data API key."""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from common import ROOT, INTERVAL_SECONDS, iso_utc, save_candles, to_utc

ENDPOINT = "https://api.twelvedata.com/time_series"


def fetch_page(api_key: str, interval: str, count: int, before: datetime | None) -> list[dict]:
    params = {
        "symbol": "XAU/USD", "interval": interval,
        "apikey": api_key, "outputsize": str(count),
        "timezone": "UTC", "format": "JSON", "order": "desc",
    }
    if before is not None:
        params["end_date"] = before.strftime("%Y-%m-%d %H:%M:%S")
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "BabylonGoldAI-DataStarter/1.0"})
    # Avoid echoing the request URL to logs (it contains the API key).
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if not isinstance(payload, dict) or payload.get("status") == "error" or "values" not in payload:
        msg = payload.get("message", str(payload)) if isinstance(payload, dict) else "invalid JSON structure"
        raise RuntimeError(f"Twelve Data rejected the request: {msg}")
    meta = payload.get("meta") or {}
    if str(meta.get("symbol", "XAU/USD")).upper().replace(" ", "") != "XAU/USD":
        raise RuntimeError(f"Unexpected symbol {meta.get('symbol')}")
    candles = []
    for value in payload["values"]:
        ts = to_utc(str(value["datetime"]))
        close_time = ts + timedelta(seconds=INTERVAL_SECONDS[interval])
        # Latest partial candle should not be used for bar-close signals/backtests.
        complete = close_time <= datetime.now(timezone.utc)
        candles.append({
            "timestamp_utc": iso_utc(ts.isoformat()),
            "open": value["open"], "high": value["high"], "low": value["low"], "close": value["close"],
            "volume": value.get("volume") or "",  # Forex/spot gold often no centralized traded volume.
            "source": "twelvedata.com", "instrument": "XAU/USD", "interval": interval,
            "bar_complete": str(complete),
        })
    return candles


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real XAU/USD OHLC candles from Twelve Data")
    parser.add_argument("--interval", required=True, choices=list(INTERVAL_SECONDS))
    parser.add_argument("--count", type=int, default=1000, help="Candles per request (1-5000)")
    parser.add_argument("--pages", type=int, default=1, help="Maximum number of backward pages")
    parser.add_argument("--start", help="Optional earliest UTC date YYYY-MM-DD")
    parser.add_argument("--end", help="Optional latest UTC date YYYY-MM-DD (inclusive)")
    parser.add_argument("--delay", type=float, default=9.0, help="Seconds between pages to respect credits")
    args = parser.parse_args()
    if args.count < 1 or args.count > 5000 or args.pages < 1 or args.pages > 100:
        parser.error("--count must be 1..5000; --pages must be 1..100")
    if args.delay < 0:
        parser.error("--delay cannot be negative")
    api_key = os.environ.get("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        parser.error("Missing TWELVEDATA_API_KEY environment variable; register at https://twelvedata.com/")
    start = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=timezone.utc) if args.start else None
    before = (datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1, seconds=-1)) if args.end else None
    if start and before and before < start:
        parser.error("--end precedes --start")
    rows: list[dict] = []
    for i in range(args.pages):
        try:
            batch = fetch_page(api_key, args.interval, args.count, before)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError, RuntimeError) as exc:
            raise SystemExit(f"Fetch stopped (no mock fallback): {exc}")
        if not batch:
            break
        new_rows = [r for r in batch if (not start or to_utc(r["timestamp_utc"]) >= start) and (not before or to_utc(r["timestamp_utc"]) <= before)]
        rows.extend(new_rows)
        oldest = min(to_utc(r["timestamp_utc"]) for r in batch)
        print(f"Page {i+1}: received {len(batch)} candles; oldest = {oldest.date()}")
        if len(batch) < args.count or (start and oldest <= start):
            break
        # Backward page boundary: one second before the oldest timestamp.
        before = oldest - timedelta(seconds=1)
        if i + 1 < args.pages:
            time.sleep(args.delay)
    if not rows:
        raise SystemExit("No OHLC candles returned. Check date range, symbol access and plan.")
    filepath = ROOT / "data" / "live" / f"XAUUSD_{args.interval}_twelvedata.csv"
    n = save_candles(filepath, rows, merge=True)
    print(f"Saved {n} unique rows (including existing data) to {filepath}")
    print("IMPORTANT: Verify your plan authorizes intraday XAU/USD and does not deliver delayed candles.")


if __name__ == "__main__":
    main()
