
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import json
import os
import logging
from config_postgres import get_connection
import pandas as pd


app = Flask(__name__)
CORS(app)
# CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500", "https://TU_DOMINIO_PRODUCCION"])

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ruta al script K-Means (usando la ruta absoluta)
KMEANS_SCRIPT = os.path.abspath("K-Means-Rotacion.py")


    
def ejecutar_kmeans():
    """Ejecuta el script K-Means y captura la salida."""
    try:
        # Ejecuta el script y captura la salida
        resultado = subprocess.run(['python', KMEANS_SCRIPT], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
        # Carga la salida JSON directamente
        json_resultado = json.loads(resultado.stdout)
        return json_resultado

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar K-Means: {e.stderr}")
        raise Exception(f"Error al ejecutar K-Means: {e.stderr}")
    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar JSON: {e}")
        raise Exception(f"Error al decodificar JSON: {e}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/kmeans', methods=['POST'])
def kmeans_endpoint():
    data = request.get_json()
    desde = data.get('desde')
    hasta = data.get('hasta')

    if desde is None or hasta is None:
        return jsonify({"error": "Faltan parámetros 'desde' o 'hasta'"}), 400

    try:
        desde = int(desde)
        hasta = int(hasta)
    except ValueError:
        return jsonify({"error": "Parámetros 'desde' y 'hasta' deben ser enteros"}), 400
    
    filtro = filtrar_dataset(desde, hasta)
    if "error" in filtro:
        return jsonify(filtro), 400

    try:
        resultado_kmeans = ejecutar_kmeans()
        # resultado_kmeans ya tiene la estructura {"data": [...]}
        # Por eso acá devolvemos directo el resultado sin envolverlo de nuevo
        return jsonify(resultado_kmeans), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import request, jsonify
import psycopg2
from psycopg2.extras import execute_values

def get_connection():
    return psycopg2.connect(
        host="ainabi-ainabi.g.aivencloud.com",
        port=14186,
        database="defaultdb",
        user="avnadmin",
        password="AVNS_-cITT1QVqP0nWCD-E9E",
        sslmode="require"
    )

@app.route('/guardar_resultados', methods=['POST'])
def guardar_resultados():
    datos = request.json.get('resultados')
    if not datos:
        return jsonify({"error": "No hay datos para guardar"}), 400
    
    # Conexión y query para insertar varios registros rápido
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Asumiendo que cada dict en datos tiene las columnas: Nombre, AusenciasInjustificadas, etc.
        # Ajustá los nombres y orden según tu tabla
        query = """
            INSERT INTO resultados_kmeans 
            (nombre, ausencias_injustificadas, llegadas_tarde, rendimiento_alto, rendimiento_bajo, rendimiento_medio, salidas_tempranas, cluster, probabilidad_rotacion)
            VALUES %s
        """
        
        valores = [
            (
                d['Nombre'],
                d['Ausencias Injustificadas'],
                d['Llegadas tarde'],
                d['Rendimiento ACTUAL_Alto'],
                d['Rendimiento ACTUAL_Bajo'],
                d['Rendimiento ACTUAL_Medio'],
                d['Salidas tempranas'],
                d['Cluster'],
                d['Probabilidad de Rotación']
            ) for d in datos
        ]

        execute_values(cursor, query, valores)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Datos guardados en PostgreSQL exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ciclos', methods=['GET'])
def obtener_ciclos():
    archivo = "dataset_empleados_kmeans.xlsx"

    if not os.path.exists(archivo):
        return jsonify({"error": f"Archivo no encontrado: {archivo}"}), 404

    df = pd.read_excel(archivo)

    if "Ciclo" not in df.columns:
        return jsonify({"error": "La columna 'Ciclo' no existe en el dataset."}), 400

    ciclos_unicos = sorted(df["Ciclo"].dropna().unique().tolist())

    return jsonify(ciclos_unicos), 200



def filtrar_dataset(desde, hasta):
    archivo = "dataset_empleados_kmeans.xlsx"
    ruta_guardado = os.path.join(os.getcwd(), "dataset_empleados_filtrado.xlsx")

    if not os.path.exists(archivo):
        return {"error": "Archivo no encontrado"}

    df = pd.read_excel(archivo)
    if "Ciclo" not in df.columns:
        return {"error": "La columna 'Ciclo' no existe"}

    df_filtrado = df[(df["Ciclo"] >= desde) & (df["Ciclo"] <= hasta)]

    if df_filtrado.empty:
        return {"error": "No hay filas en el rango especificado"}

    if os.path.exists(ruta_guardado):
        try:
            os.remove(ruta_guardado)
        except Exception as e:
            return {"error": f"No se pudo eliminar el archivo previo: {e}"}

    df_filtrado.to_excel(ruta_guardado, index=False)
    return {"ok": f"Archivo guardado con {len(df_filtrado)} filas"}


if __name__ == '__main__':
    app.run(debug=True)
