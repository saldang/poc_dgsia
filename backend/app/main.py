import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from .embed import embed
from .query import query
from .vector_db import vector_store, persistent_client, collection

load_dotenv()

TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = FastAPI()


@app.post("/embed")
async def route_embed(file: UploadFile = File(...)):
    """Embeds the uploaded files into the database"""
    if not file:
        raise HTTPException(status_code=400, detail="No file part")

    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    embedded = embed(file)
    print(embedded)

    if embedded:
        return JSONResponse(
            content={"message": "File embedded successfully"}, status_code=200
        )
    raise HTTPException(status_code=400, detail="File embedded unsuccessfully")


@app.post("/query")
async def route_query(data: dict):
    response = query(data.get("query"), data.get("model"))

    if response:
        return JSONResponse(content={"message": response}, status_code=200)

    raise HTTPException(status_code=400, detail="Something went wrong")


@app.post("/reset_db")
async def reset_chroma_db():
    try:
        if persistent_client.reset(): 
            return {"message": "ChromaDB reset successful"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/list_documents")
async def list_documents():
    """Recupera la lista dei documenti presenti in ChromaDB."""
    try:
        results = collection.get(include=["documents", "embeddings"])
        print(results)
        all_docs = []
        if results and "ids" in results:
            print(results["embeddings"])
            for doc in results["ids"]:
                all_docs.append(doc.split("_chunk_")[0])

            return {"documents": list(set(all_docs))}
    except Exception as e:
        print(str(e))
        return {"documents": []}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, debug=True)
