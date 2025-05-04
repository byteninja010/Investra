"""
LangGraph workflow — the core state machine that orchestrates all agents.

Graph topology:
  START → orchestrator → [fan-out] fundamental, technical, risk, research → [fan-in] critic → END

Key patterns demonstrated:
  - Conditional routing (orchestrator decides which agents run)
  - Parallel execution (fan-out via multiple edges)
  - Fan-in (all results converge at critic)
  - State management (shared TypedDict state)
  - Agent-to-agent communication (via state)
"""

from langgraph.graph import StateGraph, START, END

from app.models.state import AgentState
from app.agents.orchestrator import orchestrator_node
from app.agents.fundamental import fundamental_node
from app.agents.technical import technical_node
from app.agents.risk import risk_node
from app.agents.research import research_node
from app.agents.critic import critic_node


def should_run_agent(agent_name: str):
    """Create a conditional check for whether a specific agent should run."""
    def check(state: AgentState) -> bool:
        return agent_name in state.get("agents_to_run", [])
    return check


async def skip_node(state: AgentState) -> dict:
    """No-op node for skipped agents — returns empty updates."""
    return {"agent_results": [], "events": []}


# ---------------------------------------------------------------------------
# Router functions — LangGraph uses these to decide edges
# ---------------------------------------------------------------------------

def route_fundamental(state: AgentState) -> str:
    """Route to fundamental agent or skip."""
    return "fundamental" if "fundamental" in state.get("agents_to_run", []) else "skip_fundamental"


def route_technical(state: AgentState) -> str:
    """Route to technical agent or skip."""
    return "technical" if "technical" in state.get("agents_to_run", []) else "skip_technical"


def route_risk(state: AgentState) -> str:
    """Route to risk agent or skip."""
    return "risk" if "risk" in state.get("agents_to_run", []) else "skip_risk"


def route_research(state: AgentState) -> str:
    """Route to research agent or skip."""
    return "research" if "research" in state.get("agents_to_run", []) else "skip_research"


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """Construct and compile the multi-agent finance research graph."""

    graph = StateGraph(AgentState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("fundamental", fundamental_node)
    graph.add_node("technical", technical_node)
    graph.add_node("risk", risk_node)
    graph.add_node("research", research_node)
    graph.add_node("critic", critic_node)

    # Skip nodes (no-ops for agents the orchestrator didn't select)
    graph.add_node("skip_fundamental", skip_node)
    graph.add_node("skip_technical", skip_node)
    graph.add_node("skip_risk", skip_node)
    graph.add_node("skip_research", skip_node)

    # ── Entry edge ─────────────────────────────────────────────────────
    graph.add_edge(START, "orchestrator")

    # ── Fan-out: orchestrator → conditional routing to each agent ──────
    # Each branch independently decides run vs skip.
    # LangGraph executes all branches in the same super-step (parallel).
    graph.add_conditional_edges(
        "orchestrator",
        route_fundamental,
        {"fundamental": "fundamental", "skip_fundamental": "skip_fundamental"},
    )
    graph.add_conditional_edges(
        "orchestrator",
        route_technical,
        {"technical": "technical", "skip_technical": "skip_technical"},
    )
    graph.add_conditional_edges(
        "orchestrator",
        route_risk,
        {"risk": "risk", "skip_risk": "skip_risk"},
    )
    graph.add_conditional_edges(
        "orchestrator",
        route_research,
        {"research": "research", "skip_research": "skip_research"},
    )

    # ── Fan-in: all agents → critic ───────────────────────────────────
    graph.add_edge("fundamental", "critic")
    graph.add_edge("technical", "critic")
    graph.add_edge("risk", "critic")
    graph.add_edge("research", "critic")
    graph.add_edge("skip_fundamental", "critic")
    graph.add_edge("skip_technical", "critic")
    graph.add_edge("skip_risk", "critic")
    graph.add_edge("skip_research", "critic")

    # ── Critic → END ──────────────────────────────────────────────────
    graph.add_edge("critic", END)

    return graph.compile()


# Pre-compiled graph instance
workflow = build_graph()
