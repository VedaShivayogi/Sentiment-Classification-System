
import streamlit as st
from transformers import pipeline

st.set_page_config(
    page_title="Sentiment Classification App",
    page_icon="💬",
    layout="centered"
)

st.title("Sentiment Classification System")
st.write("Classify text sentiment using three pretrained Hugging Face models.")

MODELS = {
    "DistilBERT": "distilbert-base-uncased-finetuned-sst-2-english",
    "RoBERTa": "cardiffnlp/twitter-roberta-base-sentiment",
    "BERT": "nlptown/bert-base-multilingual-uncased-sentiment"
}

@st.cache_resource
def load_model(model_name):
    return pipeline("sentiment-analysis", model=MODELS[model_name])

def unify_label(model_name, label):
    if model_name == "DistilBERT":
        return label

    if model_name == "RoBERTa":
        return "POSITIVE" if label == "LABEL_2" else "NEGATIVE"

    if model_name == "BERT":
        return "POSITIVE" if label in ["4 stars", "5 stars"] else "NEGATIVE"

sentence = st.text_area("Enter a sentence:")

model_choice = st.selectbox(
    "Choose a model:",
    ["DistilBERT", "RoBERTa", "BERT"]
)

if st.button("Predict"):
    if sentence.strip() == "":
        st.warning("Please enter a sentence first.")
    else:
        classifier = load_model(model_choice)
        result = classifier(sentence[:512])[0]

        final_label = unify_label(model_choice, result["label"])
        confidence = result["score"] * 100

        st.subheader("Prediction Result")
        st.success(f"Predicted Label: {final_label}")
        st.write(f"Confidence Score: {confidence:.2f}%")
