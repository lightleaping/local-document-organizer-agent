import argparse # argparse : 명령줄 인자를 쉽게 처리할 수 있도록 도와주는 파이썬 표준 라이브러리
from pathlib import Path # Path : 파일 경로를 객체로 다룰 수 있게 해주는 pathlib 모듈의 클래스

from src.document_loader import load_documents
from src.summarizer import summarize_text
from src.keyword_extractor import extract_keywords
from src.duplicate_detector import detect_duplicates


def parse_args():
    parser = argparse.ArgumentParser(
        description="Local Document Organizer Agent"
    )
    # ArgumentParser 객체를 생성하면서 프로그램 설명(description)을 추가

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input document folder"
    )
    # --input 옵션을 추가
    # 필수(required=True) 인자로, 입력 문서 폴더 경로를 받음
    # help는 사용자가 --help를 입력했을 때 보여줄 설명.

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output report folder"
    )
    # --output 옵션을 추가.
    # 필수 인자로, 결과 보고서를 저장할 폴더 경로를 받음.

    return parser.parse_args()
    # 실제로 명령줄 인자를 파싱해서 반환

def format_keywords(keywords):
    if not keywords:
        return "키워드를 추출할 수 없습니다."

    return ", ".join([keyword for keyword, score in keywords])


def print_document_summary(documents):
    print("\nLoaded Documents")
    print("-" * 40)

    if not documents:
        print("No supported documents found.")
        return

    for index, document in enumerate(documents, start=1):
        summary = summarize_text(document.text, max_sentences=2)
        keywords = extract_keywords(document.text, top_k=5)

        print(f"{index}. {document.file_name}")
        print(f"   Extension  : {document.extension}")
        print(f"   Characters : {document.char_count}")
        print(f"   Path       : {document.file_path}")
        print(f"   Summary    : {summary}")
        print(f"   Keywords   : {format_keywords(keywords)}")
        print()

def print_duplicate_candidates(documents):
    candidates = detect_duplicates(documents, threshold=0.85)

    print("\nDuplicate Candidates")
    print("-" * 40)

    if not candidates:
        print("No duplicate candidates found.")
        return

    for candidate in candidates:
        print(f"{candidate.file_a} <-> {candidate.file_b}")
        print(f"Similarity: {candidate.similarity}")
        print()

def main():
    args = parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    print("Local Document Organizer Agent")
    print("=" * 40)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    # 출력 폴더 생성.
    # parents=True : 상위 폴더까지 자동 생성
    # exist_ok=True : 이미 폴더가 있어도 에러 없이 넘어감

    print(f"Input folder : {input_dir.resolve()}")
    print(f"Output folder: {output_dir.resolve()}")
    # 입력/출력 폴더의 절대 경로(resolve())를 출력.
    
    documents = load_documents(input_dir)
    print_document_summary(documents)
    print_duplicate_candidates(documents)

    print(f"Total documents loaded: {len(documents)}")

if __name__ == "__main__":
    main()
# 이 파일이 직접 실행될 때만 main() 함수 실행.
# 다른 모듈에서 import 될 경우에는 실행되지 않음.