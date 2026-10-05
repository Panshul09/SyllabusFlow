from datetime import date
from pathlib import Path
import base64
import html

import pandas as pd
import streamlit as st

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
    move_topic,
)

from scheduler import generate_schedule
from ai_helper import get_ai_study_advice


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SyllabusFlow",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.html(
    """
<style>
:root {
    --sf-primary: #6D5EF6;
    --sf-primary-light: #EEF0FF;
    --sf-bg: #F7F8FC;
    --sf-card: #FFFFFF;
    --sf-border: #E8EAF2;
    --sf-text: #18213A;
    --sf-muted: #7B8398;
    --sf-green: #46C58C;
    --sf-orange: #F5A340;
    --sf-blue: #4EA5FF;
    --sf-purple: #6D5EF6;
}


/* =========================================================
   MAIN APP
========================================================= */

.stApp {
    background: var(--sf-bg);
}

.block-container {
    max-width: 1480px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    width: 225px;
    min-width: 225px;
    max-width: 225px;
}

[data-testid="stSidebar"] > div:first-child {
    background: #FFFFFF;
    border-right: 1px solid var(--sf-border);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}


/* Sidebar logo */

.sf-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 5px 18px 5px;
}

.sf-sidebar-logo {
    width: 38px;
    height: 38px;
    border-radius: 11px;
}

.sf-sidebar-name {
    color: var(--sf-text);
    font-size: 1.02rem;
    font-weight: 750;
    line-height: 1.1;
}

.sf-sidebar-tagline {
    color: var(--sf-muted);
    font-size: 0.68rem;
    margin-top: 3px;
}


/* Navigation */

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 4px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 11px;
    padding: 8px 10px;
    color: #5F6880;
    transition:
        background-color 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #F5F6FA;
    transform: translateX(2px);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: var(--sf-primary-light);
    color: var(--sf-primary);
    font-weight: 650;
}


/* =========================================================
   PAGE ANIMATION
========================================================= */

@keyframes sfPageEnter {
    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

[data-testid="stAppViewContainer"] .main .block-container {
    animation: sfPageEnter 0.35s ease-out;
}


/* =========================================================
   PAGE HEADER
========================================================= */

.sf-kicker {
    color: var(--sf-primary);
    font-size: 0.73rem;
    font-weight: 750;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.sf-page-title {
    color: var(--sf-text);
    font-size: 2.05rem;
    font-weight: 760;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 5px;
}

.sf-page-subtitle {
    color: var(--sf-muted);
    font-size: 0.94rem;
    margin-bottom: 24px;
}


/* =========================================================
   CUSTOM METRIC CARDS
========================================================= */

.sf-metric-card {
    background: var(--sf-card);
    border: 1px solid var(--sf-border);
    border-radius: 16px;
    padding: 17px;
    min-height: 116px;
    box-shadow: 0 5px 20px rgba(28, 35, 56, 0.035);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.sf-metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(28, 35, 56, 0.08);
}

.sf-metric-icon {
    width: 34px;
    height: 34px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 11px;
    font-size: 17px;
    font-weight: 700;
}

.sf-icon-purple {
    background: #EEEAFE;
    color: #6D5EF6;
}

.sf-icon-blue {
    background: #E9F4FF;
    color: #4EA5FF;
}

.sf-icon-green {
    background: #EAF8F1;
    color: #46C58C;
}

.sf-icon-orange {
    background: #FFF2E2;
    color: #F5A340;
}

.sf-metric-label {
    color: var(--sf-muted);
    font-size: 0.75rem;
}

.sf-metric-value {
    color: var(--sf-text);
    font-size: 1.55rem;
    font-weight: 760;
    margin-top: 2px;
}


/* =========================================================
   CARD
========================================================= */

.sf-card {
    background: var(--sf-card);
    border: 1px solid var(--sf-border);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 5px 20px rgba(28, 35, 56, 0.035);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.sf-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 9px 25px rgba(28, 35, 56, 0.065);
}

.sf-card-title {
    color: var(--sf-text);
    font-size: 0.96rem;
    font-weight: 700;
}

.sf-card-muted {
    color: var(--sf-muted);
    font-size: 0.76rem;
}

.sf-card-value {
    color: var(--sf-text);
    font-size: 1.5rem;
    font-weight: 760;
    margin-top: 8px;
}


/* =========================================================
   PROGRESS BAR
========================================================= */

.sf-progress {
    width: 100%;
    height: 8px;
    background: #EDEFF6;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 9px;
}

.sf-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(
        90deg,
        #6D5EF6 0%,
        #7C6AF8 55%,
        #8F7EFA 100%
    );
    transition: width 0.45s ease;
}


/* =========================================================
   EXAM BADGE
========================================================= */

.sf-badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 0.69rem;
    font-weight: 700;
    margin-top: 9px;
    background: #EEF0FF;
    color: var(--sf-primary);
}

.sf-badge-today {
    background: #FFF0EA;
    color: #E76D35;
}


/* =========================================================
   PAPER MINI CARD
========================================================= */

.sf-paper {
    background: #FCFCFE;
    border: 1px solid #ECEEF5;
    border-radius: 12px;
    padding: 11px;
    transition:
        transform 0.18s ease,
        background 0.18s ease;
}

.sf-paper:hover {
    background: #F8F8FD;
    transform: translateY(-1px);
}


/* =========================================================
   MOTIVATION CARD
========================================================= */

.sf-motivation {
    border-radius: 18px;
    padding: 22px;
    min-height: 180px;
    color: white;
    background:
        linear-gradient(
            135deg,
            #5547C8 0%,
            #7768E8 55%,
            #8A6FD8 100%
        );
    box-shadow: 0 12px 32px rgba(93, 78, 214, 0.2);
}

.sf-motivation-title {
    font-size: 1.24rem;
    font-weight: 760;
    line-height: 1.15;
}

.sf-motivation-text {
    font-size: 0.82rem;
    line-height: 1.55;
    opacity: 0.88;
    margin-top: 10px;
}


/* =========================================================
   QUICK STATS
========================================================= */

.sf-quick-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid #EEF0F5;
}

.sf-quick-row:last-child {
    border-bottom: none;
}

.sf-quick-label {
    color: var(--sf-muted);
    font-size: 0.76rem;
}

.sf-quick-value {
    color: var(--sf-text);
    font-size: 0.86rem;
    font-weight: 700;
}


/* =========================================================
   AI CARD
========================================================= */

.sf-ai-card {
    background: linear-gradient(
        135deg,
        #F0EEFF 0%,
        #F8F6FF 100%
    );
    border: 1px solid #E4E0FF;
    border-radius: 16px;
    padding: 17px;
}

.sf-ai-title {
    color: #5547C8;
    font-size: 0.96rem;
    font-weight: 750;
}

.sf-ai-text {
    color: #70768A;
    font-size: 0.78rem;
    line-height: 1.5;
    margin-top: 5px;
}


/* =========================================================
   STREAMLIT INPUTS
========================================================= */

/* Text inputs */
[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #18213A !important;
    -webkit-text-fill-color: #18213A !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #9AA2B5 !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #6D5EF6 !important;
    box-shadow: 0 0 0 1px #6D5EF6 !important;
    outline: none !important;
}


/* Number inputs */
[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #18213A !important;
    -webkit-text-fill-color: #18213A !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

[data-testid="stNumberInput"] input:focus {
    border-color: #6D5EF6 !important;
    box-shadow: 0 0 0 1px #6D5EF6 !important;
    outline: none !important;
}


/* Date inputs */
[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #18213A !important;
    -webkit-text-fill-color: #18213A !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

[data-testid="stDateInput"] input:focus {
    border-color: #6D5EF6 !important;
    box-shadow: 0 0 0 1px #6D5EF6 !important;
    outline: none !important;
}

[data-testid="stDateInput"] [data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
}


/* Select boxes */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #18213A !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

[data-testid="stSelectbox"] [role="combobox"] {
    color: #18213A !important;
}


/* Text areas */
[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #18213A !important;
    -webkit-text-fill-color: #18213A !important;
    border: 1px solid #D9DEEA !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: #6D5EF6 !important;
    box-shadow: 0 0 0 1px #6D5EF6 !important;
    outline: none !important;
}


/* =========================================================
   BUTTONS
========================================================= */

div.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #DEE1EA !important;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        background-color 0.18s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(28, 35, 56, 0.08);
}


/* =========================================================
   EXPANDERS
========================================================= */

[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid var(--sf-border);
    border-radius: 13px;
    overflow: hidden;
    margin-bottom: 9px;
}


/* =========================================================
   DIVIDERS
========================================================= */

hr {
    border-color: #ECEEF4;
}


/* =========================================================
   DATAFRAME
========================================================= */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 900px) {

    [data-testid="stSidebar"] {
        width: 210px;
        min-width: 210px;
        max-width: 210px;
    }

    .block-container {
        padding-top: 1.3rem;
    }
}

</style>
"""
)


