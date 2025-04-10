"""
API request/response schemas — what the frontend sends and receives.
"""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Incoming investment allocation request from the frontend."""
    amount: float = Field(default=10000.0, description="Total amount to invest", ge=100)
    currency: str = Field(default="INR", description="Currency symbol/code: INR or USD")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance: low | moderate | high")
    horizon: str = Field(default="medium", description="Investment horizon: short (<1yr) | medium (1-3yrs) | long (3-5+yrs)")
    goal: str = Field(default="growth", description="Investment goal: growth | preservation | income | aggressive")
    preferences: str = Field(default="", description="Optional user preferences or specific sectors/stocks to evaluate")
    query: str = Field(default="", description="Optional free-form query or question")


class AgentEvent(BaseModel):
    """A single SSE event sent to the frontend during analysis."""
    event_type: str = Field(description="Event type: agent_start | agent_progress | agent_complete | agent_error | report_ready | done | error")
    agent_name: str = Field(description="Which agent emitted this event")
    message: str = Field(default="", description="Human-readable status message")
    data: dict | None = Field(default=None, description="Structured payload (candidate assets, agent results, allocation plan, report, etc.)")


class AllocationItem(BaseModel):
    """A single asset allocation in the recommended portfolio."""
    ticker: str = Field(description="Stock or ETF ticker")
    name: str = Field(description="Asset or company name")
    asset_type: str = Field(description="Equity, Debt, ETF, Cash, etc.")
    percentage: float = Field(description="Percentage allocation of total capital (0-100)")
    amount: float = Field(description="Allocated amount in user currency")
    rationale: str = Field(description="Why this asset is chosen and allocated this amount")
    risk_level: str = Field(description="Low / Moderate / High")


class AnalysisResponse(BaseModel):
    """Final response after all agents complete (non-streaming fallback)."""
    amount: float
    currency: str
    risk_tolerance: str
    horizon: str
    goal: str
    allocation_plan: list[AllocationItem]
    final_report: str
    agent_results: list[dict]

