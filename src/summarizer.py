import re
from collections import Counter
from typing import List


STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "수", "등", "및", "에서", "으로", "에게",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
}


def clean_markdown(text: str) -> str:
    """
    Remove simple Markdown syntax before summarization.
    Markdown headings are excluded from summary text.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Exclude Markdown headings entirely: # Title, ## Title
        if re.match(r"^#{1,6}\s+", line):
            continue

        # Remove Markdown list markers: -, *, +
        line = re.sub(r"^[-*+]\s+", "", line)

        # Remove bold/italic markers
        line = line.replace("**", "").replace("__", "").replace("*", "")

        cleaned_lines.append(line)

    return " ".join(cleaned_lines)


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using Korean/English punctuation.
    """
    text = clean_markdown(text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?。！？다])\s+", text)

    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()

        # Exclude very short title-like fragments
        if len(sentence) < 15:
            continue

        cleaned_sentences.append(sentence)

    return cleaned_sentences


def tokenize(text: str) -> List[str]:
    """
    Simple tokenizer for Korean/English mixed text.
    """
    text = clean_markdown(text)
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", text.lower())

    return [
        token for token in tokens
        if len(token) >= 2 and token not in STOPWORDS
    ]


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Create an extractive summary by scoring sentences with word frequency.
    """
    sentences = split_sentences(text)

    if not sentences:
        return "요약할 수 있는 문장이 없습니다."

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    all_tokens = tokenize(text)
    word_counts = Counter(all_tokens)

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        sentence_tokens = tokenize(sentence)

        if not sentence_tokens:
            score = 0
        else:
            score = sum(word_counts[token] for token in sentence_tokens) / len(sentence_tokens)

        scored_sentences.append((index, sentence, score))

    top_sentences = sorted(
        scored_sentences,
        key=lambda item: item[2],
        reverse=True
    )[:max_sentences]

    top_sentences = sorted(top_sentences, key=lambda item: item[0])

    summary = " ".join(sentence for _, sentence, _ in top_sentences)

    return summary