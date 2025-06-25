"""Configuración de logging"""

import sys
from loguru import logger
from config.settings import settings

def setup_logging():
    """Configura el sistema de logging"""
    
    # Remover logger por defecto
    logger.remove()
    
    # Configurar logger para consola
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Configurar logger para archivo
    logger.add(
        "logs/eduamentor.log",
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="1 day",
        retention="7 days"
    )
    
    logger.info("Sistema de logging configurado")