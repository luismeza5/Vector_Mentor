"""Agente Evaluador - Analiza el nivel y comprensión del estudiante - CORREGIDO"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.settings import settings

class AssessorAgent(BaseAgent):
    """Agente que evalúa el nivel de comprensión del estudiante"""
    
    def __init__(self, llm):
        super().__init__("assessor", llm)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa el nivel del estudiante y identifica gaps de conocimiento"""
        
        context = input_data.get("context", {})
        student_input = context.get("student_input", "")
        interaction_type = context.get("interaction_type", "question")
        conversation_history = context.get("conversation_history", [])
        
        # Determinar el tema principal ESPECÍFICO
        topic = await self._identify_specific_topic(student_input)
        
        # Evaluar nivel según el tipo de interacción
        if interaction_type == "answer":
            assessment = await self._assess_answer(student_input, topic, conversation_history)
        elif interaction_type in ["question", "examples_request", "procedure_request"]:
            assessment = await self._assess_question(student_input, topic)
        else:
            assessment = await self._initial_assessment(student_input, topic)
        
        # Identificar gaps de conocimiento
        knowledge_gaps = await self._identify_knowledge_gaps(student_input, topic, assessment)
        
        # Sugerir siguiente paso
        next_step = await self._suggest_next_step(assessment, knowledge_gaps, topic)
        
        return {
            "level": assessment["level"],
            "topic": topic,
            "subtopics": assessment.get("subtopics", []),
            "gaps": knowledge_gaps,
            "strengths": assessment.get("strengths", []),
            "next_step": next_step,
            "confidence": assessment.get("confidence", 0.7)
        }
    
    async def _identify_specific_topic(self, student_input: str) -> str:
        """Identifica el tema específico de la pregunta"""
        
        # Búsqueda por palabras clave específicas
        input_lower = student_input.lower()
        
        # Mapeo específico de palabras clave a temas
        keyword_mapping = {
            "producto de matrices": "multiplicacion_matrices",
            "multiplicacion de matrices": "multiplicacion_matrices", 
            "multiplicar matrices": "multiplicacion_matrices",
            "producto matriz": "multiplicacion_matrices",
            "producto punto": "producto_punto",
            "producto escalar": "producto_punto",
            "dot product": "producto_punto",
            "determinante": "determinantes",
            "det": "determinantes",
            "matriz inversa": "matriz_inversa",
            "inversa": "matriz_inversa",
            "transpuesta": "matriz_transpuesta",
            "vector": "vectores",
            "vectores": "vectores",
            "matriz": "matrices",
            "matrices": "matrices",
            "sistema": "sistemas_lineales",
            "ecuaciones": "sistemas_lineales",
            "lineal": "sistemas_lineales",
            "suma": "operaciones_basicas",
            "resta": "operaciones_basicas",
            "magnitud": "magnitud_vectores",
            "norma": "magnitud_vectores",
            "unitario": "vectores_unitarios",
            "ortogonal": "ortogonalidad",
            "perpendicular": "ortogonalidad",
            "base": "espacios_vectoriales",
            "dimension": "espacios_vectoriales",
            "independencia": "independencia_lineal"
        }
        
        # Buscar coincidencias específicas
        for keyword, topic in keyword_mapping.items():
            if keyword in input_lower:
                return topic
        
        # Si no encuentra coincidencia específica, usar LLM
        prompt = f"""
        Identifica el tema ESPECÍFICO de álgebra lineal en esta pregunta:
        
        Pregunta: "{student_input}"
        
        Temas específicos posibles:
        - multiplicacion_matrices (producto de matrices)
        - producto_punto (producto escalar entre vectores)
        - determinantes (cálculo de determinantes)
        - matriz_inversa (matriz inversa)
        - vectores (conceptos básicos de vectores)
        - matrices (conceptos básicos de matrices)
        - sistemas_lineales (sistemas de ecuaciones)
        - operaciones_basicas (suma, resta)
        - magnitud_vectores (norma, longitud)
        - ortogonalidad (perpendicular, ortogonal)
        - espacios_vectoriales (base, dimensión)
        
        Responde SOLO con el nombre del tema específico.
        """
        
        topic = await self.generate_response(prompt)
        return topic.strip().lower()
    
    async def _assess_question(self, student_question: str, topic: str) -> Dict[str, Any]:
        """Evalúa el nivel basado en la pregunta del estudiante"""
        
        prompt = f"""
        Evalúa el nivel de esta pregunta sobre {topic}:
        
        Pregunta: "{student_question}"
        
        Criterios de nivel (1-5):
        1 = Pregunta muy básica ("¿qué es?")
        2 = Pregunta sobre definiciones y conceptos básicos  
        3 = Pregunta sobre procedimientos y cálculos
        4 = Pregunta sobre aplicaciones y propiedades
        5 = Pregunta sobre teoría avanzada y demostraciones
        
        Responde en formato JSON:
        {{
            "level": [1-5],
            "subtopics": ["subtema"],
            "strengths": ["fortaleza identificada"],
            "confidence": [0.0-1.0]
        }}
        """
        
        response = await self.generate_response(prompt)
        return self._parse_json_response(response)
    
    async def _assess_answer(self, student_answer: str, topic: str, history: List) -> Dict[str, Any]:
        """Evalúa la respuesta del estudiante a un ejercicio"""
        
        # Buscar la pregunta original en el historial
        original_question = ""
        for i, msg in enumerate(reversed(history)):
            if msg.get("role") == "assistant" and ("?" in msg.get("content", "") or "calcula" in msg.get("content", "").lower()):
                original_question = msg.get("content", "")
                break
        
        prompt = f"""
        Evalúa esta respuesta sobre {topic}:
        
        Pregunta original: "{original_question}"
        Respuesta del estudiante: "{student_answer}"
        
        Evalúa en escala 1-5:
        1 = Respuesta incorrecta, conceptos mal entendidos
        2 = Respuesta parcialmente incorrecta
        3 = Respuesta correcta con errores menores
        4 = Respuesta correcta y bien explicada
        5 = Respuesta excelente con comprensión profunda
        
        Responde en formato JSON:
        {{
            "level": [1-5],
            "subtopics": ["subtema"],
            "strengths": ["lo que hizo bien"],
            "errors": ["errores específicos"],
            "confidence": [0.0-1.0]
        }}
        """
        
        response = await self.generate_response(prompt)
        return self._parse_json_response(response)
    
    async def _initial_assessment(self, student_input: str, topic: str) -> Dict[str, Any]:
        """Evaluación inicial para saludos o inputs generales"""
        
        return {
            "level": 3,  # Nivel medio por defecto
            "subtopics": [topic],
            "strengths": [],
            "confidence": 0.5
        }
    
    async def _identify_knowledge_gaps(self, student_input: str, topic: str, assessment: Dict) -> List[str]:
        """Identifica gaps específicos de conocimiento"""
        
        level = assessment.get("level", 3)
        if level >= 4:
            return []  # Nivel alto, pocos gaps
        
        # Gaps específicos por tema
        topic_gaps = {
            "multiplicacion_matrices": [
                "condición de compatibilidad para multiplicación",
                "cálculo elemento a elemento",
                "interpretación del resultado"
            ],
            "producto_punto": [
                "fórmula del producto punto", 
                "interpretación geométrica",
                "relación con ángulos"
            ],
            "vectores": [
                "representación de vectores",
                "operaciones básicas",
                "magnitud y dirección"
            ],
            "matrices": [
                "notación matricial",
                "tipos de matrices",
                "operaciones básicas"
            ]
        }
        
        return topic_gaps.get(topic, ["conceptos fundamentales"])[:2]
    
    async def _suggest_next_step(self, assessment: Dict, gaps: List[str], topic: str) -> str:
        """Sugiere el siguiente paso en el aprendizaje"""
        
        level = assessment.get("level", 3)
        
        if level <= 2:
            return f"Repasar conceptos básicos de {topic}"
        elif level == 3:
            return f"Practicar ejercicios de {topic}"
        elif level == 4:
            return f"Explorar aplicaciones de {topic}"
        else:
            return f"Profundizar en teoría de {topic}"
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parsea respuesta JSON del LLM"""
        try:
            import json
            # Buscar el JSON en la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback si no se puede parsear
        return {
            "level": 3,
            "subtopics": [],
            "strengths": [],
            "confidence": 0.5
        }