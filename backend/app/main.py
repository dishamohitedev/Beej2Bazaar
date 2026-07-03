from fastapi import FastAPI
from app.database.supabase import supabase
from app.config import settings

app = FastAPI(
    title="Beej2Bazaar API",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "Beej2Bazaar Backend Running 🚀"
    }

#@app.get("/test")
#def test_supabase():
#     response = (
#         supabase
#         .table("crops")
#         .select("*")
#         .limit(100)
#         .execute()
#     )
#     return response.data