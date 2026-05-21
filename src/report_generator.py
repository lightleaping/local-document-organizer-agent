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
    lines.append(f"- 요약 문장 수: **{summary_sentences}개**")
    lines.append(f"- 키워드 개수: **{keyword_count}개**")
    lines.append("")
    lines.append("대표 주제, 추천 파일명, 핵심 키워드는 동일한 키워드 순위 결과를 기준으로 생성했습니다.")
    lines.append("")

    lines.append("## 2. 문서별 정리")
    lines.append("")

    for index, analysis in enumerate(analyses, start=1):
        lines.append(f"### {index}. {analysis.file_name}")
        lines.append("")
        lines.append(f"- 글자 수: {analysis.char_count}")
        lines.append(f"- 대표 주제: **{analysis.topic}**")
        lines.append(f"- 핵심 키워드: {', '.join(analysis.keywords)}")
        lines.append(f"- 추천 파일명: `{analysis.suggested_name}`")
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
    lines.append("- 핵심 키워드는 복합 표현을 우선하고, 일반 불용어와 조사를 제거해 중요도 순으로 정렬했습니다.")
    lines.append("- 대표 주제는 핵심 키워드의 도메인 신호를 기준으로 판단했습니다.")
    lines.append("- 추천 파일명은 대표 주제와 상위 핵심 키워드를 함께 사용합니다.")
    lines.append("- 요약은 문서 내부 문장 중 중요도가 높은 문장을 추출합니다.")
    lines.append("- 원본 파일은 직접 변경하지 않고 추천 결과만 제공합니다.")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return report_path
