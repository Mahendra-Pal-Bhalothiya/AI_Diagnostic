import math
import numpy as np
from typing import Tuple

class AdaptiveAlgorithm:
    """
    Implementation of 1-Parameter Logistic IRT Model (Rasch Model)
    P(θ) = 1 / (1 + exp(-(θ - b)))
    """
    
    def __init__(self):
        self.D = 1.702  # Scaling constant
        
    def calculate_probability_correct(self, theta: float, difficulty: float) -> float:
        """Calculate probability of correct answer"""
        return 1 / (1 + math.exp(-self.D * (theta - difficulty)))
    
    def update_ability(self, 
                      current_theta: float, 
                      difficulty: float, 
                      response: int,
                      prior_variance: float = 1.0) -> Tuple[float, float]:
        """Update ability estimate using MLE"""
        p = self.calculate_probability_correct(current_theta, difficulty)
        information = self.D**2 * p * (1 - p)
        new_error = 1 / math.sqrt(information + 1e-10)
        gradient = self.D * (response - p)
        learning_rate = 0.5
        new_theta = current_theta + learning_rate * gradient / (information + 1e-10)
        new_theta = max(-3, min(3, new_theta))
        return new_theta, new_error
    
    def select_next_difficulty(self, 
                              current_theta: float, 
                              measurement_error: float,
                              answered_questions: list) -> float:
        """Select next question difficulty"""
        if not answered_questions:
            return self._convert_theta_to_difficulty(current_theta)
        
        target_difficulty = current_theta
        
        if measurement_error > 0.3:
            noise = np.random.normal(0, measurement_error * 0.5)
            target_difficulty += noise
        
        return self._convert_theta_to_difficulty(target_difficulty)
    
    def _convert_theta_to_difficulty(self, theta: float) -> float:
        """Convert theta (-3 to 3) to difficulty (0.1 to 1.0)"""
        difficulty = 1 / (1 + math.exp(-theta))
        return 0.1 + 0.9 * difficulty
    
    def _convert_difficulty_to_theta(self, difficulty: float) -> float:
        """Convert difficulty (0.1 to 1.0) to theta (-3 to 3)"""
        normalized = (difficulty - 0.1) / 0.9
        normalized = max(0.01, min(0.99, normalized))
        return math.log(normalized / (1 - normalized))