"""Show the Streamlit counter. Edit the page here; copy for another SQLite page."""

import streamlit as st

import db

st.set_page_config(page_title="Streamlit counter", page_icon="🔢")
st.title("Streamlit counter")
st.write("One shared counter, saved in SQLite.")

# Streamlit reruns this script for each click. The button returns True only on
# the run caused by its own click, so a page load or reload never adds 1.
# No HTTP request is needed: the script calls the database code directly.
if st.button("Add 1", type="primary"):
    db.increment()


# A fragment reruns on its own, so clicks from other visitors show up here
# within two seconds, without a reload.
@st.fragment(run_every="2s")
def show_count():
    st.subheader(f"Count: {db.read()}")


show_count()
