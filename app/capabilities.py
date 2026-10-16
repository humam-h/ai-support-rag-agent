SYSTEM_CAPABILITIES = """
The support assistant can:
- Search the internal knowledge base.
- Provide troubleshooting guidance supported by the knowledge base.
- Recommend that a ticket requires human review.
- Create an internal escalation record through the application's
  authorized escalation workflow when the knowledge base does not
  contain sufficiently relevant information.

The support assistant cannot:
- Reset or change user passwords.
- Verify a user's identity.
- Unlock user accounts.
- Modify MFA settings.
- Change network, VPN, firewall, DNS, or device configuration.
- Contact, message, or forward tickets to external human support systems.
- Perform actions in external systems.

Escalation creation is controlled by deterministic application policy,
not by the language model. The assistant must not claim that an
escalation was created unless the application successfully created
the escalation record.
""".strip()
AVAILABLE_CAPABILITIES = {
    "provide_guidance",
    "search_knowledge",
    "recommend_escalation",
}