"""
Structured output models — Pydantic schemas that enforce well-formed outputs
from each agent via LLM structured generation for Portfolio Investment Allocation.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class CandidateAsset(BaseModel):
    """A candidate asset selected by the Orchestrator for evaluation."""
    ticker: str = Field(description="Stock or ETF ticker (e.g. 'TCS.NS', 'RELIANCE.NS', 'AAPL')")
    name: str = Field(description="Full company or fund name")
    sector: str = Field(description="Industry/Sector (e.g. 'Information Technology', 'Banking', 'Energy')")
    asset_class: str = Field(default="Equity", description="Asset class: Large-cap Equity, Mid-cap Equity, ETF, Cash, etc.")
    selection_rationale: str = Field(description="Why this asset is chosen for the user's specific budget, risk profile, and goal")


class OrchestratorDecision(BaseModel):
    """The orchestrator's investment thesis and candidate asset selection."""
    investment_thesis: str = Field(description="Overarching strategic thesis tailored to amount, risk tolerance, horizon, and goal")
    candidate_assets: list[CandidateAsset] = Field(description="3 to 5 candidate assets to analyze and allocate across")
    agents_to_run: list[str] = Field(
        default=["fundamental", "technical", "risk", "research"],
        description="Which specialist agents to invoke",
    )


# ---------------------------------------------------------------------------
# Fundamental Analysis
# ---------------------------------------------------------------------------

class AssetFundamental(BaseModel):
    """Fundamental metrics & verdict for a specific candidate asset."""
    ticker: str = Field(description="Stock ticker")
    name: str = Field(description="Company name")
    pe_ratio: float | None = Field(None, description="Price-to-Earnings ratio")
    roe: float | None = Field(None, description="Return on Equity (%)")
    profit_margin: float | None = Field(None, description="Profit margin (%)")
    revenue_growth: float | None = Field(None, description="Revenue growth YoY (%)")
    debt_to_equity: float | None = Field(None, description="Debt-to-Equity ratio")
    dividend_yield: float | None = Field(None, description="Dividend yield (%)")
    fundamental_score: str = Field(description="Strong / Moderate / Weak")
    key_strength: str = Field(description="Biggest fundamental strength")
    key_concern: str = Field(description="Biggest fundamental concern")


class FundamentalAnalysis(BaseModel):
    """Structured output from the Fundamental Analysis Agent."""
    asset_evaluations: list[AssetFundamental] = Field(description="Fundamental assessment for each candidate asset")
    top_picks: list[str] = Field(description="Tickers with the strongest fundamentals for the stated goal")
    summary: str = Field(description="2-3 sentence synthesis of fundamental health across the basket")


# ---------------------------------------------------------------------------
# Technical Analysis
# ---------------------------------------------------------------------------

class AssetTechnical(BaseModel):
    """Technical indicators & trend for a specific candidate asset."""
    ticker: str = Field(description="Stock ticker")
    current_price: float | None = Field(None, description="Current price")
    rsi_14: float | None = Field(None, description="14-day RSI")
    trend: str = Field(description="Uptrend / Downtrend / Sideways")
    price_vs_sma50: str = Field(description="Above / Below 50-day moving average")
    macd_signal: str = Field(description="Bullish / Bearish / Neutral")
    entry_timing: str = Field(description="Favorable / Neutral / Caution")


class TechnicalAnalysis(BaseModel):
    """Structured output from the Technical Analysis Agent."""
    asset_evaluations: list[AssetTechnical] = Field(description="Technical assessment for each candidate asset")
    timing_summary: str = Field(description="Timing and momentum overview for allocating capital now")
    summary: str = Field(description="2-3 sentence synthesis of price trends and technical setup")


# ---------------------------------------------------------------------------
# Risk Analysis
# ---------------------------------------------------------------------------

class AssetRisk(BaseModel):
    """Risk profile for a specific candidate asset."""
    ticker: str = Field(description="Stock ticker")
    annualized_volatility: float | None = Field(None, description="Annualized volatility (%)")
    beta: float | None = Field(None, description="Beta vs market benchmark")
    sharpe_ratio: float | None = Field(None, description="Sharpe ratio")
    max_drawdown: float | None = Field(None, description="Maximum drawdown (%)")
    risk_rating: str = Field(description="Low / Moderate / High")


class RiskAnalysis(BaseModel):
    """Structured output from the Risk Agent."""
    asset_risks: list[AssetRisk] = Field(description="Risk metrics for each candidate asset")
    portfolio_risk_level: str = Field(description="Overall portfolio risk level: Low / Moderate / High")
    diversification_score: str = Field(description="Diversification quality: Excellent / Good / Concentrated")
    risk_alignment: str = Field(description="How well this basket fits the user's stated risk tolerance")
    summary: str = Field(description="2-3 sentence summary of portfolio risk factors and downside protections")


# ---------------------------------------------------------------------------
# Research / RAG
# ---------------------------------------------------------------------------

class ResearchFinding(BaseModel):
    """A research insight with source citation."""
    topic_or_asset: str = Field(description="Asset ticker, sector, or macro topic")
    title: str = Field(description="Headline or document title")
    source: str = Field(description="Source URL, document name, or vector store collection")
    snippet: str = Field(description="Relevant evidence or excerpt")
    sentiment: str = Field(description="Positive / Negative / Neutral")


class ResearchAnalysis(BaseModel):
    """Structured output from the Research/RAG Agent."""
    findings: list[ResearchFinding] = Field(description="News and retrieved document findings with sources")
    market_sentiment: str = Field(description="Overall macro and sector sentiment: Bullish / Neutral / Bearish")
    summary: str = Field(description="2-3 sentence synthesis of news catalysts and sector tailwinds")


# ---------------------------------------------------------------------------
# Critic / Synthesis & Final Allocation
# ---------------------------------------------------------------------------

class AllocationItem(BaseModel):
    """Hypothetical allocation item for a specific asset in the portfolio."""
    ticker: str = Field(description="Stock/ETF ticker or 'CASH'")
    name: str = Field(description="Asset name (e.g. 'Tata Consultancy Services', 'Liquid Cash Reserve')")
    asset_class: str = Field(description="Asset category (e.g. 'Large-Cap IT', 'Bluechip Energy', 'Cash')")
    percentage: float = Field(description="Percentage allocation of total budget (e.g. 35.0)", ge=0, le=100)
    allocated_amount: float = Field(description="Calculated monetary amount allocated in user currency (e.g. 3500.0)")
    rationale: str = Field(description="Why this asset is chosen and allocated this specific proportion")
    risk_rating: str = Field(description="Risk level: Low / Moderate / High")


class CritiqueResult(BaseModel):
    """The critic's synthesized portfolio allocation and complete analysis."""
    allocation_plan: list[AllocationItem] = Field(description="Detailed breakdown of recommended capital allocation totaling 100%")
    contradictions: list[str] = Field(description="Contradictions or trade-offs noted between agents (e.g. great fundamentals vs high technical RSI)")
    risk_warnings: list[str] = Field(description="Key caveats, downside risks, and exit triggers")
    confidence_level: str = Field(description="Confidence in this allocation plan: High / Medium / Low")
    needs_reanalysis: bool | None = Field(default=False, description="Whether re-analysis is needed")
    reanalysis_instructions: str | None = Field(default="", description="Instructions for re-analysis if required")
    final_verdict: str = Field(description="Final summary outlook for the proposed portfolio")
    final_report: str = Field(description="Complete structured markdown report with executive summary, allocation table, agent insights, and risks")
