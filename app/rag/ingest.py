from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from app.core.config import settings
from app.core.logger import logger


def load_documents(data_dir="data/oi"):
    """Load documents from the specified directory."""
    docs = []
    for p in Path(data_dir).rglob("*"):
        try:
            if p.suffix.lower() == ".pdf":
                docs.extend(PyPDFLoader(str(p)).load())
            elif p.suffix.lower() == ".md":
                docs.extend(UnstructuredMarkdownLoader(str(p)).load())
            elif p.suffix.lower() == ".txt":
                docs.extend(TextLoader(str(p), encoding="utf-8").load())
        except Exception as e:
            logger.warning(f"Failed to load {p.name}: {e}")
    return docs

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    return splitter.split_documents(docs)
