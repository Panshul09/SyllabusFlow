"""Supabase client and email/password authentication for SyllabusFlow."""

from __future__ import annotations

import streamlit as st
from supabase import Client, create_client


_CLIENT_STATE_KEY = "_sf_supabase_client"
_USER_ID_KEY = "sf_user_id"
_EMAIL_KEY = "sf_email"


def get_supabase_client() -> Client:
    """Create one Supabase client per Streamlit browser session."""
    existing_client = st.session_state.get(_CLIENT_STATE_KEY)
    if existing_client is not None:
        return existing_client

    try:
        project_url = str(st.secrets["SUPABASE_URL"]).strip()
        publishable_key = str(st.secrets["SUPABASE_KEY"]).strip()
    except Exception as exc:
        st.error(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY "
            "to .streamlit/secrets.toml locally and to the app's Secrets "
            "settings on Streamlit Community Cloud."
        )
        with st.expander("Technical details"):
            st.code(str(exc))
        st.stop()

    if not project_url or not publishable_key:
        st.error("SUPABASE_URL and SUPABASE_KEY must not be blank.")
        st.stop()

    client = create_client(project_url, publishable_key)
    # Do not use st.cache_resource here: authentication is per browser session.
    st.session_state[_CLIENT_STATE_KEY] = client
    return client


def _store_signed_in_user(response) -> bool:
    """Store the authenticated user's ID after a successful sign-in."""
    user = getattr(response, "user", None)
    if user is None:
        return False

    st.session_state[_USER_ID_KEY] = str(user.id)
    st.session_state[_EMAIL_KEY] = getattr(user, "email", "") or ""
    return True


def render_login_screen() -> bool:
    """Render sign-in/sign-up and return True only for an authenticated user."""
    if st.session_state.get(_USER_ID_KEY):
        return True

    client = get_supabase_client()

    st.markdown("<div style='height: 4vh'></div>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.title("SyllabusFlow")
        st.caption("Plan. Prioritize. Progress.")
        st.write("Sign in to keep your planner private and synced across devices.")

        sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])

        with sign_in_tab:
            with st.form("sf_sign_in_form"):
                email = st.text_input("Email address", key="sf_login_email")
                password = st.text_input(
                    "Password", type="password", key="sf_login_password"
                )
                submitted = st.form_submit_button(
                    "Sign in", type="primary", use_container_width=True
                )

            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email address and password.")
                else:
                    try:
                        response = client.auth.sign_in_with_password(
                            {"email": email.strip(), "password": password}
                        )
                        if _store_signed_in_user(response):
                            st.rerun()
                        st.error("Sign-in did not return a user. Please try again.")
                    except Exception as exc:
                        st.error("Could not sign in. Check your email and password.")
                        with st.expander("Technical details"):
                            st.code(str(exc))

        with sign_up_tab:
            with st.form("sf_sign_up_form"):
                new_email = st.text_input("Email address", key="sf_signup_email")
                new_password = st.text_input(
                    "Create a password", type="password", key="sf_signup_password"
                )
                confirm_password = st.text_input(
                    "Confirm password", type="password", key="sf_signup_confirm"
                )
                sign_up_submitted = st.form_submit_button(
                    "Create account", type="primary", use_container_width=True
                )

            if sign_up_submitted:
                email_value = new_email.strip()
                if not email_value or not new_password:
                    st.error("Enter an email address and password.")
                elif new_password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        signup_credentials = {
                            "email": email_value,
                            "password": new_password,
                        }
                        # Configure a different confirmation redirect locally and
                        # on Community Cloud if desired. Both URLs must be on the
                        # Supabase Auth redirect allow list.
                        redirect_url = str(
                            st.secrets.get("AUTH_REDIRECT_URL", "")
                        ).strip()
                        if redirect_url:
                            signup_credentials["options"] = {
                                "email_redirect_to": redirect_url
                            }
                        response = client.auth.sign_up(signup_credentials)
                        session = getattr(response, "session", None)
                        if session is not None and _store_signed_in_user(response):
                            st.success("Account created. You're signed in.")
                            st.rerun()
                        else:
                            st.success(
                                "Account request received. Check your email for a "
                                "confirmation link, then return here and sign in."
                            )
                    except Exception as exc:
                        st.error("Could not create the account. Check the details and try again.")
                        with st.expander("Technical details"):
                            st.code(str(exc))

        st.caption("Each account has its own subjects, papers, and topics.")

    return False


def sign_out_user() -> None:
    """Sign out and clear this browser session's local user state."""
    client = st.session_state.get(_CLIENT_STATE_KEY)
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            # Clear the local session even if the remote session has expired.
            pass

    st.session_state.pop(_USER_ID_KEY, None)
    st.session_state.pop(_EMAIL_KEY, None)
    st.session_state.pop(_CLIENT_STATE_KEY, None)
