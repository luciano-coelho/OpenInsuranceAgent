from pathlib import Path
from time import perf_counter
from app.rag.ingest import load_documents, chunk_documents
from app.rag.vectorstore import build_or_load_vectorstore

def ingest_open_insurance_docs():
    t0 = perf_counter()
    base_dir = Path("data/oi")

    if not base_dir.exists():
        print("Pasta 'data/oi/' não encontrada. Crie-a e adicione os arquivos oficiais da SUSEP/Open Insurance.")
        return

    print("Lendo documentos em data/oi/ ...")
    docs = load_documents(str(base_dir))
    print(f"Total de documentos encontrados: {len(docs)}")

    if not docs:
        print("Nenhum arquivo encontrado. Verifique se há PDFs, TXTs ou MDs na pasta.")
        return

    print("Dividindo documentos em chunks...")
    chunks = chunk_documents(docs)
    print(f"Chunks gerados: {len(chunks)}")

    print("Armazenando embeddings no Pinecone...")
    vs = build_or_load_vectorstore(chunks)

    elapsed = round(perf_counter() - t0, 2)
    print(f"Ingestão concluída com sucesso em {elapsed}s!")
    print("Vetores disponíveis no índice Pinecone configurado em .env.")

if __name__ == "__main__":
    ingest_open_insurance_docs()
