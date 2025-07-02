#backend/main.py
"""
Arranque del servidor FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.v1.api_router import api_router

# Crear instancia de FastAPI
app = FastAPI(
    title="AInstalia - Sistema IA Multiagente",
    description="API para gestión de mantenimiento industrial con agentes IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AInstalia API - Sistema IA Multiagente para Mantenimiento Industrial"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )