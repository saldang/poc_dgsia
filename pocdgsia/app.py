import streamlit as st

home_page = st.Page("routes/home.py", title="Home", icon=":material/home:")
knowledge_page = st.Page(
    "routes/knowledge.py", title="Knowledge Base", icon=":material/book:"
)

pg = st.navigation([home_page, knowledge_page])
st.set_page_config(page_title="Tests and Test Plans", page_icon=":material/edit:")
pg.run()
