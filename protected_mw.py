from flask import Blueprint, jsonify, request
from services.firestore_client import get_db
from services.mongo_client import get_mongo_db
from datetime import datetime, timedelta
import threading
import time

protected_mw_bp = Blueprint("protected_mw", __name__, url_prefix="/api")


# -----------------------------------------
# Role Check Function (Manual RBAC)
# -----------------------------------------
def role_required(*allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_role = getattr(request, "role", None)

            if not user_role:
                return jsonify({"error": "Role not found in token"}), 403

            if user_role not in allowed_roles:
                return jsonify({"error": "Access forbidden"}), 403

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# -----------------------------------------
# User Profile
# -----------------------------------------
@protected_mw_bp.get("/profile")
@role_required("user", "admin")
def profile():
    user_id = request.user

    db = get_db()
    doc = db.collection("users").document(user_id).get()

    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    data = doc.to_dict()
    data.pop("password_hash", None)
    data["user_id"] = user_id

    return jsonify(data), 200


# -----------------------------------------
# Admin Audit
# -----------------------------------------
@protected_mw_bp.get("/regulatory/audit")
@role_required("admin")
def regulatory_audit():
    return jsonify({
        "message": "Regulatory audit access granted (Middleware Version)"
    }), 200


def regulatory_audit_job():
    print("Regulatory audit started...")
    time.sleep(5)
    print("Regulatory audit completed.")


@protected_mw_bp.post("/regulatory/start-audit")
@role_required("admin")
def start_regulatory_audit():
    thread = threading.Thread(target=regulatory_audit_job)
    thread.start()

    return jsonify({
        "message": "Regulatory audit started in background"
    }), 202


# -----------------------------------------
# Batch Manufacture
# -----------------------------------------
@protected_mw_bp.post("/regulatory/batch-manufacture")
@role_required("admin")
def batch_manufacture():
    mongo_db = get_mongo_db()
    payload = request.get_json() or {}

    manufacturer_address = payload.get("manufacturer_address")
    if not manufacturer_address:
        return {"error": "manufacturer_address is required"}, 400

    today = datetime.utcnow()
    expiry = today + timedelta(days=365)

    medicine_names = [
        "PARACETAMOL",
        "IBUPROFEN",
        "AMOXICILLIN",
        "CETIRIZINE",
        "AZITHROMYCIN"
    ]

    batch_id = f"BATCH-{today.strftime('%Y-%m-%d')}"

    documents = []
    for name in medicine_names:
        documents.append({
            "batch_id": batch_id,
            "medicine_name": name,
            "manufacturer": manufacturer_address,
            "manufactured_at": today,
            "expiry_at": expiry
        })

    mongo_db.medicine_batches.insert_many(documents)

    return {
        "message": "Medicine batch stored successfully (Middleware Version)",
        "batch_id": batch_id,
        "count": len(documents)
    }, 201
