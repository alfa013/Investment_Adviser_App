import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ta  # Technical Analysis library

def initialize_nltk():
    """
    Downloads the VADER lexicon for sentiment analysis if not already present.
    """
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Downloading NLTK VADER lexicon...")
        nltk.download('vader_lexicon')

# Initialize NLTK resources once when the module is imported
initialize_nltk()

def calculate_technical_indicators(stock_hist_df):
    """
    Calculates technical indicators for the given stock history.

    Args:
        stock_hist_df (pd.DataFrame): DataFrame with historical stock data.

    Returns:
        pd.DataFrame: DataFrame with added technical indicator columns.
    """
    if stock_hist_df.empty:
        return stock_hist_df

    # Add all technical indicators using the 'ta' library
    df_with_indicators = ta.add_all_ta_features(
        stock_hist_df,
        open="Open",
        high="High",
        low="Low",
        close="Close",
        volume="Volume",
        fillna=True  # Fill NaN values that are generated
    )

    # Explicitly calculate 50 and 200 period SMA and EMA for clarity
    df_with_indicators['SMA_50'] = df_with_indicators['Close'].rolling(window=50).mean()
    df_with_indicators['SMA_200'] = df_with_indicators['Close'].rolling(window=200).mean()
    df_with_indicators['EMA_50'] = df_with_indicators['Close'].ewm(span=50, adjust=False).mean()
    df_with_indicators['EMA_200'] = df_with_indicators['Close'].ewm(span=200, adjust=False).mean()


    # Note: 'ta' already calculates the following, which we use in the main app:
    # RSI is calculated as 'momentum_rsi'
    # MACD is calculated as 'trend_macd', 'trend_macd_signal', 'trend_macd_diff'

    return df_with_indicators


def analyze_sentiment(articles):
    """
    Analyzes the sentiment of a list of news articles.

    Args:
        articles (list): A list of article dictionaries.

    Returns:
        float: The average sentiment score of the articles.
    """
    if not articles:
        return 0.0

    sia = SentimentIntensityAnalyzer()
    total_sentiment = 0
    
    for article in articles:
        if article.get('title'):
            sentiment = sia.polarity_scores(article['title'])
            total_sentiment += sentiment['compound']
            
    return total_sentiment / len(articles) if articles else 0.0

