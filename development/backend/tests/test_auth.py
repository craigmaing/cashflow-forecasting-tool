import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthentication:
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_failure(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "invalid", "password": "invalid"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
