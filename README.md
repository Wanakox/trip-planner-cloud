# TripPlanner

A full-stack web application for planning, organizing, tracking and documenting personal trips.

TripPlanner centralizes the main information involved in a trip, including destinations, dates, budgets, transport, accommodation, daily activities, expenses, participants, checklists, notes, files, maps and travel memories.

The project uses a decoupled client-server architecture with a **React and TypeScript** frontend, a **FastAPI** backend, a **PostgreSQL** database and a **Docker-based deployment environment**.

> TripPlanner is being developed as my Final Degree Project in Computer Engineering. The analysis and system design phases have been completed, and the project is currently entering the implementation phase.

---

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, TypeScript, Material UI, Vite |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Authentication | JSON Web Tokens |
| Maps | Leaflet, OpenStreetMap |
| Background tasks | Redis, RQ |
| PDF generation | WeasyPrint |
| Deployment | Docker, Docker Compose, Raspberry Pi 5 |
| Modeling and design | UML, Figma, AUP, Scrumban |

---

## Main Features

### User Management

Users can register, log in, log out, view and edit their profile, select a default currency and permanently delete their account.

Authentication and access control are managed using JSON Web Tokens.

### Trip Management

Users can create, view, edit, search and delete personal trips.

Each trip can contain:

- One or more destinations
- Start and end dates
- Description
- Budget
- Status
- Rating
- Transport information
- Accommodation information
- Participants
- Expenses
- Activities
- Checklist
- Notes and files

The system also calculates the duration of the trip and the number of days remaining before it starts.

### Daily Planning

Trips are organized into daily itineraries.

Users can:

- Add activities to a specific day
- Define their name, location and time
- Edit or delete activities
- Move activities between days
- Mark activities as completed

### Transport and Accommodation

Users can register and manage transport and accommodation associated with a trip.

Transport information can include:

- Transport type
- Price
- Origin and destination
- Departure and arrival dates
- Departure and arrival times
- Check-in information

Accommodation information can include:

- Name
- Address
- Price
- Check-in date and time
- Check-out date and time

### Expenses and Participants

TripPlanner includes expense tracking for each trip.

Users can:

- Add, edit and delete participants
- Register expenses associated with a participant
- Categorize expenses
- Calculate the total trip expenditure
- Calculate expenditure by participant
- Compare the real expenditure with the planned budget

The application also includes an independent currency converter that does not store conversion operations.

### Checklists

Each trip includes a checklist for managing preparation tasks.

Users can:

- Add, edit and delete tasks
- Assign priorities
- Reorder tasks
- Mark or unmark tasks as completed

### Completed Trips

Completed trips can be documented with additional content.

Users can:

- Add notes associated with different days
- Edit and delete notes
- Upload up to ten files
- Delete uploaded files
- Add a trip rating
- Display activities and locations on a timeline
- Display accommodation and activity locations on a map
- Export the complete trip information to PDF

### Search and Filtering

Trips can be searched by name and filtered using criteria such as:

- Country
- Budget
- Status

### External Integrations

TripPlanner includes planned integrations with external services:

- **Google Calendar**, for creating events associated with flights and accommodation
- **External flight search platforms**, such as Skyscanner or Kiwi
- **Mapping services**, for geocoding locations and displaying routes

The flight search functionality redirects the user to an external platform with the origin, destination and travel dates already provided.

---

## Architecture Overview

TripPlanner follows a decoupled client-server architecture.

```text
┌──────────────────────────────┐
│ React + TypeScript frontend  │
│ Single Page Application      │
└──────────────┬───────────────┘
               │
               │ HTTPS / REST API
               ▼
┌──────────────────────────────┐
│ FastAPI backend              │
│ Business logic and services  │
└──────────────┬───────────────┘
               │
               │ SQLAlchemy ORM
               ▼
┌──────────────────────────────┐
│ PostgreSQL database          │
└──────────────────────────────┘
```

Redis and RQ are used for background tasks, including operations that should not block normal API requests.

The system is designed to run through Docker Compose and to be deployed on a Raspberry Pi 5. This provides a portable and reproducible environment for development and production.

More information is available in [`docs/architecture/architecture.md`](docs/architecture/architecture.md).

---

## Repository Structure

