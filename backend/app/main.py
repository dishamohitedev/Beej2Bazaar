"""
BeejBazaar backend entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

Docs available at /docs (Swagger) once running.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.db.user_repository import user_repository
from app.routers import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("beejbazaar")

app = FastAPI(
    title="BeejBazaar API",
    description="AI-powered agriculture platform — backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await user_repository.ensure_indexes()
    logger.info("ENV=%s | USE_MOCK_DB=%s | USE_MOCK_FIREBASE=%s",
                settings.ENV, settings.USE_MOCK_DB, settings.USE_MOCK_FIREBASE)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "env": settings.ENV}


app.include_router(auth.router)

# Future module routers get included here, e.g.:
# app.include_router(farms.router)
# app.include_router(crops.router)
