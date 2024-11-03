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
    """Collect and store user feedback on response quality using star rating."""
    feedback_data = load_feedback_data()

    st.markdown("### How was this response?")

    # Initialize session state variables if they don't exist
    if 'rating' not in st.session_state:
        st.session_state.rating = 0
    if 'show_additional_feedback' not in st.session_state:
        st.session_state.show_additional_feedback = False
    if 'feedback_text' not in st.session_state:
        st.session_state.feedback_text = ""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Create star rating using radio buttons instead of individual buttons
        st.session_state.rating = st.radio(
            "Rate this response:",
            options=[0, 1, 2, 3, 4, 5],
            index=st.session_state.rating,
            format_func=lambda x: "☆" * (5 - x) + "⭐" * x,
            key="star_rating"
        )

        # Button to toggle additional feedback
        if st.button("Add detailed feedback" if not st.session_state.show_additional_feedback else "Hide detailed feedback"):
            st.session_state.show_additional_feedback = not st.session_state.show_additional_feedback

        # Show text area if button is clicked
        if st.session_state.show_additional_feedback:
            st.session_state.feedback_text = st.text_area(
                "Additional feedback",
                value=st.session_state.feedback_text,
                key="feedback_input"
            )

        # Submit button
        if st.button("Submit Feedback"):
            if st.session_state.rating > 0:  # Ensure rating is provided
                timestamp = datetime.now().isoformat()
                feedback_data[response_id] = {
                    "rating": st.session_state.rating,
                    "feedback": st.session_state.feedback_text,
                    "timestamp": timestamp,
                    "retrieval_params": {
                        "num_docs": st.session_state.get('num_docs', None),
                        "similarity_threshold": st.session_state.get('similarity_threshold', None)
                    }
                }
                save_feedback_data(feedback_data)

                # Reset state and show success message
                st.session_state.rating = 0
                st.session_state.feedback_text = ""
                st.session_state.show_additional_feedback = False
                st.session_state['show_success'] = True
                st.experimental_rerun()
            else:
                st.warning("Please provide a rating before submitting.")

        # Show success message if feedback was submitted
        if 'show_success' in st.session_state and st.session_state['show_success']:
            st.success("Thank you for your feedback!")
            time.sleep(2)
            st.session_state['show_success'] = False
            st.experimental_rerun()
