from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time
import os
from pathlib import Path

from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from app.rag.prompts import PromptTemplates
from app.rag.ingest import load_documents, chunk_documents
from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["Open Insurance Agent"])

# Cache do vectorstore
_vectorstore_cache = None

def get_vectorstore():
    """Dependency para obter vectorstore com cache"""
    global _vectorstore_cache
    if _vectorstore_cache is None:
        _vectorstore_cache = build_or_load_vectorstore()
    return _vectorstore_cache


# ==================== MODELS ====================

class QuestionRequest(BaseModel):
    """Request para consulta ao agente"""
    question: str = Field(..., description="Pergunta sobre Open Insurance Brasil", min_length=5, max_length=500)
    prompt_style: Optional[str] = Field("concise", description="Estilo do prompt: concise, detailed, bullet_points, yes_no")
    return_contexts: Optional[bool] = Field(False, description="Retornar contextos recuperados do vectorstore")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quais são os requisitos de certificados no Open Insurance?",
                "prompt_style": "concise",
                "return_contexts": True
            }
        }


class Context(BaseModel):
    """Contexto recuperado do vectorstore"""
    content: str = Field(..., description="Conteúdo do chunk")
    source: str = Field(..., description="Fonte do documento")
    page: Optional[int] = Field(None, description="Página do documento (se disponível)")


class QuestionResponse(BaseModel):
    """Response com resposta do agente"""
    question: str = Field(..., description="Pergunta original")
    answer: str = Field(..., description="Resposta gerada pelo LLM")
    model: str = Field(..., description="Modelo LLM utilizado")
    provider: str = Field(..., description="Provider LLM (groq, google, etc)")
    latency_seconds: float = Field(..., description="Latência da resposta em segundos")
    contexts: Optional[List[Context]] = Field(None, description="Contextos recuperados (se solicitado)")
    metadata: Dict[str, Any] = Field(..., description="Metadados adicionais")


class HealthResponse(BaseModel):
    """Response do health check"""
    status: str = Field(..., description="Status da API (healthy/unhealthy)")
    provider: str = Field(..., description="Provider LLM configurado")
    model: str = Field(..., description="Modelo LLM configurado")
    vectorstore_ready: bool = Field(..., description="Vectorstore Pinecone pronto")
    top_k: int = Field(..., description="Número de chunks recuperados")


class MetricsResponse(BaseModel):
    """Response com métricas do sistema"""
    provider: str
    model: str
    embedding_model: str
    pinecone_index: str
    top_k: int
    chunk_size: int
    chunk_overlap: int
    use_mmr: bool
    temperature: float
    max_tokens: int


# ==================== ENDPOINTS ====================

