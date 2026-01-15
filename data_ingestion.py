"""
Module: data_ingestion.py
Description: Handles fetching of financial news headlines from external APIs.
"""

import os
from datetime import datetime
import pandas as pd
import requests

def fetch_news(api_key='99bb391f582543129b44687a48665d62', query='finance'):
    """
    Fetches financial news headlines using NewsAPI.

    Args:
        api_key (str): The NewsAPI key. If 'MOCK', returns sample data.
        query (str): The search query for news articles.

    Returns:
        pd.DataFrame: A DataFrame containing source, text, date, and type of news articles.
    """
    if api_key == 'MOCK':
        return pd.DataFrame([
            {
                'source': 'Reuters', 
                'text': 'Global markets rally on inflation data.', 
                'date': datetime.now().strftime('%Y-%m-%d'), 
                'type': 'news'
            },
            {
                'source': 'Bloomberg', 
                'text': 'Central banks signal potential rate cuts.', 
                'date': datetime.now().strftime('%Y-%m-%d'), 
                'type': 'news'
            }
        ])

    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        news_list = []
        for article in articles:
            news_list.append({
                'source': article['source']['name'],
                'text': article['title'] + ". " + (article['description'] if article['description'] else ""),
                'date': article['publishedAt'],
                'type': 'news'
            })
        return pd.DataFrame(news_list)
    except requests.exceptions.RequestException:
        return pd.DataFrame()

def combine_and_save_data(df, output_path='raw_market_data.csv'):
    """
    Saves the processed news data to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_path (str): The path to the output CSV file.

    Returns:
        pd.DataFrame: The input DataFrame.
    """
    if not df.empty:
        df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    # Internal module testing
    NEWS_API_KEY = '99bb391f582543129b44687a48665d62'
    
    news_data = fetch_news(NEWS_API_KEY)
    if not news_data.empty:
        combine_and_save_data(news_data)
        print(f"Sample Ingestion Complete: {len(news_data)} articles fetched.")
