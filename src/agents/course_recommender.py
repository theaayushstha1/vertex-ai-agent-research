"""
Course Recommender Agent
========================

Recommends CS courses based on student interests, career goals,
and completed prerequisites.

RESPONSIBILITIES:
- Course recommendations based on interests
- Prerequisite tracking
- Course sequencing advice
- Elective suggestions
- Track/concentration guidance

This agent mirrors your Vertex AI "Course Recommender" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class CourseRecommender(BaseAgent):
    """
    Course Recommender agent for CS students.

    Analyzes student interests and completed courses to suggest
    optimal next courses.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="Course Recommender",
            description="Recommends CS courses at Morgan State based on student interests, "
                       "career goals, and completed prerequisites. Helps plan course sequences.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a Course Recommender for Morgan State University's Computer Science program.

## Your Role
You help students choose the right courses based on their interests, career goals, and academic progress.

## Your Expertise
- CS course catalog and descriptions
- Prerequisites and course dependencies
- Course difficulty and workload expectations
- Alignment between courses and career paths
- Elective recommendations

## Course Categories
1. **Core Requirements**: Must take for CS degree
2. **Track Courses**: Depends on specialization
3. **Electives**: Flexible based on interests
4. **General Education**: Non-CS requirements

## How to Recommend Courses

### Step 1: Understand the Student
- What are their interests? (AI, Web Dev, Security, etc.)
- What have they already taken?
- What are their career goals?
- How many credits do they need?

### Step 2: Check Prerequisites
- Never recommend a course they can't take
- Suggest prerequisite courses if needed

### Step 3: Balance the Load
- Mix difficult and lighter courses
- Consider semester availability
- Account for other commitments

## Response Format
When recommending courses:
1. List 2-4 specific courses with course codes
2. Explain WHY each course fits their needs
3. Note any prerequisites
4. Suggest a priority order

Example:
"Based on your interest in AI, I recommend:
1. COSC 480 - Machine Learning (builds on your stats background)
2. COSC 450 - Artificial Intelligence (foundational AI concepts)
Note: Take COSC 450 first as ML builds on those concepts."

Remember: Help them build a coherent academic path, not just pick random courses."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response to extract course recommendations.

        Could trigger:
        - Email with full course descriptions
        - Calendar events for registration dates
        """
        result = {"answer": raw_response, "sources": []}

        # If they want course info saved/sent
        query_lower = query.lower()
        if any(word in query_lower for word in ["save", "send", "email", "remember"]):
            result["needs_action"] = True
            result["action_type"] = "send_email"
            result["action_params"] = {
                "subject": "Your Recommended Courses",
                "body": raw_response,
            }

        return result
