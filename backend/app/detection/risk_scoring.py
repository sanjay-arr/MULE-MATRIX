def calculate_risk(triggered_rules):
    total_score = 0
    for rule in triggered_rules:
        total_score += rule.get('contribution', 0)
        
    # Cap at 100
    risk_score = min(total_score, 100)
    
    if risk_score <= 30:
        risk_level = "LOW"
    elif risk_score <= 60:
        risk_level = "MEDIUM"
    elif risk_score <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
        
    risk_breakdown = {rule['rule']: rule['contribution'] for rule in triggered_rules}
    
    return risk_score, risk_level, risk_breakdown
