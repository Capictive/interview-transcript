# Avance del Proyecto: Análisis de Entrevistas Políticas Peruanas

## Descripción del Proyecto
Este proyecto automatiza el análisis de entrevistas políticas en Perú, comparando discursos de candidatos presidenciales con sus planes de gobierno oficiales. Utiliza APIs de YouTube para obtener transcripciones, Gemini (Google Generative AI) para análisis inteligente, y Google Sheets para gestionar el estado de procesamiento de partidos políticos.

## Funcionalidades Implementadas

### 1. Gestión de Partidos Políticos (utils/sheets.py)
- Conexión a Google Sheets para almacenar información de partidos políticos peruanos.
- Función `get_selected_party_info()`: Selecciona aleatoriamente un partido donde la transcripción no ha sido procesada (columna "Transcripación" = FALSE).
- Funciones para marcar partidos como procesados (`turn_transcription_cell_to_true()`) y actualizar fechas (`set_last_updated_date()`).
- Manejo seguro de credenciales vía variables de entorno o archivo credentials.json.

### 2. Procesamiento de Videos de YouTube (utils/youtube.py)
- Búsqueda de entrevistas usando query "Entrevista a {presidente} - {agrupación}".
- Obtención de metadatos del video: título, ID, fecha de publicación y canal.
- Descarga y guardado de transcripciones en formato TXT (`save_without_datetime()`).
- Soporte para videos largos y en español/peruano.

### 3. Análisis con IA (utils/brain.py)
- Prompt estructurado para Gemini que genera un resumen comparativo en Markdown.
- Comparación entre puntos clave de la entrevista y el plan de gobierno oficial.
- Evaluación de coherencia en categorías como seguridad ciudadana, derechos humanos, política exterior, etc.
- Salida en formato Markdown con secciones claras y evaluaciones (Coherente, Parcialmente Coherente, No Coherente).

### 4. Script Principal (generate_summary.py)
- Integración completa del flujo: selección de partido → búsqueda de video → transcripción → análisis con Gemini → generación de SUMMARY.MD.
- Generación de ID único de expediente (formato "EXPEDIENTE XXXX-XXXX-XXXX") para identificación y recuperación posterior.
- Actualización automática de Google Sheets tras procesamiento exitoso.
- Manejo de errores para APIs faltantes o archivos no encontrados.

## Pasos Realizados
1. **Configuración del Entorno**: Instalación de dependencias (gspread, google-api-python-client, youtube-transcript-api, google-genai).
2. **Modificación de Módulos Existentes**: Actualización de utils/sheets.py y utils/brain.py para integración.
3. **Creación del Script Automatizado**: Desarrollo de generate_summary.py que ejecuta todo el proceso de manera secuencial.
4. **Pruebas y Debugging**: Resolución de errores de importación, paths y dependencias.

## Próximos Pasos
- Configurar variables de entorno (YOUTUBE_API_KEY, GENAI_API_KEY, GCP_CREDENTIALS_JSON) para ejecución completa.
- Ejecutar el script en producción para generar los primeros SUMMARY.MD.
- Implementar logging más detallado y manejo de excepciones.
- Agregar validación de PDFs de planes de gobierno.
- Posible expansión: Procesamiento por lotes, interfaz web o integración con bases de datos.

## Archivos Clave
- `generate_summary.py`: Script principal de ejecución.
- `utils/sheets.py`: Gestión de datos en Google Sheets.
- `utils/youtube.py`: Interacción con YouTube API.
- `utils/brain.py`: Generación de prompts y llamadas a Gemini.
- `PLANES DE GOBIERNO/`: Carpeta con PDFs de planes de gobierno.
- `SUMMARY.MD`: Archivo de salida generado (con expediente ID).

## Notas Técnicas
- Lenguaje: Python 3.13
- APIs: YouTube Data API v3, Google Generative AI, Google Sheets API
- Dependencias: Instaladas vía pip
- Seguridad: Uso de variables de entorno para claves sensibles, no commitear secrets.

Este proyecto facilita el análisis objetivo de discursos políticos, promoviendo transparencia electoral mediante comparación automática con documentos oficiales.