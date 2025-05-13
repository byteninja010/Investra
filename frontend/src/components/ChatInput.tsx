import { useState, type FormEvent } from 'react';
import type { InvestmentProfile } from '../types';

interface ChatInputProps {
  onSubmit: (profile: InvestmentProfile) => void;
  isLoading: boolean;
  onCancel: () => void;
}

const PRESETS = [
  {
    label: "₹10k Balanced Growth (1-3 yrs)",
    profile: {
      amount: 10000,
      currency: "INR" as const,
      riskTolerance: "moderate" as const,
      horizon: "medium" as const,
      goal: "growth" as const,
      preferences: "Bluechip leaders across IT, Banking, and Energy",
    }
  },
  {
    label: "₹25k Dividend & Passive Income",
    profile: {
      amount: 25000,
      currency: "INR" as const,
      riskTolerance: "low" as const,
      horizon: "long" as const,
      goal: "income" as const,
      preferences: "High dividend yield & defensive FMCG/PSU",
    }
  },
  {
    label: "₹50k Long-Term Tech Compounder",
    profile: {
      amount: 50000,
      currency: "INR" as const,
      riskTolerance: "high" as const,
      horizon: "long" as const,
      goal: "aggressive" as const,
      preferences: "High ROE IT, digital infrastructure & clean energy",
    }
  },
  {
    label: "₹10k Low Risk Capital Preservation",
    profile: {
      amount: 10000,
      currency: "INR" as const,
      riskTolerance: "low" as const,
      horizon: "short" as const,
      goal: "preservation" as const,
      preferences: "Large-cap bluechips with stable cash flows",
    }
  },
];

const QUICK_AMOUNTS_INR = [5000, 10000, 25000, 50000, 100000];
const QUICK_AMOUNTS_USD = [1000, 2500, 5000, 10000];

