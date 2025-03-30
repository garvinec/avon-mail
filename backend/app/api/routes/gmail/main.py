from api.routes.gmail import get_mail, get_mails, update_mail, auth
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(get_mail.router, prefix="/get_mail")
api_router.include_router(get_mails.router, prefix="/get_mails")
api_router.include_router(update_mail.router, prefix="/update_mail")
api_router.include_router(auth.router, prefix="/auth")
