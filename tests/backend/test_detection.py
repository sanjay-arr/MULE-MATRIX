import pytest
import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.detection.rule_engine import RuleEngine
from backend.app.detection.risk_scoring import calculate_risk
from backend.app.detection.explainability import generate_explanation

def test_rule_rapid_fund_movement():
    engine = RuleEngine()
    features = {"rapid_transfer_ratio": 0.8}
    res = engine.rule_rapid_fund_movement(features)
    assert res is not None
    assert res['triggered'] is True
    assert res['rule'] == "RAPID_FUND_MOVEMENT"

def test_rule_high_pass_through():
    engine = RuleEngine()
    features = {"pass_through_ratio": 0.95, "total_received": 5000}
    res = engine.rule_high_pass_through(features)
    assert res is not None
    assert res['triggered'] is True
    
    # Shouldn't trigger if received amount is tiny (noise)
    features_noise = {"pass_through_ratio": 0.95, "total_received": 100}
    assert engine.rule_high_pass_through(features_noise) is None

def test_rule_many_counterparties():
    engine = RuleEngine()
    assert engine.rule_many_counterparties({"unique_counterparties": 15}) is not None
    assert engine.rule_many_counterparties({"unique_counterparties": 5}) is None

def test_risk_scoring_capping():
    rules = [
        {"rule": "R1", "contribution": 40},
        {"rule": "R2", "contribution": 40},
        {"rule": "R3", "contribution": 40}
    ]
    score, level, breakdown = calculate_risk(rules)
    assert score == 100 # Should be capped
    assert level == "CRITICAL"

def test_risk_scoring_levels():
    score, level, _ = calculate_risk([{"rule": "R1", "contribution": 20}])
    assert level == "LOW"
    assert score == 20
    
    score, level, _ = calculate_risk([{"rule": "R1", "contribution": 45}])
    assert level == "MEDIUM"

def test_explainability():
    rules = [
        {"rule": "R1", "contribution": 40, "explanation": "Test explanation 1."},
        {"rule": "R2", "contribution": 40, "explanation": "Test explanation 2."}
    ]
    exp = generate_explanation(rules)
    assert "WHY FLAGGED?" in exp
    assert "Test explanation 1." in exp
    assert "Test explanation 2." in exp

def test_normal_account_no_rules_triggered():
    engine = RuleEngine()
    features = {
        "pass_through_ratio": 0.1,
        "rapid_transfer_ratio": 0.0,
        "unique_counterparties": 2,
        "unique_banks_involved": 1,
        "fan_in_count": 1,
        "fan_out_count": 1,
        "off_ramp_connection_count": 0,
        "burst_count": 0,
        "total_received": 1000
    }
    triggered = engine.evaluate(features)
    assert len(triggered) == 0
