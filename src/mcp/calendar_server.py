"""
Google Calendar MCP Server
==========================

MCP server that provides Google Calendar tools to AI agents.

TOOLS PROVIDED:
--------------
- create_event: Create a new calendar event
- list_events: List upcoming events
- check_availability: Check if a time slot is free
- update_event: Modify an existing event
- delete_event: Remove an event
- list_calendars: List available calendars

USE CASES FOR STUDENTS:
----------------------
1. Schedule study sessions
2. Add assignment deadlines
3. Book office hours with professors
4. Set registration reminders
5. Block time for exam prep

AUTHENTICATION:
--------------
Uses the same OAuth flow as Gmail. If you've already authenticated
Gmail, Calendar should work too (assuming you enabled the Calendar API).
"""

import asyncio
import json
from datetime import datetime, timedelta
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


# Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Token storage
DEFAULT_TOKEN_PATH = Path("credentials/calendar_token.json")
DEFAULT_CREDS_PATH = Path("credentials/oauth_credentials.json")


class CalendarClient:
    """
    Google Calendar API client wrapper.

    Provides methods for calendar operations.
    """

    def __init__(
        self,
        token_path: Path = DEFAULT_TOKEN_PATH,
        credentials_path: Path = DEFAULT_CREDS_PATH,
    ):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.

        Similar to Gmail auth - tries to load existing token first.
        """
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"OAuth credentials not found at {self.credentials_path}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        self.service = build("calendar", "v3", credentials=self.creds)
        return True

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminders: Optional[List[Dict]] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Create a new calendar event.

        Args:
            summary: Event title (e.g., "COSC 301 Study Session")
            start_time: Start time in ISO format (e.g., "2024-03-15T14:00:00-05:00")
            end_time: End time in ISO format
            description: Event description/notes
            location: Location (e.g., "Library Room 301")
            attendees: List of email addresses to invite
            reminders: Custom reminders (default: 30min popup)
            calendar_id: Which calendar to add to (default: primary)

        Returns:
            Dict with event details and link
        """
        if not self.service:
            self.authenticate()

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                "timeZone": "America/New_York",  # Morgan State timezone
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "America/New_York",
            },
        }

        if description:
            event["description"] = description

        if location:
            event["location"] = location

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        if reminders:
            event["reminders"] = {
                "useDefault": False,
                "overrides": reminders,
            }
        else:
            # Default: 30 minute popup reminder
            event["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                ],
            }

        result = self.service.events().insert(
            calendarId=calendar_id,
            body=event,
        ).execute()

        return {
            "event_id": result["id"],
            "summary": result["summary"],
            "start": result["start"],
            "end": result["end"],
            "link": result.get("htmlLink"),
            "status": "created",
        }

    def list_events(
        self,
        max_results: int = 10,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> List[Dict[str, Any]]:
        """
        List upcoming calendar events.

        Args:
            max_results: Maximum events to return
            time_min: Start of time range (ISO format, default: now)
            time_max: End of time range (ISO format)
            calendar_id: Which calendar to query

        Returns:
            List of event summaries
        """
        if not self.service:
            self.authenticate()

        if not time_min:
            time_min = datetime.utcnow().isoformat() + "Z"

        params = {
            "calendarId": calendar_id,
            "timeMin": time_min,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }

        if time_max:
            params["timeMax"] = time_max

        result = self.service.events().list(**params).execute()
        events = result.get("items", [])

        return [
            {
                "id": e["id"],
                "summary": e.get("summary", "(no title)"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "location": e.get("location", ""),
                "description": e.get("description", ""),
            }
            for e in events
        ]

    def check_availability(
        self,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Check if a time slot is available.

        Args:
            start_time: Start of time slot (ISO format)
            end_time: End of time slot (ISO format)
            calendar_id: Which calendar to check

        Returns:
            Dict with availability status and any conflicting events
        """
        if not self.service:
            self.authenticate()

        # List events in the time range
        events = self.list_events(
            time_min=start_time,
            time_max=end_time,
            calendar_id=calendar_id,
        )

        if not events:
            return {
                "available": True,
                "conflicts": [],
                "message": "Time slot is free!",
            }
        else:
            return {
                "available": False,
                "conflicts": events,
                "message": f"Found {len(events)} conflicting event(s)",
            }

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event.

        Only updates fields that are provided.

        Args:
            event_id: ID of event to update
            summary: New title (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            location: New location (optional)
            calendar_id: Which calendar

        Returns:
            Updated event details
        """
        if not self.service:
            self.authenticate()

        # Get existing event
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        # Update fields
        if summary:
            event["summary"] = summary
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if start_time:
            event["start"]["dateTime"] = start_time
        if end_time:
            event["end"]["dateTime"] = end_time

        result = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event,
        ).execute()

        return {
            "event_id": result["id"],
            "summary": result["summary"],
            "status": "updated",
            "link": result.get("htmlLink"),
        }

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> Dict[str, str]:
        """
        Delete a calendar event.

        Args:
            event_id: ID of event to delete
            calendar_id: Which calendar

        Returns:
            Confirmation message
        """
        if not self.service:
            self.authenticate()

        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        return {
            "event_id": event_id,
            "status": "deleted",
        }

    def list_calendars(self) -> List[Dict[str, str]]:
        """
        List all available calendars.

        Returns:
            List of calendar info
        """
        if not self.service:
            self.authenticate()

        result = self.service.calendarList().list().execute()
        calendars = result.get("items", [])

        return [
            {
                "id": c["id"],
                "summary": c["summary"],
                "primary": c.get("primary", False),
            }
            for c in calendars
        ]

    def create_quick_event(
        self,
        text: str,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Create an event using natural language.

        Google Calendar can parse things like:
        - "Meeting tomorrow at 3pm"
        - "Study COSC 301 Friday 2-4pm"
        - "Office hours with Dr. Smith next Monday 10am"

        Args:
            text: Natural language event description
            calendar_id: Which calendar

        Returns:
            Created event details
        """
        if not self.service:
            self.authenticate()

        result = self.service.events().quickAdd(
            calendarId=calendar_id,
            text=text,
        ).execute()

        return {
            "event_id": result["id"],
            "summary": result.get("summary", text),
            "start": result["start"],
            "end": result["end"],
            "link": result.get("htmlLink"),
            "status": "created",
        }


# ============================================================================
# MCP SERVER IMPLEMENTATION
# ============================================================================

def create_calendar_mcp_server() -> "Server":
    """Create the MCP server with Calendar tools."""
    if not MCP_AVAILABLE:
        raise ImportError("MCP not available")

    server = Server("calendar-mcp")
    calendar = CalendarClient()

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="create_event",
                description="Create a new calendar event. Use for study sessions, "
                           "deadlines, office hours, etc.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Event title",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO format (e.g., 2024-03-15T14:00:00-05:00)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time in ISO format",
                        },
                        "description": {
                            "type": "string",
                            "description": "Event notes/description",
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location",
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Email addresses to invite",
                        },
                    },
                    "required": ["summary", "start_time", "end_time"],
                },
            ),
            Tool(
                name="quick_add_event",
                description="Create event using natural language like 'Study COSC 301 Friday 2-4pm'",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Natural language event description",
                        },
                    },
                    "required": ["text"],
                },
            ),
            Tool(
                name="list_events",
                description="List upcoming calendar events",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Max events to return (default 10)",
                            "default": 10,
                        },
                        "time_min": {
                            "type": "string",
                            "description": "Start of time range (ISO format)",
                        },
                        "time_max": {
                            "type": "string",
                            "description": "End of time range (ISO format)",
                        },
                    },
                },
            ),
            Tool(
                name="check_availability",
                description="Check if a time slot is free (no conflicting events)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "Start of time slot (ISO format)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End of time slot (ISO format)",
                        },
                    },
                    "required": ["start_time", "end_time"],
                },
            ),
            Tool(
                name="update_event",
                description="Update an existing calendar event",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "ID of event to update",
                        },
                        "summary": {"type": "string"},
                        "start_time": {"type": "string"},
                        "end_time": {"type": "string"},
                        "description": {"type": "string"},
                        "location": {"type": "string"},
                    },
                    "required": ["event_id"],
                },
            ),
            Tool(
                name="delete_event",
                description="Delete a calendar event",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "ID of event to delete",
                        },
                    },
                    "required": ["event_id"],
                },
            ),
            Tool(
                name="list_calendars",
                description="List all available calendars",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            if name == "create_event":
                result = calendar.create_event(
                    summary=arguments["summary"],
                    start_time=arguments["start_time"],
                    end_time=arguments["end_time"],
                    description=arguments.get("description"),
                    location=arguments.get("location"),
                    attendees=arguments.get("attendees"),
                )
            elif name == "quick_add_event":
                result = calendar.create_quick_event(arguments["text"])
            elif name == "list_events":
                result = calendar.list_events(
                    max_results=arguments.get("max_results", 10),
                    time_min=arguments.get("time_min"),
                    time_max=arguments.get("time_max"),
                )
            elif name == "check_availability":
                result = calendar.check_availability(
                    start_time=arguments["start_time"],
                    end_time=arguments["end_time"],
                )
            elif name == "update_event":
                result = calendar.update_event(
                    event_id=arguments["event_id"],
                    summary=arguments.get("summary"),
                    start_time=arguments.get("start_time"),
                    end_time=arguments.get("end_time"),
                    description=arguments.get("description"),
                    location=arguments.get("location"),
                )
            elif name == "delete_event":
                result = calendar.delete_event(arguments["event_id"])
            elif name == "list_calendars":
                result = calendar.list_calendars()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except HttpError as e:
            return [TextContent(type="text", text=f"Calendar API error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    return server


async def main():
    """Run the Calendar MCP server."""
    if not MCP_AVAILABLE:
        print("MCP not installed. Run: pip install mcp")
        return

    server = create_calendar_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
