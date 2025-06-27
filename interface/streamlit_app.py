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
from typing import Dict, Any
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
    # NUEVO: Seguimiento del progreso del estudiante
    if 'student_progress' not in st.session_state:
        st.session_state.student_progress = {
            "level_history": [],
            "current_level": 3,
            "topics_covered": set(),
            "total_interactions": 0,
            "trend": "inicial"
        }

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
        
        st.success("VectorMentor inicializado correctamente")
        return workflow
        
    except Exception as e:
        st.error(f"❌ Error inicializando VectorMentor: {e}")
        return None
def display_chat_message(message, is_user=True, assessment=None):
    """Función mejorada para mostrar mensajes con evaluación automática"""
    import re
    
    if is_user:
        st.markdown(f"🧑‍🎓 **Tú:** {message}")
    else:
        st.markdown("🤖 **VectorMentor:**")
        
        # MOSTRAR EVALUACIÓN AUTOMÁTICA SI EXISTE
        if assessment and assessment.get("level"):
            level = assessment["level"]
            topic = assessment.get("topic", "algebra").replace("_", " ").title()
            reasoning = assessment.get("reasoning", "")
            
            # Mostrar métricas de evaluación
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Nivel Evaluado", f"{level}/5")
            with col2:
                st.metric("📚 Tema", topic)
            with col3:
                if "adaptation" in assessment:
                    complexity = assessment["adaptation"].get("complexity", "").replace("_", " ").title()
                    st.metric("🎯 Complejidad", complexity)
            
            # Mostrar explicación de la evaluación
            if reasoning:
                st.info(f"🔍 {reasoning}")
        
        # APLICAR LIMPIEZA MATEMÁTICA
        cleaned_message = clean_math_formatting(message)
        
        # SEPARAR TEXTO Y MATEMÁTICAS
        parts = re.split(r'(\$\$[^$]+\$\$|\$[^$]+\$)', cleaned_message)
        
        for part in parts:
            if part.strip():
                if part.startswith('$$') and part.endswith('$$'):
                    # Matemática en bloque
                    latex_content = part[2:-2].strip()
                    try:
                        st.latex(latex_content)
                    except:
                        st.code(f"Fórmula: {latex_content}")
                elif part.startswith('$') and part.endswith('$'):
                    # Matemática en línea - usar markdown con HTML
                    latex_content = part[1:-1].strip()
                    try:
                        st.markdown(f"${latex_content}$", unsafe_allow_html=True)
                    except:
                        st.markdown(f"`{latex_content}`")
                else:
                    # Texto normal
                    st.markdown(part)
    
    st.markdown("---")

def clean_math_formatting(text):
    """Versión mejorada de limpieza matemática"""
    import re
    
    # 1. Convertir LaTeX de paréntesis a dólares
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    # 2. Convertir paréntesis con matemáticas simples
    text = re.sub(r'\(\s*([A-Z])\s*=\s*\(([^)]+)\)\s*\)', r'$\1 = (\2)$', text)
    
    # 3. Arreglar vectores en negrita
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'\\mathbf{\1}', text)
    
    # 4. Limpiar espacios en matemáticas
    text = re.sub(r'\$\s+', '$', text)
    text = re.sub(r'\s+\$', '$', text)
    
    # 5. Convertir matrices mal formateadas
    text = re.sub(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', 
                  lambda m: f'\\begin{{pmatrix}}{m.group(1).strip()}\\end{{pmatrix}}', 
                  text, flags=re.DOTALL)
    
    return text

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
    """Procesa preguntas de álgebra lineal usando OpenAI CON EVALUACIÓN AUTOMÁTICA"""
    try:
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # EVALUACIÓN AUTOMÁTICA DEL NIVEL
        evaluated_level = evaluate_simple_level(user_input)
        difficulty_adaptation = get_difficulty_prompt(evaluated_level)
        response_style = adapt_response_to_level(evaluated_level, "algebra_lineal")
        
        # Preparar contexto
        context = ""
        if results:
            context = "\n\n".join([doc.page_content for doc in results[:2]])
        
        # Prompt adaptado al nivel evaluado automáticamente
        system_prompt = f"""Eres VectorMentor, un tutor experto en álgebra lineal.

CONTEXTO de la base de conocimientos:
{context}

EVALUACIÓN AUTOMÁTICA DEL ESTUDIANTE:
- Nivel detectado: {evaluated_level}/5
- Adaptación requerida: {difficulty_adaptation}
- Estilo de respuesta: {response_style['complexity']}
- Vocabulario: {response_style['vocabulary']}
- Tipo de ejemplos: {response_style['examples']}

INSTRUCCIONES DE ADAPTACIÓN:
{difficulty_adaptation}

FORMATO MATEMÁTICO OBLIGATORIO:
- SIEMPRE usa $...$ para matemáticas
- Variables: $\\mathbf{{u}}$, $\\mathbf{{v}}$, $A$, $B$
- Vectores: $\\mathbf{{u}} = (u_{{1}}, u_{{2}}, u_{{3}})$
- Matrices: $\\begin{{pmatrix}} a & b \\\\ c & d \\end{{pmatrix}}$
- Producto cruz: $\\mathbf{{u}} \\times \\mathbf{{v}}$
- NUNCA uses **texto**, [ ], o símbolos raros

REGLAS:
1. TODA expresión matemática en $...$
2. Adapta la complejidad al nivel {evaluated_level}
3. Usa el vocabulario apropiado para el nivel
4. Incluye ejemplos del tipo: {response_style['examples']}

Proporciona una explicación adaptada al nivel del estudiante."""

        # Llamada a OpenAI con prompt adaptado
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
        
        # Generar ejercicio de práctica adaptado al nivel
        practice_exercise = generate_practice_exercise(evaluated_level, user_input)
        
        return {
            "response": ai_response,
            "assessment": {
                "level": evaluated_level, 
                "topic": "algebra_lineal",
                "reasoning": f"Evaluación automática: nivel {evaluated_level} basado en tipo de pregunta",
                "adaptation": response_style
            },
            "practice_exercise": practice_exercise,
            "mode": "ai_enhanced_with_auto_eval"
        }
        
    except Exception as e:
        # Fallback con nivel por defecto
        print(f"Error en evaluación automática: {e}")
        if results:
            best_doc = results[0]
            return {
                "response": f"""**📚 Información sobre: "{user_input}"**\n\n{best_doc.page_content}\n\n*Sistema funcionando en modo local*""",
                "assessment": {"level": 3, "topic": "local_fallback", "reasoning": "Fallback - nivel por defecto"},
                "practice_exercise": "",
                "mode": "local_fallback"
            }
        else:
            return _create_error_response(str(e))

