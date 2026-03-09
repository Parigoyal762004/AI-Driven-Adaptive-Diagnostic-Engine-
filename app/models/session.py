"""
User session model for tracking adaptive test progress.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ResponseRecord(BaseModel):
    """Individual question response within a session."""
    question_id: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    time_spent_seconds: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # IRT parameters at time of question
    question_difficulty: float
    question_discrimination: float
    ability_before: float
    ability_after: float


class UserSessionModel(BaseModel):
    """
    Tracks a user's adaptive testing session.
    
    The session maintains:
    - Current ability estimate (theta)
    - Response history
    - Convergence metrics
    """
    id: Optional[str] = Field(None, alias="_id")
    session_id: str = Field(..., description="Unique session identifier")
    
    # User Information (optional - can be anonymous)
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    
    # Ability Tracking
    current_ability: float = Field(0.0, ge=-3.0, le=3.0, description="Current ability estimate (theta)")
    ability_history: list[float] = Field(default_factory=list, description="History of ability estimates")
    standard_error: float = Field(1.0, ge=0.0, description="Standard error of ability estimate")
    
    # Session State
    status: Literal["in_progress", "completed", "expired"] = "in_progress"
    responses: list[ResponseRecord] = Field(default_factory=list)
    questions_answered: int = 0
    questions_remaining: int = 10
    
    # Metadata
    test_type: str = Field("GRE", description="Type of test (e.g., GRE, SAT)")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Convergence Tracking
    has_converged: bool = False
    convergence_question_number: Optional[int] = None
    
    def add_response(
        self,
        question_id: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        question_difficulty: float,
        question_discrimination: float,
        ability_before: float,
        ability_after: float,
        time_spent_seconds: Optional[int] = None
    ) -> None:
        """Add a response to the session and update counters."""
        response = ResponseRecord(
            question_id=question_id,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            question_difficulty=question_difficulty,
            question_discrimination=question_discrimination,
            ability_before=ability_before,
            ability_after=ability_after
        )
        self.responses.append(response)
        self.questions_answered += 1
        self.questions_remaining -= 1
        self.last_activity = datetime.utcnow()
    
    def update_ability(self, new_ability: float, new_standard_error: float) -> None:
        """Update ability estimate and track history."""
        self.ability_history.append(self.current_ability)
        self.current_ability = new_ability
        self.standard_error = new_standard_error
    
    def mark_completed(self) -> None:
        """Mark session as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def check_convergence(self, threshold: float = 0.3) -> bool:
        """
        Check if ability estimate has converged.
        
        Convergence occurs when standard error falls below threshold
        or when ability estimate stabilizes.
        """
        if self.standard_error < threshold:
            if not self.has_converged:
                self.has_converged = True
                self.convergence_question_number = self.questions_answered
            return True
        return False
    
    @property
    def answered_question_ids(self) -> list[str]:
        """Get list of already answered question IDs."""
        return [resp.question_id for resp in self.responses]
    
    @property
    def accuracy(self) -> float:
        """Calculate percentage of correct answers."""
        if not self.responses:
            return 0.0
        correct = sum(1 for resp in self.responses if resp.is_correct)
        return correct / len(self.responses)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "user_id": "user_456",
                "current_ability": 0.5,
                "standard_error": 0.4,
                "status": "in_progress",
                "questions_answered": 3,
                "questions_remaining": 7,
                "test_type": "GRE"
            }
        }


class SessionResponse(BaseModel):
    """API response for session details."""
    session_id: str
    current_ability: float
    standard_error: float
    questions_answered: int
    questions_remaining: int
    status: str
    accuracy: float
    has_converged: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "current_ability": 0.5,
                "standard_error": 0.35,
                "questions_answered": 5,
                "questions_remaining": 5,
                "status": "in_progress",
                "accuracy": 0.6,
                "has_converged": False
            }
        }
