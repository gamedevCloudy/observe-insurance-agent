from langchain_core.documents import Document

from app.rag.vectorstore import get_vectorstore


def search(query: str, k: int = 4) -> list[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "What are the office hours?"
    results = search(query)
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ({doc.metadata.get('source', 'unknown')}) ---")
        print(doc.page_content[:500])
