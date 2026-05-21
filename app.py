from pathlib import Path
import tempfile

import streamlit as st

from src.document_loader import load_documents
from src.duplicate_detector import detect_duplicates
from src.document_analyzer import analyze_documents
from src.report_generator import generate_markdown_report


st.set_page_config(
    page_title="Local Document Organizer Agent",
    page_icon="📁",
    layout="wide",
)


def save_uploaded_files(uploaded_files, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)

    for uploaded_file in uploaded_files:
        file_path = target_dir / uploaded_file.name
        file_path.write_bytes(uploaded_file.getbuffer())


def render_keyword_chips(keywords):
    if not keywords:
        st.caption("키워드를 추출하지 못했습니다.")
        return

    chip_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; margin-bottom:8px;'>"

    for keyword in keywords:
        chip_html += (
            "<span style='"
            "background:#dbeafe;"
            "color:#111827;"
            "border:1px solid #2563eb;"
            "border-radius:999px;"
            "padding:6px 12px;"
            "font-size:0.92rem;"
            "font-weight:700;"
            "white-space:nowrap;"
            "'>"
            f"{keyword}"
            "</span>"
        )

    chip_html += "</div>"
    st.markdown(chip_html, unsafe_allow_html=True)


def render_document_card(analysis, index: int):
    with st.container(border=True):
        st.markdown(f"### {index}. {analysis.title}")
        st.caption(analysis.file_name)

        col1, col2, col3 = st.columns([1.2, 1, 2])

        with col1:
            st.metric("문서 유형", analysis.document_type)

        with col2:
            st.metric("글자 수", f"{analysis.char_count:,}")

        with col3:
            st.markdown("**추천 파일명**")
            st.code(analysis.suggested_name, language=None)

        st.caption(analysis.filename_reason)

        st.markdown("**핵심 키워드**")
        render_keyword_chips(analysis.keywords)

        st.markdown("**요약**")
        st.write(analysis.summary)


def main():
    st.title("📁 Local Document Organizer Agent")
    st.caption("문서를 업로드하면 문서 유형, 제목, 핵심 키워드, 추천 파일명, 요약, 중복 후보를 정리합니다.")

    with st.sidebar:
        st.header("분석 설정")
        summary_sentences = st.slider("요약 문장 수", min_value=1, max_value=5, value=3)
        keyword_count = st.slider("키워드 개수", min_value=3, max_value=10, value=6)
        duplicate_threshold = st.slider(
            "중복 탐지 임계값",
            min_value=0.50,
            max_value=0.95,
            value=0.65,
            step=0.01,
        )

        st.divider()
        st.markdown("### 분석 방식")
        st.write("1. 문서 유형 판정")
        st.write("2. 유형별 제목 생성")
        st.write("3. 핵심 개념 선별")
        st.write("4. 유형 기반 파일명 추천")
        st.write("5. 문장형 요약 생성")

    uploaded_files = st.file_uploader(
        "분석할 문서를 업로드하세요",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("문서를 업로드하면 문서별 카드 형태로 결과가 표시됩니다.")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input_docs"
        output_dir = Path(temp_dir) / "reports"

        save_uploaded_files(uploaded_files, input_dir)
        documents = load_documents(input_dir)

        if not documents:
            st.warning("분석 가능한 문서가 없습니다.")
            return

        analyses = analyze_documents(
            documents,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
        )
        duplicate_candidates = detect_duplicates(documents, threshold=duplicate_threshold)

        st.success(f"{len(documents)}개 문서를 분석했습니다.")

        col1, col2, col3 = st.columns(3)
        col1.metric("문서 수", len(documents))
        col2.metric("중복 후보", len(duplicate_candidates))
        col3.metric("키워드 수", keyword_count)

        st.divider()

        st.subheader("문서별 분석 결과")
        for index, analysis in enumerate(analyses, start=1):
            render_document_card(analysis, index)

        st.divider()

        st.subheader("중복 의심 문서")
        if not duplicate_candidates:
            st.info("중복 의심 문서가 발견되지 않았습니다.")
        else:
            for candidate in duplicate_candidates:
                with st.container(border=True):
                    st.markdown(f"**{candidate.file_a}** ↔ **{candidate.file_b}**")
                    st.progress(min(candidate.similarity, 1.0))
                    st.caption(f"유사도: {candidate.similarity}")

        report_path = generate_markdown_report(
            documents=documents,
            output_dir=output_dir,
            duplicate_threshold=duplicate_threshold,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
        )

        report_text = report_path.read_text(encoding="utf-8")

        st.divider()
        st.subheader("Markdown 리포트")
        with st.expander("리포트 미리보기", expanded=False):
            st.markdown(report_text)

        st.download_button(
            label="Markdown 리포트 다운로드",
            data=report_text,
            file_name="document_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
