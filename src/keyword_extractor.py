import re
from collections import Counter
from typing import List, Tuple


DOMAIN_PHRASES = [
    "인공지능",
    "자연어 처리",
    "이미지 인식",
    "추천 시스템",
    "문서 자동화",
    "키워드 추출",
    "데이터베이스",
    "관계형 데이터베이스",
    "기본 키",
    "외래 키",
    "정규화",
    "무결성",
    "인덱스",
    "markdown",
    "pdf",
    "txt",
    "streamlit",
    "tf-idf",
    "cosine similarity",
    "duplicate detection",
]

STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "수", "등", "및", "에서", "으로", "에게",
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과", "사용",
    "생성", "추출", "추천", "자동", "기반", "활용", "관리", "확인", "분석",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
}

PARTICLE_SUFFIXES = [
    "으로부터", "로부터", "에서는", "에게는", "까지는",
    "으로", "에서", "에게", "부터", "까지", "처럼", "보다",
    "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "만", "로",
]

ENDING_SUFFIXES = [
    "입니다", "합니다", "하였다", "했다", "된다", "한다", "이다", "있다", "없다",
    "된다", "된다", "된다", "다",
]


def clean_markdown(text: str) -> str:
    """
    Remove noisy Markdown syntax while preserving meaningful text.
    """
    lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("```"):
            continue

        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = line.replace("`", "")
        line = line.replace("**", "").replace("__", "").replace("*", "")

        lines.append(line)

    return " ".join(lines)


def normalize_token(token: str) -> str:
    """
    Light Korean normalization without external morphology packages.
    It removes common particles and endings from short content words.
    """
    token = token.lower().strip()
    token = re.sub(r"[^가-힣a-z0-9\-_]", "", token)

    if not token:
        return ""

    for suffix in PARTICLE_SUFFIXES:
        if len(token) > len(suffix) + 1 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break

    for suffix in ENDING_SUFFIXES:
        if len(token) > len(suffix) + 1 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break

    if token in STOPWORDS or len(token) < 2:
        return ""

    return token


def extract_domain_phrases(text: str) -> List[str]:
    """
    Extract meaningful multi-word/domain phrases first.
    """
    normalized_text = clean_markdown(text).lower()
    phrases = []

    for phrase in DOMAIN_PHRASES:
        if phrase.lower() in normalized_text:
            phrases.append(phrase)

    return phrases


def tokenize(text: str) -> List[str]:
    """
    Tokenize Korean/English mixed text and normalize common Korean particles.
    """
    text = clean_markdown(text)
    raw_tokens = re.findall(r"[가-힣A-Za-z0-9\-_]+", text)

    tokens = []
    for raw_token in raw_tokens:
        token = normalize_token(raw_token)
        if token:
            tokens.append(token)

    return tokens


def extract_keywords(text: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Extract readable keywords.

    Priority:
    1. domain/multi-word phrases found in the document
    2. normalized content words by frequency
    """
    phrase_keywords = extract_domain_phrases(text)
    tokens = tokenize(text)
    token_counts = Counter(tokens)

    results = []
    seen = set()

    for phrase in phrase_keywords:
        normalized_phrase = phrase.lower()
        if normalized_phrase not in seen:
            score = 1.0 + token_counts.get(normalized_phrase, 0)
            results.append((phrase, score))
            seen.add(normalized_phrase)

    for token, count in token_counts.most_common():
        if token in seen:
            continue

        if any(token in phrase.lower() for phrase in phrase_keywords):
            continue

        results.append((token, float(count)))
        seen.add(token)

        if len(results) >= top_k:
            break

    return results[:top_k]
