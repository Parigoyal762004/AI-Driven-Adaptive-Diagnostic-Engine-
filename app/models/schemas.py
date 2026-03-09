"""
API request and response schemas for the Adaptive Testing Engine.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request to create a new testing session."""
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    test_type: str = "GRE"
    max_questions: int = Field(10, ge=5, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "user_name": "John Doe",
                "test_type": "GRE",
                "max_questions": 10
            }
        }


class CreateSessionResponse(BaseModel):
    """Response after creating a session."""
    session_id: str
    message: str
    initial_ability: float
    max_questions: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "message": "Session created successfully",
                "initial_ability": 0.0,
                "max_questions": 10
            }
        }


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: str
    user_answer: str
    time_spent_seconds: Optional[int] = Field(None, ge=0, le=600)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "507f1f77bcf86cd799439011",
                "user_answer": "x = 5",
                "time_spent_seconds": 45
            }
        }


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer."""
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    updated_ability: float
    standard_error: float
    questions_remaining: int
    session_complete: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_correct": True,
                "correct_answer": "x = 5",
                "explanation": "Subtract 5 from both sides: 3x = 15, then divide by 3: x = 5",
                "updated_ability": 0.3,
                "standard_error": 0.65,
                "questions_remaining": 7,
                "session_complete": False
            }
        }


class LearningPlanResponse(BaseModel):
    """AI-generated personalized learning plan."""
    session_id: str
    final_ability: float
    accuracy: float
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    study_plan: str
    estimated_study_hours: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "final_ability": 0.5,
                "accuracy": 0.6,
                "strengths": ["Algebra", "Linear Equations"],
                "weaknesses": ["Geometry", "Word Problems"],
                "recommendations": [
                    "Focus on geometry fundamentals",
                    "Practice word problem translation",
                    "Review coordinate geometry"
                ],
                "study_plan": "Week 1: Focus on basic geometry...",
                "estimated_study_hours": 15
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
