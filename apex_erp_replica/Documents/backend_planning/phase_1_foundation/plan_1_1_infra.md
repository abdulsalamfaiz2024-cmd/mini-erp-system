# Plan 1.1: Environment & Infrastructure (Exhaustive Detail)

## 1. Scope & Objective
This document provides the absolute blueprint for setting up the Python development environment and the foundational directory logic. No code should be written until these specifications are verified.

---

## 2. Dependency Specification (requirements.txt)
Every package listed below has a specific role in the Apex ERP architecture. Unauthorized additions are prohibited.

| Package | Version | Justification |
| :--- | :---: | :--- |
| **fastapi** | ^0.104.0 | High-performance API framework with automated Pydantic validation. |
| **uvicorn[standard]** | ^0.23.0 | The lightning-fast ASGI server implementation for production-grade reliability. |
| **sqlalchemy** | ^2.0.0 | The industry-standard ORM for mapping complex ERP entities to relational tables. |
| **pydantic[email]** | ^2.4.0 | Data validation and settings management using Python type annotations. |
| **python-jose[cryptography]** | ^3.3.0 | Required for generating and verifying JWT tokens for secure authentication. |
| **passlib[bcrypt]** | ^1.7.0 | Secure password hashing algorithm to prevent plain-text credential leaks. |
| **python-multipart** | ^0.0.6 | Necessary for handling form-data submissions (e.g., File uploads, rich forms). |
| **psycopg2-binary** | ^2.9.0 | The low-level PostgreSQL adapter for Python. |
| **python-dotenv** | ^1.0.0 | Securely loads environment variables from `.env` files to prevent secret leakage. |

---

## 3. Configuration & Secret Management (`.env`)
The `.env` file is the most sensitive file in the system. It must never be committed to version control.

| Variable Name | Description | Default/Example Value |
| :--- | :--- | :--- |
| `ERP_ENV` | Current system state (development/production). | `development` |
| `DATABASE_URL` | Full connection string for the PostgreSQL instance. | `postgresql://user:pass@localhost:5432/apex_erp` |
| `SECRET_KEY` | High-entropy string for JWT signature encryption. | `[64-byte random hex string]` |
| `ALGORITHM` | Encryption algorithm for security tokens. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Limit for how long a user session lasts before logout. | `480` (8 Hours) |

---

## 4. Directory Structure Refinement
The `Backend/` directory must be strictly organized to ensure separate models can interact without circular dependencies.

```text
Backend/
├── main.py              # Application entry point & Global middleware.
├── requirements.txt     # List of all system dependencies.
├── .env                 # System-wide secrets and configurations.
├── core/                # System-level logic.
│   ├── config.py        # Global settings loader using Pydantic BaseSettings.
│   ├── security.py      # Token generation and password hashing functions.
│   └── database.py      # SQLAlchemy engine and SessionLocal setup.
├── api/                 # Endpoint delivery layer.
│   ├── auth.py          # Login, Registration, and Password Reset routes.
│   └── dependencies.py  # Dependency Injection functions (e.g., GetCurrentUser).
├── models/              # Database Schema (SQLAlchemy).
│   └── base.py          # The Base class and shared mixins (CreatedAt/UpdatedAt).
├── schemas/             # Data Contract layer (Pydantic).
│   └── token.py         # Response structures for authentication tokens.
└── controllers/         # Business logic & Orchestration (Pure Python).
    └── auth_manager.py  # Logic for verifying credentials against DB.
```

---

## 5. Verification Steps (The "Check-Go" Protocol)
Before proceeding to Step 1.2:
1. [ ] **Virtual Env Check**: Verify `python -m venv venv` is active.
2. [ ] **Install Check**: Run `pip install -r requirements.txt` and verify zero errors.
3. [ ] **Dotenv Check**: Create `.env` and verify `core/config.py` can read the `DATABASE_URL`.
4. [ ] **Uvicorn Check**: Start the server; access `/docs` and verify the Swagger UI loads.
