"""
Orchestrator Module
===================

The "brain" of the system. Contains:
- CSNavigator: Routes queries to appropriate agents and runs them in parallel
- ConsensusSelector: Picks the best answer from multiple agent responses
"""

from .cs_navigator import CSNavigator
from .consensus import ConsensusSelector

__all__ = ["CSNavigator", "ConsensusSelector"]
