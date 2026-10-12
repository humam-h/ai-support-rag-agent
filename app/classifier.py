import os

from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal
from pydantic import BaseModel


from app.capabilities import (
    AVAILABLE_CAPABILITIES,
    SYSTEM_CAPABILITIES,
)

load_dotenv()

class CapabilityClassification(BaseModel):
    capability: Literal[
        "provide_guidance",
        "reset_password",
        "verify_identity",
        "unlock_account",
        "modify_mfa",
        "change_network_configuration",
        "perform_external_action",
    ]

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def disposition_for_capability(required_capability):
    if required_capability in AVAILABLE_CAPABILITIES:
        return "answered"

    return "needs_human_action"

def determine_disposition(query):
    required_capability = classify_required_capability(query)

    status = disposition_for_capability(
        required_capability
    )

    return {
        "required_capability": required_capability,
        "status": status,
    }


def classify_required_capability(query):
    response = client.responses.parse(
        model="gpt-5-mini",
        instructions="""
You classify an IT support request by the capability required
to fulfill the user's request.

Use provide_guidance when the request can be satisfied by
giving troubleshooting instructions or information.

Choose an action capability when actually fulfilling the
request requires changing something or performing an action,
rather than merely explaining how it should be done.

When the user explicitly asks for an action, classify the required
capability according to that requested action, even if the knowledge
base could provide related guidance.

Examples:
- "Please unlock my account" requires "unlock_account".
- "Reset my password" requires "reset_password".
- "How do I troubleshoot my locked account?" may require
  "provide_guidance".

Do not classify an explicit action request as "provide_guidance"
merely because guidance could also be provided.
""".strip(),
        input=f"""
SUPPORT REQUEST:

{query}

SYSTEM CAPABILITIES:

{SYSTEM_CAPABILITIES}
""".strip(),
        text_format=CapabilityClassification,
    )

    return response.output_parsed.capability
