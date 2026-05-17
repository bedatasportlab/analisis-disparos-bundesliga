import pandas as pd

# 1. Cargar tu dataframe completo de eventos
df_eventos = pd.read_parquet("data/processed/events/3895052.parquet")

# 2. Quedarnos SÓLO con el dataframe simple de tiros que tienen un pase previo (key pass)
df_tiros_con_pase = df_eventos[
    (df_eventos['type_name'] == 'Shot') & 
    (df_eventos['shot_key_pass_id'].notna())
].copy()

# Extraemos los IDs únicos que queremos auditar
ids_tiros = df_tiros_con_pase['id'].unique()
ids_pases = df_tiros_con_pase['shot_key_pass_id'].unique()

# 3. Cargar el dataframe 360 del partido
df_360 = pd.read_parquet("data/processed/three-sixty/3895052.parquet")

# Detectar la columna clave (por estándar de SB es event_uuid, pero cubrimos la posibilidad de que sea id)
col_id_360 = 'event_uuid' if 'event_uuid' in df_360.columns else 'id'

# 4. Filtrar el dataframe 360 comprobando qué IDs existen en la capa espacial
tiros_en_360 = df_360[df_360[col_id_360].isin(ids_tiros)][col_id_360].unique()
pases_en_360 = df_360[df_360[col_id_360].isin(ids_pases)][col_id_360].unique()

# 5. Sacar por pantalla el reporte de disponibilidad
print("--- REPORTE DE MATCHING ESPACIAL (360) ---")
print(f"Tiros totales con key_pass previo: {len(ids_tiros)}")
print(f"Tiros con freeze-frame 360 disponible: {len(tiros_en_360)} ({(len(tiros_en_360)/len(ids_tiros))*100:.1f}%)")

print(f"\nPases totales (key_passes): {len(ids_pases)}")
print(f"Pases con freeze-frame 360 disponible: {len(pases_en_360)} ({(len(pases_en_360)/len(ids_pases))*100:.1f}%)")

# (Opcional) Guardar los IDs huérfanos por si necesitas excluirlos de tu matriz
tiros_sin_frame = set(ids_tiros) - set(tiros_en_360)
pases_sin_frame = set(ids_pases) - set(pases_en_360)

if tiros_sin_frame or pases_sin_frame:
    print("\nNota: Existen eventos sin información de 360 grados asociada.")