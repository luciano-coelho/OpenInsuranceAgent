from fastapi import FastAPI
from app.api.routes import router as oi_router

app = FastAPI(
    title="Open Insurance Security Assistant",
    description="Agente RAG com Groq + Pinecone para Segurança da Informação do Open Insurance Brasil.",
    version="1.0.0",
)

@app.get("/", tags=["Status"])
def root():
    return {"message": "API Open Insurance Security Agent ativa."}

app.include_router(oi_router)
