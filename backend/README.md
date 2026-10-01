# TripPlanner Backend

Backend service for **TripPlanner**, a full-stack travel planning application.

The backend is built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**, and exposes a versioned REST API for authentication, user management, trips, destinations, activities, transport, accommodation, expenses, participants, checklists, notes, file management, PDF export and supporting services.

This repository contains the **currently maintained cloud version** of the backend.

> The original academic version developed as part of my Final Degree Project is available in:  
> **https://github.com/Wanakox/trip-planner**

---

## Production Deployment

The backend is currently deployed as a **Render Web Service** and uses **Supabase** for PostgreSQL and file storage.

- **Backend:** https://trip-planner-cloud.onrender.com
- **Swagger / OpenAPI:** https://trip-planner-cloud.onrender.com/docs
- **Health check:** https://trip-planner-cloud.onrender.com/api/v1/health
- **Frontend:** https://trip-planner-frontend-vnir.onrender.com

---

## Main Technologies

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Psycopg
- Pydantic / Pydantic Settings
- PyJWT
- pwdlib with Argon2
- Supabase
- HTTPX
- ReportLab
- Pytest
- Pytest-Cov
- Ruff
- Uvicorn

---

## Architecture

The backend follows a layered architecture with separation of responsibilities.

```text
HTTP Request
    │
    ▼
┌───────────────────────┐
│ Routers / Endpoints   │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Services              │
│ Business logic        │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Repositories          │
│ Persistence logic     │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ SQLAlchemy / Supabase │
│ PostgreSQL            │
└───────────────────────┘
```

Additional shared responsibilities are grouped under `core/`, while external integrations are isolated from the application logic.

---

## Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/
│   ├── integrations/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── db/
│   ├── __init__.py
│   └── main.py
├── database/
│   ├── schema.sql
│   └── supabase_setup.sql
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Main Modules

### `app/main.py`

FastAPI application entry point.

It:

- creates the FastAPI application instance;
- configures metadata;
- enables OpenAPI documentation;
- includes the main API router;
- applies application-level middleware and settings;
- exposes the backend service.

The API is served with Uvicorn.

### `app/api/`

Contains the HTTP API.

The current API version is exposed under:

```text
/api/v1
```

Endpoints are grouped by resource and responsibility, including authentication, users, trips, destinations, activities, transport, accommodation, expenses, participants, tasks, notes, files, exports, currency and health checks.

### `app/core/`

Contains shared infrastructure and configuration.

Typical responsibilities include:

- application settings;
- JWT configuration;
- security helpers;
- exception handling;
- file and storage helpers;
- reusable infrastructure.

### `app/db/`

Contains SQLAlchemy database session configuration.

It creates:

- the SQLAlchemy engine;
- the session factory;
- the database dependency used by the application.

The database URL is loaded from environment configuration.

### `app/models/`

Contains SQLAlchemy persistence models representing the relational database entities.

### `app/schemas/`

Contains Pydantic schemas used for:

- request validation;
- response serialization;
- data transfer between application layers.

### `app/repositories/`

Contains persistence and database query logic.

Repositories isolate SQLAlchemy access from higher application layers.

### `app/services/`

Contains application and business logic.

Services coordinate repositories, validation, external integrations and transaction handling.

### `app/integrations/`

Contains integrations with external services used by the backend.

### `tests/`

Contains the automated backend test suite.

Tests use **Pytest**, FastAPI's **TestClient**, fixtures, mocks and monkeypatching where appropriate.

---

## Main Functional Areas

The backend currently supports:

- User registration
- Email verification
- Login and JWT authentication
- Access and refresh tokens
- Profile management
- Default currency selection
- Account deletion
- Trip CRUD
- Destination CRUD and reordering
- Activity CRUD, completion and reordering
- Transport management
- Accommodation management
- Participant management
- Expense tracking
- Checklists and tasks
- Notes
- File upload and deletion
- Profile image storage
- PDF trip export
- Currency conversion
- Health monitoring

---

## Authentication and Security

Authentication is based on JWT access and refresh tokens.

Default token lifetimes:

```text
Access token: 30 minutes
Refresh token: 7 days
```

The backend also includes:

