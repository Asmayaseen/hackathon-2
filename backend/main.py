"""
Evolution Todo API - FastAPI Backend

Task: 1.6
Spec: specs/overview.md
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_db_and_tables
import os

# Initialize FastAPI app
app = FastAPI(
    title="Evolution Todo API",
    version="1.0.0",
    description="RESTful API for Evolution Todo application"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    create_db_and_tables()


@app.get("/")
def root():
    """Root endpoint - API status check."""
    return {
        "message": "Evolution Todo API",
        "status": "running",
        "version": "1.0.0"
    }


# Import and include routers
from routes.tasks import router as tasks_router

app.include_router(tasks_router)
