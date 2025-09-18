# 🚀 GitLab GenAI Chatbot - Enhanced Edition

An advanced AI-powered chatbot that answers questions from GitLab's Handbook and Direction pages, featuring transparency, analytics, and smart follow-up capabilities.

## ✨ Features

### 🤖 Core AI Capabilities
- **Smart Response Generation** using Google's Gemini 1.5 Flash
- **Context-Aware Conversations** with memory across interactions
- **Relevance Scoring** for content matching and response quality

### 🛡️ Transparency & Trust
- **Confidence Indicators** showing response reliability (High/Medium/Low)
- **Source Attribution** with relevance scores and last-updated timestamps
- **Response Provenance** showing exactly which GitLab pages informed each answer

### 💡 Enhanced User Experience
- **Smart Follow-up Questions** generated based on conversation context
- **Interactive Topic Explorer** for discovering GitLab information
- **Conversation Analytics** tracking topics discussed and response confidence
- **Multiple Export Formats** (JSON, TXT) for saving conversations

### 📊 Analytics & Insights
- **Real-time Conversation Stats** showing message counts and topic coverage
- **Confidence Distribution** tracking response quality over time
- **Topic Clustering** identifying most discussed GitLab areas
- **Usage Patterns** helping understand user information needs

### 🔄 Dynamic Content Management
- **Hybrid Knowledge Base** with curated content and web scraping capabilities
- **Smart Update Detection** notifying when GitLab content may have changed
- **Manual Refresh Options** for getting latest information
- **Content Freshness Indicators** showing when sources were last updated

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS and responsive design
- **AI Model**: Google Gemini 1.5 Flash via Google AI Studio
- **Web Scraping**: BeautifulSoup4 for GitLab content extraction
- **Configuration**: Pydantic Settings for robust configuration management
- **Data Processing**: Advanced text processing and relevance scoring

## 📋 Prerequisites

- Python 3.8 or higher
- Google AI Studio API key (free tier: 1,500 requests/day)
- Internet connection for GitLab content updates

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd gitlab-genai-chatbot
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your Google AI API key
```

### 3. Run the Application
```bash
streamlit run enhanced_app.py
```

### 4. Access the Chatbot
Open your browser to `http://localhost:8501`

## 🔧 Configuration Options

### Environment Variables
Create a `.env` file with your settings:

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional Advanced Settings
ENABLE_WEB_SCRAPING=true
UPDATE_INTERVAL_DAYS=7
MAX_SOURCES_PER_RESPONSE=3
DEFAULT_SHOW_CONFIDENCE=true
```

### UI Settings
Configure display options in the sidebar:
- **Show Sources**: Display GitLab handbook sources for each response
- **Show Confidence**: Show AI confidence levels for transparency
- **Show Follow-ups**: Enable smart follow-up question suggestions

## 📚 Knowledge Base

### Default Topics Covered
- **Onboarding**: New hire processes, welcome procedures, training
- **Culture & Values**: GitLab's CREDIT values, transparency, collaboration
- **Remote Work**: Distributed team practices, async communication
- **Performance Management**: Reviews, feedback, career development
- **Product Strategy**: DevOps platform vision, roadmap, direction

### Content Sources
- GitLab Handbook (handbook.gitlab.com)
- GitLab Direction Pages (about.gitlab.com/direction)
- Curated knowledge base with confidence scoring
- Optional web scraping for real-time updates

## 🎯 Advanced Features

### Confidence Scoring System
- **High (🎯)**: Response based on highly relevant, recent sources
- **Medium (⚖️)**: Good source match with moderate relevance
- **Low (⚠️)**: Limited source material or low relevance match

### Smart Follow-up Generation
The system analyzes each response to suggest contextually relevant follow-up questions:
- Deeper exploration of the topic
- Practical implementation questions
- Comparative analysis requests
- Example and case study queries

### Conversation Analytics
Track your learning journey with:
- Message count and topic distribution
- Confidence score trends
- Most explored GitLab areas
- Conversation export for future reference

### Topic Explorer
Interactive discovery of GitLab information organized by:
- 🏢 Culture & Values
- 👥 People Operations
- 🛠️ Product & Engineering
- 💼 Business Operations

## 🔄 Content Update System

### Automatic Updates
- Weekly freshness checks for GitLab content
- Smart detection of outdated information
- Background updates without interrupting conversations

### Manual Updates
- One-click refresh from GitLab pages
- Real-time content fetching
- Update status notifications

## 📊 Export & Analytics

### Conversation Export Options
- **JSON Format**: Complete conversation with metadata, sources, and analytics
- **Text Format**: Clean, readable conversation transcript
- **Analytics Data**: Usage statistics and topic analysis

### Data Included
- Full conversation history with timestamps
- Source attribution for each response
- Confidence levels and relevance scores
- Topics discussed and learning patterns
- Export metadata and version information

## 🚀 Deployment

### Streamlit Community Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Community Cloud
3. Add `GOOGLE_API_KEY` to secrets
4. Deploy with one click

### Hugging Face Spaces
1. Create new Streamlit Space
2. Upload project files
3. Configure secrets in Space settings
4. Application auto-deploys

### Local Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug mode
streamlit run enhanced_app.py --server.runOnSave true

# Access at http://localhost:8501
```

## 🧪 Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific components
python -m pytest tests/test_app.py -v

# Test with coverage
python -m pytest --cov=. tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📈 Roadmap

### Upcoming Features
- **Multi-language Support** for global GitLab teams
- **Voice Interface** for hands-free interaction
- **GitLab API Integration** for real-time project data
- **Slack/Teams Bot** for workflow integration
- **Advanced Search** with semantic similarity
- **Custom Knowledge Base** for team-specific content

### Performance Improvements
- **Response Caching** for faster repeated queries
- **Streaming Responses** for real-time feedback
- **Batch Processing** for multiple questions
- **Offline Mode** with cached knowledge base


## 🙏 Acknowledgments

- GitLab for their commitment to transparency and open collaboration
- Google AI Studio for providing accessible AI capabilities
- Streamlit for the excellent web framework
- The open source community for inspiration and tools

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Join GitHub Discussions for questions and ideas
- **Documentation**: Check the wiki for detailed guides
- **Community**: Connect with other users and contributors

---

**Built with ❤️ to showcase GitLab's transparency and collaboration values**

*This project demonstrates advanced RAG (Retrieval-Augmented Generation) techniques, transparency in AI systems, and user-centered design for enterprise AI applications.*