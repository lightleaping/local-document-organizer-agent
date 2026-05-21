import re
from collections import Counter
from typing import List, Tuple


DOMAIN_TERMS = [
    "관계형 데이터베이스",
    "자연어 처리",
    "이미지 인식",
    "추천 시스템",
    "문서 자동화",
    "키워드 추출",
    "기본 키",
    "외래 키",
    "데이터베이스",
    "인공지능",
    "정규화",
    "무결성",
    "인덱스",
    "테이블",
    "패턴",
    "학습",
    "예측",
    "분류",
    "설계",
]

STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "이다", "있다", "없다", "최근", "여러",
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과", "사용",
    "생성", "추출", "추천", "자동", "기반", "활용", "관리", "확인", "분석",
    "요약", "글자", "경로", "형식", "개요", "도움", "수행", "위한", "중요",
    "데이터", "구조적", "저장", "표현", "분야", "핵심", "주요", "도구",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
}

PARTICLE_SUFFIXES = [
    "으로부터", "로부터", "에서는", "에게는", "까지는",
    "으로", "에서", "에게", "부터", "까지", "처럼", "보다",
    "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "만", "로",
]

ENDING_SUFFIXES = [
    "입니다", "합니다", "하였다", "했다", "된다", "한다", "이다", "있다", "없다",
    "하고", "하며", "하여", "되며", "된다", "한다", "이다", "하다", "되다", "다",
]


def clean_markdown(text: str) -> str:
    """
    Remove Markdown syntax and exclude heading/table/code lines.
    """
    lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("```"):
            continue

        if re.match(r"^#{1,6}\s+", line):
            continue

        if line.startswith("|"):
            continue

        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = line.replace("`", "")
        line = line.replace("**", "").replace("__", "").replace("*", "")

        lines.append(line)

    return " ".join(lines)


def split_sentences(text: str) -> List[str]:
    text = clean_markdown(text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?。！？다])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 15
    ]


def normalize_token(token: str) -> str:
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


def tokenize(text: str) -> List[str]:
    raw_tokens = re.findall(r"[가-힣A-Za-z0-9\-_]+", clean_markdown(text))

    tokens = []
    for raw_token in raw_tokens:
        token = normalize_token(raw_token)
        if token:
            tokens.append(token)

    return tokens


def extract_domain_terms(text: str) -> List[str]:
    """
    Extract only known meaningful terms.
    Avoid arbitrary phrase generation like '패턴 학습하고 예측이나'.
    """
    clean_text = clean_markdown(text).lower()
    found = []

    for term in DOMAIN_TERMS:
        if term.lower() in clean_text:
            found.append(term)

    return found


def extract_keywords(text: str, top_k: int = 6) -> List[Tuple[str, float]]:
    """
    Extract clean, readable keywords.

    Priority:
    1. Meaningful domain terms directly found in the text.
    2. Normalized single tokens as fallback.
    """
    domain_terms = extract_domain_terms(text)
    tokens = tokenize(text)
    token_counts = Counter(tokens)

    results = []
    seen = set()

    for term in domain_terms:
        key = term.lower()

        if key in seen:
            continue

        results.append((term, 100.0))
        seen.add(key)

        if len(results) >= top_k:
            return results[:top_k]

    for token, count in token_counts.most_common():
        key = token.lower()

        if key in seen:
            continue

        if any(key in term.lower() for term in domain_terms):
            continue

        results.append((token, float(count)))
        seen.add(key)

        if len(results) >= top_k:
            break

    return results[:top_k]
