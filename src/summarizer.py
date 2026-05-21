from collections import Counter
from typing import List

from src.keyword_extractor import split_sentences, tokenize


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Create an extractive summary.

    The selected summary becomes the basis for downstream keyword extraction
    and filename suggestion, so that results stay consistent.
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

            # Prefer sentences that are informative rather than title-like.
            length_bonus = min(len(sentence) / 120, 0.25)
            position_bonus = 0.10 if index < 2 else 0.0

            score = frequency_score + length_bonus + position_bonus

        scored.append((index, sentence, score))

    selected = sorted(scored, key=lambda item: item[2], reverse=True)[:max_sentences]
    selected = sorted(selected, key=lambda item: item[0])

    return " ".join(sentence for _, sentence, _ in selected)
