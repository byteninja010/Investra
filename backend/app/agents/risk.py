"""
Risk Assessment Agent — evaluates asset volatility, beta, Sharpe ratio, and portfolio diversification.

Calculates risk metrics for all candidate assets and checks compatibility with the user's
risk tolerance (Low/Moderate/High) and capital preservation needs.
"""

from app.config import get_llm
from app.models.state import AgentState, AgentResult
from app.models.agent_outputs import RiskAnalysis
from app.tools.risk_metrics import calculate_risk_metrics

SYSTEM_PROMPT = """\
You are the Chief Risk Officer in a portfolio allocation system.

You receive REAL calculated risk metrics (Annualized Volatility, Beta vs Benchmark, Sharpe Ratio, Max Drawdown)
for the candidate assets.
Your goal is to:
1. Evaluate each asset's risk profile (Low, Moderate, High risk).
2. Measure diversification quality across the candidate basket.
3. Check whether the proposed candidate basket aligns with the user's stated risk tolerance.
4. Flag downside protection needs (e.g. suggesting a cash buffer or lower-beta weighting for conservative investors).
5. Summarize the risk landscape in 2-3 concise sentences.
"""


async def risk_node(state: AgentState) -> dict:
    """Compute risk metrics across all candidate assets and verify risk profile fit."""
    candidates = state.get("candidate_assets", [])
    if not candidates:
        return {
            "agent_results": [AgentResult(agent_name="risk", status="skipped", summary="No candidate assets provided")],
            "events": [],
        }

    currency = state.get("currency", "INR")
    benchmark = "^NSEI" if currency == "INR" else "^GSPC"

    events = [{
        "event_type": "agent_start",
        "agent_name": "risk",
        "message": f"Calculating volatility, beta, and Sharpe ratios for candidate basket (benchmark: {benchmark})...",
    }]

    # Compute risk metrics for each candidate
    risk_by_ticker = {}
    for asset in candidates:
        ticker = asset.get("ticker", "")
        if ticker:
            risk_by_ticker[ticker] = calculate_risk_metrics.invoke({"ticker": ticker, "benchmark": benchmark})

    events.append({
        "event_type": "agent_progress",
        "agent_name": "risk",
        "message": "Assessing portfolio diversification and downside risk against user risk profile...",
    })

    llm = get_llm()
    structured_llm = llm.with_structured_output(RiskAnalysis)

    user_prompt = (
        f"User Risk Tolerance: {state.get('risk_tolerance', 'moderate')}\n"
        f"Investment Horizon: {state.get('horizon', 'medium')}\n"
        f"Primary Goal: {state.get('goal', 'growth')}\n\n"
        f"Candidate Assets Risk Metrics:\n{risk_by_ticker}"
    )

    analysis: RiskAnalysis = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "risk",
        "message": f"Risk assessment complete: {analysis.portfolio_risk_level} risk | Alignment: {analysis.risk_alignment}",
        "data": analysis.model_dump(),
    })

    return {
        "agent_results": [AgentResult(
            agent_name="risk",
            status="success",
            data=analysis.model_dump(),
            summary=analysis.summary,
        )],
        "events": events,
    }
