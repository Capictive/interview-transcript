
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()
def buscar_videos_oficial(query, api_key, max_results=10):
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
            'canal': item['snippet']['channelTitle'],
        }
        resultados.append(video_data)
    
    return resultados

# Uso
api_key = os.environ.get("GENAI_API_KEY", "x")
videos = buscar_videos_oficial("Entrevista Politica Sí Creo Carlos Espá", api_key)
print(videos)
