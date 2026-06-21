import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import DATA_DIR

DATA_PATH = Path(DATA_DIR)


def load_faqs() -> list[Document]:
    faq_file = DATA_PATH / "faqs" / "faqs.json"
    entries = json.loads(faq_file.read_text())
    docs = []
    for entry in entries:
        content = f"Question: {entry['question']}\nAnswer: {entry['answer']}"
        metadata = {
            "doc_type": "faq",
            "source": "faqs/faqs.json",
            "question": entry["question"],
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def load_pdfs() -> list[Document]:
    pdf_dir = DATA_PATH / "pdfs"
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        raw_docs = loader.load()
        for doc in raw_docs:
            doc.metadata["doc_type"] = "pdf"
            doc.metadata["source"] = f"pdfs/{pdf_path.name}"
        docs.extend(splitter.split_documents(raw_docs))
    return docs


def load_all_documents() -> list[Document]:
    return load_faqs() + load_pdfs()
