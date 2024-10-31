#non_rag_module.py
import time
import streamlit as st
import psutil
import subprocess
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from config import *

def init_models_non_rag():
    """Initialize non-RAG model using Ollama directly."""
    def run_model(prompt, context=""):
        try:
            full_prompt = context + "\n" + prompt if context else prompt
            command = ["ollama", "run", LLM_MODEL]
            process = subprocess.run(
                command,
                input=full_prompt,
                text=True,
                capture_output=True,
                check=True
            )
            return process.stdout
        except subprocess.CalledProcessError as e:
            return f"Error running Llama: {e.stderr}"
        except FileNotFoundError:
            return "Error: Ollama is not installed or not in PATH"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    return run_model

def handle_non_rag_mode():
    if ('chat_engine' not in st.session_state or 
        'current_mode' not in st.session_state or 
        st.session_state['current_mode'] != 'non-rag'):
        st.session_state['chat_engine'] = init_models_non_rag()
        st.session_state['current_mode'] = 'non-rag'

def generate_non_rag_response(prompt):
    with st.chat_message('user'):
        st.markdown(prompt)

    # Start timing and resource monitoring
    start_time = time.time()
    start_cpu = psutil.cpu_percent()
    start_memory = psutil.virtual_memory().percent

    # Fetch context for multi-turn conversation
    context = "\n".join([msg['content'] for msg in st.session_state.messages if msg['role'] == 'assistant'])

    # Generate response
    response = st.session_state['chat_engine'](prompt, context)

    # End timing and resource monitoring
    end_time = time.time()
    end_cpu = psutil.cpu_percent()
    end_memory = psutil.virtual_memory().percent
    response_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    memory_usage = end_memory - start_memory

    with st.chat_message('assistant'):
        st.markdown(response)

    # Log response time and resource usage
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': response})
    st.sidebar.write(f"Response Time (Non-RAG): {response_time:.2f} seconds")
    st.sidebar.write(f"CPU Usage (Non-RAG): {cpu_usage:.2f}%")
    st.sidebar.write(f"Memory Usage (Non-RAG): {memory_usage:.2f}%")
