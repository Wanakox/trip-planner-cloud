"""Deterministic configuration shared by the backend test suite."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DUFFEL_ACCESS_TOKEN", "test-duffel-token")

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """Return an isolated HTTP client and clear dependency overrides afterwards."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
