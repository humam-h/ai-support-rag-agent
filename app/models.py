from typing import Literal

from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    subject: str = Field(
        min_length=3,
        max_length=200,
    )
    description: str = Field(
        min_length=10,
        max_length=5000,
    )


class SourceChunk(BaseModel):
    source: str
    chunk_index: int
    score: float


class TriageResponse(BaseModel):
    status: Literal[
        "answered",
        "needs_human_action",
        "insufficient_knowledge",
    ]
    answer: str
    sources: list[SourceChunk]

class AgentResponse(BaseModel):
    status: Literal[
        "answered",
        "needs_human_action",
        "insufficient_knowledge",
    ]
    answer: str
    iterations: int