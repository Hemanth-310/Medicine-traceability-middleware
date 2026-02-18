from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from datetime import datetime, timedelta
from pymongo import MongoClient
import threading
import time
from config import Config  # Your config file with JWT_SECRET_KEY and Mongo URI

# ------------------------
# Flask App
# ------------------------
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
CORS(app, supports_credentials=True)
jwt = JWTManager(app)

# ------------------------
# MongoDB Connection
# ------------------------
mongo_client = MongoClient(Config.MONGO_URI)  # e.g., "mongodb://localhost:27017/"
db = mongo_client["medicine_traceability"]  # DB name
users_col = db["users"]
batches_col = db["medicine_batches"]

# ------------------------
# Middleware
# ------------------------
@app.before_request
def verify_token_middleware():
    if request.path == "/health":
        return
    if request.endpoint and request.endpoint.startswith("auth"):
        return

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Token missing"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded = decode_token(token)
        request.user = decoded["sub"]
        request.role = decoded.get("role")
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 401

# ------------------------
# Auth Blueprint
# ------------------------
auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:
        return {"error": "Email and password required"}, 400

    if users_col.find_one({"email": email}):
        return {"error": "User already exists"}, 400

    users_col.insert_one({
        "email": email,
        "password": password,
        "role": role
    })
    return {"message": "User registered successfully"}, 201

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = users_col.find_one({"email": email})
    if not user or user["password"] != password:
        return {"error": "Invalid credentials"}, 401

    token = create_access_token(identity=email, additional_claims={"role": user["role"]})
    return {"access_token": token}, 200

# ------------------------
# Role Decorator
# ------------------------
def role_required(*allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_role = getattr(request, "role", None)
            if not user_role:
                return jsonify({"error": "Role missing"}), 403
            if user_role not in allowed_roles:
                return jsonify({"error": "Access forbidden"}), 403
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# ------------------------
# Protected Routes
# ------------------------
protected_bp = Blueprint("protected", __name__, url_prefix="/api")

@protected_bp.get("/profile")
@role_required("user", "admin")
def profile():
    email = request.user
    user = users_col.find_one({"email": email}, {"password": 0, "_id": 0})
    if not user:
        return {"error": "User not found"}, 404
    return {"email": email, "role": user.get("role")}, 200

@protected_bp.get("/regulatory/audit")
@role_required("admin")
def regulatory_audit():
    return {"message": "Regulatory audit access granted"}, 200

def regulatory_audit_job():
    print("Audit started...")
    time.sleep(5)
    print("Audit completed.")

@protected_bp.post("/regulatory/start-audit")
@role_required("admin")
def start_audit():
    thread = threading.Thread(target=regulatory_audit_job)
    thread.start()
    return {"message": "Audit started in background"}, 202

@protected_bp.post("/regulatory/batch-manufacture")
@role_required("admin")
def batch_manufacture():
    data = request.get_json() or {}
    manufacturer = data.get("manufacturer_address")
    if not manufacturer:
        return {"error": "manufacturer_address required"}, 400

    today = datetime.utcnow()
    expiry = today + timedelta(days=365)
    batch_id = f"BATCH-{today.strftime('%Y-%m-%d')}"

    medicine_names = ["PARACETAMOL","IBUPROFEN","AMOXICILLIN","CETIRIZINE","AZITHROMYCIN"]

    batch_docs = []
    for name in medicine_names:
        batch_docs.append({
            "batch_id": batch_id,
            "medicine_name": name,
            "manufacturer": manufacturer,
            "manufactured_at": today,
            "expiry_at": expiry
        })

    batches_col.insert_many(batch_docs)

    return {
        "message": "Batch stored successfully",
        "batch_id": batch_id,
        "count": len(medicine_names)
    }, 201

# ------------------------
# Health Route
# ------------------------
@app.get("/health")
def health():
    return {"status": "middleware version running"}, 200

# ------------------------
# Register Blueprints
# ------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(protected_bp)

# ------------------------
# Run App
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)