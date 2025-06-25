"""
VectorMentor - Interfaz Streamlit
Sistema de Tutoría Inteligente en Álgebra Lineal
"""

import streamlit as st
import sys
import os
import re
import asyncio
from utils.math_formatter import format_tutor_response
# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# Configuración de la página
st.set_page_config(
    page_title="VectorMentor",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar CSS personalizado
def load_css():
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stats-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .exercise-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
      },
      svg: {
        fontCache: 'global'
      }
    };
    </script>
    """, unsafe_allow_html=True)



# Inicializar estado de la sesión
def initialize_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

# Función para inicializar el sistema VectorMentor
@st.cache_resource
def initialize_vectormentor():
    """Inicializa VectorMentor (se ejecuta solo una vez)"""
    try:
        from config import settings
        
        # Verificar configuración
        if not settings.OPENAI_API_KEY:
            st.warning("⚠️ API Key de OpenAI no configurada. Funcionando en modo demo.")
            return None
        
        # Importar y crear workflow
        from workflow.langgraph_flow import VectorMentorWorkflow
        workflow = VectorMentorWorkflow()
        
        # Inicializar el workflow asíncronamente
        asyncio.run(workflow.initialize())
        
        st.success("✅ VectorMentor inicializado correctamente")
        return workflow
        
    except Exception as e:
        st.error(f"❌ Error inicializando VectorMentor: {e}")
        return None

def clean_math_formatting(text):
    """Limpia el formato matemático de la respuesta del AI"""
    import re
    
    # Convertir LaTeX a formato Streamlit/MathJax
    # Paréntesis LaTeX a $...$
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    # Ya está en $...$ format, mantenerlo
    # Mejorar matrices
    text = re.sub(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', 
                  r'\\begin{pmatrix}\1\\end{pmatrix}', text, flags=re.DOTALL)
    
    # Arreglar formato de matrices simples: separar elementos con &
    text = re.sub(r'u_1 \\cdot v_1', r'u_1 \cdot v_1', text)
    text = re.sub(r'u_2 \\cdot v_2', r'u_2 \cdot v_2', text)
    
    # Limpiar variables en cursiva
    text = re.sub(r'\( ([uv]) \)', r'$\1$', text)
    text = re.sub(r'\( ([uv])_([0-9]) \)', r'$\1_{\2}$', text)
    
    # Mejorar subíndices y productos punto
    text = re.sub(r'([uv])_([0-9])', r'\1_{\2}', text)
    text = re.sub(r'\\cdot', r'\cdot', text)
    
    # Limpiar formato de ecuaciones en líneas independientes
    text = re.sub(r'\[ ([^]]+) \]', r'$$\1$$', text)
    
    # Convertir vectores con paréntesis
    text = re.sub(r'\( ([uv]) = \(([^)]+)\) \)', r'$\1 = (\2)$', text)
    
    # Títulos en negrita 
    text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)
    
    return text

# REEMPLAZAR las funciones en streamlit_app.py con esta solución robusta:
# REEMPLAZA COMPLETAMENTE estas funciones en streamlit_app.py:

def format_for_latex_blocks(text):
    """Prepara el texto para usar con st.latex - VERSIÓN FINAL CORREGIDA"""
    import re
    
    # 1. Arreglar títulos numerados CON asteriscos
    text = re.sub(r'\*\*(\d+)\.\s*([^*]+?):\*\*', r'\n### \1. \2\n', text)
    text = re.sub(r'\*\*(\d+)\.\s*([^*]+?)\*\*', r'\n### \1. \2\n', text)
    
    # 2. Convertir matemáticas en paréntesis simples
    text = re.sub(r'\\\(([^)]+?)\\\)', r'$$\1$$', text)  # \(...\) → $$...$$
    text = re.sub(r'\(\\mathbf\{([^}]+)\}\s*=\s*\(([^)]+)\)\)', r'$$\\mathbf{\1} = (\2)$$', text)
    
    # 3. Arreglar matemáticas mal formateadas con \$$ 
    text = re.sub(r'\\?\$\$([^$]+?)\\?\$\$', r'$$\1$$', text)
    
    # 4. Convertir componentes de vectores
    text = re.sub(r'Vector ([AB]) = \(([^)]+)\)', r'$$\\mathbf{\1} = (\2)$$', text)
    
    # 5. Limpiar dobles asteriscos restantes en títulos
    text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)
    
    # 6. Limpiar espacios extra y líneas múltiples
    text = re.sub(r'\n\s*\n\s*\n', r'\n\n', text)
    
    return text

def clean_all_latex(text):
    """Convierte TODOS los comandos LaTeX a texto legible"""
    import re
    
    # 1. Limpiar mathbf (vectores en negrita)
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', text)
    
    # 2. Limpiar símbolos matemáticos
    text = text.replace('\\cdot', '·')
    text = text.replace('\\times', '×')
    text = text.replace('\\pm', '±')
    text = text.replace('\\div', '÷')
    
    # 3. Limpiar subíndices y superíndices
    text = re.sub(r'([a-zA-Z])_\{([^}]+)\}', r'\1_\2', text)
    text = re.sub(r'([a-zA-Z])\^\{([^}]+)\}', r'\1^\2', text)
    text = re.sub(r'([a-zA-Z])_([0-9])', r'\1_\2', text)
    
    # 4. Limpiar fracciones
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
    
    # 5. Limpiar raíces
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
    
    # 6. Limpiar paréntesis LaTeX
    text = re.sub(r'\\left\(', '(', text)
    text = re.sub(r'\\right\)', ')', text)
    text = re.sub(r'\\left\[', '[', text)
    text = re.sub(r'\\right\]', ']', text)
    
    # 7. Limpiar espacios LaTeX
    text = text.replace('\\quad', '   ')
    text = text.replace('\\qquad', '     ')
    text = text.replace('\\,', ' ')
    
    # 8. Limpiar matrices (convertir a formato simple)
    text = re.sub(r'\\begin\{pmatrix\}([^}]+?)\\end\{pmatrix\}', 
                  lambda m: '\n' + m.group(1).replace('&', '  ').replace('\\\\', '\n') + '\n', 
                  text, flags=re.DOTALL)
    
    # 9. Limpiar comandos restantes
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # 10. Limpiar paréntesis de variables sueltos
    text = re.sub(r'\(\s*([A-Z])\s*\)', r'**\1**', text)
    
    return text

def clean_all_latex_aggressive(text):
    """Limpia AGRESIVAMENTE todo el LaTeX - NO deja nada"""
    import re
    
    # 1. Limpiar entornos matemáticos completos
    text = re.sub(r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}', '', text, flags=re.DOTALL)
    
    # 2. Limpiar vmatrix, pmatrix, etc (matrices)
    text = re.sub(r'\\?vmatrix([^\\]*?)\\?vmatrix', r'|\1|', text)
    text = re.sub(r'vmatrix\s+([^\\]+)\s*\\?\*?', r'|\1|', text)
    text = re.sub(r'\\begin\{vmatrix\}', '|', text)
    text = re.sub(r'\\end\{vmatrix\}', '|', text)
    
    # 3. Limpiar símbolos de matriz (&, \\)
    text = text.replace(' & ', ' ')
    text = text.replace('&', ' ')
    text = text.replace('\\\\', ' ')
    text = text.replace('\\ ', ' ')
    
    # 4. Limpiar comandos con llaves
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    
    # 5. Limpiar comandos sin llaves
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # 6. Limpiar símbolos matemáticos comunes
    replacements = {
        '\\cdot': '·',
        '\\times': '×',
        '\\pm': '±',
        '\\div': '÷',
        '\\sum': 'Σ',
        '\\prod': 'Π',
        '\\int': '∫',
        '\\partial': '∂',
        '\\infty': '∞',
        '\\alpha': 'α',
        '\\beta': 'β',
        '\\gamma': 'γ',
        '\\delta': 'δ',
        '\\pi': 'π',
        '\\theta': 'θ',
        '\\lambda': 'λ',
        '\\mu': 'μ',
        '\\sigma': 'σ',
        '\\omega': 'ω'
    }
    
    for latex, symbol in replacements.items():
        text = text.replace(latex, symbol)
    
    # 7. Limpiar subíndices y superíndices
    text = re.sub(r'([a-zA-Z])_\{([^}]+)\}', r'\1_\2', text)
    text = re.sub(r'([a-zA-Z])_([0-9]+)', r'\1_\2', text)
    text = re.sub(r'([a-zA-Z])\^\{([^}]+)\}', r'\1^\2', text)
    
    # 8. Limpiar paréntesis LaTeX
    text = text.replace('\\left(', '(')
    text = text.replace('\\right)', ')')
    text = text.replace('\\left[', '[')
    text = text.replace('\\right]', ']')
    text = text.replace('\\left|', '|')
    text = text.replace('\\right|', '|')
    
    # 9. Limpiar espacios múltiples y caracteres raros
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\\\*', '', text)
    text = re.sub(r'\\', '', text)
    
    # 10. Limpiar variables en paréntesis
    text = re.sub(r'\(\s*([A-Z])\s*\)', r'**\1**', text)
    
    return text.strip()

def display_chat_message(message, is_user=True):
    if is_user:
        st.write(f"🧑‍🎓 Tú: {message}")
    else:
        st.write("🤖 VectorMentor:")
        st.write(message)
    st.write("---")
# FUNCIÓN DE PRUEBA específica para tu ejemplo:
def test_cross_product():
    """Prueba con el ejemplo del producto cruz"""
    
    st.markdown("## 🧪 Test: Producto cruz")
    
    test_message = """**1. Definición**: El producto cruz de dos vectores.

