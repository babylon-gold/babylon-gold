"""Validate candle CSV before feeding analysis/backtests."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from common import HEADERS, check_candle, to_utc


def validate(path: Path) -> tuple[int, str, str]:
    with path.open(encoding="utf-8-sig", newline="") as fp:
        rdr = csv.DictReader(fp)
        if rdr.fieldnames != HEADERS:
            raise ValueError(f"Incorrect columns: {rdr.fieldnames}; expected {HEADERS}")
        last = None
        count = 0
        sources = set()
        for row in rdr:
            check_candle(row)
            ts = to_utc(row["timestamp_utc"])
            if last is not None and ts <= last:
                raise ValueError(f"Data not strictly ascending or duplicated timestamp: {ts}")
            last = ts
            count += 1
            sources.add(row["source"])
    if not count:
        raise ValueError("CSV is empty")
    if len(sources) != 1:
        raise ValueError(f"Multiple providers/sources in same file: {sources}")
    return count, next(iter(sources)), str(last)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file", type=Path)
    args = p.parse_args()
    count, source, last = validate(args.file)
    print(f"PASS | Rows={count} | Source={source} | Last candle={last}")
    if source.startswith("SYNTHETIC"):
        print("WARNING: SYNTHETIC DEMO. Never use these candles to claim real-world trading performance.")
