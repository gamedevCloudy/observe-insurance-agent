from langchain_chroma import Chroma

from app.core.config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR
from app.rag.embeddings import get_embeddings


def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
