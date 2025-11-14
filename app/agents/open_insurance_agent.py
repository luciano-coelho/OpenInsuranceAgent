from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from app.core.logger import logger

logger.info("Loading Pinecone vectorstore...")
vectorstore = build_or_load_vectorstore()  # load existing index
logger.info("Vectorstore loaded.")

def run_oi_agent(question: str):
    logger.info(f"[Question] {question}")
    answer, meta = answer_question(vectorstore, question)
    logger.info(f"[Answer] latency={meta['latency']}s | ctx={meta['contexts']}")
    return {"answer": answer, "meta": meta}
