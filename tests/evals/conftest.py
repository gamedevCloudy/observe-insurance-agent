"""Shared fixtures for LLM-as-judge evals."""

import asyncio
import atexit
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openrouter import ChatOpenRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.database as db_mod
from app.agents.call_agent.agent import build_agent
from app.agents.call_agent.memory import store as agent_store
from app.db.models import CallLog, Claim, Customer, EscalationLog, Policy  # noqa: F401

# ---------------------------------------------------------------------------
# CSV collector — written via atexit (guaranteed to fire)
# ---------------------------------------------------------------------------

_eval_records: list[dict] = []
_eval_started: str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _csv_path() -> Path:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(exist_ok=True)
    return results_dir / f"evals_{_eval_started}.csv"


def _write_csv():
    if not _eval_records:
        return
    path = _csv_path()
    fieldnames = [
        "run", "scenario", "category", "pass", "score",
        "criteria_met", "criteria_total", "judge_notes",
        "tool_calls", "agent_summary", "duration_ms",
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        w.writerows(_eval_records)
    sys.stderr.write(f"\n--- eval results written to {path} ---\n")


atexit.register(_write_csv)


def _record(scenario_id: str, category: str, passed: bool, judge_result: dict,
            tool_calls: list[dict], agent_output: str, duration_ms: float) -> None:
    criteria_met = sum(1 for c in judge_result.get("criteria_results", []) if c.get("met"))
    criteria_total = len(judge_result.get("criteria_results", []))
    summary = agent_output[:200] if agent_output else ""
    tool_names = ", ".join(tc["name"] for tc in tool_calls)

    _eval_records.append({
        "run": _eval_started,
        "scenario": scenario_id,
        "category": category,
        "pass": passed,
        "score": f"{criteria_met}/{criteria_total}",
        "criteria_met": criteria_met,
        "criteria_total": criteria_total,
        "judge_notes": judge_result.get("overall_reasoning", ""),
        "tool_calls": tool_names,
        "agent_summary": summary,
        "duration_ms": int(duration_ms),
    })


# ---------------------------------------------------------------------------
# in-memory test DB (autouse) — replaces parent conftest fixture
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _test_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestSession = sessionmaker(bind=engine)

    db_mod.Base.metadata.create_all(bind=engine)

    db = TestSession()
    db.add_all([
        Customer(cust_id=1, cust_name="Alice Johnson", contact="555-0101",
                 addr="123 Main St, Springfield, IL", email="alice@example.com"),
        Customer(cust_id=2, cust_name="Bob Smith", contact="555-0202",
                 addr="456 Oak Ave, Denver, CO", email="bob@example.com"),
    ])
    db.add_all([
        Policy(policy_num="POL-001", cust_id=1, tier="gold", premium_status="paid", premium_amt=1200),
        Policy(policy_num="POL-002", cust_id=2, tier="silver", premium_status="due", premium_amt=800),
    ])
    db.add_all([
        Claim(claim_id=1, policy_num="POL-001", status="under_review", docs_required=True,
              description="Water damage from burst pipe", created_at="2026-05-15"),
        Claim(claim_id=2, policy_num="POL-002", status="approved", docs_required=False,
              description="Hail damage to roof", created_at="2026-04-20"),
    ])
    db.add(CallLog(call_id=1, cust_id=1, caller_name="Alice Johnson",
                   summary="Checked on claim status.", sentiment="neutral",
                   start_time="2026-06-21T10:00:00", end_time="2026-06-21T10:05:00", duration=300))
    db.commit()

    # patch both the module attribute AND tools that imported directly
    orig_session = db_mod.SessionLocal
    db_mod.SessionLocal = TestSession

    # also patch tools that do `from app.db.database import SessionLocal`
    import app.agents.call_agent.tools.customers as cust_tools
    import app.agents.call_agent.tools.claims as claim_tools
    import app.agents.call_agent.tools.policies as pol_tools
    import app.agents.call_agent.tools.call_logs as clog_tools

    cust_tools.SessionLocal = TestSession
    claim_tools.SessionLocal = TestSession
    pol_tools.SessionLocal = TestSession
    clog_tools.SessionLocal = TestSession

    yield

    db_mod.SessionLocal = orig_session
    cust_tools.SessionLocal = orig_session
    claim_tools.SessionLocal = orig_session
    pol_tools.SessionLocal = orig_session
    clog_tools.SessionLocal = orig_session
    db.close()


# reset memory store between tests
@pytest.fixture(autouse=True)
def _reset_store():
    yield
    agent_store.put(("customer", "1"), "interactions", {})
    agent_store.put(("customer", "2"), "interactions", {})


# ---------------------------------------------------------------------------
# test vectorstore (autouse) — so FAQ evals work without live embeddings
# ---------------------------------------------------------------------------

TEST_FAQ_DOCS = [
    Document(
        page_content="Question: What are your office hours?\nAnswer: Monday-Friday 8AM-6PM ET.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "What are your office hours?"},
    ),
    Document(
        page_content="Question: What is the mailing address for the Midwest district?\nAnswer: Observe Insurance, Midwest Regional Office, 233 South Wacker Drive, Suite 2500, Chicago, IL 60606.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "What is the mailing address for the Midwest district?"},
    ),
    Document(
        page_content="Question: How do I start a new insurance claim?\nAnswer: Call 1-800-555-CLAIM, visit observeinsurance.com/claims, use mobile app, or contact agent. Need policy number and incident details.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "How do I start a new insurance claim?"},
    ),
    Document(
        page_content="Question: What is the general claims process?\nAnswer: File claim → adjuster assigned in 24-48h → document damage → adjuster reviews → settlement decision → payment in 5-10 business days. Standard claims: 10-15 business days.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "What is the general claims process?"},
    ),
    Document(
        page_content="Question: How can I check the status of my existing claim?\nAnswer: Log into observeinsurance.com/my-claims, call 1-800-555-CLAIM, contact your agent, or use mobile app.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "How can I check the status of my existing claim?"},
    ),
]


@pytest.fixture(autouse=True)
def _eval_vectorstore(tmp_path):
    embeddings = DeterministicFakeEmbedding(size=10)
    vs = Chroma(
        collection_name="eval_kb",
        embedding_function=embeddings,
        persist_directory=str(tmp_path / "chroma"),
        collection_metadata={"hnsw:space": "cosine"},
    )
    vs.add_documents(TEST_FAQ_DOCS)

    import app.rag.vectorstore as vs_mod
    import app.rag.retrieval as ret_mod

    orig_vs = vs_mod.get_vectorstore
    orig_ret = ret_mod.get_vectorstore

    vs_mod.get_vectorstore = lambda: vs
    ret_mod.get_vectorstore = lambda: vs
    yield
    vs_mod.get_vectorstore = orig_vs
    ret_mod.get_vectorstore = orig_ret


# ---------------------------------------------------------------------------
# judge client
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def judge_client():
    model = os.getenv("EVAL_JUDGE_MODEL", "qwen/qwen3.7-plus")
    return ChatOpenRouter(model=model, temperature=0, max_retries=2)


# ---------------------------------------------------------------------------
# agent graph (real LLM)
# ---------------------------------------------------------------------------

@pytest.fixture
def agent_graph():
    return build_agent()


# ---------------------------------------------------------------------------
# scenario runner
# ---------------------------------------------------------------------------

async def run_scenario(agent, scenario: dict) -> dict:
    """Run a single scenario against the agent, return collected trace."""
    config = {"configurable": {"thread_id": scenario["id"]}}
    tool_calls_made: list[dict] = []
    assistant_texts: list[str] = []

    for turn_idx, msg in enumerate(scenario["messages"]):
        state = await agent.ainvoke(
            {"messages": [HumanMessage(content=msg["content"])]},
            config=config,
        )
        messages = state.get("messages", [])
        for m in messages:
            if isinstance(m, ToolMessage):
                tool_calls_made.append({
                    "name": m.name,
                    "content": str(m.content),
                    "turn": turn_idx + 1,
                })

        # Collect every assistant text response (not just the last per turn)
        for m in messages:
            if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None) and m.content:
                if m.content not in assistant_texts:
                    assistant_texts.append(str(m.content))

    return {
        "agent_output": "\n\n".join(assistant_texts),
        "tool_calls": tool_calls_made,
        "scenario_id": scenario["id"],
    }


