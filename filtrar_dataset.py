import pandas as pd
import os

desde=  "202401"
hasta = "202412"

def filtrar_dataset(desde, hasta):
    archivo = "dataset_empleados_kmeans.xlsx"
    ruta_guardado = os.path.join(os.getcwd(), "dataset_empleados_filtrado.xlsx")

    if not os.path.exists(archivo):
        print(f"⚠️ Archivo no encontrado: {archivo}")
        return  # importante para evitar que siga si falla

    df = pd.read_excel(archivo)

    if "Ciclo" not in df.columns:
        print("⚠️ La columna 'Ciclo' no existe en el dataset.")
        return

    df_filtrado = df[(df["Ciclo"] >= int(desde)) & (df["Ciclo"] <= int(hasta))]

    if df_filtrado.empty:
        print("⚠️ No se encontraron filas dentro del rango especificado.")
        return

    df_filtrado.to_excel(ruta_guardado, index=False)
    print(f"✅ Archivo filtrado guardado con {len(df_filtrado)} filas.")
    print(f"🔽 El archivo se guardó en: {ruta_guardado}")
    return True