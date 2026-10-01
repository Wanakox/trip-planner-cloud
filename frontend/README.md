# TripPlanner Frontend

Frontend application for TripPlanner, built with **React**, **TypeScript**, **Vite** and **Material UI**.

This frontend is part of the currently maintained cloud version of TripPlanner.

> The original academic version developed as part of my Final Degree Project is available in:
> **https://github.com/Wanakox/trip-planner**

---

## Production Deployment

The frontend is deployed as a **Render Static Site**.

- **Application:** https://trip-planner-frontend-vnir.onrender.com
- **Backend API:** https://trip-planner-cloud.onrender.com
- **API documentation:** https://trip-planner-cloud.onrender.com/docs

---

## Main Technologies

- React
- TypeScript
- Vite
- Material UI
- React Router
- Axios
- TanStack Query
- Vitest
- Testing Library
- jsdom

---

## Local Development

Requirements:

- Node.js
- npm

Install dependencies:

```bash
npm ci
```

Create the local environment file:

```bash
cp .env.example .env
```

Start the development server:

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

---

## Configuration

The frontend uses the environment variable:

```text
VITE_API_URL
```

Example:

```text
VITE_API_URL=http://localhost:8000/api/v1
```

For the production deployment, this variable points to the deployed backend API.

The environment configuration is defined in:

```text
src/config/env.ts
```

---

## Available Scripts

### Development

```bash
npm run dev
```

### Lint

```bash
npm run lint
```

### Tests

```bash
npm test
```

### Test coverage

```bash
npm run test:coverage
```

### Production build

```bash
npm run build
```

### Preview production build

```bash
npm run preview
```

---

## Testing

Frontend tests use:

- Vitest
- Testing Library
- jsdom
- spies and mocks where appropriate

Run all tests with:

```bash
npm test
```

Run coverage with:

```bash
npm run test:coverage
```

---

## Project Structure

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── config/
│   ├── pages/
│   ├── routes/
│   ├── test/
│   ├── theme/
│   ├── types/
│   └── utils/
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## Architecture

The frontend is a **Single Page Application (SPA)**.

React Router handles client-side navigation, while the frontend communicates with the FastAPI backend through REST API requests.

The application uses:

- React for the UI
- React Router for navigation
- Axios for HTTP requests
- TanStack Query for server-state management
- Material UI for interface components
- Vite for development and production builds

---

## Cloud Deployment

The frontend is deployed on **Render** as a static site.

The production build is generated with:

```bash
npm run build
```

The resulting static assets are served directly by Render.

The frontend communicates with the deployed backend through the configured `VITE_API_URL`.

---

## Project Background

TripPlanner originated as my Final Degree Project in Computer Engineering at the University of Córdoba.

After completing the academic version, development continued in the cloud repository to make the application publicly accessible using Render and Supabase.

Original academic repository:

**https://github.com/Wanakox/trip-planner**

---

## Author

**Juan García Moreno**  
Computer Engineering Graduate

- GitHub: https://github.com/Wanakox
- Portfolio: https://wanakox.github.io
- LinkedIn: https://www.linkedin.com/in/juan-garcía-moreno