# =========================================================
# LOAD DATA
# =========================================================

data = load_data()


# =========================================================
# LOGO
# =========================================================

logo_path = (
    Path(__file__).parent
    / "assets"
    / "logo.svg"
)


def get_logo_data():
    if not logo_path.exists():
        return None

    return base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")


logo_data = get_logo_data()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe(value):
    return html.escape(str(value or ""))


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

    days_left = (
        exam - date.today()
    ).days

    if days_left > 0:
        return f"{days_left} days left", days_left

    if days_left == 0:
        return "Exam today", 0

    return "Exam completed", days_left


def get_overall_stats(data):
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
        progress,
    )


def progress_html(progress):
    percent = max(
        0,
        min(
            100,
            progress * 100
        )
    )

    return (
        '<div class="sf-progress">'
        f'<div class="sf-progress-fill" '
        f'style="width:{percent:.1f}%"></div>'
        '</div>'
    )


def render_header(kicker, title, subtitle):
    st.html(
        f"""
<div>
    <div class="sf-kicker">{safe(kicker)}</div>
    <div class="sf-page-title">{safe(title)}</div>
    <div class="sf-page-subtitle">{safe(subtitle)}</div>
</div>
"""
    )


# =========================================================
# SIDEBAR
# =========================================================

if logo_data:

    st.sidebar.html(
        f"""
<div class="sf-sidebar-brand">
    <img
        src="data:image/svg+xml;base64,{logo_data}"
        class="sf-sidebar-logo"
    >
    <div>
        <div class="sf-sidebar-name">SyllabusFlow</div>
        <div class="sf-sidebar-tagline">
            Plan. Prioritize. Progress.
        </div>
    </div>
</div>
"""
    )

