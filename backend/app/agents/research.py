"""
Research & RAG Agent — combines live financial news search with ChromaDB vector store retrieval.

Queries:
1. ChromaDB vector store for stored sector reports, macro dynamics, and allocation principles.
2. Tavily web search for recent news catalysts and market sentiment.
Produces structured findings with sources and citations.
"""

from app.config import get_llm
from app.models.state import AgentState, AgentResult
from app.models.agent_outputs import ResearchAnalysis
from app.tools.web_search import search_financial_news
from app.rag.vectorstore import get_vector_store
from app.rag.ingest import seed_knowledge_base

SYSTEM_PROMPT = """\
You are the Senior Research & Intelligence Specialist in a multi-agent investment allocation system.

You receive two types of ground-truth research:
1. [RAG Vector Store Documents]: Stored research reports on sector dynamics, macroeconomic trends, and asset allocation.
2. [Live Web Search Results]: Recent news headlines and catalysts regarding the candidate assets and market.

Your goal is to:
1. Extract 3 to 5 key findings across the candidate assets and their sectors.
2. Cite the source title/URL for every claim.
3. Assess overall market sentiment (Bullish / Neutral / Bearish).
4. Summarize the research takeaways in 2-3 concise sentences.

Never invent news or citations. Rely only on the provided context.
"""


async def research_node(state: AgentState) -> dict:
    """Retrieve sector intelligence from ChromaDB and live news via Tavily."""
    candidates = state.get("candidate_assets", [])
    if not candidates:
        return {
            "agent_results": [AgentResult(agent_name="research", status="skipped", summary="No candidate assets provided")],
            "events": [],
        }

    events = [{
        "event_type": "agent_start",
        "agent_name": "research",
        "message": f"Querying ChromaDB vector store and live financial news for candidate assets...",
    }]

    # Ensure vector store is seeded
    try:
        seed_knowledge_base()
    except Exception as e:
        print(f"[Research Node] Seed notice: {e}")

    store = get_vector_store()
    rag_docs = []

    # 1. RAG Query: Search ChromaDB for relevant sector & asset allocation documents
    sectors = list(set([c.get("sector", "") for c in candidates if c.get("sector")]))
    rag_query = f"Asset allocation and sector outlook for {' '.join(sectors)}"
    retrieved = store.search(query=rag_query, n_results=3)

    for doc in retrieved:
        rag_docs.append({
            "type": "RAG Document",
            "title": doc.get("title", "Sector Report"),
            "source": doc.get("source", "ChromaDB Knowledge Base"),
            "content": doc.get("content", ""),
        })

    events.append({
        "event_type": "agent_progress",
        "agent_name": "research",
        "message": f"Retrieved {len(rag_docs)} RAG knowledge documents from ChromaDB...",
    })

    # 2. Web Search: Search for top candidates' news via Tavily
    candidate_tickers = [c.get("ticker", "").replace(".NS", "").replace(".BO", "") for c in candidates[:3]]
    search_query = f"{' '.join(candidate_tickers)} stock earnings news outlook"
    search_res = search_financial_news.invoke({"query": search_query, "max_results": 4})
    web_results = search_res.get("results", [])

    events.append({
        "event_type": "agent_progress",
        "agent_name": "research",
        "message": f"Synthesizing RAG sector reports and live news sentiment...",
    })

    combined_context = (
        f"=== CHROMADB RAG RETRIEVED DOCUMENTS ===\n{rag_docs}\n\n"
        f"=== LIVE WEB SEARCH RESULTS ===\n{web_results}\n\n"
        f"Candidate Assets:\n{candidates}"
    )

    llm = get_llm()
    structured_llm = llm.with_structured_output(ResearchAnalysis)

    analysis: ResearchAnalysis = await structured_llm.ainvoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze these RAG and search findings:\n\n{combined_context}"},
    ])

    events.append({
        "event_type": "agent_complete",
        "agent_name": "research",
        "message": f"Research complete. Sentiment: {analysis.market_sentiment} ({len(analysis.findings)} cited findings)",
        "data": analysis.model_dump(),
    })

    return {
        "agent_results": [AgentResult(
            agent_name="research",
            status="success",
            data=analysis.model_dump(),
            summary=analysis.summary,
        )],
        "events": events,
    }
