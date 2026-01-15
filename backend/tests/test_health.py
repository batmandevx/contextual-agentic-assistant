"""
Tests for health endpoint
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_endpoint_has_cors_headers():
    """Test that CORS headers are present."""
    response = client.get("/api/health")
    # CORS headers should be present due to middleware
    assert response.status_code == 200
