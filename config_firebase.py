import os
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    # Ruta relativa o absoluta al archivo
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase-service.json')
    print("Ruta a credenciales:", cred_path) 
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en: {cred_path}")
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()
