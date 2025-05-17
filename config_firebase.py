import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    firebase_json = os.environ.get("FIREBASE_KEY")
    if not firebase_json:
        raise ValueError("La variable de entorno FIREBASE_KEY no está definida")
    # Convertimos el string JSON a dict
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()