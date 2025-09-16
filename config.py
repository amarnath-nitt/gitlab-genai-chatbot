"""
Configuration module for the GitLab GenAI Chatbot.
Follows the Single Responsibility Principle by centralizing all configuration.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic for validation."""
    
    # Google AI Configuration
    google_api_key: str = "your_google_api_key_here"
    
    # GitLab URLs
    gitlab_handbook_url: str = "https://handbook.gitlab.com"
    gitlab_direction_url: str = "https://about.gitlab.com/direction"
    
    # Application Configuration
    chroma_persist_directory: str = "./chroma_db"
    max_context_length: int = 4000
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields instead of raising error


# Global settings instance
settings = Settings()
