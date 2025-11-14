import os
from app.core.config import settings
from app.core.logger import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


def _ensure_index(pinecone_client: Pinecone) -> None:
    """Create the Pinecone index if it doesn't already exist."""
    names = [i["name"] for i in pinecone_client.list_indexes()]
    if settings.pinecone_index_name not in names:
        logger.info(f"Creating Pinecone index '{settings.pinecone_index_name}'...")
        pinecone_client.create_index(
            name=settings.pinecone_index_name,
            dimension=384,  # compatible with MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
        )
        logger.info(f"Index '{settings.pinecone_index_name}' created successfully.")
    else:
        logger.info(f"Index '{settings.pinecone_index_name}' already exists.")


def build_or_load_vectorstore(chunks=None):
    """Create or load Pinecone vectorstore."""
    logger.info("Connecting to Pinecone...")

    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
    os.environ["PINECONE_ENVIRONMENT"] = settings.pinecone_environment

    pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
    _ensure_index(pinecone_client)

    logger.info("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if chunks:
        logger.info(f"Inserting {len(chunks)} chunks into Pinecone index...")
        vectorstore = PineconeVectorStore.from_documents(
            chunks,
            embedding=embeddings,
            index_name=settings.pinecone_index_name
        )
        logger.info("Chunks inserted successfully.")
    else:
        logger.info("Loading existing Pinecone index...")
        vectorstore = PineconeVectorStore.from_existing_index(
            embedding=embeddings,
            index_name=settings.pinecone_index_name
        )

    logger.info("Vectorstore ready.")
    return vectorstore
