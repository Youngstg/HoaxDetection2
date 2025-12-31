import firebase_admin
from firebase_admin import credentials, firestore
import os

_db = None

def initialize_firebase():
    global _db
    if _db is not None:
        return _db

    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at {cred_path}. "
                "Please download it from Firebase Console and update FIREBASE_CREDENTIALS_PATH in .env"
            )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("Firebase initialized successfully")
        return _db
    except ValueError:
        # App already initialized
        _db = firestore.client()
        return _db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

def get_db():
    global _db
    if _db is None:
        _db = initialize_firebase()
    return _db
