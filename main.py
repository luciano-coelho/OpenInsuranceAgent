from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.routes import router as api_router
from app.core.config import settings

# ==================== API CONFIGURATION ====================

app = FastAPI(
    title="Open Insurance Agent API",
    description="""
    A modular and auditable AI agent for regulatory analysis of Open Insurance Brazil.

    Repository: https://github.com/luciano-coelho/OpenInsuranceAgent
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Open Insurance Agent",
            "description": "Primary endpoints for agent queries and information"
        },
        {
            "name": "System",
            "description": "System endpoints (root, health, metrics)"
        }
    ]
)

# ==================== MIDDLEWARE ====================

# CORS - Allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains explicitly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MAIN ROUTES ====================

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to Swagger documentation."""
    return RedirectResponse(url="/docs")

# Incluir rotas da API
app.include_router(api_router)
