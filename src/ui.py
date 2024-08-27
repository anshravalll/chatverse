import streamlit as st
import json
import requests

def query_handler(prompt, json_history):
    # Add the user's message to the history
    json_obj = {"User": prompt}

    if json_history:
        json_history.get("History").append(json_obj)
    else:
        json_history = {"History": [json_obj]}

    return json_history

def generate_response(json_history):
    with st.spinner("Generating a response..."):
        # Make the actual API call to get the bot's response
        response = requests.post(
            url='http://127.0.0.1:8487/invoke_chat',  # Replace with your actual API endpoint
            json=json_history
        )
       
        # Extract the response from the API
        reply = response.json().get("Response", {}).get("content", "")
       
        # Add the bot's response to the last user message in the history
        json_history.get("History")[-1]["Bot"] = reply
       
        # Update the session state with the entire updated conversation
        st.session_state["conversation"] = json_history.get("History")
        
   
    return json_history

def display():
    if st.session_state["conversation"]:
        for exchange in st.session_state.conversation:
            with st.chat_message("user"):
                st.write(exchange.get("User"))
            if "Bot" in exchange:  # Check if there's a bot response to display
                with st.chat_message("assistant"):
                    st.write(exchange.get("Bot"))

# Initialize session state for conversation
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

uploaded_file = st.file_uploader("Choose a JSON file", type="json")
json_history = None


if uploaded_file is not None:
    json_history = json.load(uploaded_file)
    if not st.session_state["conversation"]:
        st.session_state["conversation"] = json_history.get("History", [])
    st.title("Chat History")
    display()
    
# Capture user input
prompt = st.chat_input("Type your message here...")


if prompt:
    # Load existing history from session state or start a new one
    json_history = {"History": st.session_state["conversation"]} if st.session_state["conversation"] else None

    # Update history with the new user message
    json_history = query_handler(prompt, json_history)
   
    # Generate and store the bot response
    json_history = generate_response(json_history)
   
    # Display the updated conversation
    display()