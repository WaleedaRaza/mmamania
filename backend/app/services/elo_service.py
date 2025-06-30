from typing import Tuple
import math


class EloService:
    """Service for calculating Elo ratings for user predictions"""
    
    def __init__(self, k_factor: int = 32, base_rating: int = 1500):
        self.k_factor = k_factor
        self.base_rating = base_rating
    
    def calculate_expected_score(self, rating_a: int, rating_b: int) -> float:
        """Calculate expected score for player A against player B"""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
    
    def calculate_new_rating(self, current_rating: int, expected_score: float, actual_score: float) -> int:
        """Calculate new Elo rating based on expected vs actual score"""
        new_rating = current_rating + self.k_factor * (actual_score - expected_score)
        return round(new_rating)
    
    def calculate_prediction_elo_change(
        self, 
        user_rating: int, 
        fight_difficulty: float,
        prediction_correct: bool,
        method_correct: bool = False,
        round_correct: bool = False
    ) -> Tuple[int, int]:
        """
        Calculate Elo change for a fight prediction
        
        Args:
            user_rating: Current user Elo rating
            fight_difficulty: Difficulty multiplier (0.5-2.0)
            prediction_correct: Whether the winner prediction was correct
            method_correct: Whether the method prediction was correct
            round_correct: Whether the round prediction was correct
            
        Returns:
            Tuple of (elo_change, new_rating)
        """
        # Base expected score (50% for random prediction)
        expected_score = 0.5
        
        # Calculate actual score based on prediction accuracy
        actual_score = 0.0
        if prediction_correct:
            actual_score += 0.6  # Base points for correct winner
            if method_correct:
                actual_score += 0.3  # Bonus for correct method
            if round_correct:
                actual_score += 0.1  # Bonus for correct round
        
        # Apply fight difficulty multiplier
        adjusted_k_factor = self.k_factor * fight_difficulty
        
        # Calculate new rating
        new_rating = current_rating + adjusted_k_factor * (actual_score - expected_score)
        elo_change = round(new_rating - current_rating)
        
        return elo_change, round(new_rating)
    
    def calculate_fight_difficulty(self, odds_a: float, odds_b: float) -> float:
        """
        Calculate fight difficulty based on betting odds
        
        Args:
            odds_a: Odds for fighter A
            odds_b: Odds for fighter B
            
        Returns:
            Difficulty multiplier (0.5-2.0)
        """
        if not odds_a or not odds_b:
            return 1.0
        
        # Convert odds to probabilities
        prob_a = 1 / odds_a if odds_a > 0 else 0.5
        prob_b = 1 / odds_b if odds_b > 0 else 0.5
        
        # Normalize probabilities
        total_prob = prob_a + prob_b
        if total_prob > 0:
            prob_a /= total_prob
            prob_b /= total_prob
        
        # Calculate difficulty based on how close the odds are
        # Closer odds = higher difficulty
        difficulty = 1.0 + abs(prob_a - prob_b) * 2
        
        return min(max(difficulty, 0.5), 2.0)
    
    def get_rating_category(self, rating: int) -> str:
        """Get rating category based on Elo score"""
        if rating >= 2000:
            return "Elite"
        elif rating >= 1800:
            return "Expert"
        elif rating >= 1600:
            return "Advanced"
        elif rating >= 1400:
            return "Intermediate"
        else:
            return "Beginner" 