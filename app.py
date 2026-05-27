import streamlit as st

from src.document_analyzer import analyze_documents
from src.document_loader import load_uploaded_documents
import src.duplicate_detector as duplicate_detector


st.set_page_config(
    page_title="Local Document Organizer Agent",
    page_icon="📁",
    layout="wide",
)


def render_metric_cards(total_docs: int, duplicate_count: int, keyword_count: int) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("문서 수", total_docs)
    col2.metric("중복 후보", duplicate_count)
    col3.metric("키워드 수", keyword_count)


def render_keywords(keywords) -> None:
    if not keywords:
        st.write("키워드 없음")
        return

    for keyword in keywords:
        st.markdown(f"- `{keyword}`")


def render_document_card(analysis, index: int) -> None:
    if analysis is None:
        st.warning(f"{index}. 이 문서는 분석 결과를 생성하지 못했습니다.")
        return

    st.markdown(f"### {index}. {analysis.title}")
    st.caption(analysis.file_name)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**문서 유형**")
        st.write(analysis.document_type)

        st.markdown("**글자 수**")
        st.write(f"{analysis.char_count:,}")

        st.markdown("**추천 파일명**")
        st.code(analysis.suggested_name)
        st.caption(analysis.filename_reason)

    with col2:
        st.markdown("**핵심 키워드**")
        render_keywords(analysis.keywords)

    st.markdown("**요약**")
    st.write(analysis.summary)

    st.divider()


def normalize_duplicate_candidate(candidate):
    if isinstance(candidate, tuple):
        if len(candidate) == 3:
            return str(candidate[0]), str(candidate[1]), float(candidate[2])
        if len(candidate) == 2:
            pair, score = candidate
            return str(pair), "", float(score)

    if isinstance(candidate, dict):
        left = (
            candidate.get("file_a")
            or candidate.get("left")
            or candidate.get("doc1")
            or candidate.get("document_a")
            or "문서 A"
        )
        right = (
            candidate.get("file_b")
            or candidate.get("right")
            or candidate.get("doc2")
            or candidate.get("document_b")
            or "문서 B"
        )
        score = (
            candidate.get("score")
            or candidate.get("similarity")
            or candidate.get("similarity_score")
            or 0
        )
        return str(left), str(right), float(score)

    return str(candidate), "", 0.0


def render_duplicate_candidates(duplicate_candidates) -> None:
    st.subheader("중복 의심 문서")

    if not duplicate_candidates:
        st.info("중복 의심 문서가 발견되지 않았습니다.")
        return

    for candidate in duplicate_candidates:
        left, right, score = normalize_duplicate_candidate(candidate)

        if right:
            st.warning(f"{left} ↔ {right}")
        else:
            st.warning(left)

        st.caption(f"유사도: {score:.4f}")


def safe_find_duplicates(documents):
    candidate_function_names = [
        "find_duplicate_candidates",
        "find_duplicates",
        "detect_duplicates",
        "find_duplicate_documents",
        "detect_duplicate_candidates",
    ]

    for function_name in candidate_function_names:
        function = getattr(duplicate_detector, function_name, None)

        if function is None:
            continue

        try:
            return function(documents)
        except TypeError:
            for kwargs in ({"threshold": 0.5}, {"similarity_threshold": 0.5}):
                try:
                    return function(documents, **kwargs)
                except TypeError:
                    continue
                except Exception as error:
                    st.warning(f"중복 후보 탐지 중 오류가 발생했습니다: {error}")
                    return []
        except Exception as error:
            st.warning(f"중복 후보 탐지 중 오류가 발생했습니다: {error}")
            return []

    st.info("중복 후보 탐지 함수를 찾지 못해 중복 탐지를 건너뛰었습니다.")
    return []


