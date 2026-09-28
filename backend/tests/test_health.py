from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app

client = TestClient(app)


@patch("app.api.v1.endpoints.health.engine.connect")
def test_health_check_returns_ok(mock_connect: MagicMock) -> None:
    mock_connection = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_connection

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }
    mock_connection.execute.assert_called_once()


@patch("app.api.v1.endpoints.health.engine.connect")
def test_health_check_returns_503_when_database_is_unavailable(
    mock_connect: MagicMock,
) -> None:
    mock_connect.side_effect = OperationalError(
        statement="SELECT 1",
        params=None,
        orig=Exception("Database unavailable"),
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database connection unavailable",
    }
