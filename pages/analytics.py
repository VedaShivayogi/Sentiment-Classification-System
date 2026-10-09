"""
pages/analytics.py — Analytics Dashboard for VEDA
"""

import streamlit as st
import pandas as pd
from database import get_predictions
from utils import top_words, EMOJI


def render_analytics(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">📊 Analytics Dashboard</h1>
            <p class="header-sub-light">Deep dive into historical predictions, confidence distribution, voice vs text volume, and keyword trends.</p>
        </div>
    """, unsafe_allow_html=True)

    raw_preds = get_predictions(user["id"], limit=1000)

    if not raw_preds:
        st.info("No prediction data available for analytics yet. Run some sentiment or voice analyses first!")
        return

    df = pd.DataFrame(raw_preds)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["Date"] = df["created_at"].dt.date
    if "input_type" not in df.columns:
        df["input_type"] = "text"

    # Filters
    st.markdown("##### 🔍 Data Filters")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        models_available = ["All"] + list(df["model"].unique())
        selected_model = st.selectbox("Filter by Model Engine", models_available)

    with f_col2:
        sentiments_available = ["All", "POSITIVE", "NEUTRAL", "NEGATIVE"]
        selected_sentiment = st.selectbox("Filter by Sentiment", sentiments_available)

    with f_col3:
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        date_range = st.date_input("Date Range", value=(min_date, max_date))

    # Apply filters
    filtered_df = df.copy()
    if selected_model != "All":
        filtered_df = filtered_df[filtered_df["model"] == selected_model]
    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df["Date"] >= date_range[0]) & (filtered_df["Date"] <= date_range[1])]

    if filtered_df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    st.markdown("<br/>", unsafe_allow_html=True)

    # Metrics
    total_cnt = len(filtered_df)
    text_cnt = (filtered_df["input_type"].fillna("text") == "text").sum()
    voice_cnt = (filtered_df["input_type"] == "voice").sum()
    pos_cnt = (filtered_df["sentiment"] == "POSITIVE").sum()
    neu_cnt = (filtered_df["sentiment"] == "NEUTRAL").sum()
    neg_cnt = (filtered_df["sentiment"] == "NEGATIVE").sum()
    avg_conf = filtered_df["confidence"].mean()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Filtered", f"{total_cnt:,}", f"Text: {text_cnt} | Voice: {voice_cnt}")
    m2.metric("Positive %", f"{(pos_cnt/total_cnt)*100:.1f}%")
    m3.metric("Neutral %", f"{(neu_cnt/total_cnt)*100:.1f}%")
    m4.metric("Negative %", f"{(neg_cnt/total_cnt)*100:.1f}%")
    m5.metric("Avg Confidence", f"{avg_conf:.1f}%")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### 📈 Sentiment Distribution")
        st.bar_chart(filtered_df["sentiment"].value_counts())

    with c2:
        st.markdown("##### 🎙️ Input Type Breakdown (Voice vs Text)")
        st.bar_chart(filtered_df["input_type"].value_counts())

    st.markdown("<br/>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("##### 🕒 Sentiment Volume Over Time")
        trend_df = filtered_df.groupby(["Date", "sentiment"]).size().unstack(fill_value=0)
        st.line_chart(trend_df)

    with c4:
        st.markdown("##### 🎯 Average Confidence by Model")
        conf_by_model = filtered_df.groupby("model")["confidence"].mean()
        st.bar_chart(conf_by_model)

    st.markdown("---")
    st.markdown("##### 🔤 Most Frequent Words in Filtered Corpus")
    tw_df = top_words(filtered_df["text"].tolist(), n=20)
    st.bar_chart(tw_df)
