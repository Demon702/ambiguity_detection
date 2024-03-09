import streamlit as st
from get_chatbot_response import get_chatbot_response

def generate_response(user_input):
    # Placeholder function to generate a response
    # Replace or extend this logic to integrate with your own models or logic
    return get_chatbot_response(st.session_state.user_messages, st.session_state.chatbot_messages, user_input)

# Streamlit app layout setup
st.title('Simple Chatbot for Ambiguity Detection')

# Initialize session state for storing conversation if it doesn't exist
if 'user_messages' not in st.session_state:
    st.session_state.user_messages = []

if 'chatbot_messages' not in st.session_state:
    st.session_state.chatbot_messages = []

# Function to add user input to the conversation
def handle_user_input():
    user_input = st.session_state.user_input  # Get current input
    if user_input:  # If there's something typed in
        response = generate_response(user_input)  # Generate bot's response
        st.session_state.user_messages.append(user_input)  # Add user input to conversation
        st.session_state.chatbot_messages.append(response)  # Add bot response to conversation
        st.session_state.user_input = ""  # Clear input box

# Display conversation history
for idx, (user_message, chatbot_message) in enumerate(zip(st.session_state.user_messages, st.session_state.chatbot_messages)):
    st.text_area(f"User: ", value=user_message, height=75, key=f"user_{idx}")
    st.text_area(f"Chatbot: ", value=chatbot_message, height=75, key=f"chatbot_{idx}")

# User input text box
user_input = st.text_input("Say something to the chatbot", key="user_input", on_change=handle_user_input)

# The handle_user_input function will be called when the user types something in the input box.
# Due to Streamlit's rerun behavior, there's no need to manually rerun the script to refresh the UI.
