import re
from collections import Counter
from typing import List

from src.keyword_extractor import tokenize, clean_markdown


def split_sentences(text: str) -> List[str]:
    """
    Split text into readable sentences.
    """
    text = clean_markdown(text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?。！？다])\s+", text)

    cleaned = []
    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) < 15:
            continue

        if sentence.startswith("|"):
            continue

        cleaned.append(sentence)

    return cleaned


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Create an extractive summary with frequency-based sentence scoring.
    """
    sentences = split_sentences(text)

    if not sentences:
        return "요약할 수 있는 문장이 없습니다."

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    tokens = tokenize(text)
    word_counts = Counter(tokens)

    scored = []

    for index, sentence in enumerate(sentences):
        sentence_tokens = tokenize(sentence)

        if not sentence_tokens:
            score = 0.0
        else:
            frequency_score = sum(word_counts[token] for token in sentence_tokens) / len(sentence_tokens)
            position_bonus = 0.15 if index < 2 else 0.0
            score = frequency_score + position_bonus

        scored.append((index, sentence, score))

    selected = sorted(scored, key=lambda item: item[2], reverse=True)[:max_sentences]
    selected = sorted(selected, key=lambda item: item[0])

    return " ".join(sentence for _, sentence, _ in selected)
