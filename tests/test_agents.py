# tests/test_agents.py
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents import BaseAgent, CoordinatorAgent, RetrieverAgent, AssessorAgent, TutorAgent
    print("✅ Todos los agentes importados correctamente")
    print(f"✅ Agentes disponibles: {len([BaseAgent, CoordinatorAgent, RetrieverAgent, AssessorAgent, TutorAgent])}")
except ImportError as e:
    print(f"❌ Error: {e}")

try:
    from config import settings, AGENT_CONFIGS
    print("✅ Configuraciones cargadas")
    print(f"✅ Agentes configurados: {len(AGENT_CONFIGS)}")
    print(f"✅ API Key configurada: {'Sí' if settings.OPENAI_API_KEY else 'No'}")
except ImportError as e:
    print(f"❌ Error de config: {e}")