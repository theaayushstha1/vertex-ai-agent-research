"""Unit tests for the Tavily-backed web_search function tool."""

from unittest.mock import patch, MagicMock

import pytest


def test_web_search_returns_normalized_results(monkeypatch):
    """Happy path: Tavily returns results, tool returns normalized list of dicts."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-fake-key")

    fake_tavily_response = {
        "results": [
            {
                "title": "Morgan State CS Scholarships 2026",
                "url": "https://morgan.edu/financial-aid/scholarships",
                "content": "Scholarships available for CS students...",
                "published_date": "2026-02-01",
            },
            {
                "title": "UNCF STEM Scholars Program",
                "url": "https://uncf.org/programs/stem",
                "content": "Annual awards for HBCU STEM students...",
            },
        ]
    }

    with patch(
        "adk_deploy.scholarship_internship_bot_v2.tools.web_search.TavilyClient"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.search.return_value = fake_tavily_response
        mock_client_cls.return_value = mock_client

        from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

        result = web_search(query="Morgan State CS scholarships", max_results=5)

    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Morgan State CS Scholarships 2026"
    assert result["results"][0]["url"] == "https://morgan.edu/financial-aid/scholarships"
    assert result["results"][0]["snippet"] == "Scholarships available for CS students..."
    assert result["results"][0]["published_date"] == "2026-02-01"
    assert result["results"][1]["published_date"] is None
    mock_client.search.assert_called_once_with(
        query="Morgan State CS scholarships",
        max_results=5,
        search_depth="basic",
        include_answer=False,
    )


def test_web_search_returns_error_dict_when_api_key_missing(monkeypatch):
    """If TAVILY_API_KEY is unset, web_search returns {'error': ..., 'results': []}."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

    result = web_search(query="anything", max_results=3)

    assert result["results"] == []
    assert "error" in result
    assert "TAVILY_API_KEY" in result["error"]


def test_web_search_returns_error_dict_on_tavily_exception(monkeypatch):
    """If Tavily raises (network/5xx/rate-limit), tool returns error dict, does not raise."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-fake-key")

    with patch(
        "adk_deploy.scholarship_internship_bot_v2.tools.web_search.TavilyClient"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.search.side_effect = RuntimeError("Rate limit exceeded")
        mock_client_cls.return_value = mock_client

        from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

        result = web_search(query="anything", max_results=3)

    assert result["results"] == []
    assert "error" in result
    assert "Rate limit exceeded" in result["error"]
