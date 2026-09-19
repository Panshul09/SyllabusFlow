import streamlit as st
from datetime import date

from data_manager import load_data, save_data
from planner import add_subject, add_topic
from scheduler import generate_schedule

st.title("A-Level Study Planner")

data = load_data()
st.header("Today's Study Schedule")

available_hours = st.number_input(
    "How many hours can you study today?",
    min_value=0.5,
    max_value=24.0,
    value=4.0,
    step=0.5
)

if st.button("Generate Today's Schedule"):

    schedule = generate_schedule(
        data,
        available_hours
    )

    if not schedule:
        st.info("No incomplete topics available.")

    else:
        for item in schedule:

            st.write(
                f"**{item['subject']} — {item['topic']}**"
            )

            st.write(
                f"Study time: {item['hours']} hours  |  "
                f"Priority: {item['priority']:.2f}"
            )

st.header("Add Subject")

with st.form("subject_form"):
    subject_name = st.text_input("Subject name")
    exam_date = st.date_input(
        "Exam date",
        value=None
    )

    submitted = st.form_submit_button("Add Subject")

    if submitted:
        try:
            add_subject(
                data,
                subject_name,
                exam_date.isoformat()
            )

            save_data(data)

            st.success(f"{subject_name} added!")

        except ValueError as error:
            st.error(str(error))


st.header("My Subjects")


for subject in data["subjects"]:

    st.subheader(subject["name"])

    if subject["exam_date"]:
        st.write(f"Exam: {subject['exam_date']}")

    with st.form(f"topic_form_{subject['name']}"):

        topic_name = st.text_input("Topic name")

        difficulty = st.slider(
            "Difficulty",
            min_value=1,
            max_value=5,
            value=3
        )
        
        importance = st.slider(
            "Importance",
            min_value=1,
            max_value=5,
            value=3
        )
        
        estimated_hours = st.number_input(
            "Estimated study hours",
            min_value=0.5,
            max_value=100.0,
            value=1.0,
            step=0.5
        )

        submitted = st.form_submit_button("Add Topic")

        if submitted:

            try:
                add_topic(
                    data,
                    subject["name"],
                    topic_name,
                    difficulty,
                    importance,
                    estimated_hours
                )

                save_data(data)

                st.success(f"{topic_name} added!")

            except ValueError as error:
                st.error(str(error))


    for topic in subject["topics"]:

        st.write(
            f"• {topic['name']} — "
            f"Difficulty {topic['difficulty']}/5 — "
            f"Importance {topic['importance']}/5 — "
            f"{topic['estimated_hours']}h"
        )