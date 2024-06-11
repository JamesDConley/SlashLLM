import logging
import os
from openai import OpenAI
import requests
from config import TOOL_MAPPINGS, OPENAI_API_KEY, OPENAI_API_BASE, MODEL_NAME
import traceback

from flask import jsonify

logger = logging.getLogger(__name__)

def call_model(messages, temperature=0.5):
    client = OpenAI(
        api_key = OPENAI_API_KEY,
        base_url = OPENAI_API_BASE,
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        temperature=temperature
    )
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


def call_tool(api_name, message, message_history):
    json_data = {"query" : message, "message_history" : message_history}
    url = TOOL_MAPPINGS[api_name]["url"]
    try:
        response = requests.post(url, json=json_data, stream=True)
        for chunk in response.iter_content(16):
            chunk = chunk.decode("utf-8")
            # Get the returned dictionary from the response
            logger.info(f"Yielding chunk : {chunk}")
            yield chunk
    except Exception as e:
        print(traceback.format_exc())
        yield "Error reaching endpoint"


def run_query(message_history, user_request, message_db):
    # Adds user request to the messages
    # But doesn't save it to the database yet
    message_history["messages"].append({"role" : "user", "content" : user_request})

    if user_request[0] == "/":
        role = "system"
        yield role + ":"
        # The slash command (without slash)
        command = user_request[1:].split(" ")[0]
        # Text following the slash command
        text = user_request[2+len(command):]
        
        if command in TOOL_MAPPINGS.keys():
            full_response = ""
            response = call_tool(command, text, message_history["messages"])
            for item in response:
                yield item
                full_response += item
            message_history["messages"].append( {"role" : "system", "content" : full_response})

        else:
            message = {"role" : "system", "content" : f"Unknown Command `{command}`"}
            yield message["content"]
            message_history["messages"].append(message)
    
    # Standard Agent Processing
    else:
        role = "assistant"
        yield role + ":"
        i = 0
        message = {"role" : role, "content" : ""}
        for chunk in call_model(message_history["messages"]):
            message["content"] += chunk
            yield chunk
        message_history["messages"].append(message)
    # Once Processing is completed, update the message history with the request and response
    message_db.save(message_history)
    