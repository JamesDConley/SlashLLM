# document_finder_tool.py

import json

from pydantic import BaseModel, constr
from guided_agent.tool import Tool
import chromadb
from chromadb.config import Settings
from typing import List, Dict

# Define the input schema for the tool
class DocumentFinderInput(BaseModel):
    query: constr(max_length=250)

class DocumentFinderTool(Tool):
    def __init__(self, chroma_host="chromadb", chroma_port=8000, chroma_collection="files"):
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port, settings=Settings(allow_reset=True, anonymized_telemetry=False))
        self.files_collection = self.chroma_client.get_or_create_collection(name=chroma_collection)
        self.chroma_collection = chroma_collection

    def run(self, tool_input: str) -> str:
        parsed_input = DocumentFinderInput(query=tool_input)
        query = parsed_input.query

        # Query the ChromaDB collection for relevant documents
        results = self.files_collection.query(
            query_texts=[query],
            n_results=5
        )
        relevant_files = [{"uuid": file_id, "filename": metadata["filename"]} for file_id, metadata in zip(results['ids'][0], results['metadatas'][0])]
        yield "result", f"Relevant Files: {json.dumps(relevant_files, indent=4)}"

    def name(self):
        return "document_finder"

    def description(self):
        return f"Find relevant documents based on a query from the indexed files in the chromadb collection `{self.chroma_collection}`. Gives the top 5 documents for the given query."

    def get_input_json_schema(self):
        return DocumentFinderInput.model_json_schema()