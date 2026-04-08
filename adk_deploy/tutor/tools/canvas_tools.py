"""ADK tools for connecting to Canvas and syncing course materials.

DEPRECATED: These tools use a single shared CANVAS_API_TOKEN env var for all
users, which means every student hits the same Canvas identity. This is a
tenant-isolation failure in multi-user deployments. The tutor is now integrated
into cs-navigator, where Canvas access goes through the backend with per-user
LDAP auth. See: cs-chatbot-morganstate/adk_agent/cs_navigator_unified/tools/material_sync.py
"""

import os
import re
from datetime import datetime, timezone

from ..canvas.client import CanvasClient
from ..canvas.sync import sync_course_files, sync_all_courses as _sync_all
from ..canvas.datastore import get_or_create_datastore, import_documents

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN", "")

# Keywords that indicate a Canvas enrollment is not an actual class
_NON_CLASS_KEYWORDS = [
    "orientation", "honors college", "honors program", "club",
    "student organization", "advising", "tutoring center",
    "career services", "library", "campus life", "residence",
    "student affairs", "student government", "sga",
]


def _get_client() -> CanvasClient:
    return CanvasClient(access_token=CANVAS_API_TOKEN)


def _clean_course_name(raw_name: str) -> str:
    """Extract a clean course code like 'COSC 251' from raw Canvas names.

    Handles patterns like:
        'COSC 251 W04_Spring 2026'   -> 'COSC 251'
        'COSC251.001_Spring 2026'    -> 'COSC 251'
        'AAA999.001_'                -> 'AAA 999'
        'MATH 241-001 Fall 2025'     -> 'MATH 241'
        'COSC220 W01_Spring 2026'    -> 'COSC 220'
        'PHYS 206.W01_Spring 2026'   -> 'PHYS 206'
    """
    name = raw_name.strip()

    # Try to extract a course code pattern: 2-4 letters followed by 3-4 digits
    # This handles both "COSC 251" and "COSC251" and "AAA999.001_" formats
    match = re.match(r"([A-Za-z]{2,4})\s*(\d{3,4})", name)
    if match:
        dept = match.group(1).upper()
        num = match.group(2)
        return f"{dept} {num}"

    # Fallback: strip section/semester junk from whatever we have
    name = re.split(r"[._\s]*(W\d{2}|[-]\d{3}|\d{3}[-])", name)[0]
    name = re.sub(r"\s*(Spring|Summer|Fall|Winter)\s+\d{4}.*$", "", name, flags=re.IGNORECASE)
    return name.strip()


def _is_actual_class(name: str) -> bool:
    """Return False for non-class enrollments like clubs, orientation, etc."""
    lower = name.lower()
    if any(kw in lower for kw in _NON_CLASS_KEYWORDS):
        return False
    # Must contain a course-code-like pattern (letters + digits) to count as a class
    if not re.search(r"[A-Za-z]{2,4}\s*\d{3,4}", name):
        return False
    return True


def _is_current_semester(term_name: str) -> bool:
    """Check if a term name matches the current semester."""
    if not term_name:
        return True  # if no term info, include it to be safe

    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year

    # Figure out current semester from the calendar month
    if month <= 5:
        current_semester = "Spring"
    elif month <= 7:
        current_semester = "Summer"
    else:
        current_semester = "Fall"

    term_lower = term_name.lower()
    # Check if the term contains the current semester and year
    return current_semester.lower() in term_lower and str(year) in term_lower


# In-memory cache so other tools can resolve course names to IDs within a session
_course_cache: dict[int, dict] = {}


def _find_course_by_name(query: str) -> dict | None:
    """Match a query like 'COSC 251' against the cached course list."""
    query_upper = query.strip().upper()
    for cid, info in _course_cache.items():
        if query_upper in info["clean_name"].upper():
            return {"course_id": cid, **info}
    return None


