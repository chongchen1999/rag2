import streamlit as st
def display_response_metrics(response_time, cpu_usage, memory_usage):
    """Display response metrics in an organized way."""
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            label="Response Time",
            value=f"{response_time:.2f}s",
            delta=f"{response_time - st.session_state.get('last_response_time', response_time):.2f}s"
            if 'last_response_time' in st.session_state else None
        )
    
    with metrics_col2:
        st.metric(
            label="CPU Usage",
            value=f"{cpu_usage:.1f}%",
            delta=f"{cpu_usage - st.session_state.get('last_cpu_usage', cpu_usage):.1f}%"
            if 'last_cpu_usage' in st.session_state else None
        )
    
    with metrics_col3:
        st.metric(
            label="Memory Usage",
            value=f"{memory_usage:.1f}%",
            delta=f"{memory_usage - st.session_state.get('last_memory_usage', memory_usage):.1f}%"
            if 'last_memory_usage' in st.session_state else None
        )
    
    # Update last values
    st.session_state['last_response_time'] = response_time
    st.session_state['last_cpu_usage'] = cpu_usage
    st.session_state['last_memory_usage'] = memory_usage