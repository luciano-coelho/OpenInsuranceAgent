from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ---- LLM Provider ----
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    llm_provider: str = "groq"  # "groq" ou "google"
    llm_model: str = "llama-3.3-70b-versatile"
    
    # ---- LLM Parameters ----
    temperature: float = 0.3
    max_tokens: int = 300

    # ---- Embeddings ----
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ---- Pinecone ----
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "open-insurance-index"

    # ---- RAG ----
    top_k: int = 7
    chunk_size: int = 800
    chunk_overlap: int = 100
    use_mmr: bool = True
    mmr_diversity_score: float = 0.3

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Inicializar LLM baseado no provider
def _init_llm():
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.llm_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
    elif settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens,
            google_api_key=settings.google_api_key
        )
    else:
        raise ValueError(f"Provider não suportado: {settings.llm_provider}")

# Instância do LLM
llm = _init_llm()
