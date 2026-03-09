"""
API routes for question delivery and answer submission.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.question import QuestionResponse
from app.models.schemas import SubmitAnswerRequest, SubmitAnswerResponse
from app.repositories.question_repository import QuestionRepository
from app.repositories.session_repository import SessionRepository
from app.services.adaptive_engine import AdaptiveEngine
from app.services.question_selector import QuestionSelector
from app.dependencies import (
    get_question_repository,
    get_session_repository,
    get_adaptive_engine,
    get_question_selector
)
from app.utils.exceptions import (
    SessionNotFoundException,
    QuestionNotFoundException,
    QuestionPoolExhaustedException,
    SessionAlreadyCompletedException,
    InvalidAnswerException
)


router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/sessions/{session_id}/next-question", response_model=QuestionResponse)
async def get_next_question(
    session_id: str,
    question_repo: QuestionRepository = Depends(get_question_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
    question_selector: QuestionSelector = Depends(get_question_selector)
):
    """
    Get the next adaptive question for a session.
    
    This endpoint:
    1. Retrieves current session state
    2. Selects most informative question based on current ability
    3. Excludes already answered questions
    
    Args:
        session_id: Session identifier
        question_repo: Question repository dependency
        session_repo: Session repository dependency
        question_selector: Question selector service
    
    Returns:
        QuestionResponse with next question details
    
    Raises:
        HTTPException: If session not found or completed
    """
    try:
        # Get session
        session = await session_repo.get_session(session_id)
        
        # Check if session is completed
        if session.status == "completed":
            raise SessionAlreadyCompletedException()
        
        # Check if max questions reached
        if session.questions_remaining <= 0:
            # Auto-complete session
            await session_repo.mark_completed(session_id)
            raise SessionAlreadyCompletedException(
                "Maximum questions reached. Session completed."
            )
        
        # Get all active questions
        all_questions = await question_repo.get_all_active()
        
        if not all_questions:
            raise QuestionPoolExhaustedException("No active questions available")
        
        # Select next question
        next_question = question_selector.select_next_question(
            available_questions=all_questions,
            current_ability=session.current_ability,
            answered_question_ids=session.answered_question_ids
        )
        
        return QuestionResponse(
            question_id=next_question.id,
            question_text=next_question.question_text,
            options=next_question.options,
            topic=next_question.topic,
            estimated_time_seconds=next_question.estimated_time_seconds,
            question_number=session.questions_answered + 1,
            total_questions=session.questions_answered + session.questions_remaining
        )
        
    except (SessionNotFoundException, SessionAlreadyCompletedException, 
            QuestionPoolExhaustedException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/sessions/{session_id}/answers", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    question_repo: QuestionRepository = Depends(get_question_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
    adaptive_engine: AdaptiveEngine = Depends(get_adaptive_engine)
):
    """
    Submit an answer and update ability estimate.
    
    This endpoint:
    1. Validates the answer
    2. Checks correctness
    3. Updates ability estimate using IRT
    4. Records response in session
    5. Checks for convergence
    
    Args:
        session_id: Session identifier
        request: Answer submission data
        question_repo: Question repository dependency
        session_repo: Session repository dependency
        adaptive_engine: Adaptive engine service
    
    Returns:
        SubmitAnswerResponse with feedback and updated state
    
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Get session and question
        session = await session_repo.get_session(session_id)
        question = await question_repo.get_by_id(request.question_id)
        
        # Check if session is completed
        if session.status == "completed":
            raise SessionAlreadyCompletedException()
        
        # Validate answer is one of the options
        if request.user_answer not in question.options:
            raise InvalidAnswerException(
                f"Answer must be one of: {', '.join(question.options)}"
            )
        
        # Check correctness
        is_correct = request.user_answer == question.correct_answer
        
        # Store ability before update
        ability_before = session.current_ability
        
        # Update ability using IRT
        new_ability, new_standard_error = adaptive_engine.update_ability(
            current_ability=session.current_ability,
            question_difficulty=question.difficulty,
            question_discrimination=question.discrimination,
            is_correct=is_correct,
            guessing=question.guessing
        )
        
        # Record response
        session.add_response(
            question_id=question.id,
            user_answer=request.user_answer,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            question_difficulty=question.difficulty,
            question_discrimination=question.discrimination,
            ability_before=ability_before,
            ability_after=new_ability,
            time_spent_seconds=request.time_spent_seconds
        )
        
        # Update session ability
        session.update_ability(new_ability, new_standard_error)
        
        # Check convergence
        session.check_convergence(threshold=adaptive_engine.convergence_threshold)
        
        # Check if session should be completed
        session_complete = session.questions_remaining <= 0
        if session_complete:
            session.mark_completed()
        
        # Save session
        await session_repo.update_session(session)
        
        return SubmitAnswerResponse(
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            updated_ability=new_ability,
            standard_error=new_standard_error,
            questions_remaining=session.questions_remaining,
            session_complete=session_complete
        )
        
    except (SessionNotFoundException, QuestionNotFoundException, 
            SessionAlreadyCompletedException, InvalidAnswerException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
