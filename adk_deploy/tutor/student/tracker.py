"""Progress tracking -- analyze quiz history to find weak/strong topics."""

from collections import defaultdict

from .profile import get_student_profile, update_topic_mastery


def analyze_mastery(canvas_user_id: str) -> dict:
    """Analyze a student's quiz history and compute topic mastery levels.

    Returns a dict with weak_topics, strong_topics, and per-topic stats.
    """
    profile = get_student_profile(canvas_user_id)
    quiz_history = profile.get("quiz_history", [])

    if not quiz_history:
        return {
            "weak_topics": [],
            "strong_topics": [],
            "topic_stats": {},
            "message": "No quiz history yet. Complete some quizzes to start tracking progress.",
        }

    # Aggregate scores per topic
    topic_scores: dict[str, list[float]] = defaultdict(list)
    topic_missed: dict[str, list[str]] = defaultdict(list)

    for quiz in quiz_history:
        topic = quiz.get("topic", "unknown")
        score = quiz.get("score", 0)
        total = quiz.get("total", 1)
        pct = (score / total * 100) if total > 0 else 0
        topic_scores[topic].append(pct)

        missed = quiz.get("missed_concepts", [])
        topic_missed[topic].extend(missed)

    # Compute averages and classify
    topic_stats = {}
    weak = []
    strong = []

    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        recent = scores[-1] if scores else 0
        trend = "improving" if len(scores) > 1 and scores[-1] > scores[-2] else "stable"
        if len(scores) > 1 and scores[-1] < scores[-2]:
            trend = "declining"

        topic_stats[topic] = {
            "average_score": round(avg, 1),
            "recent_score": round(recent, 1),
            "attempts": len(scores),
            "trend": trend,
            "commonly_missed": list(set(topic_missed[topic]))[:5],
        }

        if avg < 70:
            weak.append(topic)
        elif avg >= 85:
            strong.append(topic)

    # Persist the updated mastery
    update_topic_mastery(canvas_user_id, weak, strong)

    return {
        "weak_topics": weak,
        "strong_topics": strong,
        "topic_stats": topic_stats,
        "total_quizzes": len(quiz_history),
    }


def get_exam_review_topics(canvas_user_id: str, exam_topics: list[str]) -> dict:
    """Given a list of exam topics, return which ones the student should prioritize.

    Cross-references exam topics with the student's weak areas.
    """
    mastery = analyze_mastery(canvas_user_id)
    weak = set(t.lower() for t in mastery["weak_topics"])

    priority = []
    review = []
    confident = []

    for topic in exam_topics:
        topic_lower = topic.lower()
        stats = mastery["topic_stats"].get(topic, mastery["topic_stats"].get(topic_lower))

        if topic_lower in weak or stats is None:
            priority.append(topic)
        elif stats and stats["average_score"] < 85:
            review.append(topic)
        else:
            confident.append(topic)

    return {
        "priority_review": priority,
        "light_review": review,
        "confident": confident,
        "message": (
            f"Focus on: {', '.join(priority)}. "
            f"Quick review: {', '.join(review)}. "
            f"You're solid on: {', '.join(confident)}."
        ) if priority or review else "You look well-prepared across all topics!",
    }
