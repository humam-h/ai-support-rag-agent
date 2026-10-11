from openai import OpenAI

from app.vector_store import search_knowledge
from app.capabilities import SYSTEM_CAPABILITIES
from app.classifier import determine_disposition


client = OpenAI()


def generate_answer(query, top_k=3):
    results = search_knowledge(
        query=query,
        top_k=top_k,
    )

    if not results:
        return {
            "answer": (
                "I could not find sufficiently relevant information "
                "in the internal knowledge base. "
                "This request should be escalated for human review."
            ),
            "retrieved_chunks": [],
            "status": "insufficient_knowledge",
        }

    disposition = determine_disposition(query)

    context_parts = []

    for result in results:
        context_parts.append(
            f"""
SOURCE: {result["source"]}
CHUNK: {result["chunk_index"]}

{result["text"]}
""".strip()
        )

    context = "\n\n---\n\n".join(context_parts)

    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""
You are an IT support assistant operating from an internal

knowledge base.

Use only troubleshooting actions explicitly supported by the

supplied internal knowledge-base context.

Do not add troubleshooting steps from your own knowledge,

even if they seem obvious or helpful.

You may rephrase the supplied instructions for clarity, but

you must not introduce new diagnostic actions, commands,

tools, settings, or procedures.

If the supplied context does not contain enough information

to answer the request safely and usefully, say that the issue

should be escalated for human review.

Keep the response concise and practical.

At the end, list only the source filenames actually used.

Do not claim that you performed or will perform an action
that is outside the supplied system capabilities.

When an action requires a human or an unavailable external
system, explain that human action is required rather than
claiming that you will perform it.

""".strip(),
        input=f"""
SUPPORT REQUEST:

{query}

SYSTEM CAPABILITIES:

{SYSTEM_CAPABILITIES}

INTERNAL KNOWLEDGE:

{context}
""".strip(),
    )

    return {
    "answer": response.output_text,
    "retrieved_chunks": results,
    "status": disposition["status"],
}