"""
Settings Configuration
======================

This module handles all environment variables and configuration settings.

HOW IT WORKS:
-------------
1. Loads from .env file (if exists)
2. Falls back to environment variables
3. Uses defaults for optional settings

REQUIRED SETTINGS:
------------------
- GOOGLE_CLOUD_PROJECT: Your Google Cloud project ID
  Example: "csnavigator-vertex-ai"

OPTIONAL SETTINGS:
------------------
- VERTEX_AI_LOCATION: Where to run Vertex AI (default: us-central1)
- VERTEX_AI_MODEL: Which model to use (default: gemini-1.5-pro)
- LOG_LEVEL: Logging verbosity (default: INFO)

AUTHENTICATION:
---------------
The system uses Google Application Default Credentials.
Run: gcloud auth application-default login
This creates credentials at: ~/.config/gcloud/application_default_credentials.json

For production, use a service account:
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic-settings automatically:
    1. Reads from .env file
    2. Reads from environment variables
    3. Validates types
    4. Provides defaults

    Example usage:
        settings = get_settings()
        print(settings.google_cloud_project)
    """

    # =========================================================================
    # GOOGLE CLOUD SETTINGS
    # =========================================================================

    google_cloud_project: str = Field(
        default="",
        description="Your Google Cloud project ID. Find it at console.cloud.google.com"
    )

    vertex_ai_location: str = Field(
        default="us-central1",
        description="Google Cloud region for Vertex AI. us-central1 has best availability."
    )

    vertex_ai_model: str = Field(
        default="gemini-1.5-pro",
        description="Which Gemini model to use. Options: gemini-1.5-pro, gemini-1.5-flash"
    )

    # =========================================================================
    # OAUTH SETTINGS (for Gmail/Calendar)
    # =========================================================================

    oauth_credentials_path: Path = Field(
        default=Path("credentials/oauth.json"),
        description="Path to OAuth 2.0 client credentials JSON (downloaded from GCP console)"
    )

    oauth_token_path: Path = Field(
        default=Path("credentials/token.json"),
        description="Path where OAuth tokens are stored after user consent"
    )

    # =========================================================================
    # MCP SETTINGS
    # =========================================================================

    mcp_gmail_enabled: bool = Field(
        default=True,
        description="Enable Gmail MCP tools"
    )

    mcp_calendar_enabled: bool = Field(
        default=True,
        description="Enable Calendar MCP tools"
    )

    # =========================================================================
    # AGENT SETTINGS
    # =========================================================================

    agent_config_path: Path = Field(
        default=Path("src/config/agents.yaml"),
        description="Path to YAML file with agent configurations"
    )

    max_parallel_agents: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Maximum number of agents to run in parallel"
    )

    agent_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for each agent response"
    )

    # =========================================================================
    # LOGGING SETTINGS
    # =========================================================================

    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )

    # =========================================================================
    # PATHS
    # =========================================================================

    data_dir: Path = Field(
        default=Path("data"),
        description="Directory containing knowledge base JSON files"
    )

    # =========================================================================
    # PYDANTIC CONFIGURATION
    # =========================================================================

    model_config = SettingsConfigDict(
        # Load from .env file if it exists
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra fields (future-proofing)
        extra="ignore",
        # Case-insensitive environment variables
        case_sensitive=False,
    )

    def validate_google_cloud(self) -> bool:
        """
        Check if Google Cloud is properly configured.

        Returns:
            True if configured, raises ValueError if not
        """
        if not self.google_cloud_project:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT is not set!\n"
                "Set it in .env file or environment variable.\n"
                "Find your project ID at: https://console.cloud.google.com"
            )
        return True

    def validate_oauth(self) -> bool:
        """
        Check if OAuth credentials exist.

        Returns:
            True if credentials exist, False otherwise
        """
        if not self.oauth_credentials_path.exists():
            print(
                f"OAuth credentials not found at: {self.oauth_credentials_path}\n"
                "Download from: Google Cloud Console → APIs & Services → Credentials\n"
                "Create an OAuth 2.0 Client ID (Desktop application)"
            )
            return False
        return True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using @lru_cache means settings are only loaded once,
    then reused for all subsequent calls.

    Returns:
        Settings instance with all configuration values
    """
    return Settings()


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def get_project_root() -> Path:
    """Get the project root directory."""
    # This file is at: src/config/settings.py
    # Project root is 3 levels up
    return Path(__file__).parent.parent.parent


def ensure_directories():
    """Create required directories if they don't exist."""
    settings = get_settings()

    directories = [
        settings.data_dir,
        settings.oauth_credentials_path.parent,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
