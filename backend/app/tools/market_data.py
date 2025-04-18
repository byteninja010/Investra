"""
Market data tools — yfinance wrappers for fetching stock fundamentals and price data.

These are registered as LangChain tools so agents can call them by name.
All functions return plain dictionaries — no hallucinated numbers.
"""

from langchain_core.tools import tool
import yfinance as yf


@tool
def get_stock_fundamentals(ticker: str) -> dict:
    """Fetch fundamental financial data for a stock ticker.

    Returns key metrics: market cap, revenue, net income, EPS, P/E, P/B,
    ROE, debt-to-equity, dividend yield, profit margins, and revenue growth.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            return {"error": f"No data found for ticker '{ticker}'. Check the symbol."}

        def fmt_large(val):
            """Format large numbers (e.g. 1.2T, 340B)."""
            if val is None:
                return None
            if val >= 1e12:
                return f"₹{val/1e12:.2f}T" if "IN" in ticker.upper() or ".NS" in ticker.upper() or ".BO" in ticker.upper() else f"${val/1e12:.2f}T"
            if val >= 1e9:
                return f"₹{val/1e9:.2f}B" if "IN" in ticker.upper() or ".NS" in ticker.upper() or ".BO" in ticker.upper() else f"${val/1e9:.2f}B"
            if val >= 1e6:
                return f"₹{val/1e6:.2f}M" if "IN" in ticker.upper() or ".NS" in ticker.upper() or ".BO" in ticker.upper() else f"${val/1e6:.2f}M"
            return str(val)

        return {
            "ticker": ticker,
            "company_name": info.get("longName", info.get("shortName", ticker)),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": fmt_large(info.get("marketCap")),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "revenue": fmt_large(info.get("totalRevenue")),
            "net_income": fmt_large(info.get("netIncomeToCommon")),
            "eps_ttm": info.get("trailingEps"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "roe": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
            "debt_to_equity": info.get("debtToEquity"),
            "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
            "profit_margin": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
            "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
            "free_cash_flow": fmt_large(info.get("freeCashflow")),
        }
    except Exception as e:
        return {"error": f"Failed to fetch fundamentals for {ticker}: {str(e)}"}


@tool
def get_stock_price_history(ticker: str, period: str = "1y") -> dict:
    """Fetch historical price data for a stock.

    Args:
        ticker: Stock ticker symbol
        period: Time period — '1mo', '3mo', '6mo', '1y', '2y', '5y'

    Returns dict with dates, prices, and volumes as lists.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No price history for '{ticker}' over period '{period}'."}

        return {
            "ticker": ticker,
            "period": period,
            "data_points": len(hist),
            "dates": [d.strftime("%Y-%m-%d") for d in hist.index],
            "close": hist["Close"].round(2).tolist(),
            "volume": hist["Volume"].tolist(),
            "high": hist["High"].round(2).tolist(),
            "low": hist["Low"].round(2).tolist(),
            "latest_close": round(hist["Close"].iloc[-1], 2),
            "period_high": round(hist["High"].max(), 2),
            "period_low": round(hist["Low"].min(), 2),
        }
    except Exception as e:
        return {"error": f"Failed to fetch price history for {ticker}: {str(e)}"}


@tool
def get_stock_info(ticker: str) -> dict:
    """Fetch general company information — name, sector, description, etc."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("longName", info.get("shortName", ticker)),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary", "")[:500],
            "website": info.get("website"),
            "country": info.get("country"),
            "employees": info.get("fullTimeEmployees"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch info for {ticker}: {str(e)}"}
