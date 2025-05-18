import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    key_json = os.getenv("FIREBASE_KEY")
    if not key_json:
        raise ValueError("La variable de entorno FIREBASE_KEY no está definida")

    cred_dict = json.loads(key_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()
