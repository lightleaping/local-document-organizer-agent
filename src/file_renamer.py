import re
from pathlib import Path
from typing import List

from src.keyword_extractor import extract_keywords


CATEGORY_RULES = [
    ("ai", ["인공지능", "자연어 처리", "이미지 인식", "추천 시스템", "문서 자동화"]),
    ("database", ["데이터베이스", "관계형 데이터베이스", "기본 키", "외래 키", "정규화", "인덱스"]),
    ("report", ["리포트", "보고서", "분석", "결과"]),
    ("meeting", ["회의", "미팅", "논의", "안건"]),
    ("study", ["학습", "강의", "정리", "개요"]),
]


def sanitize_filename(text: str) -> str:
    """
    Convert text into a safe filename fragment.
    """
    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w가-힣\-]+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    return text


def detect_category(keyword_text: str) -> str:
    """
    Detect a simple document category from keywords.
    """
    for category, signals in CATEGORY_RULES:
        if any(signal.lower() in keyword_text.lower() for signal in signals):
            return category

    return "document"


def build_title_keywords(keywords, max_count: int = 3) -> List[str]:
    """
    Select readable keywords for filename title.
    """
    selected = []

    for keyword, score in keywords:
        cleaned = sanitize_filename(keyword)

        if not cleaned:
            continue

        if cleaned in {"문서", "파일", "기능", "시스템", "기술"}:
            continue

        selected.append(cleaned)

        if len(selected) >= max_count:
            break

    return selected


def suggest_filename(document, top_k: int = 5) -> str:
    """
    Suggest a readable filename.
    This function does not rename the actual file.

    Format:
    category__keyword_keyword_keyword.ext
    """
    keywords = extract_keywords(document.text, top_k=top_k)
    keyword_text = " ".join([keyword for keyword, score in keywords])

    category = detect_category(keyword_text)
    title_keywords = build_title_keywords(keywords, max_count=3)

    if title_keywords:
        base_name = f"{category}__{'_'.join(title_keywords)}"
    else:
        base_name = f"{category}__{Path(document.file_name).stem}"

    base_name = sanitize_filename(base_name)
    base_name = base_name[:80].rstrip("_")

    return f"{base_name}{document.extension}"


def suggest_filenames(documents) -> dict:
    """
    Suggest filenames for multiple documents.
    """
    return {
        document.file_name: suggest_filename(document)
        for document in documents
    }