def generate_report_text(analyses, duplicate_candidates) -> str:
    lines = [
        "# 문서 정리 분석 리포트",
        "",
        "## 1. 전체 요약",
        "",
        f"- 분석 문서 수: {len(analyses)}개",
        f"- 중복 의심 문서: {len(duplicate_candidates)}건",
        "- 처리 방식: 문서 로딩 → 텍스트 품질 검사 → 로컬 임베딩 기반 문서 유형 분류 → 키워드/요약/추천 파일명 생성",
        "",
        "## 2. 문서별 정리",
        "",
    ]

    for index, analysis in enumerate(analyses, start=1):
        if analysis is None:
            continue

        lines.extend(
            [
                f"### {index}. {analysis.file_name}",
                "",
                f"- 문서 제목: {analysis.title}",
                f"- 문서 유형: {analysis.document_type}",
                f"- 글자 수: {analysis.char_count}",
                f"- 핵심 키워드: {', '.join(analysis.keywords) if analysis.keywords else '없음'}",
                f"- 추천 파일명: `{analysis.suggested_name}`",
                f"- 추천 근거: {analysis.filename_reason}",
                "",
                "**요약**",
                "",
                analysis.summary,
                "",
            ]
        )

    lines.extend(["## 3. 중복 의심 문서", ""])

    if duplicate_candidates:
        for candidate in duplicate_candidates:
            left, right, score = normalize_duplicate_candidate(candidate)
            if right:
                lines.append(f"- {left} ↔ {right} / 유사도: {score:.4f}")
            else:
                lines.append(f"- {left} / 유사도: {score:.4f}")
    else:
        lines.append("- 중복 의심 문서가 발견되지 않았습니다.")

    lines.extend(
        [
            "",
            "## 4. 처리 기준",
            "",
            "- 같은 파일명으로 업로드된 문서는 내부 표시명을 다르게 생성해 각각 분석합니다.",
            "- PDF/TXT/Markdown에서 추출된 텍스트 품질을 먼저 확인합니다.",
            "- 깨진 텍스트는 무리하게 요약하지 않고 확인 필요 문서로 분리합니다.",
            "- 정상 텍스트는 로컬 임베딩 기반 문서 유형 분류 후 키워드와 요약을 생성합니다.",
            "- 로컬 LLM 요약 모드는 선택 기능이며, 실패 시 기본 추출형 요약으로 자동 대체합니다.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    st.title("📁 Local Document Organizer Agent")
    st.write(
        "문서를 업로드하면 문서 유형, 제목, 핵심 키워드, 추천 파일명, 요약, 중복 후보를 정리합니다."
    )

    with st.sidebar:
        st.header("분석 옵션")
        use_local_llm = st.checkbox(
            "로컬 LLM 요약 사용",
            value=False,
            help="Ollama가 실행 중일 때만 사용하세요. 실패하면 기본 추출형 요약으로 자동 대체됩니다.",
        )
        llm_model = st.text_input(
            "Ollama 모델명",
            value="qwen2.5:1.5b",
            help="예: qwen2.5:1.5b, llama3.2:1b, gemma2:2b",
        )
        st.caption("기본 모드는 외부 API 없이 로컬 임베딩 + 추출형 요약으로 동작합니다.")

    uploaded_files = st.file_uploader(
        "분석할 문서를 업로드하세요",
        type=["txt", "md", "markdown", "pdf"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("TXT, Markdown, PDF 문서를 업로드하면 분석 결과가 표시됩니다.")
        return

    with st.spinner("문서를 읽고 분석하는 중입니다..."):
        documents = load_uploaded_documents(uploaded_files)

        if not documents:
            st.error("분석 가능한 문서를 읽지 못했습니다.")
            return

        analyses = analyze_documents(
            documents,
            use_local_llm=use_local_llm,
            llm_model=llm_model,
        )
        duplicate_candidates = safe_find_duplicates(documents)

    st.success(f"{len(documents)}개 문서를 분석했습니다.")

    total_keyword_count = sum(
        len(analysis.keywords)
        for analysis in analyses
        if analysis and analysis.keywords
    )

    render_metric_cards(
        total_docs=len(documents),
        duplicate_count=len(duplicate_candidates),
        keyword_count=total_keyword_count,
    )

    st.subheader("문서별 분석 결과")

    for index, analysis in enumerate(analyses, start=1):
        render_document_card(analysis, index)

    render_duplicate_candidates(duplicate_candidates)

    st.subheader("Markdown 리포트")
    report = generate_report_text(analyses, duplicate_candidates)

    st.markdown("**리포트 미리보기**")
    st.markdown(report)

    st.download_button(
        label="Markdown 리포트 다운로드",
        data=report,
        file_name="document_organizer_report.md",
        mime="text/markdown",
    )


if __name__ == "__main__":
    main()
