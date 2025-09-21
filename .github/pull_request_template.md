### Qué hace
- /api/v1/ai/insights: contrato estable + manejo de esquema ausente.
- /api/v1/ai/feedback: persiste user_comment/rating; validaciones; tests.
- /api/v1/ai/schema: await correcto; tests.
- RAG: endpoints stats/index sin FAISS (modo stub); tests.
- SQL agent: DSN sync (psycopg2) → elimina greenlet_spawn; test de humo.

### Cómo probar
```bash
docker compose up -d backend
docker compose exec backend bash -lc 'PYTHONPATH=/app pytest -q'
curl -i http://localhost:8000/api/v1/ai/schema
curl -i -X POST http://localhost:8000/api/v1/ai/feedback
curl -i http://localhost:8000/api/v1/ai/knowledge/stats
curl -i -X POST http://localhost:8000/api/v1/ai/knowledge/index
```
