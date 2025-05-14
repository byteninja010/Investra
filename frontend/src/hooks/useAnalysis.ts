/**
 * useAnalysis hook — manages the SSE connection to the backend
 * and tracks agent state, candidate assets, and portfolio allocation for the UI.
 */

import { useState, useCallback, useRef } from 'react';
import type { AgentEvent, AgentState, AgentName, AnalysisStatus, InvestmentProfile, AllocationItem } from '../types';
import { AGENT_CONFIG } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/** Initialize agent tracking state */
function createInitialAgents(): Map<AgentName, AgentState> {
  const agents = new Map<AgentName, AgentState>();
  const agentNames: AgentName[] = ['orchestrator', 'fundamental', 'technical', 'risk', 'research', 'critic'];
  
  for (const name of agentNames) {
    const config = AGENT_CONFIG[name];
    agents.set(name, {
      name,
      displayName: config.displayName,
      icon: config.icon,
      status: 'idle',
      messages: [],
    });
  }
  
  return agents;
}

export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [agents, setAgents] = useState<Map<AgentName, AgentState>>(createInitialAgents);
  const [report, setReport] = useState<string>('');
  const [allocationPlan, setAllocationPlan] = useState<AllocationItem[]>([]);
  const [error, setError] = useState<string>('');
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const updateAgent = useCallback((name: AgentName, update: Partial<AgentState>) => {
    setAgents(prev => {
      const next = new Map(prev);
      const existing = next.get(name);
      if (existing) {
        next.set(name, { ...existing, ...update });
      }
      return next;
    });
  }, []);

  const handleEvent = useCallback((event: AgentEvent) => {
    setEvents(prev => [...prev, event]);
    const agentName = event.agent_name as AgentName;

    switch (event.event_type) {
      case 'agent_start':
        updateAgent(agentName, {
          status: 'running',
          messages: [event.message],
          startTime: Date.now(),
        });
        break;

      case 'agent_progress':
        setAgents(prev => {
          const next = new Map(prev);
          const existing = next.get(agentName);
          if (existing) {
            next.set(agentName, {
              ...existing,
              messages: [...existing.messages, event.message],
            });
          }
          return next;
        });
        break;

      case 'agent_complete':
        setAgents(prev => {
          const next = new Map(prev);
          const existing = next.get(agentName);
          if (existing) {
            next.set(agentName, {
              ...existing,
              status: 'complete',
              messages: [...existing.messages, event.message],
              data: event.data,
              endTime: Date.now(),
            });
          }
          return next;
        });
        break;

      case 'agent_error':
        updateAgent(agentName, {
          status: 'error',
          messages: [...(agents.get(agentName)?.messages || []), `❌ ${event.message}`],
          endTime: Date.now(),
        });
        break;

      case 'report_ready':
        if (event.data?.report) {
          setReport(event.data.report as string);
        }
        if (event.data?.allocation_plan) {
          setAllocationPlan(event.data.allocation_plan as AllocationItem[]);
        }
        break;

      case 'done':
        setStatus('complete');
        break;

      case 'error':
        setError(event.message);
        setStatus('error');
        break;
    }
  }, [updateAgent, agents]);

  const analyze = useCallback(async (input: InvestmentProfile | string) => {
    // Reset state
    setStatus('running');
    setAgents(createInitialAgents());
    setReport('');
    setAllocationPlan([]);
    setError('');
    setEvents([]);

    // Cancel any previous request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const payload = typeof input === 'string' 
      ? { query: input, amount: 10000.0, currency: 'INR', risk_tolerance: 'moderate', horizon: 'medium', goal: 'growth' }
      : {
          amount: input.amount,
          currency: input.currency,
          risk_tolerance: input.riskTolerance,
          horizon: input.horizon,
          goal: input.goal,
          preferences: input.preferences || '',
          query: input.query || '',
        };

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const data = line.slice(5).trim();
            if (data) {
              try {
                const event: AgentEvent = JSON.parse(data);
                handleEvent(event);
              } catch {
                // Skip malformed events
              }
            }
          }
        }
      }

      // Process remaining buffer
      if (buffer.startsWith('data:')) {
        const data = buffer.slice(5).trim();
        if (data) {
          try {
            const event: AgentEvent = JSON.parse(data);
            handleEvent(event);
          } catch {
            // Skip
          }
        }
      }

      setStatus(prev => prev === 'running' ? 'complete' : prev);

    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  }, [handleEvent]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setStatus('idle');
  }, []);

  return {
    status,
    agents: Array.from(agents.values()),
    report,
    allocationPlan,
    error,
    events,
    analyze,
    cancel,
  };
}
