import streamlit as st
import time
import psutil
import GPUtil
import threading
def display_response_metrics(response_time, cpu_usage, memory_usage, gpu_usage=None):
    """Display response metrics in an organized way."""
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
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
    
    # Check if GPU usage is provided and display it
    if gpu_usage is not None:
        with metrics_col4:
            st.metric(
                label="GPU Usage",
                value=f"{gpu_usage:.1f}%",
                delta=f"{gpu_usage - st.session_state.get('last_gpu_usage', gpu_usage):.1f}%"
                if 'last_gpu_usage' in st.session_state else None
            )
    
    # Update last values
    st.session_state['last_response_time'] = response_time
    st.session_state['last_cpu_usage'] = cpu_usage
    st.session_state['last_memory_usage'] = memory_usage
    if gpu_usage is not None:
        st.session_state['last_gpu_usage'] = gpu_usage

class ResourceMonitor:
    def __init__(self):
        # Initialize placeholders for Streamlit display
        self.response_time_placeholder = st.empty()
        self.cpu_usage_placeholder = st.empty()
        self.memory_usage_placeholder = st.empty()
        self.gpu_usage_placeholder = st.empty()
        self.start_time = None
        self._running = False

    def start_monitoring(self):
        # Start timing
        self.start_time = time.time()
        # Start CPU, Memory, and GPU usage sampling in a separate thread
        self.cpu_usage, self.memory_usage, self.gpu_usage = [], [], []
        self._running = True
        threading.Thread(target=self._monitor, daemon=True).start()

    def _monitor(self):
        # Continuously sample system metrics in the background
        while self._running:
            # Capture CPU, Memory, and GPU usage at intervals
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            gpus = GPUtil.getGPUs()
            gpu = gpus[0].load * 100 if gpus else None

            # Store values for later average calculation
            self.cpu_usage.append(cpu)
            self.memory_usage.append(memory)
            if gpu is not None:
                self.gpu_usage.append(gpu)

            # Display metrics in Streamlit
            self.display_metrics(cpu, memory, gpu)
            time.sleep(0.5)  # Adjust interval as needed

    def display_metrics(self, cpu, memory, gpu):
        # Display live metrics in Streamlit placeholders
        elapsed_time = time.time() - self.start_time
        self.response_time_placeholder.metric("Response Time", f"{elapsed_time:.2f}s")
        self.cpu_usage_placeholder.metric("CPU Usage", f"{cpu:.1f}%")
        self.memory_usage_placeholder.metric("Memory Usage", f"{memory:.1f}%")
        if gpu is not None:
            self.gpu_usage_placeholder.metric("GPU Usage", f"{gpu:.1f}%")

    def stop_monitoring(self):
        # Stop monitoring
        self._running = False
        # Calculate averages
        self.response_time = time.time() - self.start_time
        self.avg_cpu_usage = sum(self.cpu_usage) / len(self.cpu_usage)
        self.avg_memory_usage = sum(self.memory_usage) / len(self.memory_usage)
        self.avg_gpu_usage = sum(self.gpu_usage) / len(self.gpu_usage) if self.gpu_usage else None
        
        # Display averages
        display_response_metrics(self.response_time, self.avg_cpu_usage, self.avg_memory_usage, self.avg_gpu_usage)
