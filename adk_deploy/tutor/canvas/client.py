"""Canvas REST API client -- enrollments, files, course info."""

import asyncio
import os
from typing import Any

import httpx

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "https://morganstate.instructure.com")
API_BASE = f"{CANVAS_BASE_URL}/api/v1"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class CanvasClient:
    """Async wrapper around the Canvas LMS REST API."""

    def __init__(self, access_token: str):
        self._token = access_token
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30.0,
        )

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make an API request with rate-limit awareness."""
        url = f"{API_BASE}{path}" if path.startswith("/") else path
        resp = await self._client.request(method, url, **kwargs)

        # Basic rate-limit backoff
        remaining = resp.headers.get("X-Rate-Limit-Remaining")
        if remaining and float(remaining) < 50:
            await asyncio.sleep(1)

        resp.raise_for_status()
        return resp.json()

    async def _paginate(self, path: str, **kwargs) -> list[dict]:
        """Follow Canvas pagination links to collect all results."""
        results: list[dict] = []
        url = f"{API_BASE}{path}"
        while url:
            resp = await self._client.get(url, **kwargs)
            remaining = resp.headers.get("X-Rate-Limit-Remaining")
            if remaining and float(remaining) < 50:
                await asyncio.sleep(1)
            resp.raise_for_status()
            results.extend(resp.json())

            # Canvas uses Link header for pagination
            links = resp.headers.get("Link", "")
            url = None
            for part in links.split(","):
                if 'rel="next"' in part:
                    url = part.split("<")[1].split(">")[0]
        return results

    async def get_current_enrollments(self) -> list[dict]:
        """Return active student enrollments for the current user."""
        return await self._paginate(
            "/users/self/enrollments",
            params={"state[]": "active", "type[]": "StudentEnrollment", "per_page": 50},
        )

    async def get_course_info(self, course_id: int) -> dict:
        """Return course name, term, and instructor info."""
        return await self._request(
            "GET",
            f"/courses/{course_id}",
            params={"include[]": ["term", "teachers"]},
        )

    async def get_course_files(self, course_id: int) -> list[dict]:
        """Return all files for a course (paginated)."""
        return await self._paginate(
            f"/courses/{course_id}/files",
            params={"per_page": 100},
        )

    async def download_file(self, file_url: str) -> bytes | None:
        """Download a single file. Returns None if >50 MB."""
        resp = await self._client.get(file_url, follow_redirects=True)
        resp.raise_for_status()
        if len(resp.content) > MAX_FILE_SIZE:
            return None
        return resp.content

    async def get_upcoming_events(self) -> list[dict]:
        """Return upcoming calendar events for the current user."""
        return await self._request("GET", "/users/self/upcoming_events")

    async def get_course_assignments(self, course_id: int) -> list[dict]:
        """Return assignments for a course."""
        return await self._paginate(
            f"/courses/{course_id}/assignments",
            params={"per_page": 50, "order_by": "due_at"},
        )

    async def close(self):
        await self._client.aclose()
