"""Exam prep tools -- find upcoming exams and generate study plans."""

import os

from ..canvas.client import CanvasClient
from ..canvas.mapping import get_mapping
from .search_tools import search_course_materials

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN", "")


async def find_upcoming_exams() -> dict:
    """Search Canvas calendar and assignments for upcoming exams/quizzes.

    Returns a list of upcoming assessments with dates, courses, and topics.
    """
    client = CanvasClient(access_token=CANVAS_API_TOKEN)
    try:
        events = await client.get_upcoming_events()
        enrollments = await client.get_current_enrollments()

        exams = []
        exam_keywords = {"exam", "midterm", "final", "quiz", "test", "assessment"}

        for event in events:
            title = (event.get("title") or "").lower()
            if any(kw in title for kw in exam_keywords):
                exams.append({
                    "title": event.get("title"),
                    "date": event.get("start_at") or event.get("all_day_date"),
                    "course_id": event.get("course_id"),
                    "type": "calendar_event",
                })

        for enrollment in enrollments:
            course_id = enrollment["course_id"]
            try:
                assignments = await client.get_course_assignments(course_id)
                for a in assignments:
                    name = (a.get("name") or "").lower()
                    if any(kw in name for kw in exam_keywords):
                        exams.append({
                            "title": a.get("name"),
                            "date": a.get("due_at"),
                            "course_id": course_id,
                            "type": "assignment",
                            "description": (a.get("description") or "")[:500],
                        })
            except Exception:
                continue

        return {
            "status": "ok",
            "upcoming_exams": exams,
            "count": len(exams),
            "message": f"Found {len(exams)} upcoming exams/quizzes." if exams else "No upcoming exams found in Canvas.",
        }
    finally:
        await client.close()


def generate_exam_prep_plan(course_id: str, exam_topic: str) -> dict:
    """Search course materials for an exam topic and build a study plan.

    Args:
        course_id: The Canvas course ID.
        exam_topic: The topic or exam name to prepare for.

    Returns:
        Study materials found and a suggested plan structure.
    """
    search_result = search_course_materials(exam_topic, course_id)

    mapping = get_mapping()
    entry = mapping.get(str(course_id), {})
    course_name = entry.get("course_name", f"Course {course_id}")

    if search_result["status"] == "not_synced":
        return {
            "status": "not_synced",
            "message": f"Course materials for {course_name} haven't been synced yet. Sync first to enable exam prep.",
        }

    return {
        "status": "ok",
        "course_name": course_name,
        "exam_topic": exam_topic,
        "materials_found": search_result["result_count"],
        "relevant_materials": search_result["results"],
        "message": (
            f"Found {search_result['result_count']} relevant materials for '{exam_topic}' in {course_name}. "
            f"Use these to generate practice questions and a study plan."
        ),
    }
