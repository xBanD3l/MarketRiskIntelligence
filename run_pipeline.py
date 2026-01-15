"""
Script: run_pipeline.py
Description: A standalone utility to run the full data processing pipeline and generate processed_market_data.csv.
"""

import os
from dotenv import load_dotenv
from data_ingestion import fetch_news
from event_detection import classify_event
from risk_scoring import calculate_risk_score
from sentiment_analysis import process_sentiment
from explanation import generate_explanation

# Load environment variables
load_dotenv()

def run_pipeline(api_key=None):
    """
    Executes the ingestion, analysis, and explanation generation pipeline.
    
    Args:
        api_key (str, optional): The NewsAPI key to use. If None, uses environment variable.
    """
    if api_key is None:
        api_key = os.getenv('NEWS_API_KEY', '99bb391f582543129b44687a48665d62')

    print("Starting full Market Risk Intelligence pipeline...")
    
    # 1. Data Ingestion
    df = fetch_news(api_key)
    
    if df.empty:
        print("Pipeline aborted: News ingestion failed.")
        return

    # 2. Sequential Analysis
    print("Classifying events...")
    df['category'] = df['text'].apply(classify_event)
    
    print("Calculating risk scores...")
    risk_results = df.apply(
        lambda row: calculate_risk_score(row['category'], row['text']), 
        axis=1
    )
    df['risk_score'] = [r[0] for r in risk_results]
    df['risk_reason'] = [r[1] for r in risk_results]
    
    print("Analyzing sentiment and hype...")
    df = process_sentiment(df)
    
    # 3. Intelligence Summary Generation
    print("Generating AI intelligence summaries...")
    df['intelligence_summary'] = df.apply(
        lambda row: generate_explanation(
            row['category'], 
            row['risk_score'], 
            row['sentiment'], 
            row['speculative_flag']
        ), axis=1
    )
    
    # 4. Data Persistence
    df.to_csv('processed_market_data.csv', index=False)
    print("Pipeline complete. Output saved to 'processed_market_data.csv'.")
    print("\nData Snapshot:")
    print(df[['category', 'risk_score', 'speculative_flag']].head())

if __name__ == "__main__":
    run_pipeline()
