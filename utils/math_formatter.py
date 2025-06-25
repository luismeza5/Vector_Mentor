"""Formateador de matemáticas para mejorar la visualización en CLI"""

import re

class MathFormatter:
    """Formatea matemáticas para mejor visualización en consola"""
    
    @staticmethod
    def format_for_cli(text: str) -> str:
        """Convierte LaTeX y formato matemático para CLI"""
        
        # Limpiar LaTeX básico
        text = re.sub(r'\\\((.*?)\\\)', r'\1', text)  # \(...\) → ...
        text = re.sub(r'\\\[(.*?)\\\]', r'\1', text, flags=re.DOTALL)  # \[...\] → ...
        text = re.sub(r'\$\$(.*?)\$\$', r'\1', text, flags=re.DOTALL)  # $$...$$ → ...
        text = re.sub(r'\$(.*?)\$', r'\1', text)  # $...$ → ...
        
        # Convertir matrices LaTeX a formato legible
        text = re.sub(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}', 
                     MathFormatter._format_matrix, text, flags=re.DOTALL)
        
        # Limpiar comandos LaTeX comunes
        text = re.sub(r'\\times', '×', text)
        text = re.sub(r'\\cdot', '·', text)
        text = re.sub(r'\\quad', '   ', text)
        text = re.sub(r'\\\\', '\n', text)
        text = re.sub(r'\\&', '  ', text)
        
        # Limpiar subíndices/superíndices
        text = re.sub(r'_\{([^}]+)\}', r'_\1', text)
        text = re.sub(r'\^\{([^}]+)\}', r'^\1', text)
        
        # Limpiar comandos de formato
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
        
        # Limpiar espacios extra y líneas vacías
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'  +', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def _format_matrix(match):
        """Formatea una matriz LaTeX para CLI"""
        content = match.group(1)
        
        # Dividir por filas (\\)
        rows = content.split('\\\\')
        
        formatted_rows = []
        for row in rows:
            if row.strip():
                # Dividir por columnas (&)
                cols = [col.strip() for col in row.split('&')]
                formatted_row = '  '.join(cols)
                formatted_rows.append(f"│ {formatted_row} │")
        
        if formatted_rows:
            return '\n' + '\n'.join(formatted_rows) + '\n'
        return content

class CLIRenderer:
    """Renderizador mejorado para la interfaz CLI"""
    
    @staticmethod
    def render_response(response: str) -> str:
        """Renderiza la respuesta con formato mejorado para CLI"""
        
        # Formatear matemáticas
        formatted = MathFormatter.format_for_cli(response)
        
        # Mejorar bullets y numeración
        formatted = re.sub(r'^\* ', '• ', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^\d+\.\s+\*\*([^*]+)\*\*', r'\1:', formatted, flags=re.MULTILINE)
        
        # Mejorar títulos
        formatted = re.sub(r'\*\*([^*]+)\*\*', r'\n📌 \1\n', formatted)
        
        # Agregar separadores visuales
        sections = formatted.split('\n📌')
        if len(sections) > 1:
            formatted_sections = []
            for i, section in enumerate(sections):
                if i == 0 and section.strip():
                    formatted_sections.append(section)
                elif section.strip():
                    formatted_sections.append(f"📌{section}")
            
            formatted = '\n\n'.join(formatted_sections)
        
        return formatted

def improve_cli_display():
    """Mejora la visualización en CLI"""
    
    # Configurar encoding para Windows
    import sys
    import os
    
    if os.name == 'nt':  # Windows
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass
    
    # Configurar colores básicos si es posible
    try:
        import colorama
        colorama.init()
        return True
    except ImportError:
        return False

# Función para usar en main.py
def format_tutor_response(response: str) -> str:
    """Función principal para formatear respuestas del tutor"""
    renderer = CLIRenderer()
    return renderer.render_response(response)

# Test de ejemplo
if __name__ == "__main__":
    test_response = """**🤖 VectorMentor:**1. **Definición clara y precisa:** El producto matricial es una operación que se realiza entre dos matrices para obtener una nueva matriz. Para que esto sea posible, el número de columnas de la primera matriz debe ser igual al número de filas de la segunda matriz.
1. **Explicación del concepto:** Imagina que cada matriz representa un conjunto de datos o transformaciones. Al multiplicar matrices, estamos combinando estas transformaciones. Cada elemento de la matriz resultante se obtiene multiplicando los elementos de una fila de la primera matriz por los elementos de una columna de la segunda matriz y sumando los resultados.
2. **Ejemplo numérico específico:** Supongamos que tenemos las siguientes matrices:
[ A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}, \\quad B = \\begin{pmatrix} 5 & 6 \\\\ 7 & 8 \\end{pmatrix} ]
Para calcular el producto ( C = A \\times B ):
   * Elemento ( C_{11} ) (fila 1, columna 1): [ C_{11} = (1 \\times 5) + (2 \\times 7) = 5 + 14 = 19 ]
   * Elemento ( C_{12} ) (fila 1, columna 2): [ C_{12} = (1 \\times 6) + (2 \\times 8) = 6 + 16 = 22 ]"""
    
    print("ANTES:")
    print(test_response[:200] + "...")
    print("\nDESPUÉS:")
    formatted = format_tutor_response(test_response)
    print(formatted[:300] + "...")