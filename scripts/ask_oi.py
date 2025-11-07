"""
scripts/ask_oi.py
Consulta o agente Open Insurance usando Groq (SDK legado 0.33.0)
e busca contexto no Pinecone para compor respostas RAG.
"""

import os
from groq import Groq
from app.core.config import settings
from app.rag.vectorstore import build_or_load_vectorstore

# ===============================================================
# Inicialização
# ===============================================================
print("Pinecone key carregada com sucesso.")
os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key

# Modelos Groq compatíveis (ordem de fallback)
AVAILABLE_MODELS = [
    "mixtral-8x7b-32768",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "gemma2-9b-it"
]

# ===============================================================
# Funções principais
# ===============================================================

def build_prompt(question: str, context_text: str) -> list:
    """Cria mensagens de chat para o modelo."""
    return [
        {"role": "system", "content": (
            "Você é um assistente técnico especializado no ecossistema Open Insurance Brasil. "
            "Responda apenas com base nas normas, RDDs e documentos oficiais SUSEP. "
            "Se não houver informação suficiente, diga: 'Não há informações suficientes nos documentos.'"
        )},
        {"role": "user", "content": (
            f"Pergunta: {question}\n\n"
            f"[Contexto de documentos]:\n{context_text}\n\n"
            "Responda de forma técnica, concisa e baseada apenas nas fontes fornecidas."
        )}
    ]


def query_pinecone(question: str, top_k: int = 5) -> str:
    """Busca contexto relevante no Pinecone."""
    print("Conectando ao Pinecone...")
    vs = build_or_load_vectorstore()
    docs = vs.similarity_search(question, k=top_k)
    return "\n\n".join([d.page_content for d in docs])


def answer_with_groq(messages: list) -> str:
    """Consulta o modelo Groq via Chat API (SDK 0.33.x)."""
    client = Groq(api_key=settings.groq_api_key)

    last_error = None
    for model in AVAILABLE_MODELS:
        try:
            print(f"Tentando modelo {model} ...")
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=600,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro com modelo {model}: {e}")
            last_error = e
            continue

    raise RuntimeError(f"Nenhum modelo Groq respondeu com sucesso. Último erro: {last_error}")


# ===============================================================
# Execução principal
# ===============================================================

def main():
    import sys
    if len(sys.argv) < 2:
        print("Uso: python -m scripts.ask_oi \"sua pergunta aqui\"")
        return

    question = sys.argv[1]
    print(f"Pergunta: {question}")

    # Recupera contexto
    context = query_pinecone(question)
    print(f"Contexto recuperado ({len(context)} caracteres).")

    # Monta prompt e envia ao modelo
    messages = build_prompt(question, context)
    answer = answer_with_groq(messages)

    print("\n" + "="*80)
    print("Resposta final:")
    print(answer)
    print("="*80)


if __name__ == "__main__":
    main()
