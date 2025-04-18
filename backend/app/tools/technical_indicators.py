"""
Technical indicator calculations — deterministic computations, no LLM involved.

Uses the `ta` library for standard indicators and raw numpy/pandas for
anything custom.  Registered as LangChain tools.
"""

from langchain_core.tools import tool
import yfinance as yf
import numpy as np


@tool
def calculate_technical_indicators(ticker: str) -> dict:
    """Calculate technical indicators for a stock: RSI-14, SMA-50, SMA-200, MACD, and price changes.

    Uses 1 year of daily data.  All calculations are deterministic.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty or len(hist) < 50:
            return {"error": f"Insufficient price data for {ticker} to compute indicators."}

        close = hist["Close"]
        volume = hist["Volume"]

        # ── SMA ────────────────────────────────────────────────────────
        sma_50 = round(close.rolling(window=50).mean().iloc[-1], 2)
        sma_200 = round(close.rolling(window=200).mean().iloc[-1], 2) if len(close) >= 200 else None

        # ── RSI (14-day) ───────────────────────────────────────────────
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_14 = round(rsi_series.iloc[-1], 2)

        # ── MACD (12, 26, 9) ──────────────────────────────────────────
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_histogram = macd_line - signal_line

        # ── Price changes ──────────────────────────────────────────────
        current_price = round(close.iloc[-1], 2)
        price_1m_ago = close.iloc[-22] if len(close) >= 22 else close.iloc[0]
        price_3m_ago = close.iloc[-66] if len(close) >= 66 else close.iloc[0]
        change_1m = round((current_price - price_1m_ago) / price_1m_ago * 100, 2)
        change_3m = round((current_price - price_3m_ago) / price_3m_ago * 100, 2)

        # ── 52-week high/low ───────────────────────────────────────────
        high_52w = round(hist["High"].max(), 2)
        low_52w = round(hist["Low"].min(), 2)

        # ── Volume ─────────────────────────────────────────────────────
        avg_volume_20d = round(volume.tail(20).mean(), 0)

        return {
            "ticker": ticker,
            "current_price": current_price,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi_14": rsi_14,
            "macd": round(macd_line.iloc[-1], 4),
            "macd_signal": round(signal_line.iloc[-1], 4),
            "macd_histogram": round(macd_histogram.iloc[-1], 4),
            "price_change_1m_pct": change_1m,
            "price_change_3m_pct": change_3m,
            "fifty_two_week_high": high_52w,
            "fifty_two_week_low": low_52w,
            "avg_volume_20d": avg_volume_20d,
            "price_vs_sma50": "above" if current_price > sma_50 else "below",
            "price_vs_sma200": ("above" if current_price > sma_200 else "below") if sma_200 else "N/A",
            "rsi_signal": "overbought" if rsi_14 > 70 else ("oversold" if rsi_14 < 30 else "neutral"),
            "macd_signal_cross": "bullish" if macd_histogram.iloc[-1] > 0 else "bearish",
        }
    except Exception as e:
        return {"error": f"Failed to calculate indicators for {ticker}: {str(e)}"}
