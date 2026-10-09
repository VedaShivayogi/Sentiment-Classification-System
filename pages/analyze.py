"""
pages/analyze.py — Text Sentiment & Emotion Analysis page for VEDA
"""

import streamlit as st
import pandas as pd
from models import MODELS, MODEL_INFO, predict, scores_frame
from emotion import detect_emotion
from database import save_prediction, get_settings
from utils import EMOJI, SAMPLES, extract_keywords, generate_veda_insight
from report import generate_pdf_report


def render_analyze(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">💬 Text Analysis</h1>
            <p class="header-sub-light">Analyze text sentiment and emotion using transformer-based NLP models (DistilBERT, RoBERTa, BERT).</p>
        </div>
    """, unsafe_allow_html=True)

    user_settings = get_settings(user["id"])

    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""

    # Sample texts cards
    st.markdown("##### 📝 Quick Samples")
    sample_cols = st.columns(len(SAMPLES))
    for col, (label, sample_val) in zip(sample_cols, SAMPLES.items()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state["input_text"] = sample_val
                st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    c_main, c_settings = st.columns([2.2, 1], gap="medium")

    with c_main:
        text_val = st.text_area(
            "Write or paste something here...",
            value=st.session_state["input_text"],
            height=160,
            placeholder="Write or paste customer review, social media post, or feedback text here...",
            key="analyze_textarea_v"
        )
        st.session_state["input_text"] = text_val

        char_count = len(text_val)
        word_count = len(text_val.split()) if text_val.strip() else 0

        st.caption(f"📊 Stats: **{char_count}** characters | **{word_count}** words")

    with c_settings:
        st.markdown("##### ⚙️ Model Configuration")

        default_model = user_settings.get("default_model", "DistilBERT")
        model_idx = list(MODELS.keys()).index(default_model) if default_model in MODELS else 0

        selected_model = st.selectbox(
            "Select Model",
            list(MODELS.keys()),
            index=model_idx,
            help="Choose the transformer neural network for classification."
        )

        info = MODEL_INFO[selected_model]
        st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-top: 8px; font-size: 0.82rem;">
                <div style="color: #4f46e5; font-weight: 700;">{selected_model}</div>
                <div style="color: #475569; margin-top: 2px;">{info['description']}</div>
                <div style="color: #64748b; margin-top: 6px;">⚡ Speed: {info['speed']}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        use_neutral = st.toggle("Enable Neutral Class", value=bool(user_settings.get("neutral_enabled", 1)))
        
        neutral_threshold = st.slider(
            "Neutral Threshold (%)",
            min_value=50,
            max_value=95,
            value=int(user_settings.get("neutral_threshold", 0.70) * 100),
        ) / 100.0

    st.markdown("<br/>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Analyze with VEDA", type="primary", use_container_width=True)

    if analyze_btn:
        if not text_val.strip():
            st.warning("⚠️ Please enter or select a sample text before running analysis.")
            return

        with st.spinner(f"Analyzing sentiment with `{selected_model}`..."):
            results, sec = predict(selected_model, [text_val], use_neutral, neutral_threshold)

        if not results:
            st.error("Failed to generate prediction results.")
            return

        res = results[0]
        sentiment_label = res["label"]
        confidence = res["confidence"]
        scores = res["scores"]

        # Emotion detection
        emo_data = detect_emotion(text_val, sentiment_label, confidence)
        emotion_name = emo_data["emotion"]
        emotion_emoji = emo_data["emoji"]

        # Save to database
        save_prediction(
            user_id=user["id"],
            text=text_val,
            model=selected_model,
            sentiment=sentiment_label,
            confidence=confidence,
            positive_score=res["positive_score"],
            neutral_score=res["neutral_score"],
            negative_score=res["negative_score"],
            inference_time=sec,
            input_type="text",
            emotion=emotion_name
        )

        st.markdown("---")
        st.markdown("### 🎯 Classification Results")

        badge_class = "badge-pos" if sentiment_label == "POSITIVE" else "badge-neu" if sentiment_label == "NEUTRAL" else "badge-neg"

        r_col1, r_col2 = st.columns([1.5, 2], gap="large")

        with r_col1:
            st.markdown(f"""
                <div class="veda-card" style="text-align: center; padding: 28px;">
                    <div style="font-size: 3.5rem; margin-bottom: 8px;">{EMOJI.get(sentiment_label, '💬')}</div>
                    <div><span class="{badge_class}" style="font-size: 1.2rem; padding: 6px 18px;">{sentiment_label}</span></div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-top: 14px;">{confidence:.2f}%</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Confidence Score</div>
                    <div style="margin-top: 16px;">
                        <span class="badge-emotion">{emotion_emoji} Emotion: {emotion_name}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with r_col2:
            st.markdown("##### 📊 Class Probabilities")
            s_col1, s_col2, s_col3 = st.columns(3)
            s_col1.metric("Positive", f"{res['positive_score']:.2f}%")
            s_col2.metric("Neutral", f"{res['neutral_score']:.2f}%")
            s_col3.metric("Negative", f"{res['negative_score']:.2f}%")

            st.markdown("##### ⚡ Latency & Text Metrics")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Latency", f"{sec:.3f}s")
            m_col2.metric("Words", word_count)
            m_col3.metric("Characters", char_count)
            m_col4.metric("Model", selected_model)

            st.progress(min(int(confidence), 100))

        st.markdown("<br/>", unsafe_allow_html=True)

        # AI Insight & Keywords
        c_insight, c_words = st.columns(2, gap="medium")

        with c_insight:
            st.markdown("##### 💡 VEDA AI Insight")
            insight_text = generate_veda_insight(sentiment_label, confidence, emotion_name, text_val, selected_model)
            st.markdown(f"""
                <div class="veda-card">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; margin-bottom: 6px;">AI-generated insight</div>
                    <div style="color: #334155; font-size: 0.95rem; line-height: 1.5;">{insight_text}</div>
                </div>
            """, unsafe_allow_html=True)

        with c_words:
            st.markdown("##### 🔤 Important Words")
            keywords = extract_keywords(text_val)
            st.markdown('<div class="veda-card">', unsafe_allow_html=True)
            if keywords["positive"]:
                st.markdown("**Positive Indicators:**")
                for w in keywords["positive"]:
                    st.markdown(f'<span class="keyword-chip-pos">+{w}</span>', unsafe_allow_html=True)
            if keywords["negative"]:
                st.markdown("**Negative Indicators:**")
                for w in keywords["negative"]:
                    st.markdown(f'<span class="keyword-chip-neg">-{w}</span>', unsafe_allow_html=True)
            if keywords["all"]:
                st.markdown("**Key Tokens:**")
                for w in keywords["all"]:
                    st.markdown(f'<span class="keyword-chip">{w}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Score breakdown chart
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### 📈 Score Breakdown Chart")
        st.bar_chart(scores_frame(scores))

        # Downloads
        st.markdown("---")
        st.markdown("### 📥 Download Intelligence Report")
        d1, d2 = st.columns(2)

        with d1:
            pdf_bytes = generate_pdf_report(
                input_text=text_val,
                sentiment=sentiment_label,
                confidence=confidence,
                scores=scores,
                model_name=selected_model,
                input_type="text",
                emotion=emotion_name,
                insight=insight_text,
                user_name=user["name"]
            )
            st.download_button(
                "📄 Download PDF Intelligence Report",
                data=pdf_bytes,
                file_name="veda_text_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with d2:
            df_csv = pd.DataFrame([{
                "Input Type": "Text",
                "Text": text_val,
                "Model": selected_model,
                "Sentiment": sentiment_label,
                "Confidence (%)": round(confidence, 2),
                "Emotion": emotion_name
            }])
            st.download_button(
                "⬇️ Download CSV Record",
                data=df_csv.to_csv(index=False).encode("utf-8"),
                file_name="veda_text_result.csv",
                mime="text/csv",
                use_container_width=True
            )
