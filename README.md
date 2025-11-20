# BlackStory AI

## Descripción del Proyecto

**BlackStory AI** es un innovador juego de misterio interactivo donde dos inteligencias artificiales asumen los roles de "Narrador" y "Investigador". El Narrador crea un enigma macabro y conoce la solución secreta, mientras que el Investigador intenta desentrañar el misterio haciendo preguntas de "sí" o "no". El juego simula una partida de "Black Stories" completamente automatizada, ofreciendo una experiencia única y desafiante.

## Características Principales

-   **Roles de IA Dinámicos:** Dos IAs especializadas (Narrador e Investigador) interactúan para desarrollar y resolver el misterio.
-   **Misterios Generados por IA:** El Narrador crea enigmas originales y sus soluciones, garantizando una rejugabilidad infinita.
-   **Investigación Interactiva:** El Investigador formula preguntas de sí/no, y el Narrador responde basándose en la solución secreta.
-   **Múltiples Proveedores de IA:** Soporte para diversos modelos de lenguaje grandes (LLMs) como Gemini, OpenAI, Anthropic y Ollama, permitiendo flexibilidad y experimentación.
-   **Configuración Personalizable:** Ajusta el proveedor de IA, el modelo y el número de turnos a través de argumentos de línea de comandos.
-   **Registro de Partidas:** Cada partida se guarda automáticamente en un archivo Markdown, incluyendo el enigma, la solución, el historial de chat y un diagrama de flujo (Mermaid) de la investigación.
-   **Veredicto Final:** El Narrador emite un veredicto sobre si el Investigador logró resolver el misterio.

## Proveedores de IA Soportados

El proyecto está diseñado para ser modular y soporta los siguientes proveedores de IA:

-   **Gemini** (Google AI)
-   **OpenAI** (GPT models)
-   **Anthropic** (Claude models)
-   **Ollama** (Modelos locales como Llama 3, Mistral, etc.)

## Instalación

### Requisitos

-   Python 3.9 o superior
-   `pip` (gestor de paquetes de Python)

### Pasos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/jacobobecerral/BlackStory_IA.git
    cd BlackStory_IA
    ```

2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    python -m venv .venv
    # En Windows
    .venv\Scripts\activate
    # En macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Nota: Si el archivo `requirements.txt` no existe, puedes generarlo con `pip freeze > requirements.txt` después de instalar las dependencias manualmente, o instalar las dependencias listadas en `pyproject.toml`.)*

4.  **Configurar las claves API:**
    Crea un archivo `.env` en la raíz del proyecto y añade tus claves API para los proveedores de IA que desees utilizar.

    Ejemplo de `.env`:
    ```
    GOOGLE_API_KEY="tu_clave_api_gemini"
    OPENAI_API_KEY="tu_clave_api_openai"
    ANTHROPIC_API_KEY="tu_clave_api_anthropic"
    # Para Ollama no se requiere clave API, solo que el servidor esté corriendo localmente.
    ```

## Uso

Para ejecutar el juego, utiliza el script `main.py` con los argumentos deseados.

### Argumentos de Línea de Comandos

-   `-pn`, `--provider-narrador`: Proveedor de la IA Narradora. Opciones: `ollama`, `gemini`, `anthropic`, `openai`. (Por defecto: `gemini`)
-   `-mn`, `--model-narrador`: Nombre del modelo para el Narrador. (Por defecto: `gemini-1.5-flash`)
-   `-pi`, `--provider-investigador`: Proveedor de la IA Investigadora. Opciones: `ollama`, `gemini`, `anthropic`, `openai`. (Por defecto: `gemini`)
-   `-mi`, `--model-investigador`: Nombre del modelo para el Investigador. (Por defecto: `gemini-1.5-flash`)
-   `--turnos`: Número máximo de turnos (preguntas) antes de revelar la solución. (Por defecto: `15`)

### Ejemplos de Ejecución

1.  **Ejecutar con los valores por defecto (Gemini para ambos, 15 turnos):**
    ```bash
    python main.py
    ```

2.  **Usar OpenAI para el Narrador y Gemini para el Investigador, con 10 turnos:**
    ```bash
    python main.py -pn openai -mn gpt-4o -pi gemini -mi gemini-1.5-flash --turnos 10
    ```

3.  **Usar Ollama para ambos roles (asegúrate de que tu servidor Ollama esté corriendo y los modelos estén descargados):**
    ```bash
    python main.py -pn ollama -mn llama3 -pi ollama -mi mistral --turnos 20
    ```

## Estructura del Proyecto

```
.
├── .env.example             # Ejemplo de archivo de configuración de variables de entorno
├── .gitignore               # Archivo para ignorar archivos y directorios en Git
├── main.py                  # Script principal del juego
├── game_prompts.py          # Definiciones de los prompts para las IAs
├── pyproject.toml           # Configuración del proyecto (ej. Poetry)
├── README.md                # Este archivo
├── ai_providers/            # Directorio con las implementaciones de los proveedores de IA
│   ├── __init__.py
│   ├── base_provider.py     # Clase base para los proveedores de IA
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   ├── ollama_provider.py
│   └── openai_provider.py
├── historial_partidas/      # Directorio donde se guardan las transcripciones de las partidas
│   └── partida_YYYYMMDD_HHMMSS.md
└── Prompt_programa/         # Directorio con prompts adicionales o de configuración
    └── Promp_Inicio.txt
```

## Cómo Contribuir

¡Las contribuciones son bienvenidas! Si deseas mejorar BlackStory AI, por favor, sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
3.  Realiza tus cambios y asegúrate de que el código pase las pruebas.
4.  Haz commit de tus cambios (`git commit -m 'feat: Añade nueva característica'`).
5.  Sube tu rama (`git push origin feature/nueva-caracteristica`).
6.  Abre un Pull Request.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
