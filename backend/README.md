# TripPlanner Backend

The TripPlanner backend is a REST API developed with FastAPI and PostgreSQL. It provides the server-side foundation for managing users, trips, destinations, activities, transportation, accommodation, expenses, participants, checklists, notes, and files.

The backend runs inside Docker and is designed to be reproducible across development environments and future deployment targets, including a Raspberry Pi.

## Main Technologies

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL 17
- Psycopg
- Pydantic Settings
- Pytest
- Ruff
- Uvicorn
- Docker
- Docker Compose

## Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── health.py
│   │       └── router.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── session.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── .dockerignore
├── .env.example
├── Dockerfile
├── pyproject.toml
├── README.md
└── start.sh
```

## Directory Description

### `app/`

Main Python package of the backend application.

### `app/main.py`

FastAPI application entry point.

This file:

- creates the FastAPI application instance;
- configures the application metadata;
- enables the OpenAPI documentation;
- includes the main API router;
- exposes the root endpoint.

The API is served with Uvicorn.

### `app/api/`

Contains the HTTP API routes.

The current API version is organized under:

```text
/api/v1
```

### `app/api/v1/endpoints/`

Contains the endpoints grouped by resource or functional area.

The current implementation includes:

```text
health.py
```

The health endpoint checks that:

- the FastAPI application is running;
- the PostgreSQL database is reachable.

Available endpoint:

```text
GET /api/v1/health
```

Expected successful response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### `app/api/v1/router.py`

Main router for API version 1.

It includes the routers defined in the different endpoint modules. Future modules such as authentication, users, trips, activities, and expenses will be registered here.

### `app/core/`

Contains shared application configuration.

### `app/core/config.py`

Loads environment variables through Pydantic Settings and exposes the centralized backend configuration.

The configuration includes values such as:

- application name;
- API version;
- backend host;
- backend port;
- reload mode;
- PostgreSQL connection URL.

### `app/db/`

Contains the database configuration.

### `app/db/session.py`

Creates:

- the SQLAlchemy engine;
- the SQLAlchemy session factory;
- the connection configuration used to communicate with PostgreSQL.

The database URL is obtained from the environment configuration.

### `tests/`

Contains the backend automated tests.

Test files must follow the naming pattern:

```text
test_*.py
```

The current `test_health.py` verifies that:

- the health endpoint returns HTTP 200 when the database is available;
- the expected JSON response is returned;
- the endpoint returns HTTP 503 when the database connection fails.

### `Dockerfile`

Defines the backend Docker image.

The image:

1. uses Python 3.12 Slim as its base;
2. configures Python and pip environment variables;
3. copies `pyproject.toml`;
4. copies the application source code;
5. installs the project and development dependencies;
6. exposes port 8000;
7. starts the API with Uvicorn.

### `pyproject.toml`

Defines:

- project metadata;
- runtime dependencies;
- development dependencies;
- Python version requirements;
- Pytest configuration;
- Ruff linting configuration;
- Ruff formatting configuration;
- the Python build system.

### `start.sh`

Starts the complete TripPlanner development environment from the repository root.

The script:

- checks that Docker is installed and available;
- verifies that the root `.env` file exists;
- verifies that `docker-compose.yml` exists;
- starts the Docker Compose services;
- optionally rebuilds the backend image;
- waits until the health endpoint responds;
- displays the service status and main URLs.

Normal startup:

```bash
./backend/start.sh
```

Startup with image rebuild:

```bash
./backend/start.sh --build
```

The `--build` option should be used after changing files such as:

- `Dockerfile`;
- `pyproject.toml`;
- dependency definitions.

Changes inside `app/` normally do not require rebuilding because the source code is mounted as a Docker volume and Uvicorn runs with reload enabled.

### `.dockerignore`

Defines files and directories that must not be included in the Docker build context.

This reduces build time and prevents unnecessary local files from being copied into the image.

### `.env.example`

Documents backend-specific environment variables without containing real secrets.

The main environment configuration used by Docker Compose is located in the repository root:

```text
TripPlanner/.env
```

The real `.env` file must not be committed to Git.

## Environment Requirements

The backend development environment requires:

- Docker Engine;
- Docker Compose.

Python, PostgreSQL, FastAPI, and the backend dependencies do not need to be installed directly on the host system.

## Environment Variables

From the repository root, create the local environment file:

```bash
cp .env.example .env
```

Example configuration:

```dotenv
POSTGRES_DB=tripplanner
POSTGRES_USER=tripplanner
POSTGRES_PASSWORD=change_me

