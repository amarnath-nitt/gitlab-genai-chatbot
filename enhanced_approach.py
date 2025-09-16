"""
Enhanced Approach: Hybrid Knowledge Base + Dynamic Updates

This shows how we could combine the benefits of both approaches:
1. Fast responses from knowledge_base
2. Periodic updates from GitLab pages
3. Fallback to web scraping for missing information
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class EnhancedGitLabService:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.last_update = self.get_last_update()
        self.update_interval = timedelta(days=7)  # Update weekly
        
    def load_knowledge_base(self) -> Dict:
        """Load knowledge base from file or use default"""
        try:
            with open('gitlab_knowledge.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_knowledge_base()
    
    def get_default_knowledge_base(self) -> Dict:
        """Default knowledge base (current implementation)"""
        return {
            "onboarding": {
                "content": "GitLab's onboarding process...",
                "source": "https://handbook.gitlab.com/handbook/people-group/general-onboarding/",
                "last_updated": datetime.now().isoformat()
            },
            # ... other entries
        }
    
    def get_last_update(self) -> datetime:
        """Get when knowledge base was last updated"""
        try:
            with open('last_update.txt', 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except FileNotFoundError:
            return datetime.now() - timedelta(days=30)  # Force update
    
    def should_update(self) -> bool:
        """Check if knowledge base needs updating"""
        return datetime.now() - self.last_update > self.update_interval
    
    def update_knowledge_base(self):
        """Update knowledge base from GitLab pages"""
        print("🔄 Updating knowledge base from GitLab pages...")
        
        # URLs to scrape
        urls = {
            "onboarding": "https://handbook.gitlab.com/handbook/people-group/general-onboarding/",
            "culture": "https://handbook.gitlab.com/handbook/values/",
            "remote_work": "https://handbook.gitlab.com/company/culture/all-remote/",
            "performance": "https://handbook.gitlab.com/handbook/people-group/performance-and-development/",
            "product_strategy": "https://about.gitlab.com/direction/"
        }
        
        updated_data = {}
        for key, url in urls.items():
            try:
                content = self.scrape_gitlab_page(url)
                updated_data[key] = {
                    "content": content,
                    "source": url,
                    "last_updated": datetime.now().isoformat()
                }
                print(f"✅ Updated {key}")
            except Exception as e:
                print(f"❌ Failed to update {key}: {e}")
                # Keep existing data if update fails
                updated_data[key] = self.knowledge_base.get(key, {})
        
        # Save updated knowledge base
        self.knowledge_base = updated_data
        self.save_knowledge_base()
        self.save_last_update()
        print("✅ Knowledge base updated successfully!")
    
    def scrape_gitlab_page(self, url: str) -> str:
        """Scrape content from a GitLab page"""
        headers = {
            'User-Agent': 'GitLab GenAI Chatbot (Educational Purpose)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content (adjust selectors as needed)
        content_selectors = [
            'main', '.content', '.handbook-content', 
            '.markdown-body', 'article'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text(strip=True)
                break
        
        # Clean up content
        content = content[:2000]  # Limit length
        return content
    
    def save_knowledge_base(self):
        """Save knowledge base to file"""
        with open('gitlab_knowledge.json', 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def save_last_update(self):
        """Save last update timestamp"""
        with open('last_update.txt', 'w') as f:
            f.write(datetime.now().isoformat())
    
    def get_content_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant content for a query"""
        # Check if we need to update
        if self.should_update():
            self.update_knowledge_base()
        
        # Use existing logic to find relevant content
        query_lower = query.lower()
        relevant_content = []
        
        for key, data in self.knowledge_base.items():
            if any(word in query_lower for word in key.split()):
                relevant_content.append(data)
        
        return relevant_content[:3]

# Usage in app.py:
def get_gitlab_content(query: str) -> List[Dict[str, Any]]:
    """Enhanced version with dynamic updates"""
    service = EnhancedGitLabService()
    return service.get_content_for_query(query)

"""
Benefits of this hybrid approach:

1. ⚡ Fast Responses: Uses cached knowledge base
2. 🔄 Always Updated: Automatically updates from GitLab pages
3. 🛡️ Fallback Protection: Keeps existing data if update fails
4. 📊 Transparent: Shows when data was last updated
5. 🎯 Smart Updates: Only updates when needed (weekly)
6. 💾 Persistent: Saves data between app restarts

This gives you the best of both worlds!
"""

