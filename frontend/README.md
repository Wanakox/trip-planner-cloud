# TripPlanner Frontend

Interfaz web de TripPlanner desarrollada con React, TypeScript, Vite y Material UI.

## Desarrollo local

```bash
npm ci
npm run dev
```

La aplicación se abre en `http://localhost:5173`. En desarrollo, Vite reenvía las peticiones
`/api` al backend disponible en `http://localhost:8000`.

## Comprobaciones

```bash
npm run lint
npm test
npm run build
```

Para obtener el informe de cobertura:

```bash
npm run test:coverage
```

## Imagen Docker

El `Dockerfile` utiliza dos etapas:

1. Node instala las dependencias y genera `dist`.
2. Nginx sirve los archivos estáticos y reenvía `/api` al contenedor `backend`.

Construcción independiente:

```bash
docker build -t tripplanner-frontend ./frontend
docker run --rm -p 5173:80 tripplanner-frontend
```

Normalmente debe iniciarse mediante el `docker-compose.yml` de la raíz para que el proxy pueda
resolver el servicio `backend`.

## Configuración

`VITE_API_URL` se establece durante la compilación. Su valor predeterminado es `/api/v1`, por lo
que el navegador utiliza el mismo origen que el frontend y Nginx se encarga del proxy.
