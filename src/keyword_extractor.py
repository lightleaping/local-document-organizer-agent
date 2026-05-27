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
    "PDF",
    "Markdown",
    "Streamlit",
    "TF-IDF",
    "cosine similarity",
]

NOISY_WORDS = {
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과", "사용",
    "생성", "추출", "추천", "자동", "기반", "활용", "관리", "확인", "분석",
    "요약", "글자", "경로", "형식", "개요", "도움", "수행", "여러", "최근",
    "있음", "있다", "된다", "한다", "위한", "통한", "대한",
}

STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "수", "등", "및", "에서", "으로", "에게",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
    *NOISY_WORDS,
}

PARTICLE_SUFFIXES = [
    "으로부터", "로부터", "에서는", "에게는", "까지는", "에서는",
    "으로", "에서", "에게", "부터", "까지", "처럼", "보다",
    "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "만", "로",
]

ENDING_SUFFIXES = [
    "입니다", "합니다", "하였다", "했다", "된다", "한다", "이다", "있다", "없다", "다",
]


def clean_markdown(text: str) -> str:
    lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("```"):
            continue

        # Markdown 제목은 요약/키워드 대상에서 제외
        # 예: # 데이터베이스 개요, ## Architecture
        if re.match(r"^#{1,6}\s+", line):
            continue

        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = line.replace("`", "")
        line = line.replace("**", "").replace("__", "").replace("*", "")

        lines.append(line)

    return " ".join(lines)

def split_sentences(text: str) -> List[str]:
    cleaned_text = clean_markdown(text)

    if not cleaned_text:
        return []

    sentences = re.split(r"(?<=[.!?。！？])\s+|(?<=[다요죠])\s+", cleaned_text)

    results = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 10:
            results.append(sentence)

    return results

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


def extract_domain_phrases(text: str) -> List[str]:
    normalized_text = clean_markdown(text).lower()
    phrases = []

    for phrase in DOMAIN_PHRASES:
        if phrase.lower() in normalized_text:
            phrases.append(phrase)

    return phrases


def tokenize(text: str) -> List[str]:
    text = clean_markdown(text)
    raw_tokens = re.findall(r"[가-힣A-Za-z0-9\-_]+", text)

    tokens = []
    for raw_token in raw_tokens:
        token = normalize_token(raw_token)
        if token:
            tokens.append(token)

    return tokens


def extract_keywords(text: str, top_k: int = 6) -> List[Tuple[str, float]]:
    phrase_keywords = extract_domain_phrases(text)
    tokens = tokenize(text)
    token_counts = Counter(tokens)

    results = []
    seen = set()

    for phrase in phrase_keywords:
        normalized_phrase = phrase.lower()
        if normalized_phrase not in seen:
            results.append((phrase, 100.0))
            seen.add(normalized_phrase)

    for token, count in token_counts.most_common():
        if token in seen:
            continue

        if token in NOISY_WORDS:
            continue

        if any(token in phrase.lower() for phrase in phrase_keywords):
            continue

        results.append((token, float(count)))
        seen.add(token)

        if len(results) >= top_k:
            break

    return results[:top_k]
