import json
import pandas as pd
from pathlib import Path
import os

def procesar_a_parquet(ruta_entrada: Path, ruta_salida: Path):
    """
    Lee un JSON, lo aplana, limpia columnas problemáticas para Parquet
    y lo guarda en la ruta de destino.
    """
    if not ruta_entrada.exists():
        print(f"⚠️ Aviso: No se encontró {ruta_entrada.name} en {ruta_entrada.parent}")
        return

    with open(ruta_entrada, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Aplanar el JSON
    df = pd.json_normalize(data, sep='_')

    # Parquet (pyarrow) no soporta columnas que mezclen tipos o contengan listas/diccionarios complejos.
    # Convertimos esas estructuras residuales a texto para asegurar una exportación limpia.
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].astype(str)

    # Guardar en formato columnar optimizado
    df.to_parquet(ruta_salida, engine='pyarrow', index=False)


def main():
    # 1. Definir rutas base utilizando pathlib
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")

    # 2. Recrear el árbol de directorios en 'processed'
    carpetas = ["events", "lineups", "matches", "three-sixty"]
    for carpeta in carpetas:
        (processed_dir / carpeta).mkdir(parents=True, exist_ok=True)

    # 3. Leer el archivo de partidos (matches/9/281.json)
    # StatsBomb guarda los matches estructurados por {competition_id}/{season_id}.json
    ruta_matches = raw_dir / "matches" / "9" / "281.json"
    ruta_matches_out = processed_dir / "matches" / "281.parquet"

    print(f"Abriendo el registro de partidos: {ruta_matches}")
    
    with open(ruta_matches, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    df_matches = pd.json_normalize(matches_data, sep='_')
    
    # Limpieza rápida para el archivo de matches
    for col in df_matches.columns:
         if df_matches[col].apply(lambda x: isinstance(x, (list, dict))).any():
             df_matches[col] = df_matches[col].astype(str)
             
    df_matches.to_parquet(ruta_matches_out, engine='pyarrow', index=False)
    
    lista_partidos = df_matches['match_id'].unique().tolist()
    total_partidos = len(lista_partidos)
    print(f"✅ Se han encontrado {total_partidos} partidos para procesar.\n")

    # 4. Iterar sobre cada match_id y procesar sus respectivos JSONs
    for i, match_id in enumerate(lista_partidos, 1):
        print(f"[{i}/{total_partidos}] Procesando partido ID: {match_id}...")
        
        # Archivo Events
        procesar_a_parquet(
            ruta_entrada = raw_dir / "events" / f"{match_id}.json",
            ruta_salida = processed_dir / "events" / f"{match_id}.parquet"
        )
        
        # Archivo Lineups
        procesar_a_parquet(
            ruta_entrada = raw_dir / "lineups" / f"{match_id}.json",
            ruta_salida = processed_dir / "lineups" / f"{match_id}.parquet"
        )
        
        # Archivo Three-Sixty
        procesar_a_parquet(
            ruta_entrada = raw_dir / "three-sixty" / f"{match_id}.json",
            ruta_salida = processed_dir / "three-sixty" / f"{match_id}.parquet"
        )

    print("\n🚀 ¡Procesamiento completado con éxito! Todos los archivos están listos en formato .parquet.")

if __name__ == "__main__":
    main()