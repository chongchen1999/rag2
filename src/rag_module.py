import streamlit as st
from utils import handle_file_upload, get_files_hash
import time
import psutil
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
from performance_module import display_response_metrics

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
        return

    with st.chat_message('user'):
        st.markdown(prompt)

    # Create a unique response ID
    response_id = f"{int(time.time())}_{hash(prompt)}"

    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Start timing and resource monitoring
    start_time = time.time()
    start_cpu = psutil.cpu_percent()
    start_memory = psutil.virtual_memory().percent

    # Generate response with progress updates
    chat_engine = st.session_state['chat_engine']
    
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        res = ''
        
        # Update progress for different stages
        status_text.text("🔍 Retrieving relevant documents...")
        progress_bar.progress(0.2)
        
        status_text.text("💭 Generating response...")
        progress_bar.progress(0.4)
        
        if hasattr(chat_engine, 'stream_chat'):
            response = chat_engine.stream_chat(prompt)
            
            # Stream response with progress updates
            for i, token in enumerate(response.response_gen):
                res += token
                message_placeholder.markdown(res + '▌')
                # Update progress based on token generation
                progress = min(0.4 + (i / 100) * 0.4, 0.8)  # Cap at 80%
                progress_bar.progress(progress)
        else:
            response = chat_engine.generate_response(prompt)
            res = response.response
            message_placeholder.markdown(res)
            progress_bar.progress(0.8)

        # Extract and display source information
        status_text.text("📑 Processing source references...")
        progress_bar.progress(0.9)
        
        source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        if source_nodes:
            with st.expander("📚 Source References"):
                similarity_scores = [node.score for node in source_nodes if hasattr(node, 'score')]
                source_text = format_source_info(source_nodes, similarity_scores if similarity_scores else None)
                st.markdown(source_text)
                
                st.markdown("---")
                st.markdown("**Current Retrieval Parameters:**")
                st.markdown(f"- Number of documents: {current_params['num_docs']}")
                st.markdown(f"- Similarity threshold: {current_params['similarity_threshold']}")

    # Finalize progress
    progress_bar.progress(1.0)
    status_text.text("✅ Response complete!")
    time.sleep(0.5)  # Brief pause to show completion
    status_text.empty()
    progress_bar.empty()

    # Calculate and display metrics
    end_time = time.time()
    end_cpu = psutil.cpu_percent()
    end_memory = psutil.virtual_memory().percent
    
    response_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    memory_usage = end_memory - start_memory

    # Display metrics and collect feedback
    display_response_metrics(response_time, cpu_usage, memory_usage)
    collect_user_feedback(response_id)

    # Cache the response
    cache_response(prompt, res, source_text if source_nodes else None, current_params)

    # Update session state
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': res})