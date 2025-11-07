from fastapi import APIRouter
from app.agents.open_insurance_agent import run_oi_agent

router = APIRouter(prefix="/oi", tags=["Open Insurance"])

@router.get("/ask")
def ask(query: str):
    """Consulta o agente com uma pergunta."""
    return run_oi_agent(query)
