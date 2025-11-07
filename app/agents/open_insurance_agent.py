from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from app.core.logger import logger

logger.info("Carregando vetor Pinecone...")
vs = build_or_load_vectorstore()  # carrega índice existente
logger.info("Vetor carregado.")

def run_oi_agent(question: str):
    logger.info(f"[Pergunta] {question}")
    answer, meta = answer_question(vs, question)
    logger.info(f"[Resposta] latência={meta['latency']}s | ctx={meta['contexts']}")
    return {"answer": answer, "meta": meta}
