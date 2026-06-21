from langchain_core.tools import tool

from app.rag.retrieval import search


@tool
def faq_search(query: str) -> dict:
    """Search the Observe Insurance knowledge base for answers to questions about office hours, mailing addresses, claims, insurance plans, coverage, deductibles, premiums, and contact information."""
    results = search(query, k=4)
    if not results:
        return {
            "found": False,
            "message": "I don't have information on that topic. Would you like me to connect you with a representative?",
        }

    context = "\n\n".join(doc.page_content for doc in results)
    sources = list({doc.metadata.get("source", "unknown") for doc in results})
    return {"found": True, "context": context, "sources": sources, "count": len(results)}
