# app.py
import streamlit as st
from uuid import uuid4

import json

from config import API_URL
from user_state import get_user_id
from ui import display_messages, get_user_input, conversation_sidebar
from api_utils import Client


def main(debug) -> None:
    user_id = get_user_id()

    # Setup session information
    client = Client(API_URL)

    # Get user data from API -- Need to create user here if they don't already exist
    user_doc = client.get_or_create_user_data(user_id)
    current_conversation_id = st.session_state.get("current_conversation_id", str(uuid4()))
    conversation_doc = client.get_or_create_conversation(user_id, current_conversation_id)
    # If we created a new conversation we need to update the user_doc
    user_doc = client.get_or_create_user_data(user_id)
    conversations = user_doc.get("conversations", [])

    # This saves it in case we needed to make a new one
    st.session_state["current_conversation_id"] = current_conversation_id
    
    if debug:
        st.markdown("# Running in Debug Mode")
        st.markdown(f"### Current User Data")
        st.markdown(f"```json\n{json.dumps(user_doc, indent=4)}\n")
        st.markdown("### Current Conversation Data")
        st.markdown(f"```json\n{json.dumps(conversation_doc, indent=4)}\n")
    
    # Set Title
    st.title("Local LLM")

    new_conversation_doc = conversation_sidebar(client, conversations, user_id, conversation_doc)
    if current_conversation_id != new_conversation_doc["_id"]:
        st.session_state["current_conversation_id"] = new_conversation_doc["_id"]
        st.rerun()

    messages = conversation_doc["messages"]

    display_messages(messages)
    # TODO : Work back in the prompt idea tool
    prompt = get_user_input("")
    if prompt:
        # Send query to API
        role = None
        response_iter = client.query_system(current_conversation_id, prompt)
        role = next(response_iter)
        with st.chat_message(role):
            st.write_stream(response_iter)
        st.rerun()

if __name__ == "__main__":
    main(debug=False)