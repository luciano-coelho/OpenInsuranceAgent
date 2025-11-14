from pathlib import Path
from time import perf_counter
from app.rag.ingest import load_documents, chunk_documents
from app.rag.vectorstore import build_or_load_vectorstore
from app.core.logger import logger


def ingest_open_insurance_docs():
    """Ingest Open Insurance documents from data/oi/ into Pinecone."""
    t0 = perf_counter()
    base_dir = Path("data/oi")

    if not base_dir.exists():
        logger.error(f"Directory '{base_dir}' not found. Create it and add official SUSEP/Open Insurance documents.")
        return

    logger.info(f"Reading documents from {base_dir}...")
    docs = load_documents(str(base_dir))
    logger.info(f"documents found: {len(docs)}")

    if not docs:
        logger.warning("No documents found. Ensure there are PDFs, TXTs, or MDs in the folder.")
        return

    logger.info("Splitting documents into chunks...")
    chunks = chunk_documents(docs)
    logger.info(f"Chunks generated: {len(chunks)}")

    logger.info("Storing embeddings in Pinecone...")
    # Build or update the vector store with the generated chunks
    build_or_load_vectorstore(chunks)

    elapsed = round(perf_counter() - t0, 2)
    logger.info(f"Ingestion completed successfully in {elapsed}s!")
    logger.info("Vectors are now available in the configured Pinecone index.")

if __name__ == "__main__":
    ingest_open_insurance_docs()
