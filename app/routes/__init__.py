"""
Routes package for API endpoints.
"""
from .sessions import router as sessions_router
from .questions import router as questions_router
from .learning_plan import router as learning_plan_router
from .health import router as health_router

__all__ = [
    "sessions_router",
    "questions_router",
    "learning_plan_router",
    "health_router",
]
