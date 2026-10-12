from app.escalations import create_escalation
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


def create_escalation_tool(
    subject: str,
    description: str,
    reason: str,
) -> dict:
    """
    Create an escalation record for a support request
    that requires human review.
    """
    return create_escalation(
        subject=subject,
        description=description,
        reason=reason,
    )