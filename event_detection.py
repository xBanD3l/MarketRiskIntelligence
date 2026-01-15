"""
Module: event_detection.py
Description: Classifies financial headlines into predefined categories using regex.
"""

import re

def classify_event(text):
    """
    Classifies a text into a specific event category based on keyword rules.

    Args:
        text (str): The headline or text to classify.

    Returns:
        str: The detected category ('Earnings', 'Macro', 'Leadership', etc.).
    """
    text = text.lower()
    
    # Define category keyword mappings using regex patterns
    categories = {
        'Earnings': [
            r'\bearnings\b', r'\bq[1-4]\b', r'\brevenue\b', r'\bprofit\b', 
            r'\bdividend\b', r'\bfiscal\b', r'\beat\b', r'\bmiss\b'
        ],
        'Regulation / Legal': [
            r'\blawsuit\b', r'\bsue\b', r'\bsued\b', r'\bcourt\b', 
            r'\bregulation\b', r'\bsec\b', r'\bantitrust\b', r'\bfine\b', 
            r'\bcompliance\b', r'\blegal\b', r'\bprosecutor\b'
        ],
        'Macro': [
            r'\binflation\b', r'\bfed\b', r'\binterest rate\b', r'\bwar\b', 
            r'\bgeopolitical\b', r'\bgdp\b', r'\bcpi\b', r'\bcentral bank\b', 
            r'\beconomy\b', r'\brecession\b'
        ],
        'Leadership': [
            r'\bceo\b', r'\bcfo\b', r'\bboard\b', r'\bmanagement\b', 
            r'\bchairman\b', r'\bappointment\b', r'\bresignation\b', 
            r'\bhire\b', r'\bfire\b', r'\bexecutive\b'
        ],
        'Speculative / Hype': [
            r'\brumor\b', r'\bspeculation\b', r'\bspeculative\b', r'\bpotentially\b', 
            r'\bmeme\b', r'\bhype\b', r'\bto the moon\b', r'\bvolatile\b', 
            r'\bcrypto\b', r'\bmerger\b', r'\bacquisition\b'
        ]
    }
    
    for category, patterns in categories.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return category
                
    return 'Other'

if __name__ == "__main__":
    # Test cases for internal verification
    test_headlines = [
        "Apple reports record Q3 earnings and revenue beat.",
        "The Federal Reserve signals more interest rate hikes to combat inflation.",
        "SEC sues major crypto exchange over compliance failures.",
        "New CEO appointed at Microsoft to lead AI strategy."
    ]
    
    for headline in test_headlines:
        cat = classify_event(headline)
        print(f"[{cat}] {headline}")
