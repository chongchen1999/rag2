#rag_module.py
import streamlit as st
from utils import handle_file_upload, get_files_hash
import time
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from config import *
from cache_module import cache_response
from cache_module import check_cache
from retrieval_module import add_retrieval_controls
from retrieval_module import format_source_info
from feedback_module import collect_user_feedback
from performance_module import ResourceMonitor

def init_models_rag(temp_dir, generation_config):
    """Initialize RAG models with LlamaIndex and set retrieval parameters."""
    embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL)
    Settings.embed_model = embed_model

    llm = Ollama(
        model=LLM_MODEL,
        request_timeout=LLM_TIMEOUT,
        num_ctx=generation_config['num_ctx'],
        temperature=generation_config['temperature']
    )
    Settings.llm = llm

    # Get current retrieval parameters
    num_docs = st.session_state.get('num_docs', 3)
    similarity_threshold = st.session_state.get('similarity_threshold', 0.65)

    # Set retrieval parameters
    documents = SimpleDirectoryReader(st.session_state['temp_dir']).load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        num_docs=num_docs,
        similarity_threshold=similarity_threshold
    )

    memory = ChatMemoryBuffer.from_defaults(token_limit=DEFAULT_TOKEN_LIMIT)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        verbose=True
    )

    return chat_engine
def handle_rag_mode(uploaded_files, generation_config):
    # Add retrieval parameter controls
    num_docs, similarity_threshold = add_retrieval_controls()
    
    # Check if retrieval parameters have changed
    params_changed = (
        st.session_state.get('num_docs') != num_docs or 
        st.session_state.get('similarity_threshold') != similarity_threshold
    )
    
    # Update session state
    st.session_state['num_docs'] = num_docs
    st.session_state['similarity_threshold'] = similarity_threshold
    
    current_files_hash = get_files_hash(uploaded_files) if uploaded_files else None

    if params_changed or ('files_hash' in st.session_state and st.session_state['files_hash'] != current_files_hash):
        st.session_state['files_hash'] = current_files_hash
        if 'chat_engine' in st.session_state:
            del st.session_state['chat_engine']
            st.cache_resource.clear()
        
        if uploaded_files:
            st.session_state['temp_dir'] = handle_file_upload(uploaded_files)
            st.sidebar.success("Files uploaded successfully.")
            if 'chat_engine' not in st.session_state:
                st.session_state['chat_engine'] = init_models_rag(uploaded_files, generation_config)
        else:
            st.sidebar.error("No uploaded files.")
    elif uploaded_files and 'chat_engine' not in st.session_state:
        st.session_state['files_hash'] = current_files_hash
        st.session_state['temp_dir'] = handle_file_upload(uploaded_files)
        st.sidebar.success("Files uploaded successfully.")
        st.session_state['chat_engine'] = init_models_rag(uploaded_files, generation_config)

def generate_rag_response(prompt):
    if 'chat_engine' not in st.session_state:
        st.error("Please upload files first or switch to non-RAG mode.")
        st.stop()

    current_params = {
        'num_docs': st.session_state['num_docs'],
        'similarity_threshold': st.session_state['similarity_threshold']
    }

    # Check cache
    cached_response, cached_sources = check_cache(prompt, current_params)
    if cached_response:
        st.info("📎 Using cached response")
        with st.chat_message('assistant'):
            st.markdown(cached_response)
            if cached_sources:
                with st.expander("📚 Source References"):
                    st.markdown(cached_sources)
        # Collect feedback for cached responses too
        collect_user_feedback(response_id=f"cached_{hash(prompt)}")
        return

    with st.chat_message('user'):
        st.markdown(prompt)

    # Create a unique response ID
    response_id = f"{int(time.time())}_{hash(prompt)}"

    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    monitor = ResourceMonitor()
    monitor.start_monitoring()

    chat_engine = st.session_state['chat_engine']

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        res = ''
        
        # Define stages with icons and progress percentages
        stages = [
            ("🔍 Retrieving relevant documents...", 0.2),
            ("💭 Generating response...", 0.4),
            ("📑 Processing source references...", 0.9),
            ("✅ Response complete!", 1.0),
        ]

        # Iterate through stages, updating status text and progress bar
        for i, (status, progress) in enumerate(stages):
            status_text.text(status)
            progress_bar.progress(progress)
            if i == 1:  # Generate response during the response generation stage
                if hasattr(chat_engine, 'stream_chat'):
                    response = chat_engine.stream_chat(prompt)
                    for i, token in enumerate(response.response_gen):
                        res += token
                        message_placeholder.markdown(res + '▌')
                        progress_bar.progress(min(progress + (i / 100) * 0.4, 0.8))
                else:
                    response = chat_engine.generate_response(prompt)
                    res = response.response
                    message_placeholder.markdown(res)
                    progress_bar.progress(0.8)

        # Display source information after generation
        source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        source_text = None
        if source_nodes:
            with st.expander("📚 Source References"):
                similarity_scores = [node.score for node in source_nodes if hasattr(node, 'score')]
                source_text = format_source_info(source_nodes, similarity_scores if similarity_scores else None)
                st.markdown(source_text)

                st.markdown("---")
                st.markdown("**Current Retrieval Parameters:**")
                st.markdown(f"- Number of documents: {current_params['num_docs']}")
                st.markdown(f"- Similarity threshold: {current_params['similarity_threshold']}")

    # Finalize progress and clear placeholders
    status_text.text("✅ Response complete!")
    time.sleep(2)  # Brief pause to show completion
    status_text.empty()
    progress_bar.empty()

    monitor.stop_monitoring()

    # Collect user feedback and cache response
    collect_user_feedback(response_id)
    print("Response generated, feedback collected")

    cache_response(prompt, res, source_text if source_nodes else None, current_params)
    print("Response cached.")

    # Update session state messages
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': res})