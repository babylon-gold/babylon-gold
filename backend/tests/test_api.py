"""API tests."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Babylon AI Gold Intelligence"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]


def test_data_status(client):
    """Test data status endpoint."""
    response = client.get("/api/v1/data/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_loaded" in data


def test_live_quote(client):
    """Return a fresh validated Gold API spot quote when available."""
    quote_file = Path(__file__).resolve().parents[2] / "BabylonAI_Gold_Data_Starter" / "data" / "live" / "XAUUSD_latest_quote.json"
    if not quote_file.exists():
        pytest.skip("Live quote file is not present")

    response = client.get("/api/v1/quote")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["symbol"] == "XAU"
    assert data["currency"] == "USD"
    assert data["source"] == "gold-api.com"
    assert data["price_usd_per_troy_oz"] > 0
    assert data["stale"] is False


def test_live_quote_stale_returns_503(client, monkeypatch, tmp_path):
    """Do not serve a stale spot quote as current data."""
    from api.routes import quote as quote_route

    quote_file = tmp_path / "quote.json"
    quote_file.write_text(
        '{"observed_at_utc":"2026-10-20T23:00:00Z",'
        '"provider_updated_at_utc":"2026-10-20T22:00:00Z",'
        '"symbol":"XAU","currency":"USD","price_usd_per_troy_oz":4000,'
        '"source":"gold-api.com","quote_type":"SPOT_REFERENCE_SNAPSHOT_NOT_OHLC",'
        '"age_seconds":3600,"stale":true}',
        encoding="utf-8",
    )
    monkeypatch.setattr(quote_route, "_quote_path", lambda: quote_file)

    response = client.get("/api/v1/quote")
    assert response.status_code == 503
    assert "stale" in response.json()["detail"].lower()


def test_live_quote_invalid_returns_503(client, monkeypatch, tmp_path):
    """Do not fabricate a response when the quote file is malformed."""
    from api.routes import quote as quote_route

    quote_file = tmp_path / "quote.json"
    quote_file.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(quote_route, "_quote_path", lambda: quote_file)

    response = client.get("/api/v1/quote")
    assert response.status_code == 503
    assert "invalid" in response.json()["detail"].lower()


def test_get_candles_invalid_interval(client):
    """Test get candles with invalid interval."""
    response = client.get("/api/v1/data/candles/invalid")
    assert response.status_code == 400


def test_get_candles_5min(client):
    """Test get 5min candles."""
    response = client.get("/api/v1/data/candles/5min?limit=10")
    assert response.status_code == 200, response.text
    candles = response.json()
    assert len(candles) == 10
    assert all(candle["instrument"] == "XAU/USD" for candle in candles)
    assert all(candle["source"] in {"SYNTHETIC_DEMO_NOT_REAL", "twelvedata.com", "historical"} for candle in candles)
    assert all(candle["low"] <= min(candle["open"], candle["close"]) for candle in candles)
    assert all(candle["high"] >= max(candle["open"], candle["close"]) for candle in candles)


def test_get_candles_15min(client):
    """Test get 15min candles."""
    response = client.get("/api/v1/data/candles/15min?limit=5")
    assert response.status_code == 200, response.text
    assert len(response.json()) == 5


def test_generate_signal_invalid_interval(client):
    """Test signal generation with invalid interval."""
    response = client.get("/api/v1/signals/generate/invalid")
    assert response.status_code == 400


def test_complete_analysis_15min(client):
    """Test complete analysis endpoint."""
    response = client.get("/api/v1/analysis/complete/15min?account_size=5000")
    assert response.status_code == 200, response.text
    data = response.json()
    assert {"timestamp_utc", "interval", "current_price", "indicators", "signal", "risk_assessment", "arabic_summary"} <= data.keys()
    assert data["interval"] == "15min"
    assert data["current_price"] > 0
    assert data["signal"]["interval"] == "15min"


def test_signal_history_15min(client):
    """Signal history should skip insufficient early windows and return a valid list."""
    response = client.get("/api/v1/signals/signal-history/15min?limit=3")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["interval"] == "15min"
    assert data["signal_count"] == len(data["signals"])
    assert data["signal_count"] <= 3


def test_assess_risk_15min(client):
    """Risk assessment should return a structured response for a valid interval."""
    response = client.post("/api/v1/signals/assess-risk/15min?account_size=5000")
    assert response.status_code == 200, response.text
    data = response.json()
    assert {"signal", "risk_assessment", "can_trade"} <= data.keys()
    risk = data["risk_assessment"]
    assert {"position_size_pct", "account_risk_pct", "stop_loss_distance_pips", "is_blocked", "recommendation"} <= risk.keys()


def test_live_data_mode_filters_incomplete_bars(monkeypatch):
    """When live mode is selected, only complete Twelve Data bars are loaded."""
    from core.config import settings
    from core.data_service import DataService

    live_dir = Path(__file__).resolve().parents[2] / "BabylonAI_Gold_Data_Starter" / "data" / "live"
    required = [live_dir / f"XAUUSD_{interval}_twelvedata.csv" for interval in ("5min", "15min", "1h", "4h")]
    if not all(path.exists() for path in required):
        pytest.skip("Downloaded Twelve Data files are not present")

    monkeypatch.setattr(settings, "DATA_MODE", "live")
    monkeypatch.setattr(settings, "LIVE_DATA_DIR", str(live_dir))
    service = DataService()

    assert set(service.candles) == {"5min", "15min", "1h", "4h"}
    for candles in service.candles.values():
        assert candles
        assert all(candle.source in {"twelvedata.com", "historical"} for candle in candles)
        assert all(candle.bar_complete for candle in candles)


def test_multi_timeframe_analysis(client):
    """Test multi-timeframe analysis."""
    response = client.get("/api/v1/analysis/multi-timeframe?account_size=10000")
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
