"""Deterministic configuration shared by the backend test suite."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DUFFEL_ACCESS_TOKEN", "test-duffel-token")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test-supabase-key")
os.environ.setdefault("SMTP_USERNAME", "test-smtp-user")
os.environ.setdefault("SMTP_PASSWORD", "test-smtp-password")
os.environ.setdefault("SMTP_FROM_EMAIL", "test@example.com")
os.environ.setdefault("FRONTEND_URL", "https://example.com")

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """Return an isolated HTTP client and clear dependency overrides afterwards."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
