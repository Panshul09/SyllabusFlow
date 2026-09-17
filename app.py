import streamlit as st

from data_manager import load_data, save_data
from planner import add_subject, add_topic


st.title("A-Level Study Planner")

data = load_data()

st.header("Add Subject")

subject_name = st.text_input("Subject name")

if st.button("Add Subject"):
    try:
        add_subject(data, subject_name)
        save_data(data)
        st.success(f"{subject_name} added!")
    except ValueError as error:
        st.error(str(error))


st.header("My Subjects")

for subject in data["subjects"]:
    st.subheader(subject["name"])

    with st.form(f"topic_form_{subject['name']}"):
        topic_name = st.text_input(
            f"Add topic to {subject['name']}"
        )

        submitted = st.form_submit_button(
            f"Add Topic to {subject['name']}"
        )

        if submitted:
            try:
                add_topic(data, subject["name"], topic_name)
                save_data(data)
                st.success(f"{topic_name} added!")
            except ValueError as error:
                st.error(str(error))

    for topic in subject["topics"]:
        st.write(f"• {topic['name']}")