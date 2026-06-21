"""
Claude Agent integration for hypothesis-lab.

Uses the Claude Agent SDK (claude-agent-sdk) to run hypothesis experiments
and analysis tasks. Falls back gracefully when the SDK is not installed.

Install the optional dependency:
    pip install hypothesis-lab[claude]
    # or
    pip install claude-agent-sdk
"""

from __future__ import annotations

from typing import Any

from hypothesis_lab.agents.base import AgentMessage, AgentRole
from hypothesis_lab.retrieval.engine import RetrievalResult

# Soft dependency — SDK is optional
try:
    from claude_agent_sdk import (  # type: ignore[import-untyped]
        AssistantMessage,
        ClaudeAgentOptions,
        TextBlock,
        query,
    )

    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


_SYSTEM_PROMPT = """\
You are a hypothesis-lab research agent specialising in AI retrieval systems.
Your role is to analyse the balance between "gravity" (exploitation/relevance)
and "anti-gravity" (exploration/serendipity) in personalised retrieval.

When given retrieval results, you should:
1. Identify patterns in the gravity vs novelty scores.
2. Suggest adjustments to the exploration/exploitation ratio.
3. Propose hypotheses about what the user might find interesting next.
4. Evaluate whether the current Multi-Armed Bandit strategy is converging well.

Be concise and focus on actionable insights.
"""


class ClaudeHypothesisAgent:
    """
    A Claude-powered agent for hypothesis generation and retrieval analysis.

    This agent uses the Claude Agent SDK to analyse retrieval results and
    generate hypotheses about the optimal gravity/anti-gravity balance.

    Args:
        max_turns: Maximum number of agent turns per analysis.
        system_prompt: Custom system prompt (defaults to hypothesis-lab prompt).
    """

    def __init__(
        self,
        max_turns: int = 3,
        system_prompt: str = _SYSTEM_PROMPT,
    ) -> None:
        if not _SDK_AVAILABLE:
            raise RuntimeError(
                "Claude Agent SDK is not installed. "
                "Run: pip install hypothesis-lab[claude]"
            )
        self.max_turns = max_turns
        self.system_prompt = system_prompt

    async def analyse_results(
        self, results: list[RetrievalResult], context: str = ""
    ) -> AgentMessage:
        """
        Analyse a set of retrieval results and generate insights.

        Args:
            results: The retrieval results to analyse.
            context: Optional additional context for the agent.

        Returns:
            An AgentMessage containing the Claude agent's analysis.
        """
        summary = _format_results(results)
        prompt = f"Analyse these retrieval results:\n\n{summary}"
        if context:
            prompt += f"\n\nContext: {context}"

        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            max_turns=self.max_turns,
        )

        response_parts: list[str] = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)

        return AgentMessage(
            role=AgentRole.CLAUDE,
            content="\n".join(response_parts),
            metadata={"result_count": len(results)},
        )

    async def generate_hypothesis(self, bandit_summary: dict[str, Any]) -> AgentMessage:
        """
        Generate a hypothesis about the exploration/exploitation balance.

        Args:
            bandit_summary: Summary dict from a bandit's `.summary()` method.

        Returns:
            An AgentMessage with the generated hypothesis.
        """
        prompt = (
            "Based on the following Multi-Armed Bandit statistics, "
            "generate a hypothesis about whether the current exploration/"
            "exploitation balance is optimal and what changes might improve it:\n\n"
            f"{bandit_summary}"
        )

        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            max_turns=self.max_turns,
        )

        response_parts: list[str] = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)

        return AgentMessage(
            role=AgentRole.CLAUDE,
            content="\n".join(response_parts),
            metadata={"bandit_step": bandit_summary.get("step")},
        )


def _format_results(results: list[RetrievalResult]) -> str:
    """Format retrieval results for analysis."""
    lines = [f"Strategy: {results[0].strategy if results else 'N/A'}"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. [{r.id}] gravity={r.gravity_score:.3f} "
            f"novelty={r.novelty_score:.3f} combined={r.combined_score:.3f}"
        )
    return "\n".join(lines)
