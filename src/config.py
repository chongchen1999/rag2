# config.py
import os

# Environment configuration
os.environ['OLLAMA_NUM_PARALLEL'] = '2'
os.environ['OLLAMA_MAX_LOADED_MODELS'] = '2'

# Default configurations for the language model
DEFAULT_MAX_LENGTH = 1024
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOKEN_LIMIT = 4000
DEFAULT_SYSTEM_PROMPT = "You are a chatbot, able to have normal interactions."
EMBEDDING_MODEL = "nomic-embed-text"

# Model configurations
LLM_MODELS = {
    "Llama 3": {"model_name": "llama3", "timeout": 360.0},
    "Gemini 2": {"model_name": "gemma2", "timeout": 400.0}
}

selected_model = "Llama 3"
LLM_MODEL = LLM_MODELS[selected_model]["model_name"]
LLM_TIMEOUT = LLM_MODELS[selected_model]["timeout"]

# Retrieval configurations
DEFAULT_NUM_DOCS = 3  # Default number of documents to retrieve
DEFAULT_SIMILARITY_THRESHOLD = 0.65  # Default similarity threshold

# Supported file types
SUPPORTED_FILE_TYPES = ["txt", "pdf", "docx"]
