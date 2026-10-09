"""
app.py — Main Application Entry Point & Router for VEDA (Voice, Emotion & Data Analytics)
"""

import os
import streamlit as st

# Set Streamlit page configuration as the very first command
st.set_page_config(
    page_title="VEDA — Voice, Emotion & Data Analytics",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Light Theme CSS stylesheet
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database tables & migrations
from database import init_db
init_db()

# Import authentication and views
from auth import init_auth_session, render_auth_page, logout_user
from pages.dashboard import render_dashboard
from pages.analyze import render_analyze
from pages.voice_analysis import render_voice_analysis
from pages.compare import render_compare
from pages.batch import render_batch
from pages.analytics import render_analytics
from pages.history import render_history
from pages.profile import render_profile
from pages.settings import render_settings


def main():
    init_auth_session()

    if not st.session_state.get("authenticated", False):
        render_auth_page()
        return

    user = st.session_state["user"]

    with st.sidebar:
        st.markdown("""
            <div style="padding: 12px 4px 16px 4px;">
                <div style="font-size: 1.85rem; font-weight: 800; color: #4f46e5; letter-spacing: -0.03em;">
                    🎙️💬 VEDA
                </div>
                <div style="font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;">
                    Voice, Emotion & Data Analytics
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        nav_options = {
            "Dashboard": "🏠 Dashboard",
            "Text Analysis": "💬 Text Analysis",
            "Voice Intelligence": "🎙️ Voice Intelligence",
            "Compare Models": "🤖 Compare Models",
            "Batch Analysis": "📂 Batch Analysis",
            "Analytics": "📊 Analytics",
            "History": "🕘 History",
            "Profile": "👤 Profile",
            "Settings": "⚙️ Settings",
        }

        current_page = st.session_state.get("page", "Dashboard")
        if current_page not in nav_options:
            current_page = "Dashboard"

        for page_key, page_label in nav_options.items():
            btn_type = "primary" if current_page == page_key else "secondary"
            if st.button(page_label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state["page"] = page_key
                st.rerun()

        st.markdown("---")
        st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-top: 16px;">
                <div style="font-weight: 700; color: #0f172a; font-size: 0.88rem;">👤 {user['name']}</div>
                <div style="color: #64748b; font-size: 0.78rem; word-break: break-all;">{user['email']}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
            logout_user()

    active_page = st.session_state.get("page", "Dashboard")

    if active_page == "Dashboard":
        render_dashboard(user)
    elif active_page == "Text Analysis":
        render_analyze(user)
    elif active_page == "Voice Intelligence":
        render_voice_analysis(user)
    elif active_page == "Compare Models":
        render_compare(user)
    elif active_page == "Batch Analysis":
        render_batch(user)
    elif active_page == "Analytics":
        render_analytics(user)
    elif active_page == "History":
        render_history(user)
    elif active_page == "Profile":
        render_profile(user)
    elif active_page == "Settings":
        render_settings(user)
    else:
        render_dashboard(user)


if __name__ == "__main__":
    main()
