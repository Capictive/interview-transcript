
import os
from utils import sheets, brain, youtube

PLANES_DIR = "PLANES DE GOBIERNO"
TRANSCRIPT_FILE = "Entrevista.txt"

def get_party_pdfs():
    pdfs = [f for f in os.listdir(PLANES_DIR) if f.endswith(".pdf")]
    # Filtrar solo los que terminan en "nombre".pdf
    filtered = [f for f in pdfs if f.lower().endswith("nombre.pdf")]
    return filtered

def get_all_parties():
    # Asume que la hoja tiene 34 partidos
    parties = []
    for row in range(2, sheets.NUMBER_OF_PARTIES + 2):
        info = sheets.get_relevant_party_info(row)
        parties.append(info)
    return parties

def main():
    # 1. Obtener PDFs de planes de gobierno
    pdfs = get_party_pdfs()
    # 2. Obtener nombres de partidos
    parties = get_all_parties()
    # 3. Procesar cada partido
    for party in parties:
        nombre = party["Agrupación"]
        presidente = party["Presidente"]
        # Buscar PDF correspondiente
        pdf_file = None
        for pdf in pdfs:
            if nombre.lower() in pdf.lower():
                pdf_file = os.path.join(PLANES_DIR, pdf)
                break
        if not pdf_file:
            print(f"No se encontró PDF para {nombre}")
            continue

        # 4. Buscar video y generar transcript real

        api_key = os.environ.get("YOUTUBE_API_KEY")

        query = f"Entrevista a {presidente} - {nombre}"
        videos = youtube.find_videos(query, api_key, max_results=1)
        if not videos:
            print(f"No se encontró video para {nombre} ({presidente})")
            continue
        video = videos[0]
        video_id = video['video_id']
        video_title = video['titulo']
        transcript = youtube.get_transcript(video_id, languages=['es', 'en'])
        youtube.save_transcript_to_file(video_title, transcript, TRANSCRIPT_FILE)

    # 5. Ejecutar análisis con brain.py usando el transcript generado
    with open(pdf_file, "rb") as f_pdf, open(TRANSCRIPT_FILE, "rb") as f_tr:
        prompt = brain.generation_prompt(video_title, presidente)
        response = brain.client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                brain.genai.types.Part.from_text(text=prompt),
                brain.genai.types.Part.from_bytes(data=f_pdf.read(), mime_type="application/pdf"),
                brain.genai.types.Part.from_bytes(data=f_tr.read(), mime_type="text/plain"),
            ],
            config=brain.genai.types.GenerateContentConfig(
                response_modalities=["TEXT"],
            )
        )
        print(f"Análisis para {nombre} ({presidente}):\n", response)

if __name__ == "__main__":
    main()