DATABASE_URL=postgresql+psycopg://tripplanner:change_me@database:5432/tripplanner

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=true

PGADMIN_DEFAULT_EMAIL=admin@tripplanner.com
PGADMIN_DEFAULT_PASSWORD=change_me
```

The example passwords must be replaced before using the application outside a local development environment.

## Starting the Backend

From the repository root:

```bash
./backend/start.sh
```

The environment can also be started directly with Docker Compose:

```bash
docker compose up -d
```

To rebuild the image:

```bash
docker compose up --build -d
```

## Available Services

| Service | Address |
|---|---|
| API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Health check | `http://localhost:8000/api/v1/health` |
| pgAdmin | `http://localhost:5050` |

## Running Tests

Run all backend tests:

```bash
docker compose exec backend pytest -v
```

The current expected result is:

```text
2 passed
```

Run a specific test file:

```bash
docker compose exec backend pytest -v tests/test_health.py
```

## Code Quality

Check the backend with Ruff:

```bash
docker compose exec backend ruff check .
```

Check formatting:

```bash
docker compose exec backend ruff format --check .
```

Apply automatic linting fixes:

```bash
docker compose exec backend ruff check . --fix
```

Apply formatting:

```bash
docker compose exec backend ruff format .
```

Recommended validation before creating a commit:

```bash
docker compose exec backend pytest -v
docker compose exec backend ruff check .
docker compose exec backend ruff format --check .
```

## PostgreSQL Access

Open a PostgreSQL console inside the database container:

```bash
docker compose exec database psql -U tripplanner -d tripplanner
```

Useful commands:

```sql
\dt
```

Lists the tables in the current database.

```sql
\d table_name
```

Displays the structure of a table.

```sql
\q
```

Exits the PostgreSQL console.

## pgAdmin Connection

pgAdmin runs in its own Docker container.

To register the TripPlanner PostgreSQL server in pgAdmin, use:

| Field | Value |
|---|---|
| Name | `TripPlanner Database` |
| Host name/address | `database` |
| Port | `5432` |
| Maintenance database | `tripplanner` |
| Username | value of `POSTGRES_USER` |
| Password | value of `POSTGRES_PASSWORD` |

The host must be:

```text
database
```

This is the Docker Compose service name used inside the internal Docker network.

The default PostgreSQL databases `postgres`, `template0`, and `template1` are system databases and should not be deleted.

## Development with Docker

The backend runs entirely inside Docker. A Python virtual environment on the host system is therefore not required.

The container isolates:

```text
backend container
├── Python 3.12
├── FastAPI
├── SQLAlchemy
├── Psycopg
├── Pytest
├── Ruff
└── project dependencies
```

Open a Python shell inside the backend container:

```bash
docker compose exec backend python
```

Open a Bash shell inside the backend container:

```bash
docker compose exec backend bash
```

## Useful Docker Commands

Check the service status:

```bash
docker compose ps
```

View all logs:

```bash
docker compose logs -f
```

View backend logs:

```bash
docker compose logs -f backend
```

Restart only the backend:

```bash
docker compose restart backend
```

Stop the complete environment:

```bash
docker compose down
```

Stop the environment and delete its volumes:

```bash
docker compose down -v
```

> Warning: `docker compose down -v` permanently deletes the local PostgreSQL data and the persistent pgAdmin configuration.

## Recommended Development Workflow

1. Start the environment:

   ```bash
   ./backend/start.sh
   ```

2. Implement the required functionality.

3. Run the tests:

   ```bash
   docker compose exec backend pytest -v
   ```

4. Validate the code:

   ```bash
   docker compose exec backend ruff check .
   docker compose exec backend ruff format --check .
   ```

5. Review the changes:

   ```bash
   git status
   git diff
   ```

6. Create the corresponding Git commit.

## Current Status

The current backend infrastructure includes:

- a working FastAPI application;
- PostgreSQL connectivity;
- a versioned API router;
- a health endpoint;
- automated tests;
- static analysis and formatting with Ruff;
- Docker-based execution;
- pgAdmin integration;
- a development startup script.

The next development phases will add:

- SQLAlchemy data models;
- Alembic database migrations;
- user registration;
- authentication and JWT handling;
- trip management;
- the remaining TripPlanner functional modules.