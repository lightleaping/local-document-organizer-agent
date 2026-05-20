from dataclasses import dataclass # dataclass : 데이터 수조를 간단히 정의할 수 있게 해주는 데코레이터
from pathlib import Path
from typing import List # List : 타입 힌트용, List[Document] 같은 식으로 사용

import fitz  # PyMuPDF
# PDF 파일에서 텍스트를 추출할 수 있는 라이브러리

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class Document:
    file_path: Path
    file_name: str
    extension: str # 확장자
    text: str # 텍스트 내용
    char_count: int # 글자 수


def read_text_file(file_path: Path) -> str:
    """
    Read text-based files such as .txt and .md.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="cp949")


def read_pdf_file(file_path: Path) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    """
    text_chunks = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text_chunks.append(page.get_text())

    return "\n".join(text_chunks).strip()


def read_document(file_path: Path) -> Document:
    """
    Read a single document and return a Document object.
    """
    extension = file_path.suffix.lower()

    if extension in {".txt", ".md"}:
        text = read_text_file(file_path)
    elif extension == ".pdf":
        text = read_pdf_file(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    text = text.strip()

    return Document(
        file_path=file_path,
        file_name=file_path.name,
        extension=extension,
        text=text,
        char_count=len(text),
    )


def load_documents(input_dir: Path) -> List[Document]:
    """
    Load all supported documents from the input directory.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    documents = []

    for file_path in sorted(input_dir.rglob("*")):
    # rglob("*"): 하위 폴더까지 포함해 모든 파일 탐색.
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            document = read_document(file_path)
            documents.append(document)
        except Exception as error:
            print(f"[WARN] Failed to read {file_path.name}: {error}")

    return documents