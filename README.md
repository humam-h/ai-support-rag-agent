# AI Support Triage & RAG Agent

A production-minded AI support automation system that triages support requests, retrieves relevant troubleshooting guidance from an internal knowledge base, and generates responses when sufficiently relevant knowledge is available. When the knowledge base cannot support a request, deterministic application logic creates an escalation for human review rather than allowing the language model to perform uncontrolled actions.

## Key Capabilities

- Semantic knowledge retrieval using OpenAI embeddings and PostgreSQL with pgvector
- Retrieval-Augmented Generation (RAG) for grounded support responses
- AI-assisted ticket classification and support triage
- Bounded agent loop with controlled tool execution
- Deterministic escalation policy outside the language model
- Idempotent escalation creation to prevent duplicate actions
- Persistent audit events for escalation attempts
- FastAPI endpoints for triage and agent execution
- n8n webhook integration for external ticket intake and response routing
- Docker Compose deployment with PostgreSQL, pgvector, FastAPI, and n8n
- Health and readiness checks with explicit knowledge-base ingestion
- Structured application logging without logging ticket contents or model output
- Automated behavioral and readiness tests

## Architecture

The system separates AI reasoning from application-controlled actions. The language model can decide when knowledge retrieval is useful, but Python controls tool execution, authoritative inputs, escalation policy, iteration limits, and persistence.

```text
External Support System
          │
          │ HTTP POST
          ▼
     n8n Webhook
          │
          ▼
      FastAPI API
          │
          ▼
   Support Agent Loop
          │
          ├──── Search Knowledge ────► OpenAI Embeddings
          │                                │
          │                                ▼
          │                         PostgreSQL + pgvector
          │                                │
          │◄──── Relevant Chunks ──────────┘
          │
          ▼
   Application Policy
       │         │
       │         └── No sufficient knowledge
       │                    │
       │                    ▼
       │              Create Escalation
       │                    │
       │                    ▼
       │                PostgreSQL
       │
       ▼
 Structured Agent Response
          │
          ▼
      n8n Switch
          │
          ├── Answered ──────────────┐
          ├── Human Action Required ─┼──► HTTP Response
          └── Insufficient Knowledge ┘
```

### Control Boundary

The language model does **not** have direct access to escalation creation or external systems.

For knowledge retrieval, the application supplies the original ticket text as the authoritative search query rather than allowing the model to rewrite it arbitrarily. If retrieval returns no sufficiently relevant knowledge, deterministic Python policy decides whether an internal escalation is authorized.

This keeps a clear distinction between:

- **AI reasoning** — interpreting the request and deciding when to search
- **Application policy** — deciding which actions are permitted
- **Execution** — performing database writes and other side effects
- **Structured state** — recording what actually happened

## How a Request Is Processed

### Example 1: Supported VPN Issue

A user submits a ticket such as:

```text
Subject: VPN connection problem
Description: My VPN connects but I cannot access internal company resources.
```

The system:

1. Receives the ticket through the n8n webhook.
2. Sends the structured request to the FastAPI agent endpoint.
3. Searches the internal knowledge base using the original ticket text.
4. Retrieves relevant VPN troubleshooting chunks from PostgreSQL/pgvector.
5. Uses the retrieved knowledge to generate a support response.
6. Returns a structured result with:

```json
{
  "status": "answered",
  "escalation": null,
  "action_status": "none"
}
```

n8n routes the result through the `answered` branch and returns the response to the caller.

### Example 2: Unsupported Issue

For a request outside the available knowledge base:

```text
Subject: Printer error 49
Description: My printer displays error 49 and will not print.
```

The retrieval score does not meet the configured relevance threshold. Instead of allowing the model to invent troubleshooting instructions, application policy authorizes an internal escalation.

A successful result looks like:

```json
{
  "status": "needs_human_action",
  "escalation": {
    "id": 1,
    "status": "open"
  },
  "action_status": "escalation_created"
}
```

The escalation is persisted in PostgreSQL and n8n routes the result through the human-action branch.

