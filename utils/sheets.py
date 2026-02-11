import gspread

import os
import json
from datetime import datetime

import random

if os.path.exists('credentials.json'):
    gc = gspread.service_account(filename='credentials.json')
else:
    # Leemos el secreto que inyectaremos desde GitHub Actions
    creds_json = os.environ.get('GCP_CREDENTIALS_JSON')
    creds_dict = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds_dict)

sh = gc.open("Partidos Politicos")
worksheet = sh.sheet1

COLUMNS = {
    "ID": "A",
    "Agrupación": "B",
    "Presidente": "C",
    "Vicepresidente": "D",
    "2do Vicepresidente": "E",
    "Transcripación": "F",
    "Historia": "G",
    "UltimaFecha" : "H"
}

NUMBER_OF_PARTIES = 34

def turn_transcription_cell_to_true(row: int) -> None:
    worksheet.update_acell(f"{COLUMNS['Transcripación']}{row}", "TRUE")

def turn_all_transcription_cells_to_false() -> None:
    worksheet.update([["FALSE"] for _ in range(2, NUMBER_OF_PARTIES + 2)], 
                     f"{COLUMNS['Transcripación']}2:{COLUMNS['Transcripación']}{NUMBER_OF_PARTIES + 1}")
    
def select_random_transcription_cell_false() -> int | None:
    """
    Selecciona una fila aleatoria donde la celda de transcripción es FALSE.
    Devuelve el número de fila o None si no se encuentra.
    """
    values = worksheet.get(f"{COLUMNS['Transcripación']}2:{COLUMNS['Transcripación']}{NUMBER_OF_PARTIES + 1}") # Excluye el encabezado
    formated_values = [ v[0].upper() == "FALSE" for v in values ]
    new_values = []
    for index, value in enumerate(formated_values, start=2):  # Comienza en la fila 2
        new_values.append((index, value))
    false_rows = [row for row, is_false in new_values if is_false]
    return random.choice(false_rows) if false_rows else None

def set_last_updated_date(row: int) -> None:
    """
    Establece la fecha de la última actualización en la columna correspondiente para la fila dada.
    """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.update_acell(f"{COLUMNS['UltimaFecha']}{row}", current_date)


def get_relevant_party_info(row: int) -> dict:
    """
    Obtiene la información relevante del partido político en la fila especificada.
    """
    party_info = worksheet.get(f"{COLUMNS['Agrupación']}{row}:{COLUMNS['2do Vicepresidente']}{row}")
    party_dict = {
        "Agrupación": party_info[0][0],
        "Presidente": party_info[0][1],
        "Vicepresidente": party_info[0][2],
        "2do Vicepresidente": party_info[0][3],
    }
    return party_dict

def get_selected_party_info():
    """
    Selecciona aleatoriamente un partido donde transcripción es FALSE y devuelve su info.
    """
    row = select_random_transcription_cell_false()
    if row:
        party_info = get_relevant_party_info(row)
        return party_info, row
    else:
        return None, None

def main_flow():
    row = select_random_transcription_cell_false()
    if row:
        party_info = get_relevant_party_info(row)
        print(f"Procesando partido en fila {row}: {party_info['Agrupación']}")
        # Aquí iría la lógica para obtener y guardar la transcripción
        turn_transcription_cell_to_true(row)
        set_last_updated_date(row)
    else:
        print("No hay partidos pendientes de transcripción.")

# main_flow()  # Comentado para no ejecutar automáticamente