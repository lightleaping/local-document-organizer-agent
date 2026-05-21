from pathlib import Path
from typing import List

from src.summarizer import summarize_text
from src.keyword_extractor import extract_keywords
from src.duplicate_detector import detect_duplicates
from src.file_renamer import suggest_filenames


def format_keywords(keywords) -> str:
    """
    Convert keyword tuples into a readable string.
    """
    if not keywords:
        return "키워드를 추출할 수 없습니다."

    return ", ".join([keyword for keyword, score in keywords])


def count_extensions(documents) -> dict:
    """
    Count documents by file extension.
    """
    extension_counts = {}

    for document in documents:
        extension_counts[document.extension] = extension_counts.get(document.extension, 0) + 1
        # 이렇게 하면 키가 없을 때는 0부터 시작해서 +1, 있으면 기존 값에 +1을 더해주면서 카운팅이 됩니다.
    return extension_counts


def generate_markdown_report(documents, output_dir: Path, duplicate_threshold: float = 0.75) -> Path:
    """
    Generate a Markdown report from analyzed documents.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "document_report.md"

    extension_counts = count_extensions(documents)
    duplicate_candidates = detect_duplicates(
        documents,
        threshold=duplicate_threshold
    )
    filename_suggestions = suggest_filenames(documents)

    lines: List[str] = []

    lines.append("# Local Document Organizer Report")
    lines.append("")
    lines.append("## 1. 분석 개요")
    lines.append("")
    lines.append(f"- 총 문서 수: {len(documents)}개")

    for extension, count in sorted(extension_counts.items()):
        lines.append(f"- {extension}: {count}개")

    lines.append("")
    lines.append("## 2. 문서별 분석 결과")
    lines.append("")

    if not documents:
        lines.append("분석할 문서가 없습니다.")
    else:
        for index, document in enumerate(documents, start=1):
            summary = summarize_text(document.text, max_sentences=2)
            keywords = extract_keywords(document.text, top_k=5)
            suggested_name = filename_suggestions.get(document.file_name, document.file_name)

            lines.append(f"### {index}. {document.file_name}")
            lines.append("")
            lines.append(f"- 파일 형식: `{document.extension}`")
            lines.append(f"- 글자 수: {document.char_count}")
            lines.append(f"- 파일 경로: `{document.file_path}`")
            lines.append(f"- 추천 파일명: `{suggested_name}`")
            lines.append(f"- 요약: {summary}")
            lines.append(f"- 키워드: {format_keywords(keywords)}")
            lines.append("")

    lines.append("## 3. 중복 의심 문서")
    lines.append("")

    if not duplicate_candidates:
        lines.append("중복 의심 문서가 발견되지 않았습니다.")
    else:
        for candidate in duplicate_candidates:
            lines.append(
                f"- `{candidate.file_a}` ↔ `{candidate.file_b}` "
                f"/ similarity: `{candidate.similarity}`"
            )

    lines.append("")
    lines.append("## 4. 처리 방식")
    lines.append("")
    lines.append("- 문서 로딩: PDF, TXT, Markdown 파일을 읽어 텍스트로 변환")
    lines.append("- 요약: 단어 빈도 기반 문장 점수를 계산하여 핵심 문장 추출")
    lines.append("- 키워드 추출: TF-IDF 기반 주요 단어 추출")
    lines.append("- 파일명 추천: 추출 키워드를 조합하여 안전한 파일명 후보 생성")
    lines.append("- 중복 탐지: 문자 n-gram 기반 TF-IDF 벡터와 cosine similarity 사용")
    lines.append("")
    lines.append("## 5. 한계 및 개선 가능성")
    lines.append("")
    lines.append("- 현재 요약은 생성형 요약이 아니라 추출식 요약 방식입니다.")
    lines.append("- 파일명 추천은 실제 파일을 변경하지 않고 후보명만 제공합니다.")
    lines.append("- 한국어 형태소 분석기를 사용하지 않아 조사나 어미가 포함된 키워드가 나올 수 있습니다.")
    lines.append("- 향후 kiwipiepy, sentence-transformers, 로컬 LLM 등을 활용하여 품질을 개선할 수 있습니다.")
    lines.append("")
    
    report_path.write_text("\n".join(lines), encoding="utf-8")
    lines.append(f"- 추천 파일명: `{suggested_name}`")
    return report_path

