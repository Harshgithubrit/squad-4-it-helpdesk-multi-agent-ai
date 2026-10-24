# Squad-4 — IT Helpdesk Multi-Agent System

A runnable proof-of-concept for the **IT Helpdesk (Use Case B)**. It demonstrates explicit LangGraph orchestration, specialized agents, a central tool registry, policy checks and human approval, OpenTelemetry-ready tracing, session capture/replay, a frozen support-ticket dataset, evaluation metrics, a CLI, and a Streamlit dashboard.

> **Safety boundary:** this is a demo. Account status and ticket creation are mock tools. It does not connect to real identity systems or create tickets in an external service. Do not put real customer data or secrets in the sample dataset/logs.

## 1. Architecture and orchestration

```text
User (Streamlit or CLI)
        |
        v
   LangGraph START
        |
        v
 Intent Router -------------------------------+
   | access/login/account                     | other issue
   v                                          v
Access-Check Agent                     Knowledge-Search Agent
   | mock account status                      | local retrieval
   +---------------------> Knowledge-Search <-+
                                  |
                                  v
                           Reasoning Agent
                     (plan + grounded guidance)
                                  |
                                  v
                         Policy / Action Agent
                           |             |
                    approval needed     | low-risk
                           |             v
                      HITL response   Mock ticket tool
                           |             |
                           +------> Finalize
                                      |
                       session capture + optional OTel spans
                                      |
                            CLI / Streamlit output
```

**Why this orchestration?** LangGraph makes nodes, state, and edges explicit and inspectable. The router chooses the initial specialist; the access-check node only reads synthetic status; knowledge search retrieves evidence; reasoning proposes next steps; the action node applies policy before ticket creation; finalization captures the run. Privileged actions are never executed by this demo and require approval. OpenTelemetry spans can be exported to console or an OTLP endpoint.

## 2. Project structure

```text
it-helpdesk-agent/
├── app.py
├── cli.py
├── config.py
├── graph.py
├── state.py
├── agents/                 # knowledge, access, reasoning, action/ticket nodes
├── tools/                  # local search, mock directory, mock ticket, registry
├── security/               # policy and HITL helper
├── observability/          # OpenTelemetry and session capture
├── evaluation/              # metrics, runner, golden_set.json
├── data/golden_it_support_tickets.csv
├── tests/
├── requirements.txt
└── README.md
```

## 3. Run locally

