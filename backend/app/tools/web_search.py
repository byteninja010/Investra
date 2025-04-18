"""
Web search tool — wraps Tavily for financial news search.

Phase 1: Returns a stub if no Tavily key is configured.
Phase 2: Full integration with RAG.
"""

from langchain_core.tools import tool
from app.config import get_settings


@tool
def search_financial_news(query: str, max_results: int = 5) -> dict:
    """Search for recent financial news about a company or topic.

    Args:
        query: Search query (e.g. 'TCS quarterly results 2024')
        max_results: Number of results to return (default 5)
    """
    settings = get_settings()

    if not settings.TAVILY_API_KEY:
        return {
            "source": "stub",
            "message": "Tavily API key not configured. Using placeholder results.",
            "results": [
                {
                    "title": f"[Stub] Recent news about: {query}",
                    "url": "https://example.com",
                    "content": "News search is not yet configured. Add TAVILY_API_KEY to .env to enable real search.",
                    "sentiment": "neutral",
                }
            ],
        }

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(
            query=query,
            topic="news",
            days=30,
            search_depth="basic",
            max_results=max_results,
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
            })

        return {
            "source": "tavily",
            "query": query,
            "results": results,
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
