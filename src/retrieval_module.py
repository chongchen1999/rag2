import streamlit as st
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