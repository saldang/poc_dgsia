import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .utils.ingestion import multimodal_ingestion
from .vector_db import create_or_get_collection, embeddings as em

import pandas as pd

TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")


# Function to check if the uploaded file is allowed based on the file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "pdf",
        "txt",
        "xls",
        "xlsx",
    }


# Function to save the uploaded file to the temporary folder
def save_file(file):
    # Save the uploaded file with a secure filename and return the file path
    filename = file.filename
    file_path = os.path.join(TEMP_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path


# Function to load and split the data from the PDF file
def load_and_split_data(file_path):
    if file_path.endswith(".pdf"):
        return multimodal_ingestion(file_path)

    chunks = []
    if file_path.endswith(".xlsx"):
        if "test" in file_path.lower():
            data = pd.read_excel(
                file_path, sheet_name=None, engine="openpyxl", header=[1]
            )
            for sheet_name, df in data.items():
                df = df.astype(str).replace("nan", "")
                lines = [
                    " - ".join([f"{col}: {row[col]}" for col in df.columns])
                    for _, row in df.iterrows()
                ]
                chunks = RecursiveCharacterTextSplitter().create_documents(lines)
        else:
            data = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
            for sheet_name, df in data.items():
                df = df.astype(str).replace("nan", "")
                lines = [
                    " - ".join([f"{col}: {row[col]}" for col in df.columns])
                    for _, row in df.iterrows()
                ]
                chunks = RecursiveCharacterTextSplitter(
                    chunk_size=250, chunk_overlap=50
                ).create_documents(lines)
    elif file_path.endswith(".txt"):
        with open(file_path, "r") as f:
            data = f.read()
            chunks = RecursiveCharacterTextSplitter(
                chunk_size=250, chunk_overlap=50
            ).create_documents([data])
    else:
        raise Exception("File type not supported")
    return chunks


# Main function to handle the embedding process
def embed(file, collection_name="default"):
    print(file)
    # Check if the file is valid, save it, load and split the data, add to the database, and remove the temporary file
    if file.filename != "" and file and allowed_file(file.filename):
        file_path = save_file(file)
        chunks = load_and_split_data(file_path)
        chunk_ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]
        texts = [chunk.page_content for chunk in chunks]
        chunk_embeddings = [em.embed_query(text) for text in texts]

        create_or_get_collection(collection_name=collection_name).add(
            documents=texts,
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            metadatas=[{"source": file.filename} for _ in range(len(chunks))],
        )
        os.remove(file_path)
        return True

    return False
