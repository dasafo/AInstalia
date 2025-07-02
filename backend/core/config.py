#backend/core/config.py
"""
Configuración global de la aplicación
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ainstalia_db"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # WhatsApp/Mensajería
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    
    # Chatwoot
    CHATWOOT_URL: Optional[str] = None
    CHATWOOT_ACCESS_TOKEN: Optional[str] = None
    
    # Vector Store
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    
    # Configuración del entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()