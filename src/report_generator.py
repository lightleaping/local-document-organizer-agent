from pathlib import Path
from typing import List

from src.duplicate_detector import detect_duplicates
from src.document_analyzer import analyze_documents


def generate_markdown_report(
    documents,
    output_dir: Path,
    duplicate_threshold: float = 0.70,
    summary_sentences: int = 3,
    keyword_count: int = 6,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "document_report.md"

    analyses = analyze_documents(
        documents,
        summary_sentences=summary_sentences,
        keyword_count=keyword_count,
    )
    duplicate_candidates = detect_duplicates(documents, threshold=duplicate_threshold)

    lines: List[str] = []

    lines.append("# 문서 정리 분석 리포트")
    lines.append("")
    lines.append("## 1. 전체 요약")
    lines.append("")
    lines.append(f"- 분석 문서 수: **{len(documents)}개**")
    lines.append(f"- 중복 의심 문서: **{len(duplicate_candidates)}건**")
    lines.append("")
    lines.append("이 리포트는 문서 유형을 먼저 판정한 뒤, 유형에 맞는 제목, 핵심 키워드, 추천 파일명, 요약을 생성합니다.")
    lines.append("")

    lines.append("## 2. 문서별 정리")
    lines.append("")

    for index, analysis in enumerate(analyses, start=1):
        lines.append(f"### {index}. {analysis.file_name}")
        lines.append("")
        lines.append(f"- 문서 제목: **{analysis.title}**")
        lines.append(f"- 문서 유형: {analysis.document_type}")
        lines.append(f"- 글자 수: {analysis.char_count}")
        lines.append(f"- 핵심 키워드: {', '.join(analysis.keywords)}")
        lines.append(f"- 추천 파일명: `{analysis.suggested_name}`")
        lines.append(f"- 추천 근거: {analysis.filename_reason}")
        lines.append(f"- 요약: {analysis.summary}")
        lines.append("")

    lines.append("## 3. 중복 의심 문서")
    lines.append("")

    if not duplicate_candidates:
        lines.append("중복 의심 문서가 발견되지 않았습니다.")
    else:
        for candidate in duplicate_candidates:
            lines.append(f"- `{candidate.file_a}` ↔ `{candidate.file_b}` / 유사도: `{candidate.similarity}`")

    lines.append("")
    lines.append("## 4. 처리 기준")
    lines.append("")
    lines.append("- 단순 키워드 나열이 아니라 문서 유형을 먼저 판정합니다.")
    lines.append("- 추천 파일명은 핵심 키워드 전체를 이어 붙이지 않고 문서 유형별 이름 규칙을 사용합니다.")
    lines.append("- 핵심 키워드는 문서 유형을 설명하는 주요 개념만 선별합니다.")
    lines.append("- 요약은 사용자가 문서 내용을 빠르게 이해할 수 있도록 문장형으로 정리합니다.")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return report_path
