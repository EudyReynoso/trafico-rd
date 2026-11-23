
from pathlib import Path

import pandas as pd



# 1. Directorio raíz del proyecto
ROOT = (
    Path.cwd().parent
    if Path.cwd().name == "notebooks"
    else Path.cwd()
)

# 2. Rutas de datos
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"

archivo = DATA_RAW / "Infracciones-de-Transito-DIGESETT-2018-2026.csv"

# Verificar existencia del archivo
if not archivo.exists():
    raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

# 3. Cargar datos
df = pd.read_csv(
    archivo,
    encoding="cp1252",
    sep=";"
)

# 4. Definir los meses
meses = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL",
    "MAYO", "JUNIO", "JULIO", "AGOSTO",
    "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

# Verificar columnas necesarias
columnas_requeridas = ["INFRACCIONES", "AÑO"] + meses
faltantes = set(columnas_requeridas) - set(df.columns)

if faltantes:
    raise ValueError(f"Faltan columnas en el CSV: {faltantes}")

# 5. Transformar formato ancho a largo
df_largo = df.melt(
    id_vars=["INFRACCIONES", "AÑO"],
    value_vars=meses,
    var_name="MES",
    value_name="CANTIDAD"
)

# 6. Normalizar y validar tipos
df_largo["INFRACCIONES"] = (
    df_largo["INFRACCIONES"]
    .astype("string")
    .str.strip()
)

df_largo["AÑO"] = pd.to_numeric(
    df_largo["AÑO"], errors="coerce"
)

df_largo["CANTIDAD"] = pd.to_numeric(
    df_largo["CANTIDAD"], errors="coerce"
)

# 7. Validación inicial
print("=== VALIDACIÓN INICIAL ===")
print("Dimensiones originales:", df.shape)
print("Dimensiones transformadas:", df_largo.shape)

print("\nTipos de datos:")
print(df_largo.dtypes)

print("\nValores faltantes:")
print(df_largo.isna().sum())

print("\nFilas duplicadas:")
print(df_largo.duplicated().sum())

duplicados_clave = df_largo.duplicated(
    subset=["INFRACCIONES", "AÑO", "MES"]
)

print("\nDuplicados por infracción, año y mes:")
print(duplicados_clave.sum())

print("\nRegistros por mes:")
print(df_largo["MES"].value_counts())

print("\nRango de años:")
print(df_largo["AÑO"].min(), "-", df_largo["AÑO"].max())

# 8. Revisar totales mensuales de 2026
print("\n=== TOTALES MENSUALES DE 2026 ===")

resumen_2026 = (
    df[df["AÑO"] == 2026][meses]
    .sum()
    .reindex(meses)
)

print(resumen_2026)

# 9. Identificar meses con suma igual a cero
print("\n=== MESES CON TOTAL CERO ===")

resumen_mensual = (
    df_largo
    .groupby(["AÑO", "MES"])["CANTIDAD"]
    .sum()
    .reset_index()
)

meses_cero = resumen_mensual[
    resumen_mensual["CANTIDAD"] == 0
].sort_values(["AÑO", "MES"])

print(meses_cero.to_string(index=False))

# 10. Excluir provisionalmente agosto-diciembre de 2026
meses_sin_datos_2026 = [
    "AGOSTO", "SEPTIEMBRE", "OCTUBRE",
    "NOVIEMBRE", "DICIEMBRE"
]

df_analisis = df_largo[
    ~(
        (df_largo["AÑO"] == 2026)
        & (df_largo["MES"].isin(meses_sin_datos_2026))
    )
].copy()

# 11. Crear variables cronológicas
orden_meses = {
    mes: numero
    for numero, mes in enumerate(meses, start=1)
}

df_analisis["MES_NUM"] = df_analisis["MES"].map(orden_meses)

df_analisis["FECHA"] = pd.to_datetime(
    dict(
        year=df_analisis["AÑO"],
        month=df_analisis["MES_NUM"],
        day=1
    ),
    errors="coerce"
)

# 12. Ordenar cronológicamente
df_analisis = df_analisis.sort_values(
    ["FECHA", "INFRACCIONES"]
).reset_index(drop=True)

# 13. Validación final
print("\n=== CONJUNTO PARA ANÁLISIS ===")
print("Filas transformadas:", len(df_largo))
print("Filas para análisis:", len(df_analisis))

print("\nDimensiones:", df_analisis.shape)

print("\nValores faltantes:")
print(df_analisis.isna().sum())

print("\nPrimeros registros:")
print(df_analisis.head(10))

# 14. Exportar datos procesados
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

salida = DATA_PROCESSED / "infracciones_transito_limpio.csv"

df_analisis.to_csv(
    salida,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nArchivo exportado correctamente: {salida}")
