from pathlib import Path
import shutil
import tempfile

import pandas as pd
import streamlit as st

from src.document_loader import load_documents
from src.summarizer import summarize_text
from src.keyword_extractor import extract_keywords
from src.duplicate_detector import detect_duplicates
from src.file_renamer import suggest_filenames
from src.report_generator import generate_markdown_report


st.set_page_config(
    page_title="Local Document Organizer Agent",
    page_icon="📁",
    layout="wide",
)


def format_keywords(keywords):
    if not keywords:
        return ""

    return ", ".join([keyword for keyword, score in keywords])


def save_uploaded_files(uploaded_files, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)

    for uploaded_file in uploaded_files:
        file_path = target_dir / uploaded_file.name
        file_path.write_bytes(uploaded_file.getbuffer())


def build_document_table(documents, summary_sentences: int, keyword_count: int):
    filename_suggestions = suggest_filenames(documents)

    rows = []

    for document in documents:
        summary = summarize_text(document.text, max_sentences=summary_sentences)
        keywords = extract_keywords(document.text, top_k=keyword_count)
        suggested_name = filename_suggestions.get(document.file_name, document.file_name)

        rows.append(
            {
                "파일명": document.file_name,
                "형식": document.extension,
                "글자 수": document.char_count,
                "추천 파일명": suggested_name,
                "키워드": format_keywords(keywords),
                "요약": summary,
            }
        )

    return pd.DataFrame(rows)


def main():
    st.title("📁 Local Document Organizer Agent")
    st.caption("PDF, TXT, Markdown 문서를 요약·태깅·파일명 추천·중복 탐지하고 Markdown 리포트로 정리하는 로컬 문서 자동화 도구")

    with st.sidebar:
        st.header("분석 설정")
        summary_sentences = st.slider("요약 문장 수", min_value=1, max_value=5, value=3)
        keyword_count = st.slider("키워드 개수", min_value=3, max_value=10, value=7)
        duplicate_threshold = st.slider(
            "중복 탐지 임계값",
            min_value=0.50,
            max_value=0.95,
            value=0.65,
            step=0.01,
        )

        st.divider()
        st.markdown("### 지원 파일")
        st.write("`.pdf`, `.txt`, `.md`")

    uploaded_files = st.file_uploader(
        "분석할 문서를 업로드하세요",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        st.info("왼쪽 설정을 조정한 뒤 문서를 업로드하면 분석 결과가 표시됩니다.")
        st.markdown(
            """
            #### 이 도구가 하는 일
            - 문서 텍스트 추출
            - 핵심 문장 요약
            - TF-IDF 기반 키워드 추출
            - 추천 파일명 생성
            - 유사 문서 탐지
            - Markdown 리포트 생성
            """
        )
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input_docs"
        output_dir = Path(temp_dir) / "reports"

        save_uploaded_files(uploaded_files, input_dir)
        documents = load_documents(input_dir)

        if not documents:
            st.warning("분석 가능한 문서가 없습니다.")
            return

        st.success(f"{len(documents)}개 문서를 분석했습니다.")

        col1, col2, col3 = st.columns(3)
        col1.metric("문서 수", len(documents))
        col2.metric("요약 문장 수", summary_sentences)
        col3.metric("중복 임계값", duplicate_threshold)

        st.subheader("문서별 분석 결과")
        document_table = build_document_table(
            documents=documents,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
        )
        st.dataframe(document_table, use_container_width=True, hide_index=True)

        st.subheader("중복 의심 문서")
        duplicate_candidates = detect_duplicates(documents, threshold=duplicate_threshold)

        if not duplicate_candidates:
            st.write("중복 의심 문서가 발견되지 않았습니다.")
        else:
            duplicate_rows = [
                {
                    "문서 A": candidate.file_a,
                    "문서 B": candidate.file_b,
                    "유사도": candidate.similarity,
                }
                for candidate in duplicate_candidates
            ]
            st.dataframe(pd.DataFrame(duplicate_rows), use_container_width=True, hide_index=True)

        report_path = generate_markdown_report(
            documents=documents,
            output_dir=output_dir,
            duplicate_threshold=duplicate_threshold,
            summary_sentences=summary_sentences,
            keyword_count=keyword_count,
        )

        report_text = report_path.read_text(encoding="utf-8")

        st.subheader("Markdown 리포트 미리보기")
        st.markdown(report_text)

        st.download_button(
            label="Markdown 리포트 다운로드",
            data=report_text,
            file_name="document_report.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
