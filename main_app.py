import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import functions from our other files
from data_fetcher import get_stock_data, get_news_data
from analyzer import calculate_technical_indicators, analyze_sentiment
from adviser import generate_advice, generate_gemini_report

# --- Page Configuration and CSS ---
st.set_page_config(
    page_title="AI Investment Adviser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Greatly enhanced CSS for a professional, modern look with more color
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* General App Styling */
body {
    font-family: 'Poppins', sans-serif;
    color: #333;
}
.stApp {
    background-image: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
}
/* Main content area */
.main .block-container {
    padding: 1rem 3rem;
}
h1, h2 {
    color: #2D3748; /* Darker, more professional headers */
}
/* Card styling */
.card {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid #E0E0E0;
    height: 100%;
    transition: all 0.3s ease;
}
.card:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transform: translateY(-3px);
}
.card h3 {
    margin-top: 0;
    font-weight: 600;
    color: #0072B5; /* Using primary accent color for card titles */
    border-bottom: 2px solid #F0F2F6;
    padding-bottom: 10px;
    margin-bottom: 20px;
}
/* Metric card styling with icons */
.metric-card {
    display: flex;
    align-items: center;
    padding: 10px;
    border-radius: 8px;
    background-color: #F8F9FA;
    margin-bottom: 10px;
}
.metric-card .icon {
    font-size: 1.8rem;
    margin-right: 15px;
    color: #4A90E2;
}
.metric-card .text h4 {
    color: #4A5568;
    font-size: 0.9rem;
    font-weight: 400;
    margin-bottom: 2px;
}
.metric-card .text p {
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0;
    color: #1A20C;
}
/* Recommendation card styling */
.recommendation-card {
    text-align: center;
    padding: 30px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.recommendation-card h2 {
    font-size: 2.8rem;
    font-weight: 700;
    margin: 10px 0 0 0;
}
.rec-icon {
    font-size: 4rem;
    line-height: 1;
}
.buy { background-color: #E6F7F0; border-color: #B3E6D3; color: #006A4E; }
.sell { background-color: #FDEDED; border-color: #F5C0C0; color: #A30000; }
.hold { background-color: #FFFBEA; border-color: #FFE58F; color: #D46B08; }
/* News article styling */
.news-article {
    border-bottom: 1px solid #F0F2F6;
    padding: 15px 5px;
    transition: background-color 0.2s ease;
}
.news-article:hover {
    background-color: #F8F9FA;
    border-radius: 8px;
}
.news-article:last-child { border-bottom: none; }
.news-title {
    font-weight: 600;
    font-size: 1.05rem;
    color: #2D3748;
    text-decoration: none;
}
.news-title a { color: inherit; text-decoration: none; }
.news-source { color: #718096; font-size: 0.85rem; }
/* Sidebar styling */
.st-emotion-cache-16txtl3 { /* Specific selector for sidebar */
    padding: 1.5rem 1rem;
    background-color: #FFFFFF;
    border-right: 1px solid #E0E0E0;
}
.st-emotion-cache-16txtl3 h2 {
    font-weight: 700;
    color: #0072B5;
}
/* Custom button */
div.stButton > button:first-child {
    background-image: linear-gradient(45deg, #4A90E2 0%, #0072B5 100%);
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 1rem;
    font-weight: 600;
    margin-top: 1rem;
    border: none;
    box-shadow: 0 4px 10px rgba(74, 144, 226, 0.3);
}
div.stButton > button:hover {
    background-image: linear-gradient(45deg, #3A7BC2 0%, #005A94 100%);
    box-shadow: 0 6px 15px rgba(74, 144, 226, 0.4);
}
/* Markdown report styling */
.report-card h3 {
    border-bottom: 2px solid #4A90E2;
    padding-bottom: 10px;
    margin-bottom: 15px;
}
/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
		gap: 24px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF;
    color: #0072B5;
    font-weight: 600;
    border-bottom: 2px solid #0072B5;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state to hold analysis results
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- UI Layout ---
with st.sidebar:
    st.markdown("## 📈 AI Adviser")
    st.markdown("---")
    ticker_input = st.text_input("Enter Stock Ticker", value="AAPL", help="e.g., AAPL, GOOGL, MSFT").upper()
    risk_tolerance = st.select_slider("Select Your Risk Tolerance", options=["Low", "Medium", "High"], value="Medium")
    news_api_key = st.text_input("Enter NewsAPI Key", type="password", help="Get a free key from newsapi.org")
    gemini_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get a free key from Google AI Studio")
    analyze_button = st.button("Analyze & Advise")

    # Navigation appears only after an analysis has been run
    if st.session_state.analysis_done:
        st.markdown("---")
        st.session_state.page = st.radio(
            "Navigation",
            ["Dashboard", "Detailed AI Report"],
            key="navigation"
        )

# --- App Logic ---
# This block runs when the "Analyze" button is clicked
if analyze_button:
    if not ticker_input:
        st.warning("Please enter a stock ticker.")
    else:
        with st.spinner("Analyzing..."):
            stock_info, stock_hist = get_stock_data(ticker_input)

            if stock_info and not stock_hist.empty:
                news_articles = get_news_data(ticker_input, news_api_key)
                hist_with_indicators = calculate_technical_indicators(stock_hist)
                avg_sentiment = analyze_sentiment(news_articles)
                advice, _, style_class = generate_advice(hist_with_indicators, avg_sentiment, risk_tolerance)
                gemini_report = generate_gemini_report(
                    stock_info, hist_with_indicators, avg_sentiment, risk_tolerance, gemini_api_key
                )

                st.session_state.analysis_done = True
                st.session_state.stock_info = stock_info
                st.session_state.hist_with_indicators = hist_with_indicators
                st.session_state.news_articles = news_articles
                st.session_state.advice = advice
                st.session_state.style_class = style_class
                st.session_state.gemini_report = gemini_report
                st.session_state.current_ticker = ticker_input
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error(f"Could not retrieve data for ticker: {ticker_input}. Please check the ticker symbol.")
                st.session_state.analysis_done = False

# --- Display Area ---
if st.session_state.analysis_done:
    st.title(f"Analysis for {st.session_state.current_ticker}")

    if st.session_state.page == "Dashboard":
        st.markdown("AI-powered insights into your next investment decision.")
        st.markdown("---")
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown("### Recommendation")
            rec_icon = "⬆️" if "Buy" in st.session_state.advice else "⬇️" if "Sell" in st.session_state.advice else "⏸️"
            st.markdown(f'''
            <div class="card recommendation-card {st.session_state.style_class}">
                <div class="rec-icon">{rec_icon}</div>
                <h2>{st.session_state.advice}</h2>
            </div>''', unsafe_allow_html=True)
            st.info("Navigate to the **Detailed AI Report** for a full breakdown.", icon="ℹ️")

        with col2:
            st.markdown("### Key Information")
            info = st.session_state.stock_info
            st.markdown(f"""
            <div class="card">
                <div class="metric-card"><span class="icon">💼</span><div class="text"><h4>Market Cap</h4><p>${info.get("marketCap", 0):,}</p></div></div>
                <div class="metric-card"><span class="icon">⚖️</span><div class="text"><h4>P/E Ratio</h4><p>{info.get("trailingPE", 0):.2f}</p></div></div>
                <div class="metric-card"><span class="icon">🔼</span><div class="text"><h4>52-Wk High</h4><p>${info.get("fiftyTwoWeekHigh", 0):.2f}</p></div></div>
                <div class="metric-card"><span class="icon">🔽</span><div class="text"><h4>52-Wk Low</h4><p>${info.get("fiftyTwoWeekLow", 0):.2f}</p></div></div>
                <div class="metric-card"><span class="icon">💰</span><div class="text"><h4>Div. Yield</h4><p>{info.get("dividendYield", 0)*100:.2f}%</p></div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        chart_col, news_col = st.columns([2, 1], gap="large")
        with chart_col:
            st.markdown("### Advanced Charting")
            df = st.session_state.hist_with_indicators.tail(365) # Show last year of data
            
            tab1, tab2 = st.tabs(["Price Action (Candlestick)", "Momentum Indicators (RSI, MACD)"])

            with tab1:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                    vertical_spacing=0.05, subplot_titles=('Price', 'Volume'), 
                                    row_heights=[0.7, 0.3])

                # Candlestick
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                             low=df['Low'], close=df['Close'], name='Price'), 
                              row=1, col=1)
                
                # Moving Averages
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1.5), name='SMA 50'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='purple', width=1.5), name='SMA 200'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='yellow', width=1, dash='dot'), name='EMA 50'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='cyan', width=1, dash='dot'), name='EMA 200'), row=1, col=1)

                # Volume
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(0, 114, 181, 0.6)'), row=2, col=1)

                fig.update_layout(showlegend=True, height=600,
                                  xaxis_rangeslider_visible=False,
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                fig.update_yaxes(title_text="Price ($)", row=1, col=1)
                fig.update_yaxes(title_text="Volume", row=2, col=1)
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                     vertical_spacing=0.1, subplot_titles=('Relative Strength Index (RSI)', 'MACD'))

                # RSI
                fig2.add_trace(go.Scatter(x=df.index, y=df['momentum_rsi'], name='RSI'), row=1, col=1)
                fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought", row=1, col=1)
                fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold", row=1, col=1)
                
                # MACD
                fig2.add_trace(go.Scatter(x=df.index, y=df['trend_macd'], name='MACD', line=dict(color='blue')), row=2, col=1)
                fig2.add_trace(go.Scatter(x=df.index, y=df['trend_macd_signal'], name='Signal Line', line=dict(color='orange')), row=2, col=1)
                fig2.add_trace(go.Bar(x=df.index, y=df['trend_macd_diff'], name='Histogram', marker_color='rgba(0, 0, 0, 0.3)'), row=2, col=1)
                
                fig2.update_layout(showlegend=True, height=600,
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                fig2.update_yaxes(title_text="RSI", row=1, col=1)
                fig2.update_yaxes(title_text="Value", row=2, col=1)
                st.plotly_chart(fig2, use_container_width=True)

        with news_col:
            st.markdown("### Recent News & Sentiment")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if not st.session_state.news_articles:
                    st.info("No recent news articles found.")
                else:
                    for article in st.session_state.news_articles[:5]:
                        st.markdown(f"""<div class="news-article"><p class="news-title"><a href="{article['url']}" target="_blank">{article['title']}</a></p><p class="news-source">{article['source']['name']} - {pd.to_datetime(article['publishedAt']).strftime('%Y-%m-%d')}</p></div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


    elif st.session_state.page == "Detailed AI Report":
        st.markdown("---")
        st.markdown("### AI-Generated Report")
        st.markdown(f'<div class="card report-card">{st.session_state.gemini_report}</div>', unsafe_allow_html=True)

else:
    # This is the initial view before any analysis is run
    st.title(f"AI Investment Adviser")
    st.markdown("Your AI-powered copilot for navigating the financial markets. Enter a stock ticker and your details in the sidebar to begin.")
    st.info("Enter your preferences and click 'Analyze & Advise' to begin.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #718096;'>Built with ❤️ using Streamlit & Gemini. For informational purposes only.</div>", unsafe_allow_html=True)

