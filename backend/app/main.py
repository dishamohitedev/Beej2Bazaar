from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    profile,
    onboarding,
    crop,
    irrigation,
    notification,
    disease,
    community,
)

app = FastAPI(
    title="Beej2Bazaar API",
    version="1.0.0",
    description="Backend API for Beej2Bazaar — the farmer-first agri-tech platform.",
)

# ---------------------------------------------------------------------------
# CORS — allow the React frontend (and Swagger UI) to reach the API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(crop.router, prefix="/api")
app.include_router(irrigation.router, prefix="/api")
app.include_router(notification.router, prefix="/api")
app.include_router(disease.router, prefix="/api")
app.include_router(community.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Beej2Bazaar Backend Running 🚀"
    }