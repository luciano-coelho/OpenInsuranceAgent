import os
from datetime import datetime
from app.core.config import settings
from app.core.logger import logger
from pinecone import Pinecone


def check_pinecone_status():
    """Check Pinecone index status and display diagnostics."""
    logger.info("Connecting to Pinecone...")

    # Ensure API key is available in environment
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
    os.environ["PINECONE_ENVIRONMENT"] = settings.pinecone_environment

    pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
    indexes = pinecone_client.list_indexes()

    if not indexes:
        logger.warning("No indexes found.")
        return

    logger.info(f"\nAvailable indexes ({len(indexes)}):")
    for idx in indexes:
        logger.info(f"  • {idx['name']}  |  {idx['status']}  |  {idx['metric']}  |  Dimension: {idx['dimension']}")
    logger.info("-" * 60)

    # Access the configured index
    index_name = settings.pinecone_index_name
    index = pinecone_client.Index(index_name)

    logger.info(f"\nChecking status of index '{index_name}'...")
    stats = index.describe_index_stats()

    total_vectors = stats.get("total_vector_count", 0)
    namespace_data = stats.get("namespaces", {})
    storage = sum(ns.get("vector_count", 0) for ns in namespace_data.values())

    logger.info(f"Total vectors stored: {total_vectors:,}")
    logger.info(f"Total usage across namespaces: {storage:,}")
    logger.info(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("-" * 60)

    # Try to retrieve a sample vector
    try:
        logger.info("Retrieving sample vectors...")
        sample = index.query(vector=[0.0] * 384, top_k=1, include_metadata=True)
        if sample.get("matches"):
            meta = sample["matches"][0].get("metadata", {})
            logger.info(f"Sample metadata stored: {meta}")
        else:
            logger.warning("No metadata returned (vectors may be in a different namespace).")
    except Exception as e:
        logger.error(f"Could not retrieve sample: {e}")

    logger.info("\nDiagnostics completed successfully.")


if __name__ == "__main__":
    check_pinecone_status()
