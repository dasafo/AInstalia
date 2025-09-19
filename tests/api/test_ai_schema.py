import pytest
from httpx import AsyncClient

from backend.main import app
from backend.db.session import get_db
from backend.api.v1.endpoints import ai as ai_endpoints


class DummyAsyncSession:
    async def close(self):
        return None


class FakeAIService:
    role_permissions = {"administrador": []}

    async def _get_database_schema_info(self):
        return {"tables": []}


@pytest.mark.asyncio
async def test_ai_schema_endpoint(monkeypatch):
    async def override_get_db():
        session = DummyAsyncSession()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(ai_endpoints, "get_ai_service", lambda db: FakeAIService())

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/ai/schema")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "schema" in data

    app.dependency_overrides.clear()