```text
TripPlanner/
├── backend/
├── frontend/
├── docs/
│   ├── analysis/
│   ├── architecture/
│   ├── design/
│   ├── diagrams/
│   ├── references/
│   ├── requirements/
│   └── README.md
├── docker-compose.yml
├── LICENSE
└── README.md
```

### Main Directories

| Directory | Description |
|---|---|
| `backend/` | FastAPI application, business logic, persistence and API endpoints |
| `frontend/` | React and TypeScript Single Page Application |
| `docs/analysis/` | Requirements analysis and traceability documentation |
| `docs/architecture/` | Description of the system architecture |
| `docs/design/` | Detailed system design documentation |
| `docs/diagrams/` | UML, architecture, database and planning diagrams |
| `docs/references/` | Academic and technical reference material |
| `docs/requirements/` | Official project proposal and administrative documents |

The internal structures of `backend/` and `frontend/` will be documented in their respective README files as implementation progresses.

---

## Run with Docker Compose

Create the local environment file and replace the example secrets:

```bash
cp .env.example .env
```

Build and start the complete application:

```bash
docker compose up -d --build
```

The services are available at:

| Service | Default URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API documentation | `http://localhost:8000/docs` |
| pgAdmin | `http://localhost:5050` |

Check container health and inspect logs:

```bash
docker compose ps
docker compose logs -f frontend backend
```

Stop the application without deleting database data:

```bash
docker compose down
```

The frontend is built as static assets and served by Nginx. Requests to `/api` are proxied through
the internal Docker network to FastAPI, and unknown browser routes fall back to `index.html` so
React Router works after a page refresh.

---

## Documentation

### Analysis

- [System analysis](docs/analysis/TripPlanner%20-%20Analisis.pdf)
- [Traceability matrix](docs/analysis/TripPlanner%20-%20Matriz%20de%20trazabilidad.pdf)
- [Requirements extraction](docs/analysis/requirements-extraction.txt)

### Architecture and Design

- [Architecture description](docs/architecture/architecture.md)
- [System design](docs/design/TripPlanner%20-%20Diseño.pdf)

### Project Documentation

- [Topic proposal](docs/requirements/PeticionTemaJuanGarcia.pdf)
- [Signed project document](docs/requirements/AnexoIII_JuanGarcia_signed.pdf)

### Diagrams

The [`docs/diagrams/`](docs/diagrams/) directory contains:

- System architecture
- Use-case diagram
- Activity diagrams
- Class diagrams
- Entity-relationship diagram
- Work Breakdown Structure
- Traceability matrix

---

## Development Principles

The implementation is intended to follow established software engineering practices:

- Layered architecture
- Separation of responsibilities
- SOLID principles
- Clean Code practices
- RESTful API design
- Data validation
- Secure password hashing
- Token-based authentication
- Automated testing
- Containerized and reproducible environments
- Version control with Git

The project is developed incrementally, integrating the frontend, backend and persistence layers as each functional module is implemented.

---

## Why This Project?

The idea for TripPlanner comes from a real personal need identified during an Erasmus experience.

Planning several trips requires managing transport, accommodation, budgets, activities, documents and expenses. This information is often distributed across multiple applications, websites, notes and files, which makes the complete process difficult to manage.

TripPlanner aims to provide a centralized platform covering the three main phases of a trip:

1. Planning before departure
2. Organization and expense tracking during the trip
3. Documentation and preservation of the completed trip

The project also serves as a practical application of the knowledge acquired throughout the Computer Engineering degree.

---

## What This Project Demonstrates

TripPlanner is intended to demonstrate practical skills in:

- Requirements engineering
- Software analysis and design
- UML modeling
- Relational database design
- Full-stack web development
- REST API development
- Authentication and authorization
- Integration with external services
- Background task processing
- PDF generation
- Containerized deployment
- Technical documentation
- Testing and system integration

---

## Repository Description

```text
Full-stack web application for planning, organizing and documenting personal trips, built with React, FastAPI, PostgreSQL and Docker.
```

Suggested GitHub topics:

```text
react
typescript
fastapi
python
postgresql
docker
docker-compose
sqlalchemy
jwt-authentication
material-ui
leaflet
openstreetmap
redis
rq
full-stack
rest-api
travel-planner
final-degree-project
```

---

## Author

**Juan García Moreno**  
Computer Engineering student  
GitHub: [@Wanakox](https://github.com/Wanakox)

---

## License

This project is distributed under the terms defined in the [LICENSE](LICENSE) file.
