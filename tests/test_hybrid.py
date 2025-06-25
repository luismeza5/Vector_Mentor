"""Test del sistema RAG híbrido - Versión corregida"""

import sys
import os
import asyncio

# Agregar el directorio raíz al path (DOS niveles arriba)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"📁 Directorio actual: {current_dir}")
print(f"📁 Directorio padre: {parent_dir}")

async def test_hybrid_rag():
    """Test del RAG híbrido"""
    print("🔬 Probando RAG híbrido...")
    
    try:
        # Verificar que se puede importar
        print("📦 Intentando importar rag.hybrid_store...")
        from rag.hybrid_store import HybridRAGManager
        print("✅ Import exitoso")
        
        # Inicializar
        print("🚀 Inicializando HybridRAGManager...")
        rag = HybridRAGManager()
        
        # Estadísticas
        stats = rag.get_collection_stats()
        print(f"✅ RAG híbrido: {stats['count']} documentos")
        print(f"✅ Tipo: {stats['type']}")
        print(f"✅ Estado: {stats['status']}")
        
        # Test búsqueda
        print("\n🔍 Probando búsqueda...")
        results1 = await rag.similarity_search("¿Qué es un vector?", k=2)
        print(f"✅ 'Qué es un vector': {len(results1)} resultados")
        
        if results1:
            print(f"\n📄 Ejemplo:")
            print(f"Tema: {results1[0].metadata.get('topic', 'N/A')}")
            print(f"Contenido: {results1[0].page_content[:80]}...")
        
        print("\n🎯 Test completado exitosamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        print("💡 Verifica que existe rag/hybrid_store.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_hybrid_rag())