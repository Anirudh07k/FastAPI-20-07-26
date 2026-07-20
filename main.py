from fastapi import FastAPI, HTTPException, status
from database import supabase
from routers.book_routers import router as book_routes
from routers.auth_routers import router as auth_routes

app = FastAPI(
    title="Supabase Demo",
    description="Supabase demo with FastAPI"
)

app.include_router(auth_routes)
app.include_router(book_routes)

@app.get('/', tags=["Root"])
def home():
    return {
        "message": "Supabase API is running"
    }
