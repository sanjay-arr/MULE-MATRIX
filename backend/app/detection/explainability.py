def generate_explanation(triggered_rules):
    if not triggered_rules:
        return "No suspicious activity detected."
        
    explanation_lines = ["WHY FLAGGED?"]
    for rule in triggered_rules:
        exp = rule.get("explanation", "")
        if exp:
            explanation_lines.append(f"✓ {exp}")
            
    return "\n".join(explanation_lines)
