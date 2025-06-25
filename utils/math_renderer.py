"""Renderizador de matemáticas mejorado para Streamlit"""

import re
import streamlit as st

def render_math_content(text: str) -> str:
    """Convierte matemáticas LaTeX para renderizado en Streamlit"""
    
    # Convertir matrices LaTeX a formato MathJax
    text = re.sub(
        r'\[ ([AB]) = \\begin\{pmatrix\} ([^}]+) \\end\{pmatrix\} \]',
        r'$$\1 = \begin{pmatrix} \2 \end{pmatrix}$$',
        text
    )
    
    # Convertir ecuaciones en línea
    text = re.sub(r'\[ ([^]]+) \]', r'$$\1$$', text)
    
    # Convertir variables en paréntesis a matemáticas
    text = re.sub(r'\(([A-Z])\)', r'$\1$', text)
    text = re.sub(r'\(([A-Z])_\{([^}]+)\}\)', r'$\1_{{\2}}$', text)
    
    # Arreglar matrices específicas
    text = re.sub(
        r'([0-9]+) & ([0-9]+) \\ ([0-9]+) & ([0-9]+)',
        r'\1 & \2 \\\\ \3 & \4',
        text
    )
    
    # Limpiar espacios en matemáticas
    text = re.sub(r'\$\s+([^$]+)\s+\$', r'$\1$', text)
    
    return text

def display_formatted_response(response: str):
    """Muestra la respuesta con matemáticas bien formateadas"""
    
    # Renderizar matemáticas
    formatted_response = render_math_content(response)
    
    # Dividir en secciones para mejor visualización
    sections = formatted_response.split('\n\n')
    
    for section in sections:
        if section.strip():
            # Detectar si es un título
            if section.startswith('###') or '**' in section[:50]:
                st.markdown(section)
            # Detectar si contiene matemáticas
            elif '$$' in section or '$' in section:
                st.markdown(section)
                # Forzar re-renderizado
                st.markdown('<script>if(window.MathJax)MathJax.typesetPromise();</script>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(section)

def create_math_example_display():
    """Crea una demostración de cómo debería verse"""
    
    st.markdown("### 📐 Ejemplo de producto de matrices:")
    
    st.markdown(r"""
    **Matrices a multiplicar:**
    
    $$A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}, \quad B = \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}$$
    
    **Cálculo elemento por elemento:**
    
    - $C_{11} = (1 \cdot 5) + (2 \cdot 7) = 5 + 14 = 19$
    - $C_{12} = (1 \cdot 6) + (2 \cdot 8) = 6 + 16 = 22$
    - $C_{21} = (3 \cdot 5) + (4 \cdot 7) = 15 + 28 = 43$
    - $C_{22} = (3 \cdot 6) + (4 \cdot 8) = 18 + 32 = 50$
    
    **Resultado:**
    
    $$C = A \times B = \begin{pmatrix} 19 & 22 \\ 43 & 50 \end{pmatrix}$$
    """)

# Función mejorada para el chat
def display_enhanced_chat_message(message, is_user=True):
    """Muestra mensaje con matemáticas mejoradas"""
    
    css_class = "user-message" if is_user else "assistant-message"
    icon = "🧑‍🎓" if is_user else "🤖"
    role = "Tú" if is_user else "VectorMentor"
    
    # Crear contenedor
    with st.container():
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {role}:</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if not is_user:
            # Para respuestas del tutor, usar renderizado matemático mejorado
            display_formatted_response(message)
        else:
            # Para mensajes del usuario, mostrar normal
            st.markdown(message)

if __name__ == "__main__":
    # Test del renderizado
    st.title("🧪 Test del renderizador de matemáticas")
    
    create_math_example_display()
    
    test_response = """
    ### 1. Definición clara y precisa
    El **producto matricial** es una operación que toma dos matrices y produce otra matriz.
    
    ### 3. Ejemplo numérico específico
    [ A = \\begin{pmatrix} 1 & 2 \\ 3 & 4 \\end{pmatrix} ]
    
    [ B = \\begin{pmatrix} 5 & 6 \\ 7 & 8 \\end{pmatrix} ]
    
    Para calcular (C = A \\times B):
    
    [ C_{11} = (1 \\cdot 5) + (2 \\cdot 7) = 5 + 14 = 19 ]
    """
    
    st.markdown("### Respuesta formateada:")
    display_formatted_response(test_response)