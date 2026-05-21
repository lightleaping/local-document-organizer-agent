import re
from collections import Counter
from typing import List

from src.keyword_extractor import tokenize, clean_markdown


def split_sentences(text: str) -> List[str]:
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


def summarize_text(text: str, max_sentences: int = 2, max_chars: int = 180) -> str:
    """
    Create a concise extractive summary.
    """
    sentences = split_sentences(text)

    if not sentences:
        return "요약할 수 있는 문장이 없습니다."

    if len(sentences) <= max_sentences:
        summary = " ".join(sentences)
        return trim_summary(summary, max_chars=max_chars)

    tokens = tokenize(text)
    word_counts = Counter(tokens)

    scored = []

    for index, sentence in enumerate(sentences):
        sentence_tokens = tokenize(sentence)

        if not sentence_tokens:
            score = 0.0
        else:
            frequency_score = sum(word_counts[token] for token in sentence_tokens) / len(sentence_tokens)
            position_bonus = 0.25 if index < 2 else 0.0
            length_penalty = 0.15 if len(sentence) > 140 else 0.0
            score = frequency_score + position_bonus - length_penalty

        scored.append((index, sentence, score))

    selected = sorted(scored, key=lambda item: item[2], reverse=True)[:max_sentences]
    selected = sorted(selected, key=lambda item: item[0])

    summary = " ".join(sentence for _, sentence, _ in selected)
    return trim_summary(summary, max_chars=max_chars)


def trim_summary(summary: str, max_chars: int = 180) -> str:
    if len(summary) <= max_chars:
        return summary

    return summary[:max_chars].rstrip() + "..."
