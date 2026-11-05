from datetime import datetime

from database.db import (
    save_approval,
    get_approval_history,
    get_verification_history
)


def submit_for_approval(verification_id, reviewer, comments=""):
    if not reviewer.strip():
        return False, "Reviewer name is required."

    records = get_verification_history()

    verification = next(
        (item for item in records if item["id"] == verification_id),
        None
    )

    if not verification:
        return False, "Verification record not found."

    save_approval(
        verification_id,
        "Pending",
        reviewer,
        comments
    )

    return True, "Content submitted for human approval."


def review_content(verification_id, decision, reviewer, comments=""):
    if decision not in ["Approved", "Rejected"]:
        return False, "Invalid approval decision."

    if not reviewer.strip():
        return False, "Reviewer name is required."

    records = get_verification_history()

    verification = next(
        (item for item in records if item["id"] == verification_id),
        None
    )

    if not verification:
        return False, "Verification record not found."

    save_approval(
        verification_id,
        decision,
        reviewer,
        comments
    )

    return True, f"Content {decision.lower()} successfully."


def get_approval_records():
    return get_approval_history()


def get_latest_approval(verification_id):
    records = get_approval_history()

    matching = [
        record for record in records
        if record["verification_id"] == verification_id
    ]

    if not matching:
        return None

    return max(
        matching,
        key=lambda record: record["id"]
    )