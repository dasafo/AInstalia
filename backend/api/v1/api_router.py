#backend/api/v1/api_router.py
"""
Router principal de la API v1
Centraliza todas las rutas de los diferentes módulos
"""
from fastapi import APIRouter

from backend.api.v1.endpoints import (
    clients,
    products,
    warehouses,
    stock,
    technicians,
    equipment,
    interventions,
    contracts,
    orders,
    chat,
    knowledge
)

# Crear router principal
api_router = APIRouter()

# Endpoint básico de la API
@api_router.get("/")
async def api_root():
    return {"message": "AInstalia API v1", "status": "active", "endpoints": "See /docs for full API documentation"}

@api_router.get("/ping")
async def ping():
    return {"message": "pong"}

# Incluir todos los routers de endpoints
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["technicians"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(interventions.router, prefix="/interventions", tags=["interventions"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])