@router.post("/ask", response_model=QuestionResponse, summary="Query Open Insurance Agent")
async def ask_question(
    request: QuestionRequest,
    vectorstore = Depends(get_vectorstore)
):
    """
    **Query the specialized Open Insurance Brasil agent**
    
    Receives a question and returns an answer grounded in official SUSEP documents,
    using RAG (Retrieval-Augmented Generation) techniques.
    
    **Available prompt styles:**
    - `concise`: Brief answers in 2-3 sentences (default)
    - `detailed`: Detailed and complete explanations
    - `bullet_points`: Structured responses in bullet points
    - `yes_no`: Binary answers with brief justification
    
    **Usage example:**
    ```json
    {
      "question": "What is Open Insurance?",
      "prompt_style": "concise",
      "return_contexts": true
    }
    ```
    """
    try:
        start_time = time.time()
        
        # Selecionar template de prompt
        prompt_map = {
            "concise": PromptTemplates.get_concise_rag_prompt(),
            "detailed": PromptTemplates.get_detailed_rag_prompt(),
            "bullet_points": PromptTemplates.get_bullet_points_prompt(),
            "yes_no": PromptTemplates.get_yes_no_prompt()
        }
        
        prompt_template = prompt_map.get(request.prompt_style, PromptTemplates.get_concise_rag_prompt())
        
        # Executar consulta RAG
        answer, metadata = answer_question(
            vectorstore=vectorstore,
            question=request.question,
            return_contexts=request.return_contexts,
            prompt_template=prompt_template
        )
        
        latency = time.time() - start_time
        
        # Preparar contextos se solicitado
        contexts_list = None
        if request.return_contexts and "contexts" in metadata:
            contexts_list = [
                Context(
                    content=ctx.page_content,
                    source=ctx.metadata.get("source", "unknown"),
                    page=ctx.metadata.get("page")
                )
                for ctx in metadata["contexts"]
            ]
        
        return QuestionResponse(
            question=request.question,
            answer=answer,
            model=settings.llm_model,
            provider=settings.llm_provider,
            latency_seconds=round(latency, 2),
            contexts=contexts_list,
            metadata={
                "prompt_style": request.prompt_style,
                "top_k": settings.top_k,
                "use_mmr": settings.use_mmr,
                "internal_latency": metadata.get("latency")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")


@router.get("/health", response_model=HealthResponse, summary="API health check")
async def health_check():
    """
    **Check the health status of the API**
    
    Returns information about current configuration and service availability.
    """
    try:
        vectorstore = get_vectorstore()
        vectorstore_ready = vectorstore is not None
        
        return HealthResponse(
            status="healthy",
            provider=settings.llm_provider,
            model=settings.llm_model,
            vectorstore_ready=vectorstore_ready,
            top_k=settings.top_k
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            provider=settings.llm_provider,
            model=settings.llm_model,
            vectorstore_ready=False,
            top_k=settings.top_k
        )


@router.get("/metrics", response_model=MetricsResponse, summary="Get system metrics")
async def get_metrics():
    """
    **Return system metrics and configurations**
    
    Information about models, embeddings, RAG configuration, and optimization parameters.
    """
    return MetricsResponse(
        provider=settings.llm_provider,
        model=settings.llm_model,
        embedding_model=settings.embedding_model,
        pinecone_index=settings.pinecone_index_name,
        top_k=settings.top_k,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        use_mmr=settings.use_mmr,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )


# ==================== UPLOAD MODELS ====================

class UploadResponse(BaseModel):
    """Response do upload e ingestão"""
    success: bool = Field(..., description="Status do upload")
    filename: str = Field(..., description="Nome do arquivo salvo")
    file_path: str = Field(..., description="Caminho completo do arquivo")
    file_size_bytes: int = Field(..., description="Tamanho do arquivo em bytes")
    chunks_created: int = Field(..., description="Número de chunks gerados")
    vectors_added: int = Field(..., description="Vetores adicionados ao Pinecone")
    processing_time_seconds: float = Field(..., description="Tempo de processamento")
    message: str = Field(..., description="Mensagem descritiva")


# ==================== UPLOAD ENDPOINT ====================

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
UPLOAD_DIR = Path("data/oi")

@router.post("/upload", response_model=UploadResponse, summary="Upload and ingest documents")
async def upload_document(
    file: UploadFile = File(..., description="File to upload (PDF, TXT, or MD)")
):
    """
    **Upload new documents to the Open Insurance system**
    
    This endpoint allows the team to upload new official SUSEP/OPIN documents.
    The file will be:
    1. Validated (format and size)
    2. Saved to `data/oi/`
    3. Processed (chunking + embeddings)
    4. Added to the Pinecone index
    
    **Accepted formats:** PDF, TXT, MD
    
    **Maximum size:** 50 MB
    
    **Usage example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/upload" \\
      -F "file=@circular_susep_123.pdf"
    ```
    
    **Note:** The ingestion process may take a few seconds depending on the file size.
    """
    start_time = time.time()
    
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate size (maximum 50 MB)
        content = await file.read()
        file_size = len(content)
        max_size = 50 * 1024 * 1024  # 50 MB
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: 50 MB"
            )
        
        # Create directory if it doesn't exist
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ").strip()
        file_path = UPLOAD_DIR / safe_filename
        
        # Check if file already exists
        if file_path.exists():
            # Add timestamp to name
            timestamp = int(time.time())
            name_parts = safe_filename.rsplit(".", 1)
            if len(name_parts) == 2:
                safe_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                safe_filename = f"{safe_filename}_{timestamp}"
            file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"📄 File saved: {file_path}")
        
        # Process document (ingestion) - load specific file
        print("📚 Loading document...")
        docs = []
        
        try:
            if file_ext == ".pdf":
                from langchain_community.document_loaders import PyPDFLoader
                print(f"🔍 Trying to load PDF: {file_path}")
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                print(f"✅ PDF loaded with {len(docs)} pages")
            elif file_ext == ".md":
                from langchain_community.document_loaders import UnstructuredMarkdownLoader
                docs = UnstructuredMarkdownLoader(str(file_path)).load()
            elif file_ext == ".txt":
                from langchain_community.document_loaders import TextLoader
                docs = TextLoader(str(file_path), encoding="utf-8").load()
        except Exception as e:
            # Clean up file on error
            print(f"❌ Error loading: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"Error loading document: {str(e)}"
            )
        
        if not docs:
            # Clean up file if loading failed
            file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Empty document or unsupported format."
            )
        
        print(f"✂️ Creating chunks (docs loaded: {len(docs)})...")
        chunks = chunk_documents(docs)
        chunks_count = len(chunks)
        
        print(f"🔄 Adding {chunks_count} chunks to Pinecone...")
        vectorstore = build_or_load_vectorstore(chunks)
        
        # Clear vectorstore cache in API
        global _vectorstore_cache
        _vectorstore_cache = None
        
        processing_time = time.time() - start_time
        
        print(f"✅ Ingestion completed in {processing_time:.2f}s")
        
        return UploadResponse(
            success=True,
            filename=safe_filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            chunks_created=chunks_count,
            vectors_added=chunks_count,  # Each chunk = 1 vector
            processing_time_seconds=round(processing_time, 2),
            message="Thank you. You just made me smarter!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Try to clean up file on error
        if 'file_path' in locals() and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )
