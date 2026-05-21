from dataclasses import dataclass
from pathlib import Path
from typing import List

import fitz  # PyMuPDF


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
IGNORED_DIR_NAMES = {".git", ".venv", "venv", "env", "__pycache__", "reports"}


@dataclass
class Document:
    file_path: Path
    file_name: str
    extension: str
    text: str
    char_count: int


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


def is_ignored_path(file_path: Path) -> bool:
    """
    Skip virtual environments, cache folders, git folders, and output folders.
    """
    return any(part in IGNORED_DIR_NAMES for part in file_path.parts)


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
        if not file_path.is_file():
            continue

        if is_ignored_path(file_path):
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            document = read_document(file_path)
            documents.append(document)
        except Exception as error:
            print(f"[WARN] Failed to read {file_path.name}: {error}")

    return documents
