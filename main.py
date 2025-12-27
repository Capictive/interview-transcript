from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
from utils import youtube
# ID del video (lo que está después de v= en la URL)
video_id = "KoSUo-dWxIU"

try:
    # Esto obtiene el texto casi instantáneamente porque ya existe en los servidores de YT
    transcript = YouTubeTranscriptApi().fetch(video_id=video_id,languages=['es', 'en'])
    
    print("Subtítulos encontrados:")
    for entry in transcript:
        print(f"{entry.start:.2f}s - {entry.text}")
    print(f"Total de líneas de subtítulos: {len(transcript)}")
    def _format_ts(seconds: float) -> str:
        whole = int(seconds)
        hours, rem = divmod(whole, 3600)
        minutes, secs = divmod(rem, 60)
        millis = int(round((seconds - whole) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    filename = f"transcript_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    header = [
        f"Transcript del video: {video_id}",
        f"Generado: {datetime.now().isoformat(timespec='seconds')}",
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

    print(f"Archivo de subtítulos guardado: {filename}")
        
except Exception as e:
    print(f"No se encontraron subtítulos: {e}")
