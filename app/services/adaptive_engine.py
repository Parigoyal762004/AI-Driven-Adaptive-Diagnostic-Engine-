"""
Adaptive Engine implementing Item Response Theory (IRT) algorithms.

This module implements the core IRT calculations:
- 2PL (Two-Parameter Logistic) model for probability estimation
- Newton-Raphson method for ability estimation
- Maximum information criterion for question selection
"""
import math
from typing import Tuple
from app.config import settings
from app.utils.exceptions import InvalidAbilityScoreException


class AdaptiveEngine:
    """
    Core adaptive testing engine using Item Response Theory.
    
    The 2PL IRT model:
    P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
    
    Where:
    - θ (theta): Examinee ability
    - a: Item discrimination parameter
    - b: Item difficulty parameter
    - c: Guessing parameter (pseudo-guessing)
    """
    
    def __init__(self):
        self.min_ability = settings.ability_min
        self.max_ability = settings.ability_max
        self.convergence_threshold = settings.convergence_threshold
    
    def probability_correct(
        self,
        ability: float,
        difficulty: float,
        discrimination: float,
        guessing: float = 0.25
    ) -> float:
        """
        Calculate probability of correct response using 3PL IRT model.
        
        Args:
            ability: Examinee's ability level (theta)
            difficulty: Question difficulty (b parameter)
            discrimination: Question discrimination (a parameter)
            guessing: Probability of guessing correctly (c parameter)
        
        Returns:
            Probability of correct answer (0 to 1)
        
        Example:
            >>> engine = AdaptiveEngine()
            >>> engine.probability_correct(ability=0.5, difficulty=0.3, discrimination=1.2)
            0.6457...
        """
        try:
            exponent = -discrimination * (ability - difficulty)
            # Prevent overflow
            exponent = max(min(exponent, 20), -20)
            
            prob = guessing + (1 - guessing) / (1 + math.exp(exponent))
            return max(0.0, min(1.0, prob))
            
        except (OverflowError, ValueError) as e:
            # Fallback for extreme values
            if exponent > 0:
                return guessing
            else:
                return 1.0
    
    def information(
        self,
        ability: float,
        difficulty: float,
        discrimination: float,
        guessing: float = 0.25
    ) -> float:
        """
        Calculate Fisher information for a question at given ability level.
        
        Information indicates how much a question contributes to ability estimation.
        Higher information = better discrimination at that ability level.
        
        Args:
            ability: Current ability estimate
            difficulty: Question difficulty
            discrimination: Question discrimination
            guessing: Guessing parameter
        
        Returns:
            Fisher information value
        """
        prob = self.probability_correct(ability, difficulty, discrimination, guessing)
        
        # Avoid division by zero
        if prob <= 0.01 or prob >= 0.99:
            return 0.0
        
        # 3PL information formula
        q = 1 - prob
        numerator = discrimination ** 2 * q * ((prob - guessing) ** 2)
        denominator = prob * ((1 - guessing) ** 2)
        
        if denominator == 0:
            return 0.0
        
        info = numerator / denominator
        return max(0.0, info)
    
    def update_ability(
        self,
        current_ability: float,
        question_difficulty: float,
        question_discrimination: float,
        is_correct: bool,
        guessing: float = 0.25,
        max_iterations: int = 10
    ) -> Tuple[float, float]:
        """
        Update ability estimate using Newton-Raphson method (Maximum Likelihood Estimation).
        
        This is a single-step update after one question response.
        
        Args:
            current_ability: Current ability estimate
            question_difficulty: Difficulty of answered question
            question_discrimination: Discrimination of answered question
            is_correct: Whether the answer was correct
            guessing: Guessing parameter
            max_iterations: Maximum Newton-Raphson iterations
        
        Returns:
            Tuple of (new_ability, standard_error)
        
        Raises:
            InvalidAbilityScoreException: If calculation produces invalid ability
        """
        ability = current_ability
        
        for _ in range(max_iterations):
            # Calculate probability and information
            prob = self.probability_correct(
                ability, question_difficulty, question_discrimination, guessing
            )
            info = self.information(
                ability, question_difficulty, question_discrimination, guessing
            )
            
            # Prevent division by zero
            if info < 1e-6:
                break
            
            # First derivative (score)
            response = 1 if is_correct else 0
            first_derivative = question_discrimination * (response - prob) * (prob - guessing) / (prob * (1 - guessing))
            
            # Newton-Raphson update
            delta = first_derivative / info
            ability = ability + delta
            
            # Check convergence
            if abs(delta) < 0.001:
                break
        
        # Clamp ability to valid range
        ability = max(self.min_ability, min(self.max_ability, ability))
        
        # Validate result
        if math.isnan(ability) or math.isinf(ability):
            raise InvalidAbilityScoreException(
                f"Ability calculation resulted in invalid value: {ability}"
            )
        
        # Calculate standard error
        if info > 0:
            standard_error = 1 / math.sqrt(info)
        else:
            standard_error = 1.0
        
        return ability, standard_error
    
    def estimate_ability_full(
        self,
        response_history: list[Tuple[float, float, bool, float]],
        initial_ability: float = 0.0
    ) -> Tuple[float, float]:
        """
        Estimate ability from complete response history using all responses.
        
        This uses Maximum Likelihood Estimation across all responses.
        
        Args:
            response_history: List of tuples (difficulty, discrimination, is_correct, guessing)
            initial_ability: Starting ability estimate
        
        Returns:
            Tuple of (estimated_ability, standard_error)
        """
        if not response_history:
            return initial_ability, 1.0
        
        ability = initial_ability
        max_iterations = 20
        
        for _ in range(max_iterations):
            first_deriv = 0.0
            second_deriv = 0.0
            
            for difficulty, discrimination, is_correct, guessing in response_history:
                prob = self.probability_correct(ability, difficulty, discrimination, guessing)
                
                # Avoid numerical issues
                prob = max(0.01, min(0.99, prob))
                
                response = 1 if is_correct else 0
                
                # Accumulate derivatives
                factor = (prob - guessing) / (prob * (1 - guessing))
                first_deriv += discrimination * (response - prob) * factor
                
                q = 1 - prob
                second_deriv += discrimination ** 2 * q * ((prob - guessing) ** 2) / (prob * ((1 - guessing) ** 2))
            
            # Newton-Raphson step
            if abs(second_deriv) < 1e-6:
                break
            
            delta = first_deriv / second_deriv
            ability = ability + delta
            
            # Convergence check
            if abs(delta) < 0.001:
                break
        
        # Clamp to valid range
        ability = max(self.min_ability, min(self.max_ability, ability))
        
        # Calculate standard error from information
        total_info = sum(
            self.information(ability, diff, disc, guess)
            for diff, disc, _, guess in response_history
        )
        
        if total_info > 0:
            standard_error = 1 / math.sqrt(total_info)
        else:
            standard_error = 1.0
        
        return ability, standard_error
    
    def has_converged(self, standard_error: float) -> bool:
        """
        Check if ability estimate has converged.
        
        Args:
            standard_error: Current standard error of ability estimate
        
        Returns:
            True if converged, False otherwise
        """
        return standard_error < self.convergence_threshold
