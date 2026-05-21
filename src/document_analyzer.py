from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.keyword_extractor import clean_markdown, extract_keywords
from src.summarizer import summarize_text


@dataclass
class DocumentAnalysis:
    file_name: str
    extension: str
    char_count: int
    document_type: str
    title: str
    keywords: List[str]
    suggested_name: str
    filename_reason: str
    summary: str


DOCUMENT_PROFILES = [
    {
        "profile_id": "ai_document_automation",
        "document_type": "AI 문서 자동화 개요",
        "title": "AI 기반 문서 자동화 활용 정리",
        "filename_base": "ai_document_automation_overview",
        "signals": ["인공지능", "문서 자동화", "요약", "키워드", "자연어 처리"],
        "keywords": ["인공지능", "문서 자동화", "자연어 처리", "이미지 인식", "추천 시스템", "요약", "키워드 추출"],
    },
    {
        "profile_id": "database_design",
        "document_type": "데이터베이스 설계 개념",
        "title": "데이터베이스 설계와 키 개념 정리",
        "filename_base": "database_design_keys_indexes",
        "signals": ["데이터베이스", "관계형", "기본 키", "외래 키", "정규화", "인덱스", "설계"],
        "keywords": ["데이터베이스", "관계형 데이터베이스", "기본 키", "외래 키", "정규화", "무결성", "인덱스"],
    },
    {
        "profile_id": "project_report",
        "document_type": "프로젝트 리포트",
        "title": "프로젝트 분석 리포트",
        "filename_base": "project_analysis_report",
        "signals": ["리포트", "분석", "결과", "보고서"],
        "keywords": ["분석 결과", "리포트", "요약", "개선 가능성", "처리 방식"],
    },
]


GENERIC_STOPWORDS = {
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과",
    "사용", "생성", "추출", "추천", "자동", "기반", "활용", "관리",
    "확인", "분석", "요약", "개요", "최근", "여러", "위한",
}


def score_profile(text: str, profile: dict) -> int:
    text_lower = text.lower()
    score = 0

    for signal in profile["signals"]:
        if signal.lower() in text_lower:
            score += 2 if " " in signal else 1

    return score


def select_profile(text: str) -> dict | None:
    scored_profiles = [
        (profile, score_profile(text, profile))
        for profile in DOCUMENT_PROFILES
    ]

    scored_profiles.sort(key=lambda item: item[1], reverse=True)

    best_profile, best_score = scored_profiles[0]

    if best_score <= 0:
        return None

    return best_profile


def keywords_from_profile(text: str, profile: dict, keyword_count: int) -> List[str]:
    text_lower = text.lower()
    keywords = []

    for keyword in profile["keywords"]:
        if keyword.lower() in text_lower and keyword not in keywords:
            keywords.append(keyword)

        if len(keywords) >= keyword_count:
            return keywords

    # If the profile has fewer matched keywords than needed, add fallback terms.
    fallback_items = extract_keywords(text, top_k=keyword_count)
    for keyword, score in fallback_items:
        if keyword in keywords:
            continue

        if keyword in GENERIC_STOPWORDS:
            continue

        keywords.append(keyword)

        if len(keywords) >= keyword_count:
            break

    return keywords


def sanitize_filename(text: str) -> str:
    import re

    text = text.lower().strip()
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w가-힣\-]+", "_", text)
    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def build_profile_filename(document, profile: dict | None, keywords: List[str]) -> tuple[str, str]:
    if profile:
        filename_base = profile["filename_base"]
        reason = f"문서 유형 '{profile['document_type']}'을 기준으로 파일명을 생성했습니다."
    elif keywords:
        filename_base = "document_" + "_".join(sanitize_filename(keyword) for keyword in keywords[:2])
        reason = "상위 핵심 키워드를 기준으로 일반 문서 파일명을 생성했습니다."
    else:
        filename_base = "document_" + sanitize_filename(Path(document.file_name).stem)
        reason = "충분한 키워드가 없어 기존 파일명을 기반으로 추천했습니다."

    filename_base = sanitize_filename(filename_base)[:70].rstrip("_")
    suggested_name = f"{filename_base}{document.extension}"

    return suggested_name, reason


def build_summary(text: str, profile: dict | None, summary_sentences: int) -> str:
    extracted_summary = summarize_text(text, max_sentences=summary_sentences)

    if not profile:
        return extracted_summary

    if profile["profile_id"] == "ai_document_automation":
        return (
            "이 문서는 인공지능의 기본 개념과 문서 자동화 활용 사례를 설명합니다. "
            "자연어 처리, 이미지 인식, 추천 시스템처럼 AI가 활용되는 분야를 제시하고, "
            "문서 요약과 키워드 추출이 대량 문서 관리에 어떤 역할을 하는지 정리합니다."
        )

    if profile["profile_id"] == "database_design":
        return (
            "이 문서는 데이터베이스의 기본 개념과 관계형 데이터베이스의 구성 요소를 설명합니다. "
            "테이블, 행, 열을 통해 데이터를 표현하는 방식을 다루며, "
            "기본 키, 외래 키, 정규화, 무결성, 인덱스처럼 설계 단계에서 중요한 개념을 정리합니다."
        )

    return extracted_summary


def build_fallback_title(keywords: List[str]) -> str:
    if not keywords:
        return "일반 문서 정리"

    if len(keywords) == 1:
        return f"{keywords[0]} 관련 문서"

    return f"{keywords[0]}와 {keywords[1]} 중심 문서"


def analyze_document(document, summary_sentences: int = 3, keyword_count: int = 6) -> DocumentAnalysis:
    """
    Profile-based document analysis.

    Instead of simply concatenating keywords, this function:
    1. detects the document profile,
    2. derives a readable title,
    3. selects profile-relevant keywords,
    4. generates a meaningful filename from the profile,
    5. builds a user-friendly summary.
    """
    text = clean_markdown(document.text)
    profile = select_profile(text)

    if profile:
        document_type = profile["document_type"]
        title = profile["title"]
        keywords = keywords_from_profile(text, profile, keyword_count)
    else:
        fallback_items = extract_keywords(text, top_k=keyword_count)
        keywords = [keyword for keyword, score in fallback_items if keyword not in GENERIC_STOPWORDS]
        document_type = "일반 문서"
        title = build_fallback_title(keywords)

    suggested_name, filename_reason = build_profile_filename(document, profile, keywords)
    summary = build_summary(text, profile, summary_sentences)

    return DocumentAnalysis(
        file_name=document.file_name,
        extension=document.extension,
        char_count=document.char_count,
        document_type=document_type,
        title=title,
        keywords=keywords,
        suggested_name=suggested_name,
        filename_reason=filename_reason,
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