[ **A** × **B** = \\begin{vmatrix} i & j & k \\\\ 1 & 2 & 3 \\\\ 4 & 5 & 6 \\end{vmatrix} ]

**2. Resultado**: El vector resultante es perpendicular a ambos."""
    
    st.markdown("### Antes de limpiar:")
    st.code(test_message)
    
    st.markdown("### Después de limpiar:")
    display_chat_message(test_message, is_user=False)

# FUNCIÓN DE PRUEBA ESPECÍFICA para el problema actual
def test_vector_subtraction():
    """Prueba específica con resta de vectores"""
    
    st.markdown("## 🧪 Test: Resta de vectores")
    
    test_response = """**1. Definición clara y precisa**: La resta de vectores consiste en tomar un vector y quitarle otro vector.

**2. Ejemplo numérico específico**:
* Vector A = (5, 3)
* Vector B = (2, 1)
* A - B = (3, 2)

**Ejercicio de práctica:**
Dado el vector (\\mathbf{A} = (3, 4)) y el vector (\\mathbf{B} = (1, 2)):

1. Para la suma: \\$$ \\mathbf{A} + \\mathbf{B} = (3 + 1, 4 + 2) = (4, 6) \\$$
2. Para la resta: \\$$ \\mathbf{A} - \\mathbf{B} = (3 - 1, 4 - 2) = (2, 2) \\$$"""
    
    st.markdown("### Input original:")
    st.code(test_response)
    
    st.markdown("### Output procesado:")
    display_chat_message(test_response, is_user=False)

# FUNCIÓN DE PRUEBA RÁPIDA - Agregar también
def test_quick_latex():
    """Prueba rápida del renderizado"""
    
    st.markdown("## 🧪 Prueba rápida")
    
    test_text = """**1. Ejemplo simple:**

