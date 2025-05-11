
from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os
import logging


app = Flask(__name__)


# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ruta al script K-Means (usando la ruta absoluta)
KMEANS_SCRIPT = os.path.abspath("K-Means-Rotacion.py")
FILTRAR_SCRIPT = os.path.abspath("filtrar_dataset.py") #nuevo

def ejecutar_filtrado():
    """Ejecuta el script de filtrado sin necesidad de variables externas."""
    try:
        resultado = subprocess.run(
            ['python', FILTRAR_SCRIPT],  # Ejecutamos sin parámetros
            capture_output=True, 
            text=True, 
            check=True
        )
        logging.info("✅ Filtrado ejecutado correctamente.")
        return True
    except Exception as e:
        logging.error(f"Error general al ejecutar el filtrado: {e}")
        return False
    
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
    """Endpoint para ejecutar el proceso K-Means luego del filtrado"""
    
    try:
        if ejecutar_filtrado(): #nuevo
            resultado_kmeans = ejecutar_kmeans()
            return jsonify(resultado_kmeans), 200
        else:
            return jsonify({"error": "No se pudo ejecutar el filtrado correctamente."}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)