The language model does not create the escalation directly. The database write is performed by deterministic application code after the retrieval result satisfies the escalation policy.

## Engineering Decisions

### Deterministic Actions, Not LLM-Controlled Side Effects

The language model can reason about a support request and request knowledge retrieval, but it cannot directly create escalations. Escalation authorization and execution are controlled by Python application logic.

This prevents model output from being treated as proof that an action actually occurred.

### Authoritative Retrieval Input

The application uses the original ticket text for vector retrieval rather than allowing the model to freely rewrite the search query.

This decision came from testing: an unsupported printer request scored below the relevance threshold in its original form, but an LLM-expanded version of the query increased similarity enough to cross the threshold and retrieve unrelated knowledge.

Keeping the original ticket as the authoritative retrieval input reduces this failure mode.

### Bounded Agent Execution

The agent loop has a maximum iteration count. The model cannot continue calling tools indefinitely.

If the iteration limit is reached, the application falls back to human review rather than allowing an unbounded agent loop.

### Idempotent Escalation Creation

Escalations use an idempotency key derived from the request ID.

Repeated processing of the same request therefore reuses the existing escalation instead of creating duplicate records.

### Structured Action State

The API does not rely on natural-language responses to determine whether an action occurred.

Responses include structured fields such as:

```json
{
  "status": "needs_human_action",
  "action_status": "escalation_created",
  "escalation": {
    "id": 1,
    "status": "open"
  }
}
```
### Best-Effort Audit Logging

Escalation attempts are recorded in a persistent audit table. Audit logging is deliberately separated from the business action: if writing an audit event fails after an escalation has already been committed, the application does not falsely report that the escalation itself failed.

### Explicit Readiness

Application liveness and readiness are treated separately.

A fresh deployment can start successfully while still returning:

```text
503 Service Unavailable
Knowledge base is not ready.
```

## Tech Stack

- **Python / FastAPI** — API and application-controlled agent logic
- **OpenAI API** — embeddings and language-model reasoning
- **PostgreSQL + pgvector** — persistent storage and vector similarity search
- **n8n** — external webhook intake and response routing
- **Docker Compose** — reproducible local deployment
- **pytest** — automated behavioral and readiness testing

## Running Locally

### Prerequisites

You will need:

- Docker with Docker Compose
- An OpenAI API key

### 1. Configure Environment Variables

Create `.env` from the provided example:

```bash
cp .env.example .env
```

Set your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`.

### 2. Start the Application

```bash
docker compose up -d
```

This starts:

- PostgreSQL with pgvector
- FastAPI
- n8n

On a fresh database, the API starts before the knowledge base has been populated.

Check readiness:

```bash
curl -i http://localhost:8000/ready
```

Before ingestion, a fresh deployment should return:

```text
HTTP/1.1 503 Service Unavailable
```

### 3. Ingest the Knowledge Base

Run the ingestion job explicitly:

```bash
docker compose --profile tools run --rm ingest
```

The sample knowledge documents in `knowledge/` are chunked, embedded, and stored in PostgreSQL.

Check readiness again:

```bash
curl http://localhost:8000/ready
```

Expected result:

```json
{
  "status": "ready",
  "database": "ready",
  "knowledge_chunks": 6,
  "knowledge_ready": true
}
```

### 4. Import the n8n Workflow

Open n8n at:

```text
http://localhost:5678
```

On a fresh n8n installation, complete the local setup and import:

```text
n8n/ai-support-workflow.json
```

The workflow provides:

```text
Webhook → FastAPI Agent → Status Routing → Webhook Response
```

### 5. Test the Webhook

Put the imported n8n webhook into test mode and send a request to its Test URL:

```bash
curl -X POST "YOUR_N8N_TEST_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "demo-001",
    "subject": "Printer error 49",
    "description": "My printer displays error 49 and will not print."
  }'