[ A = \\begin{pmatrix} 1 & 2 \\ 3 & 4 \\end{pmatrix} ]

Texto normal aquí.

[ B = \\begin{pmatrix} 5 & 6 \\ 7 & 8 \\end{pmatrix} ]

**2. Resultado:**

[ A + B = \\begin{pmatrix} 6 & 8 \\ 10 & 12 \\end{pmatrix} ]"""
    
    st.markdown("### Input original:")
    st.code(test_text)
    
    st.markdown("### Output procesado:")
    display_chat_message(test_text, is_user=False)

def process_user_input(workflow, user_input):
    """Procesa el input del usuario a través del workflow"""
    try:
        from rag.vector_store import VectorStoreManager
        rag = VectorStoreManager()
        
        if workflow is None:
            # Usar búsqueda vectorial
            results = rag.similarity_search(user_input, k=3)
            
            # Verificar relevancia
            algebra_keywords = [
                'vector', 'vectores', 'magnitud', 'dirección', 'componentes', 'coordenadas',
                'ortogonal', 'perpendicular', 'paralelo', 'unitario', 'normalizar',
                'matriz', 'matrices', 'determinante', 'determinantes', 'transpuesta',
                'inversa', 'diagonal', 'identidad', 'simétrica', 'antisimétrica',
                'sistema', 'ecuaciones', 'lineales', 'cramer', 'gauss', 'gaussiana',
                'eliminación', 'sustitución', 'reducción', 'escalonada', 'pivote',
                'suma', 'multiplicación', 'producto', 'punto', 'escalar', 'cruz',
                'combinación', 'lineal', 'transformación', 'proyección',
                'espacio', 'vectorial', 'base', 'bases', 'dimensión', 'independencia',
                'dependencia', 'generador', 'subespacio', 'kernel', 'nulo',
                'algebra', 'lineal', 'matemáticas', 'geometría', 'analítica',
                'ángulo', 'distancia', 'norma', 'métrica'
            ]
            
            user_words = user_input.lower().split()
            is_algebra_related = any(word in algebra_keywords for word in user_words)
            
            if is_algebra_related:
                return _process_algebra_question(user_input, results)
            else:
                return _process_off_topic_question(user_input)
        else:
            # Workflow completo
            result = asyncio.run(workflow.process_student_input(user_input))
            return result
            
    except Exception as e:
        return _create_error_response(str(e))

def _process_algebra_question(user_input, results):
    """Procesa preguntas de álgebra lineal usando OpenAI"""
    try:
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Preparar contexto
        context = ""
        if results:
            context = "\n\n".join([doc.page_content for doc in results[:2]])
        
        # Prompt unificado
        system_prompt = f"""Eres VectorMentor, un tutor experto en álgebra lineal.

