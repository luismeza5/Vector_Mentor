"""RAG Híbrido - Funciona con o sin embeddings"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from config.settings import settings

class HybridRAGManager:
    """RAG que funciona con embeddings cuando está disponible, sino usa búsqueda simple"""
    
    def __init__(self):
        self.documents = []
        self.use_embeddings = False
        self.vector_store = None
        self.embeddings = None
        
        # Intentar cargar sistema completo
        self._try_initialize_full_rag()
        
        # Si falla, usar versión simple
        if not self.use_embeddings:
            print("⚠️ Usando RAG simple sin embeddings")
            self._add_initial_content()
    
    def _try_initialize_full_rag(self):
        """Intenta inicializar el sistema RAG completo"""
        try:
            from langchain_openai import OpenAIEmbeddings
            from langchain_community.vectorstores import Chroma
            import os
            
            # Verificar API key más estrictamente
            if not settings.OPENAI_API_KEY or len(settings.OPENAI_API_KEY) < 20:
                print(f"⚠️ API Key no válida (longitud: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0})")
                raise Exception("API Key no configurada correctamente")
            
            print(f"🔑 API Key detectada (longitud: {len(settings.OPENAI_API_KEY)})")
            
            # Configurar variable de entorno para OpenAI (AQUÍ ES DONDE VA)
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            
            # Inicializar embeddings SIN parámetros adicionales
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL
            )
            
            # Crear directorio si no existe
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            self.vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
            
            # Probar embedding simple para verificar conectividad
            print("🧪 Probando conectividad con OpenAI...")
            test_embedding = self.embeddings.embed_query("test")
            print(f"✅ Conectividad OK - embedding dimensión: {len(test_embedding)}")
            
            self.use_embeddings = True
            print("✅ RAG completo con embeddings inicializado")
            
            # Agregar contenido inicial si la base está vacía
            if self.vector_store._collection.count() == 0:
                print("📚 Base vectorial vacía, agregando contenido inicial...")
                self._add_initial_content_to_vectorstore()
            else:
                print(f"📚 Base vectorial existente con {self.vector_store._collection.count()} documentos")
            
        except Exception as e:
            print(f"⚠️ No se pudo inicializar RAG completo: {e}")
            self.use_embeddings = False

    def _add_initial_content_to_vectorstore(self):
        """Agrega contenido inicial a la base vectorial"""
        documents = [
            Document(
                page_content="""
                Un vector es una cantidad que tiene tanto magnitud como dirección. 
                En el plano cartesiano, un vector se puede representar como un par ordenado (x, y).
                La magnitud de un vector v = (x, y) se calcula como ||v|| = √(x² + y²).
                Los vectores se pueden sumar componente a componente: (a, b) + (c, d) = (a+c, b+d).
                """,
                metadata={"topic": "vectores", "level": 1, "subtopic": "definicion_basica"}
            ),
            
            Document(
                page_content="""
                Las operaciones básicas con vectores incluyen:
                1. Suma: u + v = (u₁ + v₁, u₂ + v₂)
                2. Resta: u - v = (u₁ - v₁, u₂ - v₂)  
                3. Multiplicación por escalar: k·v = (k·v₁, k·v₂)
                4. Producto punto: u·v = u₁v₁ + u₂v₂
                El producto punto da como resultado un escalar, no un vector.
                """,
                metadata={"topic": "vectores", "level": 2, "subtopic": "operaciones"}
            ),
            
            Document(
                page_content="""
                El producto punto (o producto escalar) entre dos vectores u = (u₁, u₂) y v = (v₁, v₂) 
                se define como u·v = u₁v₁ + u₂v₂ = ||u|| ||v|| cos(θ), donde θ es el ángulo entre los vectores.
                Si el producto punto es cero, los vectores son perpendiculares (ortogonales).
                Si es positivo, el ángulo es agudo; si es negativo, el ángulo es obtuso.
                """,
                metadata={"topic": "producto_punto", "level": 3, "subtopic": "definicion"}
            ),
            
            Document(
                page_content="""
                Una matriz es un arreglo rectangular de números organizados en filas y columnas.
                Una matriz de m×n tiene m filas y n columnas. Las operaciones básicas incluyen:
                - Suma de matrices (del mismo tamaño): se suman elemento a elemento
                - Multiplicación por escalar: se multiplica cada elemento por el escalar
                - Multiplicación de matrices: el elemento (i,j) es el producto punto de la fila i por la columna j
                """,
                metadata={"topic": "matrices", "level": 2, "subtopic": "definicion_operaciones"}
            ),
            
            Document(
                page_content="""
                Un sistema de ecuaciones lineales se puede escribir en forma matricial como Ax = b,
                donde A es la matriz de coeficientes, x es el vector de incógnitas, y b es el vector de términos independientes.
                Los métodos de solución incluyen: eliminación gaussiana, regla de Cramer, y factorización LU.
                Un sistema puede tener solución única, infinitas soluciones, o no tener solución.
                """,
                metadata={"topic": "sistemas_lineales", "level": 3, "subtopic": "forma_matricial"}
            )
        ]
        
        # Agregar a la base vectorial
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
        print(f"✅ {len(documents)} documentos agregados a la base vectorial")
    
    def _add_initial_content(self):
        """Agrega contenido inicial para versión simple"""
        self.documents = [
            Document(
                page_content="""
                VECTORES BÁSICOS: Un vector es una cantidad que tiene magnitud y dirección. 
                En 2D se representa como (x, y). La magnitud es ||v|| = √(x² + y²).
                Ejemplos: v = (3, 4) tiene magnitud ||v|| = √(9 + 16) = 5.
                Los vectores se suman componente a componente: (2, 3) + (1, 4) = (3, 7).
                """,
                metadata={"topic": "vectores", "level": 1, "keywords": ["vector", "magnitud", "dirección", "componentes"]}
            ),
            
            Document(
                page_content="""
                OPERACIONES CON VECTORES:
                1. Suma: u + v = (u₁ + v₁, u₂ + v₂)
                2. Resta: u - v = (u₁ - v₁, u₂ - v₂)
                3. Producto por escalar: k·v = (k·v₁, k·v₂)
                4. Producto punto: u·v = u₁v₁ + u₂v₂
                Ejemplo: (2,3)·(4,1) = 2×4 + 3×1 = 8 + 3 = 11
                """,
                metadata={"topic": "vectores", "level": 2, "keywords": ["suma", "resta", "producto", "escalar", "operaciones"]}
            ),
            
            Document(
                page_content="""
                PRODUCTO PUNTO: El producto punto u·v = ||u|| ||v|| cos(θ) donde θ es el ángulo entre vectores.
                Si u·v = 0, los vectores son perpendiculares (ortogonales).
                Si u·v > 0, el ángulo es agudo (< 90°).
                Si u·v < 0, el ángulo es obtuso (> 90°).
                Ejemplo: (1,0)·(0,1) = 1×0 + 0×1 = 0, son perpendiculares.
                """,
                metadata={"topic": "producto_punto", "level": 3, "keywords": ["producto", "punto", "escalar", "perpendicular", "ortogonal", "ángulo"]}
            ),
            
            Document(
                page_content="""
                MATRICES: Una matriz m×n tiene m filas y n columnas.
                Suma: A + B se hace elemento a elemento (mismas dimensiones).
                Multiplicación: (AB)ᵢⱼ = suma de Aᵢₖ × Bₖⱼ para todo k.
                Ejemplo matriz 2×2: [[1,2],[3,4]] × [[5,6],[7,8]] = [[19,22],[43,50]]
                """,
                metadata={"topic": "matrices", "level": 2, "keywords": ["matriz", "filas", "columnas", "multiplicación", "suma"]}
            ),
            
            Document(
                page_content="""
                SISTEMAS LINEALES: Ax = b donde A es matriz, x vector incógnitas, b vector términos.
                Métodos: Eliminación Gaussiana, Regla de Cramer, factorización LU.
                Ejemplo: 2x + 3y = 7, x - y = 1 → x = 2, y = 1
                Puede tener: solución única, infinitas soluciones, o sin solución.
                """,
                metadata={"topic": "sistemas_lineales", "level": 3, "keywords": ["sistema", "ecuaciones", "eliminación", "gaussiana", "cramer", "solución"]}
            )
        ]
        print(f"✅ RAG simple inicializado con {len(self.documents)} documentos")
    
    async def similarity_search(self, query: str, k: int = 3, filter_level: int = None) -> List[Document]:
        """Búsqueda que funciona con o sin embeddings"""
        
        if self.use_embeddings and self.vector_store:
            # Usar búsqueda vectorial
            try:
                filter_dict = {}
                if filter_level:
                    filter_dict = {"level": {"$lte": filter_level}}
                
                results = self.vector_store.similarity_search(
                    query, k=k, filter=filter_dict if filter_dict else None
                )
                return results
            except Exception as e:
                print(f"⚠️ Error en búsqueda vectorial, usando búsqueda simple: {e}")
        
        # Búsqueda simple por palabras clave
        return self._simple_keyword_search(query, k, filter_level)
    
    def _simple_keyword_search(self, query: str, k: int, filter_level: int = None) -> List[Document]:
        """Búsqueda simple por palabras clave"""
        query_words = query.lower().split()
        results = []
        
        for doc in self.documents:
            score = 0
            content_lower = doc.page_content.lower()
            keywords = doc.metadata.get("keywords", [])
            
            # Puntuación por palabras en el contenido
            for word in query_words:
                if word in content_lower:
                    score += 2
                if word in keywords:
                    score += 3
            
            # Filtrar por nivel
            if filter_level:
                doc_level = doc.metadata.get("level", 3)
                if doc_level > filter_level:
                    continue
            
            if score > 0:
                results.append((doc, score))
        
        # Ordenar por score y retornar top k
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in results[:k]]
    
    def search_by_topic(self, topic: str, level: int = None, k: int = 5) -> List[Document]:
        """Busca por tema específico"""
        results = []
        
        for doc in self.documents:
            doc_topic = doc.metadata.get("topic", "")
            if topic.lower() in doc_topic.lower():
                if level is None or doc.metadata.get("level", 3) <= level:
                    results.append(doc)
        
        return results[:k]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Estadísticas de la colección"""
        if self.use_embeddings and self.vector_store:
            try:
                count = self.vector_store._collection.count()
                return {
                    "count": count,
                    "status": "embeddings_active",
                    "type": "full_rag"
                }
            except:
                pass
        
        return {
            "count": len(self.documents),
            "status": "simple_active", 
            "type": "keyword_search",
            "topics": list(set(doc.metadata.get("topic", "") for doc in self.documents))
        }
    
    def add_documents(self, documents: List[Document]):
        """Agrega documentos al sistema"""
        if self.use_embeddings and self.vector_store:
            try:
                self.vector_store.add_documents(documents)
                print(f"✅ {len(documents)} documentos agregados al vector store")
                return
            except Exception as e:
                print(f"⚠️ Error agregando a vector store: {e}")
        
        # Agregar a lista simple
        self.documents.extend(documents)
        print(f"✅ {len(documents)} documentos agregados a la lista simple")