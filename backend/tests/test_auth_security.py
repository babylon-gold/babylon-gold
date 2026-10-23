"""Security tests for authentication and authorization."""
import os
import pytest
from fastapi.testclient import TestClient

from main import app

# Set test key after app import (auth now reads dynamically)
os.environ["ADMIN_API_KEY"] = "test_admin_key_12345"

client = TestClient(app)


class TestAdminAuthenticationRequired:
    """Test that admin endpoints require authentication."""

    def test_scheduler_status_without_auth_returns_401(self):
        """GET /admin/scheduler/status without auth returns 401 Unauthorized."""
        response = client.get("/api/v1/admin/scheduler/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_data_refresh_without_auth_returns_401(self):
        """POST /admin/data/refresh without auth returns 401 Unauthorized."""
        response = client.post("/api/v1/admin/data/refresh")
        assert response.status_code == 401

    def test_scheduler_start_without_auth_returns_401(self):
        """POST /admin/scheduler/start without auth returns 401 Unauthorized."""
        response = client.post("/api/v1/admin/scheduler/start")
        assert response.status_code == 401

    def test_scheduler_stop_without_auth_returns_401(self):
        """POST /admin/scheduler/stop without auth returns 401 Unauthorized."""
        response = client.post("/api/v1/admin/scheduler/stop")
        assert response.status_code == 401


class TestNotificationAuthenticationRequired:
    """Test that notification endpoints require authentication."""

    def test_notification_preferences_post_without_auth_returns_401(self):
        """POST /notifications/preferences without auth returns 401."""
        response = client.post(
            "/api/v1/notifications/preferences",
            json={"signals": True, "analysis": False, "risks": True, "system": False},
        )
        assert response.status_code == 401

    def test_test_signal_without_auth_returns_401(self):
        """POST /notifications/test-signal without auth returns 401."""
        response = client.post("/api/v1/notifications/test-signal")
        assert response.status_code == 401

    def test_test_analysis_without_auth_returns_401(self):
        """POST /notifications/test-analysis without auth returns 401."""
        response = client.post("/api/v1/notifications/test-analysis")
        assert response.status_code == 401

    def test_test_risk_without_auth_returns_401(self):
        """POST /notifications/test-risk without auth returns 401."""
        response = client.post("/api/v1/notifications/test-risk")
        assert response.status_code == 401

    def test_test_system_without_auth_returns_401(self):
        """POST /notifications/test-system without auth returns 401."""
        response = client.post("/api/v1/notifications/test-system")
        assert response.status_code == 401

    def test_custom_notification_without_auth_returns_401(self):
        """POST /notifications/custom without auth returns 401."""
        response = client.post("/api/v1/notifications/custom", params={"message": "test"})
        assert response.status_code == 401


class TestAdminAuthenticationWithValidToken:
    """Test that valid tokens are accepted."""

    def test_scheduler_status_with_valid_token(self):
        """GET /admin/scheduler/status with valid token works."""
        headers = {"Authorization": "Bearer test_admin_key_12345"}
        response = client.get("/api/v1/admin/scheduler/status", headers=headers)
        # Should NOT return 403 (auth passes)
        assert response.status_code != 403, f"Auth failed: {response.status_code}"


class TestAdminAuthenticationWithInvalidToken:
    """Test that invalid tokens are rejected."""

    def test_scheduler_status_with_invalid_token_returns_403(self):
        """GET /admin/scheduler/status with invalid token returns 403."""
        headers = {"Authorization": "Bearer wrong_key"}
        response = client.get("/api/v1/admin/scheduler/status", headers=headers)
        assert response.status_code == 403


class TestPublicEndpointsNoAuth:
    """Test that public endpoints don't require authentication."""

    def test_health_endpoint_no_auth(self):
        """GET /health should work without auth."""
        response = client.get("/api/v1/health")
        # Public endpoint, should work
        assert response.status_code == 200

    def test_root_endpoint_no_auth(self):
        """GET / should work without auth."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "babylon" in data.get("service", "").lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