async def run_and_judge(agent, judge_client, scenario: dict) -> dict:
    """Run scenario through agent, then judge the result. Returns eval record dict."""
    from tests.evals.judge import evaluate

    t0 = time.monotonic()
    try:
        agent_result = await run_scenario(agent, scenario)
    except Exception as exc:
        agent_result = {
            "agent_output": f"[AGENT ERROR: {exc}]",
            "tool_calls": [],
            "scenario_id": scenario["id"],
        }
    elapsed = (time.monotonic() - t0) * 1000

    judge_result = await evaluate(judge_client, scenario, agent_result)

    passed = bool(judge_result.get("pass", False))
    if judge_result.get("judge_error"):
        passed = False

    _record(
        scenario_id=scenario["id"],
        category=scenario["category"],
        passed=passed,
        judge_result=judge_result,
        tool_calls=agent_result["tool_calls"],
        agent_output=agent_result["agent_output"],
        duration_ms=elapsed,
    )

    return {
        "scenario_id": scenario["id"],
        "pass": passed,
        "judge_result": judge_result,
        "agent_result": agent_result,
        "duration_ms": elapsed,
    }


def _recreate_llm():
    """Hot-swap _llm inside the current event loop."""
    import app.agents.call_agent.agent as agent_mod
    from app.llm.openrouter import get_openrouter_client

    agent_mod._llm = get_openrouter_client().bind_tools(agent_mod.ALL_TOOLS)
