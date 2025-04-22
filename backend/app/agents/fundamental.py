"""
Fundamental Analysis Agent — multi-asset valuation and financial health screening.

Calls get_stock_fundamentals for each candidate asset and evaluates their valuation (P/E),
profitability (ROE, margins), balance sheet health (Debt/Equity), and dividend yield.
"""

from app.config import get_llm
from app.models.state import AgentState, AgentResult
from app.models.agent_outputs import FundamentalAnalysis
from app.tools.market_data import get_stock_fundamentals

SYSTEM_PROMPT = """\
You are the Fundamental Analysis Specialist in a portfolio allocation system.

You receive REAL fundamental metrics fetched via API for candidate assets.
Your goal is to:
1. Review each asset's P/E ratio, ROE, profit margins, revenue growth, Debt/Equity, and Dividend Yield.
2. Assign a fundamental health score (Strong, Moderate, Weak) for each asset.
3. Identify top fundamental picks based on the user's investment goal (Growth, Preservation, Income, etc.).
4. Summarize your findings in 2-3 concise sentences.

Only reference real figures provided. Do NOT hallucinate metrics.
"""


async def fundamental_node(state: AgentState) -> dict:
    """Screen candidate assets using real fundamental data from yfinance."""
    candidates = state.get("candidate_assets", [])
    if not candidates:
        return {
            "agent_results": [AgentResult(agent_name="fundamental", status="skipped", summary="No candidate assets provided")],
            "events": [],
        }

    events = [{
        "event_type": "agent_start",
        "agent_name": "fundamental",
        "message": f"Fetching fundamental metrics for {len(candidates)} candidate assets...",
    }]

    # Fetch fundamentals for each candidate via tool
    fundamentals_by_ticker = {}
    for asset in candidates:
        ticker = asset.get("ticker", "")
        if ticker:
            fundamentals_by_ticker[ticker] = get_stock_fundamentals.invoke({"ticker": ticker})

    events.append({
        "event_type": "agent_progress",
        "agent_name": "fundamental",
        "message": f"Analyzing valuation, ROE, debt, and margins for candidate basket...",
    })

    llm = get_llm()
    structured_llm = llm.with_structured_output(FundamentalAnalysis)

    user_prompt = (
        f"User Goal: {state.get('goal', 'growth')}\n"
        f"Risk Tolerance: {state.get('risk_tolerance', 'moderate')}\n\n"
        f"Candidate Assets Data:\n{fundamentals_by_ticker}"
    )

    analysis: FundamentalAnalysis = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "fundamental",
        "message": f"Fundamental screening complete. Top picks: {', '.join(analysis.top_picks)}",
        "data": analysis.model_dump(),
    })

    return {
        "agent_results": [AgentResult(
            agent_name="fundamental",
            status="success",
            data=analysis.model_dump(),
            summary=analysis.summary,
        )],
        "events": events,
    }
