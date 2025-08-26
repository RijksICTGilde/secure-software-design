import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.authentication import get_current_user
from app.config import settings
from app.routes.main import router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Security API",
    debug=settings.DEBUG,
    version="0.1.0",
    redirect_slashes=False,
    openapi_url="/openapi.json",
    docs_url="/",
    redoc_url=None
)

app.include_router(router, dependencies=[Depends(get_current_user)], prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
