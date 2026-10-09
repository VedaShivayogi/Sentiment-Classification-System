# 🎙️💬 VEDA — Voice, Emotion & Data Analytics

> *"Understand Every Word. Discover Every Emotion."*

VEDA is an enterprise-grade, portfolio-ready **Voice & Text AI Sentiment Intelligence Platform** built with Python, Streamlit, PyTorch, Hugging Face Transformers, SpeechRecognition, ReportLab, and SQLite.

![VEDA Platform](https://img.shields.io/badge/VEDA-Voice%20%26%20Emotion%20AI-4F46E5?style=for-the-badge&logo=Streamlit)
![NLP Models](https://img.shields.io/badge/NLP-Transformers-yellow?style=for-the-badge&logo=huggingface)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)

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

```
sentiment-classification-system/
│
├── app.py              # Main application router & Light UI sidebar navigation
├── auth.py             # User authentication, registration & password reset
├── database.py         # SQLite CRUD utilities, user hashing, & predictions migration
├── models.py           # Hugging Face cached pipeline loading & score unification
├── voice.py            # Speech-to-Text transcription engine & audio processing
├── emotion.py          # Emotion classification engine (Joy, Sadness, Anger, etc.)
├── report.py           # ReportLab PDF report generator
├── utils.py            # Word extraction, VEDA AI insights & report helpers
├── requirements.txt    # Project dependencies
├── README.md           # Documentation & setup guide
├── .gitignore          # Git exclusion rules
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py    # VEDA Light UI dashboard & action cards
│   ├── analyze.py      # Text Sentiment & Emotion Analysis interface
│   ├── voice_analysis.py # Voice Intelligence & Speech Sentiment workspace
│   ├── compare.py      # 3-Model side-by-side comparison & consensus engine
│   ├── batch.py        # CSV/Excel batch processor & accuracy evaluation
│   ├── analytics.py    # Historical analytics & voice vs. text metrics
│   ├── history.py      # User-isolated prediction history & CSV export
│   ├── profile.py      # User account management
│   └── settings.py     # Default input, model & speech parameters
│
└── assets/
    └── style.css       # VEDA Light Theme CSS styling
```

---

## 🚀 Installation & Setup

### 1. Clone & Virtual Environment

```bash
# Clone repository
git clone https://github.com/VedaShivayogi/Sentiment-Classification-System
cd Sentiment-Classification-System-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Launch VEDA

```bash
streamlit run app.py
```

---

## 🔑 Demo Account

The application seeds a demo user on first run:

- **Email:** `demo@veda.ai`
- **Password:** `password123`

---

# 📸 Example Predictions

The **Images** folder contains prediction examples using all three models.

Examples include:

- Positive sentiment predictions
- Negative sentiment predictions
- Confidence score comparison across models

---



# 📊 Dataset

The dataset used in this project is located in:

```text
Dataset/
└── NLP_Project_Dataset.xlsx
```

---

# 📑 Documentation

The complete project report is available in:

```text
Documentation/
└── NLP_Project_Report.pdf
```

---

# 🛠 Technologies Used

- Python
- Streamlit
- Hugging Face Transformers
- PyTorch
- Pandas
- NumPy
- Scikit-learn
- OpenPyXL

---

# 💡 Future Improvements

- Support multi-class sentiment classification.
- Add Neutral sentiment prediction.
- Support Arabic sentiment analysis.
- Visualize confidence scores using charts.
- Deploy the application online using Streamlit Community Cloud.

---

## 🌟 Future Expansion

- **Multilingual Voice Support:** Native speech-to-text models for Regional Indian Languages (Kannada, Hindi, Tamil, Telugu).
- **Whisper / Faster-Whisper Integration:** Offline local high-accuracy speech transcription.
- **Aspect-Based Sentiment Analysis (ABSA):** Entity & feature sentiment extraction.
