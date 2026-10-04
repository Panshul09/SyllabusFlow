import streamlit as st
from datetime import date
import pandas as pd

from data_manager import load_data, save_data

from planner import (
    add_subject,
    add_paper,
    add_topic,
    set_topic_completed,
    calculate_progress,
    delete_subject,
    delete_paper,
    delete_topic,
    edit_subject,
    edit_paper,
    edit_topic,
    move_topic
)

from scheduler import generate_schedule

from ai_helper import get_ai_study_advice


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="A-Level Study Planner",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

data = load_data()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_subject_progress(subject):
    """Calculate completion percentage for an entire subject."""

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
    """Calculate unfinished study hours for a paper."""

    return sum(
        topic["estimated_hours"]
        for topic in paper["topics"]
        if not topic["completed"]
    )


def get_exam_status(exam_date):
    """
    Return a human-readable exam status
    and the number of days remaining.
    """

    if not exam_date:
        return "No exam date", None

    exam = date.fromisoformat(exam_date)

    days_left = (
        exam - date.today()
    ).days

    if days_left > 0:
        return f"{days_left} days left", days_left

    if days_left == 0:
        return "Exam today", 0

    return "Exam completed", days_left


def get_overall_stats(data):
    """Calculate overall planner statistics."""

    total_papers = 0
    total_topics = 0
    completed_topics = 0

    for subject in data["subjects"]:

        total_papers += len(
            subject["papers"]
        )

        for paper in subject["papers"]:

            for topic in paper["topics"]:

                total_topics += 1

                if topic["completed"]:
                    completed_topics += 1

    if total_topics == 0:
        progress = 0
    else:
        progress = (
            completed_topics /
            total_topics
        )

    return (
        total_papers,
        total_topics,
        completed_topics,
        progress
    )


# =========================================================
# SIDEBAR
# =========================================================

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


