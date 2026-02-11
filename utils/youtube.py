from youtube_transcript_api import YouTubeTranscriptApi

from googleapiclient.discovery import build

def find_videos(query, api_key, max_results=10):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part="snippet",          # 'snippet' contiene título, descripción, thumbnails
        q=query,                 # Término de búsqueda
        type="video",            # Filtrar por video, channel o playlist
        maxResults=max_results,
        videoDuration = "long" ,               # Opcional: ordenar por fecha (útil para noticias políticas)
        regionCode="PE"          # Opcional: Priorizar resultados de Perú
    )
    response = request.execute()

    resultados = []
    for item in response.get('items', []):
        video_data = {
            'titulo': item['snippet']['title'],
            'video_id': item['id']['videoId'],
            'fecha': item['snippet']['publishedAt'],
            'canal': item['snippet']['channelTitle']
        }
        resultados.append(video_data)
    
    return resultados

def get_transcript(video_id: str, languages: list[str] = ['es']) -> list[dict]:
    """
    Obtiene la transcripción de un video de YouTube dado su ID.
    """

    print(f"Obteniendo transcripción para video ID: {video_id} con idiomas preferidos: {languages}")
    transcript = YouTubeTranscriptApi().fetch(video_id=video_id, languages=languages)
    
    return transcript

def _format_ts(seconds: float) -> str:
    whole = int(seconds)
    hours, rem = divmod(whole, 3600)
    minutes, secs = divmod(rem, 60)
    millis = int(round((seconds - whole) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

# vision-text compression prepared
def save_without_datetime(video_titulo: str, transcript: list[dict], filename: str) -> None:
    """
    Guarda la transcripción en un archivo de texto sin la marca de tiempo de generación.
    """
    header = [
        f"Transcript del video: {video_titulo}",
        f"Total de líneas: {len(transcript)}",
        "",
        "Contenido:",
    ]

    lines = []
    
    text_process = ""
    lenght_phrase = 0

    for entry in transcript:
        text = getattr(entry, "text", entry.text).replace("\n", " ").strip()
        lines.append(f"{text}")
        if lenght_phrase > 600:
            text_process += "\n" + text
            lenght_phrase = 0
        else:
            text_process += " " + text
            lenght_phrase += len(text)
    
    

    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        f.write(text_process)  

def save_transcript_to_file(video_titulo: str, transcript: list[dict], filename: str) -> None:
    """
    Guarda la transcripción en un archivo de texto.
    """
    header = [
        f"Transcript del video: {video_titulo}",
        f"Total de líneas: {len(transcript)}",
        "",
        "Contenido:",
    ]

    lines = []
    for entry in transcript:
        text = getattr(entry, "text", entry.text).replace("\n", " ").strip()
        start = getattr(entry, "start", entry.start)
        lines.append(f"[{_format_ts(float(start))}] {text}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(header + lines))

if __name__ == "__main__":
    trancript = get_transcript("SY22W66tpWQ", languages=['es', 'en'])
    save_transcript_to_file("Integridad Democratica", trancript, "Entrevista.txt")