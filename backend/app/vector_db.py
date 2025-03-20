import os
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "local-rag")
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL", "nomic-embed-text")

persistent_client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(allow_reset=True))
collection = persistent_client.get_or_create_collection(COLLECTION_NAME)
embeddings = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)

vector_store = Chroma(
    client=persistent_client,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)
