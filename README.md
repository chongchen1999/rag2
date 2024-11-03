# Enhanced RAG Chatbot System

An advanced chatbot system implementing Retrieval-Augmented Generation (RAG) with flexible model switching, domain-specific knowledge integration, and improved conversation capabilities.

## Features

### Knowledge Base Enhancement
- Support for domain-specific document uploads (PDF, text)
- Dynamic knowledge base updates with hash-based change detection
- Integration with LlamaIndex and VectorStoreIndex for efficient retrieval
- Local file management and preprocessing

### Retrieval Performance Optimization
- Query response caching using deque data structure
- Configurable retrieval parameters:
  - Number of retrieved documents (1-10)
  - Similarity threshold (0-1)
- Performance monitoring and optimization

### LLM Integration
- Flexible switching between models:
  - Llama 3
  - Gemini 2
- Toggle between RAG and non-RAG modes
- Configurable system prompts
- Parallel processing optimization

### Conversation Improvements
- Session-based context maintenance
- Entity and topic memory tracking
- Multi-turn conversation support
- Dynamic context refreshing
- Reference to previous interactions

### Enhanced User Interface
- Dynamic mode switching controls
- Document upload interface
- Retrieval parameter adjustment controls
- Progress indicators for:
  - Document retrieval
  - Response generation
  - Source reference processing
- Source reference display with similarity scores
- User feedback collection system

## Performance Analysis

### Chat history
  - Base Model: data/answers/llama3 only
  - RAG System: data/answers/rag

### Base Model vs. RAG System Comparison
- **Response Time:**
  - Base Model: ~15.32s average
  - RAG System: ~37.53s average

- **Resource Usage:**
  - CPU: Lower in RAG system (3.96% vs 6.36%)
  - Memory: Higher in RAG system (40.84% vs ~0%)

### Key Trade-offs
- Speed vs. Accuracy
- Resource utilization differences
- Response quality and specificity

## Installation

```bash
# Clone the repository
git clone git@github.com:chongchen1999/rag2.git

# Install required packages
pip install -r requirements.txt
```

## Usage

### Basic Setup
```python
# Start Streamlit interface
streamlit run app.py
```

### Configuration Options
```python
# Configure retrieval parameters
config = {
    'RAG_MODE': True,
    'MODEL_SELECTION': 'llama3',
    'NUM_DOCUMENTS': 3,
    'SIMILARITY_THRESHOLD': 0.65
}
```

## Environment Variables
```
OLLAMA_NUM_PARALLEL=2
OLLAMA_MAX_LOADED_MODELS=2
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Improvements
- Response time optimization for RAG system
- Enhanced NLU capabilities
- Expanded model integration options
- Improved feedback analysis system
- Domain-specific model fine-tuning

## Video Link
https://www.youtube.com/watch?v=Hox7VcMog6o