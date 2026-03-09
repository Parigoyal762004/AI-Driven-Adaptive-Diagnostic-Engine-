"""
Dependency injection for FastAPI routes.
"""
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.database import get_database
from app.repositories.question_repository import QuestionRepository
from app.repositories.session_repository import SessionRepository
from app.services.adaptive_engine import AdaptiveEngine
from app.services.question_selector import QuestionSelector
from app.services.learning_plan_generator import LearningPlanGenerator


# Repository Dependencies
def get_question_repository(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> QuestionRepository:
    """Get QuestionRepository instance."""
    return QuestionRepository(db)


def get_session_repository(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> SessionRepository:
    """Get SessionRepository instance."""
    return SessionRepository(db)


# Service Dependencies
def get_adaptive_engine() -> AdaptiveEngine:
    """Get AdaptiveEngine instance."""
    return AdaptiveEngine()


def get_question_selector(
    engine: AdaptiveEngine = Depends(get_adaptive_engine)
) -> QuestionSelector:
    """Get QuestionSelector instance."""
    return QuestionSelector(engine)


def get_learning_plan_generator() -> LearningPlanGenerator:
    """Get LearningPlanGenerator instance."""
    return LearningPlanGenerator()
