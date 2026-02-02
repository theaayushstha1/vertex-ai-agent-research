"""
Schedule Builder Agent
======================

Helps students build conflict-free class schedules.
Considers course times, prerequisites, workload, and personal preferences.

RESPONSIBILITIES:
- Build conflict-free schedules
- Optimize for student preferences (morning/afternoon classes)
- Balance workload across the week
- Consider commute and work schedules

This agent mirrors your Vertex AI "Schedule Builder" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class ScheduleBuilder(BaseAgent):
    """
    Schedule Builder agent for CS students.

    Creates optimized class schedules considering multiple constraints.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="Schedule Builder",
            description="Helps students build conflict-free class schedules at Morgan State. "
                       "Considers course times, prerequisites, workload balance, "
                       "and personal preferences.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a Schedule Builder for Morgan State University CS students.

## Your Role
You help students create optimal class schedules that fit their academic and personal needs.

## Your Expertise
- Course scheduling and time slots
- Identifying schedule conflicts
- Workload balancing
- Optimizing for preferences

## Scheduling Principles

### 1. No Time Conflicts
- Classes cannot overlap
- Include travel time between buildings
- Account for back-to-back classes

### 2. Workload Balance
- Don't stack all hard classes on one day
- Consider lab times (usually 2-3 hours)
- Leave time for studying

### 3. Student Preferences
- Morning vs afternoon person
- Work schedule constraints
- Commute considerations
- Need for breaks

## How to Build a Schedule

### Step 1: List Required Courses
- What must they take this semester?
- Check all sections available

### Step 2: Check Conflicts
- Compare all time slots
- Note any overlaps

### Step 3: Optimize
- Fit their preferences
- Balance the week
- Leave study time

### Step 4: Present Options
- Show 2-3 possible schedules
- Explain trade-offs

## Response Format
When presenting a schedule:
```
Option 1: Mornings Free
Monday: COSC 301 (2:00-3:15pm), COSC 350 (4:00-5:15pm)
Tuesday: COSC 320 (1:00-2:15pm)
Wednesday: COSC 301 (2:00-3:15pm), COSC 350 (4:00-5:15pm)
Thursday: COSC 320 (1:00-2:15pm)
Friday: Free

Pros: Mornings free for work/study
Cons: Long Mondays/Wednesdays
```

Remember: A good schedule sets them up for academic success."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response to detect calendar integration needs.

        Could trigger:
        - Creating calendar events for class schedule
        - Setting registration reminders
        """
        result = {"answer": raw_response, "sources": []}

        query_lower = query.lower()
        response_lower = raw_response.lower()

        # If they want to add schedule to calendar
        if "calendar" in query_lower or "add" in query_lower:
            result["needs_action"] = True
            result["action_type"] = "create_schedule_events"
            result["action_params"] = {
                "schedule_text": raw_response,
                "context": "class_schedule",
            }

        # If discussing registration
        if "registration" in response_lower or "register" in response_lower:
            result["needs_action"] = True
            result["action_type"] = "suggest_reminder"
            result["action_params"] = {
                "reminder_type": "registration",
                "context": "course_registration",
            }

        return result
