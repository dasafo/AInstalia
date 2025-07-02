#backend/db/base.py
"""
Declarative Base para SQLAlchemy
"""
from sqlalchemy.ext.declarative import declarative_base

# Base class para todos los modelos
Base = declarative_base()

# NOTA: Las importaciones de modelos deben hacerse donde se necesiten,
# no aquí para evitar importaciones circulares.
# Alembic puede encontrar los modelos a través del archivo env.py