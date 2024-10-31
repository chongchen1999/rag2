#rag_module.py
import streamlit as st
from utils import handle_file_upload, get_files_hash
import time
import psutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from config import *

def init_models_rag(temp_dir, generation_config):
    """Initialize RAG models with LlamaIndex."""
    embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL)
    Settings.embed_model = embed_model

    llm = Ollama(
        model=LLM_MODEL,
        request_timeout=LLM_TIMEOUT,
        num_ctx=generation_config['num_ctx'],
        temperature=generation_config['temperature']
    )
    Settings.llm = llm

    documents = SimpleDirectoryReader(st.session_state['temp_dir']).load_data()
    index = VectorStoreIndex.from_documents(documents)

    memory = ChatMemoryBuffer.from_defaults(token_limit=DEFAULT_TOKEN_LIMIT)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
    )

    return chat_engine

def handle_rag_mode(uploaded_files, generation_config):
    current_files_hash = get_files_hash(uploaded_files) if uploaded_files else None

    if 'files_hash' in st.session_state:
        if st.session_state['files_hash'] != current_files_hash:
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
    else:
        if uploaded_files:
            st.session_state['files_hash'] = current_files_hash
            st.session_state['temp_dir'] = handle_file_upload(uploaded_files)
            st.sidebar.success("Files uploaded successfully.")
            if 'chat_engine' not in st.session_state:
                st.session_state['chat_engine'] = init_models_rag(uploaded_files, generation_config)
        else:
            st.sidebar.error("No uploaded files.")

def generate_rag_response(prompt):
    if 'chat_engine' not in st.session_state:
        st.error("Please upload files first or switch to non-RAG mode.")
        st.stop()

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

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        res = ''
        for token in response.response_gen:
            res += token
            message_placeholder.markdown(res + '▌')
        message_placeholder.markdown(res)

    # End timing and resource monitoring
    end_time = time.time()
    end_cpu = psutil.cpu_percent()
    end_memory = psutil.virtual_memory().percent
    response_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    memory_usage = end_memory - start_memory

    # Log response time and resource usage
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': response})
    st.sidebar.write(f"Response Time (RAG): {response_time:.2f} seconds")
    st.sidebar.write(f"CPU Usage (RAG): {cpu_usage:.2f}%")
    st.sidebar.write(f"Memory Usage (RAG): {memory_usage:.2f}%")