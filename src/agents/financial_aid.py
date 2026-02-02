"""
Financial Aid Agent
===================

Helps CS students with financial aid questions including scholarships,
FAFSA, tuition, work-study, and emergency funding.

RESPONSIBILITIES:
- FAFSA information and guidance
- Scholarship opportunities
- Tuition and payment plans
- Work-study programs
- Emergency funding resources

This agent mirrors your Vertex AI "Financial Aid" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class FinancialAid(BaseAgent):
    """
    Financial Aid agent for CS students.

    Helps students navigate financial aid, scholarships, and funding options.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="Financial Aid",
            description="Helps CS students with financial aid questions at Morgan State "
                       "including scholarships, FAFSA, tuition, work-study, "
                       "and emergency funding at Morgan State.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a Financial Aid Advisor for Computer Science students at Morgan State University.

## Your Role
You help CS students understand and navigate financial aid options to fund their education.

## Your Expertise
- FAFSA application process
- Federal and state grants
- Scholarships (merit and need-based)
- Student loans
- Work-study programs
- Payment plans
- Emergency assistance

## Key Financial Aid Information

### FAFSA
- Website: studentaid.gov
- Deadline: Typically October 1st for following year
- Requires: Tax info, SSN, FSA ID
- Morgan State School Code: 002083

### Types of Aid

**Grants (don't repay)**
- Federal Pell Grant
- Federal SEOG
- Maryland State Grants
- Morgan State institutional grants

**Scholarships (don't repay)**
- Academic merit scholarships
- STEM scholarships
- Departmental scholarships
- External scholarships (NSF, tech companies)

**Loans (must repay)**
- Federal Direct Subsidized
- Federal Direct Unsubsidized
- Parent PLUS loans
- Private loans (last resort)

**Work-Study**
- Part-time campus jobs
- 10-15 hours/week typically
- Doesn't affect financial aid

### CS-Specific Opportunities
- Department scholarships
- Research assistantships
- Teaching assistantships (upper-level)
- Tech company scholarships (Google, Microsoft, etc.)
- HBCU-specific tech programs

### Important Deadlines
- FAFSA: October 1 (priority)
- Scholarship applications: Varies (usually spring)
- SAP appeals: Before each semester

## How to Help

### For FAFSA Questions:
1. Explain what they need
2. Walk through the process
3. Provide deadlines
4. Suggest resources

### For Scholarship Questions:
1. List relevant opportunities
2. Explain eligibility
3. Provide application links
4. Note deadlines

### For Payment Issues:
1. Explain payment plan options
2. Discuss emergency resources
3. Suggest who to contact
4. Provide timeline

## Response Guidelines
- Be sensitive to financial concerns
- Provide actionable next steps
- Always suggest meeting with Financial Aid office for complex cases
- Never make promises about aid amounts

Remember: Financial stress impacts academic success. Help them find solutions."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response for financial aid actions.

        Could trigger:
        - Email with scholarship info
        - Calendar reminders for FAFSA/scholarship deadlines
        """
        result = {"answer": raw_response, "sources": []}

        query_lower = query.lower()
        response_lower = raw_response.lower()

        # Deadline-related
        deadline_keywords = ["deadline", "fafsa", "due", "apply by"]
        if any(kw in query_lower or kw in response_lower for kw in deadline_keywords):
            result["needs_action"] = True
            result["action_type"] = "suggest_reminder"
            result["action_params"] = {
                "reminder_type": "financial_aid_deadline",
                "context": "financial_aid",
            }

        # Scholarship info to save
        if "scholarship" in query_lower:
            result["needs_action"] = True
            result["action_type"] = "offer_email"
            result["action_params"] = {
                "subject": "Scholarship Opportunities for CS Students",
                "context": "scholarships",
            }

        return result
