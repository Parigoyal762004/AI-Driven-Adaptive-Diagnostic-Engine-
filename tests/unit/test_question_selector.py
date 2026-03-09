"""
Unit tests for the Question Selector service.
"""
import pytest
from app.models.question import QuestionModel
from app.services.adaptive_engine import AdaptiveEngine
from app.services.question_selector import QuestionSelector
from app.utils.exceptions import QuestionPoolExhaustedException


class TestQuestionSelector:
    """Test cases for QuestionSelector."""
    
    @pytest.fixture
    def engine(self):
        """Create AdaptiveEngine instance."""
        return AdaptiveEngine()
    
    @pytest.fixture
    def selector(self, engine):
        """Create QuestionSelector instance."""
        return QuestionSelector(engine)
    
    @pytest.fixture
    def sample_questions(self):
        """Create sample questions for testing."""
        return [
            QuestionModel(
                id=f"q{i}",
                question_text=f"Question {i}",
                options=["A", "B", "C", "D"],
                correct_answer="A",
                difficulty=diff,
                discrimination=1.0,
                topic="Math",
                is_active=True
            )
            for i, diff in enumerate([0.2, 0.3, 0.5, 0.6, 0.8, 1.0])
        ]
    
    def test_select_next_question_basic(self, selector, sample_questions):
        """Test basic question selection."""
        selected = selector.select_next_question(
            available_questions=sample_questions,
            current_ability=0.5,
            answered_question_ids=[]
        )
        
        assert selected is not None
        assert selected.id in [q.id for q in sample_questions]
    
    def test_select_excludes_answered(self, selector, sample_questions):
        """Test that answered questions are excluded."""
        answered_ids = ["q0", "q1", "q2"]
        
        selected = selector.select_next_question(
            available_questions=sample_questions,
            current_ability=0.5,
            answered_question_ids=answered_ids
        )
        
        # Should not select any answered question
        assert selected.id not in answered_ids
    
    def test_select_prefers_appropriate_difficulty(self, selector, sample_questions):
        """Test that selector prefers questions near current ability."""
        # For ability 0.5, should prefer questions with difficulty around 0.5
        selected = selector.select_next_question(
            available_questions=sample_questions,
            current_ability=0.5,
            answered_question_ids=[]
        )
        
        # Selected difficulty should be reasonably close to ability
        assert abs(selected.difficulty - 0.5) <= 1.5
    
    def test_select_raises_when_pool_exhausted(self, selector, sample_questions):
        """Test exception when all questions answered."""
        answered_ids = [q.id for q in sample_questions]
        
        with pytest.raises(QuestionPoolExhaustedException):
            selector.select_next_question(
                available_questions=sample_questions,
                current_ability=0.5,
                answered_question_ids=answered_ids
            )
    
    def test_select_raises_when_no_questions(self, selector):
        """Test exception when no questions available."""
        with pytest.raises(QuestionPoolExhaustedException):
            selector.select_next_question(
                available_questions=[],
                current_ability=0.5,
                answered_question_ids=[]
            )
    
    def test_select_with_topic_preference(self, selector):
        """Test topic-based selection."""
        questions = [
            QuestionModel(
                id="q1",
                question_text="Math question",
                options=["A", "B"],
                correct_answer="A",
                difficulty=0.5,
                topic="Math",
                is_active=True
            ),
            QuestionModel(
                id="q2",
                question_text="Science question",
                options=["A", "B"],
                correct_answer="A",
                difficulty=0.5,
                topic="Science",
                is_active=True
            ),
        ]
        
        selected = selector.select_next_question(
            available_questions=questions,
            current_ability=0.5,
            answered_question_ids=[],
            prefer_topic="Math"
        )
        
        # Should prefer Math topic when available
        assert selected.topic == "Math"
    
    def test_filter_by_difficulty_range(self, selector, sample_questions):
        """Test difficulty range filtering."""
        filtered = selector.filter_by_difficulty_range(
            questions=sample_questions,
            ability=0.5,
            tolerance=0.3
        )
        
        # All filtered questions should be within tolerance
        for q in filtered:
            assert 0.2 <= q.difficulty <= 0.8
    
    def test_handles_inactive_questions(self, selector):
        """Test that inactive questions are excluded."""
        questions = [
            QuestionModel(
                id="q1",
                question_text="Active",
                options=["A", "B"],
                correct_answer="A",
                difficulty=0.5,
                is_active=True
            ),
            QuestionModel(
                id="q2",
                question_text="Inactive",
                options=["A", "B"],
                correct_answer="A",
                difficulty=0.5,
                is_active=False
            ),
        ]
        
        selected = selector.select_next_question(
            available_questions=questions,
            current_ability=0.5,
            answered_question_ids=[]
        )
        
        # Should only select active question
        assert selected.is_active == True
        assert selected.id == "q1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
