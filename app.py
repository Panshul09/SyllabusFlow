import streamlit as st
from datetime import date
import pandas as pd

from data_manager import load_data, save_data
from planner import (
    add_subject,
    add_paper,
    add_topic,
    set_topic_completed,
    calculate_progress
)
from scheduler import generate_schedule


st.set_page_config(
    page_title="A-Level Study Planner",
    page_icon="📚",
    layout="wide"
)


data = load_data()


# -------------------------
# Helper functions
# -------------------------

def get_subject_progress(subject):
    total_topics = 0
    completed_topics = 0

    for paper in subject["papers"]:
        for topic in paper["topics"]:
            total_topics += 1

            if topic["completed"]:
                completed_topics += 1

    if total_topics == 0:
        return 0

    return completed_topics / total_topics


def get_paper_hours_remaining(paper):
    return sum(
        topic["estimated_hours"]
        for topic in paper["topics"]
        if not topic["completed"]
    )


def get_exam_status(exam_date):
    if not exam_date:
        return "No exam date", None

    exam = date.fromisoformat(exam_date)
    days_left = (exam - date.today()).days

    if days_left > 0:
        return f"{days_left} days left", days_left

    if days_left == 0:
        return "Exam today", 0

    return "Exam completed", days_left


def get_overall_stats(data):
    total_topics = 0
    completed_topics = 0
    total_papers = 0

    for subject in data["subjects"]:

        total_papers += len(subject["papers"])

        for paper in subject["papers"]:

            for topic in paper["topics"]:

                total_topics += 1

                if topic["completed"]:
                    completed_topics += 1

    if total_topics == 0:
        progress = 0
    else:
        progress = completed_topics / total_topics

    return (
        total_papers,
        total_topics,
        completed_topics,
        progress
    )


# -------------------------
# Sidebar
# -------------------------

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
        "Analytics",
        "AI Coach"
    ]
)


# -------------------------
# Overall statistics
# -------------------------

(
    total_papers,
    total_topics,
    completed_topics,
    overall_progress
) = get_overall_stats(data)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("Dashboard")

    st.caption(
        "Your complete A-Level study overview."
    )

    # Summary cards

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Subjects",
            len(data["subjects"])
        )

    with col2:
        st.metric(
            "Papers",
            total_papers
        )

    with col3:
        st.metric(
            "Topics Completed",
            f"{completed_topics}/{total_topics}"
        )

    with col4:
        st.metric(
            "Overall Progress",
            f"{overall_progress * 100:.0f}%"
        )

    st.subheader("Overall Progress")

    st.progress(
        overall_progress,
        text=f"{overall_progress * 100:.0f}% complete"
    )


    # -------------------------
    # Upcoming papers
    # -------------------------

    st.subheader("Upcoming Papers")

    upcoming_papers = []

    for subject in data["subjects"]:

        for paper in subject["papers"]:

            status, days_left = get_exam_status(
                paper["exam_date"]
            )

            if days_left is not None and days_left >= 0:

                upcoming_papers.append({
                    "subject": subject["name"],
                    "paper": paper["name"],
                    "code": paper["code"],
                    "exam_date": paper["exam_date"],
                    "days_left": days_left
                })

    upcoming_papers.sort(
        key=lambda paper: paper["exam_date"]
    )

    if not upcoming_papers:

        st.info("No upcoming papers.")

    else:

        columns = st.columns(
            min(len(upcoming_papers[:4]), 4)
        )

        for column, paper in zip(
            columns,
            upcoming_papers[:4]
        ):

            with column:

                if paper["days_left"] == 0:
                    st.metric(
                        f"{paper['subject']} — {paper['paper']}",
                        "TODAY"
                    )

                else:
                    st.metric(
                        f"{paper['subject']} — {paper['paper']}",
                        f"{paper['days_left']} days"
                    )

                if paper["code"]:
                    st.caption(
                        f"{paper['code']} • "
                        f"Exam: {paper['exam_date']}"
                    )

                else:
                    st.caption(
                        f"Exam: {paper['exam_date']}"
                    )


    # -------------------------
    # Subject overview
    # -------------------------

    st.subheader("Your Subjects")

    for subject in data["subjects"]:

        subject_progress = get_subject_progress(
            subject
        )

        st.markdown(
            f"### {subject['name']}"
        )

        st.progress(
            subject_progress,
            text=f"{subject_progress * 100:.0f}% complete"
        )

        if not subject["papers"]:

            st.info(
                "No papers added yet."
            )

            continue

        paper_columns = st.columns(
            min(len(subject["papers"]), 3)
        )

        for column, paper in zip(
            paper_columns,
            subject["papers"]
        ):

            with column:

                with st.container(border=True):

                    title = paper["name"]

                    if paper["code"]:
                        title = (
                            f"{title} ({paper['code']})"
                        )

                    st.markdown(
                        f"**{title}**"
                    )

                    paper_progress = calculate_progress(
                        paper
                    )

                    st.progress(
                        paper_progress,
                        text=(
                            f"{paper_progress * 100:.0f}% complete"
                        )
                    )

                    hours_remaining = (
                        get_paper_hours_remaining(paper)
                    )

                    st.caption(
                        f"{hours_remaining:.1f}h remaining"
                    )

                    status, days_left = get_exam_status(
                        paper["exam_date"]
                    )

                    if paper["exam_date"]:
                        st.write(
                            f"📅 {paper['exam_date']}"
                        )

                    if days_left == 0:
                        st.warning("Exam today")

                    elif days_left is not None and days_left > 0:
                        st.write(
                            f"⏳ {days_left} days left"
                        )

                    elif days_left is not None:
                        st.caption(
                            "Exam completed"
                        )


