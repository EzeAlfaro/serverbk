import os
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet

def init_firebase():
    clave_ferret = os.environ.get('KEY_FERRET')
    if not clave_ferret:
        raise ValueError("No se encontró la variable de entorno KEY_FERRET")

    fernet = Fernet(clave_ferret.encode())

    enc_path = os.path.join(os.path.dirname(__file__), 'service-firebase.enc')
    if not os.path.exists(enc_path):
        raise FileNotFoundError(f"No se encontró el archivo encriptado en: {enc_path}")

    with open(enc_path, 'rb') as f:
        data_encriptada = f.read()

    data_json = fernet.decrypt(data_encriptada)

    if not firebase_admin._apps:
        cred = credentials.Certificate(data_json)
        firebase_admin.initialize_app(cred)

    return firestore.client()

db = init_firebase()

