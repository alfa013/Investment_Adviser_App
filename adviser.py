# import pandas as pd
# import requests
# import json

# def generate_advice(hist_df, sentiment_score, risk_tolerance):
#     """
#     Generates a simple 'Buy', 'Sell', or 'Hold' recommendation based on technical and sentiment signals.
#     This function provides the high-level tag for the recommendation card.
#     """
#     if hist_df is None or 'SMA_50' not in hist_df.columns or 'SMA_200' not in hist_df.columns or len(hist_df) < 2:
#         return "Insufficient Data", "Could not generate advice due to lack of historical data.", "hold"

#     # --- Technical Signal based on SMA Crossover ---
#     latest_sma_50 = hist_df['SMA_50'].iloc[-1]
#     latest_sma_200 = hist_df['SMA_200'].iloc[-1]
#     previous_sma_50 = hist_df['SMA_50'].iloc[-2]
#     previous_sma_200 = hist_df['SMA_200'].iloc[-2]

#     technical_signal = 0 # Neutral
#     if latest_sma_50 > latest_sma_200 and previous_sma_50 <= previous_sma_200:
#         technical_signal = 1 # Golden Cross (Bullish)
#     elif latest_sma_50 < latest_sma_200 and previous_sma_50 >= previous_sma_200:
#         technical_signal = -1 # Death Cross (Bearish)

#     # --- Combine Signals for a Recommendation ---
#     # (This is a simplified logic model)
#     score = technical_signal + (sentiment_score * 2) # Giving sentiment more weight

#     advice = "Hold"
#     style_class = "hold"

#     if score > 1.0:
#         advice = "Strong Buy"
#         style_class = "buy"
#     elif score > 0.2:
#         advice = "Buy"
#         style_class = "buy"
#     elif score < -1.0:
#         advice = "Strong Sell"
#         style_class = "sell"
#     elif score < -0.2:
#         advice = "Sell"
#         style_class = "sell"

#     # Adjusting for risk tolerance
#     if risk_tolerance == "Low" and (advice == "Strong Buy" or advice == "Buy"):
#         advice = "Consider Buying"
#     if risk_tolerance == "High" and advice == "Hold" and technical_signal > 0:
#         advice = "Speculative Buy"

#     # We will let Gemini generate the detailed explanation
#     explanation = f"Generated based on technical indicators and a sentiment score of {sentiment_score:.2f}."

#     return advice, explanation, style_class


# def generate_gemini_report(stock_info, tech_indicators, sentiment, risk, api_key):
#     """
#     Generates a detailed investment report using the Google Gemini API.

#     Args:
#         stock_info (dict): Dictionary of company information.
#         tech_indicators (pd.DataFrame): DataFrame with historical data and SMAs.
#         sentiment (float): The average news sentiment score.
#         risk (str): The user's risk tolerance ('Low', 'Medium', 'High').
#         api_key (str): The user's Google Gemini API key.

#     Returns:
#         str: A Markdown-formatted report from Gemini, or an error message.
#     """
#     if not api_key:
#         return "### Gemini API Key Not Provided\n\nPlease enter your Google Gemini API key in the sidebar to generate a detailed report."

#     # --- Construct a detailed prompt for the Gemini API ---
#     latest_price = tech_indicators['Close'].iloc[-1]
#     latest_sma_50 = tech_indicators['SMA_50'].iloc[-1]
#     latest_sma_200 = tech_indicators['SMA_200'].iloc[-1]
#     company_name = stock_info.get('longName', 'the company')

#     # Determine technical situation
#     tech_situation = f"The 50-day moving average (${latest_sma_50:.2f}) is currently above the 200-day moving average (${latest_sma_200:.2f}), which is generally a bullish sign."
#     if latest_sma_50 < latest_sma_200:
#         tech_situation = f"The 50-day moving average (${latest_sma_50:.2f}) is currently below the 200-day moving average (${latest_sma_200:.2f}), which is generally a bearish sign."

#     # Determine sentiment situation
#     sentiment_situation = "Neutral"
#     if sentiment > 0.2: sentiment_situation = "Positive"
#     elif sentiment < -0.2: sentiment_situation = "Negative"

