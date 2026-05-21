from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from src.keyword_extractor import extract_keywords
from src.summarizer import summarize_text


@dataclass
class DocumentAnalysis:
    file_name: str
    extension: str
    char_count: int
    topic: str
    keywords: List[str]
    suggested_name: str
    summary: str


CATEGORY_RULES = [
    ("ai", "AI 문서", ["인공지능", "자연어 처리", "이미지 인식", "추천 시스템", "문서 자동화"]),
    ("database", "데이터베이스 문서", ["데이터베이스", "관계형 데이터베이스", "기본 키", "외래 키", "정규화", "인덱스"]),
    ("report", "분석 리포트", ["리포트", "보고서", "분석 결과"]),
    ("study", "학습 정리", ["학습", "강의", "개요"]),
]


def sanitize_filename(text: str) -> str:
    import re

    text = text.lower()
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w가-힣\-]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def infer_topic(keywords: List[str]) -> Tuple[str, str]:
    keyword_text = " ".join(keywords).lower()

    for category_slug, topic_label, signals in CATEGORY_RULES:
        if any(signal.lower() in keyword_text for signal in signals):
            return category_slug, topic_label

    if keywords:
        return "document", f"{keywords[0]} 관련 문서"

    return "document", "일반 문서"


def build_suggested_filename(document, category_slug: str, keywords: List[str]) -> str:
    title_keywords = []

    for keyword in keywords:
        safe_keyword = sanitize_filename(keyword)

        if not safe_keyword:
            continue

        if safe_keyword in {"문서", "파일", "기능", "시스템", "기술", "개요"}:
            continue

        title_keywords.append(safe_keyword)

        if len(title_keywords) >= 3:
            break

    if title_keywords:
        base_name = f"{category_slug}__{'_'.join(title_keywords)}"
    else:
        base_name = f"{category_slug}__{Path(document.file_name).stem}"

    base_name = sanitize_filename(base_name)[:80].rstrip("_")

    return f"{base_name}{document.extension}"


def analyze_document(document, summary_sentences: int = 3, keyword_count: int = 6) -> DocumentAnalysis:
    """
    Analyze one document with a single shared interpretation flow.

    Flow:
    1. Extract ranked keywords.
    2. Infer representative topic from the ranked keywords.
    3. Build suggested filename from the same topic and keywords.
    4. Generate summary from the document text.
    """
    keyword_items = extract_keywords(document.text, top_k=keyword_count)
    keywords = [keyword for keyword, score in keyword_items]

    category_slug, topic_label = infer_topic(keywords)
    suggested_name = build_suggested_filename(document, category_slug, keywords)
    summary = summarize_text(document.text, max_sentences=summary_sentences)

    return DocumentAnalysis(
        file_name=document.file_name,
        extension=document.extension,
        char_count=document.char_count,
        topic=topic_label,
        keywords=keywords,
        suggested_name=suggested_name,
        summary=summary,
    )


def analyze_documents(documents, summary_sentences: int = 3, keyword_count: int = 6) -> List[DocumentAnalysis]:
    return [
        analyze_document(
            document=document,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
        )
        for document in documents
    ]
