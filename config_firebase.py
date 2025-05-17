import os
import json
import base64
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    # Leer la clave secreta de encriptación de la variable de entorno
    secret_key = os.environ.get('FIREBASE_SECRET_KEY')
    if not secret_key:
        raise ValueError("No se encontró la clave secreta FIREBASE_SECRET_KEY en variables de entorno")

    # Leer el JSON encriptado de la variable de entorno (base64)
    encrypted_json_b64 = os.environ.get('FIREBASE_ENCRYPTED_JSON')
    if not encrypted_json_b64:
        raise ValueError("No se encontró FIREBASE_ENCRYPTED_JSON en variables de entorno")

    # Inicializar Fernet con la clave
    fernet = Fernet(secret_key)

    # Decodificar base64 y desencriptar
    encrypted_json_bytes = base64.b64decode(encrypted_json_b64)
    decrypted_json_bytes = fernet.decrypt(encrypted_json_bytes)

    # Parsear JSON a dict
    cred_dict = json.loads(decrypted_json_bytes.decode('utf-8'))

    # Inicializar Firebase solo si no está inicializado
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()

db = init_firebase()
