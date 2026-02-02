"""
Example: Gmail MCP Integration
==============================

This example shows how to use the Gmail MCP to:
1. Search your inbox
2. Draft an email
3. Send an email (with confirmation)

BEFORE RUNNING:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials (Desktop application)
3. Download JSON to credentials/oauth_credentials.json
4. Run this script - it will open browser for consent

Run with:
    python examples/email_demo.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp.gmail_server import GmailClient


async def main():
    print("=" * 60)
    print("Gmail MCP Demo")
    print("=" * 60)

    # Initialize Gmail client
    gmail = GmailClient()

    # Step 1: Authenticate
    print("\n[1] Authenticating with Gmail...")
    try:
        gmail.authenticate()
        print("    ✓ Authenticated successfully!")
    except FileNotFoundError as e:
        print(f"    ✗ Error: {e}")
        print("\n    To fix:")
        print("    1. Go to Google Cloud Console → APIs & Services → Credentials")
        print("    2. Create OAuth 2.0 Client ID (Desktop application)")
        print("    3. Download JSON to: credentials/oauth_credentials.json")
        return
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return

    # Step 2: List labels
    print("\n[2] Listing Gmail labels...")
    labels = gmail.list_labels()
    print(f"    Found {len(labels)} labels:")
    for label in labels[:5]:  # Show first 5
        print(f"      - {label['name']}")

    # Step 3: Search inbox
    print("\n[3] Searching inbox for recent emails...")
    emails = gmail.search_inbox("is:inbox", max_results=3)
    print(f"    Found {len(emails)} recent emails:")
    for email in emails:
        subject = email['subject'][:40] + "..." if len(email['subject']) > 40 else email['subject']
        print(f"      - {subject}")
        print(f"        From: {email['from']}")

    # Step 4: Draft an email (demonstration)
    print("\n[4] Creating a draft email...")
    draft = gmail.draft_email(
        to="test@example.com",
        subject="Test from CS Navigator Agent",
        body="""Hello,

This is a test email from the Morgan State CS Navigator Agent system.

The agent office can:
- Answer academic questions
- Provide career guidance
- Help with scheduling
- And now send emails!

Best regards,
CS Navigator Bot
""",
    )
    print(f"    ✓ Draft created!")
    print(f"      Draft ID: {draft['draft_id']}")
    print(f"      To: {draft['to']}")
    print(f"      Subject: {draft['subject']}")

    # Step 5: Ask about sending
    print("\n[5] Draft created but NOT sent.")
    print("    To send, you would call: gmail.send_email(draft_id='{draft_id}')")
    print("    Or open Gmail and send manually from Drafts folder.")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
