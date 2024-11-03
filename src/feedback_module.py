import json
import os
import streamlit as st

# Feedback storage configuration
FEEDBACK_FILE = "../data/feedback_data.json"  # Change this to an absolute path

def load_feedback_data():
    """Load feedback data from the feedback file, or initialize if it doesn't exist or is invalid."""
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r') as file:
                feedback_data = json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or invalid, initialize an empty dictionary
            feedback_data = {}
    else:
        feedback_data = {}
    
    return feedback_data

def save_feedback_data(feedback_data):
    """Save feedback data to the JSON file."""
    try:
        with open(FEEDBACK_FILE, 'w') as file:
            json.dump(feedback_data, file, indent=4)
    except Exception as e:
        st.error(f"An error occurred while saving feedback data: {e}")

def collect_user_feedback(response_id):
    """Collect user feedback for a given response ID."""
    feedback_data = load_feedback_data()
    
    # Create a Streamlit form for feedback collection
    with st.form(key=f"feedback_form_{response_id}"):
        print("here")
        st.write("Rate the quality of the answer:")
        rating = st.slider("Rating", min_value=1, max_value=5, key=f"rating_{response_id}")
        literal_feedback = st.text_area("Optional: Provide additional feedback", key=f"literal_feedback_{response_id}")
        
        if st.form_submit_button("Submit Feedback"):
            # Store the feedback in the feedback data dictionary
            feedback_data[response_id] = {
                "rating": rating,
                "literal_feedback": literal_feedback
            }

            print(feedback_data)
            save_feedback_data(feedback_data)
            print("saved feedback")
            st.success("Thank you for your feedback!")

# Usage example
response_id = "response_1"  # This would typically be generated dynamically
collect_user_feedback(response_id)
