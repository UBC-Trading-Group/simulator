"""
Shared pytest fixtures for backend tests.
"""

from __future__ import annotations

import os
import time
from typing import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

DEFAULT_API_BASE_URL = "http://api:8000"
HEALTH_PATH = "/health"


@pytest.fixture(scope="session")
def fastapi_test_client() -> Iterator[TestClient]:
    """
    FastAPI TestClient for unit tests that need the ASGI app without spinning up
    the entire Docker stack.
    """

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """
    Base URL used by API tests. Defaults to the docker-compose service and can
    be overridden via API_BASE_URL.
    """

    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def http_client(api_base_url: str) -> Iterator[httpx.Client]:
    """
    HTTP client that talks to the running FastAPI service. Ensures the service
    is healthy before yielding the client instance.
    """

    _wait_for_api(api_base_url)
    with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
        yield client


def _wait_for_api(base_url: str) -> None:
    timeout = float(os.getenv("API_HEALTH_TIMEOUT", "60"))
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            response = httpx.get(
                f"{base_url}{HEALTH_PATH}",
                timeout=float(os.getenv("API_HEALTH_PROBE_TIMEOUT", "5")),
            )
            if response.status_code == 200:
                return
            last_error = RuntimeError(
                f"Health endpoint returned {response.status_code}: {response.text}"
            )
        except httpx.HTTPError as exc:
            last_error = exc

        time.sleep(1)

    raise RuntimeError(
        f"API at {base_url} failed health checks within {timeout}s"
    ) from last_error
