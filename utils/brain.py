from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(
    api_key=os.environ.get("GENAI_API_KEY", "x")
)

def generation_prompt(video_title: str, president: str) -> str:
    return \
    f"""

    Actúa como un Analista de Datos Cívicos y Políticas Públicas Comparadas. Tu objetivo es procesar la entrevista "TRANSCRIPT.TXT" con "PLAN GOBIERNO.pdf" a
    {president}, candidato presidencial de Perú, titulada "{video_title}".

    Devuelve un formato markdown con los siguientes apartados y solo esto, nada más:
    # [Titulo que tu le pongas al análisis]
    
    ## Puntos clave de la entrevista

    **Candidato:** {{NOMBRE_DEL_CANDIDATO}}  
    **Partido político:** {{PARTIDO_POLITICO}}  
    **Fuente:** {{ENTREVISTA / MEDIO / FECHA}}  

    A continuación se presentan los principales puntos expresados por el candidato durante la entrevista.

    ### 🗝️ 5-10 key points (Coloca este nombre tal y como esta)
    1. {{KEY_POINT_1}}
    2. {{KEY_POINT_2}}
    3. {{KEY_POINT_3}}
    4. {{KEY_POINT_4}}
    5. {{KEY_POINT_5}}
    ...

    ---

    ## Comparación con el plan de gobierno

    Se evalúa la coherencia entre las declaraciones del candidato y el plan de gobierno oficial de su partido político.
    Ojo, para la comparación con el plan de gobierno se muy específico en cada categoría. No me des un detalle como
    "El candidato se expreso de una forma diferente" = Parcialmente Coherente, sino que detalla qué dijo el candidato y qué dice el plan de gobierno en cada categoría.

    ---
    // Estas categorías por ejemplo, si es que la entrevista se enfoca en 1 de estas, se puede colocar más de 1 vez esa categoría.

    ### 🔐 Seguridad ciudadana
    - **Lo dicho en la entrevista:** {{RESUMEN_DISCURSO_SEGURIDAD}}
    - **Lo establecido en el plan:** {{RESUMEN_PLAN_SEGURIDAD}}

    **Evaluación:** {{✔️ Coherente | 🟡 Parcialmente coherente | 🔴 No coherente}}

    ---

    ### ⚖️ Derechos humanos y uso de la fuerza
    - **Lo dicho en la entrevista:** {{RESUMEN_DISCURSO_DDHH}}
    - **Lo establecido en el plan:** {{RESUMEN_PLAN_DDHH}}

    **Evaluación:** {{✔️ | 🟡 | 🔴}}

    ---

    ### ☠️ Sistema penal y sanciones
    - **Lo dicho en la entrevista:** {{RESUMEN_DISCURSO_PENAL}}
    - **Lo establecido en el plan:** {{RESUMEN_PLAN_PENAL}}

    **Evaluación:** {{✔️ | 🟡 | 🔴}}

    ---

    ### 🌎 Política exterior y soberanía
    - **Lo dicho en la entrevista:** {{RESUMEN_DISCURSO_EXTERIOR}}
    - **Lo establecido en el plan:** {{RESUMEN_PLAN_EXTERIOR}}

    **Evaluación:** {{✔️ | 🟡 | 🔴}}

    ---

    ### 💰 Lucha contra la corrupción
    - **Lo dicho en la entrevista:** {{RESUMEN_DISCURSO_CORRUPCION}}
    - **Lo establecido en el plan:** {{RESUMEN_PLAN_CORRUPCION}}

    **Evaluación:** {{✔️ | 🟡 | 🔴}}

    ---

    ## Evaluación general de coherencia

    **Nivel de coherencia observado:** {{ALTO | MEDIO | BAJO}}

    **Conclusión:**  
    {{RESUMEN_FINAL_NEUTRAL_DE_2_3_LÍNEAS}}

    > **Nota metodológica:**
    > Este análisis se basa en información pública disponible y evalúa la coherencia entre discurso y plan de gobierno. No constituye una recomendación electoral.

    ---

    ## Hook llamativo

    Genera un título corto, llamativo y atractivo para este análisis, que resuma el contenido principal y capte la atención. Ejemplo: "¡Incoherencias alarmantes en el discurso de [partido] sobre seguridad!"


    """



# Example usage (commented out)
# response = client.models.generate_content(
#     model="gemini-3-pro-preview",
#     contents=[
#         genai.types.Part.from_text(text=generation_prompt(
#             video_title="Entrevista Politica Sí Creo Carlos Espá", president="Carlos Espá")),
#         genai.types.Part.from_bytes(data=open("PLAN GOBIERNO.pdf", "rb").read(), mime_type="application/pdf"),
#         genai.types.Part.from_bytes(data=open("TRANSCRIPT.txt", "rb").read(), mime_type="text/plain"),
#     ],
#     config=genai.types.GenerateContentConfig(
#         response_modalities=["TEXT"],
#     )
# )
