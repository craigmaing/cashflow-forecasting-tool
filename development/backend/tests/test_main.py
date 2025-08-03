import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestHealthCheck:
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data

class TestAPIVersion:
    def test_version_endpoint(self):
        """Test API version endpoint"""
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "features" in data
        assert len(data["features"]) > 0

class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Cash Flow Forecasting Tool API" in data["message"]
