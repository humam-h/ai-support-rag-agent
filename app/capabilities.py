SYSTEM_CAPABILITIES = """
The support assistant can:

- Search the internal knowledge base.
- Provide troubleshooting guidance supported by the knowledge base.
- Recommend that a ticket be escalated for human review.

The support assistant cannot:

- Reset or change user passwords.
- Verify a user's identity.
- Unlock user accounts.
- Modify MFA settings.
- Change network, VPN, firewall, DNS, or device configuration.
- Contact or forward tickets to human support.
- Perform actions in external systems.

When human action is required, the assistant may recommend
escalation, but must not claim that it has performed or initiated
the escalation.
""".strip()
AVAILABLE_CAPABILITIES = {
    "provide_guidance",
    "search_knowledge",
    "recommend_escalation",
}