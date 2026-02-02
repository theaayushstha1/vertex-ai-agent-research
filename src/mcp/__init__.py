"""
MCP (Model Context Protocol) Module
===================================

MCP is Anthropic's standard for how AI agents interact with external tools.
Think of it like a "plugin system" for AI - agents can safely use tools
without knowing the implementation details.

This module provides:
- GmailMCPServer: Send emails, create drafts, search inbox
- CalendarMCPServer: Create events, check availability, set reminders

Why MCP instead of direct API calls?
1. Standardized interface - agents don't need to know Gmail API specifics
2. Security - tools run in isolated processes
3. Composable - easy to add new tools without changing agent code
4. Ecosystem - growing library of pre-built MCP servers
"""

from .gmail_server import GmailMCPServer
from .calendar_server import CalendarMCPServer

__all__ = ["GmailMCPServer", "CalendarMCPServer"]