# =========================================================
# SUBJECTS
# =========================================================

if page == "Subjects":

    st.title("Subjects")

    st.caption(
        "Manage subjects, papers and topics."
    )


    # -------------------------
    # Add subject
    # -------------------------

    with st.expander("➕ Add Subject"):

        with st.form(
            "subject_form",
            enter_to_submit=False
        ):   
            
            subject_name = st.text_input(
                "Subject name"
            )

            submitted = st.form_submit_button(
                "Add Subject",
                width="stretch"
            )

            if submitted:

                try:

                    add_subject(
                        data,
                        subject_name
                    )

                    save_data(data)

                    st.success(
                        f"{subject_name} added!"
                    )

                    st.rerun()

                except ValueError as error:

                    st.error(
                        str(error)
                    )


    st.subheader("My Subjects")


    # -------------------------
    # Subjects and papers
    # -------------------------

    for subject in data["subjects"]:

        subject_progress = get_subject_progress(
            subject
        )

        with st.expander(
            f"{subject['name']} — "
            f"{subject_progress * 100:.0f}% complete"
        ):

            st.progress(
                subject_progress,
                text=(
                    f"{subject_progress * 100:.0f}% complete"
                )
            )


            # -------------------------
            # Add paper
            # -------------------------

            st.markdown("#### Add Paper")

            paper_name = st.text_input(
                "Paper name",
                key=f"paper_name_{subject['name']}"
            )

            paper_code = st.text_input(
                "Paper code (optional)",
                key=f"paper_code_{subject['name']}"
            )

            has_exam_date = st.checkbox(
                "Set an exam date",
                key=f"has_exam_date_{subject['name']}"
            )

            paper_exam_date = st.date_input(
                "Exam date",
                value=date.today(),
                disabled=not has_exam_date,
                key=f"paper_exam_date_{subject['name']}"
            )

            if st.button(
                "Add Paper",
                key=f"add_paper_{subject['name']}",
                width="stretch"
            ):

                try:

                    exam_date = (
                        paper_exam_date.isoformat()
                        if has_exam_date
                        else None
                    )

                    add_paper(
                        data,
                        subject["name"],
                        paper_name,
                        exam_date,
                        paper_code
                    )

                    save_data(data)

                    st.success(
                        f"{paper_name} added!"
                    )

                    st.rerun()

                except ValueError as error:

                    st.error(
                        str(error)
                    )


            # -------------------------
            # Existing papers
            # -------------------------

            for paper in subject["papers"]:

                paper_progress = calculate_progress(
                    paper
                )

                with st.expander(
                    f"{paper['name']} — "
                    f"{paper_progress * 100:.0f}% complete"
                ):

                    if paper["code"]:

                        st.caption(
                            f"Paper code: {paper['code']}"
                        )


                    status, days_left = get_exam_status(
                        paper["exam_date"]
                    )

                    if paper["exam_date"]:

                        if days_left == 0:

                            st.warning(
                                "Exam today"
                            )

                        elif days_left > 0:

                            st.info(
                                f"{paper['exam_date']} • "
                                f"{days_left} days left"
                            )

                        else:

                            st.caption(
                                f"{paper['exam_date']} • "
                                "Exam completed"
                            )


                    st.progress(
                        paper_progress,
                        text=(
                            f"{paper_progress * 100:.0f}% complete"
                        )
                    )

                    hours_remaining = (
                        get_paper_hours_remaining(paper)
                    )

                    st.caption(
                        f"{hours_remaining:.1f} study hours remaining"
                    )


                    # -------------------------
                    # Add topic
                    # -------------------------

                    with st.form(
                        f"topic_form_"
                        f"{subject['name']}_"
                        f"{paper['name']}",
                        enter_to_submit=False
                    ):

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
                            "Add Topic",
                             width="stretch"
                        )

                        if submitted:

                            try:

                                add_topic(
                                    data,
                                    subject["name"],
                                    paper["name"],
                                    topic_name,
                                    difficulty,
                                    importance,
                                    estimated_hours
                                )

                                save_data(data)

                                st.success(
                                    f"{topic_name} added!"
                                )

                                st.rerun()

                            except ValueError as error:

                                st.error(
                                    str(error)
                                )


                    # -------------------------
                    # Existing topics
                    # -------------------------

                    if not paper["topics"]:

                        st.caption(
                            "No topics added yet."
                        )

                    else:

                        st.markdown(
                            "#### Topics"
                        )

                        for topic in paper["topics"]:

                            completed = st.checkbox(
                                topic["name"],
                                value=topic["completed"],
                                key=(
                                    f"complete_"
                                    f"{subject['name']}_"
                                    f"{paper['name']}_"
                                    f"{topic['name']}"
                                )
                            )

                            st.caption(
                                f"Difficulty {topic['difficulty']}/5 • "
                                f"Importance {topic['importance']}/5 • "
                                f"{topic['estimated_hours']}h"
                            )

                            if completed != topic["completed"]:

                                set_topic_completed(
                                    data,
                                    subject["name"],
                                    paper["name"],
                                    topic["name"],
                                    completed
                                )

                                save_data(data)

                                st.rerun()


