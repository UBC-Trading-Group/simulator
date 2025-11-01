"""
Basic tests for the main application
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Trading Simulator API" in response.json()["message"]


def test_health():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs():
    """Test that API documentation is accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200
