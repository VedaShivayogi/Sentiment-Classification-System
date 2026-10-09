"""
auth.py — Authentication module for VEDA (Voice, Emotion & Data Analytics)
"""

import streamlit as st
from database import authenticate_user, create_user, email_exists, update_user_password


def init_auth_session():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    if "page" not in st.session_state:
        st.session_state["page"] = "Dashboard"


def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["page"] = "Dashboard"
    st.rerun()


def render_auth_page():
    init_auth_session()

    st.markdown("""
        <style>
        .auth-hero-v {
            background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%);
            border-radius: 20px;
            padding: 40px;
            color: #ffffff;
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.2);
            margin-bottom: 20px;
        }
        .auth-brand-v {
            font-size: 2.8rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.03em;
            margin-bottom: 4px;
        }
        .auth-sub-v {
            font-size: 0.95rem;
            color: #c7d2fe;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 16px;
        }
        .auth-tagline-v {
            font-size: 1.1rem;
            color: #e0e7ff;
            line-height: 1.5;
            margin-bottom: 24px;
        }
        .auth-pill-v {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #ffffff;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        st.markdown("""
            <div class="auth-hero-v">
                <div style="font-size: 3.2rem; margin-bottom: 8px;">🎙️💬</div>
                <div class="auth-brand-v">VEDA</div>
                <div class="auth-sub-v">Voice, Emotion & Data Analytics</div>
                <div class="auth-tagline-v">
                    "Understand Every Word. Discover Every Emotion."<br/>
                    Enterprise AI platform for real-time speech transcription, sentiment classification, and granular emotion intelligence.
                </div>
                <div>
                    <span class="auth-pill-v">🎙️ Voice Intelligence</span>
                    <span class="auth-pill-v">😊 Emotion Detection</span>
                    <span class="auth-pill-v">⚡ Transformers</span>
                    <span class="auth-pill-v">📊 Analytics</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        mode = st.session_state["auth_mode"]

        if mode == "login":
            st.markdown("### 🔐 Welcome to VEDA")
            st.caption("Sign in to access your Voice, Emotion & Data Analytics Dashboard")

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="name@organization.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                remember_me = st.checkbox("Remember me", value=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter your email and password.")
                    else:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.session_state["page"] = "Dashboard"
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Don't have an account? Register"):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()
            with c2:
                if st.button("Forgot password?"):
                    st.session_state["auth_mode"] = "forgot"
                    st.rerun()

        elif mode == "register":
            st.markdown("### 📝 Create VEDA Account")
            st.caption("Join VEDA for Voice & Emotion Intelligence")

            with st.form("register_form", clear_on_submit=False):
                name = st.text_input("Full Name", placeholder="Alex Johnson")
                email = st.text_input("Email Address", placeholder="alex@company.com")
                password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submitted:
                    if not name or not email or not password:
                        st.error("Please fill in all fields.")
                    elif "@" not in email or "." not in email:
                        st.error("Please enter a valid email address.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        res = create_user(name, email, password)
                        if res["success"]:
                            user = authenticate_user(email, password)
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.session_state["page"] = "Dashboard"
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error(res["message"])

            if st.button("← Back to Login"):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        elif mode == "forgot":
            st.markdown("### 🔑 Reset Password")
            st.caption("Enter your email address to reset password")

            with st.form("forgot_form"):
                email = st.text_input("Email Address", placeholder="name@organization.com")
                new_pw = st.text_input("New Password", type="password", placeholder="Enter new password")
                confirm_pw = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
                submitted = st.form_submit_button("Reset Password", use_container_width=True, type="primary")

                if submitted:
                    if not email or not new_pw:
                        st.error("Please enter your email and new password.")
                    elif new_pw != confirm_pw:
                        st.error("Passwords do not match.")
                    elif len(new_pw) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        if not email_exists(email):
                            st.error("No account found with this email.")
                        else:
                            from database import get_connection, _hash_password
                            with get_connection() as conn:
                                conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (_hash_password(new_pw), email.strip().lower()))
                            st.success("Password updated successfully! Please sign in.")
                            st.session_state["auth_mode"] = "login"
                            st.rerun()

            if st.button("← Back to Login"):
                st.session_state["auth_mode"] = "login"
                st.rerun()