else:

    st.sidebar.markdown(
        "### SyllabusFlow"
    )

    st.sidebar.caption(
        "Plan. Prioritize. Progress."
    )


page_label = st.sidebar.radio(
    "Navigation",
    [
        "⌂  Dashboard",
        "▦  Subjects",
        "◷  Schedule",
        "◒  Analytics",
        "✦  AI Coach",
    ],
    label_visibility="collapsed",
)


page_map = {
    "⌂  Dashboard": "Dashboard",
    "▦  Subjects": "Subjects",
    "◷  Schedule": "Schedule",
    "◒  Analytics": "Analytics",
    "✦  AI Coach": "AI Coach",
}


page = page_map[page_label]


st.sidebar.divider()

st.sidebar.caption(
    f"Today · {date.today().strftime('%d %b %Y')}"
)

st.sidebar.caption(
    "SyllabusFlow v1.0"
)


# =========================================================
# GLOBAL STATS
# =========================================================

(
    total_papers,
    total_topics,
    completed_topics,
    overall_progress,
) = get_overall_stats(data)


remaining_topics = (
    total_topics - completed_topics
)


total_hours_remaining = sum(
    get_paper_hours_remaining(paper)
    for subject in data["subjects"]
    for paper in subject["papers"]
)


upcoming_paper_count = 0

