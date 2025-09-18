"""
Enhanced Configuration module for the GitLab GenAI Chatbot.
Includes settings for new features like analytics, caching, and updates.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Enhanced application settings using Pydantic for validation."""

    # Google AI Configuration
    google_api_key: str = "your_google_api_key_here"

    # GitLab URLs
    gitlab_handbook_url: str = "https://handbook.gitlab.com"
    gitlab_direction_url: str = "https://about.gitlab.com/direction"
    gitlab_api_base_url: str = "https://gitlab.com/api/v4"

    # Application Configuration
    chroma_persist_directory: str = "./chroma_db"
    max_context_length: int = 4000
    max_chunk_size: int = 1000
    chunk_overlap: int = 200

    # Enhanced Features Configuration
    enable_web_scraping: bool = True
    update_interval_days: int = 7
    max_sources_per_response: int = 3
    confidence_threshold_high: float = 0.8
    confidence_threshold_medium: float = 0.6

    # Analytics Configuration
    enable_analytics: bool = True
    max_chat_history: int = 100
    export_formats: List[str] = ["json", "txt", "csv"]

    # Performance Configuration
    request_timeout: int = 10
    max_retry_attempts: int = 3
    cache_ttl_seconds: int = 3600  # 1 hour

    # UI Configuration
    default_show_sources: bool = True
    default_show_confidence: bool = True
    default_show_followups: bool = True
    max_followup_questions: int = 3

    # Security Configuration
    allowed_domains: List[str] = [
        "handbook.gitlab.com",
        "about.gitlab.com",
        "docs.gitlab.com"
    ]
    user_agent: str = "GitLab GenAI Chatbot (Educational Purpose)"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()