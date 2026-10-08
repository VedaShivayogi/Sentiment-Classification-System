import time
from datetime import datetime

import pandas as pd
import streamlit as st
from transformers import pipeline

# ------------------------------------------------------------------
# Page setup
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Sentiment Classification App",
    page_icon="💬",
    layout="wide",
)

MODELS = {
    "DistilBERT": "distilbert-base-uncased-finetuned-sst-2-english",
    "RoBERTa": "cardiffnlp/twitter-roberta-base-sentiment",
    "BERT": "nlptown/bert-base-multilingual-uncased-sentiment",
}

EMOJI = {"POSITIVE": "😊", "NEUTRAL": "😐", "NEGATIVE": "😞"}

SAMPLES = {
    "Positive": "I absolutely loved this movie, the acting was fantastic!",
    "Negative": "This was the worst service I have ever experienced.",
    "Neutral-ish": "The package arrived on Tuesday.",
    "Mixed": "The food was great but the waiter was really rude.",
}

if "history" not in st.session_state:
    st.session_state.history = []
if "text_input" not in st.session_state:
    st.session_state.text_input = ""


# ------------------------------------------------------------------
# Model helpers
# ------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_model(model_name):
    # top_k=None -> return the score of every class, not just the best one
    return pipeline("sentiment-analysis", model=MODELS[model_name], top_k=None)


def unify_scores(model_name, raw):
    """Convert each model's own labels into POSITIVE / NEUTRAL / NEGATIVE."""
    scores = {"POSITIVE": 0.0, "NEUTRAL": 0.0, "NEGATIVE": 0.0}
    for item in raw:
        label, score = item["label"], item["score"]
        if model_name == "DistilBERT":
            key = label.upper()
        elif model_name == "RoBERTa":
            key = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}[label]
        else:  # BERT: "1 star" ... "5 stars"
            stars = int(label[0])
            key = "POSITIVE" if stars >= 4 else "NEUTRAL" if stars == 3 else "NEGATIVE"
        scores[key] += score
    return scores


def predict(model_name, texts, use_neutral=True, neutral_threshold=0.70):
    """Return a list of dicts: label, confidence, scores (one per text)."""
    clf = load_model(model_name)
    start = time.time()
    raw_results = clf(texts, truncation=True, max_length=512, batch_size=16)
    elapsed = time.time() - start

    out = []
    for raw in raw_results:
        scores = unify_scores(model_name, raw)

        if not use_neutral:
            scores["NEUTRAL"] = 0.0

        label = max(scores, key=scores.get)
        confidence = scores[label]

        # DistilBERT has no neutral class: treat low confidence as neutral
        if use_neutral and model_name == "DistilBERT" and confidence < neutral_threshold:
            label = "NEUTRAL"

        out.append({"label": label, "confidence": confidence * 100, "scores": scores})
    return out, elapsed / max(len(texts), 1)


def scores_frame(scores):
    return pd.DataFrame({"Score (%)": {k: v * 100 for k, v in scores.items()}})


def add_history(model_name, text, res):
    st.session_state.history.insert(
        0,
        {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Model": model_name,
            "Text": text,
            "Sentiment": res["label"],
            "Confidence (%)": round(res["confidence"], 2),
        },
    )


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
st.sidebar.header("⚙️ Settings")
use_neutral = st.sidebar.checkbox("Enable Neutral class", value=True)
neutral_threshold = st.sidebar.slider(
    "DistilBERT neutral threshold (%)",
    50, 95, 70,
    help="DistilBERT only knows Positive/Negative. Predictions below this "
         "confidence are shown as Neutral.",
) / 100

st.sidebar.header("📝 Sample sentences")
for name, sample in SAMPLES.items():
    if st.sidebar.button(name):
        st.session_state.text_input = sample

st.sidebar.info(f"Predictions made this session: {len(st.session_state.history)}")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
st.title("💬 Sentiment Classification System")
st.write("Classify text sentiment using BERT, DistilBERT and RoBERTa.")

tab_single, tab_compare, tab_batch, tab_history = st.tabs(
    ["Single prediction", "Compare all models", "Batch file", "History"]
)

