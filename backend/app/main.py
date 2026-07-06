from fastapi import FastAPI
from app.database.supabase import supabase
from app.core.config import settings
from app.routers import auth

app = FastAPI(
    title="Beej2Bazaar API",
    version="1.0.0",
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "message": "Beej2Bazaar Backend Running 🚀"
    }
