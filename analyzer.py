import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# --- NLTK Setup ---
def initialize_nltk():
    """Download the VADER lexicon if it's not already present."""
    try:
        # This will raise a LookupError if the resource is not found
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        # Catch the more general LookupError
        print("Downloading VADER lexicon for sentiment analysis...")
        nltk.download('vader_lexicon')

# Initialize NLTK right away
initialize_nltk()

def calculate_technical_indicators(hist_df):
    """
    Calculates technical indicators (SMA 50, SMA 200) for a stock.

    Args:
        hist_df (pd.DataFrame): DataFrame with historical stock data.

    Returns:
        pd.DataFrame: The original DataFrame with added columns for indicators.
    """
    if hist_df is None or len(hist_df) < 200:
        return None # Not enough data for 200-day SMA

    df = hist_df.copy()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    return df

def analyze_sentiment(articles):
    """
    Performs sentiment analysis on a list of news articles.

    Args:
        articles (list): A list of news article dictionaries.

    Returns:
        float: The average compound sentiment score, ranging from -1 (very negative) to 1 (very positive).
    """
    if not articles:
        return 0.0

    sid = SentimentIntensityAnalyzer()
    sentiment_scores = [
        sid.polarity_scores(article['title'])['compound']
        for article in articles if article and article['title']
    ]
    
    return np.mean(sentiment_scores) if sentiment_scores else 0.0

