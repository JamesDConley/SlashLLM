# document_searcher_tool.py
# Searching inside a document

import json

import chromadb
from pydantic import BaseModel, constr
from guided_agent.tool import Tool
from chromadb.config import Settings
from typing import List, Dict

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
                logger.debug(f"Got invalid collection uuid : {uuid}")
                continue
            collection = self.chroma_client.get_or_create_collection(name=uuid)
            results = collection.query(
                query_texts=[query],
                n_results=10
            )
            relevant_sections.extend([
                {"file_uuid": uuid, "page": metadata["page"], "text": text}
                for text, metadata in zip(results['documents'][0], results['metadatas'][0])
            ])
        yield "result", f"Relevant Sections: {json.dumps(relevant_sections, indent=4)}"

    def name(self):
        return "document_searcher"

    def description(self):
        return "Search for relevant sections in specified documents based on a query. This method returns the sections that are identified as a match for the query based on cosine similarity scores between the query and the internal documents."

    def get_input_json_schema(self):
        return DocumentSearcherInput.model_json_schema()