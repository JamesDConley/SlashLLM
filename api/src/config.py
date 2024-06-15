import os
# OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
# MODEL_NAME = os.environ["MODEL_NAME"]

OPENAI_API_KEY="EMPTY"
OPENAI_API_BASE="http://192.168.1.33:8183/v1"
MODEL_NAME="/models/Qwen2-72B-Instruct-AWQ"

TOOL_MAPPINGS = {
    "search": {"url": "http://tool-api:8101/search"},
    "doc_search":  {"url": "http://tool-api:8101/doc_search"},
}

SYSTEM_PROMPT = "You are a virtual assistant created by the open source community. You have access to a chat log that involves a user who can also access a few other tools. Respond using markdown. Prefer aligning lists and such to the left of the page (not centered)."

COUCHDB_CONNECTION_URL = "http://admin:password@couchdb:5984/"
COUCHDB_STATE_DATABASE = "state"
COUCHDB_USER_DATABASE = "users"
COUCHDB_CONVERSATIONS_DATABASE = "conversations"