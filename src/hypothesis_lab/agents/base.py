"""
Base types shared across all agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    """The role of an agent in the managed system."""

    CLAUDE = "claude"
    JULES = "jules"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentMessage:
    """A message exchanged between agents."""

    role: AgentRole
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.role.value.upper()}] {self.content}"
