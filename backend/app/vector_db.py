import os
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "local-rag")
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL", "phi4")
COLLECTIONS = {}  # cache per Chroma vectorstore attivi

_chroma_client = chromadb.Client(
    Settings(
        persist_directory="./chroma",  # deve essere sempre lo stesso path
        is_persistent=True,
    )
)
embeddings = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)


def list_collections():
    return _chroma_client.list_collections()


def create_or_get_collection(collection_name: str):
    try:
        collection = _chroma_client.get_collection(name=collection_name)
        print(f"✔️ Collection '{collection_name}' già esistente.")
    except Exception:
        collection = _chroma_client.create_collection(name=collection_name)
        print(f"✅ Nuova collection '{collection_name}' creata.")
    return collection


def delete_collection(collection_name: str):
    try:
        _chroma_client.delete_collection(name=collection_name)
        print(f"🗑️ Collection '{collection_name}' eliminata.")
    except Exception as e:
        print(f"❌ Errore nell'eliminare '{collection_name}': {e}")


def get_vector_store(collection_name: str):
    if collection_name in COLLECTIONS:
        return COLLECTIONS[collection_name]

    try:
        collection = _chroma_client.get_collection(collection_name)
    except:
        collection = _chroma_client.create_collection(collection_name)

    vectorstore = Chroma(
        client=_chroma_client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    COLLECTIONS[collection_name] = vectorstore
    return vectorstore
