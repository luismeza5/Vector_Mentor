"""VectorMentor - Agentes del sistema de tutoría"""

from .base_agent import BaseAgent
from .coordinator_agent import CoordinatorAgent
from .retriever_agent import RetrieverAgent
from .assessor_agent import AssessorAgent
from .tutor_agent import TutorAgent

__all__ = [
    'BaseAgent',
    'CoordinatorAgent', 
    'RetrieverAgent',
    'AssessorAgent',
    'TutorAgent'
]

# Versión del módulo de agentes
__version__ = '1.0.0'