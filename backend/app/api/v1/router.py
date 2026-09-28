from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.currency import router as currency_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.trip import router as trips_router
from app.api.v1.endpoints.user import router as users_router
from app.api.v1.endpoints.destination import router as destinations_router
from app.api.v1.endpoints.activity import router as activities_router
from app.api.v1.endpoints.transport import router as transport_router
from app.api.v1.endpoints.accommodation import router as accommodation_router
from app.api.v1.endpoints.participant import router as participants_router
from app.api.v1.endpoints.expense import router as expenses_router
from app.api.v1.endpoints.task import router as tasks_router
from app.api.v1.endpoints.note import router as notes_router
from app.api.v1.endpoints.file import router as files_router
from app.api.v1.endpoints.timeline import router as timeline_router
from app.api.v1.endpoints.export import router as export_router
from app.api.v1.endpoints.flight import router as flight_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(trips_router)
api_router.include_router(destinations_router)
api_router.include_router(activities_router)
api_router.include_router(transport_router)
api_router.include_router(accommodation_router)
api_router.include_router(tasks_router)
api_router.include_router(participants_router)
api_router.include_router(expenses_router)
api_router.include_router(notes_router)
api_router.include_router(files_router)
api_router.include_router(export_router)

api_router.include_router(timeline_router)

api_router.include_router(currency_router)

api_router.include_router(flight_router)