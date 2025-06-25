"""Test del flujo completo de VectorMentor"""

import sys
import os
import asyncio

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_complete_workflow():
    """Test del flujo completo de trabajo"""
    print("🔬 Probando flujo completo de VectorMentor...")
    
    try:
        from workflow.langgraph_flow import VectorMentorWorkflow
        from config import settings
        
        # Verificar API key
        print(f"🔑 API Key configurada: {len(settings.OPENAI_API_KEY)} caracteres")
        
        # Inicializar workflow
        print("🚀 Inicializando VectorMentorWorkflow...")
        workflow = VectorMentorWorkflow()
        
        # Test 1: Saludo inicial
        print("\n👋 Test 1: Saludo inicial")
        greeting = await workflow.get_greeting()
        print(f"✅ Saludo: {greeting[:100]}...")
        
        # Test 2: Pregunta sobre vectores
        print("\n❓ Test 2: Pregunta sobre vectores")
        question = "¿Qué es un vector?"
        result = await workflow.process_student_input(question)
        print(f"✅ Respuesta generada: {len(result['response'])} caracteres")
        print(f"✅ Nivel evaluado: {result['assessment'].get('level', 'N/A')}")
        print(f"✅ Tema identificado: {result['assessment'].get('topic', 'N/A')}")
        
        # Test 3: Estadísticas del sistema
        print("\n📊 Test 3: Estadísticas del sistema")
        stats = workflow.get_system_stats()
        print(f"✅ Documentos RAG: {stats['rag_system']['count']}")
        print(f"✅ Interacciones: {stats['student_progress']['total_interactions']}")
        print(f"✅ Agentes activos: {stats['agents_active']}")
        
        # Test 4: Progreso del estudiante
        print("\n📈 Test 4: Progreso del estudiante")
        progress = workflow.get_student_progress()
        print(f"✅ Nivel promedio: {progress.get('average_level', 'N/A')}")
        print(f"✅ Tema más estudiado: {progress.get('most_studied_topic', 'N/A')}")
        
        print("\n🎯 ¡Flujo completo funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())