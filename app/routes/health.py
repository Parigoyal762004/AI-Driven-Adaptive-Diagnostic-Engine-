"""
Health check and system status routes.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.schemas import HealthCheckResponse
from app.utils.database import get_database
from app.config import settings


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Health check endpoint for monitoring system status.
    
    Returns:
        HealthCheckResponse with system status
    """
    # Test database connection
    try:
        await db.command('ping')
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.app_version,
        database=db_status,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.get("/stats")
async def get_system_stats(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Get system statistics.
    
    Returns:
        Dictionary with system statistics
    """
    try:
        # Count questions
        total_questions = await db.questions.count_documents({"is_active": True})
        
        # Count sessions
        total_sessions = await db.user_sessions.count_documents({})
        active_sessions = await db.user_sessions.count_documents({"status": "in_progress"})
        completed_sessions = await db.user_sessions.count_documents({"status": "completed"})
        
        # Get topics
        topics = await db.questions.distinct("topic", {"is_active": True})
        
        return {
            "questions": {
                "total": total_questions,
                "topics": sorted(topics),
                "topic_count": len(topics)
            },
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": completed_sessions
            },
            "system": {
                "version": settings.app_version,
                "ai_provider": settings.ai_provider
            }
        }
    except Exception as e:
        return {
            "error": f"Failed to retrieve stats: {str(e)}"
        }
