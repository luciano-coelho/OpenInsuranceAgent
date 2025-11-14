import streamlit as st
import time
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from app.rag.vectorstore import build_or_load_vectorstore
from app.rag.rag_pipeline import answer_question
from app.rag.prompts import PromptTemplates
from app.rag.ingest import chunk_documents
from app.core.config import settings
from front.i18n import i18n

# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title=i18n.t("page_title"),
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== VECTORSTORE CACHE ====================

@st.cache_resource
def get_vectorstore():
    """Load vectorstore with cache (avoids reloading on each interaction)"""
    return build_or_load_vectorstore()

# ==================== SIDEBAR ====================

with st.sidebar:
    # Apply current language from session (if any) before rendering labels
    if "lang" in st.session_state:
        i18n.set_language(st.session_state["lang"])

    # Language selector (persist in session state)
    lang_display_to_code = {
        i18n.t("language_pt_br"): "pt_BR",
        i18n.t("language_en_us"): "en_US",
    }
    # Determine default index from session
    current_lang = st.session_state.get("lang", "pt_BR")
    default_index = 0 if current_lang == "pt_BR" else 1
    selected_display = st.selectbox(
        i18n.t("language_label"),
        list(lang_display_to_code.keys()),
        index=default_index
    )
    selected_lang = lang_display_to_code[selected_display]
    if selected_lang != current_lang:
        st.session_state["lang"] = selected_lang
        i18n.set_language(selected_lang)

    st.title(i18n.t("sidebar_title"))
    
    st.markdown(i18n.t("llm_model_section"))
    st.info(f"**{i18n.t('llm_provider_label')}:** {settings.llm_provider.upper()}\n\n**{i18n.t('llm_model_label')}:** {settings.llm_model}")
    
    st.markdown(i18n.t("response_style_section"))
    
    style_options = {
        i18n.t("style_concise"): "concise",
        i18n.t("style_detailed"): "detailed",
        i18n.t("style_bullet"): "bullet_points",
        i18n.t("style_yes_no"): "yes_no"
    }
    
    selected_style = st.selectbox(
        i18n.t("response_style_prompt"),
        list(style_options.keys()),
        index=0
    )
    
    prompt_style = style_options[selected_style]
    
    show_contexts = st.checkbox(i18n.t("show_contexts_label"), value=False)
    
    st.markdown(i18n.t("rag_params_section"))
    st.text(f"{i18n.t('param_top_k')}: {settings.top_k}")
    st.text(f"{i18n.t('param_chunk_size')}: {settings.chunk_size}")
    st.text(f"{i18n.t('param_temperature')}: {settings.temperature}")
    st.text(f"{i18n.t('param_max_tokens')}: {settings.max_tokens}")
    
    st.markdown("---")
    
    # Document upload
    st.markdown(i18n.t("upload_section"))
    uploaded_file = st.file_uploader(
        i18n.t("upload_prompt"),
        type=["pdf", "txt", "md"],
        help=i18n.t("upload_help")
    )
    
    if uploaded_file is not None:
        if st.button(i18n.t("upload_button")):
            with st.spinner(i18n.t("upload_processing")):
                try:
                    # Create directory if it doesn't exist
                    upload_dir = Path("data/oi")
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save file
                    file_path = upload_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.info(i18n.t("upload_acquired", filename=uploaded_file.name))
                    
                    # Load document
                    docs = []
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    
                    if file_ext == ".pdf":
                        docs = PyPDFLoader(str(file_path)).load()
                    elif file_ext == ".md":
                        docs = UnstructuredMarkdownLoader(str(file_path)).load()
                    elif file_ext == ".txt":
                        docs = TextLoader(str(file_path), encoding="utf-8").load()
                    
                    if not docs:
                        st.error(i18n.t("upload_error_loading"))
                    else:
                        # Chunking
                        st.info(i18n.t("upload_creating_chunks", num_pages=len(docs)))
                        chunks = chunk_documents(docs)
                        
                        # Add to Pinecone
                        st.info(i18n.t("upload_adding_chunks", num_chunks=len(chunks)))
                        build_or_load_vectorstore(chunks)
                        
                        # Clear cache
                        st.cache_resource.clear()
                        
                        st.success(i18n.t("upload_success"))
                        st.balloons()
                        
                        # Processing information
                        st.markdown(f"""
                        {i18n.t("upload_stats_title")}
                        - {i18n.t("upload_stats_file")}: {uploaded_file.name}
                        - {i18n.t("upload_stats_size")}: {uploaded_file.size / 1024:.2f} KB
                        - {i18n.t("upload_stats_pages")}: {len(docs)}
                        - {i18n.t("upload_stats_chunks")}: {len(chunks)}
                        """)
                        
                except Exception as e:
                    st.error(i18n.t("upload_error", error=str(e)))

# ==================== MAIN ====================

st.title(f"🛡️ {i18n.t('page_title')}")
st.markdown(f"*{i18n.t('page_subtitle')}*")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show contexts if available
        if "contexts" in message and message["contexts"]:
            with st.expander(i18n.t("contexts_expander")):
                for i, ctx in enumerate(message["contexts"], 1):
                    st.markdown(i18n.t("context_label", index=i))
                    st.text(ctx.page_content[:300] + "...")
                    st.caption(i18n.t("context_source", source=ctx.metadata.get('source', 'N/A')))
                    st.markdown("---")

# User input
if question := st.chat_input(i18n.t("chat_input_placeholder")):
    # Add question to history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display question
    with st.chat_message("user"):
        st.markdown(question)


    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(i18n.t("thinking")):
            try:
                # Load vectorstore
                vectorstore = get_vectorstore()
                
                # Select prompt
                prompt_map = {
                    "concise": PromptTemplates.get_concise_rag_prompt(),
                    "detailed": PromptTemplates.get_detailed_rag_prompt(),
                    "bullet_points": PromptTemplates.get_bullet_points_prompt(),
                    "yes_no": PromptTemplates.get_yes_no_prompt()
                }
                prompt_template = prompt_map[prompt_style]
                
                # Execute RAG
                start_time = time.time()
                answer, metadata = answer_question(
                    vectorstore=vectorstore,
                    question=question,
                    return_contexts=show_contexts,
                    prompt_template=prompt_template
                )
                latency = time.time() - start_time
                
                # Display response
                st.markdown(answer)
                st.caption(i18n.t("latency_info", latency=latency, model=settings.llm_model))
                
                # Show contexts if requested
                contexts = metadata.get("contexts", [])
                if show_contexts and contexts:
                    with st.expander(i18n.t("contexts_expander")):
                        for i, ctx in enumerate(contexts, 1):
                            st.markdown(i18n.t("context_label", index=i))
                            st.text(ctx.page_content[:300] + "...")
                            st.caption(i18n.t("context_source", source=ctx.metadata.get('source', 'N/A')))
                            st.markdown("---")
                
                # Add response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "contexts": contexts if show_contexts else []
                })
                
            except Exception as e:
                st.error(i18n.t("error_processing", error=str(e)))

# Footer
st.markdown("---")
st.markdown(i18n.t("footer_tip"))