def generate_practice_exercise(level: int, user_input: str) -> str:
    """Genera ejercicio de práctica adaptado al nivel"""
    
    level_exercises = {
        1: "Ejercicio básico: Identifica cuáles de los siguientes son vectores: (2,3), 5, (-1,4,2)",
        2: "Ejercicio: Calcula la suma de los vectores (1,2) y (3,4)",
        3: "Ejercicio: Encuentra el producto punto de $\\mathbf{u} = (2,1,3)$ y $\\mathbf{v} = (1,4,2)$",
        4: "Ejercicio avanzado: Determina si los vectores (1,2,3), (4,5,6) y (7,8,9) son linealmente independientes",
        5: "Ejercicio experto: Demuestra que el producto cruz es anticonmutativo"
    }
    
    # Adaptar ejercicio al contenido de la pregunta
    input_lower = user_input.lower()
    if "vector" in input_lower and level <= 2:
        return level_exercises.get(level, level_exercises[3])
    elif "matriz" in input_lower:
        return f"Ejercicio de matrices (nivel {level}): Practica con operaciones matriciales básicas"
    else:
        return level_exercises.get(level, level_exercises[3])

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

def evaluate_simple_level(user_input: str) -> int:
    """Evaluación automática simple basada en palabras clave"""
    input_lower = user_input.lower()
    
    # Nivel 1: Preguntas muy básicas
    if any(word in input_lower for word in ["qué es", "definición", "define", "concepto", "significa"]):
        return 1
    
    # Nivel 5: Preguntas avanzadas
    elif any(word in input_lower for word in ["demostrar", "probar", "eigenvalor", "diagonalizar", "transformación lineal"]):
        return 5
    
    # Nivel 4: Preguntas complejas
    elif any(word in input_lower for word in ["transformación", "inversa", "rango", "nulidad", "determinante"]):
        return 4
    
    # Nivel 2: Preguntas básicas con cálculo
    elif any(word in input_lower for word in ["calcular", "resolver", "encontrar", "ejemplo", "pasos"]):
        return 2
    
    # Nivel 3: Intermedio por defecto
    else:
        return 3

def get_difficulty_prompt(level: int) -> str:
    """Obtiene prompt de adaptación según nivel"""
    prompts = {
        1: "Usa vocabulario muy simple, explica conceptos básicos paso a paso con analogías cotidianas",
        2: "Incluye ejemplos concretos y cálculos básicos paso a paso",
        3: "Nivel intermedio, incluye aplicaciones y ejemplos prácticos",
        4: "Nivel avanzado, usa terminología técnica y conceptos complejos",
        5: "Nivel experto, incluye teoría profunda y demostraciones matemáticas"
    }
    return prompts.get(level, prompts[3])

def adapt_response_to_level(level: int, topic: str) -> Dict[str, str]:
    """Adapta el estilo de respuesta según el nivel"""
    adaptations = {
        1: {
            "complexity": "muy_basico",
            "vocabulary": "cotidiano_y_simple",
            "examples": "visuales_y_concretos",
            "detail": "paso_a_paso_detallado"
        },
        2: {
            "complexity": "basico",
            "vocabulary": "matematico_simple",
            "examples": "numericos_basicos",
            "detail": "explicacion_clara"
        },
        3: {
            "complexity": "intermedio",
            "vocabulary": "matematico_estandar",
            "examples": "aplicaciones_practicas",
            "detail": "balance_teoria_practica"
        },
        4: {
            "complexity": "avanzado",
            "vocabulary": "tecnico_especializado",
            "examples": "casos_complejos",
            "detail": "enfoque_conceptual"
        },
        5: {
            "complexity": "muy_avanzado",
            "vocabulary": "altamente_especializado",
            "examples": "abstractos_y_teoricos",
            "detail": "demostraciones_rigurosas"
        }
    }
    
    return adaptations.get(level, adaptations[3])

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

                if st.session_state.student_progress['total_interactions'] > 0:
                    progress = st.session_state.student_progress
                    
                    # Calcular promedio real
                    avg_level = sum(progress['level_history']) / len(progress['level_history']) if progress['level_history'] else 3.0
                    
                    st.markdown("### 📈 Tu Progreso Real")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Nivel Actual", f"{progress['current_level']}/5")
                        st.metric("Interacciones", progress['total_interactions'])
                    
                    with col2:
                        st.metric("Nivel Promedio", f"{avg_level:.1f}")
                        st.metric("Tendencia", progress['trend'].title())
                    
                    # Gráfico simple de progreso
                    if len(progress['level_history']) > 1:
                        st.line_chart(progress['level_history'])
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
            display_chat_message(entry["response"], is_user=False, assessment=entry.get("assessment"))
            
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