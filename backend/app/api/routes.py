"""
API routes — exposes the investment allocation analysis endpoint with SSE streaming.

The /analyze endpoint:
  1. Accepts an investment profile (amount, currency, risk tolerance, horizon, goal, preferences).
  2. Runs the LangGraph multi-agent workflow.
  3. Streams agent events & candidate research to the frontend via Server-Sent Events.
"""

import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import AnalysisRequest
from app.graph.workflow import workflow

router = APIRouter()


async def event_generator(req: AnalysisRequest):
    """Run the LangGraph workflow and yield SSE events as agents produce them."""
    try:
        curr_symbol = "₹" if req.currency == "INR" else "$"
        profile_desc = f"{curr_symbol}{req.amount:,.0f} | Risk: {req.risk_tolerance.title()} | Horizon: {req.horizon.title()} | Goal: {req.goal.title()}"

        # Initial event
        yield {
            "event": "agent_event",
            "data": json.dumps({
                "event_type": "analysis_started",
                "agent_name": "system",
                "message": f"Starting multi-agent portfolio analysis for {profile_desc}...",
            }),
        }

        # Initial LangGraph state
        initial_state = {
            "amount": req.amount,
            "currency": req.currency,
            "risk_tolerance": req.risk_tolerance,
            "horizon": req.horizon,
            "goal": req.goal,
            "preferences": req.preferences or req.query,
            "query": req.query or f"Where should I invest {curr_symbol}{req.amount:,.0f} with {req.risk_tolerance} risk?",
            "candidate_assets": [],
            "investment_thesis": "",
            "agents_to_run": ["fundamental", "technical", "risk", "research"],
            "agent_results": [],
            "events": [],
            "critique": "",
            "needs_reanalysis": False,
            "reanalysis_instructions": "",
            "reanalysis_count": 0,
            "allocation_plan": [],
            "final_report": "",
        }

        # Stream through graph execution
        async for state_update in workflow.astream(
            initial_state,
            stream_mode="updates",
        ):
            for node_name, changes in state_update.items():
                if not isinstance(changes, dict):
                    continue

                # Stream any new events emitted by this node
                new_events = changes.get("events", [])
                for event in new_events:
                    yield {
                        "event": "agent_event",
                        "data": json.dumps(event, default=str),
                    }

                # If this node produced the final report / allocation, stream report_ready
                if "final_report" in changes and changes["final_report"]:
                    yield {
                        "event": "report_ready",
                        "data": json.dumps({
                            "event_type": "report_ready",
                            "agent_name": "critic",
                            "message": "Portfolio allocation plan ready",
                            "data": {
                                "report": changes["final_report"],
                                "allocation_plan": changes.get("allocation_plan", []),
                                "amount": req.amount,
                                "currency": req.currency,
                            },
                        }),
                    }

        # Completion event
        yield {
            "event": "done",
            "data": json.dumps({
                "event_type": "done",
                "agent_name": "system",
                "message": "All specialist agents completed successfully.",
            }),
        }

    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({
                "event_type": "error",
                "agent_name": "system",
                "message": f"Investment analysis failed: {str(e)}",
            }),
        }


@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    """Start an investment portfolio allocation analysis and stream results via SSE."""
    return EventSourceResponse(
        event_generator(request),
        media_type="text/event-stream",
    )


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "finance-portfolio-agents"}
