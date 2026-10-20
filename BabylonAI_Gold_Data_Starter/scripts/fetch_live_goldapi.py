"""Gold API live spot reference quote (not an OHLC candle, not broker bid/ask)."""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from common import ROOT, iso_utc, to_utc

URL = "https://api.gold-api.com/price/XAU"
OUT_DIR = ROOT / "data" / "live"
FIELDS = ["observed_at_utc", "provider_updated_at_utc", "symbol", "currency", "price_usd_per_troy_oz", "source", "quote_type", "age_seconds", "stale"]


def fetch_quote() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "BabylonGoldAI-DataStarter/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        value = json.load(response)
    if str(value.get("symbol", "")).upper() != "XAU" or str(value.get("currency", "")).upper() != "USD":
        raise ValueError(f"Unexpected symbol/currency in response: {value}")
    price = float(value["price"])
    if not 0 < price < 1e7:
        raise ValueError("Quote value out of plausible range")
    if not value.get("updatedAt"):
        raise ValueError("Provider did not supply updatedAt; quote freshness cannot be verified")
    observed = datetime.now(timezone.utc)
    source_dt = to_utc(str(value["updatedAt"]))
    age = max(0, round((observed - source_dt).total_seconds()))
    return {
        "observed_at_utc": iso_utc(observed.isoformat()),
        "provider_updated_at_utc": iso_utc(source_dt.isoformat()),
        "symbol": "XAU", "currency": "USD", "price_usd_per_troy_oz": price,
        "source": "gold-api.com", "quote_type": "SPOT_REFERENCE_SNAPSHOT_NOT_OHLC",
        "age_seconds": age, "stale": age > 1800,
    }


def persist_quote(quote: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "XAUUSD_latest_quote.json").write_text(json.dumps(quote, indent=2, ensure_ascii=False), encoding="utf-8")
    path = OUT_DIR / "XAUUSD_spot_snapshots.csv"
    # Do not append duplicates with the same provider-update timestamp.
    last_updated = None
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as fp:
            for item in csv.DictReader(fp):
                last_updated = item.get("provider_updated_at_utc")
    if last_updated == quote["provider_updated_at_utc"]:
        return
    with path.open("a", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        if fp.tell() == 0:
            writer.writeheader()
        writer.writerow(quote)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real current XAU quote from Gold API, no key required")
    parser.add_argument("--watch", action="store_true", help="Poll until interrupted; snapshots are not complete candles")
    parser.add_argument("--poll", type=int, default=60, help="Polling interval seconds; minimum 30")
    args = parser.parse_args()
    if args.poll < 30:
        parser.error("--poll must be >= 30 seconds according to provider cache recommendation")
    while True:
        try:
            quote = fetch_quote()
            persist_quote(quote)
            print(json.dumps(quote, ensure_ascii=False, indent=2))
            if quote["stale"]:
                print("WARNING: provider timestamp older than 30 minutes. Market may be closed or feed stale.")
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError, OSError) as exc:
            print(f"ERROR: quote fetch failed, no fabricated fallback: {exc}")
            if not args.watch:
                raise SystemExit(1)
        if not args.watch:
            return
        try:
            time.sleep(args.poll)
        except KeyboardInterrupt:
            print("Stopped")
            return


if __name__ == "__main__":
    main()