async def connect_canvas() -> dict:
    """Connect to Canvas and list the student's current semester courses.

    Filters out non-classes (clubs, orientation, etc.), previous semesters,
    and returns clean course names like 'COSC 251' instead of raw Canvas names.
    """
    client = _get_client()
    try:
        enrollments = await client.get_current_enrollments()
        courses = []
        for e in enrollments:
            info = await client.get_course_info(e["course_id"])
            raw_name = info.get("name", "")
            term_name = info.get("term", {}).get("name", "")

            if not _is_actual_class(raw_name):
                continue
            if not _is_current_semester(term_name):
                continue

            clean_name = _clean_course_name(raw_name)
            teachers = info.get("teachers", [])
            instructor = teachers[0]["display_name"] if teachers else "Unknown"
            course_entry = {
                "course_id": e["course_id"],
                "name": clean_name,
                "instructor": instructor,
            }
            courses.append(course_entry)
            _course_cache[e["course_id"]] = {
                "clean_name": clean_name,
                "raw_name": raw_name,
                "instructor": instructor,
            }
        return {
            "status": "connected",
            "enrolled_courses": courses,
            "message": f"Found {len(courses)} current semester courses.",
        }
    finally:
        await client.close()


async def get_course_assignments(course_name: str) -> dict:
    """Get assignments for a specific course by name (e.g. 'COSC 251').

    Matches the course name against enrolled courses and returns that
    course's assignments. Use connect_canvas first if courses aren't loaded.

    Args:
        course_name: The course code or name to look up (e.g. 'COSC 251', 'MATH 241').
    """
    # If cache is empty, fetch enrollments first
    if not _course_cache:
        await connect_canvas()

    match = _find_course_by_name(course_name)
    if not match:
        available = [info["clean_name"] for info in _course_cache.values()]
        return {
            "status": "not_found",
            "message": f"Could not find a course matching '{course_name}'. Available courses: {', '.join(available)}",
        }

    client = _get_client()
    try:
        assignments = await client.get_course_assignments(match["course_id"])
        return {
            "status": "ok",
            "course_id": match["course_id"],
            "course_name": match["clean_name"],
            "assignments": [
                {
                    "name": a.get("name"),
                    "due_at": a.get("due_at"),
                    "points_possible": a.get("points_possible"),
                    "description": (a.get("description") or "")[:300],
                }
                for a in assignments
            ],
            "count": len(assignments),
        }
    finally:
        await client.close()


async def sync_course_materials(course_id: int) -> dict:
    """Sync files from a single Canvas course to GCS and create a search datastore.

    Downloads supported files (pdf, docx, pptx, txt, html) under 50MB,
    uploads them to GCS, creates a Vertex AI Search datastore, and imports the docs.

    Args:
        course_id: The Canvas course ID to sync.
    """
    client = _get_client()
    try:
        info = await client.get_course_info(course_id)
        course_name = info.get("name", f"Course {course_id}")

        sync_result = await sync_course_files(client, course_id, course_name)
        datastore_id = get_or_create_datastore(str(course_id), course_name)
        op_name = import_documents(str(course_id))

        return {
            "status": "syncing",
            "sync_result": sync_result,
            "datastore_id": datastore_id,
            "import_operation": op_name,
            "message": (
                f"Uploaded {sync_result['files_uploaded']} files for {course_name}. "
                f"Indexing is in progress -- it may take a few minutes before search results appear."
            ),
        }
    finally:
        await client.close()


async def sync_all_courses() -> dict:
    """Sync materials from ALL enrolled Canvas courses."""
    client = _get_client()
    try:
        results = await _sync_all(client)

        for r in results:
            cid = str(r["course_id"])
            cname = r["course_name"]
            get_or_create_datastore(cid, cname)
            import_documents(cid)

        total_files = sum(r["files_uploaded"] for r in results)
        return {
            "status": "syncing",
            "courses_synced": len(results),
            "total_files_uploaded": total_files,
            "details": results,
            "message": (
                f"Synced {total_files} files across {len(results)} courses. "
                f"Indexing in progress for all courses."
            ),
        }
    finally:
        await client.close()
