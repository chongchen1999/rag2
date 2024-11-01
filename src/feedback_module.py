#feedback_module.py

import time
from datetime import datetime
import json
import os
import streamlit as st

# Feedback storage configuration
FEEDBACK_FILE = "../data/feedback_data.json"

def load_feedback_data():
    """Load existing feedback data from file."""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_feedback_data(feedback_data):
    """Save feedback data to file."""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=4)

def collect_user_feedback(response_id):
    """Collect and store user feedback on response quality."""
    feedback_data = load_feedback_data()
    
    st.markdown("### How was this response?")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        rating = st.slider("Rate the response quality (1-5)", 1, 5, 3)
        feedback_text = st.text_area("Additional feedback (optional)")
        
        if st.button("Submit Feedback"):
            timestamp = datetime.now().isoformat()
            feedback_data[response_id] = {
                "rating": rating,
                "feedback": feedback_text,
                "timestamp": timestamp,
                "retrieval_params": {
                    "num_docs": st.session_state.get('num_docs', None),
                    "similarity_threshold": st.session_state.get('similarity_threshold', None)
                }
            }
            save_feedback_data(feedback_data)
            
            # Display a temporary success message
            st.session_state['show_success'] = True
            st.experimental_rerun()
    
    if 'show_success' in st.session_state and st.session_state['show_success']:
        st.success("Thank you for your feedback!")
        time.sleep(3)
        st.session_state['show_success'] = False
        st.experimental_rerun()
