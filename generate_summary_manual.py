import os
import random
import datetime
import argparse
import requests
from utils.youtube import get_transcript, save_without_datetime
from utils.brain import generation_prompt, client
from google import genai


def main():
    parser = argparse.ArgumentParser(description="Generar resumen manual usando PDF y transcripción de YouTube")
    parser.add_argument("--agrupacion", required=True, help="Nombre de la agrupación / partido")
    parser.add_argument("--presidente", required=True, help="Nombre del candidato/entrevistado")
    parser.add_argument("--video-id", required=True, help="ID del video de YouTube")
    parser.add_argument("--titulo", required=False, help="Título del video (opcional)")
    parser.add_argument("--fecha", required=False, help="Fecha del video en formato ISO (opcional)")
    parser.add_argument("--transcript-path", required=False, help="Ruta a un archivo de transcripción ya existente (opcional)")
    args = parser.parse_args()

    agrupacion = args.agrupacion
    presidente = args.presidente
    video_id = args.video_id
    titulo = args.titulo or f"video_{video_id}"
    fecha = args.fecha or ""
    
    print(f"Procesando manual: {agrupacion} - {presidente} - Video ID: {video_id}")

    # Obtener transcripción (o usar archivo existente si se pasa)
    if args.transcript_path:
        if not os.path.exists(args.transcript_path):
            print(f"Archivo de transcripción no encontrado: {args.transcript_path}")
            return
        with open(args.transcript_path, "r", encoding="utf-8") as src, open("TRANSCRIPT.txt", "w", encoding="utf-8") as dst:
            dst.write(src.read())
        print(f"Usando transcripción existente: {args.transcript_path} -> TRANSCRIPT.txt")
    else:
        transcript = get_transcript(video_id)
        save_without_datetime(titulo, transcript, "TRANSCRIPT.txt")
        print("Transcripción guardada en TRANSCRIPT.txt")

    # Cargar PDF del partido
    pdf_path = f"PLANES DE GOBIERNO/{agrupacion}.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF no encontrado: {pdf_path}")
        return

    prompt = generation_prompt(titulo, presidente)

    with open(pdf_path, "rb") as pdf_file, open("TRANSCRIPT.txt", "rb") as transcript_file:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                genai.types.Part.from_text(text=prompt),
                genai.types.Part.from_bytes(data=pdf_file.read(), mime_type="application/pdf"),
                genai.types.Part.from_bytes(data=transcript_file.read(), mime_type="text/plain"),
            ],
            config=genai.types.GenerateContentConfig(response_modalities=["TEXT"]),
        )

    expediente_id = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

    with open("SUMMARY.MD", "w", encoding="utf-8") as f:
        f.write(f"Expediente ID: {expediente_id}\n\n")
        text_out = getattr(response, "text", None) or str(response)
        f.write(text_out)

    print(f"SUMMARY.MD creado con Expediente ID: {expediente_id}")

    # Intentar insertar en Cloudflare D1 si hay credenciales
    account_id = os.environ.get("ACCOUNT_ID_CF")
    api_token = os.environ.get("API_TOKEN_CF")
    d1_database_id = os.environ.get("D1_BINDING_ID")

    if not (account_id and api_token and d1_database_id):
        print("No se encontraron credenciales D1 en variables de entorno; se omite inserción en D1.")
        return

    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    created_at = datetime.date.today().isoformat()
    titulo_ia = text_out.strip()

    hook_start = text_out.find("## Hook llamativo")
    if hook_start != -1:
        hook_ia = text_out[hook_start + len("## Hook llamativo"):].strip()
    else:
        hook_ia = "Hook no generado"

    video_uploaded_at = fecha[0:10] if fecha else ""

    d1_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{d1_database_id}/query"
    d1_data = {
        "sql": "INSERT INTO entrevistas (created_at, entrevista_id, \" youtube_id\", titulo_ia, partido, \"video_uploaded_at\", \"hook_ia\") VALUES (?, ?, ?, ?, ?, ?, ?)",
        "params": [created_at, expediente_id, video_id, titulo_ia, agrupacion, video_uploaded_at, hook_ia],
    }

    d1_response = requests.post(d1_url, headers=headers, json=d1_data)
    if d1_response.status_code == 200:
        print("Datos insertados en D1")
    else:
        print(f"Error insertando en D1: {d1_response.text}")


if __name__ == "__main__":
    main()
