# Investment advisor App

### Problem :
There is an investor who has portfolio of investments and he requires an interface where he can monitor and take decisions for his portfolio's best interest. For instance he has 1stock of company 'A', he wants to make sure when is the best time to sell, buy, hold the stock for profits. He also wants to get the latest data and news related to his stock.

### Solution :
I will make a python app which uses yfinance and newsapi to gather data about stocks and bonds and then using AI and ML algorithms will try to give best prediction and analysis of the overall stock nature. I will give report of investment and it's future pathway.

Of course. Here is an in-depth explanation of the AI Investment Adviser project, from its high-level introduction to its core components and overall system design.

---

#### **1. Introduction: The Core Problem and Vision**

In the modern financial world, the primary challenge for an investor is not a lack of information, but an overwhelming surplus of it. Stock prices, economic reports, company news, and market sentiment create a constant stream of complex, often contradictory data. The vision for the AI Investment Adviser is to create a sophisticated yet intuitive tool that acts as a personal AI analyst for the everyday investor.

The application is designed to cut through the noise by performing four key tasks:
1.  **Aggregate:** Gather all relevant quantitative (price, volume) and qualitative (news) data in real-time.
2.  **Analyze:** Process this data using established financial indicators and advanced sentiment analysis algorithms.
3.  **Synthesize:** Combine these analytical signals into a coherent, holistic view of the stock.
4.  **Advise:** Present a clear, actionable recommendation and a detailed narrative report, personalized to the user's individual risk tolerance.

It aims to democratize sophisticated financial analysis, making it accessible not just to professional traders, but to anyone looking to make informed decisions about their investments.

---

#### **2. Overall Design: A Modular Three-Tier Architecture**

The project is built upon a professional, multi-file **Three-Tier Architecture**. This design philosophy is crucial for creating an application that is scalable, maintainable, and robust. It separates the application's core responsibilities into distinct, independent layers.



* **Tier 1: Presentation Layer (`main_app.py`):** This is the user-facing front-end. It is responsible for everything the user sees and interacts with—the UI, charts, and navigation. It knows *how* to display information but has no knowledge of *where* the data comes from or *how* it's analyzed.
* **Tier 2: Logic Layer (`analyzer.py`, `adviser.py`):** This is the application's "brain." It contains all the business logic, algorithms, and decision-making processes. It takes raw data from the data layer and transforms it into insights and advice.
* **Tier 3: Data Layer (`data_fetcher.py`):** This layer is the application's sole gateway to the outside world. Its only responsibility is to communicate with external APIs to fetch the raw data needed for analysis.

This separation ensures that a change in one layer—like updating the UI or switching to a new data provider—has minimal impact on the other layers.

---

#### **3. Component Deep Dive**

Each Python file in the project has a clearly defined role within this architecture.

##### **a) `main_app.py` - The Conductor & UI**
* **Purpose:** To manage the user experience and orchestrate the flow of data between the other modules.
* **Key Technologies:** `Streamlit` for the web framework, `Plotly` for interactive data visualization, and custom injected `CSS` for professional styling.
* **Core Logic:**
    * **UI Rendering:** It contains all the `st.` commands that draw the sidebar, input widgets, cards, and multi-page navigation. The extensive CSS block defines the professional aesthetic, from the color palette and fonts (`Poppins`) to the card shadows and button gradients.
    * **State Management:** It uses `st.session_state` to intelligently store the results of an analysis. This allows the user to navigate between the "Dashboard" and "Detailed AI Report" pages without losing data or needing to re-run the analysis.
    * **Orchestration:** When the "Analyze" button is clicked, this file executes the main logic pipeline: it calls `data_fetcher` to get data, passes that data to `analyzer` for processing, sends the results to `adviser` for a recommendation, and finally displays all the returned information in the appropriate UI components.

##### **b) `data_fetcher.py` - The Data Librarian**
* **Purpose:** To reliably fetch stock and news data from external services.
* **Key Technologies:** `yfinance` library for Yahoo Finance market data, and the `requests` library for making HTTP calls to the `NewsAPI`.
* **Core Logic:**
    * **`get_stock_data()`:** Takes a ticker symbol, creates a `yfinance.Ticker` object, and extracts two key pieces of information: the company's information dictionary (`.info`) and its historical price data (`.history()`).
    * **`get_news_data()`:** Takes a ticker and an API key, constructs the correct URL for the NewsAPI, and retrieves a list of recent news articles.
    * **Efficiency:** Both functions are decorated with `@st.cache_data`, a powerful Streamlit feature that prevents redundant API calls. If the same stock is analyzed again, the data is served from a local cache, making the app faster and reducing API usage.

##### **c) `analyzer.py` - The Technical Scientist**
* **Purpose:** To convert raw data into structured, analytical signals.
* **Key Technologies:** `pandas` for data manipulation, `ta` library for calculating a wide range of technical indicators, and `NLTK (VADER)` for sentiment analysis.
* **Core Logic:**
    * **`calculate_technical_indicators()`:** This function is the workhorse of the quantitative analysis. It takes the historical price DataFrame and calculates:
        * **Moving Averages (SMA & EMA):** 50-period and 200-period averages to identify long-term trends.
        * **Relative Strength Index (RSI):** A momentum oscillator to measure the speed and change of price movements, helping to identify overbought (>70) or oversold (<30) conditions.
        * **MACD (Moving Average Convergence Divergence):** A trend-following momentum indicator that shows the relationship between two EMAs, helping to spot changes in momentum.
    * **`analyze_sentiment()`:** This function performs the qualitative analysis. It iterates through news headlines and uses NLTK's VADER model to assign a `compound` sentiment score to each. It then averages these scores to produce a single, overall sentiment metric.

##### **d) `adviser.py` - The AI Strategist**
* **Purpose:** To synthesize all analytical signals and generate the final investment advice.
* **Key Technologies:** Google's `generative-ai` library.
* **Core Logic:**
    * **`generate_advice()`:** A simple, rules-based function that provides a quick, high-level recommendation ("Buy", "Sell", "Hold"). It primarily looks at the SMA Golden Cross/Death Cross and the overall sentiment score to make a rapid judgment. This powers the main recommendation card on the dashboard.
    * **`generate_gemini_report()`:** This is the most advanced function. It acts as a "prompt engineer," carefully constructing a detailed prompt for the Gemini AI model. This prompt includes:
        * The stock's key financial metrics.
        * The latest technical indicator values (SMA, RSI, etc.).
        * The overall news sentiment score.
        * Crucially, the user's selected **risk tolerance**.
        It then instructs the AI to act as an expert financial analyst and write a comprehensive report that considers all these factors, resulting in a nuanced and personalized narrative that is far more insightful than a simple rule.
