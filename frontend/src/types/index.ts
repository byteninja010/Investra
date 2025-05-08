/**
 * TypeScript types for the Multi-Agent Finance Investment Allocation System.
 */

/** User investment profile */
export interface InvestmentProfile {
  amount: number;
  currency: 'INR' | 'USD';
  riskTolerance: 'low' | 'moderate' | 'high';
  horizon: 'short' | 'medium' | 'long';
  goal: 'growth' | 'preservation' | 'income' | 'aggressive';
  preferences?: string;
  query?: string;
}

/** Structured allocation item returned from the critic */
export interface AllocationItem {
  ticker: string;
  name: string;
  asset_class: string;
  percentage: number;
  allocated_amount: number;
  rationale: string;
  risk_rating: string;
}

/** Agent names in the system */
export type AgentName = 
  | 'system'
  | 'orchestrator'
  | 'fundamental'
  | 'technical'
  | 'risk'
  | 'research'
  | 'critic';

/** Event types emitted by the SSE stream */
export type EventType =
  | 'analysis_started'
  | 'agent_start'
  | 'agent_progress'
  | 'agent_complete'
  | 'agent_error'
  | 'report_ready'
  | 'done'
  | 'error';

/** Single SSE event from the backend */
export interface AgentEvent {
  event_type: EventType;
  agent_name: AgentName;
  message: string;
  data?: Record<string, unknown>;
}

/** Status of an individual agent */
export type AgentStatus = 'idle' | 'running' | 'complete' | 'error';

/** Tracked state for one agent in the UI */
export interface AgentState {
  name: AgentName;
  displayName: string;
  icon: string;
  status: AgentStatus;
  messages: string[];
  data?: Record<string, unknown>;
  startTime?: number;
  endTime?: number;
}

/** Overall analysis state */
export type AnalysisStatus = 'idle' | 'running' | 'complete' | 'error';

/** Agent display configuration */
export const AGENT_CONFIG: Record<AgentName, { displayName: string; icon: string; description: string }> = {
  system: { displayName: 'System', icon: '⚙️', description: 'System coordinator' },
  orchestrator: { displayName: 'Strategy Orchestrator', icon: '🎯', description: 'Formulates investment thesis & picks candidates' },
  fundamental: { displayName: 'Fundamental Screening', icon: '📊', description: 'Valuation, P/E, ROE, margins & dividends' },
  technical: { displayName: 'Technical Timing', icon: '📈', description: 'RSI, 50/200 SMAs & entry momentum' },
  risk: { displayName: 'Risk Assessment', icon: '⚠️', description: 'Volatility, beta, Sharpe ratio & diversification' },
  research: { displayName: 'Research & RAG', icon: '🔍', description: 'ChromaDB sector reports & live news search' },
  critic: { displayName: 'Synthesis & Allocation', icon: '🧪', description: 'Resolves conflicts & computes capital allocation' },
};
