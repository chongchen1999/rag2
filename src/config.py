import os

# Environment configuration
os.environ['OLLAMA_NUM_PARALLEL'] = '2'
os.environ['OLLAMA_MAX_LOADED_MODELS'] = '2'

# Default configurations for the language model
DEFAULT_MAX_LENGTH = 1024
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOKEN_LIMIT = 4000
DEFAULT_SYSTEM_PROMPT = "You are a chatbot, able to have normal interactions."

# Model configurations
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"
LLM_TIMEOUT = 360.0

# Retrieval configurations
DEFAULT_NUM_DOCS = 5  # Default number of documents to retrieve
DEFAULT_SIMILARITY_THRESHOLD = 0.75  # Default similarity threshold

# Supported file types
SUPPORTED_FILE_TYPES = ["txt", "pdf", "docx"]
