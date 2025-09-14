import streamlit as st
import pandas as pd

# Import functions from our other files
from data_fetcher import get_stock_data, get_news_data
from analyzer import calculate_technical_indicators, analyze_sentiment
from adviser import generate_advice

# --- Page Configuration and CSS ---
st.set_page_config(
    page_title="AI Investment Adviser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* General App Styling */
.stApp { background-color: #F0F2F6; }
/* Main content area */
.main .block-container { padding: 2rem 5rem; }
/* Card styling */
.card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1); height: 100%; }
/* Metric card styling */
.metric-card { text-align: center; }
.metric-card h4 { color: #4F8BF9; font-size: 1.1rem; margin-bottom: 5px; }
.metric-card p { font-size: 1.5rem; font-weight: bold; margin: 0; }
/* Recommendation card styling */
.recommendation-card { text-align: center; padding: 30px; }
.recommendation-card h2 { font-size: 3rem; margin-bottom: 15px; }
.buy { background-color: #E6F7F0; border: 1px solid #B3E6D3; color: #006A4E; }
.sell { background-color: #FDEDED; border: 1px solid #F5C0C0; color: #A30000; }
.hold { background-color: #FFFBEA; border: 1px solid #FFE58F; color: #D46B08; }
/* News article styling */
.news-article { border-bottom: 1px solid #EAEAEA; padding: 15px 0; }
.news-article:last-child { border-bottom: none; }
.news-title { font-weight: bold; font-size: 1.1rem; color: #333; }
.news-source { color: #666; font-size: 0.9rem; }
/* Custom button */
div.stButton > button:first-child { background-color: #4F8BF9; color: white; border-radius: 5px; height: 3em; width: 100%; font-size: 1rem; font-weight: bold; margin-top: 1rem; }
div.stButton > button:hover { background-color: #3A6DC2; }
</style>
""", unsafe_allow_html=True)


# --- UI Layout ---
with st.sidebar:
    st.markdown("## 📈 AI Investment Adviser")
    st.markdown("---")
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL", help="e.g., AAPL, GOOGL, MSFT").upper()
    risk_tolerance = st.select_slider("Select Your Risk Tolerance", options=["Low", "Medium", "High"], value="Medium")
    news_api_key = st.text_input("Enter NewsAPI Key", type="password", help="Get a free key from newsapi.org")
    analyze_button = st.button("Analyze & Advise")

st.title(f"Analysis for {ticker_input}")
st.markdown("AI-powered insights into your next investment decision.")

if analyze_button:
    if not ticker_input:
        st.warning("Please enter a stock ticker.")
    else:
        # --- LOGIC FLOW ---
        # 1. Data Gathering
        # stock_info is now a dictionary, not a yf.Ticker object
        stock_info, stock_hist = get_stock_data(ticker_input)
        
        if stock_info and stock_hist is not None:
            news_articles = get_news_data(ticker_input, news_api_key)

            # 2. Analysis
            hist_with_indicators = calculate_technical_indicators(stock_hist)
            avg_sentiment = analyze_sentiment(news_articles)
            
            # 3. Advising
            advice, explanation, style_class = generate_advice(hist_with_indicators, avg_sentiment, risk_tolerance)

            # 4. Display Results
            st.markdown("---")
            col1, col2 = st.columns([1.5, 2])
            with col1:
                st.markdown("### Recommendation")
                st.markdown(f'<div class="card recommendation-card {style_class}"><h2>{advice}</h2></div>', unsafe_allow_html=True)
                st.markdown("### Reasoning")
                st.markdown(f'<div class="card"><p>{explanation}</p></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Key Information")
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    # We no longer need ".info" as stock_info is the dictionary
                    info = stock_info
                    c1, c2, c3 = st.columns(3)
                    with c1: st.markdown(f'<div class="metric-card"><h4>Market Cap</h4><p>${info.get("marketCap", 0):,}</p></div>', unsafe_allow_html=True)
                    with c2: st.markdown(f'<div class="metric-card"><h4>P/E Ratio</h4><p>{info.get("trailingPE", 0):.2f}</p></div>', unsafe_allow_html=True)
                    with c3: st.markdown(f'<div class="metric-card"><h4>Beta</h4><p>{info.get("beta", 0):.2f}</p></div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    c4, c5, c6 = st.columns(3)
                    with c4: st.markdown(f'<div class="metric-card"><h4>52-Wk High</h4><p>${info.get("fiftyTwoWeekHigh", 0):.2f}</p></div>', unsafe_allow_html=True)
                    with c5: st.markdown(f'<div class="metric-card"><h4>52-Wk Low</h4><p>${info.get("fiftyTwoWeekLow", 0):.2f}</p></div>', unsafe_allow_html=True)
                    with c6: st.markdown(f'<div class="metric-card"><h4>Div. Yield</h4><p>{info.get("dividendYield", 0)*100:.2f}%</p></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Price Chart & Moving Averages")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                chart_data = hist_with_indicators[['Close', 'SMA_50', 'SMA_200']] if hist_with_indicators is not None else stock_hist['Close']
                st.line_chart(chart_data)
                st.caption("Blue: Closing Price, Orange: 50-Day MA, Red: 200-Day MA")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("### Recent News & Sentiment")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if not news_articles: st.info("No recent news articles found.")
                else:
                    for article in news_articles[:5]:
                        st.markdown(f"""<div class="news-article"><p class="news-title"><a href="{article['url']}" target="_blank">{article['title']}</a></p><p class="news-source">{article['source']['name']} - {pd.to_datetime(article['publishedAt']).strftime('%Y-%m-%d')}</p></div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Enter your preferences in the sidebar and click 'Analyze & Advise' to begin.")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit & Python. For informational purposes only.")

