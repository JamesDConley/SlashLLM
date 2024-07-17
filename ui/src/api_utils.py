import logging
import requests

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, api_base):
        self.api_base = api_base

    def get_or_create_conversation(self, user_id, conversation_id):
        response = requests.get(f"{self.api_base}/conversation", params={"user_id": user_id, "conversation_id" : conversation_id})
        assert response.status_code == 200, "Backend API Error -- get_conversation"
        return response.json()

    def get_or_create_user_data(self, user_id):
        response = requests.get(f"{self.api_base}/user_data", params={"user_id": user_id})
        return response.json()

    def query_system(self, conversation_id, query):
        response = requests.post(f"{self.api_base}/query", params={"conversation_id": conversation_id}, json={"query": query}, stream=True, timeout=None)
        buffer = ""
        role = None
        for chunk in safe_response_iter(response):
            if role is None:
                buffer += chunk
                if ":" in buffer:
                    split_buffer = buffer.split(":")
                    role = split_buffer[0]
                    yield role
                    if len(split_buffer) > 1:
                        buffer = ":".join(split_buffer[1:])
                        yield buffer
                    else:
                        buffer = ""  
            else:
                yield chunk
    
    def delete_conversation(self, user_id, conversation_id):
        response = requests.delete(f"{self.api_base}/delete_conversation", params={"user_id": user_id, "conversation_id": conversation_id})
        assert response.status_code == 200, "Backend API Error -- delete_conversation"
        return response.json()


def safe_response_iter(response, size=128):
    buffer = None
    for chunk in response.iter_content(size):
        if buffer is not None:
            chunk = buffer + chunk
        try:
            result = chunk.decode("utf-8")
            yield result
            buffer = None
        except UnicodeDecodeError:
            logger.info(f"Parsing error encountered!")
            buffer = chunk
    logger.info(f"Finished iterator!")
    if buffer is not None:
        yield chunk.decode("utf-8", "ignore")


