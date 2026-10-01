# TripPlanner

Full-stack web application for planning, organizing and documenting personal trips.

TripPlanner centralizes destinations, dates, budgets, transport, accommodation, activities, expenses, participants, checklists, notes, files and trip memories in a single application.

This repository contains the **currently maintained cloud version** of TripPlanner.

> The original version developed and submitted as my Final Degree Project is available in the academic repository:  
> **https://github.com/Wanakox/trip-planner**

---

## Live Application

- **Frontend:** https://trip-planner-frontend-vnir.onrender.com
- **Backend API:** https://trip-planner-cloud.onrender.com
- **API documentation:** https://trip-planner-cloud.onrender.com/docs
- **Health check:** https://trip-planner-cloud.onrender.com/api/v1/health

The cloud deployment uses **Render** for the application services and **Supabase** for PostgreSQL and file storage.

---

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, TypeScript, Material UI, Vite |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Database & Storage | Supabase |
| Authentication | JWT |
| Email verification | Brevo SMTP |
| HTTP client | Axios |
| Currency conversion | Frankfurter API |
| PDF generation | ReportLab |
| Testing | Pytest, Vitest, Testing Library |
| Cloud deployment | Render, Supabase |
| Version control | Git, GitHub |

---

## Main Features

### User Accounts

Users can:

- Register an account
- Verify their email address before signing in
- Resend the verification email
- Log in using JWT authentication
- Refresh their session
- View and edit their profile
- Select a default currency
- Upload a profile picture
- Permanently delete their account

Email verification links expire after a limited period, and unverified registrations can be automatically cleaned from the database.

### Trip Management

Users can:

- Create, view, edit and delete trips
- Search and filter trips
- Define origin, dates, description and budget
- Select the trip currency
- Track trip status
- Rate completed trips

A trip can contain destinations, activities, accommodation, transport, expenses, participants, checklists, notes and uploaded documents.

### Destinations and Daily Planning

Users can:

- Add multiple destinations to a trip
- Reorder destinations
- Organize activities by day
- Reorder activities
- Move activities between days
- Mark activities as completed

### Transport and Accommodation

Users can store and manage:

- Transport type
- Origin and destination
- Departure and arrival information
- Prices
- Check-in information
- Accommodation name and address
- Check-in and check-out dates and times

### Expenses and Participants

TripPlanner includes expense tracking per trip.

Users can:

- Add participants
- Associate expenses with participants
- Categorize expenses
- Track total expenditure
- Calculate expenditure per participant
- Compare actual spending with the trip budget
- Work with different currencies

### Checklists

Each trip includes a checklist where users can:

- Add, edit and delete tasks
- Assign priorities
- Reorder tasks
- Mark tasks as completed

### Notes and Documents

Users can:

- Add notes associated with trip days
- Edit and delete notes
- Upload trip documents
- Delete uploaded files
- Store files using Supabase Storage

Deleting a trip or account also removes the associated stored files.

### Completed Trips

Completed trips can include:

- A final rating
- Notes and documents
- Activity timelines
- Map visualization
- PDF export

---

## Architecture

TripPlanner follows a decoupled client-server architecture.

```text
┌──────────────────────────────┐
│ React + TypeScript frontend  │
│ Single Page Application      │
│ Render Static Site           │
└──────────────┬───────────────┘
               │
               │ HTTPS / REST API
               ▼
┌──────────────────────────────┐
│ FastAPI backend              │
│ Render Web Service           │
└──────────────┬───────────────┘
               │
               │ SQLAlchemy
               ▼
┌──────────────────────────────┐
│ Supabase PostgreSQL          │
└──────────────────────────────┘

        ┌──────────────────────┐
        │ Supabase Storage     │
        │ User and trip files  │
        └──────────────────────┘
```

The backend is organized into separate layers:

- **Routers / Endpoints** — HTTP request handling
- **Services** — application and business logic
- **Repositories** — persistence and database queries
- **Schemas** — validation and data transfer with Pydantic
- **Models** — SQLAlchemy database models
- **Core** — configuration, security and shared infrastructure

