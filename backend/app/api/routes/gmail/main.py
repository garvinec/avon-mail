from fastapi import APIRouter

from api.routes.gmail import auth, mail

api_router = APIRouter()
api_router.include_router(mail.router, prefix="/get")
api_router.include_router(auth.router, prefix="/auth")
