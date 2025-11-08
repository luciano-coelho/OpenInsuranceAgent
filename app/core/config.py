from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ---- Ollama / LLM ----
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3"

    # ---- Embeddings ----
    embed_model: str = "nomic-embed-text"

    # ---- Pinecone ----
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "open-insurance-index"

    # ---- RAG ----
    top_k: int = 5
    chunk_size: int = 600
    chunk_overlap: int = 80

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignora variáveis extras que não estão definidas no modelo


settings = Settings()
