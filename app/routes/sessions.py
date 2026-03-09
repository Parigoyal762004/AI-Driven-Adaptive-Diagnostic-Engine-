"""
API routes for session management.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    CreateSessionRequest,
    CreateSessionResponse
)

from app.models.session import SessionResponse
from app.models.session import UserSessionModel
from app.repositories.session_repository import SessionRepository
from app.dependencies import get_session_repository
from app.config import settings
from app.utils.exceptions import SessionNotFoundException


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Create a new testing session.
    
    Args:
        request: Session creation parameters
        session_repo: Session repository dependency
    
    Returns:
        CreateSessionResponse with session_id and initial state
    """
    session = await session_repo.create_session(
        user_id=request.user_id,
        user_name=request.user_name,
        test_type=request.test_type,
        max_questions=request.max_questions,
        initial_ability=settings.default_ability
    )
    
    return CreateSessionResponse(
        session_id=session.session_id,
        message="Session created successfully. Ready to start adaptive testing.",
        initial_ability=session.current_ability,
        max_questions=request.max_questions
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_details(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Get detailed information about a session.
    
    Args:
        session_id: Session identifier
        session_repo: Session repository dependency
    
    Returns:
        SessionResponse with current session state
    
    Raises:
        HTTPException: If session not found
    """
    try:
        session = await session_repo.get_session(session_id)
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return SessionResponse(
        session_id=session.session_id,
        current_ability=session.current_ability,
        standard_error=session.standard_error,
        questions_answered=session.questions_answered,
        questions_remaining=session.questions_remaining,
        status=session.status,
        accuracy=session.accuracy,
        has_converged=session.has_converged
    )


@router.get("/{session_id}/history")
async def get_session_history(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Get complete response history for a session.
    
    Args:
        session_id: Session identifier
        session_repo: Session repository dependency
    
    Returns:
        Complete session with all responses
    
    Raises:
        HTTPException: If session not found
    """
    try:
        session = await session_repo.get_session(session_id)
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "session_id": session.session_id,
        "status": session.status,
        "current_ability": session.current_ability,
        "ability_history": session.ability_history,
        "responses": [
            {
                "question_id": resp.question_id,
                "user_answer": resp.user_answer,
                "correct_answer": resp.correct_answer,
                "is_correct": resp.is_correct,
                "time_spent_seconds": resp.time_spent_seconds,
                "ability_before": resp.ability_before,
                "ability_after": resp.ability_after,
                "question_difficulty": resp.question_difficulty
            }
            for resp in session.responses
        ],
        "total_questions": len(session.responses),
        "accuracy": session.accuracy
    }


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Delete a session.
    
    Args:
        session_id: Session to delete
        session_repo: Session repository dependency
    
    Returns:
        No content on success
    
    Raises:
        HTTPException: If session not found
    """
    deleted = await session_repo.delete_session(session_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return None
