"""Embedding Manager - Gestión de embeddings para RAG"""

from typing import List, Dict, Any, Tuple
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
import numpy as np

class EmbeddingManager:
    """Gestiona la generación y manipulación de embeddings"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY  # Cambio aquí también
        )
        
    async def embed_text(self, text: str) -> List[float]:
        """Genera embedding para un texto"""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            print(f"❌ Error generando embedding: {e}")
            return []
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para múltiples documentos"""
        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"❌ Error generando embeddings: {e}")
            return []
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calcula similaridad coseno entre dos embeddings"""
        try:
            # Convertir a numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calcular similaridad coseno
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"❌ Error calculando similaridad: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         threshold: float = None) -> List[Tuple[int, float]]:
        """Encuentra los embeddings más similares al query"""
        threshold = threshold or settings.SIMILARITY_THRESHOLD
        
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate)
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        # Ordenar por similaridad descendente
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    
    async def semantic_search(self, query: str, documents: List[str], 
                            top_k: int = 5) -> List[Tuple[str, float]]:
        """Búsqueda semántica en documentos"""
        try:
            # Generar embedding del query
            query_embedding = await self.embed_text(query)
            if not query_embedding:
                return []
            
            # Generar embeddings de documentos
            doc_embeddings = await self.embed_documents(documents)
            if not doc_embeddings:
                return []
            
            # Encontrar más similares
            similarities = self.find_most_similar(query_embedding, doc_embeddings)
            
            # Retornar top_k resultados con documentos
            results = []
            for idx, score in similarities[:top_k]:
                results.append((documents[idx], score))
            
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda semántica: {e}")
            return []
    
    def analyze_embedding_quality(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """Analiza la calidad de los embeddings"""
        if not embeddings:
            return {"status": "no_embeddings"}
        
        try:
            # Convertir a numpy array
            emb_array = np.array(embeddings)
            
            # Estadísticas básicas
            stats = {
                "count": len(embeddings),
                "dimension": len(embeddings[0]) if embeddings else 0,
                "mean_norm": np.mean([np.linalg.norm(emb) for emb in embeddings]),
                "std_norm": np.std([np.linalg.norm(emb) for emb in embeddings]),
            }
            
            # Diversidad (distancia promedio entre embeddings)
            if len(embeddings) > 1:
                similarities = []
                for i in range(len(embeddings)):
                    for j in range(i+1, len(embeddings)):
                        sim = self.cosine_similarity(embeddings[i], embeddings[j])
                        similarities.append(sim)
                
                stats["avg_similarity"] = np.mean(similarities)
                stats["diversity_score"] = 1 - np.mean(similarities)  # Más diverso = menos similar
            
            return stats
            
        except Exception as e:
            return {"status": f"error: {e}"}
    
    async def generate_topic_embedding(self, topic: str, context: str = "") -> List[float]:
        """Genera embedding optimizado para un tema específico"""
        # Crear prompt enriquecido para el tema
        enriched_text = f"{topic}"
        if context:
            enriched_text += f" {context}"
        
        # Agregar palabras clave relacionadas según el tema
        topic_keywords = {
            "vectores": "vector magnitud dirección componentes suma escalar",
            "matrices": "matriz determinante inversa filas columnas multiplicación",
            "sistemas_lineales": "ecuaciones sistema solución eliminación gaussiana",
            "espacios_vectoriales": "espacio base dimensión independencia lineal",
            "producto_punto": "producto escalar ortogonal perpendicular ángulo",
            "transformaciones_lineales": "transformación mapeo lineal matriz representación"
        }
        
        if topic.lower() in topic_keywords:
            enriched_text += f" {topic_keywords[topic.lower()]}"
        
        return await self.embed_text(enriched_text)
    
    def batch_similarity_matrix(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Calcula matriz de similaridad para un conjunto de embeddings"""
        n = len(embeddings)
        similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    similarity_matrix[i][j] = self.cosine_similarity(embeddings[i], embeddings[j])
        
        return similarity_matrix