# ---------------------------- Single ------------------------------
with tab_single:
    text = st.text_area("Enter a sentence:", key="text_input", height=120)
    model_choice = st.selectbox("Choose a model:", list(MODELS))

    if st.button("Predict", key="predict_single"):
        if not text.strip():
            st.warning("Please enter a sentence first.")
        else:
            with st.spinner("Loading model and predicting..."):
                results, sec = predict(model_choice, [text], use_neutral, neutral_threshold)
            res = results[0]
            add_history(model_choice, text, res)

            st.subheader("Prediction Result")
            msg = f"{EMOJI[res['label']]} Predicted Label: {res['label']}"
            if res["label"] == "POSITIVE":
                st.success(msg)
            elif res["label"] == "NEGATIVE":
                st.error(msg)
            else:
                st.info(msg)

            c1, c2, c3 = st.columns(3)
            c1.metric("Confidence", f"{res['confidence']:.2f}%")
            c2.metric("Words", len(text.split()))
            c3.metric("Inference time", f"{sec:.2f}s")

            st.progress(min(int(res["confidence"]), 100))
            st.bar_chart(scores_frame(res["scores"]))

# ---------------------------- Compare -----------------------------
with tab_compare:
    st.write("Run the same sentence through all three models at once.")
    cmp_text = st.text_area("Enter a sentence:", key="cmp_text", height=100)

    if st.button("Compare models"):
        if not cmp_text.strip():
            st.warning("Please enter a sentence first.")
        else:
            rows = []
            cols = st.columns(3)
            for col, name in zip(cols, MODELS):
                with st.spinner(f"Running {name}..."):
                    results, sec = predict(name, [cmp_text], use_neutral, neutral_threshold)
                res = results[0]
                add_history(name, cmp_text, res)
                rows.append(
                    {
                        "Model": name,
                        "Sentiment": res["label"],
                        "Confidence (%)": round(res["confidence"], 2),
                        "Time (s)": round(sec, 3),
                    }
                )
                with col:
                    st.markdown(f"### {name}")
                    st.markdown(f"**{EMOJI[res['label']]} {res['label']}**")
                    st.write(f"Confidence: {res['confidence']:.2f}%")
                    st.bar_chart(scores_frame(res["scores"]))

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            labels = {r["Sentiment"] for r in rows}
            if len(labels) == 1:
                st.success("✅ All models agree.")
            else:
                st.warning("⚠️ The models disagree on this sentence.")

# ----------------------------- Batch ------------------------------
with tab_batch:
    st.write("Upload a CSV or Excel file and classify every row.")
    file = st.file_uploader("Upload file", type=["csv", "xlsx"])

    if file is not None:
        data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
        st.dataframe(data.head(), use_container_width=True)

        text_col = st.selectbox("Text column", data.columns)
        true_col = st.selectbox("True label column (optional)", ["(none)"] + list(data.columns))
        batch_model = st.selectbox("Model", list(MODELS), key="batch_model")
        max_rows = st.number_input("Max rows to process", 1, len(data), min(len(data), 200))

        if st.button("Run batch prediction"):
            subset = data.head(int(max_rows)).copy()
            texts = subset[text_col].astype(str).tolist()

            with st.spinner("Classifying..."):
                results, _ = predict(batch_model, texts, use_neutral, neutral_threshold)

            subset["Predicted"] = [r["label"] for r in results]
            subset["Confidence (%)"] = [round(r["confidence"], 2) for r in results]

            st.dataframe(subset, use_container_width=True)
            st.bar_chart(subset["Predicted"].value_counts())

            if true_col != "(none)":
                mapping = {"1": "POSITIVE", "0": "NEGATIVE", "POS": "POSITIVE", "NEG": "NEGATIVE"}
                truth = subset[true_col].astype(str).str.upper().replace(mapping)
                acc = (truth == subset["Predicted"]).mean() * 100
                st.metric("Accuracy vs. true labels", f"{acc:.2f}%")

            st.download_button(
                "⬇️ Download results (CSV)",
                subset.to_csv(index=False).encode("utf-8"),
                file_name="sentiment_results.csv",
                mime="text/csv",
            )

# ---------------------------- History -----------------------------
with tab_history:
    if st.session_state.history:
        hist = pd.DataFrame(st.session_state.history)
        st.dataframe(hist, use_container_width=True, hide_index=True)
        st.bar_chart(hist["Sentiment"].value_counts())

        c1, c2 = st.columns(2)
        c1.download_button(
            "⬇️ Download history (CSV)",
            hist.to_csv(index=False).encode("utf-8"),
            file_name="prediction_history.csv",
            mime="text/csv",
        )
        if c2.button("🗑️ Clear history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No predictions yet.")
