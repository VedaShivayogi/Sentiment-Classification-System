"""
pages/dashboard.py — Main Dashboard view for VEDA (Voice, Emotion & Data Analytics)
"""

import streamlit as st
import pandas as pd
from database import get_predictions, get_user_stats
from utils import EMOJI


def render_dashboard(user: dict):
    stats = get_user_stats(user["id"])
    recent_preds = get_predictions(user["id"], limit=8)

    st.markdown(f"""
        <div class="header-banner-light">
            <h1 class="header-title-light">Welcome back, {user['name']} 👋</h1>
            <p class="header-sub-light">Understand every word. Discover every emotion.</p>
        </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Hero Section Banner
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="veda-hero-card">
            <div style="font-size: 0.85rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.08em;">
                ✨ AI-Powered Sentiment Intelligence
            </div>
            <h2 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin-top: 4px; margin-bottom: 8px;">
                Analyze text and voice using transformer-based NLP models.
            </h2>
            <p style="color: #475569; font-size: 0.98rem; margin: 0; max-width: 800px;">
                VEDA unifies speech-to-text transcription, transformer sentiment classification, and granular emotion intelligence into a single unified analytics platform.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # 3 Major Action Cards
    # ─────────────────────────────────────────────────────────────────────────
    act_col1, act_col2, act_col3 = st.columns(3, gap="medium")

    with act_col1:
        st.markdown("""
            <div class="veda-action-card">
                <div>
                    <div style="font-size: 2.8rem; margin-bottom: 8px;">💬</div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0;">Analyze Text</h3>
                    <p style="color: #64748b; font-size: 0.88rem; margin-top: 8px;">
                        Evaluate sentiment, class probabilities, and emotion indicators for raw text input.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Text Analysis →", key="btn_hero_text", use_container_width=True, type="primary"):
            st.session_state["page"] = "Text Analysis"
            st.rerun()

    with act_col2:
        st.markdown("""
            <div class="veda-action-card">
                <div>
                    <div style="font-size: 2.8rem; margin-bottom: 8px;">🎙️</div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0;">Analyze Voice</h3>
                    <p style="color: #64748b; font-size: 0.88rem; margin-top: 8px;">
                        Upload or record speech audio to transcribe and classify voice sentiment in real time.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Voice Intelligence →", key="btn_hero_voice", use_container_width=True, type="primary"):
            st.session_state["page"] = "Voice Intelligence"
            st.rerun()

    with act_col3:
        st.markdown("""
            <div class="veda-action-card">
                <div>
                    <div style="font-size: 2.8rem; margin-bottom: 8px;">🤖</div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0;">Compare Models</h3>
                    <p style="color: #64748b; font-size: 0.88rem; margin-top: 8px;">
                        Run DistilBERT, RoBERTa, and BERT side-by-side to assess consensus and variance.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Compare AI Models →", key="btn_hero_cmp", use_container_width=True, type="primary"):
            st.session_state["page"] = "Compare Models"
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # KPI Metric Cards
    # ─────────────────────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(f"""
            <div class="kpi-card-light">
                <div class="kpi-title-light">Total Analyses</div>
                <div class="kpi-value-light">{stats['total']:,}</div>
                <div class="kpi-sub-light">Text: {stats['text_count']} | Voice: {stats['voice_count']}</div>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div class="kpi-card-light" style="border-left: 4px solid #10b981;">
                <div class="kpi-title-light">Positive</div>
                <div class="kpi-value-light" style="color: #10b981;">{stats['positive']:,}</div>
                <div class="kpi-sub-light">{(stats['positive']/max(stats['total'],1))*100:.1f}% of total</div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div class="kpi-card-light" style="border-left: 4px solid #64748b;">
                <div class="kpi-title-light">Neutral</div>
                <div class="kpi-value-light" style="color: #64748b;">{stats['neutral']:,}</div>
                <div class="kpi-sub-light">{(stats['neutral']/max(stats['total'],1))*100:.1f}% of total</div>
            </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
            <div class="kpi-card-light" style="border-left: 4px solid #ef4444;">
                <div class="kpi-title-light">Negative</div>
                <div class="kpi-value-light" style="color: #ef4444;">{stats['negative']:,}</div>
                <div class="kpi-sub-light">{(stats['negative']/max(stats['total'],1))*100:.1f}% of total</div>
            </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
            <div class="kpi-card-light" style="border-left: 4px solid #4f46e5;">
                <div class="kpi-title-light">Avg Confidence</div>
                <div class="kpi-value-light" style="color: #4f46e5;">{stats['avg_confidence']:.1f}%</div>
                <div class="kpi-sub-light">Model Certainty</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Recent Activity Table
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 🕘 Recent Intelligence Logs")
    if recent_preds:
        t_data = []
        for p in recent_preds:
            t_data.append({
                "Timestamp": p["created_at"].split("T")[0] + " " + p["created_at"].split("T")[1][:5],
                "Input Type": "🎙️ Voice" if p.get("input_type") == "voice" else "💬 Text",
                "Text / Transcript Snippet": p["text"][:65] + ("..." if len(p["text"]) > 65 else ""),
                "Model": p["model"],
                "Sentiment": f"{EMOJI.get(p['sentiment'],'')} {p['sentiment']}",
                "Emotion": p.get("emotion", "Neutral"),
                "Confidence": f"{p['confidence']:.1f}%",
            })
        st.dataframe(pd.DataFrame(t_data), use_container_width=True, hide_index=True)
    else:
        st.info("No recent predictions found. Launch 'Analyze Text' or 'Voice Intelligence' to generate analytics!")