# =========================================================
# SCHEDULE
# =========================================================

if page == "Schedule":

    st.title("Study Schedule")

    st.caption(
        "Generate a schedule based on paper deadlines and workload."
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

        generate = st.button(
            "Generate Schedule",
            width="stretch"
        )


    if generate:

        schedule = generate_schedule(
            data,
            available_hours
        )


        if not schedule:

            st.info(
                "No eligible incomplete topics are available."
            )

        else:

            st.subheader("Your Plan")


            grouped_schedule = {}

            for item in schedule:

                key = (
                    item["subject"],
                    item["paper"]
                )

                grouped_schedule.setdefault(
                    key,
                    []
                ).append(item)


            for (subject_name, paper_name), items in grouped_schedule.items():

                with st.expander(
                    f"{subject_name} — {paper_name}",
                    expanded=True
                ):

                    for item in items:

                        with st.container(border=True):

                            col1, col2 = st.columns([4, 1])

                            with col1:

                                st.markdown(
                                    f"**{item['topic']}**"
                                )

                                if item["days_left"] is None:

                                    exam_text = "No exam date"

                                elif item["days_left"] == 0:

                                    exam_text = "Exam today"

                                else:

                                    exam_text = (
                                        f"{item['days_left']} days "
                                        "until exam"
                                    )

                                st.caption(
                                    f"Priority: "
                                    f"{item['priority']:.2f} • "
                                    f"{exam_text}"
                                )

                            with col2:

                                st.metric(
                                    "Study time",
                                    f"{item['hours']}h"
                                )


# =========================================================
# ANALYTICS
# =========================================================

if page == "Analytics":

    st.title("Analytics")

    st.caption(
        "See your progress across subjects and papers."
    )


    analytics_data = []


    for subject in data["subjects"]:

        for paper in subject["papers"]:

            total = len(paper["topics"])

            completed = sum(
                topic["completed"]
                for topic in paper["topics"]
            )

            remaining = total - completed

            hours_remaining = (
                get_paper_hours_remaining(paper)
            )

            progress = calculate_progress(
                paper
            )

            status, days_left = get_exam_status(
                paper["exam_date"]
            )

            analytics_data.append({
                "Subject": subject["name"],
                "Paper": paper["name"],
                "Paper Label": f"{subject['name']} — {paper['name']}",
                "Progress": progress * 100,
                "Completed": completed,
                "Remaining": remaining,
                "Hours Remaining": hours_remaining,
                "Exam Status": status
            })


    if not analytics_data:

        st.info(
            "Add subjects and papers to see analytics."
        )

    else:

        total_completed = sum(
            item["Completed"]
            for item in analytics_data
        )

        total_remaining = sum(
            item["Remaining"]
            for item in analytics_data
        )

        total_hours = sum(
            item["Hours Remaining"]
            for item in analytics_data
        )

        total_topics_analytics = (
            total_completed + total_remaining
        )

        if total_topics_analytics > 0:

            analytics_progress = (
                total_completed /
                total_topics_analytics
            )

        else:

            analytics_progress = 0


        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Overall Progress",
                f"{analytics_progress * 100:.0f}%"
            )

        with col2:

            st.metric(
                "Completed",
                total_completed
            )

        with col3:

            st.metric(
                "Remaining",
                total_remaining
            )

        with col4:

            st.metric(
                "Hours Remaining",
                f"{total_hours:.1f}h"
            )


        df = pd.DataFrame(
            analytics_data
        )


        st.subheader(
            "Paper Progress"
        )

        progress_chart = df[
            [
                "Paper Label",
                "Progress"
            ]
        ].set_index("Paper Label")

        st.bar_chart(
            progress_chart
        )


        st.subheader(
            "Study Hours Remaining"
        )

        hours_chart = df[
            [
                "Paper Label",
                "Hours Remaining"
            ]
        ].set_index("Paper Label")

        st.bar_chart(
            hours_chart
        )


        st.subheader(
            "Paper Breakdown"
        )

        st.dataframe(
            df[
                [
                    "Subject",
                    "Paper",
                    "Progress",
                    "Completed",
                    "Remaining",
                    "Hours Remaining",
                    "Exam Status"
                ]
            ],
            width="stretch",
            hide_index=True
        )


# =========================================================
# AI COACH
# =========================================================

if page == "AI Coach":

    st.title("AI Study Coach")

    st.caption(
        "Get recommendations based on your current planner."
    )

    st.info(
        "The AI Coach requires an API account with "
        "available credits."
    )

    st.write(
        "The rest of the planner works independently "
        "of the AI service."
    )