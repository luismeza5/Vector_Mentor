"""Configuraciones del sistema EduMentor AI"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# CARGAR EL ARCHIVO .ENV PRIMERO
load_dotenv()

class Settings:
    """Configuraciones del sistema"""
    
    # API Keys - Cargar directamente desde os.getenv
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Modelo de lenguaje
    LLM_MODEL: str = "gpt-4o-mini"  # Modelo más económico
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # Modelo actualizado
    
    # Base vectorial
    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # Configuraciones de RAG
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Configuraciones de agentes
    MAX_CONVERSATION_HISTORY: int = 10
    STUDENT_LEVEL_SCALE: tuple = (1, 5)  # Escala de nivel del estudiante
    
    # Streamlit
    STREAMLIT_PORT: int = 8501
    STREAMLIT_HOST: str = "localhost"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time} | {level} | {name} | {message}"

# Configuraciones específicas por agente
AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "coordinator": {
        "temperature": 0.7,
        "max_tokens": 500,
        "system_prompt": """Eres el coordinador de un sistema de tutoría académica. 
        Tu trabajo es orquestar la interacción entre diferentes agentes especializados 
        para proporcionar la mejor experiencia de aprendizaje al estudiante."""
    },
    
    "assessor": {
        "temperature": 0.3,
        "max_tokens": 300,
        "system_prompt": """Eres un evaluador experto en álgebra lineal. 
        Analiza las respuestas del estudiante y determina su nivel de comprensión 
        en una escala de 1-5. Identifica gaps de conocimiento y sugiere el siguiente paso."""
    },
    
    "retriever": {
        "temperature": 0.1,
        "max_tokens": 200,
        "system_prompt": """Eres un especialista en recuperación de contenido educativo. 
        Tu trabajo es encontrar el material más relevante y apropiado para el nivel 
        del estudiante."""
    },
    
    "tutor": {
        "temperature": 0.8,
        "max_tokens": 600,
        "system_prompt": """Eres un tutor experto en álgebra lineal. 
        Explica conceptos de manera clara y adaptada al nivel del estudiante. 
        Usa ejemplos, analogías y un lenguaje accesible."""
    }
}

# Instancia global de configuraciones
settings = Settings()

# Debug: Mostrar longitud de la API key
print(f"🔑 API Key detectada - Longitud: {len(settings.OPENAI_API_KEY)}")
if len(settings.OPENAI_API_KEY) > 40:
    print(f"✅ API Key válida (primeros 10 chars: {settings.OPENAI_API_KEY[:10]})")
else:
    print(f"⚠️ API Key parece inválida o incompleta")