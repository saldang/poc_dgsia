import os
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_db import collection, embeddings as em
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
    chunks = []
    if file_path.endswith(".pdf"):
        # Load the PDF file and split the data into chunks
        loader = UnstructuredPDFLoader(file_path=file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        chunks = text_splitter.split_documents(data)
    elif file_path.endswith(".xlsx"):
        if "test" in file_path.lower():
            data = pd.read_excel(
                file_path, sheet_name=None, engine="openpyxl", header=[1]
            )
            for sheet_name, df in data.items():
                df = df.astype(str)
                df = df.replace("nan", "")
                lines = []
                for index, row in df.iterrows():
                    line = " - ".join(
                        [
                            f"{col}: {"" if row[col] is None else  row[col]}".strip().replace(
                                "\n", " "
                            )
                            for col in df.columns
                        ]
                    )
                    lines.append(line)
                chunks = RecursiveCharacterTextSplitter().create_documents(lines)

        else:
            data = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
            for sheet_name, df in data.items():
                df = df.astype(str)
                df = df.replace("nan", "")
                lines = []
                for index, row in df.iterrows():
                    line = " - ".join(
                        [
                            f"{col}: {"" if row[col] is None else  row[col]}".strip().replace(
                                "\n", " "
                            )
                            for col in df.columns
                        ]
                    )
                    lines.append(line)
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
def embed(file):
    print(file)
    # Check if the file is valid, save it, load and split the data, add to the database, and remove the temporary file
    if file.filename != "" and file and allowed_file(file.filename):
        file_path = save_file(file)
        chunks = load_and_split_data(file_path)
        chunk_ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]
        texts = [chunk.page_content for chunk in chunks]
        chunk_embeddings = [em.embed_query(text) for text in texts]

        collection.add(
            documents=texts,
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            metadatas=[{"source": file.filename} for _ in range(len(chunks))],
        )
        os.remove(file_path)
        return True

    return False
