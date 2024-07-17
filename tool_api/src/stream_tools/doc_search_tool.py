# document_searcher_tool.py
# Searching inside a document

import json
import logging

import chromadb
from pydantic import BaseModel, constr
from guided_agent.tool import Tool
from chromadb.config import Settings
from typing import List, Dict

from llm_utils import simple_model_call

logger = logging.getLogger(__name__)

IS_RELEVANT_PROMPT = """Determine if the candidate results contains information that answers the users request partially, fully, or not at all.
You will be provided sections that are all from the same document. Your job is to determine if the provided sections answer the request or not.
Filtering out candidates that aren't useful, and floating up ones that are directly relevant.

Here's the user's request
### Start Request
{user_request}
### End Request

Here's the candidate result
### Start Result
{result}
### End Result

Respond with one of "PARTIAL", "FULL", or "IRRELEVANT"
"""

def dict_of_lists_to_list_of_dicts(dict_of_lists):
    """
    Converts a dictionary of lists into a list of dictionaries.

    Args:
        dict_of_lists (dict): A dictionary where each key maps to a list.

    Returns:
        list: A list of dictionaries, where each dictionary represents a combination of elements from the lists.
    """
    return [dict(zip(dict_of_lists, t)) for t in zip(*dict_of_lists.values())]


# Define the input schema for the tool
class DocumentSearcherInput(BaseModel):
    query: constr(max_length=250)
    file_uuids: List[str]

class DocumentSearcherTool(Tool):
    def __init__(self, chroma_host="chromadb", chroma_port=8000, chroma_collection="files"):
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port, settings=Settings(allow_reset=True, anonymized_telemetry=False))

    def run(self, tool_input: str) -> str:
        parsed_input = DocumentSearcherInput(**json.loads(tool_input))
        query = parsed_input.query
        file_uuids = parsed_input.file_uuids

        # Search for relevant sections in the specified documents
        relevant_sections = []
        all_collections = set([c.name for c in self.chroma_client.list_collections()])
        for uuid in file_uuids:
            if uuid not in all_collections:
                logger.info(f"Got invalid collection uuid : {uuid}")
                continue
            collection = self.chroma_client.get_or_create_collection(name=uuid)
            results = collection.query(
                query_texts=[query],
                n_results=100
            )
            #results = dict_of_lists_to_list_of_dicts(results)
            logger.info(f"Results : {results}")
            # TODO : order the found sections and fill in gaps in chunking
            # TODO : Use better chunking in the document uploader
            for i in range(0, len(results), 20):
                docs_slice = results["documents"][0][i:i+10]
                prompt = IS_RELEVANT_PROMPT.format(user_request=query, result=str(docs_slice))
                useful = simple_model_call(prompt, extra_body={"guided_choice" : ["FULL", "IRRELEVANT"]}).strip() == "FULL"
                if useful:
                    relevant_sections.extend([
                        {"file_uuid": uuid, "page": metadata["page"], "text": text}
                        for text, metadata in zip(results['documents'][0][i:i+10], results['metadatas'][0][i:i+10])
                    ])
        yield "result", f"Relevant Sections: {json.dumps(relevant_sections, indent=4)}"

    def name(self):
        return "document_searcher"

    def description(self):
        return "Search for relevant sections in specified documents based on a query. This method returns the sections that are identified as a match for the query based on cosine similarity scores between the query and the internal documents."

    def get_input_json_schema(self):
        return DocumentSearcherInput.model_json_schema()