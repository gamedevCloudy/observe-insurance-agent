import hashlib
from collections import defaultdict
from pathlib import Path

from app.core.config import DATA_DIR
from app.rag.loaders import load_all_documents
from app.rag.vectorstore import get_vectorstore


def _file_hash(source: str) -> str:
    path = Path(DATA_DIR) / source
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ingest() -> dict:
    docs = load_all_documents()
    vs = get_vectorstore()
    collection = vs._collection

    by_source: dict[str, list] = defaultdict(list)
    for doc in docs:
        by_source[doc.metadata["source"]].append(doc)

    added = 0
    skipped = 0

    for source, source_docs in by_source.items():
        current_hash = _file_hash(source)

        existing = collection.get(where={"source": source}, include=["metadatas"])
        if existing["ids"] and existing["metadatas"]:
            existing_hash = existing["metadatas"][0].get("source_hash")
            if existing_hash == current_hash:
                skipped += len(source_docs)
                continue
            collection.delete(where={"source": source})

        for doc in source_docs:
            doc.metadata["source_hash"] = current_hash

        vs.add_documents(source_docs)
        added += len(source_docs)

    return {"added": added, "skipped": skipped, "total_docs_in_collection": collection.count()}


if __name__ == "__main__":
    result = ingest()
    print(f"Ingestion complete: {result}")
