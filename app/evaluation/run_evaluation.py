import json
import time
import mlflow
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness
from app.core.config import settings
from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

if __name__ == "__main__":
    vs = build_or_load_vectorstore()  # usa índice existente

    with open("app/evaluation/evaluation.json", encoding="utf-8") as f:
        eval_rows = json.load(f)

    ragas_rows = []
    total_latency = 0.0

    for row in eval_rows:
        q, ideal = row["question"], row["ideal_answer"]
        ans, meta = answer_question(vs, q)
        ragas_rows.append({
            "question": q,
            "answer": ans,
            "contexts": [],           # opcionalmente, logue os textos aqui
            "ground_truth": ideal
        })
        total_latency += meta["latency"]

    ds = Dataset.from_list(ragas_rows)
    avg_latency = round(total_latency / max(1, len(ragas_rows)), 3)

    judge_llm = ChatGroq(api_key=settings.groq_api_key, model=settings.gen_model)
    embedder = HuggingFaceEmbeddings(model_name=settings.embed_model)

    with mlflow.start_run():
        mlflow.log_param("model", settings.gen_model)
        mlflow.log_param("embeddings", settings.embed_model)
        mlflow.log_param("top_k", settings.top_k)
        mlflow.log_param("num_questions", len(ragas_rows))

        print("🔎 Avaliando com RAGAs (faithfulness)...")
        t0 = time.perf_counter()
        results = evaluate(ds, metrics=[faithfulness], llm=judge_llm, embeddings=embedder)
        duration = round(time.perf_counter() - t0, 2)

        mlflow.log_metric("avg_latency", avg_latency)
        mlflow.log_metric("eval_duration_s", duration)
        for k, v in results.items():
            try:
                mlflow.log_metric(k, float(v))
            except Exception:
                pass

        print("✅ Resultados:", results)
        print(f"⏱️ Latência média: {avg_latency}s | ⌛ Duração avaliação: {duration}s")
