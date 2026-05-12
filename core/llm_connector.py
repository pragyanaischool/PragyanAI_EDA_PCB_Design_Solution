import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables from .env file
load_dotenv()

class LLMConnector:
    """
    Centralized connector for LLMs and Embedding models.
    Supports Groq for fast reasoning and HuggingFace for local RAG.
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("CRITICAL: GROQ_API_KEY not found in environment variables.")

    def get_agent_llm(self, temperature: float = 0.0, model_name: str = "llama-3.3-70b-versatile"):
        """
        Returns a ChatGroq instance for agent reasoning.
        Llama-3.3-70b is recommended for complex hardware logic and SKiDL generation.
        """
        return ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=model_name,
            temperature=temperature,
            max_retries=3
        )

    def get_embedding_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Returns a local HuggingFace embedding model for the RAG pipeline.
        This model runs locally on your CPU/GPU, ensuring datasheet data remains private.
        """
        # Set device to 'cuda' if GPU is available, else 'cpu'
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

    def get_fast_llm(self):
        """
        Returns a smaller, faster model (Llama-3-8b) for simple tasks 
        like summarization or JSON formatting.
        """
        return ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name="openai/gpt-oss-120b",
            temperature=0.1
        )

# Global helper instances for easy importing
connector = LLMConnector()

def get_main_llm():
    return connector.get_agent_llm()

def get_embeddings():
    return connector.get_embedding_model()
  
