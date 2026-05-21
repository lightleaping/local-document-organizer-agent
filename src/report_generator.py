from pathlib import Path
from typing import List

from src.summarizer import summarize_text
from src.keyword_extractor import extract_keywords
from src.duplicate_detector import detect_duplicates
from src.file_renamer import suggest_filenames


def format_keywords(keywords) -> str:
    if not keywords:
        return "키워드를 추출할 수 없습니다."

    return ", ".join([keyword for keyword, score in keywords])


def count_extensions(documents) -> dict:
    extension_counts = {}

    for document in documents:
        extension_counts[document.extension] = extension_counts.get(document.extension, 0) + 1

    return extension_counts


def generate_markdown_report(
    documents,
    output_dir: Path,
    duplicate_threshold: float = 0.70,
    summary_sentences: int = 3,
    keyword_count: int = 7,
) -> Path:
    """
    Generate a user-friendly Markdown report from analyzed documents.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "document_report.md"

    extension_counts = count_extensions(documents)
    duplicate_candidates = detect_duplicates(documents, threshold=duplicate_threshold)
    filename_suggestions = suggest_filenames(documents)

    lines: List[str] = []

    lines.append("# 문서 정리 분석 리포트")
    lines.append("")
    lines.append("## 1. 전체 요약")
    lines.append("")
    lines.append(f"- 분석 문서 수: **{len(documents)}개**")
    lines.append(f"- 요약 문장 수: **{summary_sentences}개**")
    lines.append(f"- 키워드 개수: **{keyword_count}개**")
    lines.append(f"- 중복 탐지 임계값: **{duplicate_threshold}**")

    if extension_counts:
        extension_text = ", ".join(
            [f"{extension} {count}개" for extension, count in sorted(extension_counts.items())]
        )
        lines.append(f"- 파일 형식 분포: {extension_text}")

    lines.append("")
    lines.append("## 2. 문서 정리 표")
    lines.append("")
    lines.append("| 원본 파일명 | 추천 파일명 | 글자 수 | 핵심 키워드 |")
    lines.append("|---|---|---:|---|")

    document_results = []

    for document in documents:
        keywords = extract_keywords(document.text, top_k=keyword_count)
        keyword_text = format_keywords(keywords)
        suggested_name = filename_suggestions.get(document.file_name, document.file_name)
        summary = summarize_text(document.text, max_sentences=summary_sentences)

        document_results.append((document, suggested_name, keyword_text, summary))

        lines.append(
            f"| `{document.file_name}` | `{suggested_name}` | {document.char_count} | {keyword_text} |"
        )

    lines.append("")
    lines.append("## 3. 문서별 요약")
    lines.append("")

    for index, (document, suggested_name, keyword_text, summary) in enumerate(document_results, start=1):
        lines.append(f"### {index}. {document.file_name}")
        lines.append("")
        lines.append(f"- 추천 파일명: `{suggested_name}`")
        lines.append(f"- 핵심 키워드: {keyword_text}")
        lines.append(f"- 요약: {summary}")
        lines.append("")

    lines.append("## 4. 중복 의심 문서")
    lines.append("")

    if not duplicate_candidates:
        lines.append("중복 의심 문서가 발견되지 않았습니다.")
    else:
        lines.append("| 문서 A | 문서 B | 유사도 |")
        lines.append("|---|---|---:|")

        for candidate in duplicate_candidates:
            lines.append(f"| `{candidate.file_a}` | `{candidate.file_b}` | `{candidate.similarity}` |")

    lines.append("")
    lines.append("## 5. 처리 기준")
    lines.append("")
    lines.append("- 요약: 문서 내부 문장 중 중요도가 높은 문장을 추출합니다.")
    lines.append("- 키워드: 복합 도메인 표현을 우선 추출하고, 조사 제거 후 핵심 단어를 보완합니다.")
    lines.append("- 추천 파일명: 문서 유형과 핵심 키워드를 조합하되 실제 파일은 변경하지 않습니다.")
    lines.append("- 중복 탐지: 문자 n-gram TF-IDF와 cosine similarity를 사용합니다.")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return report_path
