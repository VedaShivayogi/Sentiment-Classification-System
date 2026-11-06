# 🎙️💬 VEDA — Voice, Emotion & Data Analytics

> *"Understand Every Word. Discover Every Emotion."*

VEDA is an enterprise-grade, portfolio-ready **Voice & Text AI Sentiment Intelligence Platform** built with Python, Streamlit, PyTorch, Hugging Face Transformers, SpeechRecognition, ReportLab, and SQLite.

![VEDA Platform](https://img.shields.io/badge/VEDA-Voice%20%26%20Emotion%20AI-4F46E5?style=for-the-badge&logo=Streamlit)
![NLP Models](https://img.shields.io/badge/NLP-Transformers-yellow?style=for-the-badge&logo=huggingface)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)

---

## 🎥 Demo Video

[![VEDA Demo Walkthrough](https://drive.google.com/thumbnail?id=1k68kVUptd0Cag9KbRFYs4tjNQCzfUyUC&sz=w1200)](https://drive.google.com/file/d/1k68kVUptd0Cag9KbRFYs4tjNQCzfUyUC/view?usp=drive_link)

> 🎬 *Click the thumbnail above to watch the full VEDA demo — voice intelligence, emotion detection, multi-model consensus, batch processing, and PDF report export.*

📺 **Direct Link:** [Watch on Google Drive](https://drive.google.com/file/d/1k68kVUptd0Cag9KbRFYs4tjNQCzfUyUC/view?usp=drive_link)

---

## 🌟 Key Features

- **🎙️ Voice Intelligence & Speech-to-Text:** Record voice directly from the browser or upload `.wav`, `.mp3`, `.m4a`, or `.ogg` audio files for automated transcription and voice sentiment analysis.
- **😊 Granular Emotion Detection:** Classifies overall sentiment (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) while detecting granular emotional tones (`Joy`, `Sadness`, `Anger`, `Fear`, `Surprise`, `Neutral`).
- **🎨 Modern Light SaaS UI:** Built with a crisp, minimal white theme featuring rounded cards, pill badges, soft shadows, and indigo accents.
- **💡 VEDA AI Insights & Key Tokens:** Generates deterministic natural language summaries and extracts key positive/negative term indicators.
- **📄 Professional PDF Reports:** Export formal single-page PDF intelligence reports (with VEDA logo, date, input type, transcript, sentiment scores, emotion, and AI insight) or CSV logs.
- **🔐 Multi-User Authentication:** Secure SQLite database (`sentiment_app.db`) with SHA-256 password hashing, user registration, forgot password reset, and isolated history logs.
- **🤖 Multi-Model Comparison & Consensus:** Evaluate **DistilBERT**, **RoBERTa**, and **BERT** side-by-side with automated consensus reporting (`3/3 models agree`).
- **📂 Batch File Processing:** Process CSV or Excel datasets with automated classification, confidence distribution, accuracy metrics, confusion matrices, and report downloads.
- **📊 Interactive Analytics:** Filter historical predictions by date, model, or sentiment, with voice vs. text volume timelines.

---

## 🤖 Models & Sentiment Mapping

| Model Engine | Hugging Face Checkpoint | Native Output | VEDA Mapping |
| :--- | :--- | :--- | :--- |
| **DistilBERT** | `distilbert-base-uncased-finetuned-sst-2-english` | `POSITIVE`, `NEGATIVE` | Confidence < threshold → `NEUTRAL` |
| **RoBERTa** | `cardiffnlp/twitter-roberta-base-sentiment` | `LABEL_0`, `LABEL_1`, `LABEL_2` | `LABEL_0` → `NEGATIVE`<br/>`LABEL_1` → `NEUTRAL`<br/>`LABEL_2` → `POSITIVE` |
| **BERT** | `nlptown/bert-base-multilingual-uncased-sentiment` | `1 star` to `5 stars` | `1-2 stars` → `NEGATIVE`<br/>`3 stars` → `NEUTRAL`<br/>`4-5 stars` → `POSITIVE` |

---

## 📂 Project Architecture
