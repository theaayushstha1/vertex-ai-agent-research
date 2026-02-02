"""
Academic Advisor Agent
======================

AI advisor for Morgan State University Computer Science students.
Helps with course selection, degree requirements, and faculty information.

RESPONSIBILITIES:
- Course selection guidance
- Degree requirement explanations
- Faculty and professor information
- Academic planning advice
- Prerequisites and course sequencing

This agent mirrors your Vertex AI "Academic Advisor" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class AcademicAdvisor(BaseAgent):
    """
    Academic Advisor agent for CS students.

    This agent helps students with academic planning, course selection,
    and understanding degree requirements.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Academic Advisor.

        Args:
            llm: Vertex AI LLM instance
            knowledge_base: Dict containing CS courses, requirements, faculty info
        """
        super().__init__(
            name="Academic Advisor",
            description="AI advisor for Morgan State University Computer Science students. "
                       "Helps with course selection, degree requirements, faculty information, "
                       "and academic planning.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        """
        Return the system prompt for the Academic Advisor.

        This prompt defines:
        - The agent's role and expertise
        - How to respond to students
        - What topics it can help with
        - Response style guidelines
        """
        return """You are an AI Academic Advisor for Morgan State University's Computer Science department.

## Your Role
You help CS students with academic planning and course-related questions. You are knowledgeable, supportive, and provide actionable advice.

## Your Expertise
- Course selection and prerequisites
- Degree requirements (BS in Computer Science)
- Course sequencing and academic planning
- Faculty information and research areas
- Academic policies and procedures

## Guidelines

### DO:
- Be warm and encouraging to students
- Provide specific course recommendations when asked
- Explain prerequisites and why they matter
- Suggest meeting with human advisors for complex situations
- Give concrete next steps

### DON'T:
- Make up course numbers or faculty names
- Guarantee specific outcomes (graduation dates, grades)
- Override official university policies
- Provide information about non-CS departments

## Response Format
1. Directly answer the question
2. Provide relevant context or explanation
3. Suggest next steps or additional resources
4. If unsure, say so and recommend speaking with a human advisor

## Morgan State CS Program Overview
- Bachelor of Science in Computer Science
- Core courses: Programming, Data Structures, Algorithms, Software Engineering
- Tracks: General CS, Cybersecurity, Data Science, Software Engineering
- Required GPA: 2.0 overall, 2.5 in major courses
- Total credits: 120 minimum

Remember: You're here to help students succeed. Be their advocate and guide."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process the response to detect if follow-up actions are needed.

        For Academic Advisor, we detect if the student might benefit from:
        - Scheduling an advisor meeting
        - Sending course information via email
        """
        result = {"answer": raw_response, "sources": []}

        # Check if response suggests scheduling a meeting
        meeting_keywords = [
            "schedule a meeting",
            "meet with your advisor",
            "book an appointment",
            "office hours",
        ]
        query_lower = query.lower()
        response_lower = raw_response.lower()

        # If talking about scheduling, suggest calendar action
        if any(kw in response_lower for kw in meeting_keywords):
            result["needs_action"] = True
            result["action_type"] = "suggest_meeting"
            result["action_params"] = {
                "context": "academic_advising",
                "query": query,
            }

        # If student asks for course info to be sent
        if "send" in query_lower and ("email" in query_lower or "mail" in query_lower):
            result["needs_action"] = True
            result["action_type"] = "send_email"
            result["action_params"] = {
                "subject": "Course Information from Academic Advisor",
                "body": raw_response,
            }

        return result

    def get_relevant_knowledge(self, query: str) -> str:
        """
        Extract relevant knowledge for academic queries.

        Looks at the query to determine what knowledge to include:
        - Course info for course-related questions
        - Faculty info for professor questions
        - Requirements for graduation/degree questions
        """
        if not self.knowledge_base:
            return ""

        query_lower = query.lower()
        relevant = []

        # Course-related queries
        course_keywords = ["course", "class", "cosc", "prerequisite", "credit"]
        if any(kw in query_lower for kw in course_keywords):
            if "courses" in self.knowledge_base:
                relevant.append(f"Available Courses:\n{self.knowledge_base['courses']}")

        # Faculty queries
        faculty_keywords = ["professor", "faculty", "instructor", "teacher", "dr."]
        if any(kw in query_lower for kw in faculty_keywords):
            if "faculty" in self.knowledge_base:
                relevant.append(f"Faculty Information:\n{self.knowledge_base['faculty']}")

        # Degree requirement queries
        req_keywords = ["graduate", "requirement", "degree", "gpa", "credit"]
        if any(kw in query_lower for kw in req_keywords):
            if "requirements" in self.knowledge_base:
                relevant.append(f"Degree Requirements:\n{self.knowledge_base['requirements']}")

        return "\n\n".join(relevant) if relevant else ""
