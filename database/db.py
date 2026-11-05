import sqlite3
import os
from datetime import datetime

DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "brandproof.db")


def get_connection():
    os.makedirs(DB_FOLDER, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brand_guidelines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            tone TEXT,
            forbidden_words TEXT,
            required_words TEXT,
            max_length INTEGER,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            violations TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id INTEGER,
            decision TEXT NOT NULL,
            reviewer TEXT,
            comments TEXT,
            created_at TEXT,
            FOREIGN KEY (verification_id)
            REFERENCES verification_history(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publish_passports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id INTEGER,
            passport_code TEXT UNIQUE,
            brand_name TEXT,
            content_hash TEXT,
            issued_at TEXT,
            FOREIGN KEY (verification_id)
            REFERENCES verification_history(id)
        )
    """)

    connection.commit()
    connection.close()


def save_brand_guidelines(
    brand_name,
    tone,
    forbidden_words,
    required_words,
    max_length
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO brand_guidelines
        (brand_name, tone, forbidden_words, required_words,
         max_length, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        brand_name,
        tone,
        forbidden_words,
        required_words,
        max_length,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_brand_guidelines():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM brand_guidelines
        ORDER BY id DESC LIMIT 1
    """)

    result = cursor.fetchone()
    connection.close()

    return dict(result) if result else None


def save_verification(
    brand_name,
    content,
    status,
    violations
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO verification_history
        (brand_name, content, status, violations, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        brand_name,
        content,
        status,
        violations,
        datetime.now().isoformat()
    ))

    verification_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return verification_id


def get_verification_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM verification_history
        ORDER BY id DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return results


def save_approval(
    verification_id,
    decision,
    reviewer,
    comments
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO approvals
        (verification_id, decision, reviewer, comments, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        verification_id,
        decision,
        reviewer,
        comments,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_approval_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM approvals
        ORDER BY id DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return results


def save_publish_passport(
    verification_id,
    passport_code,
    brand_name,
    content_hash
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO publish_passports
        (verification_id, passport_code, brand_name,
         content_hash, issued_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        verification_id,
        passport_code,
        brand_name,
        content_hash,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_publish_passports():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM publish_passports
        ORDER BY id DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return results


initialize_database()