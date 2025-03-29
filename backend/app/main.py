from api.main import api_router
from api.auth import auth_middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app = FastAPI(
    title="Avon Mail API",
    description="APIs for Avon Mail",
    version="1.0.0"
)

app.middleware("http")(auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    app.run()
