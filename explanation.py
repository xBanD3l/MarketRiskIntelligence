"""
Module: explanation.py
Description: Generates natural language summaries and actionable intelligence for market events.
"""

def generate_explanation(category, risk_score, sentiment, speculative_flag):
    """
    Generates a structured risk intelligence explanation for a market event.

    Args:
        category (str): The event category.
        risk_score (float): The quantified risk score.
        sentiment (float): The sentiment score.
        speculative_flag (bool): Whether speculative risk was detected.

    Returns:
        str: A human-readable summary of the risk situation.
    """
    # 1. Determine Risk Level
    if risk_score > 30:
        risk_level = "High"
    elif risk_score > 10:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # 2. Identify Primary Drivers
    drivers = []
    driver_map = {
        "Macro": "Macroeconomic conditions",
        "Regulation / Legal": "Regulatory pressure",
        "Earnings": "Financial performance results",
        "Leadership": "Corporate governance shift"
    }
    if category in driver_map:
        drivers.append(driver_map[category])
    
    if risk_score > 40:
        drivers.append("Unprecedented market scale")

    # 3. Speculative Signals
    spec_signal = "None detected."
    if speculative_flag:
        spec_signal = "Elevated hype (High positive sentiment vs High risk)."
    elif "Speculative" in category:
        spec_signal = "Inherent category speculation."

    # 4. Suggested Stance
    if risk_level == "High":
        stance = "Reduce exposure" if sentiment < -0.5 else "Hold with caution"
    elif risk_level == "Medium":
        stance = "Neutral / Observe"
    else:
        stance = "Hold / Maintain"

    # 5. Confidence Level
    if "Speculative" in category or risk_score > 50:
        confidence = "Low"
    elif risk_score < 20:
        confidence = "High"
    else:
        confidence = "Medium"

    return (
        f"Risk Level: {risk_level}. "
        f"Drivers: {', '.join(drivers) if drivers else 'Other factors'}. "
        f"Speculative signal: {spec_signal} "
        f"Suggested stance: {stance}. "
        f"Confidence level: {confidence}."
    )

if __name__ == "__main__":
    # Internal module verification
    result = generate_explanation("Macro", 42, 0.1, False)
    print(f"Generated Explanation:\n{result}")
