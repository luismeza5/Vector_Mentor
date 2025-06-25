"""Agente Tutor - Genera respuestas educativas personalizadas - CORREGIDO PARA RESPUESTAS ESPECÍFICAS"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.settings import settings

class TutorAgent(BaseAgent):
    """Agente que genera respuestas educativas adaptadas al estudiante"""
    
    def __init__(self, llm):
        super().__init__("tutor", llm)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera respuesta educativa personalizada"""
        
        context = input_data.get("context", {})
        assessment = input_data.get("assessment", {})
        retrieved_content = input_data.get("retrieved_content", "")
        
        student_input = context.get("student_input", "")
        interaction_type = context.get("interaction_type", "question")
        student_level = assessment.get("level", 3)
        topic = assessment.get("topic", "")
        gaps = assessment.get("gaps", [])
        
        # Generar respuesta según el tipo de interacción
        if interaction_type == "greeting":
            response = await self._generate_greeting_response()
        elif interaction_type == "question":
            response = await self._generate_specific_question_response(
                student_input, student_level, topic, retrieved_content, gaps
            )
        elif interaction_type == "answer":
            response = await self._generate_feedback_response(
                student_input, assessment, retrieved_content
            )
        elif interaction_type == "explanation_request":
            response = await self._generate_explanation_response(
                student_input, student_level, topic, retrieved_content
            )
        else:
            response = await self._generate_specific_question_response(
                student_input, student_level, topic, retrieved_content, gaps
            )
        
        # Agregar ejercicio de práctica si es apropiado
        practice_exercise = await self._generate_practice_exercise(
            topic, student_level, interaction_type
        )
        
        return {
            "tutor_response": response,
            "practice_exercise": practice_exercise,
            "level_used": student_level,
            "topic_addressed": topic
        }
    
    async def _generate_specific_question_response(self, question: str, level: int, topic: str, 
                                                  content: str, gaps: List[str]) -> str:
        """Genera respuesta ESPECÍFICA y DIRECTA a la pregunta del estudiante"""
        
        # Analizar qué pregunta específicamente
        question_lower = question.lower()
        
        if "producto" in question_lower and "matrices" in question_lower:
            return await self._explain_matrix_multiplication(level, content)
        elif "ejemplos" in question_lower:
            return await self._provide_specific_examples(question, level, topic, content)
        elif "que es" in question_lower or "qué es" in question_lower:
            return await self._explain_concept_directly(question, level, content)
        elif "como" in question_lower or "cómo" in question_lower:
            return await self._explain_procedure(question, level, content)
        else:
            return await self._generate_direct_answer(question, level, topic, content)
    
    async def _explain_matrix_multiplication(self, level: int, content: str) -> str:
        """Explica específicamente el producto de matrices"""
        
        prompt = f"""
        Explica ESPECÍFICAMENTE el producto de matrices para un estudiante de nivel {level}/5.
        
        Contenido de referencia: {content}
        
        Tu explicación debe incluir:
        1. Definición clara del producto de matrices
        2. Condición necesaria (columnas de A = filas de B)
        3. Procedimiento paso a paso
        4. Ejemplo numérico concreto (matrices 2x2)
        5. Cálculo detallado de cada elemento
        
        NO des respuestas generales. Sé ESPECÍFICO y DIRECTO.
        Incluye SIEMPRE un ejemplo numérico completo.
        """
        
        return await self.generate_response(prompt)
    
    async def _provide_specific_examples(self, question: str, level: int, topic: str, content: str) -> str:
        """Proporciona ejemplos específicos y concretos"""
        
        prompt = f"""
        El estudiante pidió ejemplos sobre: "{question}"
        Tema: {topic}
        Nivel: {level}/5
        
        Proporciona 2-3 ejemplos CONCRETOS y NUMÉRICOS:
        
        1. Cada ejemplo debe tener números específicos
        2. Muestra el cálculo paso a paso
        3. Explica cada paso del proceso
        4. NO uses variables genéricas como "a, b, c"
        5. USA números reales como 2, 3, -1, etc.
        
        Contenido de referencia: {content}
        
        Sé ESPECÍFICO. El estudiante quiere ver cálculos reales.
        """
        
        return await self.generate_response(prompt)
    
    async def _explain_concept_directly(self, question: str, level: int, content: str) -> str:
        """Explica un concepto de manera directa"""
        
        prompt = f"""
        Pregunta específica: "{question}"
        Nivel del estudiante: {level}/5
        
        Responde DIRECTAMENTE a la pregunta con:
        1. Definición clara y precisa
        2. Explicación del concepto
        3. Ejemplo numérico específico
        4. Aplicación práctica
        
        Contenido de referencia: {content}
        
        NO des introducciones largas. Ve directo al punto.
        SIEMPRE incluye un ejemplo con números reales.
        """
        
        return await self.generate_response(prompt)
    
    async def _explain_procedure(self, question: str, level: int, content: str) -> str:
        """Explica cómo hacer algo paso a paso"""
        
        prompt = f"""
        Pregunta sobre procedimiento: "{question}"
        Nivel: {level}/5
        
        Explica el procedimiento paso a paso:
        1. Lista los pasos numerados
        2. Da un ejemplo numérico completo
        3. Muestra cada cálculo
        4. Explica el resultado
        
        Contenido de referencia: {content}
        
        Sé PRÁCTICO y ESPECÍFICO. El estudiante quiere saber CÓMO hacerlo.
        """
        
        return await self.generate_response(prompt)
    
    async def _generate_direct_answer(self, question: str, level: int, topic: str, content: str) -> str:
        """Genera respuesta directa para cualquier pregunta"""
        
        prompt = f"""
        Pregunta del estudiante: "{question}"
        Tema: {topic}
        Nivel: {level}/5
        
        Responde DIRECTAMENTE sin rodeos:
        
        1. Responde exactamente lo que preguntó
        2. Sé específico y concreto
        3. Incluye ejemplos numéricos
        4. Evita generalidades
        5. NO hagas introducciones largas
        
        Contenido de referencia: {content}
        
        IMPORTANTE: El estudiante quiere una respuesta ESPECÍFICA a su pregunta.
        """
        
        return await self.generate_response(prompt)
    
    async def _generate_greeting_response(self) -> str:
        """Genera respuesta de saludo"""
        
        prompt = """
        Genera un saludo breve y directo para VectorMentor.
        
        Debe ser:
        - Conciso (máximo 3 líneas)
        - Enfocado en álgebra lineal
        - Invitar a hacer preguntas específicas
        
        NO hagas introducciones largas.
        """
        
        return await self.generate_response(prompt)
    
    async def _generate_feedback_response(self, student_answer: str, assessment: Dict, 
                                        content: str) -> str:
        """Genera feedback sobre la respuesta del estudiante"""
        
        level = assessment.get("level", 3)
        errors = assessment.get("errors", [])
        strengths = assessment.get("strengths", [])
        
        prompt = f"""
        Proporciona feedback ESPECÍFICO sobre esta respuesta:
        
        Respuesta del estudiante: "{student_answer}"
        Nivel evaluado: {level}/5
        Fortalezas: {strengths}
        Errores: {errors}
        
        Tu feedback debe:
        1. Ser específico sobre qué está bien/mal
        2. Corregir errores con ejemplos
        3. Reforzar lo que hizo bien
        4. Dar sugerencias concretas
        
        Contenido de referencia: {content}
        
        Sé DIRECTO y CONSTRUCTIVO.
        """
        
        return await self.generate_response(prompt)
    
    async def _generate_explanation_response(self, request: str, level: int, topic: str, 
                                           content: str) -> str:
        """Genera explicación detallada de un concepto"""
        
        prompt = f"""
        Explica este concepto en detalle: "{request}"
        Tema: {topic}
        Nivel: {level}/5
        
        Tu explicación debe incluir:
        1. Definición clara
        2. Ejemplo numérico paso a paso
        3. Aplicación práctica
        4. Verificación del resultado
        
        Contenido de referencia: {content}
        
        Sé DETALLADO pero CLARO. Incluye cálculos específicos.
        """
        
        return await self.generate_response(prompt)
    
    async def _generate_practice_exercise(self, topic: str, level: int, 
                                        interaction_type: str) -> str:
        """Genera ejercicio de práctica relacionado con la pregunta"""
        
        # Solo generar ejercicios para preguntas, no para saludos
        if interaction_type in ["greeting", "answer"]:
            return ""
        
        # Generar ejercicio relacionado con el tema específico
        import random
        if random.random() > 0.4:  # 60% de probabilidad
            return ""
        
        prompt = f"""
        Genera un ejercicio de práctica específico sobre {topic} para nivel {level}/5.
        
        El ejercicio debe:
        1. Usar números específicos (no variables)
        2. Ser apropiado para el nivel
        3. Tener una solución clara
        4. Estar relacionado con la pregunta del estudiante
        
        Formato: "**Ejercicio de práctica:** [problema específico con números]"
        
        Si no es apropiado generar ejercicio, responde solo "".
        """
        
        response = await self.generate_response(prompt)
        return response.strip() if response.strip() != '""' else ""