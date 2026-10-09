"""
pages/batch.py — Batch CSV/Excel file sentiment analysis for VEDA
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from models import MODELS, predict
from database import save_prediction, get_settings
from utils import top_words, generate_analysis_report


def render_batch(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">📂 Batch Analysis</h1>
            <p class="header-sub-light">Process large CSV or Excel datasets using transformer models for batch sentiment classification and accuracy evaluation.</p>
        </div>
    """, unsafe_allow_html=True)

    user_settings = get_settings(user["id"])
    use_neutral = bool(user_settings.get("neutral_enabled", 1))
    neutral_threshold = float(user_settings.get("neutral_threshold", 0.70))
    default_max_rows = int(user_settings.get("max_batch_size", 200))

    uploaded_file = st.file_uploader(
        "Upload dataset (.csv or .xlsx)",
        type=["csv", "xlsx"],
        help="Upload a dataset containing text columns to run sentiment predictions."
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            return

        st.markdown("##### 📄 Dataset Preview")
        st.dataframe(df_raw.head(), use_container_width=True)

        col_opts1, col_opts2, col_opts3, col_opts4 = st.columns(4)

        with col_opts1:
            text_col = st.selectbox("Text Column", df_raw.columns)
        with col_opts2:
            true_col = st.selectbox("True Label Column (Optional)", ["(none)"] + list(df_raw.columns))
        with col_opts3:
            batch_model = st.selectbox("Select Model Engine", list(MODELS.keys()))
        with col_opts4:
            max_rows = st.number_input(
                "Max Rows to Process",
                min_value=1,
                max_value=len(df_raw),
                value=min(len(df_raw), default_max_rows)
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚀 Run VEDA Batch Analysis", type="primary", use_container_width=True):
            subset = df_raw.head(int(max_rows)).copy()
            texts = subset[text_col].astype(str).tolist()

            with st.spinner(f"Processing {len(texts)} records using `{batch_model}`..."):
                results, sec = predict(batch_model, texts, use_neutral, neutral_threshold)

            subset["Predicted"] = [r["label"] for r in results]
            subset["Confidence (%)"] = [round(r["confidence"], 2) for r in results]
            subset["Positive (%)"] = [round(r["positive_score"], 2) for r in results]
            subset["Neutral (%)"] = [round(r["neutral_score"], 2) for r in results]
            subset["Negative (%)"] = [round(r["negative_score"], 2) for r in results]

            for text_val, r in zip(texts, results):
                save_prediction(
                    user_id=user["id"],
                    text=text_val,
                    model=batch_model,
                    sentiment=r["label"],
                    confidence=r["confidence"],
                    positive_score=r["positive_score"],
                    neutral_score=r["neutral_score"],
                    negative_score=r["negative_score"],
                    inference_time=sec,
                    input_type="text",
                    emotion="Neutral"
                )

            st.markdown("---")
            st.markdown("### 📊 Batch Execution Summary")

            pos_cnt = (subset["Predicted"] == "POSITIVE").sum()
            neu_cnt = (subset["Predicted"] == "NEUTRAL").sum()
            neg_cnt = (subset["Predicted"] == "NEGATIVE").sum()
            avg_conf = subset["Confidence (%)"].mean()

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Total Processed", len(subset))
            k2.metric("Positive", pos_cnt)
            k3.metric("Neutral", neu_cnt)
            k4.metric("Negative", neg_cnt)
            k5.metric("Avg Confidence", f"{avg_conf:.2f}%")

            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("##### 📄 Classified Dataset Results")
            st.dataframe(subset, use_container_width=True)

            # Charts
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("##### 📈 Sentiment Distribution")
                st.bar_chart(subset["Predicted"].value_counts())

            with c2:
                st.markdown("##### 📊 Confidence Distribution")
                st.bar_chart(np.histogram(subset["Confidence (%)"], bins=10)[0])

            with c3:
                st.markdown("##### 🔤 Most Frequent Words")
                st.bar_chart(top_words(texts))

            # Evaluation matrix
            if true_col != "(none)":
                st.markdown("---")
                st.markdown("### 🎯 Model Evaluation vs True Labels")
                mapping = {
                    "1": "POSITIVE", "0": "NEGATIVE", "POS": "POSITIVE",
                    "NEG": "NEGATIVE", "NEU": "NEUTRAL", "POSITIVE": "POSITIVE",
                    "NEGATIVE": "NEGATIVE", "NEUTRAL": "NEUTRAL"
                }
                truth = subset[true_col].astype(str).str.upper().replace(mapping)
                pred = subset["Predicted"]

                acc = (truth == pred).mean() * 100.0
                st.metric("Model Accuracy", f"{acc:.2f}%")

                labels = sorted(list(set(truth) | set(pred)))
                report_dict = classification_report(
                    truth, pred, labels=labels, output_dict=True, zero_division=0
                )
                df_rep = pd.DataFrame(report_dict).T.round(3)

                st.markdown("##### 📋 Classification Report (Precision / Recall / F1)")
                st.dataframe(df_rep, use_container_width=True)

                st.markdown("##### 🔲 Confusion Matrix")
                cm = pd.DataFrame(
                    confusion_matrix(truth, pred, labels=labels),
                    index=[f"True {l}" for l in labels],
                    columns=[f"Pred {l}" for l in labels],
                )
                st.dataframe(cm, use_container_width=True)

            # Downloads
            st.markdown("---")
            d1, d2 = st.columns(2)
            with d1:
                csv_bytes = subset.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Classified CSV Results",
                    data=csv_bytes,
                    file_name="veda_batch_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with d2:
                report_md = generate_analysis_report(subset, batch_model)
                st.download_button(
                    "📝 Download Markdown Executive Report",
                    data=report_md.encode("utf-8"),
                    file_name="veda_batch_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
