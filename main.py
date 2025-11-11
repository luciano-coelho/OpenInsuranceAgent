from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.routes import router as api_router
from app.core.config import settings

# ==================== CONFIGURAÇÃO DA API ====================

app = FastAPI(
    title="Open Insurance Agent API",
    description="""
    Um agente de IA modular e auditável para análise normativa do Open Insurance Brasil
    
    Repositório: https://github.com/luciano-coelho/OpenInsuranceAgent
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Open Insurance Agent",
            "description": "Endpoints principais para consultas e informações do agente"
        },
        {
            "name": "System",
            "description": "Endpoints de sistema (root, health, métricas)"
        }
    ]
)

# ==================== MIDDLEWARE ====================

# CORS - Permitir requisições de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROTAS PRINCIPAIS ====================

@app.get("/", include_in_schema=False)
async def root():
    """Redireciona para documentação Swagger"""
    return RedirectResponse(url="/docs")

# Incluir rotas da API
app.include_router(api_router)
