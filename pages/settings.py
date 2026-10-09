"""
pages/settings.py — System and user preference settings page for VEDA
"""

import streamlit as st
from models import MODELS
from database import get_settings, save_settings


def render_settings(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">⚙️ VEDA Settings & Preferences</h1>
            <p class="header-sub-light">Customize default inputs, transformer models, neutral thresholds, and voice language parameters.</p>
        </div>
    """, unsafe_allow_html=True)

    current_settings = get_settings(user["id"])

    with st.form("settings_form_v"):
        st.markdown("##### 🎙️ Workspace Defaults")
        c1, c2 = st.columns(2)

        with c1:
            default_input = st.selectbox(
                "Default Input Mode",
                ["Text Analysis", "Voice Intelligence"],
                index=0 if current_settings.get("default_input", "Text") == "Text" else 1,
                help="Default landing view for new intelligence tasks."
            )

        with c2:
            default_model = st.selectbox(
                "Default Sentiment Model Engine",
                list(MODELS.keys()),
                index=list(MODELS.keys()).index(current_settings.get("default_model", "DistilBERT"))
                if current_settings.get("default_model") in MODELS else 0,
                help="Default transformer model preselected across analysis tools."
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### 🎙️ Voice & Speech Configuration")
        voice_lang = st.selectbox(
            "Speech Recognition Language",
            ["English (US/UK)"],
            index=0,
            help="Primary language engine for audio transcription. Architecture ready for regional expansions (Kannada, Hindi, Tamil, Telugu)."
        )

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### ⚖️ Sentiment Classification Parameters")
        neutral_enabled = st.checkbox(
            "Enable Neutral Class Classification",
            value=bool(current_settings.get("neutral_enabled", 1)),
            help="Allows classification outputs to return NEUTRAL."
        )

        neutral_threshold = st.slider(
            "DistilBERT Neutral Confidence Threshold (%)",
            min_value=50,
            max_value=95,
            value=int(current_settings.get("neutral_threshold", 0.70) * 100),
            help="Confidence threshold below which DistilBERT results map to NEUTRAL."
        ) / 100.0

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### 📂 Batch Processing Constraints")
        max_batch_size = st.number_input(
            "Maximum Batch Processing Rows Limit",
            min_value=10,
            max_value=5000,
            value=int(current_settings.get("max_batch_size", 200)),
            help="Limits row processing size per file upload to avoid UI latency."
        )

        st.markdown("<br/>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("Save VEDA Preferences", type="primary")

        if save_btn:
            ok = save_settings(
                user_id=user["id"],
                default_model=default_model,
                default_input="Text" if "Text" in default_input else "Voice",
                neutral_enabled=1 if neutral_enabled else 0,
                neutral_threshold=neutral_threshold,
                max_batch_size=int(max_batch_size)
            )
            if ok:
                st.success("Your VEDA settings have been saved successfully!")
            else:
                st.error("Failed to save settings to database.")
