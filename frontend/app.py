"""Show the Streamlit counter. Edit the page here; copy for another API-driven page."""

import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8081")

st.set_page_config(page_title="Streamlit counter", page_icon="🔢")
st.title("Streamlit counter")
st.write("One shared counter, saved in SQLite.")

# Streamlit reruns this script for each browser interaction. Only the clicked
# button sends POST; ordinary page loads send GET and cannot change the count.
increase = st.button("Add 1", type="primary")
try:
    # This HTTP request runs in the Python UI server, not in browser JavaScript.
    with httpx.Client(timeout=5) as client:
        if increase:
            response = client.post(f"{API_URL}/api/counter/increment")
        else:
            response = client.get(f"{API_URL}/api/counter")
        response.raise_for_status()
    st.subheader(f"Count: {response.json()['value']}")
except httpx.HTTPError:
    st.error("Cannot reach the API. Please try again.")
