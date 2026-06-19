import pytest
import numpy as np
from app.ml.inference import XGBoostInference
from app.ml.features import FeatureEngineer

def test_inference_fallback():
    inference = XGBoostInference()
    
    # Generate dummy features
    event = {"event_type": "concert", "priority": "High", "estimated_attendance": 12000, "requires_road_closure": True}
    weather = {"temperature": 28.0, "precipitation": 0.0}
    import datetime
    t = datetime.datetime.now()
    features = FeatureEngineer.build_feature_vector(event, weather, t)
    
    # Test predict_impact
    score, level = inference.predict_impact(features)
    assert isinstance(score, (float, np.floating, int))
    assert level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # Test predict_duration
    duration = inference.predict_duration(features)
    assert isinstance(duration, (float, np.floating, int))
    assert duration >= 0.0
    
    # Test predict_event_risk
    risk_assessment = inference.predict_event_risk(features)
    assert "risk_score" in risk_assessment
    assert "risk_level" in risk_assessment
    assert "priority" in risk_assessment
    assert "top_factors" in risk_assessment
    assert len(risk_assessment["top_factors"]) == 3
