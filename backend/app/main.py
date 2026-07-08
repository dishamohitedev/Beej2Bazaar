from fastapi import FastAPI
from app.routers import onboarding
from app.routers import auth, profile

app = FastAPI(
    title="Beej2Bazaar API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(onboarding.router)


@app.get("/")
def root():
    return {
        "message": "Beej2Bazaar Backend Running 🚀"
    }