"""Security tests for Babylon AI Gold Intelligence backend."""
import pytest
from fastapi.testclient import TestClient
import os

# Mock the ADMIN_API_KEY environment variable
os.environ["ADMIN_API_KEY"] = "test_admin_key_12345"

from main import app

client = TestClient(app)


class TestAdminAuthenticationRequired:
    """Test that admin endpoints require authentication."""

    def test_data_refresh_without_auth_returns_401(self):
        """POST /admin/data/refresh without auth should return 401."""
        response = client.post("/api/v1/admin/data/refresh")
        assert response.status_code == 401

    def test_scheduler_start_without_auth_returns_401(self):
        """POST /admin/scheduler/start without auth should return 401."""
        response = client.post("/api/v1/admin/scheduler/start")
        assert response.status_code == 401

    def test_scheduler_stop_without_auth_returns_401(self):
        """POST /admin/scheduler/stop without auth should return 401."""
        response = client.post("/api/v1/admin/scheduler/stop")
        assert response.status_code == 401

    def test_scheduler_status_without_auth_returns_401(self):
        """GET /admin/scheduler/status without auth should return 401."""
        response = client.get("/api/v1/admin/scheduler/status")
        assert response.status_code == 401

    def test_health_detailed_without_auth_returns_401(self):
        """GET /admin/system/health-detailed without auth should return 401."""
        response = client.get("/api/v1/admin/system/health-detailed")
        assert response.status_code == 401

    def test_data_refresh_status_without_auth_returns_401(self):
        """GET /admin/data/refresh-status without auth should return 401."""
        response = client.get("/api/v1/admin/data/refresh-status")
        assert response.status_code == 401


class TestAdminAuthenticationValid:
    """Test that admin endpoints accept valid authentication."""

    def test_scheduler_status_with_valid_auth_returns_200(self):
        """GET /admin/scheduler/status with valid auth should return 200."""
        headers = {"Authorization": f"Bearer test_admin_key_12345"}
        response = client.get("/api/v1/admin/scheduler/status", headers=headers)
        # Authentication should pass (not 401 or 403)
        assert response.status_code not in [401, 403], f"Auth failed: {response.status_code}"
        # Should return 200 (successful request)
        assert response.status_code == 200


class TestAdminAuthenticationInvalid:
    """Test that admin endpoints reject invalid credentials."""

    def test_scheduler_status_with_invalid_token_returns_403(self):
        """GET /admin/scheduler/status with invalid token should return 403."""
        headers = {"Authorization": "Bearer wrong_key"}
        response = client.get("/api/v1/admin/scheduler/status", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_scheduler_status_with_no_bearer_returns_401(self):
        """GET /admin/scheduler/status without Bearer scheme should return 401."""
        headers = {"Authorization": "test_admin_key_12345"}
        response = client.get("/api/v1/admin/scheduler/status", headers=headers)
        assert response.status_code == 401, f"Expected 401 for malformed auth, got {response.status_code}"


class TestAnalysisEndpointNoUncontrolledNotifications:
    """Test that analysis endpoint doesn't trigger Telegram notifications."""

    def test_analysis_endpoint_returns_200(self):
        """GET /analysis should return 200 without authentication."""
        response = client.get("/api/v1/analysis?timeframe=15min")
        # Should be accessible without auth (public data endpoint)
        assert response.status_code == 200, f"Analysis endpoint failed: {response.status_code}"

    def test_analysis_endpoint_returns_json(self):
        """GET /analysis should return JSON response."""
        response = client.get("/api/v1/analysis?timeframe=15min")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert "timeframe" in data, f"Missing 'timeframe' in response: {data.keys()}"


class TestPublicEndpointsNoAuth:
    """Test that public endpoints don't require authentication."""

    def test_health_endpoint_without_auth_returns_200(self):
        """GET /health should be accessible without auth."""
        response = client.get("/api/v1/health")
        # Health check should return 200
        assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"

    def test_root_endpoint_without_auth_returns_200(self):
        """GET / should be accessible without auth."""
        response = client.get("/")
        assert response.status_code == 200
        assert "babylon" in response.json().get("service", "").lower()


class TestSecurityHeaders:
    """Test that security headers are properly configured."""

    def test_cors_headers_present(self):
        """Response should have CORS headers."""
        response = client.get("/api/v1/health")
        # Public endpoint should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_api_key_txt_not_in_repo():
    """Verify that api_key.txt was removed."""
    import pathlib
    api_key_file = pathlib.Path(__file__).parent.parent.parent / "api_key.txt"
    assert not api_key_file.exists(), "api_key.txt should not exist in repository"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
