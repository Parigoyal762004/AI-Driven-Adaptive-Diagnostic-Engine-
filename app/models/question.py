"""
Data models for the Adaptive Testing Engine.
Defines Pydantic models for questions, sessions, and API schemas.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class QuestionModel(BaseModel):
    """
    Represents a test question with IRT parameters.
    
    IRT Parameters:
    - difficulty (b): How hard the question is (-3 to 3, higher = harder)
    - discrimination (a): How well it differentiates ability levels (0.5 to 2.5)
    - guessing (c): Probability of correct guess (typically 0.25 for 4 options)
    """
    id: Optional[str] = Field(None, alias="_id")
    question_text: str = Field(..., min_length=10, max_length=2000)
    options: list[str] = Field(..., min_length=2, max_length=6)
    correct_answer: str
    
    # IRT Parameters
    difficulty: float = Field(..., ge=-3.0, le=3.0, description="Item difficulty parameter (b)")
    discrimination: float = Field(1.0, ge=0.5, le=2.5, description="Item discrimination parameter (a)")
    guessing: float = Field(0.25, ge=0.0, le=0.5, description="Guessing parameter (c)")
    
    # Metadata
    topic: str = Field(..., min_length=1, max_length=100)
    subtopic: Optional[str] = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    explanation: Optional[str] = Field(None, max_length=1000)
    
    # Content Classification
    bloom_level: Optional[Literal["remember", "understand", "apply", "analyze", "evaluate", "create"]] = None
    estimated_time_seconds: int = Field(90, ge=30, le=600)
    
    # Administrative
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, v: str, info) -> str:
        """Ensure correct_answer is one of the options."""
        if "options" in info.data and v not in info.data["options"]:
            raise ValueError("correct_answer must be one of the provided options")
        return v
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "question_text": "If 3x + 5 = 20, what is the value of x?",
                "options": ["x = 3", "x = 5", "x = 7", "x = 10"],
                "correct_answer": "x = 5",
                "difficulty": 0.3,
                "discrimination": 1.2,
                "guessing": 0.25,
                "topic": "Algebra",
                "subtopic": "Linear Equations",
                "tags": ["quantitative", "algebra", "equations"],
                "explanation": "Subtract 5 from both sides: 3x = 15, then divide by 3: x = 5",
                "bloom_level": "apply",
                "estimated_time_seconds": 90
            }
        }


class QuestionResponse(BaseModel):
    """API response model for delivering questions to clients."""
    question_id: str
    question_text: str
    options: list[str]
    topic: str
    estimated_time_seconds: int
    question_number: int
    total_questions: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "507f1f77bcf86cd799439011",
                "question_text": "If 3x + 5 = 20, what is the value of x?",
                "options": ["x = 3", "x = 5", "x = 7", "x = 10"],
                "topic": "Algebra",
                "estimated_time_seconds": 90,
                "question_number": 3,
                "total_questions": 10
            }
        }
