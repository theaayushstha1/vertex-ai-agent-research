"""
Gmail MCP Server
================

MCP (Model Context Protocol) server that provides Gmail tools to AI agents.

WHAT IS MCP?
------------
MCP is a protocol from Anthropic that standardizes how AI agents interact
with external tools. Instead of each AI having its own way to call APIs,
MCP provides a common interface.

Think of it like USB for AI tools - any AI can use any MCP tool.

HOW THIS WORKS:
--------------
1. This server runs as a separate process
2. The AI agent connects to it via MCP protocol
3. Agent calls tools like "draft_email" or "send_email"
4. Server executes the Gmail API calls
5. Returns results to the agent

TOOLS PROVIDED:
--------------
- draft_email: Create a draft (doesn't send yet)
- send_email: Send a draft or send directly
- search_inbox: Search your inbox
- get_email: Read a specific email
- list_labels: List Gmail labels/folders

AUTHENTICATION:
--------------
Uses OAuth 2.0 - you'll need to:
1. Create OAuth credentials in Google Cloud Console
2. Run the auth flow once (opens browser)
3. Credentials are saved for future use

WHY MCP INSTEAD OF DIRECT API CALLS?
-----------------------------------
1. Standardized - same interface for any AI
2. Isolated - runs in separate process (security)
3. Reusable - write once, use with Claude, GPT, Gemini, etc.
4. Auditable - easy to log what tools are called
"""

import asyncio
import base64
import json
import os
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not installed. Install with: pip install mcp")


# Gmail API scopes - what permissions we request
# Modify = read + write + send
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]

# Where to store OAuth tokens
DEFAULT_TOKEN_PATH = Path("credentials/gmail_token.json")
DEFAULT_CREDS_PATH = Path("credentials/oauth_credentials.json")


