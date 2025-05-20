import os
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_clave = os.path.join(ruta_actual, "firebase-service.json")
    cred = credentials.Certificate(ruta_clave)
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()
