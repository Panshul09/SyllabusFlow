import streamlit as st
from data_manager import load_data, save_data

st.title("A-Level Study Planner")

data = load_data()

st.header("My Subjects")

subject = st.text_input("Enter a subject")

if st.button("Add Subject"):
    if subject:
        data["Subjects"].append({
            "name": subject
        })

        save_data(data)

        st.success(f"{subject} added!")
    else:
        st.warning("Please enter a subject.")

st.header("Subjects")

for subject in data["Subjects"]:
    st.write(subject["name"])