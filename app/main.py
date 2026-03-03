import sys
from pathlib import Path

# Ensure project root is in sys.path for standalone Python execution
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.faq import ingest_faq_data, faq_chain, get_chroma_client
from app.sql import sql_chain
from app.config import FAQS_PATH
from app.router import router
from app.smalltalk import handle_smalltalk

# cache initialization (CRITICAL for Streamlit)
@st.cache_resource
def init_chroma():
    chroma_client = get_chroma_client()
    ingest_faq_data(FAQS_PATH, chroma_client)
    return chroma_client

# initialize once
chroma_client = init_chroma()

def ask(query):
    print("Query:", query)
    route = router(query).name
    print("route =", route)
    if route == 'faq':
        return faq_chain(query, chroma_client)
    elif route == 'sql':
        return sql_chain(query)
    elif route == 'smalltalk':
        return handle_smalltalk(query)
    else:
        return (f"I'm sorry, I can help with shopping Shoes and accessories only.")

st.title("ShopAssist E-commerce Chat Bot")

query = st.chat_input("Write your query")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role":"user", "content":query})

    response = ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


