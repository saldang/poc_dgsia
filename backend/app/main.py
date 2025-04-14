import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from .embed import embed
from .query import query
from .routers import collections
from .vector_db import create_or_get_collection

load_dotenv()

TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = FastAPI()
app.include_router(collections.router)


@app.post("/embed")
async def route_embed(file: UploadFile = File(...), request: Request = None):

    collection_name = request.query_params.get("collection", "default")
    print(f"Collection: {collection_name}")
    """Embeds the uploaded files into the specified collection in the database"""
    if not file:
        raise HTTPException(status_code=400, detail="No file part")

    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    embedded = embed(file, collection_name=collection_name)
    print(embedded)

    if embedded:
        return JSONResponse(
            content={"message": "File embedded successfully"}, status_code=200
        )
    raise HTTPException(status_code=400, detail="File embedded unsuccessfully")


@app.post("/query")
async def route_query(data: dict):
    print(f"Query: {data.get('query')}")
    print(f"Model: {data.get('model')}")
    print(f"Collection: {data.get('collection')}")
    response = query(data.get("query"), data.get("model"), data.get("collection"))

    if response:
        return JSONResponse(content={"message": response}, status_code=200)

    raise HTTPException(status_code=400, detail="Something went wrong")


@app.post("/list_documents")
async def list_documents(request: Request):
    """Recupera la lista dei documenti presenti in ChromaDB."""
    json = await request.json()
    collection = json.get("collection", "default")
    print(f"Collection: {collection}")
    try:
        results = create_or_get_collection(collection_name=collection).get()
        all_docs = []
        if results:
            for doc in results["metadatas"]:
                all_docs.append(doc["source"])
            return {"documents": list(set(all_docs))}
    except Exception as e:
        print("ERRORE:", str(e))
        return {"documents": []}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, debug=True)
