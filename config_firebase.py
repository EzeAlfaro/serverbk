import os
import json
from firebase_admin import credentials, initialize_app, firestore

json_str = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
json_data = json.loads(json_str.replace('\\n', '\n'))

cred = credentials.Certificate(json_data)
initialize_app(cred)

db = firestore.client()
