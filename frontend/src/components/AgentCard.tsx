import type { AgentState } from '../types';

interface AgentCardProps {
  agent: AgentState;
  index: number;
}

const STATUS_STYLES: Record<string, { bg: string; border: string; dot: string }> = {
  idle: { bg: 'bg-surface-800/30', border: 'border-white/5', dot: 'bg-surface-200/30' },
  running: { bg: 'bg-primary-900/20', border: 'border-primary-500/30', dot: 'bg-primary-400' },
  complete: { bg: 'bg-accent-green/5', border: 'border-accent-green/30', dot: 'bg-accent-green' },
  error: { bg: 'bg-accent-red/5', border: 'border-accent-red/30', dot: 'bg-accent-red' },
};

export function AgentCard({ agent, index }: AgentCardProps) {
  const styles = STATUS_STYLES[agent.status];
  const lastMessage = agent.messages[agent.messages.length - 1];
  const elapsed = agent.startTime && agent.endTime
    ? ((agent.endTime - agent.startTime) / 1000).toFixed(1) + 's'
    : agent.startTime && agent.status === 'running'
      ? 'Running...'
      : null;

  return (
    <div
      className={`animate-slide-in rounded-xl p-4 border ${styles.bg} ${styles.border} transition-all duration-300`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="flex items-center gap-3 mb-2">
        {/* Status dot */}
        <div className="relative">
          <div className={`w-2.5 h-2.5 rounded-full ${styles.dot} ${agent.status === 'running' ? 'agent-pulse' : ''}`} />
          {agent.status === 'running' && (
            <div className={`absolute inset-0 w-2.5 h-2.5 rounded-full ${styles.dot} animate-ping opacity-40`} />
          )}
        </div>

        {/* Agent icon + name */}
        <span className="text-lg">{agent.icon}</span>
        <span className="text-sm font-semibold text-surface-50">{agent.displayName}</span>

        {/* Elapsed time */}
        {elapsed && (
          <span className="ml-auto text-xs font-mono text-surface-200/40">
            {elapsed}
          </span>
        )}
      </div>

      {/* Latest message */}
      {lastMessage && (
        <p className="text-xs text-surface-200/60 ml-8 line-clamp-2">
          {lastMessage}
        </p>
      )}
    </div>
  );
}
