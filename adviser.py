def generate_advice(hist_with_indicators, sentiment_score, risk_tolerance):
    """
    Generates investment advice based on technicals, sentiment, and user risk tolerance.

    Args:
        hist_with_indicators (pd.DataFrame): DataFrame with price data and technical indicators.
        sentiment_score (float): The average news sentiment score.
        risk_tolerance (str): The user's selected risk tolerance ("Low", "Medium", "High").

    Returns:
        tuple: A tuple containing the advice (str), a detailed explanation (str), and a style class (str).
    """
    if hist_with_indicators is None:
        return "Hold", "Insufficient historical data for a full analysis (less than 200 days).", "hold"

    # --- Technical Signal ---
    last_sma_50 = hist_with_indicators['SMA_50'].iloc[-1]
    last_sma_200 = hist_with_indicators['SMA_200'].iloc[-1]
    tech_signal = 1 if last_sma_50 > last_sma_200 else -1
    
    # --- Sentiment Signal ---
    sent_signal = 1 if sentiment_score > 0.1 else (-1 if sentiment_score < -0.1 else 0)
    
    combined_signal = tech_signal + sent_signal
    
    advice, reason, style_class = "Hold", "Signals are neutral or conflicting.", "hold"

    # --- Decision Logic ---
    if combined_signal >= 2:
        advice, reason, style_class = "Strong Buy", "Strong positive technicals and news sentiment.", "buy"
    elif combined_signal == 1:
        if risk_tolerance == "High":
            advice, reason, style_class = "Buy", "Positive signals suggest potential upside for higher-risk investors.", "buy"
        else:
            advice, reason, style_class = "Hold", "Signals are positive but not strong enough for a lower-risk profile.", "hold"
    elif combined_signal == -1:
        if risk_tolerance != "Low":
            advice, reason, style_class = "Sell", "Negative signals suggest potential downside risk.", "sell"
        else:
            advice, reason, style_class = "Hold", "Signals are negative but not a strong enough sell signal for a low-risk profile.", "hold"
    elif combined_signal <= -2:
        advice, reason, style_class = "Strong Sell", "Strong negative technicals and news sentiment indicate high risk.", "sell"
        
    explanation = (
        f"{reason} The 50-day moving average ({last_sma_50:.2f}) is currently "
        f"{'above' if tech_signal == 1 else 'below'} the 200-day moving average ({last_sma_200:.2f}). "
        f"Recent news sentiment is {'positive' if sent_signal == 1 else 'negative' if sent_signal == -1 else 'neutral'} "
        f"with a score of {sentiment_score:.2f}."
    )
    return advice, explanation, style_class
