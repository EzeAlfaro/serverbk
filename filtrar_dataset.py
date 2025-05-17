import pandas as pd
import os

# Rango de filtrado
desde = 202401
hasta = 202412

# Nombre del archivo
archivo = "dataset_empleados_kmeans.xlsx"
ruta_guardado = os.path.join(os.getcwd(), "dataset_empleados_filtrado.xlsx")

# Verificar si el archivo existe
if not os.path.exists(archivo):
    print(f"⚠️ Archivo no encontrado: {archivo}")
else:
    # Leer el dataset
    df = pd.read_excel(archivo)

    # Verificar si la columna Ciclo existe
    if "Ciclo" not in df.columns:
        print("⚠️ La columna 'Ciclo' no existe en el dataset.")
    else:
        # Filtrar el dataset
        df_filtrado = df[(df["Ciclo"] >= desde) & (df["Ciclo"] <= hasta)]

        if df_filtrado.empty:
            print("⚠️ No se encontraron filas dentro del rango especificado.")
        else:
            # Si ya existe el archivo filtrado, borrarlo para evitar errores
            if os.path.exists(ruta_guardado):
                try:
                    os.remove(ruta_guardado)
                    print("🗑️ Archivo existente eliminado antes de guardar el nuevo.")
                except Exception as e:
                    print(f"❌ No se pudo eliminar el archivo existente: {e}")

            # Guardar el nuevo archivo filtrado
            df_filtrado.to_excel(ruta_guardado, index=False)
            print(f"✅ Archivo filtrado guardado con {len(df_filtrado)} filas.")
            print(f"🔽 El archivo se guardó en: {ruta_guardado}")
