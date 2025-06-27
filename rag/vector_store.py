"""VectorStore Manager - Gestión de la base de datos vectorial - CORREGIDO"""

import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from config.settings import settings

# Importar Chroma desde el paquete correcto para evitar warnings
try:
    from langchain_chroma import Chroma
    print("Usando langchain-chroma")
except ImportError:
    from langchain_community.vectorstores import Chroma
    print("⚠️ Usando langchain_community.vectorstores (deprecado)")

class VectorStoreManager:
    """Gestiona la base de datos vectorial para RAG"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY  # Usar api_key en lugar de openai_api_key
        )
        self.vector_store = None
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Inicializa la base vectorial"""
        try:
            # Crear directorio si no existe
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Intentar cargar base existente
            chroma_db_path = os.path.join(self.persist_directory, "chroma.sqlite3")
            if os.path.exists(chroma_db_path):
                print("Cargando base vectorial existente...")
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                try:
                    count = self.vector_store._collection.count()
                    print(f" Base vectorial cargada con {count} documentos")
                except:
                    print(" Base vectorial cargada (no se pudo obtener count)")
            else:
                print(" Creando nueva base vectorial...")
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                # Agregar contenido inicial
                self._add_initial_content()
                
        except Exception as e:
            print(f"❌ Error inicializando vector store: {e}")
            # Fallback: crear en memoria
            self.vector_store = Chroma(embedding_function=self.embeddings)
            print(" Usando vector store en memoria como fallback")
    
    def _add_initial_content(self):
        """Agrega contenido educativo inicial"""
        print(" Agregando contenido educativo inicial...")
        
        initial_documents = [
            # Vectores básicos
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
            
            # Matrices básicas
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
                El determinante de una matriz 2×2 es: det(A) = ad - bc para A = [[a,b],[c,d]].
                Para matrices 3×3, se puede usar la regla de Sarrus o expansión por cofactores.
                El determinante es cero si y solo si la matriz es singular (no invertible).
                Una matriz es invertible si su determinante es diferente de cero.
                """,
                metadata={"topic": "matrices", "level": 3, "subtopic": "determinante"}
            ),
            
            # Sistemas lineales
            Document(
                page_content="""
                Un sistema de ecuaciones lineales se puede escribir en forma matricial como Ax = b,
                donde A es la matriz de coeficientes, x es el vector de incógnitas, y b es el vector de términos independientes.
                Los métodos de solución incluyen: eliminación gaussiana, regla de Cramer, y factorización LU.
                Un sistema puede tener solución única, infinitas soluciones, o no tener solución.
                """,
                metadata={"topic": "sistemas_lineales", "level": 3, "subtopic": "forma_matricial"}
            ),
            
            # Espacios vectoriales
            Document(
                page_content="""
                Un espacio vectorial es un conjunto de vectores con operaciones de suma y multiplicación por escalar
                que satisfacen ciertos axiomas. Los vectores en R² forman un espacio vectorial de dimensión 2.
                Una base es un conjunto de vectores linealmente independientes que generan todo el espacio.
                La dimensión de un espacio vectorial es el número de vectores en cualquier base.
                """,
                metadata={"topic": "espacios_vectoriales", "level": 4, "subtopic": "definicion"}
            ),
            
            Document(
                page_content="""
                Vectores linealmente independientes son aquellos donde ninguno puede escribirse como
                combinación lineal de los otros. En R², dos vectores son linealmente independientes
                si no son paralelos (colineales). En R³, tres vectores son linealmente independientes
                si no son coplanares. La independencia lineal se puede verificar con determinantes.
                """,
                metadata={"topic": "espacios_vectoriales", "level": 4, "subtopic": "independencia_lineal"}
            )
        ]
        
        # Agregar documentos a la base vectorial
        self.add_documents(initial_documents)
        print(f" {len(initial_documents)} documentos iniciales agregados")
    
    def similarity_search(self, query: str, k: int = None, filter_level: int = None) -> List[Document]:
        """Busca documentos similares al query"""
        if not self.vector_store:
            return []
        
        k = k or settings.RETRIEVAL_TOP_K
        
        try:
            # Construir filtros si se especifica nivel
            if filter_level:
                # Buscar documentos del nivel del estudiante o menores
                # Nota: Chroma usa diferentes sintaxis para filtros según la versión
                try:
                    # Intentar nueva sintaxis
                    docs = self.vector_store.similarity_search(
                        query, 
                        k=k, 
                        filter={"level": {"$lte": filter_level}}
                    )
                except:
                    # Fallback: buscar sin filtro y filtrar manualmente
                    all_docs = self.vector_store.similarity_search(query, k=k*2)
                    docs = [doc for doc in all_docs if doc.metadata.get("level", 3) <= filter_level][:k]
            else:
                docs = self.vector_store.similarity_search(query, k=k)
            
            return docs
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def add_documents(self, documents: List[Document]):
        """Agrega documentos a la base vectorial"""
        if not self.vector_store:
            print("❌ Vector store no inicializado")
            return
        
        try:
            self.vector_store.add_documents(documents)
            # Intentar persistir si es posible
            try:
                self.vector_store.persist()
            except:
                pass  # persist() puede no estar disponible en todas las versiones
            print(f" {len(documents)} documentos agregados")
        except Exception as e:
            print(f"❌ Error agregando documentos: {e}")
    
    def add_text_with_metadata(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Agrega textos con metadatos"""
        if not self.vector_store:
            print("❌ Vector store no inicializado")
            return
        
        try:
            self.vector_store.add_texts(texts, metadatas=metadatas)
            try:
                self.vector_store.persist()
            except:
                pass
            print(f" {len(texts)} textos agregados")
        except Exception as e:
            print(f"❌ Error agregando textos: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección"""
        if not self.vector_store:
            return {"count": 0, "status": "no_initialized"}
        
        try:
            # Intentar obtener el count de diferentes maneras
            count = 0
            try:
                count = self.vector_store._collection.count()
            except:
                try:
                    # Alternativa: hacer una búsqueda amplia
                    docs = self.vector_store.similarity_search("", k=1000)
                    count = len(docs)
                except:
                    count = "unknown"
            
            return {
                "count": count,
                "status": "active",
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {"count": 0, "status": f"error: {e}"}
    
    def clear_collection(self):
        """Limpia toda la colección (usar con cuidado)"""
        if self.vector_store:
            try:
                # Intentar diferentes métodos para limpiar
                try:
                    self.vector_store.delete_collection()
                except:
                    # Fallback: eliminar archivos físicos
                    import shutil
                    if os.path.exists(self.persist_directory):
                        shutil.rmtree(self.persist_directory)
                
                print("🗑️ Colección limpiada")
                self._initialize_vector_store()
            except Exception as e:
                print(f"❌ Error limpiando colección: {e}")
    
    def search_by_topic(self, topic: str, level: int = None, k: int = 5) -> List[Document]:
        """Busca documentos por tema específico"""
        if not self.vector_store:
            return []
        
        try:
            # Construir query de búsqueda más específica
            search_query = f"{topic} álgebra lineal"
            
            if level:
                # Filtrar por nivel si se especifica
                docs = self.similarity_search(search_query, k=k*2, filter_level=level)
            else:
                docs = self.similarity_search(search_query, k=k)
            
            # Filtrar por tema en los metadatos
            filtered_docs = []
            for doc in docs:
                doc_topic = doc.metadata.get("topic", "").lower()
                if topic.lower() in doc_topic or doc_topic in topic.lower():
                    filtered_docs.append(doc)
            
            return filtered_docs[:k]
            
        except Exception as e:
            print(f"❌ Error buscando por tema: {e}")
            return []
    
    def add_user_content(self, content: str, topic: str, level: int = 3, subtopic: str = "user_generated"):
        """Permite agregar contenido generado por el usuario o sistema"""
        document = Document(
            page_content=content,
            metadata={
                "topic": topic,
                "level": level,
                "subtopic": subtopic,
                "source": "user_generated"
            }
        )
        self.add_documents([document])
    
    def get_topics_summary(self) -> Dict[str, int]:
        """Obtiene resumen de temas disponibles"""
        try:
            # Hacer búsqueda amplia para obtener muestra de documentos
            sample_docs = self.vector_store.similarity_search("matemáticas álgebra", k=50)
            
            topics_count = {}
            for doc in sample_docs:
                topic = doc.metadata.get("topic", "unknown")
                topics_count[topic] = topics_count.get(topic, 0) + 1
            
            return topics_count
        except:
            return {"vectores": 3, "matrices": 3, "sistemas": 2, "espacios_vectoriales": 2}