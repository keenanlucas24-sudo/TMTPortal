"""
Gemini AI Assistant Component
Provides AI-powered insights and answers throughout the application
"""
import streamlit as st
from google import genai
from google.genai import types
import os
from typing import Optional, List, Dict
from data.tmt_data import get_all_companies, get_news_feed, get_earnings_calendar

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def get_context_data() -> str:
    """Get current application context for AI assistant"""
    try:
        companies = get_all_companies()
        news = get_news_feed()[:10]  # Recent 10 news items
        earnings = get_earnings_calendar()[:10]  # Next 10 earnings
        
        # Try to get volatility data
        volatility_info = ""
        try:
            from integrations.stock_prices import get_volatile_stocks
            tickers = [c['ticker'] for c in companies if c.get('ticker')][:20]  # Sample 20 for context
            volatile = get_volatile_stocks(tickers, threshold=2.0)
            if volatile['volatile_count'] > 0:
                volatility_info = f"\n- Volatile Stocks Today (>2%): {volatile['volatile_count']} with {len(volatile['gainers'])} gainers and {len(volatile['losers'])} losers"
        except:
            pass
        
        context = f"""
You are an AI assistant for a TMT (Technology, Media, Telecom) Research Portal.

Current Database Context:
- Total Companies: {len(companies)}
- Sectors: Technology, Media, Telecom
- Recent News Items: {len(news)}
- Upcoming Earnings: {len([e for e in earnings if e['status'] == 'Upcoming'])}{volatility_info}

Sample Companies: {', '.join([c['name'] for c in companies[:10]])}

You can help users with:
1. Information about specific companies (ticker, sector, market cap, description)
2. Summarizing recent news and trends
3. Earnings calendar and financial results
4. Stock price volatility and significant market movements (>2% changes)
5. TMT industry insights and analysis
6. Comparing companies and sectors

Be concise, accurate, and helpful. Use the context provided to give informed answers.
When users ask about volatility or price movements, explain that the portal tracks stocks with >2% daily movements.
"""
        return context
    except:
        return "You are an AI assistant for a TMT Research Portal. Help users with company information, news, earnings data, and stock volatility."


def chat_with_gemini(user_message: str, chat_history: List[Dict]) -> str:
    """
    Send message to Gemini and get response
    
    Args:
        user_message: User's question or message
        chat_history: Previous chat messages
    
    Returns:
        AI response text
    """
    try:
        # Build conversation history
        contents = []
        
        # Add context as system instruction
        system_prompt = get_context_data()
        
        # Add chat history
        for msg in chat_history[-10:]:  # Last 10 messages for context
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))
        
        # Add current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ))
        
        # Generate response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
        )
        
        return response.text or "I'm sorry, I couldn't generate a response."
        
    except Exception as e:
        return f"Error: {str(e)}"


def summarize_content(content: str, content_type: str = "text") -> str:
    """
    Summarize content using Gemini
    
    Args:
        content: Content to summarize
        content_type: Type of content (text, news, earnings)
    
    Returns:
        Summary text
    """
    try:
        prompts = {
            "news": f"Summarize this news article in 2-3 sentences, highlighting key points:\n\n{content}",
            "earnings": f"Summarize these earnings results, focusing on key metrics and performance:\n\n{content}",
            "text": f"Provide a concise summary:\n\n{content}"
        }
        
        prompt = prompts.get(content_type, prompts["text"])
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text or "Unable to generate summary."
        
    except Exception as e:
        return f"Error summarizing: {str(e)}"


def render_sidebar_assistant():
    """Render AI assistant in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Assistant")
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat interface
    with st.sidebar.expander("💬 Chat with AI", expanded=False):
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history[-5:]:  # Show last 5 messages
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**AI:** {msg['content']}")
                st.markdown("---")
        
        # Input area
        user_input = st.text_input(
            "Ask me anything about TMT companies, news, or earnings:",
            key="ai_assistant_input",
            placeholder="e.g., Tell me about Apple's recent news"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send", use_container_width=True, key="ai_send"):
                if user_input.strip():
                    # Add user message to history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Get AI response
                    with st.spinner("Thinking..."):
                        response = chat_with_gemini(user_input, st.session_state.chat_history)
                    
                    # Add AI response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    st.rerun()
        
        with col2:
            if st.button("Clear", use_container_width=True, key="ai_clear"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Quick action buttons
    st.sidebar.markdown("**Quick Actions:**")
    
    col1, col2 = st.sidebar.columns([1, 1])
    
    with col1:
        if st.button("📊 Latest Trends", use_container_width=True, key="quick_trends_btn"):
            question = "What are the latest trends in the TMT sector based on recent news?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Analyzing trends..."):
                response = chat_with_gemini(question, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📰 News Summary", use_container_width=True, key="quick_news_btn"):
            question = "Summarize the most important news from the past 24 hours"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Summarizing news..."):
                response = chat_with_gemini(question, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🎯 Top Performers", use_container_width=True, key="quick_performers_btn"):
            question = "Which companies are performing well based on recent earnings and news?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Analyzing performance..."):
                response = chat_with_gemini(question, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📈 Volatility Alert", use_container_width=True, key="quick_volatility_btn"):
            question = "Show me any stocks with significant price movements (>2%) today"
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Checking volatility..."):
                response = chat_with_gemini(question, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()


# Export functions for use in other views
__all__ = ['render_sidebar_assistant', 'summarize_content', 'chat_with_gemini']
