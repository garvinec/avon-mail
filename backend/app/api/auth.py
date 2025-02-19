from db.client import SUPABASE_JWT_SECRET
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

router = APIRouter()
security = HTTPBearer()


async def auth_middleware(request: Request, call_next):
    token = request.headers.get("access_token")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        request.headers.__dict__["_list"].append(
            b"authorization", f"Bearer {token}".encode())

    response = await call_next(request)
    return response


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[
                             "HS256"], options={"verify_aud": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth creds")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
