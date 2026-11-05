import os
import re
import json
from collections import Counter

from dotenv import load_dotenv
from google import genai


load_dotenv()


def run_gemini_analysis(content, brand_profile):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    prompt = f"""
You are BrandProof, an AI brand compliance analyst.

Analyze the marketing content against the brand guidelines.

BRAND:
{brand_profile.get("brand_name", "Unknown")}

COMMUNICATION TONE:
{brand_profile.get("tone", "Professional")}

RESTRICTED WORDS:
{brand_profile.get("forbidden_words", [])}

REQUIRED WORDS:
{brand_profile.get("required_words", [])}

MAXIMUM WORD COUNT:
{brand_profile.get("max_length", 500)}

CONTENT:
{content}

Check:
1. Whether the content matches the brand's communication tone.
2. Whether the messaging is consistent with the brand identity.
3. Whether there are potentially misleading or unsupported claims.
4. Whether the content sounds professional and trustworthy.
5. Whether any improvements are recommended.

Do not invent facts about the brand.
Do not repeat rule violations already covered by the restricted-word
and required-word checks unless there is an additional concern.

Return ONLY valid JSON in this format:
{{
    "tone_match": "Good, Partial, or Poor",
    "summary": "Short explanation of the analysis",
    "issues": ["Issue 1"],
    "warnings": ["Warning 1"],
    "suggestions": ["Suggestion 1"]
}}
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        result = json.loads(response.text)

        return {
            "tone_match": str(result.get("tone_match", "Not assessed")),
            "summary": str(result.get("summary", "")),
            "issues": result.get("issues", []),
            "warnings": result.get("warnings", []),
            "suggestions": result.get("suggestions", [])
        }

    except Exception as error:
        return {
            "tone_match": "Unavailable",
            "summary": "Gemini analysis could not be completed.",
            "issues": [],
            "warnings": [
                f"AI analysis unavailable: {str(error)}"
            ],
            "suggestions": []
        }


def check_brand_content(content, brand_profile):

    if not content or not content.strip():
        return {
            "status": "Needs Review",
            "score": 0,
            "violations": ["Content cannot be empty."],
            "warnings": [],
            "word_count": 0,
            "suggestions": ["Enter content before verification."],
            "ai_analysis": None
        }

    if not brand_profile:
        return {
            "status": "Needs Review",
            "score": 0,
            "violations": [
                "Brand guidelines have not been configured."
            ],
            "warnings": [],
            "word_count": len(content.split()),
            "suggestions": [
                "Create a brand profile before verification."
            ],
            "ai_analysis": None
        }

    violations = []
    warnings = []
    suggestions = []

    content_lower = content.lower()
    words = re.findall(r"\b[\w'-]+\b", content_lower)
    word_count = len(words)

    forbidden_words = brand_profile.get("forbidden_words", [])
    required_words = brand_profile.get("required_words", [])
    max_length = int(brand_profile.get("max_length", 500))

    # 1. Restricted words and phrases
    for phrase in forbidden_words:
        phrase = phrase.strip()

        if phrase and re.search(
            r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)",
            content_lower
        ):
            violations.append(
                f"Forbidden word or phrase detected: '{phrase}'"
            )
            suggestions.append(
                f"Remove or replace '{phrase}' with approved brand language."
            )

    # 2. Required words and phrases
    for phrase in required_words:
        phrase = phrase.strip()

        if phrase and not re.search(
            r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)",
            content_lower
        ):
            violations.append(
                f"Required word or phrase is missing: '{phrase}'"
            )
            suggestions.append(
                f"Include the required phrase '{phrase}'."
            )

    # 3. Maximum word count
    if word_count > max_length:
        violations.append(
            f"Content contains {word_count} words. "
            f"Maximum allowed is {max_length}."
        )
        suggestions.append(
            "Shorten the content to meet the brand's word limit."
        )

    # 4. Repeated words
    word_counts = Counter(words)

    repeated_words = [
        word for word, count in word_counts.items()
        if count >= 5 and len(word) > 3
    ]

    for word in repeated_words:
        warnings.append(
            f"The word '{word}' is repeated frequently."
        )
        suggestions.append(
            f"Consider using alternatives for '{word}'."
        )

    # 5. Excessive uppercase letters
    letters = [
        character for character in content
        if character.isalpha()
    ]

    if letters:
        uppercase_count = sum(
            character.isupper() for character in letters
        )

        uppercase_ratio = uppercase_count / len(letters)

        if uppercase_ratio > 0.5 and len(letters) > 15:
            warnings.append(
                "Content contains excessive uppercase letters."
            )
            suggestions.append(
                "Use normal capitalization for a professional appearance."
            )

    # 6. Calculate rule-based score
    total_checks = len(forbidden_words) + len(required_words) + 1
    failed_checks = len(violations)

    rule_score = round(
        max(0, (total_checks - failed_checks) / total_checks * 100)
    )

    # 7. Gemini AI analysis
    ai_analysis = run_gemini_analysis(content, brand_profile)

    if ai_analysis:
        for issue in ai_analysis["issues"]:
            warnings.append(f"AI review: {issue}")

        for warning in ai_analysis["warnings"]:
            warnings.append(f"AI warning: {warning}")

        suggestions.extend(ai_analysis["suggestions"])

    # 8. Final decision
    if violations:
        status = "Needs Review"
    elif ai_analysis and ai_analysis["issues"]:
        status = "Needs Review"
    else:
        status = "Approved"

    if not suggestions:
        suggestions.append(
            "No corrections required under the configured checks."
        )

    return {
        "status": status,
        "score": rule_score,
        "violations": violations,
        "warnings": warnings,
        "word_count": word_count,
        "suggestions": suggestions,
        "ai_analysis": ai_analysis
    }


def generate_compliance_report(content, brand_profile):

    result = check_brand_content(content, brand_profile)

    return {
        "brand": brand_profile.get("brand_name", "Unknown Brand"),
        "content": content,
        "compliance_score": result["score"],
        "decision": result["status"],
        "violations": result["violations"],
        "warnings": result["warnings"],
        "suggestions": result["suggestions"],
        "word_count": result["word_count"],
        "ai_analysis": result["ai_analysis"]
    }
