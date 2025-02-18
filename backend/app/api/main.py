from fastapi import APIRouter

from api.routes.gmail import main

api_router = APIRouter()
api_router.include_router(main.api_router, prefix="/gmail")