# =========================================================
# OVERALL STATS
# =========================================================

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

    # -----------------------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # OVERALL PROGRESS
    # -----------------------------------------------------

    st.subheader("Overall Progress")

    st.progress(
        overall_progress,
        text=f"{overall_progress * 100:.0f}% complete"
    )


    # -----------------------------------------------------
    # UPCOMING PAPERS
    # -----------------------------------------------------

    st.subheader("Upcoming Papers")

    upcoming_papers = []

    for subject in data["subjects"]:

        for paper in subject["papers"]:

            status, days_left = get_exam_status(
                paper["exam_date"]
            )

            # Ignore papers with no date
            if days_left is None:
                continue

            # Ignore papers whose exam has already happened
            if days_left < 0:
                continue

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

        st.info(
            "No upcoming papers."
        )

    else:

        number_of_cards = min(
            len(upcoming_papers[:4]),
            4
        )

        columns = st.columns(
            number_of_cards
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


    # -----------------------------------------------------
    # SUBJECT OVERVIEW
    # -----------------------------------------------------

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
            text=(
                f"{subject_progress * 100:.0f}% complete"
            )
        )


        if not subject["papers"]:

            st.caption(
                "No papers added yet."
            )

            continue


        paper_columns = st.columns(
            min(
                len(subject["papers"]),
                3
            )
        )


        for column, paper in zip(
            paper_columns,
            subject["papers"]
        ):

            with column:

                st.markdown(
                    f"**{paper['name']}**"
                )

                if paper["code"]:

                    st.caption(
                        paper["code"]
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
                    get_paper_hours_remaining(
                        paper
                    )
                )

                st.caption(
                    f"{hours_remaining:.1f}h remaining"
                )


                status, days_left = get_exam_status(
                    paper["exam_date"]
                )


                if days_left is None:

                    st.caption(
                        "No exam date"
                    )

                elif days_left == 0:

                    st.warning(
                        "Exam today"
                    )

                elif days_left > 0:

                    st.caption(
                        f"⏳ {days_left} days left"
                    )

                else:

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


    # -----------------------------------------------------
    # ADD SUBJECT
    # -----------------------------------------------------

    with st.expander("➕ Add Subject"):

        subject_name = st.text_input(
            "Subject name",
            key="new_subject_name"
        )

        if st.button(
            "Add Subject",
            key="add_subject_button",
            width="stretch"
        ):

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


    # -----------------------------------------------------
    # SUBJECT LIST
    # -----------------------------------------------------

    st.subheader("My Subjects")


    for subject_index, subject in enumerate(
        data["subjects"]
    ):

        subject_progress = get_subject_progress(
            subject
        )


        with st.expander(
            f"{subject['name']} — "
            f"{subject_progress * 100:.0f}% complete"
        ):

            # -------------------------------------------------
            # SUBJECT PROGRESS
            # -------------------------------------------------

            st.progress(
                subject_progress,
                text=(
                    f"{subject_progress * 100:.0f}% complete"
                )
            )


            # -------------------------------------------------
            # EDIT SUBJECT
            # -------------------------------------------------

            with st.expander("✏️ Edit Subject"):

                edited_subject_name = st.text_input(
                    "Subject name",
                    value=subject["name"],
                    key=(
                        f"edit_subject_name_{subject_index}"
                    )
                )


                if st.button(
                    "Save Subject",
                    key=(
                        f"save_subject_{subject_index}"
                    ),
                    width="stretch"
                ):

                    try:

                        edit_subject(
                            data,
                            subject["name"],
                            edited_subject_name
                        )

                        save_data(data)

                        st.rerun()

                    except ValueError as error:

                        st.error(
                            str(error)
                        )


            # -------------------------------------------------
            # DELETE SUBJECT
            # -------------------------------------------------

            delete_subject_confirm = st.checkbox(
                "I understand that deleting this subject "
                "will also delete all of its papers and topics.",
                key=(
                    f"confirm_delete_subject_{subject_index}"
                )
            )


            if st.button(
                "Delete Subject",
                key=(
                    f"delete_subject_{subject_index}"
                ),
                disabled=not delete_subject_confirm,
                width="stretch"
            ):

                try:

                    delete_subject(
                        data,
                        subject["name"]
                    )

                    save_data(data)

                    st.rerun()

                except ValueError as error:

                    st.error(
                        str(error)
                    )


            # -------------------------------------------------
            # ADD PAPER
            # -------------------------------------------------

            st.markdown("#### Add Paper")


            paper_name = st.text_input(
                "Paper name",
                key=(
                    f"new_paper_name_{subject_index}"
                )
            )


            paper_code = st.text_input(
                "Paper code (optional)",
                key=(
                    f"new_paper_code_{subject_index}"
                )
            )


            has_exam_date = st.checkbox(
                "Set an exam date",
                key=(
                    f"new_paper_has_date_{subject_index}"
                )
            )


            paper_exam_date = st.date_input(
                "Exam date",
                value=date.today(),
                disabled=not has_exam_date,
                key=(
                    f"new_paper_date_{subject_index}"
                )
            )


            if st.button(
                "Add Paper",
                key=(
                    f"add_paper_{subject_index}"
                ),
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


            # -------------------------------------------------
            # EXISTING PAPERS
            # -------------------------------------------------

            for paper_index, paper in enumerate(
                subject["papers"]
            ):

                paper_progress = calculate_progress(
                    paper
                )


                with st.expander(
                    f"{paper['name']} — "
                    f"{paper_progress * 100:.0f}% complete"
                ):

                    # -----------------------------------------
                    # PAPER INFORMATION
                    # -----------------------------------------

                    if paper["code"]:

                        st.caption(
                            f"Paper code: {paper['code']}"
                        )


                    status, days_left = get_exam_status(
                        paper["exam_date"]
                    )


                    if days_left is None:

                        st.caption(
                            "No exam date"
                        )

                    elif days_left == 0:

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
                        get_paper_hours_remaining(
                            paper
                        )
                    )


                    st.caption(
                        f"{hours_remaining:.1f} "
                        "study hours remaining"
                    )


                    # -----------------------------------------
                    # EDIT PAPER
                    # -----------------------------------------

                    with st.expander("✏️ Edit Paper"):

                        edited_paper_name = st.text_input(
                            "Paper name",
                            value=paper["name"],
                            key=(
                                f"edit_paper_name_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            )
                        )


                        edited_paper_code = st.text_input(
                            "Paper code",
                            value=paper["code"],
                            key=(
                                f"edit_paper_code_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            )
                        )


                        edit_has_exam_date = st.checkbox(
                            "Set an exam date",
                            value=(
                                paper["exam_date"]
                                is not None
                            ),
                            key=(
                                f"edit_paper_has_date_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            )
                        )


                        edited_exam_date = st.date_input(
                            "Exam date",
                            value=(
                                date.fromisoformat(
                                    paper["exam_date"]
                                )
                                if paper["exam_date"]
                                else date.today()
                            ),
                            disabled=not edit_has_exam_date,
                            key=(
                                f"edit_paper_date_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            )
                        )


                        if st.button(
                            "Save Paper",
                            key=(
                                f"save_paper_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
                            width="stretch"
                        ):

                            try:

                                new_exam_date = (
                                    edited_exam_date.isoformat()
                                    if edit_has_exam_date
                                    else None
                                )


                                edit_paper(
                                    data,
                                    subject["name"],
                                    paper["name"],
                                    edited_paper_name,
                                    edited_paper_code,
                                    new_exam_date
                                )


                                save_data(data)

                                st.rerun()


                            except ValueError as error:

                                st.error(
                                    str(error)
                                )


                    # -----------------------------------------
                    # DELETE PAPER
                    # -----------------------------------------

                    delete_paper_confirm = st.checkbox(
                        "Confirm deleting this paper "
                        "and all of its topics.",
                        key=(
                            f"confirm_delete_paper_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        )
                    )


                    if st.button(
                        "Delete Paper",
                        key=(
                            f"delete_paper_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        ),
                        disabled=not delete_paper_confirm,
                        width="stretch"
                    ):

                        try:

                            delete_paper(
                                data,
                                subject["name"],
                                paper["name"]
                            )

                            save_data(data)

                            st.rerun()


                        except ValueError as error:

                            st.error(
                                str(error)
                            )


                    # -----------------------------------------
                    # ADD TOPIC
                    # -----------------------------------------

                    st.markdown("#### Add Topic")


                    topic_name = st.text_input(
                        "Topic name",
                        key=(
                            f"new_topic_name_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        )
                    )


                    difficulty = st.slider(
                        "Difficulty",
                        min_value=1,
                        max_value=5,
                        value=3,
                        key=(
                            f"new_difficulty_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        )
                    )


                    importance = st.slider(
                        "Importance",
                        min_value=1,
                        max_value=5,
                        value=3,
                        key=(
                            f"new_importance_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        )
                    )


                    estimated_hours = st.number_input(
                        "Estimated study hours",
                        min_value=0.5,
                        max_value=100.0,
                        value=1.0,
                        step=0.5,
                        key=(
                            f"new_hours_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        )
                    )


                    if st.button(
                        "Add Topic",
                        key=(
                            f"add_topic_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        ),
                        width="stretch"
                    ):

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


                    # -----------------------------------------
                    # TOPICS
                    # -----------------------------------------

                    st.markdown("#### Topics")


                    if not paper["topics"]:

                        st.caption(
                            "No topics added yet."
                        )


                    else:

                        for topic_index, topic in enumerate(
                            paper["topics"]
                        ):

                            st.divider()


                            # Topic completion
                            completed = st.checkbox(
                                topic["name"],
                                value=topic["completed"],
                                key=(
                                    f"complete_"
                                    f"{subject_index}_"
                                    f"{paper_index}_"
                                    f"{topic_index}"
                                )
                            )


                            st.caption(
                                f"Difficulty "
                                f"{topic['difficulty']}/5 • "
                                f"Importance "
                                f"{topic['importance']}/5 • "
                                f"{topic['estimated_hours']}h"
                            )


                            # ---------------------------------
                            # EDIT TOPIC
                            # ---------------------------------

                            with st.expander("✏️ Edit Topic"):

                                edited_topic_name = st.text_input(
                                    "Topic name",
                                    value=topic["name"],
                                    key=(
                                        f"edit_topic_name_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    )
                                )


                                edited_difficulty = st.slider(
                                    "Difficulty",
                                    min_value=1,
                                    max_value=5,
                                    value=topic["difficulty"],
                                    key=(
                                        f"edit_difficulty_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    )
                                )


                                edited_importance = st.slider(
                                    "Importance",
                                    min_value=1,
                                    max_value=5,
                                    value=topic["importance"],
                                    key=(
                                        f"edit_importance_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    )
                                )


                                edited_hours = st.number_input(
                                    "Estimated study hours",
                                    min_value=0.5,
                                    max_value=100.0,
                                    value=float(
                                        topic["estimated_hours"]
                                    ),
                                    step=0.5,
                                    key=(
                                        f"edit_hours_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    )
                                )


                                if st.button(
                                    "Save Topic",
                                    key=(
                                        f"save_topic_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    ),
                                    width="stretch"
                                ):

                                    try:

                                        edit_topic(
                                            data,
                                            subject["name"],
                                            paper["name"],
                                            topic["name"],
                                            edited_topic_name,
                                            edited_difficulty,
                                            edited_importance,
                                            edited_hours
                                        )


                                        save_data(data)

                                        st.rerun()


                                    except ValueError as error:

                                        st.error(
                                            str(error)
                                        )


                            # ---------------------------------
                            # MOVE TOPIC
                            # ---------------------------------

                            with st.expander("↔️ Move Topic"):

                                available_papers = [
                                    other_paper["name"]
                                    for other_paper in subject["papers"]
                                    if (
                                        other_paper["name"]
                                        != paper["name"]
                                    )
                                ]


                                if not available_papers:

                                    st.caption(
                                        "No other papers available."
                                    )


                                else:

                                    target_paper = st.selectbox(
                                        "Move to",
                                        available_papers,
                                        key=(
                                            f"move_topic_"
                                            f"{subject_index}_"
                                            f"{paper_index}_"
                                            f"{topic_index}"
                                        )
                                    )


                                    if st.button(
                                        "Move Topic",
                                        key=(
                                            f"move_button_"
                                            f"{subject_index}_"
                                            f"{paper_index}_"
                                            f"{topic_index}"
                                        ),
                                        width="stretch"
                                    ):

                                        try:

                                            move_topic(
                                                data,
                                                subject["name"],
                                                paper["name"],
                                                topic["name"],
                                                target_paper
                                            )


                                            save_data(data)

                                            st.rerun()


                                        except ValueError as error:

                                            st.error(
                                                str(error)
                                            )


                            # ---------------------------------
                            # DELETE TOPIC
                            # ---------------------------------

                            if st.button(
                                "Delete Topic",
                                key=(
                                    f"delete_topic_"
                                    f"{subject_index}_"
                                    f"{paper_index}_"
                                    f"{topic_index}"
                                ),
                                width="stretch"
                            ):

                                try:

                                    delete_topic(
                                        data,
                                        subject["name"],
                                        paper["name"],
                                        topic["name"]
                                    )


                                    save_data(data)

                                    st.rerun()


                                except ValueError as error:

                                    st.error(
                                        str(error)
                                    )


                            # ---------------------------------
                            # SAVE COMPLETION
                            # ---------------------------------

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
        "Generate a schedule based on paper deadlines "
        "and remaining workload."
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


            for (
                subject_name,
                paper_name
            ), items in grouped_schedule.items():

                with st.expander(
                    f"{subject_name} — {paper_name}",
                    expanded=True
                ):

                    for item in items:

                        col1, col2 = st.columns([4, 1])


                        with col1:

                            st.markdown(
                                f"**{item['topic']}**"
                            )


                            if item["days_left"] is None:

                                exam_text = (
                                    "No exam date"
                                )

                            elif item["days_left"] == 0:

                                exam_text = "Exam today"

                            else:

                                exam_text = (
                                    f"{item['days_left']} "
                                    "days until exam"
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

            total = len(
                paper["topics"]
            )


            completed = sum(
                topic["completed"]
                for topic in paper["topics"]
            )


            remaining = (
                total - completed
            )


            hours_remaining = (
                get_paper_hours_remaining(
                    paper
                )
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
                "Paper Label": (
                    f"{subject['name']} — "
                    f"{paper['name']}"
                ),
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
            total_completed +
            total_remaining
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


        # -----------------------------------------------
        # PAPER PROGRESS
        # -----------------------------------------------

        st.subheader(
            "Paper Progress"
        )


        progress_chart = df[
            [
                "Paper Label",
                "Progress"
            ]
        ].set_index(
            "Paper Label"
        )


        st.bar_chart(
            progress_chart
        )


        # -----------------------------------------------
        # HOURS REMAINING
        # -----------------------------------------------

        st.subheader(
            "Study Hours Remaining"
        )


        hours_chart = df[
            [
                "Paper Label",
                "Hours Remaining"
            ]
        ].set_index(
            "Paper Label"
        )


        st.bar_chart(
            hours_chart
        )


        # -----------------------------------------------
        # TABLE
        # -----------------------------------------------

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


    if not data["subjects"]:

        st.info(
            "Add subjects, papers and topics "
            "before using the AI Coach."
        )


    else:

        st.write(
            "The AI Coach analyzes your papers, "
            "deadlines and unfinished topics."
        )


        if st.button(
            "Get Study Advice",
            width="stretch"
        ):

            with st.spinner(
                "Analyzing your planner..."
            ):

                try:

                    advice = get_ai_study_advice(
                        data
                    )

                    st.markdown(
                        advice
                    )

                except Exception as error:

                    st.error(
                        f"AI request failed: {error}"
                    )