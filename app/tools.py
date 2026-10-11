from app.vector_store import search_knowledge


def search_knowledge_tool(query: str) -> dict:
    """
    Search the internal support knowledge base for information
    relevant to a support request.
    """
    results = search_knowledge(
        query=query,
        top_k=3,
    )

    return {
        "query": query,
        "results": results,
    }
