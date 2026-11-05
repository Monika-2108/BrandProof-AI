import re
import json
import hashlib
from datetime import datetime


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def count_words(text):
    return len(text.split()) if text else 0


def generate_text_hash(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def format_datetime(value=None):
    if value is None:
        value = datetime.now()

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value

    return value.strftime("%d %b %Y, %I:%M %p")


def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_json(filepath, default=None):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def generate_unique_id(prefix="BP"):
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def truncate_text(text, limit=100):
    if len(text) <= limit:
        return text

    return text[:limit].rstrip() + "..."


def validate_email(email):
    pattern = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
    return bool(re.match(pattern, email.strip()))


def calculate_compliance_percentage(passed, total):
    if total <= 0:
        return 0

    return round((passed / total) * 100, 2)