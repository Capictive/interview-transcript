from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id: str, languages: list[str] = ['es']) -> list[dict]:
    """
    Obtiene la transcripción de un video de YouTube dado su ID.
    """
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


trancript = get_transcript("Yum8lIUTu5E", languages=['es', 'en'])
save_transcript_to_file("SíCreo", trancript, "Elecciones 2027 ¿Cuáles son las propuestas electorales del partido SíCreo.txt")