#     prompt = f"""
#     As an expert financial analyst, generate a comprehensive investment report for {company_name} ({stock_info.get('symbol', '')}).
#     The target audience is an investor with a **{risk}** risk tolerance.

#     **Current Data:**
#     - **Latest Closing Price:** ${latest_price:.2f}
#     - **Market Cap:** ${stock_info.get('marketCap', 0):,}
#     - **P/E Ratio:** {stock_info.get('trailingPE', 'N/A'):.2f}
#     - **52-Week High:** ${stock_info.get('fiftyTwoWeekHigh', 0):.2f}
#     - **52-Week Low:** ${stock_info.get('fiftyTwoWeekLow', 0):.2f}
#     - **Technical Situation:** {tech_situation}
#     - **Recent News Sentiment:** {sentiment_situation} (Score: {sentiment:.2f})

#     **Task:**
#     Based on the data above and the investor's {risk} risk profile, provide a detailed report.
#     Structure the report with the following Markdown sections:
#     - `### Executive Summary` (A brief, high-level recommendation and overview).
#     - `### Technical Analysis` (Elaborate on the moving averages and what they imply).
#     - `### Sentiment Analysis` (Discuss the news sentiment and its potential impact).
#     - `### Risk Assessment` (Analyze the potential risks, specifically tailored to a {risk} risk tolerance investor).
#     - `### Final Recommendation` (Provide a concluding paragraph with a clear course of action).

#     The tone should be professional, balanced, and strictly informational. Do not give financial advice, but rather an expert analysis based on the provided data.
#     """

#     # --- API Call to Gemini ---
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-05-20:generateContent?key={api_key}"
#     payload = {
#         "contents": [{
#             "parts": [{"text": prompt}]
#         }]
#     }
#     headers = {'Content-Type': 'application/json'}

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()  # Raise an exception for bad status codes
#         result = response.json()
#         report = result['candidates'][0]['content']['parts'][0]['text']
#         return report
#     except requests.exceptions.RequestException as e:
#         return f"### Error Connecting to Gemini API\n\nAn error occurred: {e}\nPlease check your API key and network connection."
#     except (KeyError, IndexError) as e:
#         return f"### Error Parsing Gemini Response\n\nReceived an unexpected response from the API: {result}"

import pandas as pd
import google.generativeai as genai  # <-- Import the new library
# import requests  <-- No longer needed
# import json      <-- No longer needed

def generate_advice(hist_df, sentiment_score, risk_tolerance):
    """
    Generates a simple 'Buy', 'Sell', or 'Hold' recommendation based on technical and sentiment signals.
    This function provides the high-level tag for the recommendation card.
    """
    if hist_df is None or 'SMA_50' not in hist_df.columns or 'SMA_200' not in hist_df.columns or len(hist_df) < 2:
        return "Insufficient Data", "Could not generate advice due to lack of historical data.", "hold"

    # --- Technical Signal based on SMA Crossover ---
    latest_sma_50 = hist_df['SMA_50'].iloc[-1]
    latest_sma_200 = hist_df['SMA_200'].iloc[-1]
    previous_sma_50 = hist_df['SMA_50'].iloc[-2]
    previous_sma_200 = hist_df['SMA_200'].iloc[-2]

    technical_signal = 0 # Neutral
    if latest_sma_50 > latest_sma_200 and previous_sma_50 <= previous_sma_200:
        technical_signal = 1 # Golden Cross (Bullish)
    elif latest_sma_50 < latest_sma_200 and previous_sma_50 >= previous_sma_200:
        technical_signal = -1 # Death Cross (Bearish)

    # --- Combine Signals for a Recommendation ---
    # (This is a simplified logic model)
    score = technical_signal + (sentiment_score * 2) # Giving sentiment more weight

    advice = "Hold"
    style_class = "hold"

    if score > 1.0:
        advice = "Strong Buy"
        style_class = "buy"
    elif score > 0.2:
        advice = "Buy"
        style_class = "buy"
    elif score < -1.0:
        advice = "Strong Sell"
        style_class = "sell"
    elif score < -0.2:
        advice = "Sell"
        style_class = "sell"

    # Adjusting for risk tolerance
    if risk_tolerance == "Low" and (advice == "Strong Buy" or advice == "Buy"):
        advice = "Consider Buying"
    if risk_tolerance == "High" and advice == "Hold" and technical_signal > 0:
        advice = "Speculative Buy"

    # We will let Gemini generate the detailed explanation
    explanation = f"Generated based on technical indicators and a sentiment score of {sentiment_score:.2f}."

    return advice, explanation, style_class


