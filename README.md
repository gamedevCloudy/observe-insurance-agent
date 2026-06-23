# Observe Insurance — AI Claims Support Agent

VoiceAI agent that handles inbound calls from customers checking on insurance claim status. Built for the Observe.AI AI Agent Engineer take-home assessment.

**Status:** Take-home assessment — not intended for production use.

## Quick Start

```bash
uv sync
cp .env.example .env   # fill in API keys
uv run python -m app.db.init_db   # seed database
uv run python -m app.rag.ingest   # build FAQ vector store
uv run uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the web voice demo.

## Architecture

```mermaid
graph TB
    Caller([Caller]) -->|WebSocket| VoiceRoute[Voice Route]
    VoiceRoute --> Pipeline[Voice Pipeline]

    subgraph Pipeline
        STT[Deepgram STT] --> Sanitize[Sanitize]
        Sanitize --> Agent
        Agent --> TTS[Deepgram TTS]
        TTS -->|audio stream| VoiceRoute
    end

    subgraph Agent [LangGraph Agent]
        direction LR
        AgentNode[Agent Node] -->|tool calls| ToolNode[Tool Node]
        ToolNode -->|results| AgentNode
    end

    AgentNode --> Tools

    subgraph Tools
        direction TB
        Customers[(Customers DB)]
        Claims[(Claims DB)]
        Policies[(Policies DB)]
        FAQ[FAQ RAG / Chroma]
        SMS[SMS Sender]
        Escalation[Escalation]
        CallLog[Call Logger]
    end

    CallLog --> External[(External System)]

    style Agent fill:#edf5ff,stroke:#0f62fe
    style Tools fill:#f4f4f4,stroke:#c6c6c6
    style Pipeline fill:#f4f4f4,stroke:#c6c6c6
```

### Call Flow

1. **Authenticate** — caller provides phone number, agent verifies against customer DB
2. **Handle request** — retrieve claim status, answer FAQs, or escalate
3. **Respond** — agent generates response, TTS streams audio back
4. **Log** — post-call record (summary, sentiment, duration) written to external system

## Integrations

| Service | Purpose |
|---------|---------|
| **Deepgram** | Speech-to-text and text-to-speech |
| **OpenRouter** | LLM orchestration (multi-provider) |
| **Chroma** | Vector store for FAQ retrieval (RAG) |
| **SQLite + SQLAlchemy** | Customer, claim, and policy data |
| **LangGraph** | Agent workflow and state management |

## Agent Tools

| Tool | Description |
|------|-------------|
| `customers` | Look up customer by phone number |
| `claims` | Retrieve claim status and details |
| `policies` | Fetch policy information |
| `faq` | RAG-based FAQ retrieval from knowledge base |
| `sms` | Send SMS with claim documentation instructions |
| `escalation` | Escalate to human representative |
| `call_logs` | Write post-call interaction record |

## Project Structure

```
obvserve-insurance-support/
├── app/
│   ├── agents/       # LangGraph agent graph, prompt, tools
│   ├── core/         # Config, logging
│   ├── db/           # SQLAlchemy models, seed data
│   ├── llm/          # OpenRouter client
│   ├── rag/          # Chroma vector store, FAQ ingestion
│   ├── routes/       # FastAPI endpoints (voice, chat, CRUD)
│   ├── voice/        # Deepgram STT/TTS, audio pipeline
│   └── main.py
├── data/             # FAQ JSON, PDFs
├── scripts/          # Build utilities
├── tests/            # Pytest test suite
├── static/           # Web demo (voice.html)
└── pyproject.toml
```

