import firebase_admin
from firebase_admin import credentials, db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "../firebase/travel-with-northern-valley-firebase-adminsdk-fbsvc-3aa4152aa6.json")

print("Using Firebase credential at:", cred_path)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://travel-with-northern-valley-default-rtdb.firebaseio.com/'
    })
