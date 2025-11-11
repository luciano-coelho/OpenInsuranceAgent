import streamlit as st
import time
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from app.rag.prompts import PromptTemplates
from app.rag.ingest import chunk_documents
from app.core.config import settings

# ==================== CONFIGURAÇÃO DA PÁGINA ====================

st.set_page_config(
    page_title="Open Insurance Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CACHE DO VECTORSTORE ====================

@st.cache_resource
def get_vectorstore():
    """Carrega vectorstore com cache (evita recarregar a cada interação)"""
    return build_or_load_vectorstore()

# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("⚙️ Configurações")
    
    st.markdown("### Modelo LLM")
    st.info(f"**Provedor:** {settings.llm_provider.upper()}\n\n**Modelo:** {settings.llm_model}")
    
    st.markdown("### Estilo de Resposta")
    
    style_options = {
        "Resumido (2-3 frases)": "concise",
        "Detalhado (explicação completa)": "detailed",
        "Lista com tópicos": "bullet_points",
        "Sim/Não (resposta direta)": "yes_no"
    }
    
    selected_style = st.selectbox(
        "Escolha como você quer sua resposta:",
        list(style_options.keys()),
        index=0
    )
    
    prompt_style = style_options[selected_style]
    
    show_contexts = st.checkbox("Mostrar contextos recuperados", value=False)
    
    st.markdown("### Parâmetros RAG")
    st.text(f"Top K: {settings.top_k}")
    st.text(f"Chunk Size: {settings.chunk_size}")
    st.text(f"Temperature: {settings.temperature}")
    st.text(f"Max Tokens: {settings.max_tokens}")
    
    st.markdown("---")
    
    # Upload de documentos
    st.markdown("### Upload de Documento")
    uploaded_file = st.file_uploader(
        "Adicione novos documentos para me deixar mais inteligente:",
        type=["pdf", "txt", "md"],
        help="Faça upload de arquivos PDF, TXT ou MD para adicionar à base de conhecimento"
    )
    
    if uploaded_file is not None:
        if st.button("Processar e Adicionar"):
            with st.spinner("Adquirindo conhecimento..."):
                try:
                    # Criar diretório se não existir
                    upload_dir = Path("data/oi")
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Salvar arquivo
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.info(f"Conhecimento adquirido: {uploaded_file.name}")
                    
                    # Carregar documento
                    docs = []
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    
                    if file_ext == ".pdf":
                        docs = PyPDFLoader(str(file_path)).load()
                    elif file_ext == ".md":
                        docs = UnstructuredMarkdownLoader(str(file_path)).load()
                    elif file_ext == ".txt":
                        docs = TextLoader(str(file_path), encoding="utf-8").load()
                    
                    if not docs:
                        st.error("Não foi possível carregar o documento")
                    else:
                        # Chunking
                        st.info(f"Criando chunks ({len(docs)} páginas carregadas)...")
                        chunks = chunk_documents(docs)
                        
                        # Adicionar ao Pinecone
                        st.info(f"Adicionando {len(chunks)} chunks ao Pinecone...")
                        build_or_load_vectorstore(chunks)
                        
                        # Limpar cache
                        st.cache_resource.clear()
                        
                        st.success(f"Obrigado. Você acaba de me deixar mais inteligente!")
                        st.balloons()
                        
                        # Informações do processamento
                        st.markdown(f"""
                        **Estatísticas:**
                        - Arquivo: {uploaded_file.name}
                        - Tamanho: {uploaded_file.size / 1024:.2f} KB
                        - Páginas: {len(docs)}
                        - Chunks criados: {len(chunks)}
                        """)
                        
                except Exception as e:
                    st.error(f"Erro ao processar: {str(e)}")

# ==================== MAIN ====================

st.title("🛡️ Open Insurance Agent")
st.markdown("*Seu assistente de IA modular e auditável para análise normativa do Open Insurance Brasil*")

# Inicializar histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Mostrar contextos se disponíveis
        if "contexts" in message and message["contexts"]:
            with st.expander("📚 Ver contextos recuperados"):
                for i, ctx in enumerate(message["contexts"], 1):
                    st.markdown(f"**Contexto {i}:**")
                    st.text(ctx.page_content[:300] + "...")
                    st.caption(f"Fonte: {ctx.metadata.get('source', 'N/A')}")
                    st.markdown("---")

# Input do usuário
if question := st.chat_input("Faça sua pergunta sobre Open Insurance..."):
    # Adicionar pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Exibir pergunta
    with st.chat_message("user"):
        st.markdown(question)


    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Carregar vectorstore
                vectorstore = get_vectorstore()
                
                # Selecionar prompt
                prompt_map = {
                    "concise": PromptTemplates.get_concise_rag_prompt(),
                    "detailed": PromptTemplates.get_detailed_rag_prompt(),
                    "bullet_points": PromptTemplates.get_bullet_points_prompt(),
                    "yes_no": PromptTemplates.get_yes_no_prompt()
                }
                prompt_template = prompt_map[prompt_style]
                
                # Executar RAG
                start_time = time.time()
                answer, metadata = answer_question(
                    vectorstore=vectorstore,
                    question=question,
                    return_contexts=show_contexts,
                    prompt_template=prompt_template
                )
                latency = time.time() - start_time
                
                # Exibir resposta
                st.markdown(answer)
                st.caption(f"Latência: {latency:.2f}s | {settings.llm_model}")
                
                # Mostrar contextos se solicitado
                contexts = metadata.get("contexts", [])
                if show_contexts and contexts:
                    with st.expander("Ver contextos recuperados"):
                        for i, ctx in enumerate(contexts, 1):
                            st.markdown(f"**Contexto {i}:**")
                            st.text(ctx.page_content[:300] + "...")
                            st.caption(f"Fonte: {ctx.metadata.get('source', 'N/A')}")
                            st.markdown("---")
                
                # Adicionar resposta ao histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "contexts": contexts if show_contexts else []
                })
                
            except Exception as e:
                st.error(f"Erro ao processar pergunta: {str(e)}")

# Footer
st.markdown("---")
st.markdown("💡 **Dica:** Use o menu lateral para ajustar o estilo de resposta e fazer upload de novos documentos")
