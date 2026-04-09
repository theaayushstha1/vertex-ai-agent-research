"""Student profile model and Firestore CRUD operations."""

import os
from datetime import datetime, timezone
from typing import Any

from google.cloud import firestore

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
COLLECTION = "students"


def _get_db():
    return firestore.Client(project=PROJECT_ID)


def get_student_profile(canvas_user_id: str) -> dict:
    """Load a student's profile from Firestore.

    Returns the profile dict, or a default empty profile if none exists.
    """
    db = _get_db()
    doc = db.collection(COLLECTION).document(canvas_user_id).get()
    if doc.exists:
        return doc.to_dict()
    return {
        "canvas_user_id": canvas_user_id,
        "enrolled_courses": [],
        "quiz_history": [],
        "weak_topics": [],
        "strong_topics": [],
        "sessions": [],
        "last_active": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_student_profile(canvas_user_id: str, profile: dict) -> None:
    """Save or update a student's profile in Firestore."""
    db = _get_db()
    profile["last_active"] = datetime.now(timezone.utc).isoformat()
    db.collection(COLLECTION).document(canvas_user_id).set(profile, merge=True)


def update_enrolled_courses(canvas_user_id: str, courses: list[dict]) -> None:
    """Update the student's enrolled courses list."""
    db = _get_db()
    db.collection(COLLECTION).document(canvas_user_id).set(
        {
            "enrolled_courses": courses,
            "last_active": datetime.now(timezone.utc).isoformat(),
        },
        merge=True,
    )


def add_quiz_result(canvas_user_id: str, result: dict) -> None:
    """Append a quiz result to the student's history.

    result should contain: topic, score, total, missed_concepts, timestamp
    """
    db = _get_db()
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    db.collection(COLLECTION).document(canvas_user_id).update(
        {"quiz_history": firestore.ArrayUnion([result])}
    )


def update_topic_mastery(canvas_user_id: str, weak: list[str], strong: list[str]) -> None:
    """Set the student's current weak and strong topic lists."""
    db = _get_db()
    db.collection(COLLECTION).document(canvas_user_id).set(
        {
            "weak_topics": weak,
            "strong_topics": strong,
            "last_active": datetime.now(timezone.utc).isoformat(),
        },
        merge=True,
    )


def log_session(canvas_user_id: str, session_data: dict) -> None:
    """Log a tutoring session."""
    db = _get_db()
    session_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    db.collection(COLLECTION).document(canvas_user_id).update(
        {"sessions": firestore.ArrayUnion([session_data])}
    )
