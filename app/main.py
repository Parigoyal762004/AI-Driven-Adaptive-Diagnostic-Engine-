"""
Main FastAPI application for the Adaptive Testing Engine.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.utils.database import Database
from app.utils.exceptions import AdaptiveTestingException
from app.routes import (
    sessions_router,
    questions_router,
    learning_plan_router,
    health_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Connect to database
    await Database.connect()
    await Database.create_indexes()
    
    # Validate AI configuration
    try:
        settings.validate_ai_config()
        print(f"✓ AI Provider: {settings.ai_provider}")
    except ValueError as e:
        print(f"⚠ Warning: {e}")
        print("  Learning plan generation will use fallback templates")
    
    print("✓ Application ready")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")
    await Database.disconnect()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-Driven Adaptive Diagnostic Engine using Item Response Theory (IRT).
    
    This API provides:
    - Adaptive question selection based on ability estimation
    - Real-time ability tracking using 2PL IRT model
    - Personalized learning plans powered by AI
    - Session management and progress tracking
    
    ## Key Endpoints
    
    - **POST /api/sessions** - Create a new test session
    - **GET /api/sessions/{id}/next-question** - Get next adaptive question
    - **POST /api/sessions/{id}/answers** - Submit an answer
    - **GET /api/sessions/{id}/learning-plan** - Get AI-generated study plan
    - **GET /api/health** - System health check
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for custom exceptions
@app.exception_handler(AdaptiveTestingException)
async def custom_exception_handler(request: Request, exc: AdaptiveTestingException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(questions_router)
app.include_router(learning_plan_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-Driven Adaptive Testing Engine",
        "documentation": "/docs",
        "health": "/api/health",
        "stats": "/api/stats"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
