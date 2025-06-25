"""Cargador de contenido educativo - CORREGIDO"""

import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from rag.vector_store import VectorStoreManager

class ContentLoader:
    """Carga y procesa contenido educativo para la base vectorial"""
    
    def __init__(self):
        self.content_dir = Path(__file__).parent / "data"
        self.vector_manager = None
        
    def load_all_content(self):
        """Carga todo el contenido educativo - MÉTODO SINCRÓNICO"""
        
        # Inicializar vector manager (sin await)
        self.vector_manager = VectorStoreManager()
        
        # Verificar si ya existe contenido
        if self._content_exists():
            print("✅ Contenido ya cargado en la base vectorial")
            return
        
        # Cargar contenido por categorías
        documents = []
        
        documents.extend(self._load_vectores_content())
        documents.extend(self._load_matrices_content())
        documents.extend(self._load_sistemas_content())
        documents.extend(self._load_ejercicios_content())
        documents.extend(self._load_advanced_content())
        
        # Agregar a la base vectorial (sin await)
        self.vector_manager.add_documents(documents)
        
        print(f"✅ Cargados {len(documents)} documentos educativos")
    
    def _content_exists(self) -> bool:
        """Verifica si ya existe contenido en la base vectorial"""
        try:
            if not self.vector_manager:
                return False
            results = self.vector_manager.similarity_search("vector", k=1)
            return len(results) > 0
        except:
            return False
    
    def _load_vectores_content(self) -> List[Document]:
        """Carga contenido sobre vectores"""
        
        documents = []
        
        # Definiciones básicas
        vectores_def = Document(
            page_content="""
            # Vectores en Álgebra Lineal
            
            ## Definición
            Un vector es una entidad matemática que tiene magnitud y dirección. En álgebra lineal, 
            trabajamos principalmente con vectores en espacios como R² y R³.
            
            ## Representación
            - En R²: v = (x, y) donde x e y son las componentes
            - En R³: v = (x, y, z) donde x, y, z son las componentes
            
            ## Interpretación Geométrica
            Un vector puede representar:
            - Un desplazamiento en el espacio
            - Una fuerza aplicada a un objeto
            - Una velocidad con dirección
            
            ## Ejemplo Básico
            El vector v = (3, 4) en R² representa un desplazamiento de 3 unidades 
            en x y 4 unidades en y.
            """,
            metadata={"topic": "vectores", "level": 1, "subtopic": "definicion"}
        )
        
        vectores_ops = Document(
            page_content="""
            # Operaciones con Vectores
            
            ## Suma de Vectores
            Para sumar dos vectores, sumamos sus componentes correspondientes:
            - Si u = (u₁, u₂) y v = (v₁, v₂)
            - Entonces u + v = (u₁ + v₁, u₂ + v₂)
            
            Ejemplo: (2, 3) + (1, 4) = (3, 7)
            
            ## Producto por Escalar
            Para multiplicar un vector por un número (escalar):
            - Si v = (v₁, v₂) y k es un escalar
            - Entonces k·v = (k·v₁, k·v₂)
            
            Ejemplo: 3·(2, 1) = (6, 3)
            
            ## Propiedades
            - Conmutativa: u + v = v + u
            - Asociativa: (u + v) + w = u + (v + w)
            - Elemento neutro: v + 0 = v
            """,
            metadata={"topic": "vectores", "level": 2, "subtopic": "operaciones"}
        )
        
        # Producto punto
        producto_punto = Document(
            page_content="""
            # Producto Punto de Vectores
            
            ## Definición
            El producto punto (o producto escalar) entre dos vectores u y v se define como:
            u · v = u₁v₁ + u₂v₂ + u₃v₃ (para vectores en R³)
            
            ## Fórmula Alternativa
            u · v = ||u|| ||v|| cos(θ)
            donde θ es el ángulo entre los vectores.
            
            ## Interpretación Geométrica
            - Si u · v = 0, los vectores son perpendiculares (ortogonales)
            - Si u · v > 0, el ángulo es agudo (menor a 90°)
            - Si u · v < 0, el ángulo es obtuso (mayor a 90°)
            
            ## Ejemplo
            u = (3, 4) y v = (1, 2)
            u · v = 3×1 + 4×2 = 3 + 8 = 11
            """,
            metadata={"topic": "producto_punto", "level": 3, "subtopic": "definicion"}
        )
        
        # Magnitud y normalización
        magnitud_norm = Document(
            page_content="""
            # Magnitud y Normalización de Vectores
            
            ## Magnitud (Norma)
            La magnitud de un vector v = (v₁, v₂, v₃) es:
            ||v|| = √(v₁² + v₂² + v₃²)
            
            ## Vector Unitario
            Un vector unitario tiene magnitud 1. Para normalizar un vector:
            û = v / ||v||
            
            ## Ejemplo
            v = (3, 4)
            ||v|| = √(3² + 4²) = √(9 + 16) = √25 = 5
            û = (3/5, 4/5) = (0.6, 0.8)
            
            ## Verificación
            ||û|| = √(0.6² + 0.8²) = √(0.36 + 0.64) = √1 = 1 ✓
            """,
            metadata={"topic": "vectores", "level": 2, "subtopic": "magnitud"}
        )
        
        documents.extend([vectores_def, vectores_ops, producto_punto, magnitud_norm])
        return documents
    
    def _load_matrices_content(self) -> List[Document]:
        """Carga contenido sobre matrices"""
        
        documents = []
        
        matrices_def = Document(
            page_content="""
            # Matrices en Álgebra Lineal
            
            ## Definición
            Una matriz es un arreglo rectangular de números organizados en filas y columnas.
            Una matriz de m×n tiene m filas y n columnas.
            
            ## Notación
            A = [a₁₁  a₁₂  a₁₃]
                [a₂₁  a₂₂  a₂₃]
            
            ## Tipos Especiales
            - Matriz cuadrada: mismo número de filas y columnas
            - Matriz identidad: diagonal principal con 1s, resto 0s
            - Matriz cero: todos los elementos son 0
            - Matriz transpuesta: A^T donde filas y columnas se intercambian
            
            ## Ejemplo
            A = [1  2]  es una matriz 2×2
                [3  4]
            
            A^T = [1  3]  es la transpuesta de A
                  [2  4]
            """,
            metadata={"topic": "matrices", "level": 2, "subtopic": "definicion"}
        )
        
        matrices_mult = Document(
            page_content="""
            # Multiplicación de Matrices
            
            ## Condición
            Para multiplicar A×B, el número de columnas de A debe igual al número 
            de filas de B.
            
            ## Proceso
            El elemento (i,j) del producto C = A×B se calcula como:
            c_ij = Σ(a_ik × b_kj)
            
            ## Ejemplo Detallado
            [1  2] × [5  6] = [1×5+2×7  1×6+2×8] = [19  22]
            [3  4]   [7  8]   [3×5+4×7  3×6+4×8]   [43  50]
            
            Paso a paso:
            - c₁₁ = 1×5 + 2×7 = 5 + 14 = 19
            - c₁₂ = 1×6 + 2×8 = 6 + 16 = 22
            - c₂₁ = 3×5 + 4×7 = 15 + 28 = 43
            - c₂₂ = 3×6 + 4×8 = 18 + 32 = 50
            
            ## Propiedades
            - NO es conmutativa: A×B ≠ B×A (en general)
            - Es asociativa: (A×B)×C = A×(B×C)
            - Distributiva: A×(B+C) = A×B + A×C
            """,
            metadata={"topic": "matrices", "level": 3, "subtopic": "multiplicacion"}
        )
        
        determinantes = Document(
            page_content="""
            # Determinantes de Matrices
            
            ## Matriz 2×2
            Para A = [a  b], det(A) = ad - bc
                    [c  d]
            
            ## Ejemplo
            A = [3  1], det(A) = 3×4 - 1×2 = 12 - 2 = 10
                [2  4]
            
            ## Interpretación Geométrica
            - det(A) = 0: la matriz no es invertible (singular)
            - det(A) ≠ 0: la matriz es invertible
            - |det(A)| representa el área del paralelogramo formado por los vectores fila
            
            ## Matriz 3×3 (Regla de Sarrus)
            Para calcular el determinante de una matriz 3×3, se puede usar
            la expansión por cofactores o la regla de Sarrus.
            """,
            metadata={"topic": "matrices", "level": 3, "subtopic": "determinante"}
        )
        
        documents.extend([matrices_def, matrices_mult, determinantes])
        return documents
    
    def _load_sistemas_content(self) -> List[Document]:
        """Carga contenido sobre sistemas de ecuaciones"""
        
        documents = []
        
        sistemas_def = Document(
            page_content="""
            # Sistemas de Ecuaciones Lineales
            
            ## Definición
            Un sistema de ecuaciones lineales es un conjunto de ecuaciones donde 
            cada ecuación es lineal en las variables.
            
            ## Forma General
            a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ = b₁
            a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ = b₂
            ...
            aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ = bₘ
            
            ## Forma Matricial
            Ax = b, donde:
            - A es la matriz de coeficientes (m×n)
            - x es el vector de variables (n×1)
            - b es el vector de términos independientes (m×1)
            
            ## Ejemplo Simple
            2x + 3y = 7
            x - y = 1
            
            En forma matricial:
            [2  3] [x] = [7]
            [1 -1] [y]   [1]
            
            Solución: x = 2, y = 1
            """,
            metadata={"topic": "sistemas", "level": 2, "subtopic": "definicion"}
        )
        
        metodos_solucion = Document(
            page_content="""
            # Métodos de Solución de Sistemas Lineales
            
            ## 1. Sustitución
            Despejar una variable de una ecuación y sustituir en las otras.
            
            ## 2. Eliminación
            Sumar/restar ecuaciones para eliminar variables.
            
            ## 3. Eliminación Gaussiana
            Convertir la matriz aumentada a forma escalonada:
            [2  3 | 7]  →  [1  0 | 2]
            [1 -1 | 1]     [0  1 | 1]
            
            ## 4. Regla de Cramer
            Para sistemas con determinante no nulo:
            x_i = det(A_i) / det(A)
            donde A_i es A con la columna i reemplazada por b.
            
            ## Tipos de Solución
            - Solución única: det(A) ≠ 0
            - Infinitas soluciones: sistema consistente pero dependiente
            - Sin solución: sistema inconsistente
            """,
            metadata={"topic": "sistemas", "level": 3, "subtopic": "metodos"}
        )
        
        documents.extend([sistemas_def, metodos_solucion])
        return documents
    
    def _load_ejercicios_content(self) -> List[Document]:
        """Carga ejercicios de práctica"""
        
        documents = []
        
        ejercicios_vectores = Document(
            page_content="""
            # Ejercicios Resueltos - Vectores
            
            ## Ejercicio 1: Suma de Vectores
            Dados u = (2, 3) y v = (1, -2), calcular u + v.
            
            Solución:
            u + v = (2, 3) + (1, -2) = (2+1, 3+(-2)) = (3, 1)
            
            ## Ejercicio 2: Producto por Escalar  
            Dado v = (4, -1) y k = 3, calcular k·v.
            
            Solución:
            3·v = 3·(4, -1) = (3×4, 3×(-1)) = (12, -3)
            
            ## Ejercicio 3: Magnitud de Vector
            Calcular la magnitud del vector v = (3, 4).
            
            Solución:
            ||v|| = √(3² + 4²) = √(9 + 16) = √25 = 5
            
            ## Ejercicio 4: Producto Punto
            Calcular u · v donde u = (2, 1) y v = (3, 4).
            
            Solución:
            u · v = 2×3 + 1×4 = 6 + 4 = 10
            """,
            metadata={"topic": "ejercicios", "level": 1, "subtopic": "vectores_basicos"}
        )
        
        ejercicios_matrices = Document(
            page_content="""
            # Ejercicios Resueltos - Matrices
            
            ## Ejercicio 1: Suma de Matrices
            Calcular A + B donde:
            A = [1  2]    B = [3  0]
                [3  4]        [1  2]
            
            Solución:
            A + B = [1+3  2+0] = [4  2]
                    [3+1  4+2]   [4  6]
            
            ## Ejercicio 2: Multiplicación de Matrices
            Calcular A×B donde:
            A = [1  2]    B = [2  1]
                [3  4]        [0  3]
            
            Solución:
            A×B = [1×2+2×0  1×1+2×3] = [2  7]
                  [3×2+4×0  3×1+4×3]   [6  15]
            
            ## Ejercicio 3: Determinante 2×2
            Calcular det(A) donde A = [2  3]
                                    [1  4]
            
            Solución:
            det(A) = 2×4 - 3×1 = 8 - 3 = 5
            """,
            metadata={"topic": "ejercicios", "level": 2, "subtopic": "matrices_basicas"}
        )
        
        documents.extend([ejercicios_vectores, ejercicios_matrices])
        return documents
    
    def _load_advanced_content(self) -> List[Document]:
        """Carga contenido avanzado"""
        
        documents = []
        
        espacios_vectoriales = Document(
            page_content="""
            # Espacios Vectoriales
            
            ## Definición
            Un espacio vectorial V es un conjunto de vectores con operaciones 
            de suma y multiplicación por escalar que satisface 8 axiomas:
            
            1. Clausura bajo suma: u + v ∈ V
            2. Conmutatividad: u + v = v + u
            3. Asociatividad: (u + v) + w = u + (v + w)
            4. Elemento neutro: existe 0 tal que v + 0 = v
            5. Elemento inverso: existe -v tal que v + (-v) = 0
            6. Clausura bajo multiplicación por escalar: k·v ∈ V
            7. Distributividad: k·(u + v) = k·u + k·v
            8. Compatibilidad: (ab)·v = a·(b·v)
            
            ## Ejemplos
            - R²: vectores en el plano
            - R³: vectores en el espacio
            - Polinomios de grado ≤ n
            - Matrices m×n
            """,
            metadata={"topic": "espacios_vectoriales", "level": 4, "subtopic": "definicion"}
        )
        
        independencia_lineal = Document(
            page_content="""
            # Independencia Lineal
            
            ## Definición
            Un conjunto de vectores {v₁, v₂, ..., vₙ} es linealmente independiente
            si la única solución a:
            c₁v₁ + c₂v₂ + ... + cₙvₙ = 0
            es c₁ = c₂ = ... = cₙ = 0
            
            ## Interpretación Geométrica
            - En R²: dos vectores son linealmente independientes si no son paralelos
            - En R³: tres vectores son linealmente independientes si no son coplanares
            
            ## Ejemplo
            u = (1, 0) y v = (0, 1) son linealmente independientes porque:
            c₁(1, 0) + c₂(0, 1) = (0, 0) solo si c₁ = c₂ = 0
            
            ## Base
            Un conjunto de vectores linealmente independientes que genera
            todo el espacio vectorial se llama base.
            """,
            metadata={"topic": "espacios_vectoriales", "level": 4, "subtopic": "independencia"}
        )