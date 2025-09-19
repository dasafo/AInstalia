import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

from backend.main import app
from backend.db.session import get_db
from backend.services.ai_service import AIService
from backend.api.v1.endpoints import ai as ai_endpoints


def _build_scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalar_one.return_value = value
    result.scalar.return_value = value
    return result


@pytest.mark.asyncio
async def test_ai_insights_success(monkeypatch):
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(side_effect=[
        _build_scalar_result(12),
        _build_scalar_result(7),
        _build_scalar_result(5),
        _build_scalar_result(3200.5),
        _build_scalar_result(3),
    ])

    service = object.__new__(AIService)
    service.db_session = mock_session

    monkeypatch.setattr(ai_endpoints, "get_ai_service", lambda _db: service)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/ai/insights", json={"query": "overview"})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["insights"], list)
    assert any(item["metric"] == "total_clients" for item in data["insights"])

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ai_insights_handles_service_error(monkeypatch):
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(side_effect=Exception("DB boom"))

    service = object.__new__(AIService)
    service.db_session = mock_session

    monkeypatch.setattr(ai_endpoints, "get_ai_service", lambda _db: service)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/ai/insights", json={"query": "overview"})

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "DB boom" in data["error"]

    app.dependency_overrides.clear()
