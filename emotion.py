"""
emotion.py — Emotion Detection module for VEDA Platform
Distinguishes Sentiment (Pos/Neu/Neg) from Emotion (Joy, Sadness, Anger, Fear, Surprise, Neutral)
"""

import re

EMOTION_EMOJIS = {
    "Joy": "😊",
    "Sadness": "😢",
    "Anger": "😡",
    "Neutral": "😐",
    "Fear": "😨",
    "Surprise": "😲"
}

EMOTION_KEYWORDS = {
    "Joy": set("love loved happy delighted fantastic awesome great excellent enjoying glad cheerful thrilled ecstatic code".split()),
    "Sadness": set("sad unhappy depressed crying heartbreaking sorrow disappointed hopeless miserable down broken painful regret".split()),
    "Anger": set("worst rude terrible awful angry furious outraged annoying hate useless unacceptable service scam garbage".split()),
    "Fear": set("scared afraid terrified anxious nervous worried warning danger risky threaten unsafe crash error panic".split()),
    "Surprise": set("wow unexpected surprising unbelievable amazed shock astonishing stunning sudden marvel wonder".split())
}


def detect_emotion(text: str, sentiment: str, confidence: float = 80.0) -> dict:
    """
    Detect granular emotion based on textual triggers and model output context.
    Returns dict: {"emotion": name, "emoji": emoji, "confidence": confidence_pct}
    """
    words = [w.lower() for w in re.findall(r"[a-zA-Z']+", text)]
    scores = {e: 0 for e in EMOTION_KEYWORDS.keys()}

    for w in words:
        for emo, kw_set in EMOTION_KEYWORDS.items():
            if w in kw_set:
                scores[emo] += 1

    top_emotion = max(scores, key=scores.get)

    if scores[top_emotion] > 0:
        detected = top_emotion
        emo_conf = min(85.0 + scores[top_emotion] * 5.0, 98.5)
    else:
        # Fallback mapping based on overall sentiment
        if sentiment == "POSITIVE":
            detected = "Joy"
            emo_conf = confidence * 0.95
        elif sentiment == "NEGATIVE":
            # Check if text leans towards anger or sadness
            if any(w in words for w in ["worst", "rude", "terrible", "hate", "scam"]):
                detected = "Anger"
            elif any(w in words for w in ["sad", "sorry", "missed", "lost"]):
                detected = "Sadness"
            else:
                detected = "Anger"
            emo_conf = confidence * 0.90
        else:
            detected = "Neutral"
            emo_conf = confidence

    return {
        "emotion": detected,
        "emoji": EMOTION_EMOJIS.get(detected, "😐"),
        "confidence": round(emo_conf, 1)
    }
