"""
pages/profile.py — User Profile page for VEDA
"""

import streamlit as st
from database import get_user, get_user_stats, update_user_name, update_user_password
from auth import logout_user


def render_profile(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">👤 VEDA Profile</h1>
            <p class="header-sub-light">Manage your account profile details, security credentials, and view intelligence metrics.</p>
        </div>
    """, unsafe_allow_html=True)

    current_user = get_user(user["id"]) or user
    stats = get_user_stats(current_user["id"])

    c_info, c_security = st.columns([1, 1], gap="large")

    with c_info:
        st.markdown("""
            <div class="veda-card">
                <h3 style="margin-top:0; color:#4f46e5; font-size: 1.3rem;">Profile Details</h3>
        """, unsafe_allow_html=True)

        st.markdown(f"**Full Name:** {current_user['name']}")
        st.markdown(f"**Email Address:** {current_user['email']}")
        st.markdown(f"**Account Role:** `{current_user.get('role', 'user')}`")
        created_str = current_user['created_at'].split("T")[0] if "T" in current_user['created_at'] else current_user['created_at']
        st.markdown(f"**Member Since:** {created_str}")
        st.markdown(f"**Total Analyses:** `{stats['total']:,}` (Text: `{stats['text_count']}` | Voice: `{stats['voice_count']}`)")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### ✏️ Edit Profile Name")
        with st.form("edit_name_form_v"):
            new_name = st.text_input("Full Name", value=current_user["name"])
            save_name_btn = st.form_submit_button("Update Name", type="primary")

            if save_name_btn:
                if not new_name.strip():
                    st.error("Name cannot be empty.")
                else:
                    res = update_user_name(current_user["id"], new_name)
                    if res["success"]:
                        st.session_state["user"]["name"] = new_name.strip()
                        st.success(res["message"])
                        st.rerun()
                    else:
                        st.error(res["message"])

    with c_security:
        st.markdown("##### 🔑 Change Password")
        with st.form("change_password_form_v"):
            curr_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            save_pass_btn = st.form_submit_button("Update Password", type="primary")

            if save_pass_btn:
                if not curr_pass or not new_pass:
                    st.error("Please fill in all password fields.")
                elif new_pass != confirm_pass:
                    st.error("New passwords do not match.")
                elif len(new_pass) < 6:
                    st.error("New password must be at least 6 characters long.")
                else:
                    res = update_user_password(current_user["id"], curr_pass, new_pass)
                    if res["success"]:
                        st.success(res["message"])
                    else:
                        st.error(res["message"])

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### 🚪 Session Management")
        if st.button("Sign Out of VEDA Account", type="secondary", use_container_width=True):
            logout_user()
