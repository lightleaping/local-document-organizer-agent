import math
import re
from collections import Counter
from typing import List, Tuple


DOMAIN_PHRASES = [
    "Course Study RAG Tutor", "Multimodal Intent QA Agent", "Local Document Organizer Agent",
    "Biz-English", "AI 영어 학습", "직장인 영어", "대화 시나리오", "선택지",
    "RAG", "AI Agent", "Agent Workflow", "Intent", "Grounded Answer", "Self-check",
    "Keyword Retrieval", "Embedding Retrieval", "Hybrid Retrieval", "chunk_id", "evidence",
    "인공지능", "자연어 처리", "이미지 인식", "추천 시스템", "문서 자동화", "키워드 추출",
    "데이터 분석", "데이터분석", "파이썬", "파이썬입문",
    "데이터베이스", "관계형 데이터베이스", "기본 키", "외래 키", "정규화", "무결성", "인덱스",
    "공정거래 의결서", "Section-aware Hybrid RAG", "BM25", "Dense Retrieval", "FAISS",
    "Evidence Trace", "Top-5 chunk_id", "Grounded Answer Builder",
    "수강신청", "시간표", "최종 과목", "영어뉴스리딩", "일잘러 데이터분석", "취업영어", "영어회화",
    "미구현", "예매 시나리오", "카트 기능", "물품 구매", "전화 형식", "고정 시나리오",
    "PDF", "Markdown", "Streamlit", "FastAPI", "TF-IDF", "cosine similarity",
]

NOISY_WORDS = {
    "문서", "파일", "기능", "시스템", "기술", "작업", "내용", "결과", "사용",
    "생성", "추출", "추천", "자동", "기반", "활용", "관리", "확인", "분석",
    "요약", "글자", "경로", "형식", "개요", "도움", "수행", "여러", "최근",
    "있음", "있다", "된다", "한다", "위한", "통한", "대한", "중심",
    "선택", "문서별", "전체", "리포트", "미리보기", "처리", "기준",
    "최종", "후보", "자료", "목록", "정리", "프로젝트", "설명", "제공",
}

STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "수", "등", "및", "에서", "으로", "에게",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
    "have", "has", "had", "do", "does", "did", "some", "any", "be", "been",
    "we", "you", "i", "he", "she", "they", "it", "ll", "re", "ve", "m", "d",
    "can", "could", "would", "should", "will", "your", "our", "their", "my",
    "this", "that", "these", "those", "yes", "no", "ok", "okay", "stage",
    "flowchart", "subgraph", "classdef", "style",
    *NOISY_WORDS,
}

PARTICLE_SUFFIXES = [
    "으로부터", "로부터", "에서는", "에게는", "까지는",
    "으로", "에서", "에게", "부터", "까지", "처럼", "보다",
    "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "만", "로",
]

ENDING_SUFFIXES = ["입니다", "합니다", "하였다", "했다", "된다", "한다", "이다", "있다", "없다", "다"]


def clean_markdown(text: str) -> str:
    lines = []
    in_fence = False

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.startswith("```"):
            in_fence = not in_fence
            continue

        if in_fence:
            continue

        if not line:
            continue

        if re.match(r"^#{1,6}\s+", line):
            line = re.sub(r"^#{1,6}\s+", "", line).strip()

        if re.match(r"^(flowchart|graph|sequenceDiagram|classDiagram)\b", line):
            continue

        if re.search(r"-->|---|\{.*\}|\[.*\]", line) and ("-->" in line or "flowchart" in line):
            continue

        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = line.replace("`", "").replace("**", "").replace("__", "").replace("*", "")
        line = line.replace("–", "-").replace("—", "-")
        line = re.sub(r"<[^>]+>", " ", line)
        line = re.sub(r"\s+", " ", line)

        if line:
            lines.append(line)

    return " ".join(lines)


def split_sentences(text: str) -> List[str]:
    cleaned_text = clean_markdown(text)
    if not cleaned_text:
        return []

    cleaned_text = cleaned_text.replace("📋", ". ")
    candidates = re.split(
        r"(?<=[.!?。！？])\s+|(?<=[다요죠])\s+|(?<=\))\s+|(?<=\])\s+|(?<=미구현)\s+",
        cleaned_text,
    )

    results = []
    for sentence in candidates:
        sentence = sentence.strip(" -•\t")
        if len(sentence) < 8:
            continue
        if re.search(r"-->|flowchart|subgraph|classDef", sentence):
            continue
        results.append(sentence)

    return results


def is_noise_token(token: str) -> bool:
    if not token:
        return True
    if re.fullmatch(r"\d{1,2}[-–]\d{1,2}", token):
        return True
    if re.fullmatch(r"\d+", token):
        return True
    if token in {"월", "화", "수", "목", "금", "토", "일", "원격"}:
        return True
    if token in STOPWORDS:
        return True
    if len(token) < 2:
        return True
    return False


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

    if is_noise_token(token):
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
    raw_tokens = re.findall(r"[가-힣A-Za-z0-9\-_]+", clean_markdown(text))
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

    total_tokens = max(len(tokens), 1)

    results = []
    seen = set()

    for phrase in phrase_keywords:
        key = phrase.lower()
        if key not in seen:
            results.append((phrase, 100.0))
            seen.add(key)

    for token, count in token_counts.most_common():
        if token in seen or token in NOISY_WORDS or is_noise_token(token):
            continue
        if any(token in phrase.lower() for phrase in phrase_keywords):
            continue

        tf_score = 1 + math.log(count)
        normalized_score = tf_score / total_tokens
        results.append((token, float(normalized_score)))
        seen.add(token)

        if len(results) >= top_k:
            break

    return results[:top_k]
