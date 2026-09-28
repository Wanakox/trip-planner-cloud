# Architecture

Trip Planner follows a decoupled client-server architecture based on a Single Page Application, a REST API and a relational database.

---

## 1. General Architecture

```text
User
 |
 v
React + TypeScript SPA
 |
 | REST API over HTTP
 v
FastAPI Backend
 |
 | SQLAlchemy ORM
 v
PostgreSQL Database
```

The system separates frontend, backend and persistence responsibilities. This improves maintainability, makes the application easier to test and allows each component to evolve independently.

---

## 2. Frontend

The frontend is planned as a Single Page Application.

Technologies:

- React
- TypeScript
- Material UI
- Leaflet
- OpenStreetMap

Responsibilities:

- User interface rendering.
- Form handling.
- Client-side navigation.
- API consumption.
- Map visualization.
- Trip, expense, checklist and profile screens.

A SPA approach is suitable because the application is focused on authenticated users and does not require strong SEO optimization.

---

## 3. Backend

The backend is planned as a REST API.

Technologies:

- Python
- FastAPI
- SQLAlchemy
- JWT
- RQ
- Redis
- WeasyPrint

Responsibilities:

- Business logic.
- Authentication and authorization.
- Data validation.
- Persistence orchestration.
- Integration with external services.
- PDF generation.
- Background task management.

FastAPI is selected because it allows fast REST API development, automatic documentation and a clean integration with Python-based tooling.

---

## 4. Database

The application uses PostgreSQL as the relational database.

PostgreSQL is appropriate because the domain contains multiple related entities, such as users, trips, destinations, checklists, tasks, expenses, files and activities.

Expected benefits:

- Relational integrity.
- Transactions.
- JOIN operations.
- Constraints.
- Strong consistency.
- Future support for geographic extensions if needed.

---

## 5. Deployment

The target deployment environment is a Raspberry Pi 5 using Docker Compose.

Expected services:

```text
frontend
backend
postgresql
redis
```

Docker Compose is used to make the environment reproducible and easy to deploy.

---

## 6. External Integrations

Planned integrations:

- Google Calendar for travel-related reminders.
- Flight search APIs such as Skyscanner or Kiwi.
- OpenStreetMap for map visualization.

These integrations are considered optional or future work depending on project scope and time constraints.