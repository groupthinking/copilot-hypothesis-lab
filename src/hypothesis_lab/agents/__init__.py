"""Agents sub-package for hypothesis-lab."""

from hypothesis_lab.agents.base import AgentMessage, AgentRole
from hypothesis_lab.agents.claude_agent import ClaudeHypothesisAgent

__all__ = ["AgentMessage", "AgentRole", "ClaudeHypothesisAgent"]
