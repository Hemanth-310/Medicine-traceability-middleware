# Medicine Traceability — Middleware Layer

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)

Flask middleware layer for the Medicine Traceability system, demonstrating global JWT authentication using Flask's `before_request` hook instead of per-route decorators — a cleaner pattern for APIs where most routes require authentication.

Built during my Backend Developer Internship at Farm To Plate (January–May 2026), assigned by my backend mentor to implement and compare middleware-based vs decorator-based auth patterns.

---

## Key Concept — Middleware vs Decorator Auth

This is the core thing this repo demonstrates:

```python
# Decorator approach — must add @jwt_required() to every route
@app.route('/api/profile')
@jwt_required()
def profile():
    ...

# Middleware approach — one global check covers all /api/ routes
@app.before_request
def authenticate():
    if request.path.startswith('/api/'):
        # validate JWT once, here, for everything
        ...
```

**Why middleware is better for larger APIs:** as the number of routes grows, forgetting a single `@jwt_required()` decorator creates a security hole. Middleware authentication is enforced globally — no route can accidentally be left unprotected.

---

## Features

- Global JWT authentication via `before_request` — no per-route decorators
- Role-based access control (user / admin)
- MongoDB integration for users and medicine batch storage
- Background job support for long-running audit operations
- Public routes (`/auth/register`, `/auth/login`, `/health`) bypass middleware automatically

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask |
| Authentication | JWT (PyJWT) |
| Database | MongoDB |
| Auth Strategy | Global middleware via `before_request` |

---

## Project Structure

```
Medicine-traceability-middleware/
├── middlewareapp.py        # Main app — global before_request auth
├── middlewareapp1.py       # Alternate version for comparison
├── protected_mw.py         # Protected route handlers
├── config.py               # JWT secret and DB config
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.10+
- MongoDB 6.0+ running locally

### 1. Clone the repository

```bash
git clone https://github.com/Hemanth-310/Medicine-traceability-middleware.git
cd Medicine-traceability-middleware
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
JWT_SECRET=your_secret_key_here
FIREBASE_CERT_PATH=path_to_firebase_cert.json
FIREBASE_PROJECT_ID=your_firebase_project_id
MONGO_URI=mongodb://localhost:27017/medicine_trace
```

### 5. Run the app

```bash
python middlewareapp.py
```

Server runs at `http://127.0.0.1:5000`

---

## API Demo

### Register a user

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "hemanth@example.com", "password": "secure123", "role": "user"}'
```

### Login and get JWT token

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "hemanth@example.com", "password": "secure123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Access protected profile route

```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer <your_token>"
```

### Register a medicine batch (admin only)

```bash
curl -X POST http://localhost:5000/api/regulatory/batch-manufacture \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"manufacturer_address": "XYZ Pharma"}'
```

### Try accessing without token — blocked by middleware

```bash
curl -X GET http://localhost:5000/api/profile
```

Response:
```json
{
  "error": "Authorization token missing or invalid"
}
```

---

## Full API Reference

| Method | Endpoint | Auth Required | Role |
|--------|----------|--------------|------|
| POST | `/auth/register` | No | — |
| POST | `/auth/login` | No | — |
| GET | `/health` | No | — |
| GET | `/api/profile` | Yes | user / admin |
| GET | `/api/regulatory/audit` | Yes | admin |
| POST | `/api/regulatory/start-audit` | Yes | admin |
| POST | `/api/regulatory/batch-manufacture` | Yes | admin |

---

## Related Repos

This is the middleware layer extracted from the broader Medicine Traceability system:

- [`Medicine-Traceability`](https://github.com/Hemanth-310/Medicine-Traceability) — original full-stack version with Solidity smart contracts + Flask backend
- [`medicine-traceability-js`](https://github.com/Hemanth-310/medicine-traceability-js) — Node.js + Express backend rewrite

---

## Author

**Hemanth E B**  
Backend Developer Intern, Farm To Plate (Jan–May 2026)  
[LinkedIn](https://www.linkedin.com/in/hemanth10) · [GitHub](https://github.com/Hemanth-310)
