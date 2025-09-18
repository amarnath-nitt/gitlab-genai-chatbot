"""
Enhanced GitLab GenAI Chatbot with Advanced Features
A sophisticated chatbot with dynamic updates, transparency features, and analytics.
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
import os
import json
from datetime import datetime, timedelta
from config import settings
from enhanced_gitlab_service import get_gitlab_service

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

# Enhanced Custom CSS
st.markdown("""
<style>
    :root {
        --accent: #FC6D26;
        --accent-2: #4285f4;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
        --text-muted: #666666;
        --surface: #f8f9fa;
        --soft: #f0f2f6;
        --info-bg: #e9f5ff;
        --info-bd: #b3e0ff;
        --warn-bg: #fff4e5;
        --warn-bd: #ffd199;
        --shadow: 0 2px 6px rgba(0,0,0,0.06);
        --border-radius: 12px;
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
        
        .notice.info { 
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 2px solid var(--accent);
            color: #e2e8f0;
        }
        .notice.warning { 
            background: linear-gradient(135deg, #451a03 0%, #78350f 100%);
            border: 2px solid var(--warning);
            color: #fbbf24;
        }
        .notice.tip { 
            background: linear-gradient(135deg, #14532d 0%, #166534 100%);
            border: 2px solid var(--success);
            color: #bbf7d0;
        }
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, var(--accent), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
    }

    .subheader {
        text-align: center;
        margin-bottom: 2rem;
        color: var(--text-muted);
    }

    .chat-message {
        padding: 1.2rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent);
        background: var(--surface);
        box-shadow: var(--shadow);
        position: relative;
    }
    
    .user-message {
        background-color: var(--soft);
        border-left-color: var(--accent);
    }
    
    .assistant-message {
        background-color: var(--info-bg);
        border-left-color: var(--accent-2);
    }
    
    .confidence-indicator {
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 0.8rem;
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .confidence-high { background: var(--success); color: white; }
    .confidence-medium { background: var(--warning); color: black; }
    .confidence-low { background: var(--danger); color: white; }
    
    .source-link {
        color: var(--accent);
        text-decoration: none;
        font-size: 0.9rem;
    }
    .source-link:hover { text-decoration: underline; }

    .followup-question {
        background: var(--soft);
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .followup-question:hover {
        background: var(--info-bg);
        border-color: var(--accent);
        transform: translateY(-1px);
    }

    .stats-card {
        background: var(--surface);
        padding: 1rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        text-align: center;
    }

    .notice {
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 1px solid transparent;
        box-shadow: var(--shadow);
        margin: 1rem 0;
    }
    .notice.center { text-align: center; }
    .notice.info { 
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid var(--accent);
        color: #1a202c;
    }
    .notice.warning { 
        background: linear-gradient(135deg, #fffbf0 0%, #fef5e7 100%);
        border: 2px solid var(--warning);
        color: #744210;
    }
    .notice.tip { 
        background: linear-gradient(135deg, #f0fff4 0%, #dcfce7 100%);
        border: 2px solid var(--success);
        color: #14532d;
    }
    .notice h3, .notice h4 { margin: 0 0 .5rem 0; }
    
    .update-banner {
        background: linear-gradient(45deg, var(--accent), var(--accent-2));
        color: white;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced features
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'chat_history': [],
        'model': None,
        'api_key_set': False,
        'custom_api_key': "",
        'conversation_stats': {'total_queries': 0, 'topics_discussed': set()},
        'show_sources': True,
        'show_confidence': True,
        'show_followups': True
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Fix topics_discussed if it's not a set
    if not isinstance(st.session_state.conversation_stats['topics_discussed'], set):
        st.session_state.conversation_stats['topics_discussed'] = set(st.session_state.conversation_stats['topics_discussed'])

def initialize_ai(api_key=None):
    """Initialize Google Gemini AI model with enhanced error handling."""
    try:
        key_to_use = api_key or st.session_state.custom_api_key or settings.google_api_key

        if not key_to_use or key_to_use == "your_google_api_key_here":
            return False, "No valid API key provided"

        genai.configure(api_key=key_to_use)
        st.session_state.model = genai.GenerativeModel("gemini-1.5-flash")

        # Test the API key
        test_response = st.session_state.model.generate_content("Hello")
        if test_response.text:
            st.session_state.api_key_set = True
            return True, "AI initialized successfully"
        else:
            return False, "API key test failed"

    except Exception as e:
        return False, f"Error initializing AI: {str(e)}"

def generate_enhanced_response(query: str) -> Tuple[str, List[Dict], List[str], str]:
    """Generate enhanced AI response with sources, follow-ups, and confidence"""
    try:
        # Get GitLab service
        gitlab_service = get_gitlab_service()

        # Get relevant content with scoring
        gitlab_content = gitlab_service.get_content_for_query(query)

        # Build context with relevance scores
        context_parts = []
        for item in gitlab_content:
            relevance = item.get('relevance_score', 0)
            context_parts.append(
                f"Source: {item['source']} (Relevance: {relevance:.2f})\n"
                f"Topic: {item.get('topic', 'General')}\n"
                f"Content: {item['content']}\n"
            )
        context = "\n".join(context_parts)

        # Build conversation history
        conversation_history = ""
        if len(st.session_state.chat_history) > 1:
            recent_messages = st.session_state.chat_history[-4:]
            conversation_history = "\n\nRecent conversation:\n"
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_history += f"{role}: {msg['content'][:200]}...\n"

        # Enhanced prompt with confidence indicators
        prompt = f"""
        You are a helpful AI assistant for GitLab. Answer the user's question using the provided context.
        
        Context from GitLab documentation (with relevance scores):
        {context}
        
        {conversation_history}
        
        Current User Question: {query}
        
        Guidelines:
        1. Provide specific, detailed answers based on the GitLab context
        2. Be helpful and professional
        3. Reference conversation history if this is a follow-up question
        4. Focus on GitLab-specific information
        5. If context has low relevance scores, acknowledge uncertainty
        6. Organize your response clearly with proper formatting
        
        Answer:
        """

        # Generate response
        response = st.session_state.model.generate_content(prompt)
        response_text = response.text

        # Generate follow-up questions
        followup_questions = gitlab_service.generate_followup_questions(
            response_text, query, st.session_state.model
        )

        # Calculate confidence
        confidence_level, confidence_icon = gitlab_service.get_response_confidence(
            query, gitlab_content
        )

        # Prepare sources with metadata
        sources_with_metadata = []
        for item in gitlab_content:
            sources_with_metadata.append({
                'url': item['source'],
                'title': extract_title_from_url(item['source']),
                'relevance_score': item.get('relevance_score', 0),
                'confidence': item.get('confidence', 0),
                'last_updated': item.get('last_updated', 'Unknown'),
                'topic': item.get('topic', 'General')
            })

        return response_text, sources_with_metadata, followup_questions, confidence_level

    except Exception as e:
        logger.error(f"Error generating enhanced response: {e}")
        return (
            "I apologize, but I encountered an error while generating a response. Please try again.",
            [],
            ["Can you try rephrasing your question?", "What specific aspect interests you?"],
            "Low"
        )

def extract_title_from_url(url: str) -> str:
    """Extract a readable title from GitLab URL"""
    if "onboarding" in url:
        return "GitLab Onboarding Guide"
    elif "values" in url:
        return "GitLab Values & Culture"
    elif "remote" in url:
        return "Remote Work at GitLab"
    elif "performance" in url:
        return "Performance Management"
    elif "direction" in url:
        return "GitLab Product Direction"
    else:
        return "GitLab Handbook"

def display_enhanced_chat_history():
    """Display chat history with enhanced features"""
    if not st.session_state.chat_history:
        return

    st.markdown("### 💬 Conversation")

    for i, message in enumerate(st.session_state.chat_history):
        is_user = message["role"] == "user"

        # Use columns for better layout
        col1, col2 = st.columns([1, 12])

        with col1:
            if is_user:
                st.markdown("👤")
            else:
                st.markdown("🤖")

        with col2:
            # Create container for each message
            with st.container():
                # Message header with role and confidence
                if is_user:
                    st.markdown("**You**")
                else:
                    header_cols = st.columns([3, 1])
                    with header_cols[0]:
                        st.markdown("**GitLab Assistant**")
                    with header_cols[1]:
                        if st.session_state.show_confidence and 'confidence_level' in message:
                            confidence = message['confidence_level']
                            if confidence == "High":
                                st.markdown('<span style="background: #28a745; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem; font-weight: bold;">🎯 High</span>', unsafe_allow_html=True)
                            elif confidence == "Medium":
                                st.markdown('<span style="background: #ffc107; color: black; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem; font-weight: bold;">⚖️ Medium</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span style="background: #dc3545; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem; font-weight: bold;">⚠️ Low</span>', unsafe_allow_html=True)

                # Message content
                content = message['content']

                # For assistant messages, format the content better
                if not is_user:
                    # Replace **text** with proper markdown bold
                    content = content.replace('**', '**')
                    # Handle bullet points properly
                    lines = content.split('\n')
                    formatted_lines = []
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*') and not line.startswith('**'):
                            # Convert * to proper bullet
                            formatted_lines.append(f"• {line[1:].strip()}")
                        else:
                            formatted_lines.append(line)
                    content = '\n'.join(formatted_lines)

                st.markdown(content)

                # Add sources for assistant messages
                if not is_user and st.session_state.show_sources and 'sources' in message:
                    sources = message['sources']
                    if sources:
                        st.markdown("---")
                        st.markdown("**📚 Sources:**")
                        for source in sources:
                            relevance = source.get('relevance_score', 0)
                            col_source1, col_source2 = st.columns([4, 1])
                            with col_source1:
                                st.markdown(f"[{source['title']}]({source['url']})")
                            with col_source2:
                                st.caption(f"Relevance: {relevance:.1f}")

        # Add some spacing between messages
        st.markdown("---")

        # Add follow-up questions for the latest assistant message
        if (not is_user and st.session_state.show_followups and
            'followup_questions' in message and message['followup_questions'] and
            i == len(st.session_state.chat_history) - 1):

            st.markdown("**💡 Follow-up questions:**")
            followup_cols = st.columns(min(len(message['followup_questions']), 2))

            for j, followup in enumerate(message['followup_questions']):
                with followup_cols[j % len(followup_cols)]:
                    if st.button(f"❓ {followup}", key=f"followup_{i}_{j}", use_container_width=True):
                        process_user_query(followup)

def process_user_query(user_input: str):
    """Process user query and generate response"""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    # Update stats
    st.session_state.conversation_stats['total_queries'] += 1

    # Generate enhanced response
    with st.spinner("🤔 Analyzing and generating response..."):
        response_text, sources, followup_questions, confidence_level = generate_enhanced_response(user_input)

    # Extract topics for stats
    topics = extract_topics_from_query(user_input)
    for topic in topics:
        st.session_state.conversation_stats['topics_discussed'].add(topic)

    # Add assistant response with enhanced metadata
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text,
        "sources": sources,
        "followup_questions": followup_questions,
        "confidence_level": confidence_level,
        "timestamp": datetime.now().isoformat(),
        "topics": topics
    })

    st.rerun()

def extract_topics_from_query(query: str) -> List[str]:
    """Extract topics from user query for analytics"""
    query_lower = query.lower()
    topics = []

    topic_keywords = {
        "onboarding": ["onboarding", "new hire", "welcome", "start", "join"],
        "culture": ["culture", "values", "transparency", "collaboration"],
        "remote_work": ["remote", "work from home", "distributed", "async"],
        "performance": ["performance", "review", "feedback", "development"],
        "product": ["product", "strategy", "direction", "roadmap"],
        "hiring": ["hiring", "interview", "recruitment", "candidate"],
        "management": ["management", "manager", "leadership", "team"]
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            topics.append(topic)

    return topics if topics else ["general"]

def show_conversation_analytics():
    """Display conversation analytics dashboard"""
    if not st.session_state.chat_history:
        st.info("Start a conversation to see analytics!")
        return

    st.markdown("### 📊 Conversation Analytics")

    # Basic metrics
    total_messages = len(st.session_state.chat_history)
    user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])

    # Ensure topics_discussed is a set
    if not isinstance(st.session_state.conversation_stats['topics_discussed'], set):
        st.session_state.conversation_stats['topics_discussed'] = set(st.session_state.conversation_stats['topics_discussed'])

    topics_discussed = list(st.session_state.conversation_stats['topics_discussed'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("Your Questions", user_messages)
    with col3:
        st.metric("Topics Explored", len(topics_discussed))

    # Topics breakdown
    if topics_discussed:
        st.markdown("**🏷️ Topics Discussed:**")
        topic_cols = st.columns(min(len(topics_discussed), 4))
        for i, topic in enumerate(topics_discussed):
            with topic_cols[i % len(topic_cols)]:
                st.button(f"#{topic}", disabled=True, key=f"topic_tag_{i}")

    # Confidence distribution
    assistant_messages = [m for m in st.session_state.chat_history if m["role"] == "assistant"]
    if assistant_messages:
        confidence_levels = [m.get('confidence_level', 'Medium') for m in assistant_messages]
        confidence_counts = {level: confidence_levels.count(level) for level in ['High', 'Medium', 'Low']}

        st.markdown("**🎯 Response Confidence Distribution:**")
        conf_col1, conf_col2, conf_col3 = st.columns(3)
        with conf_col1:
            st.metric("🎯 High", confidence_counts.get('High', 0))
        with conf_col2:
            st.metric("⚖️ Medium", confidence_counts.get('Medium', 0))
        with conf_col3:
            st.metric("⚠️ Low", confidence_counts.get('Low', 0))

def export_conversation():
    """Enhanced conversation export with analytics"""
    if not st.session_state.chat_history:
        st.warning("No conversation to export!")
        return

    # Ensure topics_discussed is a set and convert to list for serialization
    if not isinstance(st.session_state.conversation_stats['topics_discussed'], set):
        st.session_state.conversation_stats['topics_discussed'] = set(st.session_state.conversation_stats['topics_discussed'])

    # Prepare comprehensive export data
    export_data = {
        "metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "total_messages": len(st.session_state.chat_history),
            "user_messages": len([m for m in st.session_state.chat_history if m["role"] == "user"]),
            "topics_discussed": list(st.session_state.conversation_stats['topics_discussed']),
            "export_version": "2.0"
        },
        "conversation": st.session_state.chat_history,
        "analytics": {
            "total_queries": st.session_state.conversation_stats['total_queries'],
            "topics_discussed": list(st.session_state.conversation_stats['topics_discussed'])
        },
        "settings": {
            "show_sources": st.session_state.show_sources,
            "show_confidence": st.session_state.show_confidence,
            "show_followups": st.session_state.show_followups
        }
    }

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Export as JSON",
            data=json_str,
            file_name=f"gitlab_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            help="Complete conversation with metadata and analytics"
        )

    with col2:
        # Create a simplified text version
        text_export = create_text_export(st.session_state.chat_history)
        st.download_button(
            label="📝 Export as Text",
            data=text_export,
            file_name=f"gitlab_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            help="Simplified text version for easy reading"
        )

def create_text_export(chat_history: List[Dict]) -> str:
    """Create a readable text export of the conversation"""
    lines = [
        "GitLab GenAI Chatbot Conversation Export",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        ""
    ]

    for i, message in enumerate(chat_history, 1):
        role = "You" if message["role"] == "user" else "GitLab Assistant"
        timestamp = message.get("timestamp", "")

        lines.append(f"[{i}] {role} {timestamp}")
        lines.append("-" * 30)
        lines.append(message["content"])

        # Add sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            lines.append("\nSources:")
            for source in message["sources"]:
                lines.append(f"- {source['title']}: {source['url']}")

        lines.append("")

    return "\n".join(lines)

def show_enhanced_sidebar():
    """Enhanced sidebar with all controls"""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")

        # API Key Management
        st.markdown("### 🔑 API Key Setup")
        session_key_available = st.session_state.custom_api_key != ""

        if session_key_available:
            st.success("✅ API Key Set")
            if st.button("🔄 Change API Key"):
                st.session_state.custom_api_key = ""
                st.session_state.model = None
                st.session_state.api_key_set = False
                st.rerun()
        else:
            st.info("📝 Please enter your Google AI API Key")
            with st.form(key="api_key_form"):
                api_key_input = st.text_input(
                    "Enter Google AI API Key:",
                    type="password",
                    placeholder="AIza...",
                    help="Get your free API key from https://aistudio.google.com"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("🔑 Set Key", type="primary") and api_key_input:
                        st.session_state.custom_api_key = api_key_input
                        st.success("API key set!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🧪 Test Key") and api_key_input:
                        with st.spinner("Testing..."):
                            success, message = initialize_ai(api_key_input)
                            if success:
                                st.success("✅ Valid!")
                                st.session_state.custom_api_key = api_key_input
                            else:
                                st.error(f"❌ {message}")

        # AI Initialization
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
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.session_state.conversation_stats = {'total_queries': 0, 'topics_discussed': set()}
                    st.success("Chat cleared!")
                    st.rerun()
            with col2:
                if st.button("🔄 Reset AI"):
                    st.session_state.model = None
                    st.session_state.api_key_set = False
                    st.rerun()

        # Display Settings
        st.markdown("### ⚙️ Display Settings")
        st.session_state.show_sources = st.checkbox("📚 Show Sources", value=st.session_state.show_sources)
        st.session_state.show_confidence = st.checkbox("🎯 Show Confidence", value=st.session_state.show_confidence)
        st.session_state.show_followups = st.checkbox("💡 Show Follow-ups", value=st.session_state.show_followups)

        # Knowledge Base Management
        st.markdown("### 📖 Knowledge Base")
        gitlab_service = get_gitlab_service()

        # Check if update is needed
        if gitlab_service.should_update():
            st.markdown("""
            <div class="update-banner">
                🔄 Knowledge base can be updated
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Update from GitLab"):
            gitlab_service.update_knowledge_base_from_web()

        # Show last update info
        last_update = gitlab_service.get_last_update()
        days_since_update = (datetime.now() - last_update).days
        st.markdown(f"**Last Updated:** {days_since_update} days ago")

        # System Status
        st.markdown("### 📊 System Status")
        st.markdown(f"**API Source:** {'Custom' if session_key_available else 'None'}")
        st.markdown("**Model:** Gemini 1.5 Flash")
        st.markdown(f"**Status:** {'✅ Ready' if st.session_state.model else '❌ Not Ready'}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")

        # Export Options
        if st.session_state.chat_history:
            st.markdown("### 💾 Export Options")
            export_conversation()

        # Quick Analytics
        if st.session_state.chat_history:
            st.markdown("### 📈 Quick Stats")
            topics = list(st.session_state.conversation_stats['topics_discussed'])
            if topics:
                st.markdown("**Top Topics:**")
                for topic in topics[:3]:
                    st.markdown(f"• {topic}")

def show_topic_explorer():
    """Interactive topic explorer"""
    st.markdown("### 🗺️ Explore GitLab Topics")

    topic_categories = {
        "🏢 Culture & Values": {
            "topics": ["culture", "values", "transparency", "collaboration"],
            "description": "Learn about GitLab's core values and culture"
        },
        "👥 People Operations": {
            "topics": ["onboarding", "performance", "hiring", "development"],
            "description": "Understand GitLab's people practices"
        },
        "🛠️ Product & Engineering": {
            "topics": ["product strategy", "development process", "security"],
            "description": "Explore GitLab's product and technical approach"
        },
        "💼 Business Operations": {
            "topics": ["sales process", "marketing", "customer success"],
            "description": "Discover GitLab's business operations"
        }
    }

    for category, info in topic_categories.items():
        with st.expander(f"{category} - {info['description']}"):
            topic_cols = st.columns(2)
            for i, topic in enumerate(info['topics']):
                with topic_cols[i % 2]:
                    if st.button(f"💡 Learn about {topic}", key=f"explore_{topic}"):
                        query = f"Tell me about GitLab's approach to {topic}"
                        process_user_query(query)

def main():
    """Enhanced main application function"""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🚀 GitLab GenAI Chatbot - Enhanced</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="subheader">
        Ask questions about GitLab's culture, processes, and practices with enhanced AI features.
    </div>
    """, unsafe_allow_html=True)

    # Show enhanced sidebar
    show_enhanced_sidebar()

    # Main content area
    if st.session_state.model:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "🗺️ Explore"])

        with tab1:
            # Display enhanced chat history
            display_enhanced_chat_history()

            # Chat input section
            st.markdown("### 💭 Ask a Question")
            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_area(
                    "Type your question about GitLab:",
                    height=100,
                    placeholder="e.g., How does GitLab handle remote team collaboration?",
                    key="user_input"
                )

                col1, col2 = st.columns([1, 4])
                with col1:
                    send_button = st.form_submit_button("📤 Send", type="primary")

                # Process message when form is submitted
                if send_button and user_input.strip():
                    process_user_query(user_input.strip())

            # Example questions based on context
            st.markdown("### 💡 Suggested Questions")
            if len(st.session_state.chat_history) == 0:
                # Initial suggestions
                examples = [
                    "What makes GitLab's culture unique?",
                    "How does GitLab's onboarding process work?",
                    "What are GitLab's core values?",
                    "How does GitLab approach remote work?",
                    "What is GitLab's product strategy?"
                ]
            else:
                # Context-aware suggestions
                examples = [
                    "Can you elaborate on that?",
                    "What are the practical benefits?",
                    "How does this compare to other companies?",
                    "What challenges might arise?",
                    "Are there specific examples?"
                ]

            # Display example questions in columns
            example_cols = st.columns(2)
            for i, example in enumerate(examples):
                with example_cols[i % 2]:
                    if st.button(f"❓ {example}", key=f"example_{i}"):
                        process_user_query(example)

        with tab2:
            # Analytics dashboard
            show_conversation_analytics()

        with tab3:
            # Topic explorer
            show_topic_explorer()

        # Show conversation tips
        if len(st.session_state.chat_history) > 0:
            st.markdown("""
            <div class="notice tip">
                <h4>💡 Pro Tips</h4>
                <ul>
                    <li><strong>Follow-up:</strong> Ask "Can you tell me more?" for deeper insights</li>
                    <li><strong>Compare:</strong> "How does this compare to traditional approaches?"</li>
                    <li><strong>Examples:</strong> "Can you give me a specific example?"</li>
                    <li><strong>Practical:</strong> "How would this work in practice?"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Welcome screen for non-initialized users
        session_key_available = st.session_state.custom_api_key != ""

        if not session_key_available:
            st.markdown("""
            <div class="notice info center">
                <h3 style="margin-bottom: 1rem; color: #FC6D26;">🔑 Enhanced GitLab GenAI Chatbot</h3>
                <p style="font-size: 1.1rem; margin-bottom: 1rem;">Experience advanced AI features with transparency and analytics!</p>
                <div style="background: rgba(252, 109, 38, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <p style="margin: 0; font-weight: bold;">✨ New Features:</p>
                </div>
                <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 0.5rem; margin: 1rem 0;">
                        <span>🎯</span><span>Confidence indicators for response quality</span>
                        <span>📚</span><span>Source attribution with relevance scores</span>
                        <span>💡</span><span>Smart follow-up question suggestions</span>
                        <span>📊</span><span>Conversation analytics and insights</span>
                        <span>🗺️</span><span>Interactive topic exploration</span>
                        <span>💾</span><span>Enhanced conversation export options</span>
                    </div>
                </div>
                <div style="background: rgba(66, 133, 244, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                    <p style="margin: 0; font-weight: bold;">🚀 Get Started:</p>
                    <p style="margin: 0.5rem 0 0 0;">Add your Google AI API key in the sidebar!</p>
                    <p style="margin: 0.5rem 0 0 0; font-style: italic; opacity: 0.8;">Free tier: 1,500 API calls per day</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="notice tip center">
                <h3 style="margin-bottom: 1rem; color: #059669;">🚀 Ready to Launch!</h3>
                <p style="font-size: 1.1rem; margin-bottom: 1rem;">Click "Initialize AI" in the sidebar to start chatting with enhanced features.</p>
                <div style="background: rgba(5, 150, 105, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <p style="margin: 0; font-weight: bold;">🎁 You'll get:</p>
                    <p style="margin: 0.5rem 0 0 0;">Smart responses, source tracking, follow-up suggestions, and analytics!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()