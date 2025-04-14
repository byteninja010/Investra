"""
Document ingestion pipeline for ChromaDB vector store.
Pre-populates market intelligence, sector research, and asset allocation guidelines.
"""

from app.rag.vectorstore import get_vector_store

SEED_DOCUMENTS = [
    {
        "id": "it_sector_outlook_2025",
        "title": "Indian IT Sector Outlook: Margin Expansion & Cloud AI Transition",
        "source": "Global Tech Equity Research Report",
        "sector": "Information Technology",
        "content": (
            "Indian IT leaders like TCS and Infosys are experiencing robust deal momentum driven by enterprise cloud migrations "
            "and generative AI implementations. High return on equity (ROE > 30%), zero net debt, and strong operating cash flows "
            "provide defensive resilience during global macro uncertainties. Valuation multiples trade near historical averages, "
            "making top-tier IT companies a core pillar for long-term growth portfolios."
        ),
    },
    {
        "id": "banking_credit_growth_2025",
        "title": "Indian Private Banking & Credit Expansion Dynamics",
        "source": "National Financial System Quarterly Report",
        "sector": "Banking & Financial Services",
        "content": (
            "Private sector banks including HDFC Bank and ICICI Bank continue to report healthy loan growth across retail and MSME segments. "
            "Gross NPA ratios remain at multi-year lows (< 1.5%), with strong capital adequacy ratios above 16%. "
            "Rising digital penetration and deposit franchise expansion provide long-term compound growth opportunities for balanced portfolios."
        ),
    },
    {
        "id": "energy_industrial_transition_2025",
        "title": "Energy Conglomerates: Cash Generation & Green Transformation",
        "source": "Industrial & Energy Macro Review",
        "sector": "Energy & Conglomerates",
        "content": (
            "Conglomerates like Reliance Industries blend steady cash flows from traditional oil-to-chemicals and retail with aggressive capital "
            "expenditure in 5G telecommunications and renewable energy infrastructure. This creates a balanced risk profile suitable for "
            "medium to long-term investors seeking both cash flow stability and new-economy growth."
        ),
    },
    {
        "id": "fmcg_consumer_stability_2025",
        "title": "Consumer Goods & FMCG: Steady Dividends & Inflation Hedge",
        "source": "Consumer Sector Strategic Briefing",
        "sector": "FMCG / Consumer",
        "content": (
            "FMCG companies such as ITC and Hindustan Unilever offer defensive characteristics with consistent dividend yields (3-5%), "
            "pricing power against raw material inflation, and low debt. During periods of market volatility, FMCG allocations help preserve capital "
            "and reduce portfolio beta."
        ),
    },
    {
        "id": "asset_allocation_principles_2025",
        "title": "Modern Portfolio Theory & Retail Capital Allocation Guidelines",
        "source": "Investment Strategy & Risk Management Handbook",
        "sector": "Portfolio Strategy",
        "content": (
            "For retail portfolios between ₹10,000 to ₹100,000, optimal diversification typically involves 3 to 5 non-correlated large-cap and bluechip assets. "
            "Conservative investors should prioritize low-debt, high-dividend stocks (e.g. FMCG, IT), moderate investors should balance IT, Banking, and Conglomerates (30-40% each), "
            "and aggressive investors can tilt towards high-beta cyclicals while keeping a 5-10% liquid cash buffer for market pullbacks."
        ),
    },
]


def seed_knowledge_base():
    """Seed ChromaDB vector store with initial research documents if empty."""
    store = get_vector_store()
    if store.count() == 0:
        docs = [d["content"] for d in SEED_DOCUMENTS]
        metadatas = [
            {
                "title": d["title"],
                "source": d["source"],
                "sector": d["sector"],
            }
            for d in SEED_DOCUMENTS
        ]
        ids = [d["id"] for d in SEED_DOCUMENTS]
        store.add_documents(documents=docs, metadatas=metadatas, ids=ids)
        print(f"[RAG Ingest] Seeded {len(docs)} documents into ChromaDB.")
    else:
        print(f"[RAG Ingest] ChromaDB already contains {store.count()} documents.")


if __name__ == "__main__":
    seed_knowledge_base()
