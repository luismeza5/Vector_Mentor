"""Test del sistema RAG de VectorMentor"""

import sys
import os
import asyncio

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_rag_system():
    """Test completo del sistema RAG"""
    print("🔬 Iniciando tests del sistema RAG...")
    
    # Test 1: Imports
    try:
        from rag import VectorStoreManager, EmbeddingManager
        print("✅ Imports de RAG exitosos")
    except ImportError as e:
        print(f"❌ Error importando RAG: {e}")
        return
    
    # Test 2: Configuración
    try:
        from config import settings
        print(f"✅ API Key configurada: {'Sí' if settings.OPENAI_API_KEY else 'No'}")
        print(f"✅ Modelo de embeddings: {settings.EMBEDDING_MODEL}")
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        return
    
    # Test 3: Inicializar VectorStore
    try:
        print("\n📚 Inicializando VectorStore...")
        vector_store = VectorStoreManager()
        stats = vector_store.get_collection_stats()
        print(f"✅ VectorStore inicializado: {stats['count']} documentos")
    except Exception as e:
        print(f"❌ Error inicializando VectorStore: {e}")
        return
    
    # Test 4: Búsqueda básica
    try:
        print("\n🔍 Probando búsqueda...")
        results = await vector_store.similarity_search("¿Qué es un vector?", k=3)
        print(f"✅ Búsqueda exitosa: {len(results)} resultados encontrados")
        
        if results:
            print(f"📄 Primer resultado: {results[0].page_content[:100]}...")
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    # Test 5: EmbeddingManager
    try:
        print("\n🧠 Probando EmbeddingManager...")
        embedding_manager = EmbeddingManager()
        
        # Test embedding simple
        test_text = "Los vectores tienen magnitud y dirección"
        embedding = await embedding_manager.embed_text(test_text)
        print(f"✅ Embedding generado: dimensión {len(embedding) if embedding else 0}")
        
    except Exception as e:
        print(f"❌ Error en EmbeddingManager: {e}")
    
    # Test 6: Búsqueda por tema
    try:
        print("\n📖 Probando búsqueda por tema...")
        topic_results = vector_store.search_by_topic("vectores", level=2, k=2)
        print(f"✅ Búsqueda por tema: {len(topic_results)} documentos sobre vectores")
    except Exception as e:
        print(f"❌ Error en búsqueda por tema: {e}")
    
    print("\n🎯 Tests de RAG completados!")

if __name__ == "__main__":
    asyncio.run(test_rag_system())