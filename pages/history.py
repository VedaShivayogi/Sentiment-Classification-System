"""
pages/history.py — Prediction history view for current logged-in user in VEDA
"""

import streamlit as st
import pandas as pd
from database import get_predictions, delete_predictions
from utils import EMOJI


def render_history(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">🕘 Prediction History</h1>
            <p class="header-sub-light">View, filter, search, and export your personal prediction and voice transcription logs.</p>
        </div>
    """, unsafe_allow_html=True)

    predictions = get_predictions(user["id"], limit=1000)

    if not predictions:
        st.info("No prediction history found. Run predictions in 'Text Analysis' or 'Voice Intelligence' to generate history.")
        return

    df = pd.DataFrame(predictions)
    df["Timestamp"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    if "input_type" not in df.columns:
        df["input_type"] = "text"
    if "emotion" not in df.columns:
        df["emotion"] = "Neutral"

    # Search and Filter Bar
    c_search, c_model, c_sent = st.columns([2, 1, 1])

    with c_search:
        search_query = st.text_input("🔍 Search logs...", placeholder="Search text keyword...")

    with c_model:
        models = ["All"] + list(df["model"].unique())
        filter_model = st.selectbox("Model Filter", models, key="hist_model_filter_v")

    with c_sent:
        sentiments = ["All", "POSITIVE", "NEUTRAL", "NEGATIVE"]
        filter_sent = st.selectbox("Sentiment Filter", sentiments, key="hist_sent_filter_v")

    # Apply filters
    filtered = df.copy()
    if search_query.strip():
        filtered = filtered[filtered["text"].str.contains(search_query.strip(), case=False, na=False)]
    if filter_model != "All":
        filtered = filtered[filtered["model"] == filter_model]
    if filter_sent != "All":
        filtered = filtered[filtered["sentiment"] == filter_sent]

    st.markdown("<br/>", unsafe_allow_html=True)

    # Data Table View
    display_df = filtered[["Timestamp", "input_type", "model", "text", "sentiment", "emotion", "confidence"]].copy()
    display_df.columns = ["Timestamp", "Input Type", "Model", "Text / Transcript", "Sentiment", "Emotion", "Confidence (%)"]
    display_df["Input Type"] = display_df["Input Type"].apply(lambda t: "🎙️ Voice" if t == "voice" else "💬 Text")
    display_df["Sentiment"] = display_df["Sentiment"].apply(lambda s: f"{EMOJI.get(s,'')} {s}")
    display_df["Confidence (%)"] = display_df["Confidence (%)"].round(2)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    act_col1, act_col2 = st.columns(2)

    with act_col1:
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export VEDA Logs as CSV",
            data=csv_data,
            file_name="veda_prediction_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    with act_col2:
        if st.button("🗑️ Clear My History", type="secondary", use_container_width=True):
            if delete_predictions(user["id"]):
                st.success("Your prediction history has been cleared.")
                st.rerun()
            else:
                st.error("Failed to clear prediction history.")