for subject in data["subjects"]:

    for paper in subject["papers"]:

        status, days_left = get_exam_status(
            paper["exam_date"]
        )

        if days_left is not None and days_left >= 0:
            upcoming_paper_count += 1


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    render_header(
        "OVERVIEW",
        "Your study command center",
        "Everything important, without the clutter.",
    )


    # -----------------------------------------------------
    # TOP METRICS
    # -----------------------------------------------------

    metric_columns = st.columns(4)


    metric_data = [
        (
            metric_columns[0],
            "sf-icon-purple",
            "▦",
            "Subjects",
            len(data["subjects"]),
        ),
        (
            metric_columns[1],
            "sf-icon-blue",
            "▤",
            "Papers",
            total_papers,
        ),
        (
            metric_columns[2],
            "sf-icon-green",
            "✓",
            "Topics Completed",
            f"{completed_topics}/{total_topics}",
        ),
        (
            metric_columns[3],
            "sf-icon-purple",
            "◔",
            "Overall Progress",
            f"{overall_progress * 100:.0f}%",
        ),
    ]


    for (
        column,
        icon_class,
        icon,
        label,
        value,
    ) in metric_data:

        with column:

            st.html(
                f"""
<div class="sf-metric-card">
    <div class="sf-metric-icon {icon_class}">
        {safe(icon)}
    </div>
    <div class="sf-metric-label">
        {safe(label)}
    </div>
    <div class="sf-metric-value">
        {safe(value)}
    </div>
</div>
"""
            )


    st.write("")


    # -----------------------------------------------------
    # OVERALL PROGRESS
    # -----------------------------------------------------

    st.html(
        f"""
<div class="sf-card">
    <div style="display:flex;
                justify-content:space-between;
                align-items:center;">
        <div>
            <div class="sf-card-title">
                Overall Progress
            </div>
            <div class="sf-card-muted">
                Keep building momentum across every paper.
            </div>
        </div>

        <div class="sf-card-value">
            {overall_progress * 100:.0f}%
        </div>
    </div>

    {progress_html(overall_progress)}
</div>
"""
    )


    st.write("")


    # -----------------------------------------------------
    # MAIN + SIDE CONTENT
    # -----------------------------------------------------

    main_column, side_column = st.columns(
        [2.15, 1]
    )


    with main_column:

        # -----------------------------------------------
        # UPCOMING PAPERS
        # -----------------------------------------------

        st.subheader(
            "Upcoming Papers"
        )


        upcoming_papers = []


        for subject in data["subjects"]:

            for paper in subject["papers"]:

                status, days_left = get_exam_status(
                    paper["exam_date"]
                )

                if days_left is None:
                    continue

                if days_left < 0:
                    continue

                upcoming_papers.append(
                    {
                        "subject": subject["name"],
                        "paper": paper["name"],
                        "code": paper["code"],
                        "date": paper["exam_date"],
                        "days": days_left,
                    }
                )


        upcoming_papers.sort(
            key=lambda item: item["date"]
        )


        if not upcoming_papers:

            st.info(
                "No upcoming papers."
            )

        else:

            exam_columns = st.columns(
                min(
                    len(upcoming_papers[:4]),
                    4
                )
            )


            for column, paper in zip(
                exam_columns,
                upcoming_papers[:4]
            ):

                with column:

                    if paper["days"] == 0:

                        badge_class = (
                            "sf-badge sf-badge-today"
                        )

                        badge_text = "Exam today"

                        value_text = "TODAY"

                    else:

                        badge_class = "sf-badge"

                        badge_text = (
                            f"{paper['days']} days left"
                        )

                        value_text = (
                            f"{paper['days']}"
                        )


                    st.html(
                        f"""
<div class="sf-card">
    <div class="sf-card-muted">
        {safe(paper['subject'])}
    </div>

    <div class="sf-card-title">
        {safe(paper['paper'])}
    </div>

    <div class="sf-card-value">
        {value_text}
    </div>

    <div class="sf-card-muted">
        {safe(paper['date'])}
    </div>

    <div class="{badge_class}">
        {safe(badge_text)}
    </div>
</div>
"""
                    )


        st.write("")


        # -----------------------------------------------
        # SUBJECT OVERVIEW
        # -----------------------------------------------

        st.subheader(
            "Your Subjects"
        )


        for subject in data["subjects"]:

            subject_progress = (
                get_subject_progress(
                    subject
                )
            )


            st.html(
                f"""
<div class="sf-card">
    <div style="display:flex;
                justify-content:space-between;
                align-items:center;">

        <div class="sf-card-title">
            {safe(subject['name'])}
        </div>

        <div class="sf-card-muted">
            {subject_progress * 100:.0f}%
        </div>
    </div>

    {progress_html(subject_progress)}
</div>
"""
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

                    paper_progress = (
                        calculate_progress(
                            paper
                        )
                    )

                    hours_remaining = (
                        get_paper_hours_remaining(
                            paper
                        )
                    )

                    status, days_left = (
                        get_exam_status(
                            paper["exam_date"]
                        )
                    )


                    if days_left is None:

                        exam_line = "No exam date"

                    elif days_left == 0:

                        exam_line = "Exam today"

                    elif days_left > 0:

                        exam_line = (
                            f"{days_left} days left"
                        )

                    else:

                        exam_line = "Exam completed"


                    st.html(
                        f"""
<div class="sf-paper">

    <div class="sf-card-title">
        {safe(paper['name'])}
    </div>

    <div class="sf-card-muted">
        {
            safe(paper['code'])
            if paper['code']
            else 'Paper'
        }
    </div>

    {progress_html(paper_progress)}

    <div class="sf-card-muted"
         style="margin-top:8px;">
        {paper_progress * 100:.0f}% complete
        · {hours_remaining:.1f}h left
    </div>

    <div class="sf-card-muted"
         style="margin-top:4px;">
        {safe(exam_line)}
    </div>

</div>
"""
                    )


    with side_column:

        # -----------------------------------------------
        # MOTIVATION
        # -----------------------------------------------

        st.html(
            """
<div class="sf-motivation">
    <div class="sf-motivation-title">
        Progress over perfection.
    </div>

    <div class="sf-motivation-text">
        You're not just studying.
        You're building a system that helps
        you study consistently.
    </div>
</div>
"""
        )


        st.write("")


        # -----------------------------------------------
        # QUICK STATS
        # -----------------------------------------------

        st.html(
            f"""
<div class="sf-card">

    <div class="sf-card-title">
        Quick Stats
    </div>

    <div class="sf-quick-row">
        <div class="sf-quick-label">
            Study hours remaining
        </div>

        <div class="sf-quick-value">
            {total_hours_remaining:.1f}h
        </div>
    </div>

    <div class="sf-quick-row">
        <div class="sf-quick-label">
            Topics completed
        </div>

        <div class="sf-quick-value">
            {completed_topics}
        </div>
    </div>

    <div class="sf-quick-row">
        <div class="sf-quick-label">
            Topics remaining
        </div>

        <div class="sf-quick-value">
            {remaining_topics}
        </div>
    </div>

    <div class="sf-quick-row">
        <div class="sf-quick-label">
            Upcoming papers
        </div>

        <div class="sf-quick-value">
            {upcoming_paper_count}
        </div>
    </div>

</div>
"""
        )


        st.write("")


        # -----------------------------------------------
        # AI CARD
        # -----------------------------------------------

        st.html(
            """
<div class="sf-ai-card">

    <div class="sf-ai-title">
        ✦ AI Study Coach
    </div>

    <div class="sf-ai-text">
        Get recommendations based on your
        papers, deadlines and unfinished topics.
    </div>

</div>
"""
        )


# =========================================================
# SUBJECTS
# =========================================================

if page == "Subjects":

    render_header(
        "MANAGE",
        "Subjects & papers",
        "Build your syllabus exactly the way you study it.",
    )


    with st.expander(
        "＋  Add Subject"
    ):

        subject_name = st.text_input(
            "Subject name",
            key="new_subject_name",
        )


        if st.button(
            "Add Subject",
            key="add_subject_button",
            width="stretch",
        ):

            try:

                add_subject(
                    data,
                    subject_name,
                )

                save_data(data)

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )


    st.subheader(
        "My Subjects"
    )


    for subject_index, subject in enumerate(
        data["subjects"]
    ):

        subject_progress = (
            get_subject_progress(
                subject
            )
        )


        with st.expander(
            f"{subject['name']} · "
            f"{subject_progress * 100:.0f}%"
        ):

            st.html(
                f"""
<div class="sf-card">
    <div class="sf-card-title">
        {safe(subject['name'])}
    </div>

    <div class="sf-card-muted">
        {len(subject['papers'])} papers
    </div>

    {progress_html(subject_progress)}
</div>
"""
            )


            # -------------------------------------------------
            # EDIT SUBJECT
            # -------------------------------------------------

            with st.expander(
                "✎ Edit Subject"
            ):

                edited_subject_name = st.text_input(
                    "Subject name",
                    value=subject["name"],
                    key=(
                        f"edit_subject_"
                        f"{subject_index}"
                    ),
                )


                if st.button(
                    "Save Subject",
                    key=(
                        f"save_subject_"
                        f"{subject_index}"
                    ),
                    width="stretch",
                ):

                    try:

                        edit_subject(
                            data,
                            subject["name"],
                            edited_subject_name,
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
                "will also delete its papers and topics.",
                key=(
                    f"confirm_delete_subject_"
                    f"{subject_index}"
                ),
            )


            if st.button(
                "Delete Subject",
                key=(
                    f"delete_subject_"
                    f"{subject_index}"
                ),
                disabled=not delete_subject_confirm,
                width="stretch",
            ):

                try:

                    delete_subject(
                        data,
                        subject["name"],
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

            st.markdown(
                "#### Add Paper"
            )


            paper_name = st.text_input(
                "Paper name",
                key=(
                    f"new_paper_name_"
                    f"{subject_index}"
                ),
            )


            paper_code = st.text_input(
                "Paper code (optional)",
                key=(
                    f"new_paper_code_"
                    f"{subject_index}"
                ),
            )


            has_exam_date = st.checkbox(
                "Set an exam date",
                key=(
                    f"new_paper_has_date_"
                    f"{subject_index}"
                ),
            )


            paper_exam_date = st.date_input(
                "Exam date",
                value=date.today(),
                disabled=not has_exam_date,
                key=(
                    f"new_paper_date_"
                    f"{subject_index}"
                ),
            )


            if st.button(
                "Add Paper",
                key=(
                    f"add_paper_"
                    f"{subject_index}"
                ),
                width="stretch",
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
                        paper_code,
                    )


                    save_data(data)

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

                paper_progress = (
                    calculate_progress(
                        paper
                    )
                )


                with st.expander(
                    f"{paper['name']} · "
                    f"{paper_progress * 100:.0f}%"
                ):

                    status, days_left = (
                        get_exam_status(
                            paper["exam_date"]
                        )
                    )


                    st.html(
                        f"""
<div class="sf-card">

    <div class="sf-card-title">
        {safe(paper['name'])}
    </div>

    <div class="sf-card-muted">
        {
            safe(paper['code'])
            if paper['code']
            else 'No paper code'
        }
    </div>

    {progress_html(paper_progress)}

    <div class="sf-card-muted"
         style="margin-top:8px;">
        {paper_progress * 100:.0f}% complete
        · {get_paper_hours_remaining(paper):.1f}h remaining
    </div>

</div>
"""
                    )


                    # Paper status

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
                            f"{paper['exam_date']} · "
                            f"{days_left} days left"
                        )

                    else:

                        st.caption(
                            f"{paper['exam_date']} · "
                            "Exam completed"
                        )


                    # -----------------------------------------
                    # EDIT PAPER
                    # -----------------------------------------

                    with st.expander(
                        "✎ Edit Paper"
                    ):

                        edited_paper_name = st.text_input(
                            "Paper name",
                            value=paper["name"],
                            key=(
                                f"edit_paper_name_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
                        )


                        edited_paper_code = st.text_input(
                            "Paper code",
                            value=paper["code"],
                            key=(
                                f"edit_paper_code_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
                        )


                        edit_has_exam_date = st.checkbox(
                            "Set an exam date",
                            value=(
                                paper["exam_date"]
                                is not None
                            ),
                            key=(
                                f"edit_has_date_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
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
                                f"edit_date_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
                        )


                        if st.button(
                            "Save Paper",
                            key=(
                                f"save_paper_"
                                f"{subject_index}_"
                                f"{paper_index}"
                            ),
                            width="stretch",
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
                                    new_exam_date,
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
                        ),
                    )


                    if st.button(
                        "Delete Paper",
                        key=(
                            f"delete_paper_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        ),
                        disabled=not delete_paper_confirm,
                        width="stretch",
                    ):

                        try:

                            delete_paper(
                                data,
                                subject["name"],
                                paper["name"],
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

                    st.markdown(
                        "#### Add Topic"
                    )


                    topic_name = st.text_input(
                        "Topic name",
                        key=(
                            f"new_topic_name_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        ),
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
                        ),
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
                        ),
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
                        ),
                    )


                    if st.button(
                        "Add Topic",
                        key=(
                            f"add_topic_"
                            f"{subject_index}_"
                            f"{paper_index}"
                        ),
                        width="stretch",
                    ):

                        try:

                            add_topic(
                                data,
                                subject["name"],
                                paper["name"],
                                topic_name,
                                difficulty,
                                importance,
                                estimated_hours,
                            )


                            save_data(data)

                            st.rerun()


                        except ValueError as error:

                            st.error(
                                str(error)
                            )


                    # -----------------------------------------
                    # TOPICS
                    # -----------------------------------------

                    st.markdown(
                        "#### Topics"
                    )


                    if not paper["topics"]:

                        st.caption(
                            "No topics added yet."
                        )


                    else:

                        for topic_index, topic in enumerate(
                            paper["topics"]
                        ):

                            st.divider()


                            completed = st.checkbox(
                                topic["name"],
                                value=topic["completed"],
                                key=(
                                    f"complete_"
                                    f"{subject_index}_"
                                    f"{paper_index}_"
                                    f"{topic_index}"
                                ),
                            )


                            st.caption(
                                f"Difficulty "
                                f"{topic['difficulty']}/5 · "
                                f"Importance "
                                f"{topic['importance']}/5 · "
                                f"{topic['estimated_hours']}h"
                            )


                            # EDIT TOPIC

                            with st.expander(
                                "✎ Edit Topic"
                            ):

                                edited_topic_name = st.text_input(
                                    "Topic name",
                                    value=topic["name"],
                                    key=(
                                        f"edit_topic_name_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    ),
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
                                    ),
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
                                    ),
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
                                    ),
                                )


                                if st.button(
                                    "Save Topic",
                                    key=(
                                        f"save_topic_"
                                        f"{subject_index}_"
                                        f"{paper_index}_"
                                        f"{topic_index}"
                                    ),
                                    width="stretch",
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
                                            edited_hours,
                                        )


                                        save_data(data)

                                        st.rerun()


                                    except ValueError as error:

                                        st.error(
                                            str(error)
                                        )


                            # MOVE TOPIC

                            with st.expander(
                                "↔ Move Topic"
                            ):

                                available_papers = [
                                    other_paper["name"]
                                    for other_paper
                                    in subject["papers"]
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
                                        ),
                                    )


                                    if st.button(
                                        "Move Topic",
                                        key=(
                                            f"move_button_"
                                            f"{subject_index}_"
                                            f"{paper_index}_"
                                            f"{topic_index}"
                                        ),
                                        width="stretch",
                                    ):

                                        try:

                                            move_topic(
                                                data,
                                                subject["name"],
                                                paper["name"],
                                                topic["name"],
                                                target_paper,
                                            )


                                            save_data(data)

                                            st.rerun()


                                        except ValueError as error:

                                            st.error(
                                                str(error)
                                            )


                            # DELETE TOPIC

                            if st.button(
                                "Delete Topic",
                                key=(
                                    f"delete_topic_"
                                    f"{subject_index}_"
                                    f"{paper_index}_"
                                    f"{topic_index}"
                                ),
                                width="stretch",
                            ):

                                try:

                                    delete_topic(
                                        data,
                                        subject["name"],
                                        paper["name"],
                                        topic["name"],
                                    )


                                    save_data(data)

                                    st.rerun()


                                except ValueError as error:

                                    st.error(
                                        str(error)
                                    )


                            # COMPLETION

                            if completed != topic["completed"]:

                                set_topic_completed(
                                    data,
                                    subject["name"],
                                    paper["name"],
                                    topic["name"],
                                    completed,
                                )

                                save_data(data)

                                st.rerun()


