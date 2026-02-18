import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret_change_me")
    FIREBASE_CERT_PATH = os.getenv("FIREBASE_CERT_PATH")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")