- password hashing with Argon2;
- protected API routes;
- resource ownership checks;
- server-side validation;
- email verification before login;
- environment-based secrets;
- file ownership validation;
- cascading deletion of related data.

JWT secrets and infrastructure credentials must never be committed to Git.

---

## Email Verification

Account verification is performed by email before login is allowed.

The backend uses **Brevo SMTP** for outgoing verification emails.

Relevant environment variables include:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
FRONTEND_URL
```

Verification links expire after a limited period.

Unverified registrations can be removed automatically using a Supabase/PostgreSQL scheduled cleanup job.

---

## Database

The backend uses PostgreSQL through SQLAlchemy.

### Relational schema

The canonical relational schema is stored in:

```text
database/schema.sql
```

This file represents the current database structure for a fresh installation.

### Supabase-specific setup

Provider-specific database configuration is stored separately in:

```text
database/supabase_setup.sql
```

This can contain features such as scheduled cleanup jobs that depend on Supabase or PostgreSQL extensions such as `pg_cron`.

Keeping provider-specific configuration separate avoids coupling the main relational schema to Supabase.

---

## File Storage

The cloud deployment uses **Supabase Storage**.

Files include:

- user profile pictures;
- trip documents.

When a trip or account is deleted, the application attempts to remove the associated storage objects before deleting the related database rows.

Storage and PostgreSQL do not share a distributed transaction, so storage failures are handled defensively to reduce inconsistent states.

---

## Environment Variables

Create a local environment file from the template:

```bash
cp .env.example .env
```

The backend configuration includes variables such as:

```dotenv
DATABASE_URL=postgresql+psycopg://user:password@host:5432/database

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=false

JWT_SECRET_KEY=replace-with-random-secret

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=replace-with-supabase-secret

SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=2525
SMTP_USERNAME=replace-with-brevo-smtp-login
SMTP_PASSWORD=replace-with-brevo-smtp-key
SMTP_FROM_EMAIL=verified-sender@example.com

FRONTEND_URL=http://localhost:5173
```

Real credentials must never be committed.

---

## Local Development

Requirements:

- Python 3.12+
- PostgreSQL-compatible database
- Python virtual environment recommended

From the `backend/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Configure the required environment variables in `.env`, then start the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Health check:

```text
http://localhost:8000/api/v1/health
```

---

## Running Tests

From the `backend/` directory:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest -v tests/test_health.py
```

Coverage is configured through `pyproject.toml`.

---

## Code Quality

Check the backend with Ruff:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Apply automatic linting fixes:

```bash
ruff check . --fix
```

Apply formatting:

```bash
ruff format .
```

Recommended validation before committing:

```bash
pytest
ruff check .
ruff format --check .
```

---

## Cloud Deployment

### Render

The backend is deployed as a Render Web Service.

Typical production start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables are configured in Render and are not stored in the repository.

### Supabase

Supabase provides:

- PostgreSQL;
- file storage;
- provider-specific database features used by the project.

### Brevo

Brevo SMTP is used for verification email delivery.

---

## Health Check

Available endpoint:

```text
GET /api/v1/health
```

A successful response indicates that the API is running and that the database is reachable.

Example:

```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## Development Practices

The backend applies practices such as:

- layered architecture;
- separation of responsibilities;
- repository and service layers;
- RESTful API design;
- server-side validation;
- transaction handling;
- secure password hashing;
- token-based authentication;
- automated testing;
- linting and formatting;
- environment-based configuration;
- version control with Git.

---

## Project Background

TripPlanner originated as my Final Degree Project in Computer Engineering at the University of Córdoba.

The original backend was part of the complete academic project and was initially deployed in a self-hosted environment.

Development later continued in this repository to adapt the application to a public cloud deployment using Render and Supabase.

Original academic repository:

**https://github.com/Wanakox/trip-planner**

---

## Author

**Juan García Moreno**  
Computer Engineering Graduate

- GitHub: https://github.com/Wanakox
- Portfolio: https://wanakox.github.io
- LinkedIn: https://www.linkedin.com/in/juan-garcía-moreno

---

## License

This project is distributed under the terms defined in the repository's `LICENSE` file.