```

Because the sample knowledge base does not contain printer troubleshooting guidance, the request should be escalated:

```json
{
  "status": "needs_human_action",
  "answer": "I could not find sufficiently relevant information in the internal knowledge base. An escalation was created for human review.",
  "iterations": 1,
  "escalation": {
    "id": 1,
    "status": "open"
  },
  "action_status": "escalation_created"
}
```

The exact escalation ID depends on the current database state.

## Testing

The project includes automated tests for agent behavior, escalation handling, audit behavior, API contracts, and application readiness.

Run the test suite from the project virtual environment:

```bash
pytest
```

The current test suite contains 31 passing tests.

In addition to automated tests, the deployment lifecycle has been tested from a fresh Docker environment:

```text
Fresh PostgreSQL
      ↓
Schema initialization
      ↓
/ready → 503
      ↓
Explicit knowledge ingestion
      ↓
6 knowledge chunks stored
      ↓
/ready → 200
      ↓
Fresh n8n instance
      ↓
Workflow imported from repository
      ↓
External webhook request
      ↓
Agent execution
      ↓
Escalation persisted
      ↓
Structured HTTP response
```

Retrieval behavior was also evaluated against supported and unsupported sample queries. These tests are intended to validate retrieval behavior on the included sample knowledge base; they should not be interpreted as a general accuracy benchmark for RAG systems.

## Known Limitations

This project is production-minded but intentionally not presented as production-ready.

Current limitations include:

- **Client-provided request IDs** — idempotency currently relies on the supplied `request_id`. A production system should detect attempts to reuse an ID with a different request payload.
- **Retrieval-before-answer enforcement** — the agent is instructed to use knowledge retrieval, but stricter application-level state enforcement would further prevent direct model answers before retrieval.
- **Small demonstration knowledge base** — the included knowledge base contains only a few troubleshooting documents and is designed to demonstrate the architecture rather than represent a real support corpus.
- **RAG evaluation coverage** — retrieval tests use a small controlled dataset. Larger datasets would require more extensive retrieval and answer-quality evaluation.
- **Knowledge lifecycle management** — ingestion upserts existing chunks but does not currently remove obsolete chunks when a source document becomes shorter or is deleted.
- **n8n provisioning** — the workflow is version-controlled as JSON but must currently be imported manually into a fresh n8n instance.
- **Local n8n configuration** — the included Compose configuration is intended for local development and disables secure cookies. Production deployment would require appropriate authentication, TLS, secret management, and hardened n8n configuration.
- **Container version pinning** — the n8n image currently uses the `latest` tag and should be pinned for reproducible production deployments.
- **Audit semantics** — retries can produce multiple audit events for the same logical action. A production implementation should explicitly define whether auditing is per attempt or per logical action.
- **Generated support responses** — retrieved knowledge constrains the response, but generated answers can still introduce unnecessary diagnostic questions or elaboration. Stricter grounding evaluation and output validation would be required for higher-assurance use.

## Repository Structure

```text
ai-support-rag-agent/
├── app/
│   ├── agent.py              # Bounded agent loop and control flow
│   ├── audit.py              # Persistent audit events
│   ├── capabilities.py       # Explicit system capability boundaries
│   ├── database.py           # PostgreSQL connectivity and readiness
│   ├── embeddings.py         # Embedding generation
│   ├── escalations.py        # Escalation persistence and idempotency
│   ├── ingest.py             # Knowledge ingestion pipeline
│   ├── knowledge.py          # Document loading and chunking
│   ├── logging_config.py     # Application logging configuration
│   ├── main.py               # FastAPI application and endpoints
│   ├── models.py             # API and agent data models
│   ├── rag.py                # Retrieval-augmented response generation
│   ├── tools.py              # Agent-accessible tool definitions
│   └── vector_store.py       # pgvector similarity search
│
├── knowledge/                # Sample troubleshooting knowledge base
├── migrations/
│   └── 001_initial_schema.sql
├── n8n/
│   └── ai-support-workflow.json
├── tests/                    # Automated test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Project Scope

This project was built to explore how an AI support agent can be given useful reasoning and retrieval capabilities without giving the language model unrestricted control over application side effects.

The main engineering focus is therefore not simply generating support answers. It is establishing clear boundaries between model reasoning, retrieval, deterministic business policy, persistent actions, and observable application state.
