"""
database.py — SQLite database utility for VEDA (Voice, Emotion & Data Analytics)
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "sentiment_app.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'user',
                created_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                text           TEXT    NOT NULL,
                model          TEXT    NOT NULL,
                sentiment      TEXT    NOT NULL,
                confidence     REAL    NOT NULL,
                positive_score REAL    DEFAULT 0.0,
                neutral_score  REAL    DEFAULT 0.0,
                negative_score REAL    DEFAULT 0.0,
                inference_time REAL    DEFAULT 0.0,
                input_type     TEXT    DEFAULT 'text',
                emotion        TEXT    DEFAULT 'Neutral',
                created_at     TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id           INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                default_model     TEXT    NOT NULL DEFAULT 'DistilBERT',
                default_input     TEXT    NOT NULL DEFAULT 'Text',
                neutral_enabled   INTEGER NOT NULL DEFAULT 1,
                neutral_threshold REAL    NOT NULL DEFAULT 0.70,
                max_batch_size    INTEGER NOT NULL DEFAULT 200,
                theme             TEXT    NOT NULL DEFAULT 'light'
            );
        """)

        # Migration logic for existing SQLite DB files
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(predictions);")
        columns = [row["name"] for row in cursor.fetchall()]

        if "input_type" not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN input_type TEXT DEFAULT 'text';")
        if "emotion" not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN emotion TEXT DEFAULT 'Neutral';")

        cursor.execute("PRAGMA table_info(settings);")
        s_columns = [row["name"] for row in cursor.fetchall()]
        if "default_input" not in s_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN default_input TEXT DEFAULT 'Text';")

    # Seed default demo user
    _seed_demo_user()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _seed_demo_user():
    demo_email = "demo@veda.ai"
    if not email_exists(demo_email):
        create_user(name="Demo User", email=demo_email, password="password123", role="user")


def create_user(name: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
    password_hash = _hash_password(password)
    created_at = datetime.now().isoformat()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (name.strip(), email.strip().lower(), password_hash, role, created_at),
            )
            user_id = cursor.lastrowid
            conn.execute(
                "INSERT OR IGNORE INTO settings (user_id) VALUES (?)", (user_id,)
            )
        return {"success": True, "message": "Account created successfully.", "user_id": user_id}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "An account with this email already exists."}
    except Exception as e:
        return {"success": False, "message": f"Database error: {e}"}


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    password_hash = _hash_password(password)
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, name, email, role, created_at FROM users WHERE email = ? AND password_hash = ?",
                (email.strip().lower(), password_hash),
            ).fetchone()
        if row:
            return dict(row)
        return None
    except Exception:
        return None


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def update_user_name(user_id: int, new_name: str) -> Dict[str, Any]:
    try:
        with get_connection() as conn:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (new_name.strip(), user_id))
        return {"success": True, "message": "Profile name updated successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_user_password(user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
    current_hash = _hash_password(current_password)
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE id = ? AND password_hash = ?",
                (user_id, current_hash),
            ).fetchone()
            if not row:
                return {"success": False, "message": "Current password is incorrect."}
            new_hash = _hash_password(new_password)
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        return {"success": True, "message": "Password updated successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def email_exists(email: str) -> bool:
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email.strip().lower(),)
            ).fetchone()
        return row is not None
    except Exception:
        return False


def save_prediction(
    user_id: int,
    text: str,
    model: str,
    sentiment: str,
    confidence: float,
    positive_score: float = 0.0,
    neutral_score: float = 0.0,
    negative_score: float = 0.0,
    inference_time: float = 0.0,
    input_type: str = "text",
    emotion: str = "Neutral",
) -> bool:
    try:
        created_at = datetime.now().isoformat()
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO predictions
                   (user_id, text, model, sentiment, confidence,
                    positive_score, neutral_score, negative_score, inference_time, input_type, emotion, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, text, model, sentiment, confidence,
                    positive_score, neutral_score, negative_score, inference_time, input_type, emotion, created_at,
                ),
            )
        return True
    except Exception:
        return False


def get_predictions(user_id: int, limit: int = 500) -> List[Dict[str, Any]]:
    try:
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT id, text, model, sentiment, confidence,
                          positive_score, neutral_score, negative_score,
                          inference_time, input_type, emotion, created_at
                   FROM predictions WHERE user_id = ?
                   ORDER BY id DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def delete_predictions(user_id: int) -> bool:
    try:
        with get_connection() as conn:
            conn.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        return True
    except Exception:
        return False


def get_user_stats(user_id: int) -> Dict[str, Any]:
    try:
        with get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ?", (user_id,)
            ).fetchone()["cnt"]
            text_cnt = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND (input_type = 'text' OR input_type IS NULL)",
                (user_id,),
            ).fetchone()["cnt"]
            voice_cnt = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND input_type = 'voice'",
                (user_id,),
            ).fetchone()["cnt"]
            pos = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND sentiment = 'POSITIVE'",
                (user_id,),
            ).fetchone()["cnt"]
            neu = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND sentiment = 'NEUTRAL'",
                (user_id,),
            ).fetchone()["cnt"]
            neg = conn.execute(
                "SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND sentiment = 'NEGATIVE'",
                (user_id,),
            ).fetchone()["cnt"]
            avg_conf = conn.execute(
                "SELECT AVG(confidence) as avg FROM predictions WHERE user_id = ?", (user_id,)
            ).fetchone()["avg"]
        return {
            "total": total,
            "text_count": text_cnt,
            "voice_count": voice_cnt,
            "positive": pos,
            "neutral": neu,
            "negative": neg,
            "avg_confidence": round(avg_conf or 0.0, 2),
        }
    except Exception:
        return {
            "total": 0, "text_count": 0, "voice_count": 0,
            "positive": 0, "neutral": 0, "negative": 0, "avg_confidence": 0.0
        }


def get_settings(user_id: int) -> Dict[str, Any]:
    defaults = {
        "default_model": "DistilBERT",
        "default_input": "Text",
        "neutral_enabled": 1,
        "neutral_threshold": 0.70,
        "max_batch_size": 200,
        "theme": "light",
    }
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM settings WHERE user_id = ?", (user_id,)
            ).fetchone()
        if row:
            return dict(row)
        return defaults
    except Exception:
        return defaults


def save_settings(user_id: int, **kwargs) -> bool:
    try:
        with get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM settings WHERE user_id = ?", (user_id,)
            ).fetchone()
            if existing:
                sets = ", ".join(f"{k} = ?" for k in kwargs)
                conn.execute(
                    f"UPDATE settings SET {sets} WHERE user_id = ?",
                    list(kwargs.values()) + [user_id],
                )
            else:
                kwargs["user_id"] = user_id
                cols = ", ".join(kwargs.keys())
                placeholders = ", ".join("?" * len(kwargs))
                conn.execute(
                    f"INSERT INTO settings ({cols}) VALUES ({placeholders})",
                    list(kwargs.values()),
                )
        return True
    except Exception:
        return False
