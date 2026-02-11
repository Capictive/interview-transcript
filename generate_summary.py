import os
import random
import datetime
import requests
from utils.sheets import get_selected_party_info, turn_transcription_cell_to_true, set_last_updated_date
from utils.youtube import find_videos, get_transcript, save_without_datetime
from utils.brain import generation_prompt, client
from google import genai

# Obtener API keys
youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
if not youtube_api_key:
    raise ValueError("YOUTUBE_API_KEY not found in environment variables")

# Paso 1: Obtener info del partido
party_info, row = get_selected_party_info()
if not party_info:
    print("No hay partidos pendientes.")
    exit()

agrupacion = party_info['Agrupación']
presidente = party_info['Presidente']

print(f"Procesando: {agrupacion} - {presidente}")

# Paso 2: Buscar en YouTube
query = f"Entrevista a {presidente} - {agrupacion}"
resultados = find_videos(query, youtube_api_key, max_results=1)
if not resultados:
    print("No se encontraron videos.")
    exit()

video = resultados[0]
titulo = video['titulo']
video_id = video['video_id']
fecha = video['fecha']
canal = video['canal']

print(f"Video encontrado: {titulo} (ID: {video_id})")

# Obtener transcripción
transcript = get_transcript(video_id)
save_without_datetime(titulo, transcript, "TRANSCRIPT.txt")
print("Transcripción guardada en TRANSCRIPT.txt")

# Paso 3: Generar summary con Gemini
pdf_path = f"PLANES DE GOBIERNO/{agrupacion}.pdf"
if not os.path.exists(pdf_path):
    print(f"PDF no encontrado: {pdf_path}")
    exit()

prompt = generation_prompt(titulo, presidente)

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        genai.types.Part.from_text(text=prompt),
        genai.types.Part.from_bytes(data=open(pdf_path, "rb").read(), mime_type="application/pdf"),
        genai.types.Part.from_bytes(data=open("TRANSCRIPT.txt", "rb").read(), mime_type="text/plain"),
    ],
    config=genai.types.GenerateContentConfig(
        response_modalities=["TEXT"],
    )
)

# Generar expediente ID
expediente_id = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

# Escribir SUMMARY.MD con el expediente ID
with open("SUMMARY.MD", "w", encoding="utf-8") as f:
    f.write(f"Expediente ID: {expediente_id}\n\n")
    f.write(response.text)

print(f"SUMMARY.MD creado con Expediente ID: {expediente_id}")

# Actualizar sheets
turn_transcription_cell_to_true(row)
set_last_updated_date(row)
print("Sheets actualizado: Transcripción TRUE y fecha actualizada.")

# Subir a Cloudflare D1
account_id = os.environ.get("ACCOUNT_ID_CF")
api_token = os.environ.get("API_TOKEN_CF")
d1_database_id = os.environ.get("D1_BINDING_ID")

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Insertar en D1
created_at = datetime.date.today().isoformat()
titulo_ia = response.text.strip()  # Contenido completo del análisis

# Extraer hook_ia del response.text
hook_start = response.text.find("## Hook llamativo")
if hook_start != -1:
    hook_ia = response.text[hook_start + len("## Hook llamativo"):].strip()
else:
    hook_ia = "Hook no generado"

video_uploaded_at = fecha[0:10] # Formatear fecha

d1_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{d1_database_id}/query"
d1_data = {
    "sql": "INSERT INTO entrevistas (created_at, entrevista_id, \" youtube_id\", titulo_ia, partido, \"video_uploaded_at\", \"hook_ia\") VALUES (?, ?, ?, ?, ?, ?, ?)",
    "params": [created_at, expediente_id, video_id, titulo_ia, agrupacion, video_uploaded_at, hook_ia]
}
d1_response = requests.post(d1_url, headers=headers, json=d1_data)
if d1_response.status_code == 200:
    print("Datos insertados en D1")
else:
    print(f"Error insertando en D1: {d1_response.text}")