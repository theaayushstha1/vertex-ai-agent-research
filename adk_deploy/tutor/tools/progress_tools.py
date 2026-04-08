"""ADK tools for student progress tracking via Firestore.

DEPRECATED: These tools accept canvas_user_id as a free parameter, allowing
the model to read/write any student's Firestore profile without authorization.
The tutor is now integrated into cs-navigator, where the user ID is resolved
server-side from JWT auth and injected into session state by the backend.
See: cs-chatbot-morganstate/adk_agent/cs_navigator_unified/tools/progress.py
"""

from ..student.profile import (
    get_student_profile as _get_profile,
    add_quiz_result,
    log_session as _log_session,
)
from ..student.tracker import analyze_mastery


def get_student_profile(canvas_user_id: str) -> dict:
    """Load the current student's profile including courses, quiz history, and weak topics.

    Args:
        canvas_user_id: The student's Canvas user ID.

    Returns:
        The student's full profile with enrolled courses, quiz history, and mastery data.
    """
    profile = _get_profile(canvas_user_id)
    # Also include computed mastery
    mastery = analyze_mastery(canvas_user_id)
    profile["computed_mastery"] = mastery
    return profile


def update_quiz_score(canvas_user_id: str, topic: str, score: int, total: int, missed_concepts: list[str]) -> dict:
    """Record a quiz result and update the student's mastery levels.

    Args:
        canvas_user_id: The student's Canvas user ID.
        topic: The quiz topic (e.g., "binary search trees", "calculus derivatives").
        score: Number of correct answers.
        total: Total number of questions.
        missed_concepts: List of concepts the student got wrong.

    Returns:
        Updated mastery analysis.
    """
    add_quiz_result(canvas_user_id, {
        "topic": topic,
        "score": score,
        "total": total,
        "missed_concepts": missed_concepts,
    })

    # Re-analyze after recording
    mastery = analyze_mastery(canvas_user_id)
    pct = round(score / total * 100) if total > 0 else 0

    return {
        "status": "recorded",
        "score": f"{score}/{total} ({pct}%)",
        "updated_mastery": mastery,
        "message": (
            f"Quiz recorded: {pct}% on {topic}. "
            + (f"Keep working on: {', '.join(mastery['weak_topics'])}." if mastery["weak_topics"] else "Looking strong!")
        ),
    }


def get_weaknesses(canvas_user_id: str) -> dict:
    """Return the student's weak topics for adaptive tutoring.

    Args:
        canvas_user_id: The student's Canvas user ID.

    Returns:
        Weak topics, commonly missed concepts, and suggestions.
    """
    mastery = analyze_mastery(canvas_user_id)
    weak = mastery.get("weak_topics", [])
    stats = mastery.get("topic_stats", {})

    details = []
    for topic in weak:
        s = stats.get(topic, {})
        details.append({
            "topic": topic,
            "average_score": s.get("average_score", "N/A"),
            "commonly_missed": s.get("commonly_missed", []),
            "trend": s.get("trend", "unknown"),
        })

    return {
        "weak_topics": details,
        "message": (
            f"Areas to focus on: {', '.join(weak)}." if weak
            else "No weak areas identified yet. Keep taking quizzes to track progress."
        ),
    }


def log_session(canvas_user_id: str, topics_covered: list[str]) -> dict:
    """Log a tutoring session with the topics that were covered.

    Args:
        canvas_user_id: The student's Canvas user ID.
        topics_covered: List of topics discussed in this session.

    Returns:
        Confirmation of the logged session.
    """
    _log_session(canvas_user_id, {"topics_covered": topics_covered})
    return {
        "status": "logged",
        "topics": topics_covered,
        "message": f"Session logged: covered {', '.join(topics_covered)}.",
    }