CONTEXTO de la base de conocimientos:
{context}

FORMATO MATEMÁTICO OBLIGATORIO:
- SIEMPRE usa $...$ para matemáticas
- Variables: $\\mathbf{{u}}$, $\\mathbf{{v}}$, $A$, $B$
- Vectores: $\\mathbf{{u}} = (u_{{1}}, u_{{2}}, u_{{3}})$
- Matrices: $\\begin{{pmatrix}} a & b \\\\ c & d \\end{{pmatrix}}$
- Producto cruz: $\\mathbf{{u}} \\times \\mathbf{{v}}$
- NUNCA uses **texto**, [ ], o símbolos raros

REGLAS:
1. TODA expresión matemática en $...$
2. Subíndices con llaves: $u_{{1}}$
3. Matrices bien formateadas con & y \\\\

Proporciona explicaciones claras con ejemplos numéricos."""

        # Llamada unificada a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        ai_response = response.choices[0].message.content
        ai_response = clean_math_formatting(ai_response)
        
        return {
            "response": ai_response,
            "assessment": {"level": 3, "topic": "algebra_lineal"},
            "practice_exercise": "",
            "mode": "ai_enhanced"
        }
        
    except Exception as e:
        # Fallback al RAG local
        if results:
            best_doc = results[0]
            return {
                "response": f"""**📚 Información sobre: "{user_input}"**\n\n{best_doc.page_content}\n\n*Sistema funcionando en modo local*""",
                "assessment": {"level": 2, "topic": "local_fallback"},
                "practice_exercise": "",
                "mode": "local_fallback"
            }
        else:
            return _create_error_response(str(e))

def _process_off_topic_question(user_input):
    """Maneja preguntas no relacionadas con álgebra lineal"""
    return {
        "response": f"""**🤖 Lo siento, soy VectorMentor** - especializado únicamente en **álgebra lineal**.

**Puedo ayudarte con:**
- 📐 **Vectores**: definición, operaciones, magnitud
- 🔢 **Matrices**: suma, multiplicación, determinantes
- 🎯 **Producto punto**: cálculo, interpretación
- 📊 **Espacios vectoriales**: bases, dimensión

