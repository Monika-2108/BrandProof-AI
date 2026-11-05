import json
import os

from database.db import (
    save_brand_guidelines,
    get_brand_guidelines
)


DATA_FOLDER = "data"
KNOWLEDGE_FILE = os.path.join(DATA_FOLDER, "brand_knowledge.json")


def create_brand_profile(
    brand_name,
    tone,
    forbidden_words,
    required_words,
    max_length
):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    profile = {
        "brand_name": brand_name.strip(),
        "tone": tone,
        "forbidden_words": [
            word.strip()
            for word in forbidden_words.split(",")
            if word.strip()
        ],
        "required_words": [
            word.strip()
            for word in required_words.split(",")
            if word.strip()
        ],
        "max_length": int(max_length)
    }

    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)

    save_brand_guidelines(
        profile["brand_name"],
        profile["tone"],
        ", ".join(profile["forbidden_words"]),
        ", ".join(profile["required_words"]),
        profile["max_length"]
    )

    return profile


def get_brand_profile():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    database_profile = get_brand_guidelines()

    if database_profile:
        return {
            "brand_name": database_profile["brand_name"],
            "tone": database_profile["tone"],
            "forbidden_words": [
                word.strip()
                for word in (database_profile["forbidden_words"] or "").split(",")
                if word.strip()
            ],
            "required_words": [
                word.strip()
                for word in (database_profile["required_words"] or "").split(",")
                if word.strip()
            ],
            "max_length": database_profile["max_length"]
        }

    return None


def delete_brand_profile():
    if os.path.exists(KNOWLEDGE_FILE):
        os.remove(KNOWLEDGE_FILE)

    return True


def validate_brand_profile(profile):
    if not profile:
        return False, "Brand profile does not exist."

    if not profile.get("brand_name"):
        return False, "Brand name is required."

    if not profile.get("tone"):
        return False, "Brand communication tone is required."

    if profile.get("max_length", 0) <= 0:
        return False, "Maximum content length must be greater than zero."

    return True, "Brand profile is valid."