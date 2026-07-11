from fastapi import FastAPI

from app.routers import (
    auth,
    profile,
    onboarding,
    crop,
    irrigation,
    notification,
    disease,
    disease_alert,
)

app = FastAPI(
    title="Beej2Bazaar API",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(crop.router, prefix="/api")
app.include_router(irrigation.router, prefix="/api")
app.include_router(notification.router, prefix="/api")
app.include_router(disease.router, prefix="/api")
app.include_router(disease_alert.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Beej2Bazaar Backend Running 🚀"
    }