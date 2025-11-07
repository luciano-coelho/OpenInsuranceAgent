import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM
    groq_api_key: str | None = None
    gen_model: str = "llama3-70b-8192"

    # Embeddings
    embed_model: str = "all-MiniLM-L6-v2"

    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "open-insurance-index"

    # RAG
    top_k: int = 5
    chunk_size: int = 600
    chunk_overlap: int = 80

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Debug — imprime se as chaves principais foram lidas
if not settings.pinecone_api_key:
    print("PINECONE_API_KEY não encontrada. Verifique o arquivo .env.")
else:
    print("Pinecone key carregada com sucesso.")
