import google.generativeai as genai
import streamlit as st
from google.api_core import exceptions as google_exceptions

def get_chatbot_response(api_key, chat_history, user_prompt, stock_ticker):
    """
    Manages the conversational chat with the Gemini API with improved error handling.

    Args:
        api_key (str): The user's Google Gemini API key.
        chat_history (list): The existing conversation history.
        user_prompt (str): The new prompt from the user.
        stock_ticker (str): The stock ticker currently being analyzed for context.

    Returns:
        str: The response from the chatbot.
    """
    if not api_key:
        return "Error: Gemini API key is not provided. Please enter it in the sidebar."
        
    try:
        genai.configure(api_key=api_key)
        
        # System instruction to define the chatbot's persona and context
        system_instruction = f"""
        You are 'InvestaBot', a specialized financial assistant within the AI Investment Adviser app. 
        Your primary focus is the stock with the ticker symbol: {stock_ticker}.
        You are conversational, helpful, and provide insights based on financial concepts.
        When asked a question, provide a clear, concise answer. 
        Do not hallucinate or provide financial advice that you are not qualified to give.
        Your goal is to help the user understand the data presented in the app.
        """
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )

        history_for_api = []
        for message in chat_history:
            role = 'user' if message['role'] == 'user' else 'model'
            history_for_api.append({'role': role, 'parts': [message['content']]})

        chat = model.start_chat(history=history_for_api)
        response = chat.send_message(user_prompt)
        
        return response.text

    except google_exceptions.PermissionDenied as e:
        error_message = "Authentication Error: Your Gemini API key is invalid or has expired. Please check your key in the sidebar and try again."
        st.error(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred with the Gemini API: {e}"
        st.error(error_message)
        return "Sorry, I'm having trouble connecting to the AI. An unexpected error occurred. Please try again later."

