import yfinance as yf
import requests
import streamlit as st

@st.cache_data(show_spinner="Fetching stock data...")
def get_stock_data(ticker, period="1y"):
    """
    Fetches historical stock data and company information from Yahoo Finance.
    
    Args:
        ticker (str): The stock ticker symbol.
        period (str): The time period for historical data (e.g., "1y", "6mo").

    Returns:
        tuple: A tuple containing the stock's info dictionary and a DataFrame of historical data.
               Returns (None, None) if the ticker is invalid or data cannot be fetched.
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch info dictionary first to check if the ticker is valid
        info = stock.info
        if not info or info.get('trailingPE') is None: # A simple check for valid ticker data
             st.error(f"No data found for ticker '{ticker}'. It might be delisted or an incorrect symbol.")
             return None, None
             
        hist = stock.history(period=period)
        if hist.empty:
            st.error(f"No historical data found for ticker '{ticker}'.")
            return None, None
            
        # Return the info dictionary directly, which is serializable
        return info, hist
    except Exception as e:
        st.error(f"Error fetching stock data for {ticker}: {e}")
        return None, None

@st.cache_data(show_spinner="Fetching latest news...")
def get_news_data(ticker, api_key):
    """
    Fetches news articles related to a stock ticker from NewsAPI.

    Args:
        ticker (str): The stock ticker symbol to search for in news.
        api_key (str): Your personal NewsAPI key.

    Returns:
        list: A list of news articles, or an empty list if an error occurs.
    """
    if not api_key or api_key == "YOUR_API_KEY":
        st.warning("NewsAPI key not provided. News analysis will be skipped.")
        return []
    try:
        url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}&language=en&sortBy=publishedAt&pageSize=20'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        articles = response.json().get('articles', [])
        return articles
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch news. Please check your NewsAPI key. Error: {e}")
        return []

