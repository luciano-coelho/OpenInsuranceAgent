from langchain_groq import ChatGroq
from app.core.config import settings
from app.core.metrics import observe_latency, count_fallbacks
from time import perf_counter

SYSTEM_PROMPT = """Você é um especialista em Segurança da Informação do Open Insurance Brasil (SUSEP).
Responda APENAS com base no contexto fornecido (normativos, guias, portarias, FAPI, DCR, diretório de participantes).
Se não houver evidências suficientes no contexto, diga: "Não há informações suficientes nos documentos oficiais."
Seja objetivo, até 3 frases, e cite o nome do documento quando possível.
"""

def answer_question(vs, question: str):
    start = perf_counter()

    docs = vs.similarity_search(question, k=settings.top_k)
    contexts = [d.page_content for d in docs]
    context_text = "\n\n---\n\n".join(contexts)

    prompt = f"""{SYSTEM_PROMPT}

Pergunta: {question}

[CONTEXTOS]
{context_text}
"""

    llm = ChatGroq(api_key=settings.groq_api_key, model=settings.gen_model, temperature=0.1)
    resp = llm.invoke(prompt)
    answer = (resp.content or "").strip()

    latency = round(perf_counter() - start, 3)
    observe_latency(latency)
    count_fallbacks(answer)

    return answer, {"latency": latency, "contexts": len(contexts)}
