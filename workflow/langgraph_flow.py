"""Definición del flujo de trabajo con LangGraph - CORREGIDO"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from agents.coordinator_agent import CoordinatorAgent
from agents.assessor_agent import AssessorAgent
from agents.retriever_agent import RetrieverAgent
from agents.tutor_agent import TutorAgent
from rag.vector_store import VectorStoreManager
from config.settings import settings

# Definir el estado del workflow
class WorkflowState(TypedDict):
    student_input: str
    context: Dict[str, Any]
    assessment: Dict[str, Any]
    retrieved_content: str
    tutor_response: str
    practice_exercise: str
    final_response: str
    needs_assessment: bool
    needs_retrieval: bool
    needs_tutoring: bool

class VectorMentorWorkflow:
    """Workflow principal del sistema multiagente - CORREGIDO"""
    
    def __init__(self):
        self.llm = None
        self.agents = {}
        self.workflow = None
        self.vector_manager = None
        
    async def initialize(self):
        """Inicializa el workflow y todos los agentes"""
        
        # Inicializar LLM con la API correcta
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0.7
        )
        
        # Inicializar vector store (sin await - no es async)
        self.vector_manager = VectorStoreManager()
        
        # Inicializar agentes
        self.agents = {
            "coordinator": CoordinatorAgent(self.llm),
            "assessor": AssessorAgent(self.llm),
            "retriever": RetrieverAgent(self.llm, self.vector_manager),
            "tutor": TutorAgent(self.llm)
        }
        
        # Crear workflow con LangGraph
        self._create_workflow()
        
        print("✅ VectorMentor workflow inicializado")
    
    def _create_workflow(self):
        """Crea el workflow usando LangGraph con sintaxis correcta"""
        
        # Definir el grafo de estados con TypedDict
        workflow = StateGraph(WorkflowState)
        
        # Agregar nodos (agentes)
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("assessor", self._assessor_node)
        workflow.add_node("retriever", self._retriever_node)
        workflow.add_node("tutor", self._tutor_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Definir flujo con condiciones
        workflow.set_entry_point("coordinator")
        
        # Flujo condicional mejorado
        workflow.add_conditional_edges(
            "coordinator",
            self._route_after_coordinator,
            {
                "assess": "assessor",
                "skip_assess": "retriever"
            }
        )
        
        workflow.add_conditional_edges(
            "assessor", 
            self._route_after_assessor,
            {
                "retrieve": "retriever",
                "skip_retrieve": "tutor"
            }
        )
        
        workflow.add_edge("retriever", "tutor")
        workflow.add_edge("tutor", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        # Compilar workflow
        self.workflow = workflow.compile()
    
    def _route_after_coordinator(self, state: WorkflowState) -> str:
        """Determina si necesita evaluación"""
        return "assess" if state.get("needs_assessment", True) else "skip_assess"
    
    def _route_after_assessor(self, state: WorkflowState) -> str:
        """Determina si necesita recuperación"""
        return "retrieve" if state.get("needs_retrieval", True) else "skip_retrieve"
    
    async def _coordinator_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del coordinador"""
        try:
            result = await self.agents["coordinator"].process(state)
            state.update(result)
            return state
        except Exception as e:
            print(f"Error en coordinador: {e}")
            state["final_response"] = "Error en el coordinador"
            return state
    
    async def _assessor_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del evaluador"""
        try:
            if state.get("needs_assessment", True):
                result = await self.agents["assessor"].process(state)
                state["assessment"] = result
            return state
        except Exception as e:
            print(f"Error en evaluador: {e}")
            state["assessment"] = {"level": 3, "topic": "error"}
            return state
    
    async def _retriever_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del recuperador"""
        try:
            if state.get("needs_retrieval", True):
                result = await self.agents["retriever"].process(state)
                state.update(result)
            return state
        except Exception as e:
            print(f"Error en recuperador: {e}")
            state["retrieved_content"] = "Contenido no disponible"
            return state
    
    async def _tutor_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del tutor"""
        try:
            if state.get("needs_tutoring", True):
                result = await self.agents["tutor"].process(state)
                state.update(result)
            return state
        except Exception as e:
            print(f"Error en tutor: {e}")
            state["tutor_response"] = "Error generando respuesta tutorial"
            return state
    
    async def _synthesizer_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo sintetizador final"""
        try:
            final_response = await self.agents["coordinator"].synthesize_response(state)
            state["final_response"] = final_response
            return state
        except Exception as e:
            print(f"Error en sintetizador: {e}")
            state["final_response"] = "Error sintetizando respuesta"
            return state
    
    async def process_student_input(self, student_input: str) -> str:
        """Procesa input del estudiante a través del workflow"""
        
        initial_state = WorkflowState(
            student_input=student_input,
            context={},
            assessment={},
            retrieved_content="",
            tutor_response="",
            practice_exercise="",
            final_response="",
            needs_assessment=True,
            needs_retrieval=True,
            needs_tutoring=True
        )
        
        try:
            # Ejecutar workflow
            result = await self.workflow.ainvoke(initial_state)
            return result.get("final_response", "Lo siento, no pude procesar tu solicitud.")
            
        except Exception as e:
            print(f"Error en workflow: {e}")
            return f"Ha ocurrido un error en VectorMentor: {str(e)}"
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        try:
            vector_stats = self.vector_manager.get_collection_stats()
            
            return {
                "agents_active": len(self.agents),
                "llm_model": settings.LLM_MODEL,
                "rag_system": vector_stats,
                "student_progress": {
                    "total_interactions": len(self.agents["coordinator"].conversation_history),
                    "current_level": self.agents["coordinator"].session_context.get("student_level", 3),
                    "average_level": 3.0,  # Calcular dinámicamente en implementación real
                    "most_studied_topic": self.agents["coordinator"].session_context.get("current_topic", "vectores"),
                    "progress_trend": "estable"
                }
            }
        except Exception as e:
            return {
                "agents_active": 0,
                "llm_model": "Error",
                "rag_system": {"count": 0, "status": f"error: {e}"},
                "student_progress": {
                    "total_interactions": 0,
                    "current_level": 3,
                    "average_level": 3.0,
                    "most_studied_topic": "vectores",
                    "progress_trend": "sin datos"
                }
            }
    
    def reset_conversation(self):
        """Reinicia la conversación"""
        for agent in self.agents.values():
            agent.conversation_history = []
        self.agents["coordinator"].session_context = {}
    
    def suggest_next_topic(self) -> str:
        """Sugiere el siguiente tema de estudio"""
        current_topic = self.agents["coordinator"].session_context.get("current_topic", "")
        level = self.agents["coordinator"].session_context.get("student_level", 3)
        
        suggestions = {
            "vectores": "¿Qué tal si exploramos el producto punto entre vectores?",
            "matrices": "Podrías aprender sobre determinantes de matrices",
            "sistemas": "Los métodos de eliminación gaussiana son muy útiles",
            "": "Te sugiero comenzar con conceptos básicos de vectores"
        }
        
        return suggestions.get(current_topic, "Continúa explorando los temas que más te interesen")