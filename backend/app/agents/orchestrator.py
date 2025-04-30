"""
Orchestrator Agent — formulate the investment thesis and select candidate assets.

Takes the user's investment profile (amount, risk tolerance, horizon, goal, preferences)
and designs an allocation strategy, selecting 3-5 candidate assets for detailed analysis.
"""

from app.config import get_llm
from app.models.state import AgentState
from app.models.agent_outputs import OrchestratorDecision

SYSTEM_PROMPT = """\
You are the Chief Investment Strategist and Orchestrator of a multi-agent portfolio allocation system.

Your job is to:
1. Review the user's capital, currency, risk tolerance, investment horizon, and primary goal:
   - Risk Tolerance: Low (Conservative/Preservation), Moderate (Balanced Growth), High (Aggressive Growth).
   - Horizon: Short (< 1 yr), Medium (1-3 yrs), Long (3-5+ yrs).
   - Goal: Wealth Growth, Capital Preservation, Passive Income / Dividends, Aggressive Growth.
   - User Preferences: Any specific sectors, assets, or constraints provided.
2. Formulate a clear, actionable Investment Thesis.
3. Select 3 to 4 well-suited candidate assets (stocks/ETFs) to analyze.
   - For INR currency, pick established Indian stocks with correct yahoo ticker suffixes:
     • TCS.NS or INFY.NS (Information Technology)
     • RELIANCE.NS (Energy / Retail / Telecom)
     • HDFCBANK.NS or ICICIBANK.NS (Banking & Financials)
     • ITC.NS or HINDUNILVR.NS (FMCG / High Dividend)
     • LT.NS (Infrastructure / Capital Goods)
   - For USD currency, pick top US equities (e.g. AAPL, MSFT, NVDA, VOO, SCHD).
   - Respect any specific sector or stock preferences requested by the user.
4. Specify which specialist agents will analyze this basket (fundamental, technical, risk, research).
"""


async def orchestrator_node(state: AgentState) -> dict:
    """Analyze the user's investment profile and select candidate assets for evaluation."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(OrchestratorDecision)

    amount = state.get("amount", 10000.0)
    currency = state.get("currency", "INR")
    curr_symbol = "₹" if currency == "INR" else "$"
    risk = state.get("risk_tolerance", "moderate")
    horizon = state.get("horizon", "medium")
    goal = state.get("goal", "growth")
    preferences = state.get("preferences", "")
    query = state.get("query", "")

    user_profile_text = (
        f"Investment Capital: {curr_symbol}{amount:,.2f} ({currency})\n"
        f"Risk Tolerance: {risk.title()}\n"
        f"Time Horizon: {horizon.title()}\n"
        f"Primary Goal: {goal.title()}\n"
        f"Preferences / Notes: {preferences or query or 'None specified'}"
    )

    # Emit planning event
    events = [{
        "event_type": "agent_start",
        "agent_name": "orchestrator",
        "message": f"Formulating investment strategy for {curr_symbol}{amount:,.0f} ({risk} risk, {horizon} horizon)...",
    }]

    decision: OrchestratorDecision = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Formulate an investment allocation plan for this profile:\n\n{user_profile_text}"},
    ])

    candidates_summary = ", ".join([f"{c.name} ({c.ticker})" for c in decision.candidate_assets])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "orchestrator",
        "message": f"Selected candidate basket: {candidates_summary}",
        "data": {
            "investment_thesis": decision.investment_thesis,
            "candidate_assets": [c.model_dump() for c in decision.candidate_assets],
        },
    })

    return {
        "candidate_assets": [c.model_dump() for c in decision.candidate_assets],
        "investment_thesis": decision.investment_thesis,
        "agents_to_run": decision.agents_to_run,
        "events": events,
    }
