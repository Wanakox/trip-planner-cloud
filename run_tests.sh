#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker no está instalado o no está disponible en PATH." >&2
    exit 1
fi

if ! docker compose ps --services --status running | grep -qx "backend"; then
    echo "El servicio backend no está iniciado. Arrancándolo..."
    docker compose up -d --build backend
fi

echo "Ejecutando los tests del backend..."
docker compose exec backend pytest -v "$@"

if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm no está instalado o no está disponible en PATH." >&2
    exit 1
fi

echo "Ejecutando lint, tests y build del frontend..."
cd "$project_dir/frontend"

if [[ ! -d node_modules ]]; then
    npm ci
fi

npm run lint
npm test
npm run build
