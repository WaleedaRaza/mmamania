from typing import Dict, Any, List, Optional
import random
import numpy as np
from ..models.fighter import Fighter
from ..models.fight import Fight


class MLService:
    """Service for ML predictions and analytics"""
    
    def __init__(self):
        # TODO: Load trained models
        self.models_loaded = False
    
    def predict_fight_outcome(self, fighter_a: Fighter, fighter_b: Fighter, fight: Fight) -> Dict[str, Any]:
        """
        Predict fight outcome using ML models
        
        Args:
            fighter_a: First fighter
            fighter_b: Second fighter
            fight: Fight details
            
        Returns:
            Dictionary with predictions and confidence
        """
        # TODO: Implement actual ML model prediction
        # For now, return mock predictions based on fighter stats
        
        # Calculate basic probabilities based on records
        total_a = fighter_a.record.get("wins", 0) + fighter_a.record.get("losses", 0)
        total_b = fighter_b.record.get("wins", 0) + fighter_b.record.get("losses", 0)
        
        win_rate_a = fighter_a.record.get("wins", 0) / max(total_a, 1)
        win_rate_b = fighter_b.record.get("wins", 0) / max(total_b, 1)
        
        # Adjust for reach advantage
        reach_advantage = 0
        if fighter_a.reach and fighter_b.reach:
            reach_diff = fighter_a.reach - fighter_b.reach
            reach_advantage = min(max(reach_diff / 10, -0.1), 0.1)
        
        # Calculate final probabilities
        prob_a = (win_rate_a + reach_advantage) / (win_rate_a + win_rate_b + 2 * reach_advantage)
        prob_b = 1 - prob_a
        
        # Add some randomness for realistic predictions
        confidence = random.uniform(0.6, 0.9)
        
        # Determine recommended pick
        recommended_pick = fighter_a.id if prob_a > prob_b else fighter_b.id
        
        # Style analysis
        style_analysis = self._analyze_style_matchup(fighter_a, fighter_b)
        
        # Key factors
        key_factors = self._identify_key_factors(fighter_a, fighter_b, fight)
        
        return {
            "fighter_a_probability": round(prob_a, 3),
            "fighter_b_probability": round(prob_b, 3),
            "confidence": round(confidence, 3),
            "recommended_pick": str(recommended_pick),
            "style_analysis": style_analysis,
            "key_factors": key_factors,
            "predicted_method": self._predict_method(fighter_a, fighter_b),
            "predicted_rounds": self._predict_rounds(fighter_a, fighter_b)
        }
    
    def analyze_fighter(self, fighter: Fighter) -> Dict[str, Any]:
        """
        Analyze a fighter's strengths, weaknesses, and style
        
        Args:
            fighter: Fighter to analyze
            
        Returns:
            Dictionary with fighter analytics
        """
        # Calculate basic stats
        total_fights = fighter.record.get("wins", 0) + fighter.record.get("losses", 0)
        win_rate = fighter.record.get("wins", 0) / max(total_fights, 1)
        
        # Analyze strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if win_rate > 0.7:
            strengths.append("High win rate")
        elif win_rate < 0.4:
            weaknesses.append("Low win rate")
        
        if fighter.reach and fighter.reach > 76:
            strengths.append("Long reach advantage")
        elif fighter.reach and fighter.reach < 70:
            weaknesses.append("Short reach")
        
        if fighter.style:
            if "Striker" in fighter.style:
                strengths.append("Strong striking game")
            if "Grappler" in fighter.style:
                strengths.append("Excellent grappling")
        
        # Style breakdown
        style_breakdown = {
            "primary_style": fighter.style or "Mixed",
            "stance": fighter.stance or "Unknown",
            "reach_advantage": fighter.reach > 74 if fighter.reach else False,
            "experience_level": self._get_experience_level(total_fights)
        }
        
        # Performance trends (mock data)
        performance_trends = {
            "recent_form": random.choice(["Winning", "Mixed", "Losing"]),
            "finish_rate": random.uniform(0.3, 0.8),
            "decision_rate": random.uniform(0.2, 0.7),
            "avg_fight_time": random.uniform(8, 15)
        }
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "style_breakdown": style_breakdown,
            "performance_trends": performance_trends,
            "win_rate": round(win_rate, 3),
            "total_fights": total_fights
        }
    
    def generate_fight_insights(self, fighter_a: Fighter, fighter_b: Fighter, fight: Fight) -> Dict[str, Any]:
        """
        Generate detailed insights for a fight matchup
        
        Args:
            fighter_a: First fighter
            fighter_b: Second fighter
            fight: Fight details
            
        Returns:
            Dictionary with fight insights
        """
        # Matchup analysis
        matchup_analysis = {
            "style_clash": self._analyze_style_clash(fighter_a, fighter_b),
            "reach_advantage": self._calculate_reach_advantage(fighter_a, fighter_b),
            "experience_gap": self._calculate_experience_gap(fighter_a, fighter_b),
            "momentum_factor": self._calculate_momentum(fighter_a, fighter_b)
        }
        
        # Historical comparison
        historical_comparison = {
            "similar_opponents": self._find_similar_opponents(fighter_a, fighter_b),
            "common_opponents": self._find_common_opponents(fighter_a, fighter_b),
            "performance_against_style": self._analyze_style_performance(fighter_a, fighter_b)
        }
        
        # Betting analysis
        betting_analysis = {
            "value_pick": self._identify_value_pick(fighter_a, fighter_b, fight),
            "risk_level": self._assess_risk_level(fighter_a, fighter_b),
            "prop_bet_opportunities": self._suggest_prop_bets(fighter_a, fighter_b)
        }
        
        # Risk factors
        risk_factors = self._identify_risk_factors(fighter_a, fighter_b, fight)
        
        return {
            "matchup_analysis": matchup_analysis,
            "historical_comparison": historical_comparison,
            "betting_analysis": betting_analysis,
            "risk_factors": risk_factors
        }
    
    def get_prediction_leaderboard(self, period: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get ML prediction accuracy leaderboard
        
        Args:
            period: Time period (week, month, all)
            limit: Number of entries to return
            
        Returns:
            List of leaderboard entries
        """
        # TODO: Implement actual leaderboard calculation
        # For now, return mock data
        leaderboard = []
        for i in range(min(limit, 20)):
            leaderboard.append({
                "rank": i + 1,
                "user_id": f"user_{i}",
                "username": f"Predictor_{i}",
                "accuracy": round(random.uniform(0.6, 0.9), 3),
                "total_predictions": random.randint(10, 100),
                "correct_predictions": random.randint(5, 80)
            })
        
        # Sort by accuracy
        leaderboard.sort(key=lambda x: x["accuracy"], reverse=True)
        
        return leaderboard
    
    def _analyze_style_matchup(self, fighter_a: Fighter, fighter_b: Fighter) -> Dict[str, Any]:
        """Analyze style matchup between two fighters"""
        styles = {
            "striker_vs_grappler": "Striker vs Grappler",
            "striker_vs_striker": "Striker vs Striker", 
            "grappler_vs_grappler": "Grappler vs Grappler",
            "mixed_vs_specialist": "Mixed vs Specialist"
        }
        
        style_a = fighter_a.style or "Mixed"
        style_b = fighter_b.style or "Mixed"
        
        if "Striker" in style_a and "Grappler" in style_b:
            matchup_type = "striker_vs_grappler"
        elif "Grappler" in style_a and "Striker" in style_b:
            matchup_type = "striker_vs_grappler"
        elif "Striker" in style_a and "Striker" in style_b:
            matchup_type = "striker_vs_striker"
        elif "Grappler" in style_a and "Grappler" in style_b:
            matchup_type = "grappler_vs_grappler"
        else:
            matchup_type = "mixed_vs_specialist"
        
        return {
            "matchup_type": matchup_type,
            "description": styles[matchup_type],
            "advantage": self._determine_style_advantage(style_a, style_b)
        }
    
    def _identify_key_factors(self, fighter_a: Fighter, fighter_b: Fighter, fight: Fight) -> List[str]:
        """Identify key factors that could decide the fight"""
        factors = []
        
        # Reach advantage
        if fighter_a.reach and fighter_b.reach:
            reach_diff = abs(fighter_a.reach - fighter_b.reach)
            if reach_diff > 3:
                factors.append(f"Reach advantage ({reach_diff:.1f} inches)")
        
        # Experience gap
        total_a = fighter_a.record.get("wins", 0) + fighter_a.record.get("losses", 0)
        total_b = fighter_b.record.get("wins", 0) + fighter_b.record.get("losses", 0)
        exp_diff = abs(total_a - total_b)
        if exp_diff > 5:
            factors.append(f"Experience gap ({exp_diff} fights)")
        
        # Style matchup
        if fighter_a.style != fighter_b.style:
            factors.append("Style clash")
        
        # Weight class
        if fight.weight_class:
            factors.append(f"{fight.weight_class} division dynamics")
        
        return factors
    
    def _predict_method(self, fighter_a: Fighter, fighter_b: Fighter) -> str:
        """Predict most likely method of victory"""
        methods = ["Decision", "KO/TKO", "Submission"]
        weights = [0.4, 0.35, 0.25]  # Base weights
        
        # Adjust based on fighter styles
        if fighter_a.style and "Striker" in fighter_a.style:
            weights[1] += 0.1  # Increase KO probability
        if fighter_a.style and "Grappler" in fighter_a.style:
            weights[2] += 0.1  # Increase submission probability
        
        return random.choices(methods, weights=weights)[0]
    
    def _predict_rounds(self, fighter_a: Fighter, fighter_b: Fighter) -> int:
        """Predict number of rounds the fight will last"""
        # Mock prediction based on fighter styles
        if fighter_a.style and "Striker" in fighter_a.style:
            return random.randint(1, 3)  # Earlier finish
        else:
            return random.randint(2, 5)  # Later finish
    
    def _get_experience_level(self, total_fights: int) -> str:
        """Get experience level based on number of fights"""
        if total_fights < 5:
            return "Novice"
        elif total_fights < 15:
            return "Experienced"
        else:
            return "Veteran"
    
    def _analyze_style_clash(self, fighter_a: Fighter, fighter_b: Fighter) -> str:
        """Analyze style clash between fighters"""
        style_a = fighter_a.style or "Mixed"
        style_b = fighter_b.style or "Mixed"
        
        if style_a != style_b:
            return f"{style_a} vs {style_b} - Different approaches"
        else:
            return f"Both {style_a} - Similar styles"
    
    def _calculate_reach_advantage(self, fighter_a: Fighter, fighter_b: Fighter) -> Dict[str, Any]:
        """Calculate reach advantage"""
        if not fighter_a.reach or not fighter_b.reach:
            return {"advantage": "Unknown", "difference": 0}
        
        diff = fighter_a.reach - fighter_b.reach
        if diff > 2:
            advantage = "Fighter A"
        elif diff < -2:
            advantage = "Fighter B"
        else:
            advantage = "Even"
        
        return {"advantage": advantage, "difference": abs(diff)}
    
    def _calculate_experience_gap(self, fighter_a: Fighter, fighter_b: Fighter) -> Dict[str, Any]:
        """Calculate experience gap between fighters"""
        total_a = fighter_a.record.get("wins", 0) + fighter_a.record.get("losses", 0)
        total_b = fighter_b.record.get("wins", 0) + fighter_b.record.get("losses", 0)
        
        diff = total_a - total_b
        if diff > 5:
            advantage = "Fighter A"
        elif diff < -5:
            advantage = "Fighter B"
        else:
            advantage = "Even"
        
        return {"advantage": advantage, "difference": abs(diff)}
    
    def _calculate_momentum(self, fighter_a: Fighter, fighter_b: Fighter) -> str:
        """Calculate momentum factor"""
        # Mock momentum calculation
        return random.choice(["Fighter A on streak", "Fighter B on streak", "Both inconsistent"])
    
    def _find_similar_opponents(self, fighter_a: Fighter, fighter_b: Fighter) -> List[str]:
        """Find similar opponents between fighters"""
        return ["Common opponent 1", "Common opponent 2"]
    
    def _find_common_opponents(self, fighter_a: Fighter, fighter_b: Fighter) -> List[str]:
        """Find common opponents between fighters"""
        return ["Shared opponent 1", "Shared opponent 2"]
    
    def _analyze_style_performance(self, fighter_a: Fighter, fighter_b: Fighter) -> Dict[str, Any]:
        """Analyze performance against specific styles"""
        return {
            "fighter_a_vs_style": "Good record",
            "fighter_b_vs_style": "Mixed results"
        }
    
    def _identify_value_pick(self, fighter_a: Fighter, fighter_b: Fighter, fight: Fight) -> str:
        """Identify value pick based on odds"""
        return random.choice(["Fighter A", "Fighter B", "No clear value"])
    
    def _assess_risk_level(self, fighter_a: Fighter, fighter_b: Fighter) -> str:
        """Assess risk level of the fight"""
        return random.choice(["Low", "Medium", "High"])
    
    def _suggest_prop_bets(self, fighter_a: Fighter, fighter_b: Fighter) -> List[str]:
        """Suggest prop bet opportunities"""
        return ["Fight goes the distance", "Fight ends in round 2", "Decision victory"]
    
    def _identify_risk_factors(self, fighter_a: Fighter, fighter_b: Fighter, fight: Fight) -> List[str]:
        """Identify risk factors for the fight"""
        factors = []
        
        if fighter_a.record.get("losses", 0) > 5:
            factors.append("Fighter A has multiple losses")
        if fighter_b.record.get("losses", 0) > 5:
            factors.append("Fighter B has multiple losses")
        
        if not fighter_a.style or not fighter_b.style:
            factors.append("Limited style information")
        
        return factors
    
    def _determine_style_advantage(self, style_a: str, style_b: str) -> str:
        """Determine which style has advantage"""
        if "Striker" in style_a and "Grappler" in style_b:
            return "Striker advantage"
        elif "Grappler" in style_a and "Striker" in style_b:
            return "Grappler advantage"
        else:
            return "Even matchup" 