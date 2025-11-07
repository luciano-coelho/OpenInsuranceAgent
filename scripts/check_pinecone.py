import os
from datetime import datetime
from app.core.config import settings
from pinecone import Pinecone


def check_pinecone_status():
    print("Conectando ao Pinecone...")

    # Garantir que a key esteja disponível no ambiente
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
    os.environ["PINECONE_ENVIRONMENT"] = settings.pinecone_environment

    pc = Pinecone(api_key=settings.pinecone_api_key)
    indexes = pc.list_indexes()

    if not indexes:
        print("Nenhum índice encontrado.")
        return

    print(f"\nÍndices disponíveis ({len(indexes)}):")
    for idx in indexes:
        print(f"  • {idx['name']}  |  {idx['status']}  |  {idx['metric']}  |  Dimensão: {idx['dimension']}")
    print("-" * 60)

    # Acessa o índice configurado no projeto
    index_name = settings.pinecone_index_name
    index = pc.Index(index_name)

    print(f"\n🔎 Verificando status do índice '{index_name}'...")
    stats = index.describe_index_stats()

    total_vectors = stats.get("total_vector_count", 0)
    namespace_data = stats.get("namespaces", {})
    storage = sum(ns.get("vector_count", 0) for ns in namespace_data.values())

    print(f"Vetores totais armazenados: {total_vectors:,}")
    print(f"Uso total por namespaces: {storage:,}")
    print(f"Verificado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("-" * 60)

    # Tenta coletar uma amostra de vetores (caso existam)
    try:
        print("Recuperando amostra de vetores...")
        sample = index.query(vector=[0.0] * 384, top_k=1, include_metadata=True)
        if sample.get("matches"):
            meta = sample["matches"][0].get("metadata", {})
            print(f"Exemplo de metadado armazenado: {meta}")
        else:
            print("Nenhum metadado retornado (vetores podem estar em namespace diferente).")
    except Exception as e:
        print(f"Não foi possível recuperar amostra: {e}")

    print("\nDiagnóstico concluído com sucesso.")


if __name__ == "__main__":
    check_pinecone_status()
