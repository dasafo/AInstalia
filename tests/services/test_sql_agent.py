import os
from unittest.mock import MagicMock

import pytest

import backend.services.ai_service as ai_service


class DummyAgent:
    pass


class DummyToolkit:
    def __init__(self, db, llm):
        self.db = db
        self.llm = llm


def test_initialize_sql_agent_uses_sync_dsn(monkeypatch):
    original_url = ai_service.settings.DATABASE_URL
    ai_service.settings.DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
    monkeypatch.setenv("DATABASE_URL_SYNC", "postgresql://user:pass@localhost:5432/dbname_sync")

    captured = {}

    def fake_from_uri(dsn, *_, **__):
        captured["dsn"] = dsn
        return MagicMock()

    monkeypatch.setattr(ai_service.SQLDatabase, "from_uri", staticmethod(fake_from_uri))
    monkeypatch.setattr(ai_service, "SQLDatabaseToolkit", DummyToolkit)
    monkeypatch.setattr(ai_service, "create_sql_agent", lambda llm, toolkit, **_: DummyAgent())

    service = object.__new__(ai_service.AIService)
    service.db_session = MagicMock()
    service.llm = object()

    agent = service._initialize_sql_agent()

    assert agent is not None
    assert captured["dsn"] == "postgresql://user:pass@localhost:5432/dbname_sync"

    ai_service.settings.DATABASE_URL = original_url
    monkeypatch.delenv("DATABASE_URL_SYNC", raising=False)