¿Te gustaría hacer una pregunta sobre álgebra lineal?""",
        "assessment": {"level": 1, "topic": "off_topic"},
        "practice_exercise": "",
        "mode": "off_topic"
    }

def _create_error_response(error_msg):
    """Crea respuesta de error estándar"""
    return {
        "response": f"""Ocurrió un error procesando tu consulta.

Puedo ayudarte con:
- **Vectores y operaciones**
- **Matrices y sistemas lineales**
- **Producto punto y ortogonalidad**

*Error: {error_msg}*""",
        "assessment": {"level": 3, "topic": "error"},
        "practice_exercise": "",
        "mode": "error"
    }

# Función principal de la interfaz
def main():
    """Función principal de la aplicación"""
    
    # Cargar CSS y inicializar
    load_css()
    initialize_session_state()
    
    # Header principal
    st.markdown('<h1 class="main-header">📐 VectorMentor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Tu tutor inteligente especializado en Álgebra Lineal</p>', unsafe_allow_html=True)
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.header("🎯 Estado del Sistema")
        
        # Inicializar VectorMentor
        if not st.session_state.system_initialized:
            with st.spinner("Inicializando VectorMentor..."):
                st.session_state.workflow = initialize_vectormentor()
                st.session_state.system_initialized = True
        
        # Mostrar estado
        if st.session_state.workflow:
            st.success("✅ Sistema completo activo")
            
            # Estadísticas del sistema
            try:
                stats = st.session_state.workflow.get_system_stats()
                st.markdown("### 📊 Estadísticas")
                st.markdown(f"""
                <div class="stats-box">
                <strong>📚 Base de conocimientos:</strong> {stats['rag_system']['count']} documentos<br>
                <strong>🤖 Agentes activos:</strong> {stats['agents_active']}<br>
                <strong>🧠 Modelo LLM:</strong> {stats['llm_model']}<br>
                <strong>💬 Interacciones:</strong> {stats['student_progress']['total_interactions']}
                </div>
                """, unsafe_allow_html=True)
                
                # Progreso del estudiante
                if stats['student_progress']['total_interactions'] > 0:
                    progress = stats['student_progress']
                    st.markdown("### 📈 Tu Progreso")
                    st.markdown(f"""
                    <div class="stats-box">
                    <strong>Nivel actual:</strong> {progress['current_level']}/5<br>
                    <strong>Nivel promedio:</strong> {progress['average_level']:.1f}<br>
                    <strong>Tema principal:</strong> {progress['most_studied_topic']}<br>
                    <strong>Tendencia:</strong> {progress['progress_trend']}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.info(f"Estadísticas no disponibles: {e}")
        else:
            st.warning("⚠️ Modo demo activo")
            st.info("Sistema funcionando con búsqueda básica")
        
        # Controles
        st.markdown("### ⚙️ Controles")
        if st.button("🔄 Reiniciar conversación"):
            st.session_state.conversation_history = []
            if st.session_state.workflow:
                st.session_state.workflow.reset_conversation()
            st.rerun()
        
        if st.button("📋 Sugerir siguiente tema"):
            if st.session_state.workflow:
                try:
                    suggestion = st.session_state.workflow.suggest_next_topic()
                    st.info(suggestion)
                except:
                    st.info("Sugerencia no disponible")
            else:
                suggestions = [
                    "Intenta preguntarme sobre vectores",
                    "¿Qué tal si exploramos las matrices?", 
                    "El producto punto es muy útil",
                    "Los sistemas lineales son fundamentales"
                ]
                import random
                st.info(random.choice(suggestions))
    
    # Área principal de chat
    st.header("💬 Conversación")
    
    # Mostrar historial de conversación
    if st.session_state.conversation_history:
        for entry in st.session_state.conversation_history:
            display_chat_message(entry["user_input"], is_user=True)
            display_chat_message(entry["response"], is_user=False)
            
            # Mostrar ejercicio de práctica si existe
            if entry.get("practice_exercise"):
                st.markdown(f"""
                <div class="exercise-box">
                <strong>📝 Ejercicio de práctica:</strong><br>
                {entry["practice_exercise"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        # Mensaje de bienvenida
        welcome_msg = """
        ¡Hola! Soy **VectorMentor**, tu tutor inteligente especializado en álgebra lineal. 
        
        Puedo ayudarte con:
        - 📐 **Vectores**: definición, operaciones, magnitud, dirección
        - 🔢 **Matrices**: operaciones, determinantes, sistemas lineales  
        - 📊 **Producto punto**: cálculo, interpretación geométrica
        - 🎯 **Espacios vectoriales**: bases, dimensión, independencia lineal
        
        ¿Qué te gustaría aprender hoy?
        """
        display_chat_message(welcome_msg, is_user=False)
    
    # Input del usuario
    with st.form("user_input_form", clear_on_submit=True):
        user_input = st.text_area(
            "Tu pregunta:",
            placeholder="Ejemplo: ¿Qué es un vector? ¿Cómo se calcula el producto punto?",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submit_button = st.form_submit_button("💬 Enviar")
        with col2:
            example_button = st.form_submit_button("💡 Ejemplo")
    
    # Procesar input
    if submit_button and user_input.strip():
        with st.spinner("🤔 Pensando..."):
            # Procesar input del usuario
            result = process_user_input(st.session_state.workflow, user_input)
            
            # Verificar si result es una corrutina y ejecutarla
            if hasattr(result, '__await__'):
                result = asyncio.run(result)
            
            # VERIFICAR SI RESULT ES UN STRING (del workflow completo)
            if isinstance(result, str):
                # El workflow retornó solo un string, convertir al formato esperado
                result = {
                    "response": result,
                    "assessment": {"level": 3, "topic": "workflow_complete"},
                    "practice_exercise": "",
                    "mode": "workflow"
                }
            
            # Verificar que result sea un diccionario válido
            if not isinstance(result, dict) or "response" not in result:
                result = {
                    "response": "Error procesando la respuesta. Por favor, intenta de nuevo.",
                    "assessment": {"level": 3, "topic": "error"},
                    "practice_exercise": "",
                    "mode": "error"
                }
            
            # Agregar a historial
            st.session_state.conversation_history.append({
                "user_input": user_input,
                "response": result["response"],
                "assessment": result.get("assessment", {}),
                "practice_exercise": result.get("practice_exercise", "")
            })
            
            st.rerun()
    
    # Botón de ejemplo
    if example_button:
        examples = [
            "¿Qué es un vector?",
            "¿Cómo se calcula el producto punto de dos vectores?",
            "Explícame la suma de matrices",
            "¿Cuál es la diferencia entre un vector y un escalar?",
            "¿Cómo resuelvo un sistema de ecuaciones lineales?"
        ]
        import random
        example_question = random.choice(examples)
        
        with st.spinner("🤔 Procesando ejemplo..."):
            result = process_user_input(st.session_state.workflow, example_question)
            
            # Verificar si result es una corrutina y ejecutarla
            if hasattr(result, '__await__'):
                result = asyncio.run(result)
            
            # VERIFICAR SI RESULT ES UN STRING (del workflow completo)
            if isinstance(result, str):
                # El workflow retornó solo un string, convertir al formato esperado
                result = {
                    "response": result,
                    "assessment": {"level": 3, "topic": "workflow_complete"},
                    "practice_exercise": "",
                    "mode": "workflow"
                }
            
            # Verificar que result sea un diccionario válido
            if not isinstance(result, dict) or "response" not in result:
                result = {
                    "response": "Error procesando la respuesta. Por favor, intenta de nuevo.",
                    "assessment": {"level": 3, "topic": "error"},
                    "practice_exercise": "",
                    "mode": "error"
                }
            
            st.session_state.conversation_history.append({
                "user_input": f"💡 {example_question}",
                "response": result["response"],
                "assessment": result.get("assessment", {}),
                "practice_exercise": result.get("practice_exercise", "")
            })
            
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #888;">VectorMentor - Desarrollado para el aprendizaje de álgebra lineal</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()