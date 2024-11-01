import streamlit as st
from utils import handle_file_upload, get_files_hash
import time
import psutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from config import *

# Cache configuration
from collections import deque
QUERY_CACHE_LIMIT = 10
query_cache = deque(maxlen=QUERY_CACHE_LIMIT)

def add_retrieval_controls():
    """Add sidebar controls for adjusting retrieval parameters."""
    st.sidebar.markdown("### Retrieval Parameters")
    
    num_docs = st.sidebar.slider(
        "Number of Retrieved Documents",
        min_value=1,
        max_value=10,
        value=5,
        help="Adjust how many documents to retrieve for each query. More documents may provide more context but could introduce noise."
    )
    
    similarity_threshold = st.sidebar.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Set the minimum similarity score for retrieved documents. Higher values mean stricter matching."
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Reset Parameters"):
        st.session_state['num_docs'] = 5
        st.session_state['similarity_threshold'] = 0.75
        # Force reinitialization of the chat engine
        if 'chat_engine' in st.session_state:
            del st.session_state['chat_engine']
    
    return num_docs, similarity_threshold

def cache_response(prompt, response, sources, retrieval_params):
    """Add a new query-response pair to the cache."""
    query_cache.append({
        'prompt': prompt, 
        'response': response,
        'sources': sources,
        'retrieval_params': retrieval_params
    })

def check_cache(prompt, current_params):
    """Check if the prompt already has a cached response with matching parameters."""
    for item in query_cache:
        if item['prompt'] == prompt and item['retrieval_params'] == current_params:
            return item['response'], item['sources']
    return None, None

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
    num_docs = st.session_state.get('num_docs', 5)
    similarity_threshold = st.session_state.get('similarity_threshold', 0.75)

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

def format_source_info(source_nodes, similarity_scores=None):
    """Format source information for display with similarity scores."""
    source_info = []
    for i, node in enumerate(source_nodes):
        filename = node.metadata.get('file_name', 'Unknown source')
        text_snippet = node.text[:200] + "..." if len(node.text) > 200 else node.text
        
        # Include similarity score if available
        score_info = f" (Similarity: {similarity_scores[i]:.2f})" if similarity_scores and i < len(similarity_scores) else ""
        
        source_info.append(f"📄 **{filename}**{score_info}\n> {text_snippet}")
    return "\n\n".join(source_info)

def generate_rag_response(prompt):
    if 'chat_engine' not in st.session_state:
        st.error("Please upload files first or switch to non-RAG mode.")
        st.stop()

    # Get current retrieval parameters
    current_params = {
        'num_docs': st.session_state['num_docs'],
        'similarity_threshold': st.session_state['similarity_threshold']
    }

    # Check if the prompt has a cached response with matching parameters
    cached_response, cached_sources = check_cache(prompt, current_params)
    if cached_response:
        st.write("Using cached response.")
        with st.chat_message('assistant'):
            st.markdown(cached_response)
            if cached_sources:
                with st.expander("📚 Source References"):
                    st.markdown(cached_sources)
        return

    with st.chat_message('user'):
        st.markdown(prompt)

    # Start timing and resource monitoring
    start_time = time.time()
    start_cpu = psutil.cpu_percent()
    start_memory = psutil.virtual_memory().percent

    # Generate response
    chat_engine = st.session_state['chat_engine']
    if hasattr(chat_engine, 'stream_chat'):
        response = chat_engine.stream_chat(prompt)
    else:
        response = chat_engine.generate_response(prompt)

    # Display response while accumulating it
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        res = ''
        for token in response.response_gen:
            res += token
            message_placeholder.markdown(res + '▌')
        message_placeholder.markdown(res)

        # Extract and display source information
        source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        if source_nodes:
            with st.expander("📚 Source References"):
                # Extract similarity scores if available
                similarity_scores = [node.score for node in source_nodes if hasattr(node, 'score')]
                source_text = format_source_info(source_nodes, similarity_scores if similarity_scores else None)
                st.markdown(source_text)
                
                # Display current retrieval parameters
                st.markdown("---")
                st.markdown("**Current Retrieval Parameters:**")
                st.markdown(f"- Number of documents: {current_params['num_docs']}")
                st.markdown(f"- Similarity threshold: {current_params['similarity_threshold']}")

    # Cache the new query-response pair with sources and parameters
    cache_response(prompt, res, source_text if source_nodes else None, current_params)

    # End timing and resource monitoring
    end_time = time.time()
    end_cpu = psutil.cpu_percent()
    end_memory = psutil.virtual_memory().percent
    response_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    memory_usage = end_memory - start_memory

    # Log response time and resource usage
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': res})
    st.sidebar.write(f"Response Time (RAG): {response_time:.2f} seconds")
    st.sidebar.write(f"CPU Usage (RAG): {cpu_usage:.2f}%")
    st.sidebar.write(f"Memory Usage (RAG): {memory_usage:.2f}%")