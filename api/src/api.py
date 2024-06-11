import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from pycouchdb import Server

# Local Imports
from constants import DEFAULT_TEMPERATURE, DEFAULT_SYSTEM_PROMPT
from api_message_handler import run_query
from config import COUCHDB_CONNECTION_URL, COUCHDB_USER_DATABASE, COUCHDB_CONVERSATIONS_DATABASE


def get_or_create_database(server, db_name):
    try:
        return server.database(db_name)
    except:
        return server.create(db_name)

app = Flask(__name__)
CORS(app)

# CouchDB connection
server = Server(COUCHDB_CONNECTION_URL)
db_users = get_or_create_database(server, COUCHDB_USER_DATABASE)
db_conversations = get_or_create_database(server, COUCHDB_CONVERSATIONS_DATABASE)

@app.route('/user_data', methods=['GET'])
def get_or_create_user_data():
    user_id = request.args.get('user_id')
    if not user_id:
        return "Please pass a `user_id`", 400
    
    if user_id in db_users:
        user_doc = db_users.get(user_id)
        return jsonify(user_doc)

    else:
        # Create new user document
        user_doc = {'_id': user_id, 'conversations': [], "user_temperature" : DEFAULT_TEMPERATURE, "user_system_prompt" : DEFAULT_SYSTEM_PROMPT}
        db_users.save(user_doc)
        return jsonify(user_doc)

@app.route('/conversation', methods=['GET'])
def get_conversation():
    user_id = request.args.get('user_id', None)
    conversation_id = request.args.get('conversation_id', None)
    # Check requirements for inputs
    if not conversation_id:
        return "Please pass a `conversation_id`", 400

    if not user_id:
        return "Please pass a `user_id`", 400

    if user_id not in db_users:
        return "Please pass a valid `user_id`", 400
    
    user_data = db_users.get(user_id)

    if  conversation_id in db_conversations:
        conversation_doc = db_conversations.get(conversation_id)
        # Safeguard to avoid people editing other user's conversations
        # Note that this isn't really security, it's just a debug helper.
        if conversation_doc["user_id"] != user_id:
            return "Passed user ID does not match stored ID for the given conversation!", 400
        return jsonify(dict(conversation_doc))
    else:
        # Create new conversation document
        conversation_doc = {'_id': conversation_id, 'user_id' : user_id, 'messages': [{"role" : "system", "content" : user_data["user_system_prompt"]}]}
        db_conversations.save(conversation_doc)
        user_data["conversations"].append(conversation_id)
        db_users.save(user_data)
        return jsonify(dict(conversation_doc))

@app.route('/query', methods=['POST'])
def query_system():
    conversation_id = request.args.get('conversation_id', None)
    data = request.get_json()
    query = data.get('query', None)
    if not conversation_id:
        return "Please pass a `conversation_id`", 400
    if conversation_id not in db_conversations:
        return "Please pass a valid `conversation_id`", 400

    if not query:
        return "Please pass a valid `query`", 400
    
    conversation_doc = db_conversations.get(conversation_id)
    stream = run_query(conversation_doc, query, db_conversations)
    return app.response_class(stream, mimetype="text/plain")


@app.route('/delete_conversation', methods=['DELETE'])
def delete_conversation():
    user_id = request.args.get('user_id', None)
    conversation_id = request.args.get('conversation_id', None)

    if not user_id:
        return "Please pass a `user_id`", 400

    if not conversation_id:
        return "Please pass a `conversation_id`", 400

    if user_id not in db_users:
        return "Please pass a valid `user_id`", 400

    if conversation_id not in db_conversations:
        return "Please pass a `conversation_id`", 400

    user_data = db_users.get(user_id)

    if conversation_id in user_data["conversations"]:
        db_conversations.delete(conversation_id)
        user_data["conversations"].remove(conversation_id)
        db_users.save(user_data)
        return jsonify({"message": "Conversation deleted successfully"})
    else:
        return "User does not have permission to delete this conversation", 403

if __name__ == '__main__':
    logging.basicConfig(filename="/logs/api.log", level=logging.INFO, format='%(asctime)s %(message)s')
    app.run(host="0.0.0.0")