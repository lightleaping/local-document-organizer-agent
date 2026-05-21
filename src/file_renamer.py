from src.document_analyzer import analyze_document


def suggest_filename(document, top_k: int = 6) -> str:
    analysis = analyze_document(document, summary_sentences=3, keyword_count=top_k)
    return analysis.suggested_name


def suggest_filenames(documents) -> dict:
    return {
        document.file_name: suggest_filename(document)
        for document in documents
    }
