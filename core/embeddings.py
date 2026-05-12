import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration for paths
RAW_DATA_PATH = "data/raw_datasheets/"
VECTOR_DB_PATH = "data/vector_store/"
COLLECTION_NAME = "pcb_knowledge_base"

class EmbeddingsManager:
    """
    Manages the lifecycle of the Vector Database.
    Handles loading PDFs, chunking text, and persisting embeddings.
    """
    
    def __init__(self):
        # Initialize the local embedding model (runs on CPU/GPU)
        # all-MiniLM-L6-v2 is fast and efficient for technical text
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

    def ingest_datasheets(self):
        """
        Processes all PDF files in the raw_datasheets directory and
        updates the vector database.
        """
        if not os.listdir(RAW_DATA_PATH):
            print(f"⚠️ No PDF files found in {RAW_DATA_PATH}. Skipping ingestion.")
            return

        print(f"📂 Loading documents from {RAW_DATA_PATH}...")
        loader = DirectoryLoader(
            RAW_DATA_PATH, 
            glob="./*.pdf", 
            loader_cls=PyPDFLoader
        )
        raw_documents = loader.load()

        # Use a technical splitter to keep tables and lists relatively intact
        # Overlap ensures that context is preserved between chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(raw_documents)
        print(f"✂️ Split {len(raw_documents)} pages into {len(chunks)} chunks.")

        # Create and persist the ChromaDB
        print(f"🧠 Generating embeddings and saving to {VECTOR_DB_PATH}...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=VECTOR_DB_PATH,
            collection_name=COLLECTION_NAME
        )
        
        print("✅ Vector database updated and persisted.")

    def get_retriever(self):
        """
        Returns a retriever object for agents to search the knowledge base.
        """
        vector_db = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME
        )
        return vector_db.as_retriever(search_kwargs={"k": 5})

# Execution logic for standalone use
if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    
    manager = EmbeddingsManager()
    manager.ingest_datasheets()
  
