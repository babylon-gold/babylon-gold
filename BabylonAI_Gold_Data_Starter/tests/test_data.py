"""Offline unit tests, no live API key and no network required."""
import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import common
import fetch_live_goldapi
import fetch_history_twelvedata


class Response(BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()


class DataTests(unittest.TestCase):
    def test_valid_ohlc_and_no_double_count(self):
        row = {"timestamp_utc": "2024-01-01T12:00:00Z", "open": "2000", "high": "2010", "low": "1990", "close": "2005", "volume": "", "source": "SYNTHETIC_DEMO_NOT_REAL", "instrument": "XAU/USD", "interval": "5min", "bar_complete": "True"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.csv"
            common.save_candles(path, [row])
            common.save_candles(path, [row], merge=True)
            with path.open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 1)

    def test_bad_ohlc_rejected(self):
        row = {"timestamp_utc": "2024-01-01T12:00:00Z", "open": 2000, "high": 1900, "low": 1950, "close": 2005, "source": "SYNTHETIC", "instrument": "XAU/USD", "interval": "5min", "bar_complete": "True"}
        with self.assertRaises(ValueError):
            common.check_candle(row)

    def test_quote_json_mock(self):
        payload = {"symbol": "XAU", "currency": "USD", "price": 2040.25, "updatedAt": "2024-01-01T00:00:00Z"}
        with patch("urllib.request.urlopen", return_value=Response(json.dumps(payload).encode())):
            result = fetch_live_goldapi.fetch_quote()
        self.assertEqual(result["price_usd_per_troy_oz"], 2040.25)
        self.assertEqual(result["quote_type"], "SPOT_REFERENCE_SNAPSHOT_NOT_OHLC")
        self.assertTrue(result["stale"])

    def test_historical_candle_json_mock(self):
        payload = {"status": "ok", "meta": {"symbol": "XAU/USD"}, "values": [
            {"datetime": "2024-01-01 12:00:00", "open": "2000", "high": "2002", "low": "1999", "close": "2001"}]}
        with patch("urllib.request.urlopen", return_value=Response(json.dumps(payload).encode())):
            candles = fetch_history_twelvedata.fetch_page("sample_key", "15min", 1, None)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0]["timestamp_utc"], "2024-01-01T12:00:00Z")
        common.check_candle(candles[0])
        self.assertEqual(candles[0]["volume"], "")

    def test_provider_error_no_fallback(self):
        with patch("urllib.request.urlopen", return_value=Response(json.dumps({"status":"error","message":"access denied"}).encode())):
            with self.assertRaises(RuntimeError):
                fetch_history_twelvedata.fetch_page("sample_key", "5min", 2, None)


if __name__ == "__main__":
    unittest.main()
