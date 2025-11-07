import os
from app.core.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


def _ensure_index(pc: Pinecone):
    """Cria o índice Pinecone se ele ainda não existir."""
    names = [i["name"] for i in pc.list_indexes()]
    if settings.pinecone_index_name not in names:
        print(f"Criando índice '{settings.pinecone_index_name}' no Pinecone...")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=384,  # compatível com all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
        )
    else:
        print(f"ℹÍndice '{settings.pinecone_index_name}' já existe.")


def build_or_load_vectorstore(chunks=None):
    """Cria ou carrega o vetorstore do Pinecone."""
    print("Conectando ao Pinecone...")

    # FORÇA a variável no ambiente para que o SDK do LangChain reconheça
    os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
    os.environ["PINECONE_ENVIRONMENT"] = settings.pinecone_environment

    pc = Pinecone(api_key=settings.pinecone_api_key)
    _ensure_index(pc)

    print("Carregando modelo de embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=settings.embed_model)

    if chunks:
        print("Inserindo chunks no índice Pinecone...")
        vs = PineconeVectorStore.from_documents(
            chunks,
            embedding=embeddings,
            index_name=settings.pinecone_index_name
        )
    else:
        print("Carregando índice existente do Pinecone...")
        vs = PineconeVectorStore.from_existing_index(
            embedding=embeddings,
            index_name=settings.pinecone_index_name
        )

    print("Vetorstore pronto.")
    return vs
