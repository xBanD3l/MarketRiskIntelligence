"""
Module: sentiment_analysis.py
Description: Performs sentiment analysis on market news to detect speculative hype and bubble signals.
"""

import nltk
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize analyzer once at module level for efficiency
_SIA = SentimentIntensityAnalyzer()

def get_sentiment_score(text):
    """
    Analyzes the sentiment of a given text.

    Args:
        text (str): The news headline or description.

    Returns:
        float: Compound sentiment score ranging from -1.0 to 1.0.
    """
    return _SIA.polarity_scores(text)['compound']

def analyze_speculative_risk(sentiment_score, risk_score):
    """
    Determines if an event represents a speculative risk.
    Logic: Highly positive sentiment (hype) combined with high quantified risk.

    Args:
        sentiment_score (float): The sentiment score.
        risk_score (float): The calculated risk score.

    Returns:
        bool: True if identified as a speculative signal.
    """
    # Thresholds: very positive sentiment (> 0.5) AND high risk magnitude (> 30)
    return sentiment_score > 0.5 and risk_score > 30

def process_sentiment(df):
    """
    Augments a DataFrame with sentiment scores and speculative risk flags.

    Args:
        df (pd.DataFrame): DataFrame containing at least a 'text' column.

    Returns:
        pd.DataFrame: The enriched DataFrame.
    """
    df['sentiment'] = df['text'].apply(get_sentiment_score)
    
    if 'risk_score' in df.columns:
        df['speculative_flag'] = df.apply(
            lambda row: analyze_speculative_risk(row['sentiment'], row['risk_score']), 
            axis=1
        )
    else:
        df['speculative_flag'] = False
        
    return df

if __name__ == "__main__":
    # Internal module verification
    sample_text = "Market surges to all-time highs as rumors of infinite growth spread!"
    sentiment = get_sentiment_score(sample_text)
    is_speculative = analyze_speculative_risk(sentiment, 45)
    print(f"Text: {sample_text}")
    print(f"Sentiment: {sentiment} | Speculative Risk: {is_speculative}")
