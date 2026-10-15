from fastapi import FastAPI, HTTPException
from app.agent import run_agent

from app.models import (
    AgentResponse,
    SourceChunk,
    TicketRequest,
    TriageResponse,
)
from app.rag import generate_answer
from app.database import check_database_readiness

app = FastAPI(
    title="AI Support RAG Agent",
    version="0.1.0",
)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ai-support-rag-agent",
    }

@app.get("/ready")
def readiness():
    try:
        result = check_database_readiness()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready.",
        )

    if not result["knowledge_ready"]:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base is not ready.",
        )

    return {
        "status": "ready",
        **result,
    }


@app.post(
    "/tickets/triage",
    response_model=TriageResponse,
)
def triage_ticket(ticket: TicketRequest):
    query = f"""
Subject: {ticket.subject}

Description:
{ticket.description}
""".strip()

    result = generate_answer(query)

    sources = [
        SourceChunk(
            source=chunk["source"],
            chunk_index=chunk["chunk_index"],
            score=chunk["score"],
        )
        for chunk in result["retrieved_chunks"]
    ]

    return TriageResponse(
        status=result["status"],
        answer=result["answer"],
        sources=sources,
    )
@app.post(
    "/tickets/agent",
    response_model=AgentResponse,
)
def agent_ticket(ticket: TicketRequest):
    query = f"""
Subject: {ticket.subject}

Description:
{ticket.description}
""".strip()

    result = run_agent(
        request_id=ticket.request_id,
        subject=ticket.subject,
        description=ticket.description,
                       
        )

    return AgentResponse(
    status=result["status"],
    answer=result["answer"],
    iterations=result["iterations"],
    escalation=result.get("escalation"),
    action_status=result.get("action_status", "none"),
)
