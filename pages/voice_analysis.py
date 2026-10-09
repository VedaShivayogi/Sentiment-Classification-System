"""
pages/voice_analysis.py — Dedicated Voice Intelligence & Speech Sentiment Page for VEDA
"""

import streamlit as st
import pandas as pd
from voice import transcribe_audio
from models import MODELS, MODEL_INFO, predict, scores_frame
from emotion import detect_emotion
from database import save_prediction, get_settings
from utils import EMOJI, extract_keywords, generate_veda_insight
from report import generate_pdf_report


def render_voice_analysis(user: dict):
    st.markdown("""
        <div class="header-banner-light">
            <h1 class="header-title-light">🎙️ Voice Intelligence</h1>
            <p class="header-sub-light">Speak naturally. VEDA will understand — Real-time Speech-to-Text & Voice Sentiment Analysis.</p>
        </div>
    """, unsafe_allow_html=True)

    user_settings = get_settings(user["id"])
    use_neutral = bool(user_settings.get("neutral_enabled", 1))
    neutral_threshold = float(user_settings.get("neutral_threshold", 0.70))

    # Controls row
    c_opts, c_info = st.columns([1.5, 1], gap="medium")

    with c_opts:
        selected_model = st.selectbox(
            "Select Sentiment Model Engine",
            list(MODELS.keys()),
            index=0,
            help="Choose the transformer model for voice transcript classification."
        )

    with c_info:
        st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; font-size: 0.82rem; margin-top: 4px;">
                <b style="color: #4f46e5;">{selected_model}</b>: {MODEL_INFO[selected_model]['description']}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    tab_upload, tab_record = st.tabs(["📁 Upload Audio File", "🎙️ Record Voice Input"])

    audio_bytes = None
    file_type = "wav"

    with tab_upload:
        audio_file = st.file_uploader(
            "Upload audio recording (.wav, .mp3, .m4a, .ogg)",
            type=["wav", "mp3", "m4a", "ogg"],
            help="Supported audio formats: WAV, MP3, M4A, OGG."
        )
        if audio_file is not None:
            audio_bytes = audio_file.read()
            file_type = audio_file.name.split(".")[-1].lower()
            st.audio(audio_bytes, format=f"audio/{file_type}")

    with tab_record:
        recorded_audio = st.audio_input("Record your voice directly from browser microphone:")
        if recorded_audio is not None:
            audio_bytes = recorded_audio.read()
            file_type = "wav"
            st.audio(audio_bytes, format="audio/wav")

    st.markdown("<br/>", unsafe_allow_html=True)
    process_btn = st.button("🚀 Transcribe & Analyze Voice Sentiment", type="primary", use_container_width=True)

    if process_btn:
        if not audio_bytes:
            st.warning("⚠️ Please upload an audio file or record your voice before processing.")
            return

        with st.spinner("Transcribing speech audio with VEDA Speech Engine..."):
            stt_res = transcribe_audio(audio_bytes, file_type)

        if not stt_res["success"]:
            st.error(f"❌ {stt_res['message']}")
            return

        transcript = stt_res["transcript"]
        duration = stt_res["duration"]

        st.markdown("---")
        st.markdown("### 📄 Speech-to-Text Transcript")
        st.markdown(f"""
            <div class="veda-card" style="background: #f8fafc; border-left: 4px solid #4f46e5;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #4f46e5; text-transform: uppercase;">TRANSCRIPT</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #0f172a; margin-top: 6px; line-height: 1.6;">
                    "{transcript}"
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Run sentiment analysis on transcript
        with st.spinner(f"Classifying sentiment using `{selected_model}`..."):
            results, sec = predict(selected_model, [transcript], use_neutral, neutral_threshold)

        if not results:
            st.error("Failed to classify transcript sentiment.")
            return

        res = results[0]
        sentiment_label = res["label"]
        confidence = res["confidence"]
        scores = res["scores"]

        # Emotion detection
        emo_data = detect_emotion(transcript, sentiment_label, confidence)
        emotion_name = emo_data["emotion"]
        emotion_emoji = emo_data["emoji"]

        # Save voice prediction to DB
        save_prediction(
            user_id=user["id"],
            text=transcript,
            model=selected_model,
            sentiment=sentiment_label,
            confidence=confidence,
            positive_score=res["positive_score"],
            neutral_score=res["neutral_score"],
            negative_score=res["negative_score"],
            inference_time=sec,
            input_type="voice",
            emotion=emotion_name
        )

        st.markdown("### 🎯 Voice Intelligence Results")

        badge_class = "badge-pos" if sentiment_label == "POSITIVE" else "badge-neu" if sentiment_label == "NEUTRAL" else "badge-neg"

        col_res1, col_res2 = st.columns([1.5, 2], gap="large")

        with col_res1:
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

        with col_res2:
            st.markdown("##### 📊 Class Probabilities")
            s1, s2, s3 = st.columns(3)
            s1.metric("Positive", f"{res['positive_score']:.2f}%")
            s2.metric("Neutral", f"{res['neutral_score']:.2f}%")
            s3.metric("Negative", f"{res['negative_score']:.2f}%")

            st.markdown("##### ⚡ Audio & Performance Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Audio Duration", f"{duration}s" if duration > 0 else "N/A")
            m2.metric("Word Count", len(transcript.split()))
            m3.metric("Latency", f"{sec:.3f}s")
            m4.metric("Model Engine", selected_model)

            st.progress(min(int(confidence), 100))

        st.markdown("<br/>", unsafe_allow_html=True)

        # AI Insight & Keywords
        c_insight, c_words = st.columns(2, gap="medium")

        with c_insight:
            st.markdown("##### 💡 VEDA AI Insight")
            insight_text = generate_veda_insight(sentiment_label, confidence, emotion_name, transcript, selected_model)
            st.markdown(f"""
                <div class="veda-card">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; margin-bottom: 6px;">AI-generated insight</div>
                    <div style="color: #334155; font-size: 0.95rem; line-height: 1.5;">{insight_text}</div>
                </div>
            """, unsafe_allow_html=True)

        with c_words:
            st.markdown("##### 🔤 Important Words")
            keywords = extract_keywords(transcript)
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

        # Downloads
        st.markdown("---")
        st.markdown("### 📥 Download Intelligence Report")
        d1, d2 = st.columns(2)

        with d1:
            pdf_bytes = generate_pdf_report(
                input_text=transcript,
                sentiment=sentiment_label,
                confidence=confidence,
                scores=scores,
                model_name=selected_model,
                input_type="voice",
                emotion=emotion_name,
                insight=insight_text,
                user_name=user["name"]
            )
            st.download_button(
                "📄 Download PDF Intelligence Report",
                data=pdf_bytes,
                file_name="veda_voice_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with d2:
            df_csv = pd.DataFrame([{
                "Input Type": "Voice",
                "Transcript": transcript,
                "Model": selected_model,
                "Sentiment": sentiment_label,
                "Confidence (%)": round(confidence, 2),
                "Emotion": emotion_name,
                "Audio Duration (s)": duration
            }])
            st.download_button(
                "⬇️ Download CSV Record",
                data=df_csv.to_csv(index=False).encode("utf-8"),
                file_name="veda_voice_result.csv",
                mime="text/csv",
                use_container_width=True
            )
