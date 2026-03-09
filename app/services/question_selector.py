"""
Question selection service using maximum information criterion.
"""
import random
from typing import Optional
from app.models.question import QuestionModel
from app.services.adaptive_engine import AdaptiveEngine
from app.utils.exceptions import QuestionPoolExhaustedException


class QuestionSelector:
    """
    Selects next question using maximum information criterion.
    
    Strategy:
    1. Filter questions by difficulty range (ability ± tolerance)
    2. Exclude already answered questions
    3. Select question with maximum information at current ability
    4. Add randomization to prevent predictability
    """
    
    def __init__(self, adaptive_engine: AdaptiveEngine):
        self.engine = adaptive_engine
        self.difficulty_tolerance = 1.5  # Search within ±1.5 of current ability
        self.min_pool_size = 3  # Minimum candidates before selection
    
    def select_next_question(
        self,
        available_questions: list[QuestionModel],
        current_ability: float,
        answered_question_ids: list[str],
        prefer_topic: Optional[str] = None
    ) -> QuestionModel:
        """
        Select the most informative next question.
        
        Args:
            available_questions: Pool of available questions
            current_ability: Current ability estimate
            answered_question_ids: IDs of already answered questions
            prefer_topic: Optional topic to prioritize
        
        Returns:
            Selected question
        
        Raises:
            QuestionPoolExhaustedException: If no suitable questions available
        """
        # Filter out already answered questions
        candidates = [
            q for q in available_questions
            if q.id not in answered_question_ids and q.is_active
        ]
        
        if not candidates:
            raise QuestionPoolExhaustedException(
                "All questions have been answered or no active questions available"
            )
        
        # Filter by difficulty range (ability ± tolerance)
        difficulty_min = current_ability - self.difficulty_tolerance
        difficulty_max = current_ability + self.difficulty_tolerance
        
        filtered = [
            q for q in candidates
            if difficulty_min <= q.difficulty <= difficulty_max
        ]
        
        # If too few matches, expand tolerance
        if len(filtered) < self.min_pool_size:
            filtered = candidates[:20]  # Take top 20 if filter too restrictive
        
        if not filtered:
            raise QuestionPoolExhaustedException(
                f"No questions available in difficulty range {difficulty_min:.2f} to {difficulty_max:.2f}"
            )
        
        # Prioritize preferred topic if specified
        if prefer_topic:
            topic_matches = [q for q in filtered if q.topic == prefer_topic]
            if topic_matches:
                filtered = topic_matches
        
        # Calculate information for each candidate
        question_info = []
        for question in filtered:
            info = self.engine.information(
                ability=current_ability,
                difficulty=question.difficulty,
                discrimination=question.discrimination,
                guessing=question.guessing
            )
            question_info.append((question, info))
        
        # Sort by information (descending)
        question_info.sort(key=lambda x: x[1], reverse=True)
        
        # Select from top candidates with some randomization
        # Take top 3 highest information questions and randomly pick one
        # This prevents test predictability while maintaining quality
        top_n = min(3, len(question_info))
        top_candidates = question_info[:top_n]
        
        selected_question, _ = random.choice(top_candidates)
        return selected_question
    
    def filter_by_difficulty_range(
        self,
        questions: list[QuestionModel],
        ability: float,
        tolerance: float = 1.5
    ) -> list[QuestionModel]:
        """
        Filter questions within difficulty range.
        
        Args:
            questions: All questions
            ability: Current ability
            tolerance: Difficulty range tolerance
        
        Returns:
            Filtered questions
        """
        min_diff = ability - tolerance
        max_diff = ability + tolerance
        
        return [
            q for q in questions
            if min_diff <= q.difficulty <= max_diff and q.is_active
        ]
    
    def get_balanced_question_by_topic(
        self,
        available_questions: list[QuestionModel],
        answered_question_ids: list[str],
        topic_counts: dict[str, int]
    ) -> Optional[QuestionModel]:
        """
        Select question to balance topic coverage.
        
        Args:
            available_questions: Available questions
            answered_question_ids: Already answered question IDs
            topic_counts: Count of answered questions per topic
        
        Returns:
            Question from least covered topic, or None
        """
        candidates = [
            q for q in available_questions
            if q.id not in answered_question_ids and q.is_active
        ]
        
        if not candidates:
            return None
        
        # Find topic with fewest questions answered
        min_count = min(topic_counts.values()) if topic_counts else 0
        underrepresented_topics = [
            topic for topic, count in topic_counts.items()
            if count == min_count
        ]
        
        # Filter candidates from underrepresented topics
        balanced_candidates = [
            q for q in candidates
            if q.topic in underrepresented_topics or q.topic not in topic_counts
        ]
        
        if balanced_candidates:
            return random.choice(balanced_candidates)
        
        return None
