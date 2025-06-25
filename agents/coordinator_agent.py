"""Agente Coordinador - Orquesta la interacción entre agentes - CORREGIDO"""

from typing import Dict, Any
from .base_agent import BaseAgent

class CoordinatorAgent(BaseAgent):
    """Agente coordinador que orquesta el flujo de trabajo"""
    
    def __init__(self, llm):
        super().__init__("coordinator", llm)
        self.session_context = {}
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordina el procesamiento de entrada del estudiante"""
        
        student_input = input_data.get("student_input", "")
        self.add_to_history(student_input, "student")
        
        # Determinar el tipo de interacción
        interaction_type = await self._classify_interaction(student_input)
        
        # Preparar contexto para otros agentes
        context = {
            "student_input": student_input,
            "interaction_type": interaction_type,
            "session_context": self.session_context,
            "conversation_history": self.conversation_history
        }
        
        return {
            "context": context,
            "needs_assessment": True,  # Siempre evaluar
            "needs_retrieval": True,   # Siempre recuperar contenido
            "needs_tutoring": True     # Siempre generar respuesta tutorial
        }
    
    async def _classify_interaction(self, student_input: str) -> str:
        """Clasifica el tipo de interacción del estudiante"""
        
        prompt = f"""
        Clasifica este input del estudiante en UNA de estas categorías:
        
        - "question": Pregunta sobre un concepto específico
        - "examples_request": Pide ejemplos específicos  
        - "procedure_request": Pregunta cómo hacer algo
        - "greeting": Saludo inicial
        - "answer": Responde a un ejercicio
        
        Input: "{student_input}"
        
        Responde SOLO con la categoría. Nada más.
        """
        
        classification = await self.generate_response(prompt)
        return classification.lower().strip()
    
    async def synthesize_response(self, agent_outputs: Dict[str, Any]) -> str:
        """Sintetiza las respuestas de todos los agentes"""
        
        assessment = agent_outputs.get("assessment", {})
        retrieved_content = agent_outputs.get("retrieved_content", "")
        tutor_response = agent_outputs.get("tutor_response", "")
        practice_exercise = agent_outputs.get("practice_exercise", "")
        
        # Actualizar contexto de sesión
        if assessment:
            self.session_context.update({
                "student_level": assessment.get("level", 3),
                "current_topic": assessment.get("topic", ""),
                "knowledge_gaps": assessment.get("gaps", [])
            })
        
        # IMPORTANTE: Devolver directamente la respuesta del tutor
        # sin modificarla ni agregar texto genérico
        final_response = tutor_response
        
        # Solo agregar ejercicio si existe
        if practice_exercise:
            final_response += f"\n\n{practice_exercise}"
        
        self.add_to_history(final_response, "assistant")
        
        return final_response