# =========================================================
# SCHEDULE
# =========================================================

if page == "Schedule":

    render_header(
        "PLAN",
        "Study schedule",
        "Turn paper deadlines and workload into your next study session.",
    )


    col1, col2 = st.columns(
        [2.2, 1]
    )


    with col1:

        available_hours = st.number_input(
            "Study hours available today",
            min_value=0.5,
            max_value=24.0,
            value=4.0,
            step=0.5,
        )


    with col2:

        st.write("")

        generate = st.button(
            "Generate Schedule",
            width="stretch",
        )


    if generate:

        schedule = generate_schedule(
            data,
            available_hours,
        )


        if not schedule:

            st.info(
                "No eligible incomplete topics are available."
            )


        else:

            st.subheader(
                "Your Plan"
            )


            grouped_schedule = {}


            for item in schedule:

                key = (
                    item["subject"],
                    item["paper"],
                )

                grouped_schedule.setdefault(
                    key,
                    [],
                ).append(item)


            for (
                subject_name,
                paper_name,
            ), items in grouped_schedule.items():

                st.html(
                    f"""
<div class="sf-card"
     style="margin-bottom:10px;">
    <div class="sf-card-title">
        {safe(subject_name)} · {safe(paper_name)}
    </div>
</div>
"""
                )


                for item in items:

                    with st.container(
                        border=True
                    ):

                        col1, col2 = st.columns(
                            [4, 1]
                        )


                        with col1:

                            st.markdown(
                                f"**{item['topic']}**"
                            )


                            if item["days_left"] is None:

                                exam_text = (
                                    "No exam date"
                                )

                            elif item["days_left"] == 0:

                                exam_text = (
                                    "Exam today"
                                )

                            else:

                                exam_text = (
                                    f"{item['days_left']} "
                                    "days until exam"
                                )


                            st.caption(
                                f"Priority "
                                f"{item['priority']:.2f} · "
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

    render_header(
        "INSIGHTS",
        "Analytics",
        "See where your progress and remaining workload are concentrated.",
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


            status, days_left = (
                get_exam_status(
                    paper["exam_date"]
                )
            )


            analytics_data.append(
                {
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
                    "Exam Status": status,
                }
            )


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


        total_analytics_topics = (
            total_completed +
            total_remaining
        )


        analytics_progress = (
            total_completed /
            total_analytics_topics
            if total_analytics_topics > 0
            else 0
        )


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
                "Progress",
            ]
        ].set_index(
            "Paper Label"
        )


        st.bar_chart(
            progress_chart
        )


        st.subheader(
            "Study Hours Remaining"
        )


        hours_chart = df[
            [
                "Paper Label",
                "Hours Remaining",
            ]
        ].set_index(
            "Paper Label"
        )


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
                    "Exam Status",
                ]
            ],
            width="stretch",
            hide_index=True,
        )


# =========================================================
# AI COACH
# =========================================================

if page == "AI Coach":

    render_header(
        "AI",
        "AI Study Coach",
        "Get recommendations based on your subjects, papers, deadlines and unfinished work.",
    )


    if not data["subjects"]:

        st.info(
            "Add subjects, papers and topics first."
        )


    else:

        st.html(
            """
<div class="sf-ai-card">

    <div class="sf-ai-title">
        ✦ Smart assistance
    </div>

    <div class="sf-ai-text">
        Your scheduler remains your own algorithm.
        The AI Coach analyzes your current planner
        and provides additional study advice.
    </div>

</div>
"""
        )


        st.write("")


        if st.button(
            "✦ Get Study Advice",
            width="stretch",
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


        st.caption(
            "AI usage requires an API account "
            "with available credits."
        )