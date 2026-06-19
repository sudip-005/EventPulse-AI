from typing import Dict, Any

class RiskService:
    @staticmethod
    def calculate_risk_score(impact_score: float, duration_minutes: float, closure_probability: float) -> float:
        """
        Calculates a risk score from 0 to 100 based on impact, duration, and road closure probability.
        """
        # Duration factor: scaled up to 30 points (max impact reached at 12 hours / 720 minutes)
        duration_factor = min(duration_minutes / 720.0, 1.0) * 30.0
        
        # Impact factor: scaled up to 40 points
        impact_factor = (impact_score / 100.0) * 40.0
        
        # Closure probability factor: scaled up to 30 points
        closure_factor = closure_probability * 30.0
        
        total_risk = impact_factor + duration_factor + closure_factor
        return min(max(total_risk, 0.0), 100.0)


    @staticmethod
    def determine_risk_level(risk_score: float) -> str:
        """
        Determines the risk level (LOW, MEDIUM, HIGH, CRITICAL) from a risk score.
        """
        if risk_score < 30.0:
            return "LOW"
        elif risk_score < 60.0:
            return "MEDIUM"
        elif risk_score < 85.0:
            return "HIGH"
        else:
            return "CRITICAL"

    @staticmethod
    def calculate_priority(risk_score: float, closure_probability: float) -> int:
        """
        Determines event response priority from 1 (lowest) to 5 (highest).
        """
        if risk_score >= 85.0 or closure_probability >= 0.9:
            return 5
        elif risk_score >= 60.0 or closure_probability >= 0.5:
            return 4
        elif risk_score >= 40.0:
            return 3
        elif risk_score >= 20.0:
            return 2
        else:
            return 1

    @staticmethod
    def build_assessment(impact_score: float, duration_minutes: float, closure_probability: float) -> Dict[str, Any]:
        """
        Builds a complete risk assessment dictionary.
        """
        risk_score = RiskService.calculate_risk_score(impact_score, duration_minutes, closure_probability)
        risk_level = RiskService.determine_risk_level(risk_score)
        priority = RiskService.calculate_priority(risk_score, closure_probability)
        
        return {
            "impact_score": impact_score,
            "expected_duration_minutes": duration_minutes,
            "closure_probability": closure_probability,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "priority": priority
        }