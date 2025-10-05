"""Configuration management for the Perplexity Clone application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")  # Default model

    # SerpAPI Configuration
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")

    # Supabase Configuration (for future caching implementation)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tfvenxrnmdxbbnvidaut.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Search Configuration
    MIN_SEARCH_RESULTS = 5
    MAX_SEARCH_RESULTS = 10

    # Agent Configuration
    NUM_AGENTS = 3

    # LLM Configuration
    MIN_MAX_TOKENS = 20  # Minimum max_tokens for OpenRouter (some models require >= 16)

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        missing = []

        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        if not cls.SERPAPI_KEY:
            missing.append("SERPAPI_KEY")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file."
            )
