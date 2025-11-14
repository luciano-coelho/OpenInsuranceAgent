from time import perf_counter
from app.core.config import settings, llm
from app.rag.prompts import PromptTemplates


def answer_question(
    vectorstore,
    question: str,
    return_contexts: bool = False,
    prompt_template=None,
):
    """Run the RAG pipeline and return the answer and metadata.

    Parameters:
    - vectorstore: VectorStore to retrieve relevant chunks
    - question: user question
    - return_contexts: if True, include retrieved Documents in metadata
    - prompt_template: optional LangChain PromptTemplate; uses the concise template by default
    """
    start = perf_counter()

    # Manual identity response for "who are you"-type questions (Portuguese triggers supported)
    ql = (question or "").strip().lower()
    identity_triggers = [
        "quem é você", "quem é vc", "quem é voce", "quem é o agente", "quem é o bot",
        "o que você é", "o que vc é", "o que voce é", "o que você faz", "sobre você",
        "qual seu nome", "quem é este sistema", "quem é esse sistema"
    ]
    if any(trigger in ql for trigger in identity_triggers):
        intro = (
            "Sou um assistente de IA modular e auditável para análise normativa do Open Insurance Brasil. "
            "Posso te ajudar a: responder dúvidas sobre normas e guias da SUSEP/OPIN, explicar requisitos técnicos "
            "(como FAPI, DCR e certificados), recuperar trechos e referências dos documentos oficiais e resumir conteúdos."
        )
        latency = round(perf_counter() - start, 3)
        metadata = {"latency": latency, "contexts": [] if return_contexts else None}
        return intro, metadata

    # Document retrieval (optional MMR)
    if getattr(settings, "use_mmr", False):
        docs = vectorstore.max_marginal_relevance_search(
            question,
            k=settings.top_k,
            lambda_mult=getattr(settings, "mmr_diversity_score", 0.3),
        )
    else:
        docs = vectorstore.similarity_search(question, k=settings.top_k)

    context_text = "\n\n---\n\n".join([d.page_content for d in docs])

    # Select default template if none provided
    prompt_template = prompt_template or PromptTemplates.get_concise_rag_prompt()
    final_prompt = prompt_template.format(context=context_text, question=question)

    resp = llm.invoke(final_prompt)
    answer = (getattr(resp, "content", "") or "").strip()

    latency = round(perf_counter() - start, 3)

    metadata = {"latency": latency}
    if return_contexts:
        metadata["contexts"] = docs

    return answer, metadata
