"""
VectorMentor - Sistema Multiagente con RAG para Tutoría Académica
Archivo principal de ejecución - CORREGIDO
"""

import sys
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from knowledge_base.content_loader import ContentLoader
from rag.vector_store import VectorStoreManager
from workflow.langgraph_flow import VectorMentorWorkflow
from utils.logging_config import setup_logging

async def initialize_system():
    """Inicializa todos los componentes del sistema"""
    print("🚀 Inicializando VectorMentor...")
    
    # Configurar logging si existe
    try:
        setup_logging()
    except ImportError:
        print("⚠️ Logging config no disponible, continuando...")
    
    # Cargar contenido educativo (método sincrónico)
    print("📚 Cargando contenido educativo...")
    content_loader = ContentLoader()
    content_loader.load_all_content()  # Sin await
    
    # Inicializar base vectorial (método sincrónico)
    print("🔍 Verificando base vectorial...")
    vector_manager = VectorStoreManager()
    stats = vector_manager.get_collection_stats()
    print(f"📊 Base vectorial: {stats['count']} documentos - {stats['status']}")
    
    # Crear workflow
    print("🤖 Configurando agentes y workflow...")
    workflow = VectorMentorWorkflow()
    await workflow.initialize()
    
    print("✅ VectorMentor inicializado correctamente!")
    return workflow

def main():
    """Función principal"""
    print("🎓 VectorMentor - Tu tutor de álgebra lineal")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Modo consola
        asyncio.run(run_cli_mode())
    else:
        # Modo interfaz web (por defecto)
        asyncio.run(run_web_mode())

async def run_cli_mode():
    """Ejecuta el sistema en modo consola"""
    try:
        # Importar formateador de matemáticas
        from utils.math_formatter import format_tutor_response, improve_cli_display
        
        # Mejorar display CLI
        improve_cli_display()
        
        workflow = await initialize_system()
        
        print("\n💬 Modo consola activado. Escribe 'quit' para salir.\n")
        print("Ejemplos de preguntas:")
        print("- ¿Qué es un vector?")
        print("- ¿Cómo se calcula el producto punto?")
        print("- Explícame la suma de matrices")
        print("- ¿Qué es el producto de matrices?")
        print("- Dame ejemplos del determinante")
        print()
        
        while True:
            try:
                user_input = input("🧑‍🎓 Tú: ")
                if user_input.lower() in ['quit', 'exit', 'salir', 'q']:
                    break
                    
                if not user_input.strip():
                    continue
                
                print("🤖 VectorMentor: Procesando...")
                response = await workflow.process_student_input(user_input)
                
                # Formatear la respuesta para mejor visualización
                formatted_response = format_tutor_response(response)
                print(f"🤖 VectorMentor:\n{formatted_response}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Intenta con otra pregunta.\n")
        
        print("👋 ¡Hasta luego! Sigue estudiando álgebra lineal.")
        
    except Exception as e:
        print(f"❌ Error inicializando VectorMentor: {e}")
        print("Verifica tu configuración y conexión a internet.")

async def run_web_mode():
    """Ejecuta el sistema con interfaz web"""
    try:
        workflow = await initialize_system()
        
        print(f"🌐 Iniciando interfaz web...")
        print(f"📍 URL: http://{settings.STREAMLIT_HOST}:{settings.STREAMLIT_PORT}")
        print("💡 Usa Ctrl+C para detener el servidor")
        
        # Configurar Streamlit
        import streamlit as st
        
        # Almacenar workflow en session_state si no existe
        if 'workflow' not in st.session_state:
            st.session_state.workflow = workflow
        
        # Ejecutar Streamlit
        import subprocess
        import os
        
        # Obtener el path al archivo de streamlit
        streamlit_file = Path(__file__).parent / "interface" / "streamlit_app.py"
        
        # Ejecutar streamlit run
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_file),
            "--server.port", str(settings.STREAMLIT_PORT),
            "--server.address", settings.STREAMLIT_HOST,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error en modo web: {e}")
        print("Intenta el modo consola: python main.py --cli")

def run_streamlit_app():
    """Función auxiliar para ejecutar streamlit (llamada desde streamlit_app.py)"""
    # Esta función es llamada desde streamlit_app.py
    # No necesita hacer nada especial aquí
    pass

if __name__ == "__main__":
    main()