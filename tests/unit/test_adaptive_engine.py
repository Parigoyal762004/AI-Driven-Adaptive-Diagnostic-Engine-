"""
Unit tests for the Adaptive Engine (IRT implementation).
"""
import pytest
import math
from app.services.adaptive_engine import AdaptiveEngine


class TestAdaptiveEngine:
    """Test cases for AdaptiveEngine IRT calculations."""
    
    @pytest.fixture
    def engine(self):
        """Create AdaptiveEngine instance for testing."""
        return AdaptiveEngine()
    
    def test_probability_correct_basic(self, engine):
        """Test basic probability calculation."""
        # For ability = difficulty, probability should be around 0.5 (+ guessing)
        prob = engine.probability_correct(
            ability=0.5,
            difficulty=0.5,
            discrimination=1.0,
            guessing=0.25
        )
        # With guessing, minimum is 0.25, so 0.5 + 0.25/2 ≈ 0.625
        assert 0.6 <= prob <= 0.65
    
    def test_probability_correct_high_ability(self, engine):
        """Test probability for high ability on easy question."""
        prob = engine.probability_correct(
            ability=2.0,
            difficulty=0.0,
            discrimination=1.0,
            guessing=0.25
        )
        # High ability on easy question should have high probability
        assert prob > 0.9
    
    def test_probability_correct_low_ability(self, engine):
        """Test probability for low ability on hard question."""
        prob = engine.probability_correct(
            ability=-2.0,
            difficulty=2.0,
            discrimination=1.0,
            guessing=0.25
        )
        # Low ability on hard question should be close to guessing
        assert prob < 0.3
    
    def test_probability_bounds(self, engine):
        """Test that probability is always between 0 and 1."""
        test_cases = [
            (3.0, -3.0, 2.0, 0.25),  # Extreme ability difference
            (-3.0, 3.0, 2.0, 0.25),  # Extreme difficulty difference
            (0.0, 0.0, 0.5, 0.25),   # Low discrimination
        ]
        
        for ability, difficulty, discrimination, guessing in test_cases:
            prob = engine.probability_correct(ability, difficulty, discrimination, guessing)
            assert 0.0 <= prob <= 1.0, f"Probability out of bounds: {prob}"
    
    def test_information_maximum_at_difficulty(self, engine):
        """Test that information is maximized when ability = difficulty."""
        difficulty = 0.5
        discrimination = 1.2
        
        # Calculate information at different ability levels
        info_at_difficulty = engine.information(difficulty, difficulty, discrimination)
        info_below = engine.information(difficulty - 1.0, difficulty, discrimination)
        info_above = engine.information(difficulty + 1.0, difficulty, discrimination)
        
        # Information should be highest when ability matches difficulty
        assert info_at_difficulty > info_below
        assert info_at_difficulty > info_above
    
    def test_information_non_negative(self, engine):
        """Test that information is always non-negative."""
        test_cases = [
            (0.0, 0.0, 1.0),
            (1.0, -1.0, 1.5),
            (-2.0, 2.0, 0.8),
        ]
        
        for ability, difficulty, discrimination in test_cases:
            info = engine.information(ability, difficulty, discrimination)
            assert info >= 0.0, f"Negative information: {info}"
    
    def test_update_ability_correct_answer(self, engine):
        """Test ability increases after correct answer on appropriate question."""
        current_ability = 0.0
        difficulty = 0.2  # Slightly easier than current ability
        discrimination = 1.0
        
        new_ability, se = engine.update_ability(
            current_ability=current_ability,
            question_difficulty=difficulty,
            question_discrimination=discrimination,
            is_correct=True
        )
        
        # Ability should increase after correct answer
        assert new_ability > current_ability
        # Standard error should be reasonable
        assert 0.0 < se < 2.0
    
    def test_update_ability_incorrect_answer(self, engine):
        """Test ability decreases after incorrect answer."""
        current_ability = 0.0
        difficulty = 0.2
        discrimination = 1.0
        
        new_ability, se = engine.update_ability(
            current_ability=current_ability,
            question_difficulty=difficulty,
            question_discrimination=discrimination,
            is_correct=False
        )
        
        # Ability should decrease after incorrect answer
        assert new_ability < current_ability
    
    def test_update_ability_clamping(self, engine):
        """Test that ability is clamped to valid range."""
        # Test upper bound
        high_ability = 2.8
        new_ability, _ = engine.update_ability(
            current_ability=high_ability,
            question_difficulty=0.0,
            question_discrimination=1.0,
            is_correct=True
        )
        assert new_ability <= engine.max_ability
        
        # Test lower bound
        low_ability = -2.8
        new_ability, _ = engine.update_ability(
            current_ability=low_ability,
            question_difficulty=2.0,
            question_discrimination=1.0,
            is_correct=False
        )
        assert new_ability >= engine.min_ability
    
    def test_estimate_ability_full_all_correct(self, engine):
        """Test ability estimation when all answers are correct."""
        # Simulate answering progressively harder questions correctly
        response_history = [
            (0.2, 1.0, True, 0.25),  # easy
            (0.5, 1.0, True, 0.25),  # medium
            (0.8, 1.0, True, 0.25),  # hard
        ]
        
        ability, se = engine.estimate_ability_full(response_history)
        
        # Should estimate high ability
        assert ability > 0.5
        # Standard error should decrease with more responses
        assert se < 1.0
    
    def test_estimate_ability_full_all_incorrect(self, engine):
        """Test ability estimation when all answers are incorrect."""
        response_history = [
            (0.2, 1.0, False, 0.25),
            (0.0, 1.0, False, 0.25),
            (-0.5, 1.0, False, 0.25),
        ]
        
        ability, se = engine.estimate_ability_full(response_history)
        
        # Should estimate low ability
        assert ability < 0.0
    
    def test_estimate_ability_full_mixed(self, engine):
        """Test ability estimation with mixed responses."""
        response_history = [
            (0.0, 1.0, True, 0.25),   # correct on easy
            (0.5, 1.0, False, 0.25),  # incorrect on medium
            (0.2, 1.0, True, 0.25),   # correct on easy
        ]
        
        ability, se = engine.estimate_ability_full(response_history)
        
        # Should estimate moderate ability
        assert -0.5 < ability < 0.5
    
    def test_has_converged(self, engine):
        """Test convergence detection."""
        # Low SE should indicate convergence
        assert engine.has_converged(0.2) == True
        
        # High SE should indicate no convergence
        assert engine.has_converged(0.8) == False
        
        # Threshold SE
        threshold = engine.convergence_threshold
        assert engine.has_converged(threshold - 0.01) == True
        assert engine.has_converged(threshold + 0.01) == False
    
    def test_discrimination_effect(self, engine):
        """Test that higher discrimination gives more information."""
        ability = 0.5
        difficulty = 0.5
        
        info_low_disc = engine.information(ability, difficulty, discrimination=0.8)
        info_high_disc = engine.information(ability, difficulty, discrimination=1.5)
        
        # Higher discrimination should give more information
        assert info_high_disc > info_low_disc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
