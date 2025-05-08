import { ChatInput } from './components/ChatInput';
import { AgentTimeline } from './components/AgentTimeline';
import { AnalysisReport } from './components/AnalysisReport';
import { useAnalysis } from './hooks/useAnalysis';
import './index.css';

function App() {
  const { status, agents, report, allocationPlan, error, analyze, cancel } = useAnalysis();

  return (
    <div className="min-h-screen bg-surface-950 flex flex-col selection:bg-primary-500 selection:text-white">
      {/* Header */}
      <header className="pt-10 pb-6 px-6 text-center">
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary-500 via-accent-cyan to-accent-green flex items-center justify-center text-2xl shadow-lg shadow-primary-500/20">
            💼
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold gradient-text tracking-tight">
            AI Portfolio Investment Advisor
          </h1>
        </div>
        <p className="text-surface-200/60 text-sm max-w-xl mx-auto mb-4">
          Tell us how much you have to invest. Six specialized AI agents collaborate with real market data, ChromaDB RAG, and deterministic risk metrics to build your personalized asset allocation.
        </p>

        {/* 6 Collaborative Agents Badges */}
        <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
          {[
            { name: '🎯 Strategy Orchestrator', desc: 'Asset Selection' },
            { name: '📊 Fundamental Screening', desc: 'Valuation & Health' },
            { name: '📈 Technical Timing', desc: 'Entry Momentum' },
            { name: '🔍 Research & RAG', desc: 'News & ChromaDB' },
            { name: '⚠️ Risk Management', desc: 'Beta & Sharpe' },
            { name: '🧪 Synthesis & Critic', desc: 'Capital Allocation' },
          ].map(badge => (
            <span
              key={badge.name}
              className="px-3 py-1 rounded-lg text-xs font-medium bg-surface-900/80 text-surface-200/70 border border-white/5 shadow-sm"
              title={badge.desc}
            >
              {badge.name}
            </span>
          ))}
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 px-4 sm:px-6 pb-16 max-w-5xl mx-auto w-full">
        <ChatInput
          onSubmit={analyze}
          isLoading={status === 'running'}
          onCancel={cancel}
        />

        {/* Error Alert */}
        {error && (
          <div className="w-full max-w-4xl mx-auto mt-6">
            <div className="rounded-2xl p-4 bg-accent-red/10 border border-accent-red/30 text-accent-red text-sm flex items-start gap-3">
              <span className="text-lg">⚠️</span>
              <div>
                <strong className="font-bold">Analysis Notice:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* Agent Activity Timeline */}
        {status !== 'idle' && (
          <AgentTimeline agents={agents} />
        )}

        {/* Final Report & Portfolio Allocation */}
        {(report || allocationPlan.length > 0) && (
          <AnalysisReport report={report} allocationPlan={allocationPlan} />
        )}

        {/* Success Completion Badge */}
        {status === 'complete' && report && (
          <div className="w-full max-w-4xl mx-auto mt-6 text-center">
            <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-semibold bg-accent-green/10 text-accent-green border border-accent-green/30 shadow-md">
              ✓ Multi-Agent Portfolio Allocation Ready
            </span>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-surface-200/30 border-t border-white/5">
        Multi-Agent Finance Investment System • LangGraph + ChromaDB RAG + FastAPI + React • Demo & Educational
      </footer>
    </div>
  );
}

export default App;
