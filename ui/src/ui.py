import streamlit as st
import requests
from config import API_URL
from copy import deepcopy
from uuid import uuid4


def display_messages(messages) -> None: 
    """
    Display the conversation history.

    This function displays the conversation history by iterating over the messages in the current conversation.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_user_input(default_question) -> str:
    """
    Get user input from the chat input field.

    Returns:
        str: The user input, or None if no input is provided.
    """
    prompt = st.chat_input(default_question)
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        return prompt
    return None


def conversation_sidebar(client, conversations, user_id, current_doc):
    # Add a sidebar to switch between conversations
    return_val = current_doc
    with st.sidebar:
        st.header("Conversations")
        # Add a button to create a new conversation
        if st.button("New Conversation", key="new_conversation"):
            new_id = str(uuid4())
            # Create new conversation via API
            conversation_doc = client.get_or_create_conversation(user_id, new_id)
            return_val = conversation_doc

        for i, conversation_id in enumerate(conversations):
            # Get conversation title from API
            conversation_doc = client.get_or_create_conversation(user_id, conversation_id)
            
            if len(conversation_doc["messages"]) == 1:
                conversation_title = "EMPTY"
            else:
                conversation_title = conversation_doc["messages"][1]["content"][0:30]
                if len(conversation_doc["messages"][1]["content"]) > 20:
                    conversation_title += "..."
            # Highlight the current button by changing it's style
            if conversation_doc["_id"] == current_doc["_id"]:
                conversation_title = f"***{conversation_title}***"
            # Conversation selection button and delete button
            col1, col2 = st.columns((4, 1))
            with col1:
                if st.button(f"{conversation_title}", key=f"select_conversation_{i}"):
                    return_val = conversation_doc
            with col2:
                if st.button("❌", key=f"delete_conversation_{i}"):
                    client.delete_conversation(user_id, conversation_id)
                    if conversation_doc["_id"] == current_doc["_id"]:
                        if len(conversations) > 1:
                            return_val = client.get_or_create_conversation(user_id, conversations[0])
                        else:
                            return_val = client.get_or_create_conversation(user_id, str(uuid4()))
                    else:
                        st.rerun()

    return return_val