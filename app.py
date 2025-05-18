
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import json
import os
import logging
from config_firebase import db
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

@app.route('/guardar_resultados', methods=['POST'])
def guardar_resultados():
    try:
        print("Existe archivo firebase?", os.path.exists('/opt/render/project/src/firebase-service.json'))
        data = request.get_json()
        if data is None:
            print("❌ No se recibió JSON.")
            return jsonify({"error": "No se recibió JSON válido"}), 400

        resultados = data.get('resultados', [])
        print(f"📥 Recibidos {len(resultados)} resultados para guardar.")

        for resultado in resultados:
            db.collection('resultados_kmeans').add(resultado)

        print("✅ Datos guardados correctamente.")
        return jsonify({"message": "Datos guardados correctamente."}), 200

    except Exception as e:
        print(f"❌ Error al guardar en Firebase: {e}")
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
