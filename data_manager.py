"""Cloud persistence layer for SyllabusFlow (Supabase PostgreSQL)."""

from __future__ import annotations

import streamlit as st

from supabase_client import get_supabase_client


def _get_user_context():
    user_id = st.session_state.get("sf_user_id")
    if not user_id:
        raise ValueError("Please sign in before accessing your planner.")
    return get_supabase_client(), str(user_id)


def load_data():
    """Load the current user's Supabase rows into the app's nested data shape."""
    client, user_id = _get_user_context()

    try:
        subject_result = (
            client.table("subjects")
            .select("id, name, created_at")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        subject_rows = subject_result.data or []
        if not subject_rows:
            return {"subjects": []}

        subject_ids = [row["id"] for row in subject_rows]
        papers_result = (
            client.table("papers")
            .select("id, subject_id, name, code, exam_date, created_at")
            .in_("subject_id", subject_ids)
            .order("created_at")
            .execute()
        )
        paper_rows = papers_result.data or []

        topic_rows = []
        paper_ids = [row["id"] for row in paper_rows]
        if paper_ids:
            topics_result = (
                client.table("topics")
                .select(
                    "paper_id, name, difficulty, importance, "
                    "estimated_hours, completed, created_at"
                )
                .in_("paper_id", paper_ids)
                .order("created_at")
                .execute()
            )
            topic_rows = topics_result.data or []

        data_subjects = []
        subject_by_id = {}
        for row in subject_rows:
            item = {"name": row["name"], "papers": []}
            data_subjects.append(item)
            subject_by_id[row["id"]] = item

        paper_by_id = {}
        for row in paper_rows:
            paper = {
                "name": row["name"],
                "code": row.get("code") or "",
                "exam_date": row.get("exam_date"),
                "topics": [],
            }
            subject_by_id[row["subject_id"]]["papers"].append(paper)
            paper_by_id[row["id"]] = paper

        for row in topic_rows:
            paper = paper_by_id[row["paper_id"]]
            paper["topics"].append(
                {
                    "name": row["name"],
                    "difficulty": int(row["difficulty"]),
                    "importance": int(row["importance"]),
                    "estimated_hours": float(row["estimated_hours"]),
                    "completed": bool(row["completed"]),
                }
            )

        return {"subjects": data_subjects}

    except Exception as exc:
        raise RuntimeError(
            "Couldn't load your planner from Supabase. Check the database "
            "grants, RLS policies, Data API exposure, and SQL function setup. "
            f"Details: {exc}"
        ) from exc


def save_data(data):
    """Atomically replace the current user's nested planner using a SQL RPC."""
    client, _user_id = _get_user_context()

    try:
        client.rpc(
            "replace_my_planner",
            {"p_subjects": data.get("subjects", [])},
        ).execute()
    except Exception as exc:
        raise ValueError(
            "Couldn't save your planner to Supabase. Your last change may not "
            "have been saved. Check that replace_my_planner was installed and "
            "that the authenticated role has the required grants. "
            f"Details: {exc}"
        ) from exc
