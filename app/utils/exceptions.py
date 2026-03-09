"""
Custom exceptions for the Adaptive Testing Engine.
Each exception maps to a specific HTTP status code.
"""


class AdaptiveTestingException(Exception):
    """Base exception for all custom exceptions."""
    status_code: int = 500
    detail: str = "An internal error occurred"
    
    def __init__(self, detail: str = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class SessionNotFoundException(AdaptiveTestingException):
    """Raised when a session ID doesn't exist."""
    status_code = 404
    detail = "Session not found"


class QuestionNotFoundException(AdaptiveTestingException):
    """Raised when a question ID doesn't exist."""
    status_code = 404
    detail = "Question not found"


class QuestionPoolExhaustedException(AdaptiveTestingException):
    """Raised when no suitable questions are available."""
    status_code = 422
    detail = "No suitable questions available for current ability level"


class SessionExpiredException(AdaptiveTestingException):
    """Raised when attempting to use an expired session."""
    status_code = 410
    detail = "Session has expired"


class SessionAlreadyCompletedException(AdaptiveTestingException):
    """Raised when attempting to answer questions in a completed session."""
    status_code = 409
    detail = "Session is already completed"


class InvalidAnswerException(AdaptiveTestingException):
    """Raised when an answer doesn't match question options."""
    status_code = 400
    detail = "Invalid answer provided"


class InvalidAbilityScoreException(AdaptiveTestingException):
    """Raised when ability score is outside valid range."""
    status_code = 500
    detail = "Ability score calculation error: value outside valid range"


class DatabaseConnectionException(AdaptiveTestingException):
    """Raised when database connection fails."""
    status_code = 503
    detail = "Database connection error"


class AIServiceException(AdaptiveTestingException):
    """Raised when AI service (OpenAI/Anthropic) fails."""
    status_code = 503
    detail = "AI service temporarily unavailable"


class ValidationException(AdaptiveTestingException):
    """Raised for validation errors."""
    status_code = 422
    detail = "Validation error"
