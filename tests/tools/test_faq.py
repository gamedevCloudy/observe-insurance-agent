from app.agents.call_agent.tools.faq import faq_search


def test_faq_search_found():
    result = faq_search.invoke({"query": "office hours"})
    assert result["found"] is True
    assert "8" in result["context"]
    assert result["count"] > 0
    assert isinstance(result["sources"], list)


def test_faq_search_returns_context():
    result = faq_search.invoke({"query": "mailing address"})
    assert result["found"] is True
    assert "mailing" in result["context"].lower() or "address" in result["context"].lower()
    assert len(result["sources"]) > 0
