import streamlit as st
import requests

# Indirizzo del server FastAPI
FASTAPI_URL = "http://localhost:8000"


def read_and_save_file():
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with st.session_state["ingestion_spinner"], st.spinner(
            f"Ingesting {file.name}"
        ):
            response = requests.post(f"{FASTAPI_URL}/embed", files={"file": file})
            if response.status_code != 200:
                st.error("Error: Unable to embed the file.")



st.title("Lista Documenti Caricati")
st.subheader("Upload a document")
st.file_uploader(
    "Upload document",
    type=["pdf", "txt", "xlsx"],
    key="file_uploader",
    on_change=read_and_save_file,
    label_visibility="collapsed",
    accept_multiple_files=True,
)

st.session_state["ingestion_spinner"] = st.empty()

row = st.columns(2)
if row[0].button("Reset ChromaDB", key="reset_button"):
    response = requests.post(f"{FASTAPI_URL}/reset_db")
    if response.status_code == 200:
        st.success("ChromaDB reset successful")
    else:
        st.error(f"Error: {response.text}")

if row[1].button("Aggiorna lista documenti"):
    response = requests.get(f"{FASTAPI_URL}/list_documents")
    if response.status_code == 200:
        documents = response.json().get("documents", [])
        if documents:
            st.write("### Documenti:")
            for doc in documents:
                st.write(f"- {doc}")
        else:
            st.info("Nessun documento trovato.")
    else:
        st.error(f"Errore nel recupero dei documenti: {response.text}")
