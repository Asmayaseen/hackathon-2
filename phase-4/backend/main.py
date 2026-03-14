"""
Evolution Todo API - FastAPI Backend

Task: 1.6
Spec: specs/overview.md
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file first

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db import create_db_and_tables
import os
import traceback

# Initialize FastAPI app
app = FastAPI(
    title="Evolution Todo API",
    version="1.0.0",
    description="RESTful API for Evolution Todo application"
)

# CORS Configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://frontend-umber-nine-80.vercel.app,https://frontend-qnzzeug89-asma-yaseens-projects.vercel.app,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and return with proper CORS headers."""
    print(f"❌ Global Exception: {exc}")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "http://localhost:3000"),
            "Access-Control-Allow-Credentials": "true",
        }
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


@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return {
        "status": "healthy",
        "service": "evolution-todo-api",
        "version": "1.0.0"
    }


@app.get("/ready")
def readiness_check():
    """Readiness check - verifies database connectivity."""
    try:
        from db import engine
        from sqlmodel import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


# Import and include routers
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from routes.recurrence import router as recurrence_router
from routes.search import router as search_router
from routes.bulk import router as bulk_router
from routes.history import router as history_router
from routes.notifications import router as notifications_router
from routes.preferences import router as preferences_router
from routes.stats import router as stats_router
from routes.export_import import router as export_import_router
from routes.chat import router as chat_router  # Phase III: AI Chatbot
from routes.voice import router as voice_router  # Phase III: Voice Input (Whisper)
from routes.events import router as events_router  # Phase V: Event-Driven (T5-304)
from routes.cron_handlers import router as cron_router  # Phase V: Dapr Cron Bindings
from routes.chatkit import router as chatkit_router  # Phase III: ChatKit Integration

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(recurrence_router)
app.include_router(search_router)
app.include_router(bulk_router)
app.include_router(history_router)
app.include_router(notifications_router)
app.include_router(preferences_router)
app.include_router(stats_router)
app.include_router(export_import_router)
app.include_router(chat_router)  # Phase III: AI Chatbot (T-CHAT-012)
app.include_router(voice_router)  # Phase III: Voice Input (T-CHAT-015)
app.include_router(events_router)  # Phase V: Event-Driven (T5-304)
app.include_router(cron_router)  # Phase V: Dapr Cron Bindings
app.include_router(chatkit_router)  # Phase III: ChatKit Integration (T-CHATKIT-003)
