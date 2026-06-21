"""Run a tool-bound LLM until it stops requesting tools."""

from __future__ import annotations

from typing import Any


def run_tool_bound_agent(
    messages: list[Any],
    chain,
    tool_node,
    *,
    max_rounds: int = 6,
) -> list[Any]:
    """Return new messages produced after the initial conversation tail."""
    start_len = len(messages)
    working = list(messages)

    for _ in range(max_rounds):
        response = chain.invoke({"messages": working})
        working.append(response)

        tool_calls = getattr(response, "tool_calls", None) or []
        if not tool_calls:
            break

        tool_out = tool_node.invoke({"messages": working})
        working.extend(tool_out["messages"])

    return working[start_len:]
