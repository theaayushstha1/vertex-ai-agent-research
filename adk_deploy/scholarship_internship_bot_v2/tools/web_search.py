"""Tavily-backed web search tool for the scholarship V2 agent.

Replaces Gemini's `google_search` grounding with a regular function tool
so it can coexist with other function tools on the same LlmAgent.
"""

import os
from typing import Any

from tavily import TavilyClient


def _get_client() -> TavilyClient:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY not set. Add it to .env. "
            "Get a free key at https://app.tavily.com."
        )
    return TavilyClient(api_key=api_key)


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the web for current scholarship, internship, and career info.

    Start with one broad query. Do a second, narrower query if the first
    misses Morgan-State-specific, HBCU-specific, or major-specific hits.

    Args:
        query: What to search for. Be specific (e.g., "HBCU CS scholarships
            2026 junior" beats "scholarships").
        max_results: How many results to return, 1-10. Default 5.

    Returns:
        A dict with key "results" holding a list of
        {title, url, snippet, published_date} entries. On error, the dict
        has an "error" key and empty "results".
    """
    max_results = max(1, min(10, max_results))
    try:
        client = _get_client()
        raw = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=False,
        )
    except Exception as exc:
        return {"error": str(exc), "results": []}

    normalized = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "published_date": r.get("published_date"),
        }
        for r in raw.get("results", [])
    ]
    return {"results": normalized}
