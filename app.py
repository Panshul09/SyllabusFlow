import streamlit as st
st.set_page_config(
    page_title="A-Level Study Planner",
    page_icon="📚",
    layout="wide"
)
from datetime import date
import pandas as pd
from data_manager import load_data, save_data
from planner import (
    add_subject,
    add_topic,
    set_topic_completed,
    calculate_progress
)
from scheduler import generate_schedule
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0;
        }

        .subtitle {
            color: #6b7280;
            margin-top: 0;
            margin-bottom: 2rem;
        }

        .metric-card {
            padding: 1.2rem;
            border-radius: 14px;
            background: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.15);
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    '<div class="main-title">A-Level Study Planner</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Plan smarter. Study consistently. Track your progress.</div>',
    unsafe_allow_html=True
)

data = load_data()

st.sidebar.title("📚 A-Level Planner")

st.sidebar.caption(
    "Plan smarter. Study consistently."
)
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Subjects",
        "Schedule",
        "Analytics"
    ]
)
total_topics = 0
completed_topics = 0

for subject in data["subjects"]:

    for topic in subject["topics"]:

        total_topics += 1

        if topic["completed"]:
            completed_topics += 1

if total_topics > 0:
    overall_progress = completed_topics / total_topics
else:
    overall_progress = 0

total_subjects = len(data["subjects"])

remaining_topics = total_topics - completed_topics
if page == "Dashboard":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Subjects",
            total_subjects
        )

    with col2:
        st.metric(
            "Topics Completed",
            f"{completed_topics}/{total_topics}"
        )

    with col3:
        st.metric(
            "Overall Progress",
            f"{overall_progress * 100:.0f}%"
        )

    st.subheader("Overall Progress")

    st.progress(
        overall_progress,
        text=f"{overall_progress * 100:.0f}% complete"
    )
    st.subheader("Upcoming Exams")

    upcoming_exams = []

    for subject in data["subjects"]:

        if subject["exam_date"]:

            exam_date = date.fromisoformat(
                subject["exam_date"]
            )

            days_left = (exam_date - date.today()).days

            upcoming_exams.append({
                "name": subject["name"],
                "date": subject["exam_date"],
                "days_left": days_left
            })

    upcoming_exams.sort(
        key=lambda subject: subject["date"]
    )

    if not upcoming_exams:

        st.info("No exam dates added yet.")

    else:

        exam_columns = st.columns(
            len(upcoming_exams[:3])
        )

        for column, exam in zip(
            exam_columns,
            upcoming_exams[:3]
        ):

            with column:

                st.metric(
                    exam["name"],
                    f"{exam['days_left']} days"
                )

                st.caption(
                    f"Exam: {exam['date']}"
                )
if page == "Schedule":
    st.title("Study Schedule")
    st.caption(
        "Let the planner decide what to study based on your priorities."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        available_hours = st.number_input(
            "How many hours can you study today?",
            min_value=0.5,
            max_value=24.0,
            value=4.0,
            step=0.5
        )

    with col2:
        st.write("")
        st.write("")

        generate = st.button(
            "Generate Today's Schedule",
            use_container_width=True
        )

    if generate:
        schedule = generate_schedule(
            data,
            available_hours
        )

        if not schedule:
            st.info("No incomplete topics available.")

        else:

            st.subheader("Your Plan")

            for item in schedule:

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(
                            f"### {item['topic']}"
                        )

                        st.caption(
                            f"{item['subject']} • "
                            f"Priority score: {item['priority']:.2f}"
                        )

                    with col2:
                        st.metric(
                            "Study time",
                            f"{item['hours']}h"
                        )
                    

            


if page == "Subjects":
    with st.expander("➕ Add Subject"):
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
        
    st.subheader("My Subjects")


    for subject in data["subjects"]:

        progress = calculate_progress(subject)
        topic_count = len(subject["topics"])

        completed_count = sum(
            topic["completed"]
            for topic in subject["topics"]
        )

        with st.expander(
            f"{subject['name']} — {progress * 100:.0f}% complete"
        ):

            st.progress(
                progress,
                text=f"{progress * 100:.0f}% complete"
            )
            st.caption(
                f"{completed_count}/{topic_count} topics completed"
            )

            if subject["exam_date"]:
                st.write(
                    f"Exam: {subject['exam_date']}"
                )

            with st.form(f"topic_form_{subject['name']}"):

                topic_name = st.text_input(
                    "Topic name"
                )

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

                submitted = st.form_submit_button(
                    "Add Topic"
                )

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

                        st.success(
                            f"{topic_name} added!"
                        )

                    except ValueError as error:
                        st.error(str(error))

            for topic in subject["topics"]:

                completed = st.checkbox(
                    topic["name"],
                    value=topic["completed"],
                    key=f"complete_{subject['name']}_{topic['name']}"
                )

                if completed != topic["completed"]:

                    set_topic_completed(
                        data,
                        subject["name"],
                        topic["name"],
                        completed
                    )

                    save_data(data)

                    st.rerun()
if page == "Analytics": 
    st.title("Analytics")

    st.caption(
        "A breakdown of your current study progress."
    )

    analytics_data = []

    for subject in data["subjects"]:

        total_topics = len(subject["topics"])

        completed_topics = sum(
            topic["completed"]
            for topic in subject["topics"]
        )

        remaining_topics = (
            total_topics - completed_topics
        )

        remaining_hours = sum(
            topic["estimated_hours"]
            for topic in subject["topics"]
            if not topic["completed"]
        )

        progress = calculate_progress(subject)

        analytics_data.append({
            "Subject": subject["name"],
            "Progress": progress * 100,
            "Completed": completed_topics,
            "Remaining": remaining_topics,
            "Study Hours Remaining": remaining_hours
        })
    if not analytics_data:
        st.info(
            "Add some subjects and topics to see analytics."
        )
    else:
        total_topics = sum(
            item["Completed"] + item["Remaining"]
            for item in analytics_data
        )

        completed_topics = sum(
            item["Completed"]
            for item in analytics_data
        )

        remaining_topics = sum(
            item["Remaining"]
            for item in analytics_data
        )

        total_remaining_hours = sum(
            item["Study Hours Remaining"]
            for item in analytics_data
        )

        overall_progress = (
            completed_topics / total_topics
            if total_topics > 0
            else 0
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Overall Progress",
                f"{overall_progress * 100:.0f}%"
            )

        with col2:
            st.metric(
                "Completed",
                completed_topics
            )

        with col3:
            st.metric(
                "Remaining",
                remaining_topics
            )

        with col4:
            st.metric(
                "Hours Remaining",
                f"{total_remaining_hours:.1f}h"
            )
        df = pd.DataFrame(analytics_data)
        st.subheader("Subject Progress")
        progress_chart = df[
            ["Subject", "Progress"]
        ].set_index("Subject")

        st.bar_chart(
            progress_chart
        )
        st.subheader("Study Hours Remaining")
        hours_chart = df[
            ["Subject", "Study Hours Remaining"]
        ].set_index("Subject")

        st.bar_chart(
            hours_chart
        )
        st.subheader("Subject Breakdown")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )