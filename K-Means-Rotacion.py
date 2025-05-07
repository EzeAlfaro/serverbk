#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
import numpy as np
from sklearn.decomposition import PCA
import pickle
import json
import os
import logging
import sys

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ruta relativa al archivo actual
ruta_dataset = os.path.join(os.path.dirname(__file__), "dataset_empleados_kmeans.txt")
logging.info(f"Intentando cargar dataset desde: {ruta_dataset}")

try:
    dataset = pd.read_csv(ruta_dataset, sep='\t')  # Leemos el .txt con separador de tabulaciones
except FileNotFoundError:
    logging.error(f"No se encontró el archivo: {ruta_dataset}")
    print(json.dumps({"error": f"No se encontró el archivo: {ruta_dataset}"}))
    sys.exit(1)  # Salir con código de error
except Exception as e:
    logging.error(f"Error al cargar el dataset: {str(e)}")
    print(json.dumps({"error": f"Error al procesar el archivo: {str(e)}"}))
    sys.exit(1)

# Procesamiento de datos
codificador = OneHotEncoder()
codificacion = codificador.fit_transform(dataset[["Rendimiento ACTUAL"]])
nuevas_cols = pd.DataFrame(
    codificacion.toarray(),
    columns=codificador.get_feature_names_out(["Rendimiento ACTUAL"])
)
dataset = pd.concat([dataset, nuevas_cols], axis="columns")
dataset = dataset.drop("Rendimiento ACTUAL", axis=1)

columnas_numericas = dataset.columns.difference(["Nombre", "Ciclo"]).tolist()
dataset_agrupado_por_Nombre = dataset.groupby("Nombre")[columnas_numericas].sum().reset_index()

# Escalado de características
escalador = MinMaxScaler()
columnas_a_escalar = [
    "Ausencias Injustificadas",
    "Llegadas tarde",
    "Rendimiento ACTUAL_Alto",
    "Rendimiento ACTUAL_Bajo",
    "Rendimiento ACTUAL_Medio",
    "Salidas tempranas"
]

dataset_agrupado_por_Nombre_escalado = dataset_agrupado_por_Nombre.copy()
dataset_agrupado_por_Nombre_escalado[columnas_a_escalar] = escalador.fit_transform(
    dataset_agrupado_por_Nombre_escalado[columnas_a_escalar]
)

# Aplicación de K-Means
n_clusters = 3
X = dataset_agrupado_por_Nombre_escalado.drop(['Nombre'], axis=1)
kmeans = KMeans(n_clusters=n_clusters, random_state=12)
dataset_agrupado_por_Nombre_escalado['Cluster'] = kmeans.fit_predict(X)

# Mapeo de clusters a probabilidades
dataset_agrupado_por_Nombre["Cluster"] = dataset_agrupado_por_Nombre_escalado["Cluster"]
dataset_agrupado_por_Nombre["Probabilidad de Rotacion"] = dataset_agrupado_por_Nombre["Cluster"].map({
    2: "ALTA",
    0: "BAJA",
    1: "MEDIA"  # Corregido typo "MEDIA" (antes decía "MEDIA")
})

# Salida JSON
if __name__ == "__main__":
    resultados = {
        "data": dataset_agrupado_por_Nombre.to_dict(orient="records"),
        "clusters": n_clusters,
        "status": "success"
    }
    
    try:
        json_output = json.dumps(resultados, ensure_ascii=False)
        print(json_output)
        logging.info("Proceso K-Means completado exitosamente")
    except Exception as e:
        logging.error(f"Error al generar JSON: {str(e)}")
        print(json.dumps({"error": "Error al generar resultados", "status": "error"}))
        sys.exit(1)