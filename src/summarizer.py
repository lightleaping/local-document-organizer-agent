import re
from collections import Counter

from src.keyword_extractor import clean_markdown, split_sentences, tokenize
from src.project_utils import detect_project_name


def summarize_project_readme(text: str, file_name: str = "", keywords: list[str] | None = None) -> str:
    cleaned = clean_markdown(text)
    project_name = detect_project_name(cleaned, file_name=file_name)
    keyword_text = ", ".join((keywords or [])[:6]) if keywords else "핵심 키워드 없음"

    if project_name == "Multimodal Intent QA Agent":
        return (
            "Multimodal Intent QA Agent 프로젝트의 README 문서입니다. "
            "텍스트와 이미지 입력을 공통 document 구조로 변환하고, intent 분류, evidence retrieval, grounded answer, "
            "self-check validation, cost estimate, FastAPI/Streamlit UI 흐름을 설명합니다."
        )

    if project_name == "Course Study RAG Tutor":
        return (
            "Course Study RAG Tutor 프로젝트의 README 문서입니다. "
            "수업자료를 chunk 단위로 나누고 Keyword Retrieval, Embedding Retrieval, Hybrid Retrieval을 비교하며, "
            "file_name, chunk_id, score 기반 근거 추적 구조를 설명하는 RAG 학습 프로젝트입니다."
        )

    if project_name == "Local Document Organizer Agent":
        return (
            "Local Document Organizer Agent 프로젝트의 README 문서입니다. "
            "로컬 문서를 업로드해 문서 유형 분류, 핵심 키워드 추출, 추천 파일명 생성, 요약, 중복 후보 탐지, "
            "Markdown 리포트 생성을 수행하는 문서 자동화 Agent 구조를 설명합니다."
        )

    if project_name == "Manufacturing MCP Agent":
        return (
            "Manufacturing MCP Agent 프로젝트의 README 문서입니다. "
            "제조 데이터 기반 질문을 intent로 분류하고 MCP Tool, Agent Workflow, FastAPI API, PyTorch 센서 이상탐지 모델을 연결하는 구조를 설명합니다."
        )

    if project_name == "Sensor Anomaly Model Pipeline":
        return (
            "Sensor Anomaly Model Pipeline 프로젝트의 README 문서입니다. "
            "센서 데이터 생성, 전처리, PyTorch AutoEncoder 모델 학습/추론, 이상 점수 반환, FastAPI 서빙 흐름을 설명합니다."
        )

    return (
        f"이 문서는 프로젝트의 목적, 주요 기능, 실행 방법과 구현 구조를 설명하는 README/기술 문서입니다. "
        f"주요 키워드는 {keyword_text}입니다. "
        "코드 실행과 포트폴리오 검토를 위해 프로젝트 개요, 기능 흐름, 사용 기술을 빠르게 파악할 수 있습니다."
    )


def summarize_by_document_type(
    text: str,
    document_type: str,
    keywords: list[str],
    file_name: str = "",
) -> str:
    keyword_text = ", ".join(keywords[:6]) if keywords else "핵심 키워드 없음"

    if document_type == "프로젝트 README / 기술 문서":
        return summarize_project_readme(text, file_name=file_name, keywords=keywords)

    if document_type == "기획서 / 제안서":
        return (
            f"이 문서는 문제 정의, 접근 방식, 모델 또는 서비스 구조, 기대효과를 정리한 기획서/제안서입니다. "
            f"주요 키워드는 {keyword_text}입니다. "
            "프로젝트의 목표와 구현 방향, 평가 기준을 검토하는 데 활용할 수 있습니다."
        )

    if document_type == "포트폴리오 / 자기소개서":
        return (
            f"이 문서는 지원자의 프로젝트 경험, 핵심 역량, 기술 스택과 직무 적합성을 정리한 취업 서류입니다. "
            f"주요 키워드는 {keyword_text}입니다. "
            "지원 직무와 연결되는 경험과 역량을 검토하는 데 활용할 수 있습니다."
        )

    if document_type == "학습 자료":
        return (
            f"이 문서는 특정 개념이나 수업 내용을 정리한 학습 자료입니다. "
            f"주요 키워드는 {keyword_text}입니다. "
            "핵심 개념을 빠르게 복습하고 관련 내용을 찾는 데 활용할 수 있습니다."
        )

    if document_type == "시나리오 / 대화 스크립트":
        return (
            f"이 문서는 서비스 흐름, 사용자 발화, 선택지 또는 대화 장면을 정리한 시나리오/스크립트 문서입니다. "
            f"주요 키워드는 {keyword_text}입니다. "
            "AI 응답 흐름이나 사용자 경험 설계를 검토하는 데 활용할 수 있습니다."
        )

    if document_type == "일정 / 시간표 자료":
        return summarize_course_registration(text)

    if document_type == "구현 TODO / 작업 목록":
        return summarize_implementation_todo(text)

    return summarize_text(text, max_sentences=3)


def extract_final_course_block(text: str) -> str:
    cleaned = clean_markdown(text)
    for marker in ["최종 9과목", "최종 과목", "최종"]:
        if marker in cleaned:
            return cleaned.split(marker, 1)[-1].strip()
    return ""


def summarize_course_registration(text: str, max_items: int = 9) -> str:
    final_block = extract_final_course_block(text)
    target = final_block if final_block else clean_markdown(text)
    course_candidates = re.findall(r"([가-힣A-Za-z0-9·\s]+?)\s*\((?:원격·)?[월화수목금토일][^)]+\)", target)

    courses = []
    seen = set()
    for item in course_candidates:
        course = re.sub(r"\s+", " ", item).strip(" -•,")
        if len(course) >= 2 and course not in seen:
            courses.append(course)
            seen.add(course)

    if courses:
        return f"수강신청 후보와 시간표 정보를 정리한 문서입니다. 최종 선택 과목은 {', '.join(courses[:max_items])} 등으로 확인됩니다."

    return "수강신청 후보 과목과 요일·교시 정보를 정리한 시간표 자료입니다."


def summarize_implementation_todo(text: str) -> str:
    cleaned = clean_markdown(text)
    items = re.findall(r"([^.!?。！？]*미구현[^.!?。！？]*)", cleaned)

    cleaned_items = []
    seen = set()
    for item in items:
        item = re.sub(r"\s+", " ", item).strip(" -•")
        if item and item not in seen:
            cleaned_items.append(item)
            seen.add(item)

    if cleaned_items:
        return f"미구현 기능과 개발 보완 항목을 정리한 문서입니다. 주요 항목은 {' / '.join(cleaned_items[:5])} 등입니다."

    return "구현 예정 기능과 보완이 필요한 시나리오를 정리한 개발 작업 목록입니다."


def summarize_text(text: str, max_sentences: int = 3) -> str:
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
            length_bonus = min(len(sentence) / 180, 0.20)
            position_bonus = 0.10 if index < 3 else 0.0
            digit_ratio = sum(char.isdigit() for char in sentence) / max(len(sentence), 1)
            digit_penalty = 0.35 if digit_ratio > 0.25 else 0.0
            code_penalty = 0.50 if re.search(r"-->|flowchart|classDef|subgraph", sentence) else 0.0
            score = frequency_score + length_bonus + position_bonus - digit_penalty - code_penalty

        scored.append((index, sentence, score))

    selected = sorted(scored, key=lambda item: item[2], reverse=True)[:max_sentences]
    selected = sorted(selected, key=lambda item: item[0])
    return " ".join(sentence for _, sentence, _ in selected)
