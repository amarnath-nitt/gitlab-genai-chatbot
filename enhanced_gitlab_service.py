"""
Enhanced GitLab Service with Dynamic Updates and Smart Features
"""
import requests
from bs4 import BeautifulSoup
import json
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class EnhancedGitLabService:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.last_update = self.get_last_update()
        self.update_interval = timedelta(days=7)  # Update weekly

    def load_knowledge_base(self) -> Dict:
        """Load knowledge base from session state or use default"""
        if 'gitlab_knowledge_base' in st.session_state:
            return st.session_state.gitlab_knowledge_base

        default_kb = self.get_default_knowledge_base()
        st.session_state.gitlab_knowledge_base = default_kb
        return default_kb

    def get_default_knowledge_base(self) -> Dict:
        """Enhanced default knowledge base with metadata"""
        return {
            "onboarding": {
                "content": """
                GitLab's onboarding process for new team members includes:
                1. Welcome call with People Operations team
                2. Complete access to GitLab Handbook for self-paced learning
                3. Introduction to immediate team and key cross-functional stakeholders
                4. Technical setup including tool access and security training
                5. Structured 30-60-90 day check-ins with direct manager
                6. Buddy system pairing with experienced team member
                7. Comprehensive culture and values training sessions
                8. Security awareness and compliance training modules
                9. Product overview and company strategy sessions
                10. Continuous feedback loops and onboarding experience optimization
                """,
                "source": "https://handbook.gitlab.com/handbook/people-group/general-onboarding/",
                "last_updated": datetime.now().isoformat(),
                "confidence": 0.9,
                "keywords": ["onboarding", "new hire", "welcome", "training", "setup"]
            },
            "culture": {
                "content": """
                GitLab's company culture is built on transparency and collaboration:
                - Transparency: All company information is public by default, fostering trust
                - Collaboration: Cross-functional teamwork and open communication
                - Remote-first: Fully distributed team with asynchronous work culture
                - Iteration: Continuous improvement in small, measurable steps
                - Results-oriented: Focus on outcomes rather than hours worked
                - Efficiency: Work smarter through automation and clear processes
                - Diversity & Inclusion: Creating welcoming environment for everyone
                - Asynchronous communication to respect global time zones
                - Strong emphasis on work-life balance and mental health
                - Building in public philosophy with transparent decision-making
                """,
                "source": "https://handbook.gitlab.com/handbook/values/",
                "last_updated": datetime.now().isoformat(),
                "confidence": 0.95,
                "keywords": ["culture", "values", "transparency", "collaboration", "remote"]
            },
            "remote_work": {
                "content": """
                GitLab's remote work philosophy and practices:
                - Fully remote company since 2011 with no physical offices
                - Asynchronous communication is preferred over real-time meetings
                - Flexible working hours respecting personal schedules and time zones
                - Global team spanning multiple continents and cultures
                - Comprehensive toolstack: GitLab, Slack, Zoom, Google Workspace
                - Regular structured team meetings and individual one-on-ones
                - Documentation-first approach to knowledge sharing
                - Strong emphasis on work-life balance and mental health support
                - Remote-friendly processes for hiring, onboarding, and collaboration
                - Continuous investment in remote work infrastructure and best practices
                """,
                "source": "https://handbook.gitlab.com/company/culture/all-remote/",
                "last_updated": datetime.now().isoformat(),
                "confidence": 0.92,
                "keywords": ["remote", "work from home", "distributed", "async", "flexible"]
            },
            "performance": {
                "content": """
                GitLab's performance management and development approach:
                - Quarterly performance review cycles with clear expectations
                - Comprehensive 360-degree feedback from peers, reports, and managers
                - Goal setting aligned with company objectives and individual growth
                - Regular career development discussions and advancement planning
                - Structured one-on-one meetings for ongoing feedback and support
                - Peer recognition programs and public acknowledgment systems
                - Performance improvement plans with clear metrics and timelines
                - Transparent promotion processes and career progression paths
                - Continuous learning culture with training stipends and resources
                - Manager training programs to support effective people leadership
                """,
                "source": "https://handbook.gitlab.com/handbook/people-group/performance-and-development/",
                "last_updated": datetime.now().isoformat(),
                "confidence": 0.88,
                "keywords": ["performance", "review", "feedback", "development", "promotion"]
            },
            "product_strategy": {
                "content": """
                GitLab's product strategy and vision:
                - Single DevOps platform consolidating the entire software development lifecycle
                - Strong commitment to open source community and contribution
                - Enterprise-grade security, compliance, and scalability features
                - Cloud-native solutions optimized for modern infrastructure
                - AI and machine learning integration for developer productivity
                - Focus on developer experience optimization and workflow efficiency
                - Strategic global market expansion and localization efforts
                - Customer success programs and comprehensive support offerings
                - Continuous innovation through R&D and community feedback
                - Platform scalability to serve enterprises of all sizes
                """,
                "source": "https://about.gitlab.com/direction/",
                "last_updated": datetime.now().isoformat(),
                "confidence": 0.85,
                "keywords": ["product", "strategy", "devops", "platform", "direction"]
            }
        }

    def get_last_update(self) -> datetime:
        """Get when knowledge base was last updated"""
        if 'last_knowledge_update' in st.session_state:
            return datetime.fromisoformat(st.session_state.last_knowledge_update)
        return datetime.now() - timedelta(days=30)  # Force initial update

    def should_update(self) -> bool:
        """Check if knowledge base needs updating"""
        return datetime.now() - self.last_update > self.update_interval

    def calculate_relevance_score(self, query: str, content_item: Dict) -> float:
        """Calculate how relevant a content item is to the query"""
        query_lower = query.lower()
        content_text = content_item['content'].lower()
        keywords = content_item.get('keywords', [])

        # Keyword matching score
        keyword_matches = sum(1 for keyword in keywords if keyword in query_lower)
        keyword_score = min(keyword_matches / len(keywords), 1.0) if keywords else 0

        # Content relevance score (simple word matching)
        query_words = set(query_lower.split())
        content_words = set(content_text.split())
        common_words = query_words.intersection(content_words)
        content_score = len(common_words) / max(len(query_words), 1)

        # Base confidence from content quality
        base_confidence = content_item.get('confidence', 0.5)

        # Combined score
        relevance = (keyword_score * 0.5 + content_score * 0.3 + base_confidence * 0.2)
        return min(relevance, 1.0)

    def get_content_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant content for a query with enhanced scoring"""
        # Check if we need to update (optional - can be triggered manually)
        update_available = self.should_update()

        # Calculate relevance scores for all content
        scored_content = []
        for key, data in self.knowledge_base.items():
            score = self.calculate_relevance_score(query, data)
            if score > 0.1:  # Only include somewhat relevant content
                content_with_score = data.copy()
                content_with_score['relevance_score'] = score
                content_with_score['topic'] = key
                scored_content.append(content_with_score)

        # Sort by relevance and return top 3
        scored_content.sort(key=lambda x: x['relevance_score'], reverse=True)

        # If no good matches, return default culture/values content
        if not scored_content:
            default_content = [
                self.knowledge_base.get('culture', {}),
                self.knowledge_base.get('values', {})
            ]
            for i, content in enumerate(default_content):
                if content:
                    content['relevance_score'] = 0.3
                    content['topic'] = 'culture' if i == 0 else 'values'
            return [c for c in default_content if c]

        return scored_content[:3]

    def generate_followup_questions(self, response: str, query: str, model) -> List[str]:
        """Generate contextual follow-up questions"""
        try:
            followup_prompt = f"""
            Based on this GitLab-related conversation:
            User asked: "{query}"
            Assistant responded: "{response[:300]}..."
            
            Generate 3 relevant follow-up questions that a GitLab employee or someone interested in GitLab might ask.
            Make the questions specific and practical.
            Return only the questions, one per line, without numbering.
            """

            followup_response = model.generate_content(followup_prompt)
            questions = [q.strip('- ').strip() for q in followup_response.text.split('\n') if q.strip()]
            return [q for q in questions if len(q) > 10][:3]  # Filter out short/empty questions

        except Exception as e:
            logger.error(f"Error generating follow-ups: {e}")
            return [
                "Can you tell me more about that?",
                "What are the practical benefits of this approach?",
                "How does this work in practice at GitLab?"
            ]

    def get_response_confidence(self, query: str, content_items: List[Dict]) -> Tuple[str, str]:
        """Determine response confidence based on content quality"""
        if not content_items:
            return "Low", "⚠️"

        avg_relevance = sum(item.get('relevance_score', 0) for item in content_items) / len(content_items)
        avg_confidence = sum(item.get('confidence', 0) for item in content_items) / len(content_items)

        combined_score = (avg_relevance + avg_confidence) / 2

        if combined_score > 0.8:
            return "High", "🎯"
        elif combined_score > 0.6:
            return "Medium", "⚖️"
        else:
            return "Low", "⚠️"

    def update_knowledge_base_from_web(self) -> bool:
        """Update knowledge base from GitLab pages (optional feature)"""
        try:
            st.info("🔄 Updating knowledge base from GitLab pages...")

            # URLs to scrape
            urls = {
                "onboarding": "https://handbook.gitlab.com/handbook/people-group/general-onboarding/",
                "culture": "https://handbook.gitlab.com/handbook/values/",
                "remote_work": "https://handbook.gitlab.com/company/culture/all-remote/",
                "performance": "https://handbook.gitlab.com/handbook/people-group/performance-and-development/"
            }

            updated_items = 0
            for key, url in urls.items():
                try:
                    with st.spinner(f"Updating {key}..."):
                        content = self.scrape_gitlab_page(url)
                        if content and len(content) > 100:  # Valid content
                            # Update existing entry
                            if key in self.knowledge_base:
                                old_content = self.knowledge_base[key]
                                self.knowledge_base[key].update({
                                    'content': content,
                                    'last_updated': datetime.now().isoformat(),
                                    'confidence': old_content.get('confidence', 0.8)
                                })
                                updated_items += 1
                            st.success(f"✅ Updated {key}")
                        else:
                            st.warning(f"⚠️ Could not update {key} - content too short")

                except Exception as e:
                    st.error(f"❌ Failed to update {key}: {str(e)}")
                    continue

            # Save updated knowledge base
            st.session_state.gitlab_knowledge_base = self.knowledge_base
            st.session_state.last_knowledge_update = datetime.now().isoformat()

            if updated_items > 0:
                st.success(f"✅ Successfully updated {updated_items} knowledge base entries!")
                return True
            else:
                st.warning("⚠️ No entries were updated")
                return False

        except Exception as e:
            st.error(f"❌ Error updating knowledge base: {str(e)}")
            return False

    def scrape_gitlab_page(self, url: str) -> Optional[str]:
        """Scrape content from a GitLab page"""
        headers = {
            'User-Agent': 'GitLab GenAI Chatbot (Educational Purpose)'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()

            # Extract main content
            content_selectors = [
                'main', '.content', '.handbook-content',
                '.markdown-body', 'article', '.post-content'
            ]

            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True, separator=' ')
                    break

            # If no structured content found, get body text
            if not content:
                content = soup.get_text(strip=True, separator=' ')

            # Clean and limit content
            content = ' '.join(content.split())  # Normalize whitespace
            return content[:3000] if content else None  # Limit to 3000 chars

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

# Global service instance
@st.cache_resource
def get_gitlab_service():
    """Get or create the GitLab service instance"""
    return EnhancedGitLabService()