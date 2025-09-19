import pytest
from httpx import AsyncClient

from backend.main import app
from backend.db.session import get_db
from backend.api.v1.endpoints import ai as ai_endpoints


class DummyAsyncSession:
    async def close(self):
        return None


class FakeRAGService:
    def __init__(self, *_args, **_kwargs):
        pass

    async def get_knowledge_stats(self):
        return {"success": True, "docs_indexed": 0}

    async def index_documents(self):
        return {"success": True, "indexed": 0}


@pytest.mark.asyncio
async def test_ai_knowledge_stats_stub_ok(monkeypatch):
    async def override_get_db():
        session = DummyAsyncSession()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(ai_endpoints, "RAGService", FakeRAGService)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/ai/knowledge/stats")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert isinstance(data.get("docs_indexed"), int)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ai_knowledge_index_stub_ok(monkeypatch):
    async def override_get_db():
        session = DummyAsyncSession()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(ai_endpoints, "RAGService", FakeRAGService)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/ai/knowledge/index")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert isinstance(data.get("indexed"), int)

    app.dependency_overrides.clear()
