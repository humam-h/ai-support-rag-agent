from fastapi import FastAPI
from app.agent import run_agent

from app.models import (
    AgentResponse,
    SourceChunk,
    TicketRequest,
    TriageResponse,
)
from app.rag import generate_answer


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
        subject=ticket.subject,
        description=ticket.description,
                       
        )

    return AgentResponse(
        status=result["status"],
        answer=result["answer"],
        iterations=result["iterations"],
    )
