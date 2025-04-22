"""
Technical Analysis Agent — evaluates entry timing and price trends for candidate assets.

Calculates RSI-14, 50-day & 200-day SMAs, and MACD indicators across all candidate assets
to identify optimal entry points and momentum.
"""

from app.config import get_llm
from app.models.state import AgentState, AgentResult
from app.models.agent_outputs import TechnicalAnalysis
from app.tools.technical_indicators import calculate_technical_indicators

SYSTEM_PROMPT = """\
You are the Technical Analysis Specialist in a portfolio allocation system.

You receive REAL calculated indicators (RSI-14, SMA-50, SMA-200, MACD) for candidate assets.
Your goal is to:
1. Assess trend (Uptrend, Downtrend, Sideways) and price position relative to moving averages.
2. Check RSI: >70 (Overbought), <30 (Oversold), 30-70 (Neutral/Accumulation).
3. Evaluate entry timing (Favorable, Neutral, Caution) for deploying new capital.
4. Summarize your overall technical setup and timing in 2-3 concise sentences.
"""


async def technical_node(state: AgentState) -> dict:
    """Compute technical indicators for all candidate assets and assess timing."""
    candidates = state.get("candidate_assets", [])
    if not candidates:
        return {
            "agent_results": [AgentResult(agent_name="technical", status="skipped", summary="No candidate assets provided")],
            "events": [],
        }

    events = [{
        "event_type": "agent_start",
        "agent_name": "technical",
        "message": f"Computing technical indicators for {len(candidates)} candidate assets...",
    }]

    # Compute technicals for each candidate
    technicals_by_ticker = {}
    for asset in candidates:
        ticker = asset.get("ticker", "")
        if ticker:
            technicals_by_ticker[ticker] = calculate_technical_indicators.invoke({"ticker": ticker})

    events.append({
        "event_type": "agent_progress",
        "agent_name": "technical",
        "message": "Assessing RSI, Moving Averages, and MACD momentum signals...",
    })

    llm = get_llm()
    structured_llm = llm.with_structured_output(TechnicalAnalysis)

    user_prompt = (
        f"Time Horizon: {state.get('horizon', 'medium')}\n\n"
        f"Candidate Assets Technical Data:\n{technicals_by_ticker}"
    )

    analysis: TechnicalAnalysis = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "technical",
        "message": f"Technical timing analysis complete: {analysis.timing_summary}",
        "data": analysis.model_dump(),
    })

    return {
        "agent_results": [AgentResult(
            agent_name="technical",
            status="success",
            data=analysis.model_dump(),
            summary=analysis.summary,
        )],
        "events": events,
    }
