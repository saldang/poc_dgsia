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
            response = requests.post(
                f"{FASTAPI_URL}/embed",
                files={"file": file},
                params={"collection": st.session_state["selected_collection"]},
            )
            if response.status_code != 200:
                st.error("Error: Unable to embed the file.")


if "selected_collection" not in st.session_state:
    st.session_state["selected_collection"] = None

# Carica lista collezioni
collections_response = requests.get(f"{FASTAPI_URL}/collections")

collection_names = collections_response.json().get("collections", [])
new_collection = st.text_input("Crea nuova collection")
if st.button("Crea"):
    if new_collection and new_collection not in collection_names:
        requests.post(f"{FASTAPI_URL}/collections/{new_collection}")
        collection_names.append(new_collection)
        st.success(f"Creata collection '{new_collection}'")
        st.session_state["selected_collection"] = new_collection

# Selezione collection corrente
st.session_state["selected_collection"] = st.selectbox(
    "Collection attiva",
    options=collection_names,
    index=(
        collection_names.index(st.session_state["selected_collection"])
        if st.session_state["selected_collection"] in collection_names
        else 0
    ),
)

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
if row[0].button("Elimina Collection", key="reset_button"):
    response = requests.delete(
        f"{FASTAPI_URL}/collections/{st.session_state['selected_collection']}"
    )
    if response.status_code == 200:
        st.success("Collection eliminata con successo.")
        collection_names.remove(st.session_state["selected_collection"])
        st.session_state["selected_collection"] = None
    else:
        st.error(f"Error: {response.text}")

if row[1].button("Documenti nella collection", key="list_documents_button"):
    if st.session_state["selected_collection"]:
        st.write(f"### Collection: {st.session_state['selected_collection']}")
        response = requests.post(
            f"{FASTAPI_URL}/list_documents",
            json={"collection": st.session_state["selected_collection"]},
        )
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
    else:
        st.error("Seleziona una collection prima di visualizzare i documenti.")
