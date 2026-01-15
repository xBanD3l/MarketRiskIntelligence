"""
Module: risk_scoring.py
Description: Calculates composite risk scores for market events based on magnitude and uncertainty.
"""

def calculate_risk_score(category, text):
    """
    Calculates a risk score based on category and headline text.
    
    Formula: Risk Score = (Severity + Uncertainty) * Scope
    
    Args:
        category (str): The event category (e.g., 'Macro', 'Earnings').
        text (str): The headline text.

    Returns:
        tuple: (int, str) - The calculated score and a justification string.
    """
    text = text.lower()
    
    # Default values for score components
    severity = 1
    uncertainty = 3 
    scope = 1
    
    justification = []

    # 1. Base Severity by Category
    category_severity = {
        'Earnings': 3,
        'Regulation / Legal': 4,
        'Macro': 5,
        'Leadership': 3,
        'Speculative / Hype': 2,
        'Other': 1
    }
    severity = category_severity.get(category, 1)
    justification.append(f"Base severity for {category} is {severity}.")

    # 2. Refine Severity based on critical keywords
    critical_keywords = [
        'record', 'crash', 'surge', 'unprecedented', 
        'historic', 'antitrust', 'war', 'recession'
    ]
    if any(kw in text for kw in critical_keywords):
        severity = min(5, severity + 1)
        justification.append("Severity increased due to critical keyword match.")

    # 3. Determine Uncertainty
    # 5 = High Uncertainty (Rumor), 1 = Low Uncertainty (Fact)
    if any(kw in text for kw in ['rumor', 'speculation', 'potentially', 'could', 'may']):
        uncertainty = 5
        justification.append("High uncertainty (5) due to speculative language.")
    elif any(kw in text for kw in ['reports', 'announces', 'confirmed', 'official']):
        uncertainty = 1
        justification.append("Low uncertainty (1) due to confirmed report.")
    else:
        uncertainty = 3
        justification.append("Moderate uncertainty (3) assigned by default.")

    # 4. Determine Scope
    # 5 = Market/Macro, 3 = Sector, 1 = Company
    if category == 'Macro' or any(kw in text for kw in ['global', 'market', 'economy', 'fed']):
        scope = 5
        justification.append("Market-wide scope (5).")
    elif any(kw in text for kw in ['ai', 'tech', 'banking', 'crypto', 'retail']):
        scope = 3
        justification.append("Sector-specific scope (3).")
    else:
        scope = 1
        justification.append("Individual/Company scope (1).")

    # Composite Calculation
    risk_score = (severity + uncertainty) * scope
    
    reasoning = " ".join(justification)
    return risk_score, reasoning

if __name__ == "__main__":
    # Internal module testing
    headline = "The Federal Reserve signals more interest rate hikes to combat inflation."
    score, reason = calculate_risk_score("Macro", headline)
    print(f"Headline: {headline}")
    print(f"Risk Score: {score}")
    print(f"Reasoning: {reason}")
