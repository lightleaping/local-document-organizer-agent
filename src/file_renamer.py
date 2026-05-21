import re
from pathlib import Path
from typing import List

from src.keyword_extractor import extract_keywords


def sanitize_filename(text: str) -> str:
    """
    Convert text into a safe filename fragment.
    """
    text = text.lower()
    text = re.sub(r"[^\w가-힣]+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    return text


def shorten_filename(text: str, max_length: int = 60) -> str:
    """
    Shorten filename while keeping it readable.
    """
    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip("_")


def suggest_filename(document, top_k: int = 3) -> str:
    """
    Suggest a new filename based on extracted keywords.
    This function does not rename the actual file.
    """
    keywords = extract_keywords(document.text, top_k=top_k)

    if not keywords:
        base_name = Path(document.file_name).stem
        safe_name = sanitize_filename(base_name)
        return f"{safe_name}{document.extension}"

    keyword_parts: List[str] = []

    for keyword, score in keywords:
        safe_keyword = sanitize_filename(keyword)

        if safe_keyword:
            keyword_parts.append(safe_keyword)

    if not keyword_parts:
        base_name = Path(document.file_name).stem
        safe_name = sanitize_filename(base_name)
        return f"{safe_name}{document.extension}"

    suggested_base = "_".join(keyword_parts)
    suggested_base = shorten_filename(suggested_base)

    return f"{suggested_base}{document.extension}"


def suggest_filenames(documents) -> dict:
    """
    Suggest filenames for multiple documents.
    """
    suggestions = {}

    for document in documents:
        suggestions[document.file_name] = suggest_filename(document)

    return suggestions