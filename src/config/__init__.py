"""
Configuration Module
====================

Handles all settings and configurations:
- settings.py: Environment variables and runtime settings
- agents.yaml: Agent prompts and behavior configurations
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
