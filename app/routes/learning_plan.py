"""
API routes for AI-generated learning plans.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import LearningPlanResponse
from app.repositories.question_repository import QuestionRepository
from app.repositories.session_repository import SessionRepository
from app.services.learning_plan_generator import LearningPlanGenerator
from app.dependencies import (
    get_question_repository,
    get_session_repository,
    get_learning_plan_generator
)
from app.utils.exceptions import SessionNotFoundException, AIServiceException


router = APIRouter(prefix="/api", tags=["learning-plan"])


@router.get("/sessions/{session_id}/learning-plan", response_model=LearningPlanResponse)
async def get_learning_plan(
    session_id: str,
    question_repo: QuestionRepository = Depends(get_question_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
    plan_generator: LearningPlanGenerator = Depends(get_learning_plan_generator)
):
    """
    Generate personalized learning plan based on session performance.
    
    This endpoint:
    1. Analyzes session responses to identify strengths/weaknesses
    2. Uses AI (OpenAI or Anthropic) to generate personalized recommendations
    3. Creates a structured study plan
    4. Estimates required study hours
    
    Best used after session completion, but can be called anytime.
    
    Args:
        session_id: Session identifier
        question_repo: Question repository dependency
        session_repo: Session repository dependency
        plan_generator: Learning plan generator service
    
    Returns:
        LearningPlanResponse with personalized recommendations
    
    Raises:
        HTTPException: If session not found or AI service fails
    """
    try:
        # Get session
        session = await session_repo.get_session(session_id)
        
        # Check if session has responses
        if not session.responses:
            raise HTTPException(
                status_code=400,
                detail="Cannot generate learning plan: no questions answered yet"
            )
        
        # Get question details for analysis
        questions_map = {}
        for response in session.responses:
            try:
                question = await question_repo.get_by_id(response.question_id)
                questions_map[response.question_id] = {
                    "topic": question.topic,
                    "subtopic": question.subtopic,
                    "difficulty": question.difficulty,
                    "question_text": question.question_text,
                    "tags": question.tags
                }
            except Exception:
                # If question not found, skip it
                continue
        
        # Generate learning plan
        try:
            plan = await plan_generator.generate_plan(session, questions_map)
        except AIServiceException as e:
            # AI service failed, but we can still return a basic plan
            print(f"AI service error: {e}, using fallback")
            plan = {
                "session_id": session.session_id,
                "final_ability": session.current_ability,
                "accuracy": session.accuracy,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [
                    "Review all questions you got wrong",
                    "Practice more questions in weak areas",
                    "Take regular breaks while studying"
                ],
                "study_plan": "Continue practicing adaptive tests to improve your score.",
                "estimated_study_hours": 10
            }
        
        return LearningPlanResponse(**plan)
        
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
