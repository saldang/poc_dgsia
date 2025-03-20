import os
import requests
import streamlit as st
from streamlit_chat import message


FASTAPI_URL = "http://localhost:8000"
MODEL_LIST = ["phi4", "qwen2.5-coder:14b", "deepseek-r1:14b"]
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")


def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
        print(msg)
    st.session_state["thinking_spinner"] = st.empty()


def process_input(model):
    if (
        st.session_state["user_input"]
        and len(st.session_state["user_input"].strip()) > 0
    ):
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking"):
            response = requests.post(
                f"{FASTAPI_URL}/query", json={"query": user_text, "model": model}
            )
            if response.status_code == 200:
                agent_text = response.json().get("message")
                print(agent_text)
            else:
                agent_text = "Error: Unable to process the query."

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))


if len(st.session_state) == 0:
    st.session_state["messages"] = []

st.header("Tests and Test Plans Chat")
model: str = st.selectbox("Model", options=MODEL_LIST)
print(model)


display_messages()
st.text_input("Message", key="user_input", on_change=process_input, args=(model,))
