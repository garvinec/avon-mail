from fastapi import APIRouter

from api.routes import get

api_router = APIRouter()
api_router.include_router(get.router)