Requires Python 3.10+ (Python 3.11 recommended).

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
copy config.example.env .env   # Windows; on macOS/Linux: cp config.example.env .env
```

The default `LLM_PROVIDER=mock` mode runs without a model API key and is suitable for the hackathon demo. The starter intentionally uses deterministic, explainable rules for the reasoning node so the project remains runnable in restricted environments. To connect an LLM, implement a provider adapter in `agents/reasoning.py`, configure the provider/key, and keep policy enforcement outside the model.

### Streamlit dashboard

```bash
streamlit run app.py
```

### CLI

```bash
python cli.py ask "My laptop is connected to Wi-Fi but the internet is not working"
python cli.py tools
python cli.py eval
```

The `ask` command prints the full graph state including `session_id`. Use that ID to replay the captured record:

```bash
python cli.py replay <SESSION_ID>
```

### Tests

```bash
pytest -q
```

## 4. OpenTelemetry

Tracing is disabled by default. To emit spans to the console, set in `.env`:

```env
OTEL_ENABLED=true
OTEL_EXPORTER=console
```

For an OTLP/HTTP collector, configure `OTEL_EXPORTER=otlp` and `OTEL_EXPORTER_OTLP_ENDPOINT` to the collector's traces endpoint. For a local Jaeger all-in-one, configure the collector endpoint supported by your Jaeger setup. Confirm endpoint path and authentication for your environment.

Spans cover the request, router, and agent nodes. Extend instrumentation to tool-level calls, latency, token counts, and decision attributes as needed. Avoid putting prompts, secrets, or PII into span attributes.

## 5. Evaluation

The runner uses `initial_message` as the query and `resolution_summary` as reference. It reports:
- **Correctness proxy:** token overlap with the reference resolution.
- **Groundedness proxy:** token overlap with retrieved resolution summaries.
- **Ticket creation rate** and mean latency.

These are intentionally simple baseline metrics, not a substitute for human evaluation or a dedicated LLM judge. Freeze the chosen dataset subset before comparing versions. Do not train a model on the golden set.

## 6. Design and production-hardening notes

- **Policy is not prompt text.** Enforce authorization in backend code before any tool call; deny by default.
- **Human approval:** implement an authenticated approval identity and audit record before production use. The UI's approval button is only a demo interaction.
- **Tool registry:** metadata is centralized in `tools/registry.py`; add schema validation and role scopes before enabling real tools.
- **Retrieval:** this sample uses lexical token overlap to avoid heavyweight setup. Replace with Chroma/FAISS/Pinecone/Azure AI Search embeddings for semantic retrieval; retain source IDs and access filters.
- **Session replay:** captures a safe subset of state as JSONL. Production replay should version prompts, model, tool schemas, dataset, and deterministic mock responses.
- **Reliability:** add bounded retries with exponential backoff, timeouts, circuit breakers, idempotency keys, and fallback responses around network/LLM calls.
- **Secrets and privacy:** use environment variables or a secret manager; redact PII; apply retention controls to logs.
- **Scaling:** the POC is single-process. For scale, separate agents behind services/queues, add persistent state, distributed tracing, and an approval workflow service.

## 7. Known demo limitations

- LLM provider configuration is prepared but an actual provider call is not wired into the baseline reasoning node; the demo uses deterministic rules so it works offline.
- Account lookup is synthetic, and ticket creation is local/mock.
- Retrieval is lexical rather than embedding-based.
- The approval UI records a demo decision only; it does not resume a paused graph. A production implementation should use LangGraph interrupts/checkpointing and authenticated approval.
- The dataset is a small illustrative sample. Replace it with the supplied frozen dataset from the hackathon package, retaining the exact field names.


## Authentication, authorization, dependency injection, and validation

The project includes a FastAPI API (`api.py`) in addition to the Streamlit and CLI interfaces. FastAPI dependencies inject the authenticated principal and the compiled LangGraph instance into route handlers. JWT bearer tokens provide authentication; `require_roles("admin")` protects administrative tool listing. The helpdesk query endpoint derives `user_id` from the verified token rather than trusting a caller-supplied identity. Pydantic v2 schemas validate login and query payloads and reject unknown fields.

### Configure and run the API

1. Copy `config.example.env` to `.env` and change `AUTH_SECRET`, demo usernames, and passwords. Use a cryptographically random secret in any shared environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the API: `uvicorn api:app --reload`
4. Open `http://127.0.0.1:8000/docs` for interactive Swagger documentation.

Demo accounts are loaded from environment variables (defaults are for local demonstrations only):

- User: `squad4-user` / `ChangeMe123!`
- Admin: `squad4-admin` / `ChangeAdmin123!`

Example JSON login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"squad4-user","password":"ChangeMe123!"}'
```

Use the returned `access_token` as `Authorization: Bearer <token>` when calling `POST /helpdesk/query`. Example body:

```json
{"query":"My laptop cannot connect to the office Wi-Fi"}
```

`GET /admin/tools` requires an admin token and returns HTTP 403 for a normal user. `GET /auth/me` returns the identity and roles encoded in the verified token. `GET /health` is public.

### Security notes

- This is a hackathon/demo authentication implementation. Replace environment-backed demo credentials with your identity provider, use HTTPS, rotate secrets, and add rate limiting and audit controls before deployment.
- JWT is signed, not encrypted. Do not put secrets or sensitive personal data in claims.
- Authorization is enforced server-side; hiding UI controls is not authorization. Privileged IT changes still require the separate policy/HITL workflow.
- The existing Streamlit UI and CLI are local demo interfaces; the new API is the boundary that enforces JWT authentication and role-based authorization.
