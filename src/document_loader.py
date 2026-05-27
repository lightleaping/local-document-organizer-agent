from dataclasses import dataclass
from pathlib import Path
from typing import List
import hashlib
import tempfile

import fitz  # PyMuPDF


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}
IGNORED_DIR_NAMES = {".git", ".venv", "venv", "env", "__pycache__", "reports"}


@dataclass
class Document:
    file_path: Path
    file_name: str
    extension: str
    text: str
    char_count: int
    document_id: str = ""


def make_document_id(file_name: str, content: bytes, index: int = 0) -> str:
    digest = hashlib.md5(content).hexdigest()[:8]
    stem = Path(file_name).stem
    suffix = Path(file_name).suffix.lower()

    if index > 0:
        return f"{stem}_{index}_{digest}{suffix}"

    return f"{stem}_{digest}{suffix}"


def make_unique_display_name(file_name: str, content: bytes, seen_names: dict) -> str:
    path = Path(file_name)
    stem = path.stem
    suffix = path.suffix

    count = seen_names.get(file_name, 0) + 1
    seen_names[file_name] = count

    if count == 1:
        return file_name

    digest = hashlib.md5(content).hexdigest()[:6]
    return f"{stem}_{count}_{digest}{suffix}"


def read_text_file(file_path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return file_path.read_text(encoding="utf-8", errors="replace")


def read_text_bytes(content: bytes) -> str:
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue

    return content.decode("utf-8", errors="replace")


def read_pdf_file(file_path: Path) -> str:
    text_chunks = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text_chunks.append(page.get_text())

    return "\n".join(text_chunks).strip()


def read_pdf_bytes(content: bytes) -> str:
    text_chunks = []

    with fitz.open(stream=content, filetype="pdf") as pdf:
        for page in pdf:
            text_chunks.append(page.get_text())

    return "\n".join(text_chunks).strip()


def is_ignored_path(file_path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in file_path.parts)


def read_document(file_path: Path) -> Document:
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {extension}")

    if extension in {".txt", ".md", ".markdown"}:
        text = read_text_file(file_path)
    elif extension == ".pdf":
        text = read_pdf_file(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    text = text.strip()

    try:
        content = file_path.read_bytes()
    except Exception:
        content = text.encode("utf-8", errors="replace")

    document_id = make_document_id(
        file_name=file_path.name,
        content=content,
    )

    return Document(
        file_path=file_path,
        file_name=file_path.name,
        extension=extension,
        text=text,
        char_count=len(text),
        document_id=document_id,
    )


def load_documents(input_dir: Path) -> List[Document]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    documents = []
    seen_names = {}

    for file_path in sorted(input_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if is_ignored_path(file_path):
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            document = read_document(file_path)
            content = file_path.read_bytes()
            document.file_name = make_unique_display_name(
                file_name=document.file_name,
                content=content,
                seen_names=seen_names,
            )
            documents.append(document)
        except Exception as error:
            print(f"[WARN] Failed to read {file_path.name}: {error}")

    return documents


def read_uploaded_document(uploaded_file, index: int, seen_names: dict) -> Document:
    original_name = uploaded_file.name
    extension = Path(original_name).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {extension}")

    content = uploaded_file.getvalue()
    display_name = make_unique_display_name(
        file_name=original_name,
        content=content,
        seen_names=seen_names,
    )
    document_id = make_document_id(
        file_name=original_name,
        content=content,
        index=index,
    )

    if extension in {".txt", ".md", ".markdown"}:
        text = read_text_bytes(content)
    elif extension == ".pdf":
        text = read_pdf_bytes(content)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    text = text.strip()
    temp_path = Path(tempfile.gettempdir()) / display_name

    return Document(
        file_path=temp_path,
        file_name=display_name,
        extension=extension,
        text=text,
        char_count=len(text),
        document_id=document_id,
    )


def load_uploaded_documents(uploaded_files) -> List[Document]:
    documents = []
    seen_names = {}

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        try:
            document = read_uploaded_document(
                uploaded_file=uploaded_file,
                index=index,
                seen_names=seen_names,
            )
            documents.append(document)
        except Exception as error:
            print(f"[WARN] Failed to read {uploaded_file.name}: {error}")

    return documents
