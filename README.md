# LegalAI Backend

This repository contains the **LegalAI** backend service built with [FastAPI](https://fastapi.tiangolo.com/). It provides API endpoints for user management and authentication, and will serve as the foundation for the LegalDocAI document generation module.

## Project structure

```
legal-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # Application entry point with FastAPI instance
│   │   ├── db.py              # Database setup using SQLAlchemy
│   │   └── auth/              # Authentication package
│   │       ├── __init__.py
│   │       ├── models.py      # SQLAlchemy models for User and RefreshToken
│   │       ├── schemas.py     # Pydantic schemas for requests and responses
│   │       ├── utils.py       # Password hashing & JWT utilities
│   │       └── routes.py      # API routes: register, login, profile
│   ├── routers/
│   │   └── user.py            # Example router (placeholder)
│   ├── schemas/
│   │   └── user.py            # Example Pydantic schema (placeholder)
│   ├── config.py              # Settings and configuration
│   ├── main.py                # Re-exports the app from `app/main.py` for uvicorn
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Optional Dockerfile (not used in tests)
│   └── __init__.py
├── docker-compose.yml         # Compose file for future services
└── README.md                  # Project documentation
```

## Setup

1. **Clone the repository** and change into its directory:

   ```bash
   git clone https://github.com/lescontactrassvet-hub/legal-ai.git
   cd legal-ai
   ```

2. **Create a virtual environment** (optional but recommended) and activate it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the application**:

   ```bash
   uvicorn backend.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

## API Endpoints

### Health check

- `GET /` – Returns a simple message confirming that the service is running.

### Users (demo)

- `GET /users` – Returns a static list of users (placeholder from the original template).
- `POST /users` – Echoes a posted user payload (placeholder).

### Authentication

All authentication endpoints are prefixed with `/auth`.

#### Register

- **Endpoint:** `POST /auth/register`
- **Request body (JSON):**

  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Description:** Creates a new user in the database after hashing their password. Returns the created user.

#### Login

- **Endpoint:** `POST /auth/login`
- **Request type:** `application/x-www-form-urlencoded`
- **Form fields:**
  - `username`: your username or email
  - `password`: your password
- **Description:** Authenticates the user and returns a JSON response with an access token (JWT). Use this token to authenticate subsequent requests.

#### Profile

- **Endpoint:** `GET /auth/profile`
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Description:** Returns the currently authenticated user’s information. Requires a valid JWT obtained from the login endpoint.

## Notes

- The database uses SQLite for local development. The connection URL can be changed in `backend/config.py` or via the `DATABASE_URL` environment variable.
- Passwords are securely hashed using `passlib` with the bcrypt algorithm.
- JWT tokens are generated using `python-jose` and signed with a secret key defined in environment variables.
- The `/users` endpoints are placeholders left from the starter template and can be removed or replaced as the project evolves.

## Next Steps

This repository will be extended with a **LegalDocAI** module for generating legal documents. Future work includes:

- Implementing the LegalDocAI module under `backend/app/legal_doc` with routes and business logic.
- Adding endpoints to create, read, and manage legal document templates.
- Integrating authentication so that only authorized users can generate and manage documents.

If you encounter issues or have suggestions, please open an issue in this repository.
