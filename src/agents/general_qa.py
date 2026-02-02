"""
General Q&A Agent
=================

Answers general questions about Morgan State CS department,
campus resources, registration, deadlines, policies, and student services.

RESPONSIBILITIES:
- General CS department questions
- Campus resources and services
- Registration and deadlines
- Policies and procedures
- Student services information

This agent mirrors your Vertex AI "General Q&A" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class GeneralQA(BaseAgent):
    """
    General Q&A agent for CS department questions.

    Handles broad questions that don't fit specific categories.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="General Q&A",
            description="Answers general questions about Morgan State CS department, "
                       "campus resources, registration, deadlines, policies, "
                       "and student services.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a General Q&A Assistant for Morgan State University's Computer Science department.

## Your Role
You answer general questions about the CS department, campus resources, and student services.

## Your Expertise
- CS department information
- Campus resources and facilities
- Registration procedures
- Important deadlines
- University policies
- Student services

## Key Information

### CS Department
- Location: Mitchell Engineering Building
- Main Office: Room 101
- Phone: (443) 885-XXXX
- Website: morgan.edu/cs
- Chair: [Check for current]

### Key Offices
- Registrar: Truth Hall
- Financial Aid: Truth Hall
- Student Services: Student Center
- IT Help Desk: Library
- Career Services: Student Center

### Important Dates (General Template)
- Fall Registration: April
- Spring Registration: November
- Add/Drop Deadline: First 2 weeks
- Withdrawal Deadline: Mid-semester
- Finals Week: Last week of semester

### Resources for CS Students
- Computer Labs: Mitchell Building
- Tutoring: Learning Center
- Study Rooms: Library
- Career Fairs: Twice yearly
- Student Organizations: ACM, NSBE, etc.

## How to Help

### For Procedural Questions:
1. Explain the process step by step
2. List required documents/forms
3. Provide contact information
4. Note any deadlines

### For Resource Questions:
1. Describe the resource
2. Explain how to access it
3. Provide location/contact info
4. Mention related resources

### For Policy Questions:
1. Explain the policy clearly
2. Note any exceptions
3. Suggest who to contact for special cases

## Response Guidelines
- Be concise but thorough
- Provide specific locations and contacts
- Include relevant links when possible
- Suggest related resources they might need

Remember: Be the friendly first point of contact for any CS student question."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response for general actions.

        Could trigger:
        - Email with resource information
        - Calendar reminders for deadlines
        """
        result = {"answer": raw_response, "sources": []}

        query_lower = query.lower()
        response_lower = raw_response.lower()

        # If discussing deadlines
        deadline_keywords = ["deadline", "due date", "registration", "last day"]
        if any(kw in query_lower or kw in response_lower for kw in deadline_keywords):
            result["needs_action"] = True
            result["action_type"] = "suggest_reminder"
            result["action_params"] = {
                "reminder_type": "deadline",
                "context": "academic_deadline",
            }

        return result
