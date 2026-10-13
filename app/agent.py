import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools import (
    create_escalation_tool,
    search_knowledge_tool,
)

from app.capabilities import SYSTEM_CAPABILITIES

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


TOOLS = [
    {
        "type": "function",
        "name": "search_knowledge",
        "description": (
            "Search the internal IT support knowledge base "
            "using the user's original support request."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

INSUFFICIENT_KNOWLEDGE_RESPONSE = (
    "I could not find sufficiently relevant information "
    "in the internal knowledge base. "
    "This request requires human review."
)

def can_create_escalation(
    knowledge_searched: bool,
    knowledge_found: bool,
) -> bool:
    return (
        knowledge_searched
        and not knowledge_found
    )

def escalation_idempotency_key(request_id: str) -> str:
    return f"ticket:{request_id}:escalation"

def execute_tool(name, arguments, original_query):
    if name == "search_knowledge":
        return search_knowledge_tool(
            query=original_query

        )

    raise ValueError(
        f"Unknown tool: {name}"
    )
def run_agent(
    request_id,
    subject,
    description,
    max_iterations=5,
    model_client=None,
):
    query = f"""
Subject: {subject}
Description:

{description}

""".strip()
    
    if model_client is None:
        model_client = client
    input_items = [
        {
            "role": "user",
            "content": query,
        }
    ]


    instructions = """
You are an IT support agent.

SYSTEM CAPABILITIES:

{SYSTEM_CAPABILITIES}

Use the available tools when you need information from the

internal knowledge base.

Base troubleshooting guidance only on information returned

by the tools.

If the knowledge base does not contain enough relevant

information, say that human review is required.

Do not add troubleshooting procedures, diagnostic steps,

information-gathering requirements, or escalation procedures

from your own knowledge.

Do not claim that you performed, initiated, or will perform

an action unless an available tool actually allows that action.

If human action is required, recommend human review without

claiming that you can contact, forward to, or create a ticket

for the human team.
""".strip()

    for iteration in range(max_iterations):
        print(f"\nAGENT ITERATION {iteration + 1}")

        response = model_client.responses.create(
            model="gpt-5-mini",
            instructions=instructions,
            tools=TOOLS,
            input=input_items,
        )

        input_items += response.output

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # No tool calls means the model has finished.
        if not tool_calls:
            if response.output_text:
                return {
                    "status": "answered",
                    "answer": response.output_text,
                    "iterations": iteration + 1,
                }

            return {
                "status": "needs_human_action",
                "answer": (
                    "The agent could not produce a final response. "
                    "Human review is required."
                ),
                "iterations": iteration + 1,
            }

        for item in tool_calls:
            arguments = json.loads(item.arguments)

            print("\nTOOL CALL:")
            print("name:", item.name)
            print("arguments:", arguments)

            result = execute_tool(
                item.name,
                arguments,
                original_query=query,
            )

            print("\nTOOL RESULT:")
            print(json.dumps(result, indent=2))

            if (
                item.name == "search_knowledge"
                and not result["results"]
            ):
                allowed = can_create_escalation(
                    knowledge_searched=True,
                    knowledge_found=False,
                )
                if not allowed:
                    return {
                        "status": "insufficient_knowledge",
                        "answer": INSUFFICIENT_KNOWLEDGE_RESPONSE,
                        "iterations": iteration + 1,
                    }
                escalation = create_escalation_tool(
                    subject=subject,
                    description=description,
                    reason=(
                        "No sufficiently relevant knowledge-base "
                        "information was found."
                    ),
                    idempotency_key=escalation_idempotency_key(
                        request_id
                    ),
                )
                return{
                    "status": "needs_human_action",
                    "answer": (
                        "I could not find sufficiently relevant information "
                        "in the internal knowledge base. "
                        "An escalation was created for human review."
                    ),
                    "iterations": iteration + 1,
                    "escalation": {
                        "id": escalation["id"],
                        "status": escalation["status"],
                    },
                }

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

    return {
    "status": "needs_human_action",
    "answer": (
        "The agent reached its maximum number of reasoning "
        "steps. Human review is required."
    ),
    "iterations": max_iterations,
}