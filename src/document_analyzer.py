from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.keyword_extractor import clean_markdown, extract_keywords
from src.llm_summarizer import summarize_with_ollama
from src.profile_classifier import classify_document
from src.project_utils import (
    detect_project_name,
    filter_keywords_by_project,
    project_readme_filename,
)
from src.summarizer import summarize_by_document_type
from src.text_quality import check_text_quality


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


GENERIC_STOPWORDS = {
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과",
    "사용", "생성", "추출", "추천", "자동", "기반", "활용", "관리",
    "확인", "분석", "요약", "개요", "최근", "여러", "위한",
}


def sanitize_filename(text: str) -> str:
    import re

    text = text.lower().strip()
    text = text.replace(" ", "_")
    text = re.sub(r"[^\w가-힣\-]+", "_", text)
    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def keywords_from_profile(text: str, profile: dict, keyword_count: int) -> List[str]:
    text_lower = text.lower()
    keywords = []

    for keyword in profile.get("keywords", []):
        if keyword.lower() in text_lower and keyword not in keywords:
            keywords.append(keyword)

        if len(keywords) >= keyword_count:
            return keywords

    fallback_items = extract_keywords(text, top_k=keyword_count)

    for keyword, score in fallback_items:
        if keyword in keywords or keyword in GENERIC_STOPWORDS:
            continue

        keywords.append(keyword)

        if len(keywords) >= keyword_count:
            break

    return keywords


def build_title(document_type: str, profile: dict | None, project_name: str | None) -> str:
    if document_type == "프로젝트 README / 기술 문서" and project_name:
        return f"{project_name} README 정리"

    if profile and profile.get("title"):
        return profile["title"]

    return "일반 문서 정리"


def build_profile_filename(
    document,
    profile: dict | None,
    keywords: List[str],
    project_name: str | None = None,
    document_type: str = "",
) -> tuple[str, str]:
    if document_type == "프로젝트 README / 기술 문서" and project_name:
        suggested_name = project_readme_filename(project_name, extension=document.extension)
        return (
            suggested_name,
            f"문서 안에서 감지한 프로젝트명 '{project_name}'을 기준으로 README 파일명을 생성했습니다.",
        )

    if profile and profile.get("profile_id") != "general_document":
        filename_base = profile["filename_base"]
        reason = f"로컬 임베딩 모델이 분류한 문서 유형 '{profile['document_type']}'을 기준으로 파일명을 생성했습니다."
    elif keywords:
        filename_base = "document_" + "_".join(sanitize_filename(keyword) for keyword in keywords[:2])
        reason = "상위 핵심 키워드를 기준으로 일반 문서 파일명을 생성했습니다."
    else:
        filename_base = "document_" + sanitize_filename(Path(document.file_name).stem)
        reason = "충분한 키워드가 없어 기존 파일명을 기반으로 추천했습니다."

    filename_base = sanitize_filename(filename_base)[:70].rstrip("_")
    return f"{filename_base}{document.extension}", reason


def build_extraction_failed_analysis(document, reason: str) -> DocumentAnalysis:
    return DocumentAnalysis(
        file_name=document.file_name,
        extension=document.extension,
        char_count=document.char_count,
        document_type="텍스트 추출 확인 필요",
        title="텍스트 추출 실패 문서",
        keywords=["추출 불가"],
        suggested_name=f"extraction_check_needed{document.extension}",
        filename_reason="문서 텍스트가 깨졌거나 충분히 추출되지 않아 확인용 파일명을 생성했습니다.",
        summary=(
            "문서에서 읽을 수 있는 텍스트가 충분히 추출되지 않아 자동 요약을 생성하지 않았습니다. "
            "PDF가 이미지 기반이거나 글자 인코딩이 깨졌을 가능성이 있습니다. "
            f"감지 사유: {reason}"
        ),
    )


def analyze_document(
    document,
    summary_sentences: int = 3,
    keyword_count: int = 6,
    use_local_llm: bool = False,
    llm_model: str = "qwen2.5:1.5b",
) -> DocumentAnalysis:
    text = clean_markdown(document.text)
    quality = check_text_quality(text, file_extension=document.extension)

    if not quality.is_valid:
        return build_extraction_failed_analysis(document=document, reason=quality.reason)

    profile = classify_document(text=text, file_name=document.file_name)
    document_type = profile["document_type"] if profile else "일반 문서"
    project_name = detect_project_name(text, file_name=document.file_name)

    if profile and profile.get("profile_id") != "general_document":
        keywords = keywords_from_profile(
            text=text,
            profile=profile,
            keyword_count=keyword_count,
        )
    else:
        fallback_items = extract_keywords(text, top_k=keyword_count)
        keywords = [
            keyword
            for keyword, score in fallback_items
            if keyword not in GENERIC_STOPWORDS
        ][:keyword_count]

    if document_type == "프로젝트 README / 기술 문서":
        keywords = filter_keywords_by_project(
            keywords=keywords,
            project_name=project_name,
            max_count=keyword_count,
        )

    title = build_title(
        document_type=document_type,
        profile=profile,
        project_name=project_name,
    )

    suggested_name, filename_reason = build_profile_filename(
        document=document,
        profile=profile,
        keywords=keywords,
        project_name=project_name,
        document_type=document_type,
    )

    summary = None

    if use_local_llm:
        summary = summarize_with_ollama(
            text=text,
            document_type=document_type,
            keywords=keywords,
            model=llm_model,
        )

    if not summary:
        summary = summarize_by_document_type(
            text=text,
            document_type=document_type,
            keywords=keywords,
            file_name=document.file_name,
        )

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


def analyze_documents(
    documents,
    summary_sentences: int = 3,
    keyword_count: int = 6,
    use_local_llm: bool = False,
    llm_model: str = "qwen2.5:1.5b",
) -> List[DocumentAnalysis]:
    results = []

    for document in documents:
        analysis = analyze_document(
            document=document,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
            use_local_llm=use_local_llm,
            llm_model=llm_model,
        )

        if analysis is not None:
            results.append(analysis)

    return results
