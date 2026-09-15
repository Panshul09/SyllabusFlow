import streamlit as st

st.title("A-Level Study Planner")

st.write("Welcome! Let's organize your A-Level preparation.")

st.header("My Subjects")

subject = st.text_input("Enter a subject")

if st.button("Add Subject"):
    if subject:
        st.success(f"{subject} added!")
    else:
        st.warning("Please enter a subject.")