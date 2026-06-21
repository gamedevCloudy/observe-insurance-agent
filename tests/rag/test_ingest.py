from app.rag.ingest import ingest


def test_ingest_idempotent(test_vectorstore, monkeypatch):
    monkeypatch.setattr("app.rag.ingest.get_vectorstore", lambda: test_vectorstore)

    result1 = ingest()
    assert result1["added"] > 0
    count_after_first = test_vectorstore._collection.count()

    result2 = ingest()
    assert result2["skipped"] == result1["added"]
    assert result2["added"] == 0
    assert test_vectorstore._collection.count() == count_after_first


def test_ingest_adds_source_hash(test_vectorstore, monkeypatch):
    monkeypatch.setattr("app.rag.ingest.get_vectorstore", lambda: test_vectorstore)

    ingest()

    stored = test_vectorstore._collection.get(
        where={"source": "faqs/faqs.json"}, include=["metadatas"]
    )
    assert all(m.get("source_hash") for m in stored["metadatas"])
