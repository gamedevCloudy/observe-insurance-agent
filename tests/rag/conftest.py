import pytest
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

TEST_DOCS = [
    Document(
        page_content="Question: What are your office hours?\nAnswer: Monday-Friday 8AM-6PM ET.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "What are your office hours?", "source_hash": "abc123"},
    ),
    Document(
        page_content="Question: What is the mailing address?\nAnswer: P.O. Box 1234, Springfield, IL.",
        metadata={"doc_type": "faq", "source": "faqs/faqs.json", "question": "What is the mailing address?", "source_hash": "abc123"},
    ),
    Document(
        page_content="Silver plan: Deductible $3,000, premium from $250.",
        metadata={"doc_type": "pdf", "source": "pdfs/tiers.pdf", "source_hash": "def456"},
    ),
]


@pytest.fixture()
def test_vectorstore(tmp_path):
    embeddings = DeterministicFakeEmbedding(size=10)
    vs = Chroma(
        collection_name="test_kb",
        embedding_function=embeddings,
        persist_directory=str(tmp_path / "chroma"),
        collection_metadata={"hnsw:space": "cosine"},
    )
    vs.add_documents(TEST_DOCS)
    return vs


@pytest.fixture(autouse=True)
def _rag_store(monkeypatch, test_vectorstore):
    monkeypatch.setattr("app.rag.vectorstore.get_vectorstore", lambda: test_vectorstore)
    monkeypatch.setattr("app.rag.retrieval.get_vectorstore", lambda: test_vectorstore)
