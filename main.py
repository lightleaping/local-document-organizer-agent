import argparse
from pathlib import Path

from src.document_loader import load_documents
from src.duplicate_detector import detect_duplicates
from src.report_generator import generate_markdown_report
from src.document_analyzer import analyze_documents


def parse_args():
    parser = argparse.ArgumentParser(
        description="Local Document Organizer Agent"
    )

    parser.add_argument("--input", required=True, help="Path to the input document folder")
    parser.add_argument("--output", required=True, help="Path to the output report folder")
    parser.add_argument("--summary-sentences", type=int, default=3, help="Number of summary sentences")
    parser.add_argument("--keywords", type=int, default=6, help="Number of keywords")
    parser.add_argument("--duplicate-threshold", type=float, default=0.70, help="Duplicate similarity threshold")

    return parser.parse_args()


def print_document_cards(analyses):
    print("\nDocument Analysis")
    print("-" * 60)

    if not analyses:
        print("No supported documents found.")
        return

    for index, analysis in enumerate(analyses, start=1):
        print(f"[{index}] {analysis.file_name}")
        print(f"    문서 제목     : {analysis.title}")
        print(f"    문서 유형     : {analysis.document_type}")
        print(f"    글자 수       : {analysis.char_count}")
        print(f"    핵심 키워드   : {', '.join(analysis.keywords)}")
        print(f"    추천 파일명   : {analysis.suggested_name}")
        print(f"    추천 근거     : {analysis.filename_reason}")
        print(f"    요약          : {analysis.summary}")
        print()


def print_duplicate_candidates(documents, duplicate_threshold: float):
    candidates = detect_duplicates(documents, threshold=duplicate_threshold)

    print("\nDuplicate Candidates")
    print("-" * 60)

    if not candidates:
        print("No duplicate candidates found.")
        return

    for candidate in candidates:
        print(f"- {candidate.file_a} <-> {candidate.file_b} / similarity: {candidate.similarity}")


def main():
    args = parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    print("Local Document Organizer Agent")
    print("=" * 60)
    print(f"Input folder       : {input_dir.resolve()}")
    print(f"Output folder      : {output_dir.resolve()}")
    print(f"Summary sentences  : {args.summary_sentences}")
    print(f"Keyword count      : {args.keywords}")
    print(f"Duplicate threshold: {args.duplicate_threshold}")

    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(input_dir)
    analyses = analyze_documents(
        documents,
        summary_sentences=args.summary_sentences,
        keyword_count=args.keywords,
    )

    print_document_cards(analyses)

    print_duplicate_candidates(
        documents=documents,
        duplicate_threshold=args.duplicate_threshold,
    )

    report_path = generate_markdown_report(
        documents=documents,
        output_dir=output_dir,
        duplicate_threshold=args.duplicate_threshold,
        summary_sentences=args.summary_sentences,
        keyword_count=args.keywords,
    )

    print("\nResult")
    print("-" * 60)
    print(f"Total documents loaded: {len(documents)}")
    print(f"Report generated      : {report_path}")


if __name__ == "__main__":
    main()