export function ChatInput({ onSubmit, isLoading, onCancel }: ChatInputProps) {
  const [amount, setAmount] = useState<number>(10000);
  const [currency, setCurrency] = useState<'INR' | 'USD'>('INR');
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'moderate' | 'high'>('moderate');
  const [horizon, setHorizon] = useState<'short' | 'medium' | 'long'>('medium');
  const [goal, setGoal] = useState<'growth' | 'preservation' | 'income' | 'aggressive'>('growth');
  const [preferences, setPreferences] = useState<string>('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (amount > 0 && !isLoading) {
      onSubmit({
        amount,
        currency,
        riskTolerance,
        horizon,
        goal,
        preferences,
      });
    }
  };

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setAmount(preset.profile.amount);
    setCurrency(preset.profile.currency);
    setRiskTolerance(preset.profile.riskTolerance);
    setHorizon(preset.profile.horizon);
    setGoal(preset.profile.goal);
    setPreferences(preset.profile.preferences);
  };

  const currSymbol = currency === 'INR' ? '₹' : '$';
  const quickAmounts = currency === 'INR' ? QUICK_AMOUNTS_INR : QUICK_AMOUNTS_USD;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="glass-card gradient-border p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <span className="text-2xl">💼</span>
            <div>
              <h2 className="text-base font-bold text-surface-50">Investment Profile & Goal</h2>
              <p className="text-xs text-surface-200/50">Tell the agents what you have to invest and your expectations</p>
            </div>
          </div>

          {/* Currency Toggle */}
          <div className="flex items-center bg-surface-900/80 p-1 rounded-lg border border-white/5">
            <button
              type="button"
              onClick={() => setCurrency('INR')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                currency === 'INR' ? 'bg-primary-600 text-white shadow-sm' : 'text-surface-200/50 hover:text-surface-200'
              }`}
            >
              ₹ INR (India)
            </button>
            <button
              type="button"
              onClick={() => setCurrency('USD')}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                currency === 'USD' ? 'bg-primary-600 text-white shadow-sm' : 'text-surface-200/50 hover:text-surface-200'
              }`}
            >
              $ USD (US)
            </button>
          </div>
        </div>

        {/* Amount Input & Quick Chips */}
        <div className="mb-6">
          <label className="block text-xs font-medium text-surface-200/70 mb-2">
            HOW MUCH CAPITAL DO YOU WANT TO INVEST?
          </label>
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg font-bold text-primary-400">
                {currSymbol}
              </span>
              <input
                id="investment-amount"
                type="number"
                min={0}
                step={500}
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value) || 0)}
                disabled={isLoading}
                placeholder="10000"
                className="w-full bg-surface-900/90 pl-10 pr-4 py-3 rounded-xl text-xl font-bold text-surface-50 border border-white/10 focus:border-primary-500 focus:outline-none"
              />
            </div>
            <div className="flex items-center gap-1.5 overflow-x-auto py-1">
              {quickAmounts.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setAmount(q)}
                  className={`px-3 py-2 rounded-lg text-xs font-mono font-medium border transition-all cursor-pointer ${
                    amount === q
                      ? 'bg-primary-500/20 border-primary-500/50 text-primary-300'
                      : 'bg-surface-800/40 border-white/5 text-surface-200/60 hover:text-surface-200'
                  }`}
                >
                  {currSymbol}{q >= 1000 ? `${q / 1000}k` : q}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 3 Grid Selectors: Risk, Horizon, Goal */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Risk Tolerance */}
          <div>
            <label className="block text-xs font-medium text-surface-200/70 mb-2">
              RISK TOLERANCE
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { key: 'low', label: 'Low', icon: '🛡️' },
                { key: 'moderate', label: 'Moderate', icon: '⚖️' },
                { key: 'high', label: 'High', icon: '🚀' },
              ].map((r) => (
                <button
                  key={r.key}
                  type="button"
                  onClick={() => setRiskTolerance(r.key as any)}
                  className={`py-2 px-1 text-center rounded-lg text-xs font-medium border transition-all cursor-pointer flex flex-col items-center gap-1 ${
                    riskTolerance === r.key
                      ? 'bg-primary-500/20 border-primary-500/50 text-primary-300 font-semibold'
                      : 'bg-surface-800/40 border-white/5 text-surface-200/50 hover:text-surface-200'
                  }`}
                >
                  <span>{r.icon}</span>
                  <span>{r.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Investment Horizon */}
          <div>
            <label className="block text-xs font-medium text-surface-200/70 mb-2">
              TIME HORIZON
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { key: 'short', label: '< 1 Year', sub: 'Short' },
                { key: 'medium', label: '1 - 3 Yrs', sub: 'Medium' },
                { key: 'long', label: '3 - 5+ Yrs', sub: 'Long' },
              ].map((h) => (
                <button
                  key={h.key}
                  type="button"
                  onClick={() => setHorizon(h.key as any)}
                  className={`py-2 px-1 text-center rounded-lg text-xs font-medium border transition-all cursor-pointer flex flex-col items-center gap-0.5 ${
                    horizon === h.key
                      ? 'bg-primary-500/20 border-primary-500/50 text-primary-300 font-semibold'
                      : 'bg-surface-800/40 border-white/5 text-surface-200/50 hover:text-surface-200'
                  }`}
                >
                  <span className="font-semibold">{h.label}</span>
                  <span className="text-[10px] opacity-60">{h.sub}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Investment Goal */}
          <div>
            <label className="block text-xs font-medium text-surface-200/70 mb-2">
              PRIMARY GOAL
            </label>
            <select
              value={goal}
              onChange={(e) => setGoal(e.target.value as any)}
              className="w-full bg-surface-900/90 text-surface-50 border border-white/10 rounded-lg px-3 py-2.5 text-xs font-medium focus:border-primary-500 focus:outline-none"
            >
              <option value="growth">📈 Balanced Wealth Growth</option>
              <option value="preservation">🛡️ Capital Preservation</option>
              <option value="income">💵 Dividends & Passive Income</option>
              <option value="aggressive">🚀 Aggressive Capital Appreciation</option>
            </select>
          </div>
        </div>

        {/* Optional Custom Preferences */}
        <div className="mb-6">
          <label className="block text-xs font-medium text-surface-200/70 mb-1.5">
            OPTIONAL PREFERENCES / SECTOR CONSTRAINTS
          </label>
          <input
            type="text"
            value={preferences}
            onChange={(e) => setPreferences(e.target.value)}
            placeholder="e.g., 'Focus on Indian IT and Bluechip Banking' or 'Include high dividend FMCG'"
            className="w-full bg-surface-900/60 px-4 py-2.5 rounded-xl text-xs text-surface-50 placeholder:text-surface-200/30 border border-white/5 focus:border-primary-500 focus:outline-none"
          />
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-4 border-t border-white/5">
          <div className="text-xs text-surface-200/40 font-mono">
            {currSymbol}{amount.toLocaleString()} capital • {riskTolerance} risk • {horizon} horizon
          </div>

          {isLoading ? (
            <button
              type="button"
              onClick={onCancel}
              className="px-5 py-2.5 rounded-xl bg-accent-red/20 text-accent-red text-sm font-semibold hover:bg-accent-red/30 transition-colors cursor-pointer"
            >
              Cancel Analysis
            </button>
          ) : (
            <button
              type="submit"
              disabled={amount <= 0}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary-600 to-accent-cyan text-white text-sm font-bold shadow-lg shadow-primary-500/20 hover:brightness-110 disabled:opacity-30 disabled:cursor-not-allowed transition-all cursor-pointer"
            >
              Generate Portfolio Allocation →
            </button>
          )}
        </div>
      </form>

      {/* Preset Examples */}
      {!isLoading && (
        <div className="mt-4">
          <div className="text-center text-xs text-surface-200/40 mb-2">Or try a ready-to-run profile:</div>
          <div className="flex flex-wrap gap-2 justify-center">
            {PRESETS.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => applyPreset(p)}
                className="px-3 py-1.5 rounded-full text-xs text-surface-200/70 border border-white/5 bg-surface-900/40 hover:border-primary-500/40 hover:text-primary-300 transition-all cursor-pointer"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