class GmailClient:
    """
    Gmail API client wrapper.

    Handles authentication and provides methods for Gmail operations.
    This is the actual Gmail logic - the MCP server wraps this.
    """

    def __init__(
        self,
        token_path: Path = DEFAULT_TOKEN_PATH,
        credentials_path: Path = DEFAULT_CREDS_PATH,
    ):
        """
        Initialize Gmail client.

        Args:
            token_path: Where to save/load OAuth token
            credentials_path: Path to OAuth client credentials JSON
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.

        First tries to load existing token. If not found or expired,
        runs the OAuth flow (opens browser for consent).

        Returns:
            True if authentication successful
        """
        # Try to load existing token
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # If no valid credentials, run OAuth flow
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh expired token
                self.creds.refresh(Request())
            else:
                # Run full OAuth flow
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"OAuth credentials not found at {self.credentials_path}. "
                        "Download from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save token for next time
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        # Build the Gmail service
        self.service = build("gmail", "v1", credentials=self.creds)
        return True

    def draft_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a draft email (doesn't send).

        This is safer than send_email - user can review before sending.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)

        Returns:
            Dict with draft_id and message info
        """
        if not self.service:
            self.authenticate()

        # Create the email message
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        # Encode for Gmail API
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create draft
        draft = self.service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}}
        ).execute()

        return {
            "draft_id": draft["id"],
            "message_id": draft["message"]["id"],
            "status": "draft_created",
            "to": to,
            "subject": subject,
        }

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        draft_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email directly or send an existing draft.

        Args:
            to: Recipient email (ignored if draft_id provided)
            subject: Email subject (ignored if draft_id provided)
            body: Email body (ignored if draft_id provided)
            cc: CC recipients
            draft_id: If provided, send this draft instead

        Returns:
            Dict with send status and message info
        """
        if not self.service:
            self.authenticate()

        if draft_id:
            # Send existing draft
            result = self.service.users().drafts().send(
                userId="me",
                body={"id": draft_id}
            ).execute()
        else:
            # Create and send new message
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = self.service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()

        return {
            "message_id": result["id"],
            "status": "sent",
            "labels": result.get("labelIds", []),
        }

    def search_inbox(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search inbox with Gmail search syntax.

        Gmail search examples:
        - "from:professor@morgan.edu" - emails from someone
        - "subject:COSC 301" - emails about a course
        - "is:unread" - unread emails
        - "after:2024/01/01" - emails after date

        Args:
            query: Gmail search query
            max_results: Maximum emails to return

        Returns:
            List of email summaries
        """
        if not self.service:
            self.authenticate()

        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            # Get full message details
            full_msg = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            ).execute()

            # Extract headers
            headers = {h["name"]: h["value"] for h in full_msg.get("payload", {}).get("headers", [])}

            emails.append({
                "id": msg["id"],
                "thread_id": msg.get("threadId"),
                "from": headers.get("From", "Unknown"),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", ""),
                "snippet": full_msg.get("snippet", ""),
            })

        return emails

    def get_email(self, message_id: str) -> Dict[str, Any]:
        """
        Get full content of a specific email.

        Args:
            message_id: The Gmail message ID

        Returns:
            Dict with full email content
        """
        if not self.service:
            self.authenticate()

        msg = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full",
        ).execute()

        # Extract headers
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Extract body
        body = ""
        payload = msg.get("payload", {})

        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        elif "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain" and part["body"].get("data"):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break

        return {
            "id": message_id,
            "from": headers.get("From", "Unknown"),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", "(no subject)"),
            "date": headers.get("Date", ""),
            "body": body,
            "labels": msg.get("labelIds", []),
        }

    def list_labels(self) -> List[Dict[str, str]]:
        """
        List all Gmail labels (folders).

        Returns:
            List of label info dicts
        """
        if not self.service:
            self.authenticate()

        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        return [{"id": l["id"], "name": l["name"]} for l in labels]


# ============================================================================
# MCP SERVER IMPLEMENTATION
# ============================================================================

def create_gmail_mcp_server() -> "Server":
    """
    Create the MCP server with Gmail tools.

    This is what gets run when you start the MCP server.
    """
    if not MCP_AVAILABLE:
        raise ImportError("MCP not available. Install with: pip install mcp")

    server = Server("gmail-mcp")
    gmail = GmailClient()

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available Gmail tools."""
        return [
            Tool(
                name="draft_email",
                description="Create a draft email (doesn't send). "
                           "Returns draft_id that can be used to send later.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line",
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body text",
                        },
                        "cc": {
                            "type": "string",
                            "description": "CC recipients (optional)",
                        },
                    },
                    "required": ["to", "subject", "body"],
                },
            ),
            Tool(
                name="send_email",
                description="Send an email directly or send an existing draft.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line",
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body text",
                        },
                        "draft_id": {
                            "type": "string",
                            "description": "Send existing draft (if provided, ignores other fields)",
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="search_inbox",
                description="Search inbox using Gmail search syntax. "
                           "Examples: 'from:someone@email.com', 'subject:meeting', 'is:unread'",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Max results to return (default 10)",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_email",
                description="Get the full content of a specific email by ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID",
                        },
                    },
                    "required": ["message_id"],
                },
            ),
            Tool(
                name="list_labels",
                description="List all Gmail labels (folders like Inbox, Sent, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls from the AI agent."""
        try:
            if name == "draft_email":
                result = gmail.draft_email(
                    to=arguments["to"],
                    subject=arguments["subject"],
                    body=arguments["body"],
                    cc=arguments.get("cc"),
                )
            elif name == "send_email":
                result = gmail.send_email(
                    to=arguments.get("to", ""),
                    subject=arguments.get("subject", ""),
                    body=arguments.get("body", ""),
                    draft_id=arguments.get("draft_id"),
                )
            elif name == "search_inbox":
                result = gmail.search_inbox(
                    query=arguments["query"],
                    max_results=arguments.get("max_results", 10),
                )
            elif name == "get_email":
                result = gmail.get_email(arguments["message_id"])
            elif name == "list_labels":
                result = gmail.list_labels()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except HttpError as e:
            return [TextContent(type="text", text=f"Gmail API error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    return server


async def main():
    """Run the Gmail MCP server."""
    if not MCP_AVAILABLE:
        print("MCP not installed. Run: pip install mcp")
        return

    server = create_gmail_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
