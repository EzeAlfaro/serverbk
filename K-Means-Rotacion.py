#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
import numpy as np
import os
import json
import logging
import sys

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ruta dataset
ruta_dataset = os.path.join(os.path.dirname(__file__), "dataset_empleados_filtrado.xlsx")
logging.info(f"🟡 DEBUG: Buscando archivo en {ruta_dataset}")

# Intentar cargar dataset
try:
    dataset = pd.read_excel(ruta_dataset)
except Exception as e:
    logging.error(f"❌ Error al cargar dataset: {str(e)}")
    print(json.dumps({"error": f"No se pudo cargar el archivo: {str(e)}"}))
    sys.exit(1)

# Codificación y preprocesamiento
try:
    codificador = OneHotEncoder()
    codificacion = codificador.fit_transform(dataset[["Rendimiento ACTUAL"]])
    nuevas_cols = pd.DataFrame(codificacion.toarray(), columns=codificador.get_feature_names_out(["Rendimiento ACTUAL"]))
    dataset = pd.concat([dataset, nuevas_cols], axis="columns")
    dataset = dataset.drop("Rendimiento ACTUAL", axis=1)

    columnas_numericas = dataset.columns.difference(["Nombre", "Ciclo"]).tolist()
    dataset_agrupado_por_Nombre = dataset.groupby("Nombre")[columnas_numericas].sum().reset_index()

    # Escalado
    escalador = MinMaxScaler()
    columnas_a_escalar = [
        "Ausencias Injustificadas", "Llegadas tarde",
        "Rendimiento ACTUAL_Alto", "Rendimiento ACTUAL_Bajo",
        "Rendimiento ACTUAL_Medio", "Salidas tempranas"
    ]
    dataset_agrupado_por_Nombre_escalado = dataset_agrupado_por_Nombre.copy()
    dataset_agrupado_por_Nombre_escalado[columnas_a_escalar] = escalador.fit_transform(
        dataset_agrupado_por_Nombre_escalado[columnas_a_escalar]
    )

    # KMeans
    n_clusters = 3
    X = dataset_agrupado_por_Nombre_escalado.drop(['Nombre'], axis=1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=12)
    dataset_agrupado_por_Nombre_escalado['Cluster'] = kmeans.fit_predict(X)

    # Mapeo
    dataset_agrupado_por_Nombre["Cluster"] = dataset_agrupado_por_Nombre_escalado["Cluster"]
    dataset_agrupado_por_Nombre["Probabilidad de Rotacion"] = dataset_agrupado_por_Nombre["Cluster"].map({
        2: "ALTA", 0: "BAJA", 1: "MEDIA"
    })

    dataset_agrupado_por_Nombre["DESDE"] = dataset["Ciclo"].min()
    dataset_agrupado_por_Nombre["HASTA"] = dataset["Ciclo"].max()

    # Renombrar
    dataset_agrupado_por_Nombre = dataset_agrupado_por_Nombre.rename(columns={
        "Rendimiento ACTUAL_Alto": "Rendimiento Alto",
        "Rendimiento ACTUAL_Bajo": "Rendimiento Bajo",
        "Rendimiento ACTUAL_Medio": "Rendimiento Medio"
    })

    columnas_ordenadas = [
        "Nombre", "DESDE", "HASTA", "Cluster", "Probabilidad de Rotacion",
        "Ausencias Injustificadas", "Llegadas tarde",
        "Rendimiento Alto", "Rendimiento Bajo", "Rendimiento Medio", "Salidas tempranas"
    ]
    dataset_agrupado_por_Nombre = dataset_agrupado_por_Nombre[columnas_ordenadas]

    # Output
    resultados = {
        "data": dataset_agrupado_por_Nombre.to_dict(orient="records"),
        "clusters": n_clusters,
        "status": "success"
    }

    json_output = json.dumps(resultados, ensure_ascii=False)
    logging.info("🟢 JSON generado correctamente.")
    print(json_output)

except Exception as e:
    logging.error(f"❌ Error en procesamiento: {str(e)}")
    print(json.dumps({"error": "Error al generar resultados", "status": "error"}))
    sys.exit(1)
