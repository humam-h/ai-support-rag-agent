import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools import (
    create_escalation_tool,
    search_knowledge_tool,
)

from app.capabilities import SYSTEM_CAPABILITIES
from app.audit import record_audit_event
import logging

logger = logging.getLogger(__name__)

def _complete_agent_request(request_id, result):
    logger.info(
        "Agent request completed request_id=%s status=%s "
        "action_status=%s iterations=%s",
        request_id,
        result["status"],
        result.get("action_status", "none"),
        result["iterations"],
    )
    return result


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
    logger.info(
        "Agent request started request_id=%s",
        request_id,
    )

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


    instructions = f"""
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
an action unless the application has confirmed that the action
was successfully completed.

If human action is required, recommend human review. Do not
claim that you contacted, messaged, or forwarded the request
to an external human support system.

Internal escalation creation is controlled by deterministic
application policy outside the language model. Do not claim
that an escalation was created based only on your own reasoning.
""".strip()

    for iteration in range(max_iterations):
        logger.debug(
            "Agent iteration request_id=%s iteration=%d",
            request_id,
            iteration + 1,
)

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
                return _complete_agent_request(
                    request_id,
                    {
                       "status": "answered",
                        "answer": response.output_text,
                        "iterations": iteration + 1,
                    },
                )

            return _complete_agent_request(
                request_id,
                {
                "status": "needs_human_action",
                "answer": (
                    "The agent could not produce a final response. "
                    "Human review is required."
                ),
                "iterations": iteration + 1,
            },
            )

        for item in tool_calls:
            arguments = json.loads(item.arguments)

            logger.info(
                "Agent tool call request_id=%s tool=%s",
                request_id,
                item.name,
            )
            
            result = execute_tool(
                item.name,
                arguments,
                original_query=query,
            )

            logger.debug(
                "Agent tool completed request_id=%s tool=%s",
                request_id,
                item.name,
            )
            
            if (
                item.name == "search_knowledge"
                and not result["results"]
            ):
                allowed = can_create_escalation(
                    knowledge_searched=True,
                    knowledge_found=False,
                )
                if not allowed:
                    return _complete_agent_request(
                        request_id,
                        {
                        "status": "insufficient_knowledge",
                        "answer": INSUFFICIENT_KNOWLEDGE_RESPONSE,
                        "iterations": iteration + 1,
                    },
                    )
                try:
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
                except Exception as exc:
                    logger.exception(
                        "Escalation creation failed request_id=%s",
                        request_id,
                    )
                    
                    record_audit_event(
                        request_id=request_id,
                        event_type="escalation_creation",
                        outcome="failure",
                        details={
                            "error_type": type(exc).__name__,
                        },
                    )

                    return _complete_agent_request(
                        request_id,
                        {
                        "status": "needs_human_action",
                        "answer": (
                            "I could not find sufficiently relevant information "
                            "in the internal knowledge base. "
                            "Human review is required, but the escalation "
                            "could not be created."
                        ),
                        "iterations": iteration + 1,
                        "escalation": None,
                        "action_status": "escalation_failed",
                    },
                    )
                record_audit_event(
                    request_id=request_id,
                    event_type="escalation_creation",
                    outcome="success",
                    details={
                        "escalation_id": escalation["id"],
                    },
                )
                return _complete_agent_request(
                    request_id,
                    {
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
                    "action_status": "escalation_created",
                },
                )

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

    return _complete_agent_request(
        request_id,
        {
    "status": "needs_human_action",
    "answer": (
        "The agent reached its maximum number of reasoning "
        "steps. Human review is required."
    ),
    "iterations": max_iterations,
},
    )