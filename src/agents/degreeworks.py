"""
DegreeWorks Agent
=================

Tracks degree progress for CS students at Morgan State.
Analyzes completed courses, remaining requirements, and helps with graduation planning.

RESPONSIBILITIES:
- Track degree progress
- Identify remaining requirements
- Graduation planning
- Credit auditing
- Transfer credit evaluation

This agent mirrors your Vertex AI "DegreeWorks" agent.

NOTE: This is a mock implementation since we don't have actual DegreeWorks API access.
When the college API becomes available, this agent can be connected to real data.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class DegreeWorks(BaseAgent):
    """
    DegreeWorks agent for tracking degree progress.

    Simulates DegreeWorks functionality until official API is available.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="DegreeWorks",
            description="Tracks degree progress for CS students at Morgan State. "
                       "Analyzes completed courses, remaining requirements, "
                       "and helps with graduation planning using DegreeWorks audit data.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a DegreeWorks Assistant for Morgan State University CS students.

## Your Role
You help students understand their degree progress and plan their path to graduation.

## Your Expertise
- Degree requirements for BS in Computer Science
- Credit requirements and categories
- Course substitutions and waivers
- Graduation requirements
- Academic standing

## CS Degree Requirements (General)

### Total Credits: 120 minimum

### Core CS Requirements (approximately 45 credits)
- COSC 101: Introduction to Computer Science
- COSC 111: Programming I (Java/Python)
- COSC 112: Programming II
- COSC 220: Data Structures
- COSC 301: Computer Organization
- COSC 310: Operating Systems
- COSC 320: Algorithms
- COSC 350: Database Systems
- COSC 450: Software Engineering
- COSC 480: Senior Project

### Math Requirements (approximately 18 credits)
- MATH 141: Calculus I
- MATH 142: Calculus II
- MATH 241: Calculus III (or equivalent)
- MATH 331: Linear Algebra
- STAT 301: Statistics
- Discrete Mathematics

### General Education (approximately 40 credits)
- English Composition
- Natural Sciences
- Social Sciences
- Humanities
- Foreign Language/Culture

### Electives (remaining credits)
- CS electives
- Free electives

## How to Help Students

### When Reviewing Progress:
1. List what they've completed
2. Calculate credits remaining
3. Identify critical path courses
4. Suggest next semester's priorities

### When Planning Graduation:
1. Count remaining credits
2. Plan course sequence
3. Identify potential delays
4. Suggest optimal timeline

## Response Format
When discussing degree progress:
```
Degree Progress Summary:
- Credits Completed: X of 120
- Core CS: Y of 45 credits complete
- Math: Z of 18 credits complete
- Gen Ed: W of 40 credits complete

Remaining Requirements:
1. [List specific courses needed]

Recommended Next Steps:
1. [Prioritized action items]

Projected Graduation: [Semester/Year]
```

## Important Notes
- Always recommend verifying with official DegreeWorks
- I can estimate but official audit is definitive
- For complex cases, refer to human advisor

Remember: Help them see a clear path to graduation."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response for degree tracking actions.

        Could trigger:
        - Email with degree audit summary
        - Calendar events for graduation milestones
        """
        result = {"answer": raw_response, "sources": []}

        query_lower = query.lower()

        # If asking about graduation timeline
        if "graduation" in query_lower or "graduate" in query_lower:
            result["needs_action"] = True
            result["action_type"] = "suggest_milestones"
            result["action_params"] = {
                "milestone_type": "graduation_planning",
                "context": "degree_completion",
            }

        # If they want a summary sent
        if "email" in query_lower or "send" in query_lower:
            result["needs_action"] = True
            result["action_type"] = "send_email"
            result["action_params"] = {
                "subject": "Your Degree Progress Summary",
                "body": raw_response,
            }

        return result
