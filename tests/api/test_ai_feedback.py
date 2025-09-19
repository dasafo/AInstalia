import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

from backend.main import app
from backend.db.session import get_db


class DummyAsyncSession:
    def __init__(self):
        self.added = []
        self.rollback_called = False

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        return None

    async def refresh(self, obj):
        if getattr(obj, "feedback_id", None) is None:
            obj.feedback_id = 1
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(timezone.utc)

    async def rollback(self):
        self.rollback_called = True


@pytest.mark.asyncio
async def test_ai_feedback_success(monkeypatch):
    session = DummyAsyncSession()

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "original_query": "¿Cuál es el horario del servicio?",
        "ai_response": "El servicio atiende de 9 a 18 h",
        "user_comment": "Respuesta clara",
        "rating": 4,
        "user_type": "administrador"
    }

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/ai/feedback", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["feedback_id"] == 1
    assert data["user_comment"] == "Respuesta clara"
    assert data["rating"] == 4
    assert data["status"] == "pendiente"
    assert "created_at" in data

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ai_feedback_rating_validation(monkeypatch):
    session = DummyAsyncSession()

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "original_query": "¿Cuál es el horario del servicio?",
        "ai_response": "El servicio atiende de 9 a 18 h",
        "user_comment": "Respuesta clara",
        "rating": 6,
        "user_type": "administrador"
    }

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/ai/feedback", json=payload)

    assert response.status_code == 422

    app.dependency_overrides.clear()
