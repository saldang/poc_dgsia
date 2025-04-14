from fastapi import APIRouter
from app.vector_db import list_collections, create_or_get_collection, delete_collection

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/")
def get_all_collections():
    return {"collections": [col for col in list_collections()]}


@router.post("/{name}")
def create_collection(name: str):
    create_or_get_collection(name)
    return {"message": f"Collection '{name}' pronta."}


@router.delete("/{name}")
def remove_collection(name: str):
    delete_collection(name)
    return {"message": f"Collection '{name}' eliminata."}
