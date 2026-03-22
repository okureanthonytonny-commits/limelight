from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from database import engine, test_connection
from models import User, Product, Order  # Import models to register metadata
from starlette.middleware.sessions import SessionMiddleware
from config import settings  # fixed import
import os

# Create database tables (for development - use Alembic in production)
SQLModel.metadata.create_all(engine)

app = FastAPI(title="Limelight API", version="0.1.0")

# Create static directory if not exists
os.makedirs("static/images", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    test_connection()  # just call, don't check return value

@app.get("/")
def root():
    return {"message": "Limelight API is running"}

# Import and include routers
from routers import store, admin
from routers import cart
from auth import router as auth_router

app.include_router(store.router, prefix="/api/store")
app.include_router(cart.router, prefix="/api/store")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(auth_router, prefix="/auth")