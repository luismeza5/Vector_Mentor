"""Clase base para todos los agentes del sistema"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings, AGENT_CONFIGS

class BaseAgent(ABC):
    """Clase base abstracta para todos los agentes"""
    
    def __init__(self, agent_type: str, llm: ChatOpenAI):
        self.agent_type = agent_type
        self.llm = llm
        self.config = AGENT_CONFIGS.get(agent_type, {})
        self.conversation_history = []
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la entrada y retorna el resultado"""
        pass
    
    def get_system_message(self) -> str:
        """Retorna el mensaje del sistema para este agente"""
        return self.config.get("system_prompt", "")
    
    def add_to_history(self, message: str, role: str = "user"):
        """Agrega mensaje al historial de conversación"""
        self.conversation_history.append({"role": role, "content": message})
        
        # Mantener solo los últimos N mensajes
        max_history = settings.MAX_CONVERSATION_HISTORY
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
    
    async def generate_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Genera respuesta usando el LLM"""
        messages = [
            SystemMessage(content=self.get_system_message()),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"Error en {self.agent_type}: {e}")
            return "Lo siento, ha ocurrido un error procesando tu solicitud."