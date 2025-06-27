

# VectorMentor - Sistema Multiagente con RAG

Sistema de tutoría académica personalizada que utiliza múltiples agentes de IA para proporcionar una experiencia de aprendizaje adaptativa en álgebra lineal.

## Características

- **Sistema Multiagente**: 4 agentes especializados que colaboran
- **RAG (Retrieval-Augmented Generation)**: Base de conocimiento vectorial con Chroma
- **Tutoría Personalizada**: Adaptación al nivel del estudiante
- **Interfaz Web**: Aplicación interactiva con Streamlit
- **LangGraph**: Orquestación avanzada del flujo de trabajo

## Arquitectura

### Agentes Especializados:

1. **Coordinador**: Orquesta la interacción entre agentes
2. **Evaluador**: Analiza el nivel y progreso del estudiante
3. **Recuperador**: Busca contenido relevante usando RAG
4. **Tutor**: Genera explicaciones personalizadas

### Tecnologías:

- **LangChain** + **LangGraph**: Framework de agentes
- **OpenAI GPT-4**: Modelo de lenguaje
- **Chroma**: Base de datos vectorial
- **Streamlit**: Interfaz web
- **Python 3.9+**: Lenguaje de desarrollo

## Instalación

### Requisitos Previos

- Python 3.9 o superior
- Clave API de OpenAI

### Pasos de Instalación

1. **Clonar el repositorio:**

```bash
git clone <repository-url>
cd eduamentor-ai
```

2. **Crear entorno virtual:**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**

```bash
# Crear archivo .env
echo "OPENAI_API_KEY=tu_clave_api_aqui" > .env
```

5. **Ejecutar el sistema:**

```bash
python main.py
```

## Uso

### Modo Web (Por defecto)

```bash
python main.py
```

Abre tu navegador en `http://localhost:8501`

### Modo Consola

```bash
python main.py --cli
```

## Estructura del Proyecto

```
vector_mentor/
├── main.py                    # Archivo principal
├── requirements.txt           # Dependencias
├── README.md                 # Este archivo
├── config/
│   └── settings.py           # Configuraciones
├── agents/                   # Agentes especializados
│   ├── base_agent.py
│   ├── coordinator_agent.py
│   ├── assessor_agent.py
│   ├── retriever_agent.py
│   └── tutor_agent.py
├── knowledge_base/           # Contenido educativo
│   ├── content_loader.py
│   └── data/
├── rag/                      # Sistema RAG
│   ├── vector_store.py
│   ├── embeddings.py
│   └── retrieval.py
├── workflow/                 # LangGraph
│   └── langgraph_flow.py
├── interface/                # Interfaz web
│   └── streamlit_app.py
└── utils/                    # Utilidades
    ├── logging_config.py
    └── helpers.py
```

## Ejemplos de Uso

### Preguntas Básicas

- "¿Qué es un vector?"
- "¿Cómo sumo dos matrices?"
- "Explica los sistemas de ecuaciones lineales"

### Ejercicios Prácticos

- "Dame un ejercicio de vectores nivel básico"
- "Quiero practicar multiplicación de matrices"
- "Genera un problema de sistemas de ecuaciones"

### Evaluación

- Responde ejercicios y recibe retroalimentación personalizada
- El sistema adapta el contenido a tu nivel automáticamente

## Configuración Avanzada

### Cambiar Modelo de IA

Edita `config/settings.py`:

```python
LLM_MODEL = "gpt-3.5-turbo"  # o "mistral-7b-instruct"
```

### Ajustar Parámetros RAG

```python
RETRIEVAL_TOP_K = 3          # Número de documentos a recuperar
SIMILARITY_THRESHOLD = 0.8   # Umbral de similitud
```

### Personalizar Contenido

Agrega archivos .txt en `knowledge_base/data/` organizados por tema.

## Testing

```bash
# Ejecutar tests
pytest tests/

# Test específico
pytest tests/test_agents.py -v
```

## Monitoreo

Los logs se guardan en `logs/eduamentor.log` con información sobre:

- Interacciones de usuarios
- Rendimiento de agentes
- Errores del sistema

## Contribuir

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Elaborado por:

- **Luis Meza Chavarría**
