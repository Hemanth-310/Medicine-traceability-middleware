
---

## **Overview**

- **JWT Authentication:** Tokens are generated during login/register and stored client-side.  
- **Middleware Authentication:** Instead of `@jwt_required` per route, all requests (except public ones) are checked globally using Flask’s `@app.before_request`.  
- **Protected Routes:** Routes under `/api/...` are accessible only if the JWT token is valid.  
- **Roles:** Role-based access control is implemented (user/admin).  
- **MongoDB Integration:** Stores medicine batches and user info in MongoDB for persistence.

---

## **Installation**

1. Clone the repository:
```bash
git clone https://github.com/Hemanth-310/Medicine-traceability-middleware.git
```
```bash
cd Medicine-traceability-middleware
```
2. Create a virtual environment:
```bash
python -m venv venv
```
```bash
source venv/bin/activate
```

3.  Install dependencies:
```bash
pip install -r requirements.txt
```

4.  Create a .env file (or set environment variables) with:
```bash
JWT_SECRET=your_secret_key_here
FIREBASE_CERT_PATH=path_to_firebase_cert.json
FIREBASE_PROJECT_ID=your_firebase_project_id
MONGO_URI=mongodb://localhost:27017/medicine_trace
```

5.  Running the App
```bash
python middlewareapp.py
```
OR
```bash
python middlewareapp1.py
```

App runs at 
```bash
http://127.0.0.1:5000/
```

## **API Endpoints**

GET	```/health ```		Check if app is running

POST	```/auth/register```	{"email": "...", "password": "...", "role": "user/admin"}	Register a new user

POST	```/auth/login```	{"email": "...", "password": "..."}	Get JWT token for authentication

- **Protected (Requires JWT)**

Include header: Authorization: Bearer <JWT_TOKEN>

- **Method	Endpoint**    

GET	```/api/profile```	None	Returns logged-in user profile

GET	```/api/regulatory/audit```	None	Admin-only regulatory audit access

POST	```/api/regulatory/start-audit```	None	Admin-only, starts background audit job

POST	```/api/regulatory/batch-manufacture```	{"manufacturer_address": "XYZ Pharma"}	Admin-only, stores new medicine batch in MongoDB

- **Testing**

Use Postman or cURL to test endpoints.

Register a user and login to get JWT.

Include Authorization: Bearer <token> in headers for protected routes.

MongoDB collections users and medicine_batches will store data.

MongoDB setup: ```mongodb://localhost:27017/medicine_trace.```

- **Key Concepts**

Middleware vs JWT Decorators:

@jwt_required() checks token per route.

Middleware (@app.before_request) checks token globally for all protected routes.

Role-Based Access: Users have user or admin role; middleware passes role info for route checks.

Background Jobs: Long-running operations (audit) are run in threads.
