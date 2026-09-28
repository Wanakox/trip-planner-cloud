#!/usr/bin/env bash

set -Eeuo pipefail

# Directorio del script: TripPlanner/backend
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Raíz del proyecto: TripPlanner
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

MAX_ATTEMPTS=60

echo "========================================"
echo "        Iniciando TripPlanner"
echo "========================================"

# ------------------------------------------------------------
# Comprobaciones previas
# ------------------------------------------------------------

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker no está instalado o no está disponible."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker no está iniciado o tu usuario no puede acceder a él."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl no está instalado o no está disponible."
    exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "Error: no se encontró ${COMPOSE_FILE}."
    exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Error: no existe el archivo .env."
    echo "Créalo desde la plantilla con:"
    echo "  cp \"${PROJECT_ROOT}/.env.example\" \"${ENV_FILE}\""
    exit 1
fi

# ------------------------------------------------------------
# Lectura segura de variables simples del .env
# ------------------------------------------------------------

get_env_value() {
    local variable_name="$1"
    local default_value="$2"
    local value

    value="$(
        grep -E "^${variable_name}=" "${ENV_FILE}" |
        tail -n 1 |
        cut -d= -f2- |
        tr -d '\r'
    )"

    printf '%s' "${value:-${default_value}}"
}

BACKEND_PORT="$(get_env_value "BACKEND_PORT" "8000")"
FRONTEND_PORT="$(get_env_value "FRONTEND_PORT" "5173")"

BACKEND_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"

BACKEND_HEALTH_URL="${BACKEND_URL}/api/v1/health"
FRONTEND_HEALTH_URL="${FRONTEND_URL}/health"
PROXY_HEALTH_URL="${FRONTEND_URL}/api/v1/health"

# ------------------------------------------------------------
# Inicio de los contenedores
# ------------------------------------------------------------

cd "${PROJECT_ROOT}"

if [[ "${1:-}" == "--build" ]]; then
    echo "Construyendo imágenes e iniciando servicios..."
    docker compose up --build -d
else
    echo "Iniciando servicios..."
    docker compose up -d
fi

# ------------------------------------------------------------
# Espera de servicios
# ------------------------------------------------------------

wait_for_service() {
    local service_name="$1"
    local health_url="$2"
    local attempt=1

    echo
    echo "Esperando a ${service_name}..."

    until curl --silent --fail "${health_url}" >/dev/null 2>&1; do
        if [[ "${attempt}" -ge "${MAX_ATTEMPTS}" ]]; then
            echo
            echo "Error: ${service_name} no respondió después de ${MAX_ATTEMPTS} intentos."
            return 1
        fi

        printf "."
        sleep 1
        attempt=$((attempt + 1))
    done

    echo
    echo "${service_name} está disponible."
}

if ! wait_for_service "la API" "${BACKEND_HEALTH_URL}"; then
    echo
    echo "Revisa los logs con:"
    echo "  docker compose logs backend database"
    exit 1
fi

if ! wait_for_service "el frontend" "${FRONTEND_HEALTH_URL}"; then
    echo
    echo "Revisa los logs con:"
    echo "  docker compose logs frontend"
    exit 1
fi

if ! wait_for_service "el proxy frontend-backend" "${PROXY_HEALTH_URL}"; then
    echo
    echo "Nginx está iniciado, pero no puede comunicarse con el backend."
    echo "Revisa los logs con:"
    echo "  docker compose logs frontend backend"
    exit 1
fi

# ------------------------------------------------------------
# Resultado
# ------------------------------------------------------------

echo
docker compose ps

echo
echo "========================================"
echo "       TripPlanner está preparado"
echo "========================================"
echo
echo "Aplicación:    ${FRONTEND_URL}"
echo "API:           ${BACKEND_URL}"
echo "Swagger:       ${BACKEND_URL}/docs"
echo "Health API:    ${BACKEND_HEALTH_URL}"
echo "Health web:    ${FRONTEND_HEALTH_URL}"
echo "pgAdmin:       http://localhost:5050"
echo
echo "Logs generales:"
echo "  docker compose logs -f"
echo
echo "Logs del frontend:"
echo "  docker compose logs -f frontend"
echo
echo "Detener el entorno:"
echo "  docker compose down"