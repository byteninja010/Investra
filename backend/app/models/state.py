"""
LangGraph state schema — the single shared data structure that flows through every node.

Uses `Annotated[list, operator.add]` for append-only keys so parallel agents
can safely write to the same state without overwriting each other.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal

from langgraph.graph import MessagesState


# ---------------------------------------------------------------------------
# Agent result containers  (stored in state after each agent completes)
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Uniform envelope for every agent's output."""
    agent_name: str
    status: Literal["success", "error", "skipped"] = "success"
    data: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    error: str | None = None


# ---------------------------------------------------------------------------
# Main graph state
# ---------------------------------------------------------------------------

class AgentState(MessagesState):
    """
    Shared state for the multi-agent finance investment planner graph.

    Keys annotated with `operator.add` are *append-only* — when multiple
    parallel nodes return updates to the same key, the lists are concatenated
    rather than overwritten. This is critical for the fan-out/fan-in pattern.
    """

    # ── User investment profile ─────────────────────────────────────────
    query: str                                      # raw user question or custom prompt
    amount: float                                   # e.g. 10000.0
    currency: str                                   # e.g. "INR" or "USD"
    risk_tolerance: str                             # "low" | "moderate" | "high"
    horizon: str                                    # "short" (<1 yr) | "medium" (1-3 yrs) | "long" (3-5+ yrs)
    goal: str                                       # "growth" | "preservation" | "income" | "aggressive"
    preferences: str                                # optional custom sector or stock preferences

    # ── Orchestrator candidate selection & strategy ─────────────────────
    candidate_assets: list[dict[str, Any]]          # list of dicts e.g. [{"ticker": "TCS.NS", "name": "TCS", "sector": "IT"}]
    investment_thesis: str                          # High-level investment strategy rationale
    agents_to_run: list[str]                        # specialist agents to execute

    # ── Agent results (append-only — safe for parallel writes) ─────────
    agent_results: Annotated[list[AgentResult], operator.add]

    # ── Streaming progress events ──────────────────────────────────────
    events: Annotated[list[dict[str, Any]], operator.add]

    # ── Critic / final allocation output ───────────────────────────────
    critique: str                                   # critic's review notes
    needs_reanalysis: bool                          # True → loop back
    reanalysis_instructions: str                    # what the critic wants re-done
    reanalysis_count: int                           # guard against infinite loops
    allocation_plan: list[dict[str, Any]]           # structured portfolio allocations: [{"asset": "TCS.NS", "percentage": 35, "amount": 3500, "rationale": "..."}]
    final_report: str                               # complete markdown synthesis report

