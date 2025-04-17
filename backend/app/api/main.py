from fastapi import APIRouter

from api.routes.gmail import main
from api.routes.email_analysis import router as email_analysis_router

api_router = APIRouter()
api_router.include_router(main.api_router, prefix="/gmail")
api_router.include_router(email_analysis_router, prefix="/email_analysis")
