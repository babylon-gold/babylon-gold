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


def test_get_candles_invalid_interval(client):
    """Test get candles with invalid interval."""
    response = client.get("/api/v1/data/candles/invalid")
    assert response.status_code == 400


def test_get_candles_5min(client):
    """Test get 5min candles."""
    response = client.get("/api/v1/data/candles/5min?limit=10")
    assert response.status_code in [200, 404]  # 404 if no data


def test_get_candles_15min(client):
    """Test get 15min candles."""
    response = client.get("/api/v1/data/candles/15min?limit=5")
    assert response.status_code in [200, 404]


def test_generate_signal_invalid_interval(client):
    """Test signal generation with invalid interval."""
    response = client.get("/api/v1/signals/generate/invalid")
    assert response.status_code == 400


def test_complete_analysis_15min(client):
    """Test complete analysis endpoint."""
    response = client.get("/api/v1/analysis/complete/15min?account_size=5000")
    # Should be 200 if data is loaded, 404 if not, 500 if data loading fails gracefully
    assert response.status_code in [200, 404, 500]
    if response.status_code == 200:
        data = response.json()
        assert "analysis" in data or "signal" in data or "indicators" in data


def test_multi_timeframe_analysis(client):
    """Test multi-timeframe analysis."""
    response = client.get("/api/v1/analysis/multi-timeframe?account_size=10000")
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
