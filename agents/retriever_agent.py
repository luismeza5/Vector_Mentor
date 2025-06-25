"""Agente Recuperador - Implementa RAG para recuperar contenido educativo - CORREGIDO"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.settings import settings

class RetrieverAgent(BaseAgent):
    """Agente que recupera contenido usando RAG"""
    
    def __init__(self, llm, vector_store_manager):
        super().__init__("retriever", llm)
        self.vector_store = vector_store_manager
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recupera contenido relevante usando RAG"""
        
        context = input_data.get("context", {})
        assessment = input_data.get("assessment", {})
        
        student_input = context.get("student_input", "")
        student_level = assessment.get("level", 3)
        topic = assessment.get("topic", "")
        
        # Construir query para recuperación
        search_query = await self._build_search_query(student_input, topic, student_level)
        
        # Recuperar contenido de la base vectorial (SIN await - es método sincrónico)
        retrieved_docs = self.vector_store.similarity_search(
            query=search_query,
            k=settings.RETRIEVAL_TOP_K,
            filter_level=student_level
        )
        
        # Procesar y filtrar contenido recuperado
        processed_content = await self._process_retrieved_content(retrieved_docs, assessment)
        
        return {
            "retrieved_content": processed_content,
            "source_documents": retrieved_docs,
            "search_query": search_query
        }
    
    async def _build_search_query(self, student_input: str, topic: str, level: int) -> str:
        """Construye una query optimizada para la búsqueda vectorial"""
        
        prompt = f"""
        Basándote en el input del estudiante, genera una query de búsqueda optimizada 
        para encontrar contenido educativo relevante:
        
        Input del estudiante: "{student_input}"
        Tema identificado: "{topic}"
        Nivel del estudiante: {level}/5
        
        Genera una query de búsqueda que capture los conceptos clave.
        Responde solo con la query de búsqueda, sin explicaciones adicionales.
        """
        
        try:
            search_query = await self.generate_response(prompt)
            return search_query.strip()
        except Exception as e:
            print(f"Error generando query: {e}")
            # Fallback: usar input original o tema
            return topic if topic else student_input
    
    async def _process_retrieved_content(self, documents: List, assessment: Dict) -> str:
        """Procesa y filtra el contenido recuperado"""
        
        if not documents:
            return "No se encontró contenido específico para tu consulta."
        
        # Combinar contenido de documentos (máximo 3 para evitar sobrecarga)
        combined_content = "\n\n".join([doc.page_content for doc in documents[:3]])
        
        prompt = f"""
        Procesa el siguiente contenido educativo recuperado y adáptalo para un estudiante 
        de nivel {assessment.get('level', 3)}/5:
        
        Contenido recuperado:
        {combined_content}
        
        Procesa el contenido para:
        1. Mantener solo la información más relevante
        2. Adaptar el lenguaje al nivel del estudiante
        3. Estructurar la información de manera clara
        4. Incluir ejemplos si están disponibles
        
        Proporciona un resumen educativo bien estructurado.
        """
        
        try:
            processed = await self.generate_response(prompt)
            return processed
        except Exception as e:
            print(f"Error procesando contenido: {e}")
            # Fallback: devolver contenido sin procesar
            return combined_content[:500] + "..." if len(combined_content) > 500 else combined_content
    
    def get_available_topics(self) -> List[str]:
        """Obtiene lista de temas disponibles en la base vectorial"""
        try:
            topics_summary = self.vector_store.get_topics_summary()
            return list(topics_summary.keys())
        except:
            return ["vectores", "matrices", "sistemas", "espacios_vectoriales"]
    
    async def search_specific_topic(self, topic: str, level: int = 3) -> List:
        """Busca contenido específico de un tema"""
        try:
            # Usar método sincrónico sin await
            docs = self.vector_store.search_by_topic(topic, level=level, k=3)
            return docs
        except Exception as e:
            print(f"Error buscando tema {topic}: {e}")
            return []
    
    async def add_context_from_conversation(self, conversation_history: List[Dict]) -> str:
        """Agrega contexto basado en la conversación previa"""
        if not conversation_history:
            return ""
        
        # Obtener últimos mensajes relevantes
        recent_messages = conversation_history[-3:]  # Últimos 3 mensajes
        
        context_text = ""
        for msg in recent_messages:
            if msg.get("role") == "user":
                context_text += f"Estudiante: {msg.get('content', '')}\n"
            elif msg.get("role") == "assistant":
                context_text += f"Tutor: {msg.get('content', '')}\n"
        
        return context_text
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de recuperación"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            topics = self.get_available_topics()
            
            return {
                "total_documents": vector_stats.get("count", 0),
                "available_topics": topics,
                "status": vector_stats.get("status", "unknown"),
                "retrieval_k": settings.RETRIEVAL_TOP_K
            }
        except Exception as e:
            return {
                "total_documents": 0,
                "available_topics": [],
                "status": f"error: {e}",
                "retrieval_k": settings.RETRIEVAL_TOP_K
            }