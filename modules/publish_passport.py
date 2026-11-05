import hashlib
import uuid
import json
from datetime import datetime, timezone

from database.db import (
    save_publish_passport,
    get_publish_passports,
    get_verification_history
)

from modules.approval import get_latest_approval


def generate_content_hash(content):
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def generate_passport_code():
    return "BP-" + uuid.uuid4().hex[:12].upper()


def create_publish_passport(verification_id):
    records = get_verification_history()

    verification = next(
        (
            record for record in records
            if record["id"] == verification_id
        ),
        None
    )

    if not verification:
        return None, "Verification record not found."

    approval = get_latest_approval(verification_id)

    if not approval or approval["decision"] != "Approved":
        return None, "Human approval is required before issuing a passport."

    content = verification["content"]

    content_hash = generate_content_hash(content)
    passport_code = generate_passport_code()

    brand_name = verification.get("brand_name") or "Unknown Brand"

    save_publish_passport(
        verification_id,
        passport_code,
        brand_name,
        content_hash
    )

    passport = {
        "passport_code": passport_code,
        "verification_id": verification_id,
        "brand_name": brand_name,
        "content_hash": content_hash,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "approval_status": "Approved",
        "verification_status": verification["status"]
    }

    return passport, "Publish Passport generated successfully."


def get_all_passports():
    return get_publish_passports()


def verify_passport(passport_code):
    passports = get_publish_passports()

    passport = next(
        (
            item for item in passports
            if item["passport_code"] == passport_code
        ),
        None
    )

    if not passport:
        return {
            "valid": False,
            "message": "Passport not found."
        }

    records = get_verification_history()

    verification = next(
        (
            record for record in records
            if record["id"] == passport["verification_id"]
        ),
        None
    )

    if not verification:
        return {
            "valid": False,
            "message": "Original verification record not found."
        }

    current_hash = generate_content_hash(
        verification["content"]
    )

    if current_hash != passport["content_hash"]:
        return {
            "valid": False,
            "message": "Content integrity check failed."
        }

    approval = get_latest_approval(
        passport["verification_id"]
    )

    if not approval or approval["decision"] != "Approved":
        return {
            "valid": False,
            "message": "Approval is no longer valid."
        }

    return {
        "valid": True,
        "message": "Passport is authentic. Content integrity verified.",
        "passport": passport
    }