"""
Basic end-to-end checks for the running API service.
"""

import pytest

pytestmark = pytest.mark.api


def test_root(http_client):
    """Root endpoint returns the product banner"""
    response = http_client.get("/")
    assert response.status_code == 200
    assert "Trading Simulator API" in response.json()["message"]


def test_health(http_client):
    """Health endpoint signals readiness"""
    response = http_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs(http_client):
    """Swagger UI is served"""
    response = http_client.get("/api/docs")
    assert response.status_code == 200
