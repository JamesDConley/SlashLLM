# Upload a file page
# Give it a name
# Backend will also have a UUID for it because of possible duplicate names
# Second page for select indexes to put it in

import streamlit as st
import os
import uuid
from unstructured.partition.auto import partition
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings

st.set_page_config(page_title="/Upload", page_icon="📓")

SUPPORTED_FILE_TYPES = [
    ".csv", 
    ".eml", ".msg", 
    ".epub", 
    ".xlsx", ".xls", 
    ".html", ".htm", 
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".heic",  
    ".md", 
    ".org", 
    ".odt", 
    ".pdf", 
    ".txt", ".text", ".log", 
    ".ppt", ".pptx", 
    ".rst", 
    ".rtf", 
    ".tsv", 
    ".doc", ".docx", 
    ".xml", 
    ".js", ".py", ".java", ".cpp", ".cc", ".cxx", ".c", ".cs", ".php", ".rb", ".swift", ".ts", ".go"
]


chroma_client = chromadb.HttpClient(host="chromadb", port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))

# Create an embedding function
ef = embedding_functions.SentenceTransformerEmbeddingFunction()

def upload_page(file_dir="/files"):
    st.title('File Upload Example')

    # Create a file uploader widget
    uploaded_file = st.file_uploader("Choose a file", type=SUPPORTED_FILE_TYPES)

    if uploaded_file is not None:
        # Save the uploaded file to the specified directory
        file_path = os.path.join(file_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File saved to {file_path}")

        # Generate a UUID for the file
        file_uuid = str(uuid.uuid4())

        # TODO : Post process the file
        # 1. Use unstructured to get the full text of the file
        elements = partition(file_path)

        # 2. Get a few sentence summary of the full file
        # For simplicity, we'll just take the first few elements as summary
        summary = " ".join([e.text for e in elements[:2]])

        # 3. Add the summary to the file level ChromaDB collection along with a random UUID for that file
        file_collection = chroma_client.get_or_create_collection(name="files", embedding_function=ef)
        file_collection.add(
            documents=[summary],
            ids=[file_uuid],
            metadatas=[{"filename": uploaded_file.name}]
        )

        # 4. Chunk the text and add it to a ChromaDB collection just for that file. The collection name should be the UUID
        text_collection = chroma_client.get_or_create_collection(name=file_uuid, embedding_function=ef)
        text_collection.add(
            documents=[e.text for e in elements],
            ids=[str(uuid.uuid4()) for _ in elements],
            metadatas=[{"page": i} for i, _ in enumerate(elements)]
        )
        st.success(f"Finished Indexing!")

if __name__ == '__main__':
    upload_page()