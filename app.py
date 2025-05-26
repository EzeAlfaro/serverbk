from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from K_Means_Rotacion import ejecutar_kmeans
import json
import os
import logging
from config_postgres import get_connection
from psycopg2.extras import execute_values
import pandas as pd
import requests

app = Flask(__name__)
CORS(app)
# CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500", "https://TU_DOMINIO_PRODUCCION"])

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reporteria')
def reporteria():
    return render_template('reporteria.html')

@app.route('/kmeans', methods=['GET', 'POST'])
@app.route('/api/kmeans', methods=['GET', 'POST'])
def kmeans_endpoint():
    if request.method == 'POST':
        try:
            data = request.get_json(force=True, silent=True)
        except Exception:
            data = None
        desde = data.get('desde') if data and data.get('desde') is not None else 202404
        hasta = data.get('hasta') if data and data.get('hasta') is not None else 202504
    else:
        # Para GET, toma los parámetros de la URL o usa valores por defecto
        desde = request.args.get('desde', 202404)
        hasta = request.args.get('hasta', 202504)

    try:
        desde = int(desde)
        hasta = int(hasta)
    except (ValueError, TypeError):
        return jsonify({"error": "Parámetros 'desde' y 'hasta' deben ser enteros"}), 400
    
    filtro = filtrar_dataset(desde, hasta)
    if "error" in filtro:
        return jsonify(filtro), 400

    try:
        resultado_kmeans = ejecutar_kmeans()
        return jsonify(resultado_kmeans), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            (nombre, ausencias_injustificadas, llegadas_tarde, rendimiento_alto, rendimiento_bajo, rendimiento_medio, salidas_tempranas, cluster, probabilidad_rotacion, desde, hasta)
            VALUES %s
        """
        
        valores = [
            (
                d['Nombre'],
                d['Ausencias Injustificadas'],
                d['Llegadas tarde'],
                d['Rendimiento Alto'],
                d['Rendimiento Bajo'],
                d['Rendimiento Medio'],
                d['Salidas tempranas'],
                d['Cluster'],
                d['Probabilidad de Rotacion'],
                d['DESDE'],
                d['HASTA']
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



@app.route('/mi-ip-publica')
def mi_ip_publica():
    ip = requests.get('https://api.ipify.org').text
    return f"Mi IP pública es: {ip}"


@app.route('/api/metabase_card/<int:card_id>', methods=['GET'])
def metabase_card(card_id):
    METABASE_URL = "http://54.172.128.185:3000"
    METABASE_USER = "ceciliactorales@gmail.com"
    METABASE_PASS = "AINABI2025"

    # Autenticación
    auth_res = requests.post(f"{METABASE_URL}/api/session", json={
        "username": METABASE_USER,
        "password": METABASE_PASS
    })
    if not auth_res.ok:
        return jsonify({"error": "No se pudo autenticar con Metabase"}), 500

    token = auth_res.json()['id']

    # Consulta la tarjeta
    headers = {"X-Metabase-Session": token}
    query_res = requests.get(f"{METABASE_URL}/api/card/{card_id}/query/json", headers=headers)

    if not query_res.ok:
        return jsonify({"error": "No se pudo obtener datos de Metabase"}), 500

    return jsonify(query_res.json())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
