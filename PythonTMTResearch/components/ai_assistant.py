"""
Gemini AI Assistant Component
Provides AI-powered insights and answers throughout the application
"""
import streamlit as st
from google import genai
from google.genai import types
from typing import Optional, List, Dict
from data.tmt_data import get_all_companies, get_news_feed, get_earnings_calendar

# Initialize Gemini client
# Uses API key from Streamlit secrets (see .streamlit/secrets.toml)
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

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

def chat_with_gemini(user_message: str, conversation_history: Optional[List[Dict]] = None) -> str:
    """Chat with Gemini AI using conversation history"""
    try:
        context = get_context_data()
        
        # Build conversation for Gemini
        contents = []
        
        # Add system context first
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=context)]
        ))
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                ))
        
        # Add current message
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ))
        
        # Generate response
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

def summarize_content(content: str, max_length: int = 200) -> str:
    """Generate a summary of given content"""
    try:
        prompt = f"Summarize the following content in {max_length} characters or less:\n\n{content}"
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )],
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=100
            )
        )
        return response.text
    except:
        # Fallback to simple truncation
        return content[:max_length] + "..." if len(content) > max_length else content

def render_sidebar_assistant():
    """Render AI Assistant in sidebar"""
    with st.sidebar:
        st.markdown("### 🤖 AI Assistant")
        st.markdown("Ask me anything about the TMT sector!")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**AI:** {content}")
        
        # Input area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask a question...",
                key="ai_input",
                label_visibility="collapsed"
            )
            
            if user_input:
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
