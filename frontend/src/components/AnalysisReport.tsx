import type { AllocationItem } from '../types';

interface AnalysisReportProps {
  report: string;
  allocationPlan?: AllocationItem[];
}

const ASSET_COLORS = [
  'bg-primary-500',
  'bg-accent-cyan',
  'bg-accent-green',
  'bg-accent-purple',
  'bg-accent-amber',
];

export function AnalysisReport({ report, allocationPlan = [] }: AnalysisReportProps) {
  if (!report && (!allocationPlan || allocationPlan.length === 0)) return null;

  const html = markdownToHtml(report);

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 animate-slide-in">
      {/* 1. Visual Portfolio Allocation Cards (if structured plan exists) */}
      {allocationPlan && allocationPlan.length > 0 && (
        <div className="glass-card gradient-border p-6 mb-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
            <div className="flex items-center gap-2.5">
              <span className="text-xl">💰</span>
              <h2 className="text-base font-bold text-surface-50">Hypothetical Capital Allocation</h2>
            </div>
            <span className="text-xs font-mono text-accent-green bg-accent-green/10 px-2.5 py-1 rounded-full border border-accent-green/20">
              100% Allocated
            </span>
          </div>

          {/* Allocation Visual Bar */}
          <div className="h-3 w-full rounded-full bg-surface-900 overflow-hidden flex mb-6 p-0.5 border border-white/5">
            {allocationPlan.map((item, idx) => (
              <div
                key={item.ticker + idx}
                className={`${ASSET_COLORS[idx % ASSET_COLORS.length]} h-full first:rounded-l-full last:rounded-r-full transition-all duration-700`}
                style={{ width: `${item.percentage}%` }}
                title={`${item.name} (${item.ticker}): ${item.percentage}%`}
              />
            ))}
          </div>

          {/* Allocation Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {allocationPlan.map((item, idx) => (
              <div
                key={item.ticker + idx}
                className="bg-surface-900/80 p-4 rounded-xl border border-white/5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-mono font-bold text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded">
                      {item.ticker}
                    </span>
                    <span className="text-sm font-extrabold text-surface-50">
                      {item.percentage}%
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-surface-50 line-clamp-1 mb-1">{item.name}</h3>
                  <div className="text-[11px] text-surface-200/50 mb-2">{item.asset_class}</div>
                  <p className="text-xs text-surface-200/70 line-clamp-2 mb-3">{item.rationale}</p>
                </div>

                <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-surface-200/40">Allocated</span>
                  <span className="font-mono font-bold text-accent-green">
                    ₹{item.allocated_amount ? item.allocated_amount.toLocaleString() : '-'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 2. Comprehensive Synthesis Report */}
      {report && (
        <div className="glass-card p-8 rounded-2xl">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5">
            <div className="flex items-center gap-3">
              <span className="text-xl">📋</span>
              <h2 className="text-lg font-bold text-surface-50">Detailed Multi-Agent Research Synthesis</h2>
            </div>
            <button
              type="button"
              onClick={() => navigator.clipboard.writeText(report)}
              className="text-xs text-surface-200/50 hover:text-primary-300 transition-colors cursor-pointer flex items-center gap-1 border border-white/5 px-3 py-1.5 rounded-lg bg-surface-900/60"
            >
              <span>📋</span> Copy Report
            </button>
          </div>
          <div
            className="report-content prose prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
      )}
    </div>
  );
}

/** Markdown to HTML parser for headers, bold, lists, tables, and paragraphs */
function markdownToHtml(md: string): string {
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Markdown Tables
  html = html.replace(/\n\|(.+)\|\n\|[-:| ]+\|\n((?:\|.+\|\n?)+)/g, (_, header, body) => {
    const headers = header.split('|').filter((h: string) => h.trim()).map((h: string) => `<th class="px-3 py-2 text-left font-semibold text-surface-50 border-b border-white/10 bg-surface-900/50">${h.trim()}</th>`).join('');
    const rows = body.trim().split('\n').map((row: string) => {
      const cols = row.split('|').filter((c: string) => c.trim()).map((c: string) => `<td class="px-3 py-2 border-b border-white/5 text-surface-200/80">${c.trim()}</td>`).join('');
      return `<tr class="hover:bg-white/[0.02]">${cols}</tr>`;
    }).join('');
    return `<div class="overflow-x-auto my-4 rounded-xl border border-white/5"><table class="w-full text-xs font-sans">${`<thead><tr>${headers}</tr></thead><tbody>${rows}</tbody>`}</table></div>`;
  });

  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Bold & Italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr/>');

  // Unordered lists
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>(\n|$))+/g, (match) => `<ul>${match}</ul>`);

  // Paragraphs
  html = html.replace(/^(?!<[hldut])((?!<).+)$/gm, '<p>$1</p>');
  html = html.replace(/<p>\s*<\/p>/g, '');

  return html;
}
