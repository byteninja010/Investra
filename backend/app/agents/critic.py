"""
Critic / Synthesis Agent — reviews multi-agent findings, resolves trade-offs,
and generates the final Hypothetical Portfolio Allocation and comprehensive report.
"""

from app.config import get_llm
from app.models.state import AgentState
from app.models.agent_outputs import CritiqueResult

SYSTEM_PROMPT = """\
You are the Chief Investment Committee Lead and Critic in a multi-agent portfolio allocation system.

Your responsibilities:
1. **Review Agent Evidence**: Analyze findings from the Fundamental, Technical, Risk, and Research/RAG agents.
2. **Resolve Contradictions**: Identify and highlight trade-offs (e.g. excellent fundamentals but near-term overbought RSI, or high growth vs high beta).
3. **Formulate Hypothetical Capital Allocation**:
   - Allocate 100% of the user's total budget across 3 to 4 recommended assets (and optional liquid Cash buffer if prudent for high volatility / short horizon).
   - Ensure the sum of percentages equals 100.0%.
   - Calculate the exact allocated monetary amount for each asset matching the user's budget and currency.
4. **Produce a Comprehensive Markdown Report** formatted with:
   - `# 🎯 Investment Portfolio Allocation Report`
   - `## 📊 Executive Summary` (Bottom line recommendation, risk match, expected trajectory)
   - `## 💰 Hypothetical Asset Allocation` (A formatted Markdown Table: Asset, Ticker, Allocation %, Amount, Asset Class, Strategic Rationale)
   - `## 🔍 Multi-Agent Analysis Highlights`
     - Fundamental Health & Valuation
     - Technical Trends & Entry Timing
     - Risk Assessment & Diversification
     - Market Intelligence & RAG Insights
   - `## ⚖️ Trade-offs & Contradictions`
   - `## ⚠️ Downside Risks & Monitoring Strategy`
   - `## 📚 Sources & References` (Include citations from RAG & news)

Always ground your allocations in the real data provided. Be transparent about risks.
"""


async def critic_node(state: AgentState) -> dict:
    """Review all agent analyses and generate the final portfolio allocation report."""
    amount = state.get("amount", 10000.0)
    currency = state.get("currency", "INR")
    curr_symbol = "₹" if currency == "INR" else "$"
    risk = state.get("risk_tolerance", "moderate")
    horizon = state.get("horizon", "medium")
    goal = state.get("goal", "growth")
    thesis = state.get("investment_thesis", "")
    candidates = state.get("candidate_assets", [])

    events = [{
        "event_type": "agent_start",
        "agent_name": "critic",
        "message": f"Synthesizing specialist agent findings into final portfolio allocation for {curr_symbol}{amount:,.0f}...",
    }]

    # Compile all specialist agent outputs
    agent_results = state.get("agent_results", [])
    results_summary = []
    for result in agent_results:
        results_summary.append(
            f"### Specialist Agent: {result.agent_name.upper()}\n"
            f"Status: {result.status}\n"
            f"Summary: {result.summary}\n"
            f"Data: {result.data}\n"
        )

    combined_results = "\n\n".join(results_summary) if results_summary else "No agent outputs available."

    user_context = (
        f"USER INVESTMENT PROFILE:\n"
        f"- Capital: {curr_symbol}{amount:,.2f} ({currency})\n"
        f"- Risk Tolerance: {risk.title()}\n"
        f"- Horizon: {horizon.title()}\n"
        f"- Goal: {goal.title()}\n"
        f"- Initial Thesis: {thesis}\n"
        f"- Candidate Assets Basket: {candidates}\n\n"
        f"SPECIALIST AGENT FINDINGS:\n{combined_results}"
    )

    llm = get_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(CritiqueResult)

    critique: CritiqueResult = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_context},
    ])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "critic",
        "message": f"Portfolio synthesized: {critique.final_verdict} (Confidence: {critique.confidence_level})",
        "data": {
            "allocation_plan": [a.model_dump() for a in critique.allocation_plan],
            "confidence": critique.confidence_level,
            "verdict": critique.final_verdict,
            "contradictions": critique.contradictions,
            "risk_warnings": critique.risk_warnings,
        },
    })

    events.append({
        "event_type": "report_ready",
        "agent_name": "critic",
        "message": "Investment portfolio allocation ready.",
        "data": {
            "report": critique.final_report,
            "allocation_plan": [a.model_dump() for a in critique.allocation_plan],
        },
    })

    return {
        "critique": critique.final_verdict,
        "needs_reanalysis": False,
        "reanalysis_instructions": critique.reanalysis_instructions,
        "allocation_plan": [a.model_dump() for a in critique.allocation_plan],
        "final_report": critique.final_report,
        "events": events,
    }
