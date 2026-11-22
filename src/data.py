
import pandas as pd

# 1. Cargar los datos originales
archivo = "data/Infracciones-de-Transito-DIGESETT-2018-2026.csv"

df = pd.read_csv(
    archivo,
    encoding="cp1252",
    sep=";"
)

# 2. Definir los meses
meses = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL",
    "MAYO", "JUNIO", "JULIO", "AGOSTO",
    "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

# 3. Transformar los datos de formato ancho a formato largo
df_largo = df.melt(
    id_vars=["INFRACCIONES", "AÑO"],
    value_vars=meses,
    var_name="MES",
    value_name="CANTIDAD"
)

# 4. Validar la transformación
print("=== VALIDACIÓN INICIAL ===")
print("Dimensiones originales:", df.shape)
print("Dimensiones transformadas:", df_largo.shape)

print("\nValores faltantes:")
print(df_largo.isna().sum())

print("\nFilas duplicadas:")
print(df_largo.duplicated().sum())

print("\nCantidad de registros por mes:")
print(df_largo["MES"].value_counts())

print("\nRango de años:")
print(df_largo["AÑO"].min(), "-", df_largo["AÑO"].max())

# 5. Revisar los totales mensuales de 2026
print("\n=== TOTALES MENSUALES DE 2026 ===")

resumen_2026 = (
    df[df["AÑO"] == 2026][meses]
    .sum()
    .reindex(meses)
)

print(resumen_2026)

# 6. Identificar meses con suma igual a cero
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

# 7. Crear una copia para el análisis
# Excluir provisionalmente agosto-diciembre de 2026.
# No se modifica el DataFrame original.

meses_sin_datos_2026 = [
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE"
]

df_analisis = df_largo[
    ~(
        (df_largo["AÑO"] == 2026)
        & (df_largo["MES"].isin(meses_sin_datos_2026))
    )
].copy()

# 8. Mostrar el resultado final
print("\n=== CONJUNTO PARA ANÁLISIS ===")
print("Filas originales transformadas:", len(df_largo))
print("Filas para análisis:", len(df_analisis))

print("\nPrimeros registros:")
print(df_analisis.head(10))

print("\nDimensiones del conjunto de análisis:")
print(df_analisis.shape)

# 9. Exportar datos para Power BI
salida = "data/infracciones_transito_limpio.csv"

df_analisis.to_csv(
    salida,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nArchivo exportado correctamente: {salida}")