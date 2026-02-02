"""
Consensus Selector
==================

When multiple agents respond to the same query, we need to pick the best answer
(or combine them). This module handles that decision.

HOW IT WORKS:
-------------
1. Collect responses from multiple agents
2. Score each response on multiple dimensions
3. Either select the highest-scoring response OR synthesize a combined answer

SCORING DIMENSIONS:
-------------------
- Relevance: How well does it answer the question?
- Completeness: Is the answer thorough?
- Confidence: How confident is the agent?
- Specificity: Does it have concrete details?
- Actionability: Does it give clear next steps?

WHY NOT JUST PICK THE FIRST RESPONSE?
-------------------------------------
Different agents have different expertise. A career question might get a better
answer from Career Guidance even if Academic Advisor responds first. The consensus
system ensures we pick the BEST answer, not just the FASTEST.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..agents.base import AgentResponse


@dataclass
class ScoredResponse:
    """
    A response with its calculated scores.

    Attributes:
        response: The original AgentResponse
        relevance_score: How relevant to the query (0-1)
        completeness_score: How thorough the answer (0-1)
        specificity_score: How specific/concrete (0-1)
        total_score: Weighted combination of all scores
    """
    response: AgentResponse
    relevance_score: float
    completeness_score: float
    specificity_score: float
    total_score: float


class ConsensusSelector:
    """
    Selects the best response from multiple agent responses.

    This class implements the "consensus" algorithm that picks the best
    answer when multiple agents respond to the same query.

    Example usage:
        selector = ConsensusSelector()
        responses = [academic_response, career_response, general_response]
        best = selector.select_best(responses, original_query)
    """

    def __init__(
        self,
        relevance_weight: float = 0.35,
        completeness_weight: float = 0.25,
        confidence_weight: float = 0.25,
        specificity_weight: float = 0.15,
    ):
        """
        Initialize the consensus selector.

        Args:
            relevance_weight: Weight for relevance score (default 0.35)
            completeness_weight: Weight for completeness score (default 0.25)
            confidence_weight: Weight for confidence score (default 0.25)
            specificity_weight: Weight for specificity score (default 0.15)

        Note: Weights should sum to 1.0 for interpretable final scores.
        """
        self.relevance_weight = relevance_weight
        self.completeness_weight = completeness_weight
        self.confidence_weight = confidence_weight
        self.specificity_weight = specificity_weight

    def score_response(self, response: AgentResponse, query: str) -> ScoredResponse:
        """
        Score a single response on multiple dimensions.

        Args:
            response: The agent's response
            query: The original user query

        Returns:
            ScoredResponse with individual and total scores
        """
        # Calculate individual scores
        relevance = self._calculate_relevance(response.answer, query)
        completeness = self._calculate_completeness(response.answer)
        specificity = self._calculate_specificity(response.answer)

        # Calculate weighted total
        total = (
            relevance * self.relevance_weight +
            completeness * self.completeness_weight +
            response.confidence * self.confidence_weight +
            specificity * self.specificity_weight
        )

        return ScoredResponse(
            response=response,
            relevance_score=relevance,
            completeness_score=completeness,
            specificity_score=specificity,
            total_score=total,
        )

    def _calculate_relevance(self, answer: str, query: str) -> float:
        """
        Calculate how relevant the answer is to the query.

        Uses simple keyword overlap. A more sophisticated implementation
        could use embeddings/semantic similarity.

        Args:
            answer: The response text
            query: The original query

        Returns:
            Float between 0.0 and 1.0
        """
        # Extract keywords from query (simple approach)
        query_words = set(query.lower().split())
        # Remove common words
        stop_words = {"a", "an", "the", "is", "are", "what", "how", "can", "i", "my", "to", "for"}
        query_keywords = query_words - stop_words

        if not query_keywords:
            return 0.5  # Default if no keywords

        # Check how many query keywords appear in answer
        answer_lower = answer.lower()
        matches = sum(1 for kw in query_keywords if kw in answer_lower)

        # Calculate ratio (with cap at 1.0)
        relevance = min(1.0, matches / len(query_keywords))

        return max(0.3, relevance)  # Minimum 0.3 (benefit of doubt)

    def _calculate_completeness(self, answer: str) -> float:
        """
        Calculate how complete/thorough the answer is.

        Factors:
        - Length (longer is usually more complete)
        - Structure (lists, sections indicate thoroughness)
        - Presence of examples

        Args:
            answer: The response text

        Returns:
            Float between 0.0 and 1.0
        """
        score = 0.5  # Base score

        # Length factor
        length = len(answer)
        if length > 200:
            score += 0.1
        if length > 500:
            score += 0.1
        if length > 1000:
            score += 0.1

        # Structure indicators
        structure_indicators = [
            "\n1." in answer or "\n- " in answer,  # Lists
            "##" in answer or "**" in answer,  # Markdown formatting
            ":" in answer,  # Definitions/explanations
        ]
        score += sum(0.05 for indicator in structure_indicators if indicator)

        # Example indicators
        example_words = ["example", "for instance", "such as", "e.g.", "like"]
        if any(word in answer.lower() for word in example_words):
            score += 0.1

        return min(1.0, score)

    def _calculate_specificity(self, answer: str) -> float:
        """
        Calculate how specific/concrete the answer is.

        Factors:
        - Numbers and statistics
        - Proper nouns (names, places)
        - Technical terms
        - Dates and times

        Args:
            answer: The response text

        Returns:
            Float between 0.0 and 1.0
        """
        score = 0.4  # Base score

        # Numbers indicate specificity
        has_numbers = any(char.isdigit() for char in answer)
        if has_numbers:
            score += 0.15

        # Percentages are very specific
        if "%" in answer:
            score += 0.1

        # Course codes (like COSC 301) are specific
        import re
        course_pattern = r"[A-Z]{4}\s*\d{3}"
        if re.search(course_pattern, answer):
            score += 0.15

        # URLs/links are specific
        if "http" in answer.lower() or ".edu" in answer.lower():
            score += 0.1

        # Dates/times
        time_words = ["monday", "tuesday", "wednesday", "thursday", "friday",
                     "january", "february", "march", "april", "may", "june",
                     "july", "august", "september", "october", "november", "december"]
        if any(word in answer.lower() for word in time_words):
            score += 0.1

        return min(1.0, score)

    def select_best(
        self,
        responses: List[AgentResponse],
        query: str
    ) -> Tuple[AgentResponse, List[ScoredResponse]]:
        """
        Select the best response from multiple agent responses.

        Args:
            responses: List of responses from different agents
            query: The original user query

        Returns:
            Tuple of (best_response, all_scored_responses)
            The scored responses are useful for debugging/transparency
        """
        if not responses:
            raise ValueError("No responses to select from")

        if len(responses) == 1:
            scored = self.score_response(responses[0], query)
            return responses[0], [scored]

        # Score all responses
        scored_responses = [
            self.score_response(response, query)
            for response in responses
        ]

        # Sort by total score (descending)
        scored_responses.sort(key=lambda x: x.total_score, reverse=True)

        # Return the best one
        best = scored_responses[0].response
        return best, scored_responses

    def synthesize(
        self,
        responses: List[AgentResponse],
        query: str,
        llm=None
    ) -> AgentResponse:
        """
        Synthesize multiple responses into a single comprehensive answer.

        This is an alternative to select_best when you want to COMBINE
        insights from multiple agents rather than pick just one.

        Args:
            responses: List of responses from different agents
            query: The original user query
            llm: Optional LLM to use for synthesis (if None, uses simple merge)

        Returns:
            A new AgentResponse that combines the best parts of all responses
        """
        if not responses:
            raise ValueError("No responses to synthesize")

        if len(responses) == 1:
            return responses[0]

        # Simple synthesis: combine answers with attribution
        combined_parts = []
        for response in responses:
            if response.answer and response.confidence > 0.3:
                combined_parts.append(
                    f"**From {response.agent_name}:**\n{response.answer}"
                )

        combined_answer = "\n\n---\n\n".join(combined_parts)

        # Calculate combined confidence (average of top 2)
        sorted_by_confidence = sorted(responses, key=lambda x: x.confidence, reverse=True)
        avg_confidence = sum(r.confidence for r in sorted_by_confidence[:2]) / 2

        return AgentResponse(
            agent_name="Combined Response",
            answer=combined_answer,
            confidence=avg_confidence,
            sources=[s for r in responses for s in r.sources],
            metadata={
                "synthesis": True,
                "source_agents": [r.agent_name for r in responses],
            }
        )

    def explain_selection(self, scored_responses: List[ScoredResponse]) -> str:
        """
        Generate a human-readable explanation of why a response was selected.

        Useful for debugging and transparency.

        Args:
            scored_responses: List of scored responses (sorted by score)

        Returns:
            String explanation of the selection
        """
        if not scored_responses:
            return "No responses to explain."

        lines = ["## Response Selection Explanation\n"]

        for i, scored in enumerate(scored_responses, 1):
            rank = "SELECTED" if i == 1 else f"Rank {i}"
            lines.append(f"### {rank}: {scored.response.agent_name}")
            lines.append(f"- **Total Score:** {scored.total_score:.2f}")
            lines.append(f"- **Relevance:** {scored.relevance_score:.2f}")
            lines.append(f"- **Completeness:** {scored.completeness_score:.2f}")
            lines.append(f"- **Confidence:** {scored.response.confidence:.2f}")
            lines.append(f"- **Specificity:** {scored.specificity_score:.2f}")
            lines.append("")

        return "\n".join(lines)
