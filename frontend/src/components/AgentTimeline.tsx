import type { AgentState } from '../types';
import { AgentCard } from './AgentCard';

interface AgentTimelineProps {
  agents: AgentState[];
}

export function AgentTimeline({ agents }: AgentTimelineProps) {
  const activeAgents = agents.filter(a => a.status !== 'idle');
  
  if (activeAgents.length === 0) return null;

  const completedCount = agents.filter(a => a.status === 'complete').length;
  const totalActive = agents.filter(a => a.status !== 'idle').length;

  return (
    <div className="w-full max-w-3xl mx-auto mt-6">
      <div className="glass-card p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-surface-50 uppercase tracking-wider">
            Agent Activity
          </h2>
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-24 rounded-full bg-surface-800 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-cyan transition-all duration-500"
                style={{ width: `${totalActive > 0 ? (completedCount / Math.max(totalActive, 1)) * 100 : 0}%` }}
              />
            </div>
            <span className="text-xs font-mono text-surface-200/50">
              {completedCount}/{totalActive}
            </span>
          </div>
        </div>

        {/* Agent cards grid */}
        <div className="grid gap-3">
          {agents.map((agent, i) => (
            <AgentCard key={agent.name} agent={agent} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
