"""
pages/compare.py — Compare multiple Transformer models on single input for VEDA
"""

import streamlit as st
import pandas as pd
from models import MODELS, predict, scores_frame
from database import save_prediction, get_settings
from utils import EMOJI


def render_compare(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">🤖 Compare AI Models</h1>
            <p class="header-sub-light">Evaluate DistilBERT, RoBERTa, and BERT side-by-side on the same sentence to assess model consensus and accuracy variance.</p>
        </div>
    """, unsafe_allow_html=True)

    user_settings = get_settings(user["id"])
    use_neutral = bool(user_settings.get("neutral_enabled", 1))
    neutral_threshold = float(user_settings.get("neutral_threshold", 0.70))

    if "cmp_text_input" not in st.session_state:
        st.session_state["cmp_text_input"] = "The food was great but the waiter was really rude."

    cmp_text = st.text_area(
        "Enter text to compare across all models:",
        value=st.session_state["cmp_text_input"],
        height=110,
        placeholder="Type or paste text here...",
        key="compare_textarea_v"
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🚀 Run VEDA Model Comparison", type="primary", use_container_width=True):
        if not cmp_text.strip():
            st.warning("⚠️ Please enter a sentence first.")
            return

        rows = []
        model_cols = st.columns(len(MODELS))

        for col, model_name in zip(model_cols, MODELS.keys()):
            with col:
                with st.spinner(f"Evaluating {model_name}..."):
                    results, sec = predict(model_name, [cmp_text], use_neutral, neutral_threshold)
                
                res = results[0]
                label = res["label"]
                conf = res["confidence"]

                save_prediction(
                    user_id=user["id"],
                    text=cmp_text,
                    model=model_name,
                    sentiment=label,
                    confidence=conf,
                    positive_score=res["positive_score"],
                    neutral_score=res["neutral_score"],
                    negative_score=res["negative_score"],
                    inference_time=sec,
                    input_type="text",
                    emotion="Neutral"
                )

                rows.append({
                    "Model": model_name,
                    "Predicted Sentiment": label,
                    "Confidence (%)": round(conf, 2),
                    "Latency (s)": round(sec, 3),
                    "Positive (%)": round(res["positive_score"], 2),
                    "Neutral (%)": round(res["neutral_score"], 2),
                    "Negative (%)": round(res["negative_score"], 2),
                })

                badge_class = "badge-pos" if label == "POSITIVE" else "badge-neu" if label == "NEUTRAL" else "badge-neg"

                st.markdown(f"""
                    <div class="model-card-light">
                        <div class="model-name-light">{model_name}</div>
                        <div style="font-size: 2.2rem; margin: 6px 0;">{EMOJI.get(label, '')}</div>
                        <div><span class="{badge_class}">{label}</span></div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-top: 10px;">{conf:.2f}%</div>
                        <div style="color: #64748b; font-size: 0.8rem; margin-top: 4px;">Latency: {sec:.3f}s</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br/>", unsafe_allow_html=True)
                st.bar_chart(scores_frame(res["scores"]))

        st.markdown("---")

        # ─────────────────────────────────────────────────────────────────────
        # VEDA Model Consensus Check
        # ─────────────────────────────────────────────────────────────────────
        sentiments_list = [r["Predicted Sentiment"] for r in rows]
        most_common = max(set(sentiments_list), key=sentiments_list.count)
        agree_count = sentiments_list.count(most_common)
        total_models = len(MODELS)

        st.markdown("### 🤝 VEDA Model Consensus")

        if agree_count == total_models:
            st.success(f"✅ **{agree_count} / {total_models} models agree** on the predicted `{most_common}` sentiment.")
        else:
            st.warning(f"⚠️ **{agree_count} / {total_models} models agree** on `{most_common}`. Models show prediction variance.")

        # Summary Table
        st.markdown("##### 📋 Detailed Comparison Matrix")
        df_cmp = pd.DataFrame(rows)
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)
