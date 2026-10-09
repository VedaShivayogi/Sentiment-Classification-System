"""
models.py — Transformer Model pipeline loading & predictions for SentimentAI
"""

import time
import pandas as pd
import streamlit as st
from transformers import pipeline

MODELS = {
    "DistilBERT": "distilbert-base-uncased-finetuned-sst-2-english",
    "RoBERTa": "cardiffnlp/twitter-roberta-base-sentiment",
    "BERT": "nlptown/bert-base-multilingual-uncased-sentiment",
}

MODEL_INFO = {
    "DistilBERT": {
        "description": "Fast & lightweight transformer model optimized for binary sentiment classification.",
        "architecture": "DistilBERT (6-layer, 66M parameters)",
        "task": "SST-2 Binary Sentiment Analysis",
        "speed": "⚡ Very Fast (~10-30ms)",
    },
    "RoBERTa": {
        "description": "Robustly optimized BERT approach fine-tuned on ~58M tweets for 3-class sentiment.",
        "architecture": "RoBERTa-base (12-layer, 125M parameters)",
        "task": "Twitter 3-Class Sentiment (Neg, Neu, Pos)",
        "speed": "⚡⚡ Fast (~30-60ms)",
    },
    "BERT": {
        "description": "Multilingual BERT model fine-tuned on star ratings (1 to 5 stars).",
        "architecture": "BERT-base multilingual (12-layer, 110M parameters)",
        "task": "Product Review 5-Star Rating (Mapped to 3-Class)",
        "speed": "⚡ Moderate (~40-80ms)",
    },
}


@st.cache_resource(show_spinner=False)
def load_model(model_name: str):
    """
    Load huggingface pipeline with cached resource so models load only once.
    """
    model_path = MODELS[model_name]
    return pipeline("sentiment-analysis", model=model_path, top_k=None)


def unify_scores(model_name: str, raw: list) -> dict:
    """
    Convert each model's raw label outputs into normalized POSITIVE / NEUTRAL / NEGATIVE scores.
    """
    scores = {"POSITIVE": 0.0, "NEUTRAL": 0.0, "NEGATIVE": 0.0}
    for item in raw:
        label, score = item["label"], float(item["score"])
        if model_name == "DistilBERT":
            key = label.upper()
        elif model_name == "RoBERTa":
            key = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}.get(label, "NEUTRAL")
        else:  # BERT: "1 star" ... "5 stars"
            stars = int(label[0]) if label[0].isdigit() else 3
            key = "POSITIVE" if stars >= 4 else "NEUTRAL" if stars == 3 else "NEGATIVE"
        scores[key] += score
    return scores


def predict(model_name: str, texts: list, use_neutral: bool = True, neutral_threshold: float = 0.70):
    """
    Run sentiment analysis over a list of text inputs.
    Returns: (list of dicts, average_inference_time_per_sample)
    """
    if not texts:
        return [], 0.0

    clf = load_model(model_name)
    start = time.time()
    # Batch pipeline call with truncation
    raw_results = clf(texts, truncation=True, max_length=512, batch_size=16)
    elapsed = time.time() - start

    out = []
    for raw in raw_results:
        scores = unify_scores(model_name, raw)

        if not use_neutral:
            # Re-normalize between POSITIVE & NEGATIVE if neutral disabled
            scores["NEUTRAL"] = 0.0
            tot = scores["POSITIVE"] + scores["NEGATIVE"]
            if tot > 0:
                scores["POSITIVE"] /= tot
                scores["NEGATIVE"] /= tot

        label = max(scores, key=scores.get)
        confidence = scores[label]

        # DistilBERT has no native neutral class: convert low-confidence binary output to Neutral
        if use_neutral and model_name == "DistilBERT" and confidence < neutral_threshold:
            label = "NEUTRAL"

        out.append({
            "label": label,
            "confidence": confidence * 100.0,
            "scores": scores,
            "positive_score": scores["POSITIVE"] * 100.0,
            "neutral_score": scores["NEUTRAL"] * 100.0,
            "negative_score": scores["NEGATIVE"] * 100.0,
        })

    avg_time = elapsed / max(len(texts), 1)
    return out, avg_time


def scores_frame(scores: dict) -> pd.DataFrame:
    """
    Format scores dictionary into DataFrame for bar charts or visual tables.
    """
    return pd.DataFrame({
        "Sentiment": list(scores.keys()),
        "Score (%)": [round(v * 100.0, 2) for v in scores.values()]
    }).set_index("Sentiment")
