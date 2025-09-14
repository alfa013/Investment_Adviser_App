# Investment advisor App

### Problem :
There is an investor who has portfolio of investments and he requires an interface where he can monitor and take decisions for his portfolio's best interest. For instance he has 1stock of company 'A', he wants to make sure when is the best time to sell, buy, hold the stock for profits. He also wants to get the latest data and news related to his stock.

### Solution :
I will make a python app which uses yfinance and newsapi to gather data about stocks and bonds and then using AI and ML algorithms will try to give best prediction and analysis of the overall stock nature. I will give report of investment and it's future pathway.


It operates on a three-tier model: a Presentation Layer (UI), a Logic Layer (Backend Processing), and a Data Layer (External APIs).

### I. System Architecture: A Modular, Three-Tier Design

The entire application is architected to separate distinct functionalities into different files (modules). This is a core principle of good software engineering known as "Separation of Concerns."

**Tier 1: Presentation Layer (`main_app.py`)**
* **Technology:** Streamlit
* **Responsibility:** This is the user-facing component. Its sole job is to render the web interface, capture user inputs (stock ticker, risk tolerance, API key), and display the final results in a structured and visually appealing way. It acts as the orchestrator, calling functions from the backend modules and passing data between them, but it contains no core analytical or data-fetching logic itself.

**Tier 2: Logic Layer (`analyzer.py`, `adviser.py`)**
This is the "brain" of the application where all processing and decision-making occurs.
* **`analyzer.py` (The Signal Processor):**
    * **Technologies:** Pandas, NLTK
    * **Responsibility:** To transform raw data into meaningful, machine-readable signals. It takes historical price data and news articles and applies specific algorithms to extract insights. It calculates technical indicators and quantifies news sentiment, effectively converting unstructured information into structured signals for the decision engine.
* **`adviser.py` (The Decision Engine):**
    * **Technology:** Python (Core Logic)
    * **Responsibility:** This module functions as a rules-based expert system. It receives the processed signals from the `analyzer` and the user's risk profile from the UI. It then applies a predefined set of rules to synthesize this information into a final, human-readable recommendation ("Buy," "Sell," "Hold") and a corresponding explanation.

**Tier 3: Data Layer (`data_fetcher.py`)**
* **Technologies:** `yfinance`, `requests` library
* **Responsibility:** This module is the application's gateway to the outside world. It is solely responsible for all communication with external services. It handles the API calls to Yahoo Finance (for stock data) and NewsAPI (for news), manages potential errors during these calls, and implements caching to optimize performance and minimize redundant requests.

### II. Data Flow and Processing Pipeline

The technical execution follows a precise, sequential pipeline from user input to final output:

1.  **Initiation:** The user enters a ticker (e.g., "TSLA") into the Streamlit UI (`main_app.py`) and clicks "Analyze."
2.  **Data Fetching:** `main_app.py` calls functions in `data_fetcher.py`.
    * `get_stock_data("TSLA")` is executed. It makes an API call to Yahoo Finance, retrieves historical price data and company info, and returns them as a Pandas DataFrame and a dictionary.
    * `get_news_data("TSLA", api_key)` is executed, making an API call to NewsAPI and returning a list of article dictionaries.
    * **Performance Optimization:** Both functions are decorated with `@st.cache_data`. If the same ticker is requested again within a short time, the data is served from a local cache instead of making a new API call, drastically improving speed.
3.  **Signal Generation:** The raw data is passed to `analyzer.py`.
    * `calculate_technical_indicators()` receives the price DataFrame and calculates the 50-day and 200-day Simple Moving Averages (SMAs).
    * `analyze_sentiment()` receives the list of news articles and uses the NLTK VADER model to compute an average sentiment score.
4.  **Decision Synthesis:** The generated signals are passed to `adviser.py`.
    * `generate_advice()` receives the SMA data, the sentiment score, and the user's risk tolerance. It evaluates its internal rule-set to determine the final advice and justification.
5.  **Result Display:** The final advice, explanation, and processed data (like the chart with SMAs) are returned to `main_app.py`, which then updates the UI to display the complete analysis to the user.

### III. Core Technical Algorithms

**1. Technical Analysis: Simple Moving Average (SMA) Crossover**
The system uses the relationship between a short-term and a long-term trend indicator to identify market momentum.
* **Implementation:** The code uses the `.rolling(window=X).mean()` method from the Pandas library on the 'Close' price column of the stock's historical data.
* **The "Golden Cross" Signal (Bullish 🐂):** This occurs when the 50-day SMA crosses *above* the 200-day SMA. The code detects this by checking the most recent data point: `if latest_sma_50 > latest_sma_200 and previous_sma_50 <= previous_sma_200`. This condition confirms a recent upward crossover, signaling positive long-term momentum.
* **The "Death Cross" Signal (Bearish 🐻):** This is the inverse, where the 50-day SMA crosses *below* the 200-day SMA. It signals potential long-term decline.

**2. Sentiment Analysis: NLTK VADER**
VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool.
* **Why VADER?** It is specifically tuned for analyzing texts from social media and news headlines, which are often short and contain emotionally charged language. It doesn't require a complex machine learning model to be trained.
* **Implementation:**
    1.  An instance of `SentimentIntensityAnalyzer()` is created.
    2.  For each news headline, the `polarity_scores()` method is called.
    3.  This method returns a dictionary with scores, but we primarily use the `compound` score. This is a single, normalized metric from -1 (most negative) to +1 (most positive).
    4.  The system averages the `compound` scores of all recent articles to produce a single, overarching sentiment signal. A score > 0.05 is considered positive, < -0.05 is negative, and in between is neutral.
