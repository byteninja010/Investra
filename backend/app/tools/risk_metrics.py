"""
Risk metric calculations — deterministic, using historical price data.

Computes volatility, beta (vs a market index), Sharpe ratio,
max drawdown, and Value-at-Risk.
"""

from langchain_core.tools import tool
import yfinance as yf
import numpy as np


@tool
def calculate_risk_metrics(ticker: str, benchmark: str = "^NSEI") -> dict:
    """Calculate risk metrics for a stock relative to a benchmark index.

    Args:
        ticker: Stock ticker symbol
        benchmark: Market index ticker (default: ^NSEI for Nifty 50; use ^GSPC for S&P 500)

    Returns volatility, beta, Sharpe ratio, max drawdown, and VaR.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty or len(hist) < 30:
            return {"error": f"Insufficient data for {ticker}."}

        close = hist["Close"]
        returns = close.pct_change().dropna()

        # ── Volatility ─────────────────────────────────────────────────
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)

        # ── Beta ───────────────────────────────────────────────────────
        beta = None
        try:
            bench = yf.Ticker(benchmark)
            bench_hist = bench.history(period="1y")
            if not bench_hist.empty:
                bench_returns = bench_hist["Close"].pct_change().dropna()
                # Align dates
                common = returns.index.intersection(bench_returns.index)
                if len(common) > 30:
                    r = returns.loc[common]
                    b = bench_returns.loc[common]
                    cov = np.cov(r, b)
                    beta = round(cov[0, 1] / cov[1, 1], 3)
        except Exception:
            pass  # beta stays None if benchmark fetch fails

        # ── Sharpe Ratio (assuming risk-free rate ≈ 6% for India) ─────
        risk_free_daily = 0.06 / 252
        excess_returns = returns - risk_free_daily
        sharpe = round((excess_returns.mean() / excess_returns.std()) * np.sqrt(252), 3) if excess_returns.std() > 0 else None

        # ── Max Drawdown ───────────────────────────────────────────────
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = round(drawdown.min() * 100, 2)

        # ── Value at Risk (95%) ────────────────────────────────────────
        var_95 = round(np.percentile(returns, 5) * 100, 3)

        return {
            "ticker": ticker,
            "benchmark": benchmark,
            "daily_volatility": round(daily_vol * 100, 4),
            "annualized_volatility": round(annual_vol * 100, 2),
            "beta": beta,
            "sharpe_ratio": sharpe,
            "max_drawdown_pct": max_drawdown,
            "var_95_daily_pct": var_95,
            "data_points": len(returns),
            "period": "1 year",
        }
    except Exception as e:
        return {"error": f"Failed to calculate risk metrics for {ticker}: {str(e)}"}
