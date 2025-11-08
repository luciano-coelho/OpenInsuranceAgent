import sys
import time
from app.core.config import settings
from app.rag.vectorstore import build_or_load_vectorstore

# LangChain 0.3+ compatível
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():
    print("Configurações carregadas com sucesso.")
    print(f"🔹 Modelo LLM: {settings.llm_model}")
    print(f"🔹 Modelo de embeddings: {settings.embed_model}")
    print(f"🔹 Pinecone index: {settings.pinecone_index_name}")

    # Pergunta do usuário
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Pergunta: ")

    print(f"\nPergunta: {query}\n")

    # ---- Carregar vetorstore Pinecone ----
    print("Conectando ao Pinecone...")
    vs = build_or_load_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": settings.top_k})
    print("Vetorstore carregado com sucesso.")

    # ---- LLM (Ollama local) ----
    llm = Ollama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
    )

    # ---- Recuperar contexto ----
    print("Recuperando contexto...")
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    print(f"{len(docs)} trechos de contexto carregados.\n")

    # ---- Template de prompt ----
    template = """
Você é um assistente especializado no Open Insurance Brasil.
Responda de forma objetiva, fundamentada e cite o contexto quando necessário.

Contexto:
{context}

Pergunta:
{question}

Resposta fundamentada:
"""
    prompt = PromptTemplate.from_template(template)

    # ---- Executar pipeline ----
    start = time.time()
    formatted_prompt = prompt.format(context=context, question=query)
    print("Gerando resposta com o modelo Ollama...\n")
    response = llm.invoke(formatted_prompt)
    end = time.time()

    # ---- Exibir resultado ----
    print("=" * 70)
    print("RESPOSTA:")
    print(response)
    print("=" * 70)
    print(f"Tempo de resposta: {end - start:.2f}s")


if __name__ == "__main__":
    main()
