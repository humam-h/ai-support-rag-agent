import os

from dotenv import load_dotenv
from openai import OpenAI
from app.capabilities import SYSTEM_CAPABILITIES


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def evaluate_grounding(query, answer, retrieved_chunks):
    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"""
SOURCE: {chunk["source"]}
CHUNK: {chunk["chunk_index"]}

{chunk["text"]}
""".strip()
        )

    context = "\n\n---\n\n".join(context_parts)

    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""
You are evaluating an IT support answer against two sources

of evidence:

1. The supplied internal knowledge-base context.

2. The supplied system-capability description.

Evaluate troubleshooting actions, factual claims, procedures,

and claims about what the assistant can or cannot do.

A claim is supported if it is justified by either the

knowledge-base context or the system-capability description.

Reasonable rephrasing is allowed.

Do not judge whether advice is generally correct IT advice.

Do not use your own IT knowledge to justify a claim.

Return:

VERDICT: GROUNDED or NOT_GROUNDED

UNSUPPORTED:

- list each unsupported claim or action

- write "None" if there are none
""".strip(),
        input=f"""
USER REQUEST:

{query}

SYSTEM CAPABILITIES:

{SYSTEM_CAPABILITIES}

KNOWLEDGE-BASE CONTEXT:

{context}

ANSWER TO EVALUATE:

{answer}
""".strip(),
    )

    return response.output_text
