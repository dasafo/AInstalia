#backend/core/logging.py
"""
Sistema de logging profesional para AInstalia
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# Crear directorio de logs si no existe
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """
    Configura el sistema de logging con múltiples handlers
    """
    # Configuración básica
    logging.basicConfig(level=logging.INFO)
    
    # Crear formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo principal
    app_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    
    # Handler para errores
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "errors.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Handler para tests
    test_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "tests.log",
        maxBytes=5242880,  # 5MB
        backupCount=3
    )
    test_handler.setLevel(logging.DEBUG)
    test_handler.setFormatter(detailed_formatter)
    
    # Handler para consola (desarrollo)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configurar logger principal
    logger = logging.getLogger("ainstalia")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    # Logger específico para tests
    test_logger = logging.getLogger("ainstalia.tests")
    test_logger.setLevel(logging.DEBUG)
    test_logger.addHandler(test_handler)
    test_logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "ainstalia"):
    """
    Obtiene un logger configurado
    """
    return logging.getLogger(name)

# Configurar logging al importar
setup_logging() 