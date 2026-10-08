# Sentiment Classification System

An NLP-based sentiment analysis application built with Python, Streamlit, and Hugging Face Transformers. The system classifies text into **Positive** or **Negative** sentiment using three state-of-the-art pretrained transformer models: **BERT**, **DistilBERT**, and **RoBERTa**.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20Application-red?logo=streamlit)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-red?logo=pytorch)
![NLP](https://img.shields.io/badge/NLP-Sentiment%20Analysis-green)

---

# 📖 Overview

This project was developed to compare the performance of multiple transformer-based language models for sentiment classification.

The application provides an interactive web interface where users can enter any English sentence, choose one of three pretrained Hugging Face models, and instantly receive the predicted sentiment along with the confidence score.

The project demonstrates how modern NLP models can accurately analyze textual opinions and emotions through transfer learning without training models from scratch.

---

# ✨ Features

- Interactive Streamlit web application.
- Supports three pretrained transformer models.
- Predicts Positive or Negative sentiment.
- Displays prediction confidence score.
- Easy model switching for comparison.
- Fast real-time inference.
- Clean and user-friendly interface.

---

# 🤖 Models Used

The project compares the following Hugging Face pretrained models:

| Model | Purpose |
|--------|----------|
| BERT | Bidirectional Encoder Representations from Transformers |
| DistilBERT | Lightweight and faster version of BERT |
| RoBERTa | Robustly Optimized BERT Pretraining Approach |

---

# 📂 Project Structure

```text
NLP-Project
│
├── Dataset
│   └── NLP_Project_Dataset.xlsx
│
├── Demo
│   └── Demo.mp4
│
├── Documentation
│   └── NLP_Project_Report.pdf
│
├── Images
│   ├── Negative_Example1_BERT.png
│   ├── ...
│   └── Positive_Example2_RoBERTa.png
│
├── Models
│   └── Model_Evaluation.ipynb
│
├── app.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone the repository:

```bash
git clone [https://github.com/USERNAME/NLP-Project.git](https://github.com/Shooqaladwani/Sentiment-Classification-System.git)

cd NLP-Project
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your web browser.

---

# 📸 Example Predictions

The **Images** folder contains prediction examples using all three models.

Examples include:

- Positive sentiment predictions
- Negative sentiment predictions
- Confidence score comparison across models

---

# 🎥 Demo

A demonstration video is available in:

```text
Demo/
└── Demo.mp4
```

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

