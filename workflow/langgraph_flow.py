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
        self.conversation_history = []  # ← AGREGADO: Historial centralizado
        self.student_progress = {       # ← AGREGADO: Progreso del estudiante
            "current_level": 3,
            "level_history": [],
            "topics_covered": set(),
            "total_interactions": 0
        }
        
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
        """Nodo del coordinador - MEJORADO"""
        try:
            # Preparar contexto con historial y progreso
            enhanced_context = {
                "student_input": state["student_input"],
                "conversation_history": self.conversation_history,
                "student_progress": self.student_progress,
                "interaction_type": self._detect_interaction_type(state["student_input"])
            }
            state["context"] = enhanced_context
            
            result = await self.agents["coordinator"].process(state)
            state.update(result)
            return state
        except Exception as e:
            print(f"Error en coordinador: {e}")
            state["final_response"] = "Error en el coordinador"
            return state
    
    async def _assessor_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del evaluador - MEJORADO CON EVALUACIÓN AUTOMÁTICA"""
        try:
            if state.get("needs_assessment", True):
                # Evaluar automáticamente el nivel
                assessment = await self.agents["assessor"].process(state)
                
                # Evaluar progreso si hay historial suficiente
                if len(self.conversation_history) > 0:
                    progress_eval = await self.agents["assessor"].evaluate_student_progress(
                        self.conversation_history
                    )
                    assessment["progress"] = progress_eval
                
                # ACTUALIZAR PROGRESO DEL ESTUDIANTE AUTOMÁTICAMENTE
                self._update_student_progress(assessment)
                
                state["assessment"] = assessment
                
                print(f"📊 Evaluación automática: Nivel {assessment.get('level', 3)} en {assessment.get('topic', 'algebra')}")
                
            return state
        except Exception as e:
            print(f"Error en evaluador: {e}")
            state["assessment"] = {"level": 3, "topic": "error"}
            return state
    
    async def _retriever_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del recuperador - ADAPTADO AL NIVEL"""
        try:
            if state.get("needs_retrieval", True):
                # Adaptar búsqueda según el nivel evaluado
                assessment = state.get("assessment", {})
                level = assessment.get("level", 3)
                topic = assessment.get("topic", "vectores")
                
                # Modificar contexto para búsqueda adaptada
                adapted_context = state["context"].copy()
                adapted_context["target_level"] = level
                adapted_context["specific_topic"] = topic
                
                result = await self.agents["retriever"].process({
                    **state,
                    "context": adapted_context
                })
                state.update(result)
                
                print(f"🔍 Contenido recuperado adaptado al nivel {level}")
                
            return state
        except Exception as e:
            print(f"Error en recuperador: {e}")
            state["retrieved_content"] = "Contenido no disponible"
            return state
    
    async def _tutor_node(self, state: WorkflowState) -> WorkflowState:
        """Nodo del tutor - RESPUESTA ADAPTADA AL NIVEL"""
        try:
            if state.get("needs_tutoring", True):
                # Adaptar respuesta según evaluación automática
                assessment = state.get("assessment", {})
                level = assessment.get("level", 3)
                gaps = assessment.get("gaps", [])
                
                # Preparar contexto adaptado para el tutor
                tutor_context = state["context"].copy()
                tutor_context.update({
                    "evaluated_level": level,
                    "knowledge_gaps": gaps,
                    "difficulty_adaptation": self._get_difficulty_adaptation(level),
                    "student_progress": self.student_progress
                })
                
                result = await self.agents["tutor"].process({
                    **state,
                    "context": tutor_context
                })
                state.update(result)
                
                print(f"🎓 Respuesta tutorial adaptada al nivel {level}")
                
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
            
            # Agregar interacción al historial
            self._add_to_history(state)
            
            return state
        except Exception as e:
            print(f"Error en sintetizador: {e}")
            state["final_response"] = "Error sintetizando respuesta"
            return state
    
    def _detect_interaction_type(self, student_input: str) -> str:
        """Detecta el tipo de interacción del estudiante"""
        input_lower = student_input.lower()
        
        if any(word in input_lower for word in ["qué es", "define", "definición", "concepto"]):
            return "definition_request"
        elif any(word in input_lower for word in ["cómo", "pasos", "procedimiento", "método"]):
            return "procedure_request"
        elif any(word in input_lower for word in ["ejemplo", "ejemplos", "muestra", "demuestra"]):
            return "examples_request"
        elif any(word in input_lower for word in ["calcula", "resuelve", "encuentra"]):
            return "calculation_request"
        elif "?" in student_input:
            return "question"
        else:
            return "statement"
    
    def _update_student_progress(self, assessment: Dict[str, Any]):
        """NUEVO: Actualiza automáticamente el progreso del estudiante"""
        level = assessment.get("level", 3)
        topic = assessment.get("topic", "algebra")
        
        # Actualizar nivel actual
        self.student_progress["current_level"] = level
        
        # Agregar al historial de niveles
        self.student_progress["level_history"].append(level)
        
        # Agregar tema estudiado
        self.student_progress["topics_covered"].add(topic)
        
        # Incrementar interacciones
        self.student_progress["total_interactions"] += 1
        
        # Calcular tendencia (últimas 3 interacciones)
        recent_levels = self.student_progress["level_history"][-3:]
        if len(recent_levels) >= 2:
            avg_recent = sum(recent_levels) / len(recent_levels)
            if len(self.student_progress["level_history"]) >= 4:
                prev_levels = self.student_progress["level_history"][-6:-3]
                avg_prev = sum(prev_levels) / len(prev_levels) if prev_levels else avg_recent
                
                if avg_recent > avg_prev + 0.3:
                    trend = "mejorando"
                elif avg_recent < avg_prev - 0.3:
                    trend = "declinando" 
                else:
                    trend = "estable"
            else:
                trend = "evaluando"
        else:
            trend = "inicial"
            
        self.student_progress["trend"] = trend
        
        print(f"📈 Progreso actualizado: Nivel {level}, Tendencia: {trend}")
    
    def _get_difficulty_adaptation(self, level: int) -> Dict[str, str]:
        """NUEVO: Obtiene adaptaciones de dificultad según el nivel"""
        adaptations = {
            1: {
                "complexity": "muy_basico",
                "vocabulary": "simple_y_claro",
                "examples": "concretos_y_visuales",
                "pace": "lento_y_detallado"
            },
            2: {
                "complexity": "basico",
                "vocabulary": "matematico_basico",
                "examples": "paso_a_paso",
                "pace": "moderado"
            },
            3: {
                "complexity": "intermedio",
                "vocabulary": "matematico_estandar",
                "examples": "aplicaciones_practicas",
                "pace": "normal"
            },
            4: {
                "complexity": "avanzado",
                "vocabulary": "tecnico",
                "examples": "casos_complejos",
                "pace": "rapido"
            },
            5: {
                "complexity": "muy_avanzado",
                "vocabulary": "especializado",
                "examples": "abstractos_y_teoricos",
                "pace": "muy_rapido"
            }
        }
        
        return adaptations.get(level, adaptations[3])
    
    def _add_to_history(self, state: WorkflowState):
        """Agrega la interacción al historial"""
        self.conversation_history.append({
            "student_input": state["student_input"],
            "assessment": state.get("assessment", {}),
            "final_response": state.get("final_response", ""),
            "timestamp": "now"  # En implementación real usar datetime
        })
        
        # Limitar historial a últimas 20 interacciones
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    async def process_student_input(self, student_input: str) -> Dict[str, Any]:
        """Procesa input del estudiante a través del workflow - MEJORADO"""
        
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
            
            # RETORNAR RESPUESTA COMPLETA CON EVALUACIÓN
            return {
                "response": result.get("final_response", "Lo siento, no pude procesar tu solicitud."),
                "assessment": result.get("assessment", {"level": 3, "topic": "algebra"}),
                "practice_exercise": result.get("practice_exercise", ""),
                "mode": "workflow_complete",
                "student_progress": self.student_progress.copy()
            }
            
        except Exception as e:
            print(f"Error en workflow: {e}")
            return {
                "response": f"Ha ocurrido un error en VectorMentor: {str(e)}",
                "assessment": {"level": 3, "topic": "error"},
                "practice_exercise": "",
                "mode": "error"
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema - MEJORADO CON DATOS REALES"""
        try:
            vector_stats = self.vector_manager.get_collection_stats()
            
            # Calcular estadísticas reales del progreso
            avg_level = (sum(self.student_progress["level_history"]) / 
                        len(self.student_progress["level_history"])) if self.student_progress["level_history"] else 3.0
            
            most_studied = max(self.student_progress["topics_covered"], 
                             key=lambda x: x, default="vectores") if self.student_progress["topics_covered"] else "vectores"
            
            return {
                "agents_active": len(self.agents),
                "llm_model": settings.LLM_MODEL,
                "rag_system": vector_stats,
                "student_progress": {
                    "total_interactions": self.student_progress["total_interactions"],
                    "current_level": self.student_progress["current_level"],
                    "average_level": round(avg_level, 1),
                    "most_studied_topic": most_studied,
                    "progress_trend": self.student_progress.get("trend", "inicial"),
                    "topics_covered": len(self.student_progress["topics_covered"]),
                    "level_distribution": self._get_level_distribution()
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
    
    def _get_level_distribution(self) -> Dict[str, int]:
        """Calcula distribución de niveles en el historial"""
        if not self.student_progress["level_history"]:
            return {}
        
        from collections import Counter
        distribution = Counter(self.student_progress["level_history"])
        return dict(distribution)
    
    def reset_conversation(self):
        """Reinicia la conversación y progreso"""
        self.conversation_history = []
        self.student_progress = {
            "current_level": 3,
            "level_history": [],
            "topics_covered": set(),
            "total_interactions": 0
        }
        
        for agent in self.agents.values():
            if hasattr(agent, 'conversation_history'):
                agent.conversation_history = []
        
        if "coordinator" in self.agents:
            self.agents["coordinator"].session_context = {}
    
    def suggest_next_topic(self) -> str:
        """Sugiere el siguiente tema de estudio - BASADO EN PROGRESO REAL"""
        current_level = self.student_progress["current_level"]
        topics_covered = self.student_progress["topics_covered"]
        
        # Sugerencias por nivel
        level_suggestions = {
            1: ["vectores", "operaciones_basicas", "magnitud_vectores"],
            2: ["producto_punto", "matrices", "operaciones_basicas"],
            3: ["multiplicacion_matrices", "determinantes", "sistemas_lineales"],
            4: ["matriz_inversa", "espacios_vectoriales", "transformaciones"],
            5: ["eigenvalores", "diagonalizacion", "formas_cuadraticas"]
        }
        
        suggested_topics = level_suggestions.get(current_level, level_suggestions[3])
        
        # Filtrar temas ya cubiertos
        new_topics = [topic for topic in suggested_topics if topic not in topics_covered]
        
        if new_topics:
            return f"Te sugiero explorar: {new_topics[0].replace('_', ' ')}"
        else:
            return "¡Excelente progreso! Podrías avanzar al siguiente nivel de dificultad"