def generate_gemini_report(stock_info, tech_indicators, sentiment, risk, api_key):
    """
    Generates a detailed investment report using the Google Gemini API.

    Args:
        stock_info (dict): Dictionary of company information.
        tech_indicators (pd.DataFrame): DataFrame with historical data and SMAs.
        sentiment (float): The average news sentiment score.
        risk (str): The user's risk tolerance ('Low', 'Medium', 'High').
        api_key (str): The user's Google Gemini API key.

    Returns:
        str: A Markdown-formatted report from Gemini, or an error message.
    """
    if not api_key:
        return "### Gemini API Key Not Provided\n\nPlease enter your Google Gemini API key in the sidebar to generate a detailed report."

    try:
        # --- Configure the Gemini API key ---
        genai.configure(api_key=api_key)

        # --- Prepare data for the prompt ---
        latest_price = tech_indicators['Close'].iloc[-1]
        latest_sma_50 = tech_indicators['SMA_50'].iloc[-1]
        latest_sma_200 = tech_indicators['SMA_200'].iloc[-1]
        company_name = stock_info.get('longName', 'the company')
        
        # Safe handling for P/E ratio
        pe_ratio = stock_info.get('trailingPE', 'N/A')
        pe_ratio_str = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"

        # Determine technical situation
        tech_situation = f"The 50-day moving average (${latest_sma_50:.2f}) is currently above the 200-day moving average (${latest_sma_200:.2f}), which is generally a bullish sign."
        if latest_sma_50 < latest_sma_200:
            tech_situation = f"The 50-day moving average (${latest_sma_50:.2f}) is currently below the 200-day moving average (${latest_sma_200:.2f}), which is generally a bearish sign."

        # Determine sentiment situation
        sentiment_situation = "Neutral"
        if sentiment > 0.2: sentiment_situation = "Positive"
        elif sentiment < -0.2: sentiment_situation = "Negative"

        # --- 1. Define the System Instruction (The "Persona") ---
        system_instruction = """
As an expert financial analyst, your task is to generate a comprehensive investment report.
The tone should be professional, balanced, and strictly informational. Do not give financial advice, but rather an expert analysis based on the provided data.
Structure the report with the following Markdown sections:
- `### Executive Summary` (A brief, high-level recommendation and overview).
- `### Technical Analysis` (Elaborate on the moving averages and what they imply).
- `### Sentiment Analysis` (Discuss the news sentiment and its potential impact).
- `### Risk Assessment` (Analyze the potential risks, specifically tailored to the investor's risk tolerance).
- `### Final Recommendation` (Provide a concluding paragraph with a clear course of action).
"""

        # --- 2. Initialize the Model (as per your last request) ---
        model = genai.GenerativeModel(
            model_name='gemini-2.5-pro',  # Using 1.5-pro as a robust standard
            system_instruction=system_instruction
        )

        # --- 3. Define the User Prompt (The specific data) ---
        user_prompt = f"""
Generate a comprehensive investment report for {company_name} ({stock_info.get('symbol', '')}).
The target audience is an investor with a **{risk}** risk tolerance.

**Current Data:**
- **Latest Closing Price:** ${latest_price:.2f}
- **Market Cap:** ${stock_info.get('marketCap', 0):,}
- **P/E Ratio:** {pe_ratio_str}
- **52-Week High:** ${stock_info.get('fiftyTwoWeekHigh', 0):.2f}
- **52-Week Low:** ${stock_info.get('fiftyTwoWeekLow', 0):.2f}
- **Technical Situation:** {tech_situation}
- **Recent News Sentiment:** {sentiment_situation} (Score: {sentiment:.2f})
"""

        # --- 4. Call the API ---
        response = model.generate_content(user_prompt)
        
        return response.text

    except Exception as e:
        # Catch-all for API errors, auth errors, etc.
        return f"### Error Generating Gemini Report\n\nAn error occurred: {e}\nPlease check your API key, network connection, and model name."