This separation keeps the API layer independent from business logic and persistence concerns.

---

## Repository Structure

```text
trip-planner-cloud/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   ├── database/
│   ├── tests/
│   ├── .env.example
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── types/
│   │   └── utils/
│   ├── .env.example
│   └── package.json
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Database

The relational schema is available in:

```text
backend/database/schema.sql
```

The project uses PostgreSQL in Supabase.

Provider-specific setup is stored separately in:

```text
backend/database/supabase_setup.sql
```

This keeps the relational schema independent from Supabase-specific features such as scheduled cleanup jobs.

---

## Environment Variables

The repository contains example environment files only.

### Backend

Copy:

```bash
cp backend/.env.example backend/.env
```

The backend requires variables such as:

```text
DATABASE_URL
JWT_SECRET_KEY

SUPABASE_URL
SUPABASE_SECRET_KEY

SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL

FRONTEND_URL
```

Never commit real credentials or production secrets.

### Frontend

Copy:

```bash
cp frontend/.env.example frontend/.env
```

Example:

```text
VITE_API_URL=/api/v1
```

For the cloud deployment, the frontend is configured to communicate with the deployed backend.

---

## Local Development

The project can be run locally without Docker.

### Backend

Requirements:

- Python 3.12+
- PostgreSQL-compatible database
- Python virtual environment recommended

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### Frontend

Requirements:

- Node.js
- npm

From the repository root:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

---

## Testing

### Backend

Backend tests use **Pytest** and FastAPI's testing utilities.

From the backend directory:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

Coverage is configured through `pyproject.toml`.

### Frontend

Frontend tests use **Vitest**, **Testing Library** and **jsdom**.

From the frontend directory:

```bash
npm test
```

Coverage can be executed with:

```bash
npm run test:coverage
```

Linting:

```bash
npm run lint
```

Production build validation:

```bash
npm run build
```

---

## Security

The application includes:

- Password hashing with Argon2
- JWT access and refresh tokens
- Protected API routes
- Resource ownership checks
- Email verification before login
- Environment-based secrets
- Server-side validation
- File ownership checks
- Database constraints and cascading deletion

Access tokens are short-lived and refresh tokens are used to renew authenticated sessions.

---

## Cloud Deployment

The current public version is deployed using:

### Frontend

**Render Static Site**

```text
React + TypeScript + Vite
```

### Backend

**Render Web Service**

```text
FastAPI + Uvicorn
```

Typical production start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Database

**Supabase PostgreSQL**

SQLAlchemy communicates with PostgreSQL through the configured `DATABASE_URL`.

### File Storage

**Supabase Storage**

Profile pictures and trip documents are stored outside the application service so they persist independently from Render deployments.

### Email

**Brevo SMTP**

Used for account verification emails.

---

## Project Background

TripPlanner originated as my Final Degree Project in Computer Engineering at the University of Córdoba.

The original academic version focused on the complete engineering process: requirements, analysis, architecture, design, implementation, testing and deployment.

After completing the degree project, development continued in this repository to move the application from the original self-hosted environment to a publicly accessible cloud deployment.

The original academic repository is available here:

**https://github.com/Wanakox/trip-planner**

---

## What This Project Demonstrates

TripPlanner demonstrates practical experience with:

- Backend development with FastAPI
- REST API design
- Layered software architecture
- React and TypeScript frontend development
- PostgreSQL and relational database design
- SQLAlchemy ORM
- JWT authentication
- Email verification flows
- External service integration
- File storage
- Cloud deployment
- Automated testing
- Linux-based development
- Git and GitHub

---

## Author

**Juan García Moreno**  
Computer Engineering Graduate

- GitHub: https://github.com/Wanakox
- Portfolio: https://wanakox.github.io
- LinkedIn: https://www.linkedin.com/in/juan-garcía-moreno

---

## License

This project is distributed under the terms defined in the [LICENSE](LICENSE) file.