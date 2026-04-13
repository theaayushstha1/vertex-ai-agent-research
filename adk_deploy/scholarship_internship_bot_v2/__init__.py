"""Scholarship & Internship Bot V2 — flat agent with Tavily web search.

This module exposes `root_agent` (for `adk run`) and `agent` (for import
into cs_navigator) once agent.py is implemented.
"""
# agent.py is imported lazily by consumers (adk or cs_navigator).
# Importing this package does not eagerly construct the agent.
