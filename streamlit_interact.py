import streamlit as st

st.title("Main Window")

with st.expander("Open Child Window 1"):
    st.write("This is Child Window 1.")
    # Add more components for Child Window 1 here

with st.expander("Open Child Window 2"):
    st.write("This is Child Window 2.")
    # Add more components for Child Window 2 here
