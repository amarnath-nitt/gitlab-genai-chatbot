"""
GitLab GenAI Chatbot - Simplified Version
A clean, simple chatbot that uses RAG to answer questions about GitLab.
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from typing import List, Dict, Any
import os
from config import settings

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GitLab GenAI Chatbot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --accent: #FC6D26;            /* GitLab orange */
        --accent-2: #4285f4;          /* Google blue */
        --text-muted: #666666;
        --surface: #f8f9fa;
        --soft: #f0f2f6;
        --info-bg: #e9f5ff;
        --info-bd: #b3e0ff;
        --warn-bg: #fff4e5;
        --warn-bd: #ffd199;
        --shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-muted: #a3a3a3;
            --surface: #1f2937;
            --soft: #111827;
            --info-bg: #0b2537;
            --info-bd: #1f4a6e;
            --warn-bg: #3b2a17;
            --warn-bd: #7a4b15;
            --shadow: 0 2px 10px rgba(0,0,0,0.25);
        }
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--accent);
        text-align: center;
        margin-bottom: 1rem;
    }

    .subheader {
        text-align: center;
        margin-bottom: 2rem;
        color: var(--text-muted);
    }

    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent);
        background: var(--surface);
        box-shadow: var(--shadow);
    }
    
    .user-message {
        background-color: var(--soft);
        border-left-color: var(--accent);
    }
    
    .assistant-message {
        background-color: var(--info-bg);
        border-left-color: var(--accent-2);
    }
    
    .source-link {
        color: var(--accent);
        text-decoration: none;
    }
    .source-link:hover { text-decoration: underline; }

    /* Reusable notice blocks */
    .notice {
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid transparent;
        box-shadow: var(--shadow);
        margin-top: 1rem;
    }
    .notice.center { text-align: center; }
    .notice.info { background: var(--info-bg); border-color: var(--info-bd); }
    .notice.warning { background: var(--warn-bg); border-color: var(--warn-bd); }
    .notice.tip { background: var(--surface); border-color: #e5e7eb; }
    .notice h3, .notice h4 { margin: 0 0 .5rem 0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'model' not in st.session_state:
    st.session_state.model = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'custom_api_key' not in st.session_state:
    st.session_state.custom_api_key = ""

def initialize_ai(api_key=None):
    """Initialize Google Gemini AI model."""
    try:
        # Use provided API key or session state key or environment key
        key_to_use = api_key or st.session_state.custom_api_key or settings.google_api_key
        
        if not key_to_use or key_to_use == "your_google_api_key_here":
            return False, "No valid API key provided"
        
        genai.configure(api_key=key_to_use)
        st.session_state.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Test the API key with a simple request
        test_response = st.session_state.model.generate_content("Hello")
        if test_response.text:
            st.session_state.api_key_set = True
            return True, "AI initialized successfully"
        else:
            return False, "API key test failed"
            
    except Exception as e:
        return False, f"Error initializing AI: {str(e)}"

def get_gitlab_content(query: str) -> List[Dict[str, Any]]:
    """Get relevant GitLab content based on query."""
    
    # Enhanced GitLab knowledge base
    # NOTE: This is a curated, pre-verified knowledge base for instant responses
    # Alternative approach: We could implement periodic web scraping to update this data
    # Benefits of current approach: Fast, reliable, consistent
    # Benefits of dynamic scraping: Always up-to-date, comprehensive coverage
    knowledge_base = {
        "onboarding": {
            "content": """
            GitLab's onboarding process for new team members includes:
            1. Welcome call with People Operations
            2. Access to GitLab Handbook and training materials
            3. Introduction to team and key stakeholders
            4. Technical setup and tool access
            5. 30-60-90 day check-ins with manager
            6. Buddy system for new hires
            7. Culture and values training sessions
            8. Security and compliance training
            9. Product and company overview sessions
            10. Regular feedback and adjustment periods
            """,
            "source": "https://handbook.gitlab.com/handbook/people-group/general-onboarding/"
        },
        "culture": {
            "content": """
            GitLab's company culture is built on:
            - Transparency: All company information is public
            - Collaboration: Cross-functional teamwork
            - Remote-first: Fully distributed team
            - Iteration: Continuous improvement
            - Results: Focus on outcomes
            - Efficiency: Work smarter, not harder
            - Diversity & Inclusion: Welcoming environment
            - Asynchronous communication
            - Work-life balance
            - Building in public
            """,
            "source": "https://handbook.gitlab.com/handbook/values/"
        },
        "remote work": {
            "content": """
            GitLab's remote work approach:
            - Fully remote company since 2011
            - Asynchronous communication preferred
            - Flexible working hours
            - Global team across time zones
            - Tools: GitLab, Slack, Zoom, Google Workspace
            - Regular team meetings and 1:1s
            - Documentation-first approach
            - Work-life balance emphasis
            - No office locations
            - Remote-friendly processes
            """,
            "source": "https://handbook.gitlab.com/company/culture/all-remote/"
        },
        "performance": {
            "content": """
            GitLab's performance review process:
            - Quarterly performance reviews
            - 360-degree feedback system
            - Goal setting and tracking
            - Career development discussions
            - Regular one-on-one meetings
            - Peer feedback and recognition
            - Performance improvement plans
            - Promotion and advancement opportunities
            - Continuous feedback culture
            - Manager training and support
            """,
            "source": "https://handbook.gitlab.com/handbook/people-group/performance-and-development/"
        },
        "values": {
            "content": """
            GitLab's core values (CREDIT):
            - Collaboration: Working together effectively
            - Results: Focus on outcomes and impact
            - Efficiency: Optimizing processes and time
            - Diversity, Inclusion & Belonging: Welcoming all
            - Iteration: Continuous improvement
            - Transparency: Open and honest communication
            
            These values guide all company decisions and behaviors.
            """,
            "source": "https://handbook.gitlab.com/handbook/values/"
        },
        "product": {
            "content": """
            GitLab's product strategy focuses on:
            - DevOps platform consolidation
            - Open source community engagement
            - Enterprise security and compliance
            - Cloud-native solutions
            - AI and ML integration
            - Developer experience optimization
            - Global market expansion
            - Customer success and support
            - Innovation and R&D
            - Platform scalability
            """,
            "source": "https://about.gitlab.com/direction/"
        }
    }
    
    # Simple keyword matching to find relevant content
    query_lower = query.lower()
    relevant_content = []
    
    for key, data in knowledge_base.items():
        if any(word in query_lower for word in key.split()):
            relevant_content.append(data)
        elif any(word in query_lower for word in ["gitlab", "company", "organization"]):
            relevant_content.append(data)
    
    # If no specific match, return culture and values as default
    if not relevant_content:
        relevant_content = [knowledge_base["culture"], knowledge_base["values"]]
    
    return relevant_content[:3]  # Return top 3 relevant pieces

def generate_response(query: str) -> str:
    """Generate AI response using Gemini with conversation context."""
    try:
        # Get relevant GitLab content
        gitlab_content = get_gitlab_content(query)
        
        # Build context
        context = "\n\n".join([f"Source: {item['source']}\nContent: {item['content']}" for item in gitlab_content])
        
        # Build conversation history for context
        conversation_history = ""
        if len(st.session_state.chat_history) > 1:
            recent_messages = st.session_state.chat_history[-4:]  # Last 4 messages for context
            conversation_history = "\n\nRecent conversation:\n"
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_history += f"{role}: {msg['content']}\n"
        
        # Create prompt with conversation context
        prompt = f"""
        You are a helpful AI assistant for GitLab. Answer the user's question about GitLab using the provided context and conversation history.
        
        Context from GitLab documentation:
        {context}
        
        {conversation_history}
        
        Current User Question: {query}
        
        Guidelines:
        1. Provide specific, detailed answers based on the GitLab context
        2. Be helpful and professional
        3. If this is a follow-up question, reference the previous conversation
        4. Mention relevant sources when possible
        5. If the context doesn't contain enough information, say so clearly
        6. Focus on GitLab-specific information
        7. Maintain conversation flow and context
        
        Answer:
        """
        
        # Generate response
        response = st.session_state.model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "I apologize, but I encountered an error while generating a response. Please try again."

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 GitLab GenAI Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="subheader">
        Ask questions about GitLab's culture, processes, and practices.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # API Key Management
        st.markdown("### 🔑 API Key Setup")
        
        # Always show API key input form
        session_key_available = st.session_state.custom_api_key != ""
        
        if session_key_available:
            st.success("✅ API Key Set")
            st.markdown("*Ready to initialize AI*")
            
            # Show option to change API key
            if st.button("🔄 Change API Key"):
                st.session_state.custom_api_key = ""
                st.session_state.model = None
                st.session_state.api_key_set = False
                st.rerun()
        else:
            st.info("📝 Please enter your Google AI API Key")
            
            # API Key input form
            with st.form(key="api_key_form"):
                api_key_input = st.text_input(
                    "Enter Google AI API Key:",
                    type="password",
                    placeholder="AIza...",
                    help="Get your free API key from https://aistudio.google.com"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    set_key_button = st.form_submit_button("🔑 Set Key", type="primary")
                with col2:
                    test_key_button = st.form_submit_button("🧪 Test Key")
                
                if set_key_button and api_key_input:
                    st.session_state.custom_api_key = api_key_input
                    st.success("API key set! Click 'Initialize AI' to start.")
                    st.rerun()
                
                if test_key_button and api_key_input:
                    with st.spinner("Testing API key..."):
                        success, message = initialize_ai(api_key_input)
                        if success:
                            st.success("✅ API key is valid!")
                            st.session_state.custom_api_key = api_key_input
                        else:
                            st.error(f"❌ {message}")
        
        # Initialize AI
        st.markdown("### 🤖 AI Initialization")
        if st.session_state.model is None:
            if st.button("🚀 Initialize AI", type="primary", disabled=not session_key_available):
                with st.spinner("Initializing AI..."):
                    success, message = initialize_ai()
                    if success:
                        st.success("✅ AI Ready!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            st.success("✅ AI Ready")
            
            # Clear chat and reset options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.success("Chat cleared!")
                    st.rerun()
            with col2:
                if st.button("🔄 Reset AI"):
                    st.session_state.model = None
                    st.session_state.api_key_set = False
                    st.success("AI reset!")
                    st.rerun()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        st.markdown(f"**API Source:** {'UI' if session_key_available else 'None'}")
        st.markdown("**Model:** Gemini 1.5 Flash")
        st.markdown(f"**Status:** {'✅ Ready' if st.session_state.model else '❌ Not Ready'}")
        
        # Help section
        st.markdown("### 💡 Help")
        st.markdown("""
        **Get API Key:**
        1. Visit [Google AI Studio](https://aistudio.google.com)
        2. Create account and generate API key
        3. Free tier: 1,500 requests/day
        
        **Features:**
        - Follow-up questions
        - GitLab knowledge base
        - Auto-clear input
        - Conversation context
        """)
    
    # Main chat interface
    if st.session_state.model:
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Conversation")
            for message in st.session_state.chat_history:
                is_user = message["role"] == "user"
                message_class = "user-message" if is_user else "assistant-message"
                
                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>{'You' if is_user else 'GitLab Assistant'}</strong>
                    <div style="margin-top: 0.5rem;">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("### 💭 Ask a Question")
        
        # Create a form for better UX
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your question about GitLab:",
                height=100,
                placeholder="e.g., What is GitLab's onboarding process? How does GitLab handle remote work?",
                key="user_input"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                send_button = st.form_submit_button("📤 Send", type="primary")
        
        # Process message when form is submitted
        if send_button and user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": "now"
            })
            
            # Generate response
            with st.spinner("🤔 Thinking..."):
                response = generate_response(user_input)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": "now"
            })
            
            st.rerun()
        
        # Example questions
        st.markdown("### 💡 Example Questions")
        
        # Show different examples based on conversation context
        if len(st.session_state.chat_history) == 0:
            # Initial questions
            examples = [
                "What is GitLab's onboarding process?",
                "How does GitLab approach remote work?",
                "What are GitLab's core values?",
                "How does GitLab handle performance reviews?",
                "What is GitLab's product strategy?"
            ]
        else:
            # Follow-up questions based on context
            examples = [
                "Can you tell me more about that?",
                "What are the benefits of this approach?",
                "How does this compare to other companies?",
                "What challenges might someone face?",
                "Are there any best practices?"
            ]
        
        for example in examples:
            if st.button(f"❓ {example}", key=f"example_{example}"):
                # Add user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": example,
                    "timestamp": "now"
                })
                
                # Generate response
                with st.spinner("🤔 Thinking..."):
                    response = generate_response(example)
                
                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": "now"
                })
                
                st.rerun()
        
        # Conversation tips
        if len(st.session_state.chat_history) > 0:
            st.markdown("""
            <div class="notice tip">
                <h4>💬 Conversation Tips</h4>
                <ul>
                    <li>Ask follow-up questions like "Can you tell me more about that?"</li>
                    <li>Request specific details: "What are the steps?"</li>
                    <li>Ask for comparisons: "How does this work compared to...?"</li>
                    <li>Request examples: "Can you give me an example?"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Welcome message
        session_key_available = st.session_state.custom_api_key != ""
        
        if not session_key_available:
            st.markdown("""
            <div class="notice info center">
                <h3 style="color: white;">🔑 Google AI API Key Required</h3>
                <p style="color: white;">To unlock the full potential of the GitLab GenAI Chatbot, please provide your Google AI API Key.</p>
                <p style="color: white;"><strong>Follow these steps to get started:</strong></p>
                <ol style="text-align: left; display: inline-block; color: white;">
                    <li>Visit <a href="https://aistudio.google.com" target="_blank" style="color: white;">Google AI Studio</a> to generate your free API key.</li>
                    <li>Enter your generated API key in the sidebar's "API Key Setup" section.</li>
                    <li>Click the "Initialize AI" button to begin chatting!</li>
                </ol>
                <p style="color: white;"><i>A free tier offering 1,500 API calls per day is available.</i></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="notice info center">
                <h3>👋 Welcome to GitLab GenAI Chatbot!</h3>
                <p>Click "Initialize AI" in the sidebar to get started.</p>
                <p>Ask questions about GitLab's culture, processes, and practices.</p>
                <p><strong>Features:</strong> Follow-up questions, conversation context, auto-clear input</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()