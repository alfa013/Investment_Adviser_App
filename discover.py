# # discover.py

# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import requests # <-- Import the requests library
# from collections import defaultdict

# @st.cache_data(ttl=86400) # Cache the data for 24 hours
# def discover_stocks_yfinance():
#     """
#     Fetches S&P 500 tickers, gets their sector using yfinance, and categorizes them.
#     The result is cached to ensure the app is fast after the first run.

#     Returns:
#         dict: A dictionary where keys are sector names and values are lists of stock data.
#     """
#     try:
#         st.info("Fetching S&P 500 stock list... This may take a moment on the first run.")
#         url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        
#         # --- FIX: ADD USER-AGENT HEADER ---
#         # This makes our request look like it's coming from a browser, avoiding the 403 error.
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         response = requests.get(url, headers=headers)
#         response.raise_for_status() # This will raise an error if the request failed
        
#         # Now we pass the HTML content from our successful request to pandas
#         table = pd.read_html(response.text)
#         # --- END OF FIX ---

#         sp500_df = table[0]
#         tickers = sp500_df['Symbol'].tolist()
        
#     except Exception as e:
#         st.error(f"Failed to fetch S&P 500 list: {e}")
#         # Fallback to a smaller, curated list if the scrape fails
#         tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "JPM", "JNJ", "V", "PG", "UNH", "HD"]
#         st.warning("Using a default list of stocks.")


#     categorized_stocks = defaultdict(list)
#     progress_bar = st.progress(0, text="Analyzing stock sectors...")

#     for i, ticker_str in enumerate(tickers):
#         try:
#             # yfinance can be sensitive to symbols with '.', replace with '-'
#             ticker_symbol = ticker_str.replace('.', '-')
            
#             stock = yf.Ticker(ticker_symbol)
#             info = stock.info

#             # Use 'sector' for broad categorization. Use .get() for safety.
#             sector = info.get('sector', 'Other')
#             long_name = info.get('longName', ticker_symbol) # Use longName for description

#             if sector:
#                 categorized_stocks[sector].append({
#                     'symbol': ticker_symbol,
#                     'description': long_name
#                 })
#         except Exception as e:
#             # Silently skip tickers that yfinance fails on
#             print(f"Could not fetch info for {ticker_symbol}: {e}")
#             continue
        
#         # Update progress bar
#         progress_bar.progress((i + 1) / len(tickers), text=f"Analyzing {ticker_symbol}...")

#     progress_bar.empty()
#     st.success("Discovery data loaded successfully!")
    
#     # Sort the dictionary by sector name
#     return dict(sorted(categorized_stocks.items()))

# discover.py

import streamlit as st
import pandas as pd
import requests
from collections import defaultdict

# NOTE: Ensure lxml is installed: pip install lxml

@st.cache_data(ttl=86400)
def discover_stocks_yfinance():
    """
    Fetches S&P 500 tickers from Wikipedia.
    Robustness: Iterates through all tables to find the one with a 'Symbol' column.
    """
    categorized_stocks = defaultdict(list)
    
    try:
        st.info("Fetching S&P 500 stock list...")
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Fetch ALL tables (do not filter by match text yet)
        tables = pd.read_html(response.text)
        
        sp500_df = None
        
        # Iterate through found tables to find the correct one
        for table in tables:
            # We look for the table that has 'Symbol' in its columns
            if 'Symbol' in table.columns:
                sp500_df = table
                break
        
        if sp500_df is None:
            raise ValueError("Found tables, but none contained a 'Symbol' column.")

        # Iterate through the correct DataFrame
        for index, row in sp500_df.iterrows():
            ticker_symbol = row.get('Symbol')
            company_name = row.get('Security')
            
            # Try to find the sector column (it is usually 'GICS Sector')
            # If not found, default to "Uncategorized"
            sector = row.get('GICS Sector')
            
            if not sector and 'Sector' in row:
                sector = row['Sector']
            
            if not sector:
                sector = "Other"
            
            # Skip rows if Symbol is missing
            if pd.isna(ticker_symbol):
                continue

            # Convert to string and fix formatting (BRK.B -> BRK-B)
            ticker_symbol = str(ticker_symbol).replace('.', '-')
            
            categorized_stocks[sector].append({
                'symbol': ticker_symbol,
                'description': company_name
            })

        st.success("Discovery data loaded successfully!")

    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        # Fallback data
        return {
            "Technology": [{"symbol": "AAPL", "description": "Apple Inc."}, {"symbol": "MSFT", "description": "Microsoft"}],
            "Consumer": [{"symbol": "AMZN", "description": "Amazon.com"}]
        }
    
    return dict(sorted(categorized_stocks.items()))