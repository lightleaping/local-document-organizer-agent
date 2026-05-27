from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

from src.keyword_extractor import clean_markdown


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


DOCUMENT_PROFILES = [
    {
        "profile_id": "project_readme",
        "document_type": "프로젝트 README / 기술 문서",
        "title": "프로젝트 README 문서 정리",
        "filename_base": "project_readme_summary",
        "description": "GitHub README, 프로젝트 소개, 주요 기능, 실행 방법, 기술 스택, 폴더 구조, API 사용법, Streamlit 또는 FastAPI 실행 방법을 설명하는 기술 문서",
        "keywords": ["README", "프로젝트", "기술 스택", "실행 방법", "주요 기능", "폴더 구조"],
    },
    {
        "profile_id": "proposal_plan",
        "document_type": "기획서 / 제안서",
        "title": "기획서 및 제안서 정리",
        "filename_base": "proposal_plan_summary",
        "description": "문제 정의, 목표, 접근 방식, 모델 구조, 기대효과, 평가 방법, 활용 데이터, 추진 계획을 설명하는 기획서 또는 제안서 문서",
        "keywords": ["기획서", "문제 정의", "접근 방식", "모델 구조", "기대효과", "평가 방법"],
    },
    {
        "profile_id": "portfolio_resume",
        "document_type": "포트폴리오 / 자기소개서",
        "title": "취업 포트폴리오 및 자기소개서 정리",
        "filename_base": "career_portfolio_summary",
        "description": "취업 포트폴리오, 자기소개서, 프로젝트 경험, 핵심 역량, 지원 직무, 기술 스택, 역할과 성과를 설명하는 문서",
        "keywords": ["포트폴리오", "자기소개서", "핵심 역량", "프로젝트 경험", "기술 스택", "지원 직무"],
    },
    {
        "profile_id": "learning_material",
        "document_type": "학습 자료",
        "title": "학습 자료 정리",
        "filename_base": "learning_material_summary",
        "description": "수업자료, 학습 노트, 개념 설명, 데이터베이스, 머신러닝, 영어 어휘, 예문, 용어 정리 등 학습을 위한 문서",
        "keywords": ["학습 자료", "수업자료", "개념 설명", "용어 정리", "예문", "학습 노트"],
    },
    {
        "profile_id": "scenario_script",
        "document_type": "시나리오 / 대화 스크립트",
        "title": "시나리오 및 대화 스크립트 정리",
        "filename_base": "scenario_script_summary",
        "description": "서비스 시나리오, 대화 스크립트, stage, 선택지, 사용자 발화, AI 응답, 게임 장면, 학습 흐름을 정리한 문서",
        "keywords": ["시나리오", "대화 스크립트", "선택지", "사용자 발화", "AI 응답", "학습 흐름"],
    },
    {
        "profile_id": "schedule_timetable",
        "document_type": "일정 / 시간표 자료",
        "title": "일정 및 시간표 정리",
        "filename_base": "schedule_timetable_summary",
        "description": "수강신청, 시간표, 요일, 교시, 원격 수업, 최종 선택 과목, 일정, 캘린더 정보를 정리한 문서",
        "keywords": ["수강신청", "시간표", "일정", "요일", "교시", "최종 과목"],
    },
    {
        "profile_id": "todo_task_list",
        "document_type": "구현 TODO / 작업 목록",
        "title": "구현 TODO 및 작업 목록 정리",
        "filename_base": "todo_task_list_summary",
        "description": "미구현 기능, 개발 예정 작업, 보완할 기능, 오류 수정, 체크리스트, todo list, 구현 목록을 정리한 문서",
        "keywords": ["미구현", "TODO", "작업 목록", "체크리스트", "보완 사항", "오류 수정"],
    },
    {
        "profile_id": "general_document",
        "document_type": "일반 문서",
        "title": "일반 문서 정리",
        "filename_base": "general_document_summary",
        "description": "명확한 특정 유형으로 분류하기 어려운 일반 텍스트 문서",
        "keywords": [],
    },
]


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_profile_embeddings():
    model = get_model()
    descriptions = [profile["description"] for profile in DOCUMENT_PROFILES]
    return model.encode(descriptions, convert_to_tensor=True, normalize_embeddings=True)


def add_filename_context(file_name: str, text: str) -> str:
    return f"파일명: {file_name}\n본문: {text}"


def rule_boost(profile_id: str, file_name: str, text: str) -> float:
    target = f"{file_name}\n{text}".lower()
    boost = 0.0

    if profile_id == "project_readme":
        if "readme" in file_name.lower():
            boost += 0.18
        if "installation" in target or "how to run" in target or "project structure" in target:
            boost += 0.10
        if "streamlit" in target or "fastapi" in target:
            boost += 0.06

    if profile_id == "proposal_plan":
        if "기획서" in target or "제안서" in target:
            boost += 0.18
        if "문제 정의" in target and "기대효과" in target:
            boost += 0.12
        if "평가 방법" in target or "모델 구조" in target:
            boost += 0.06

    if profile_id == "portfolio_resume":
        if "포트폴리오" in target or "자기소개서" in target:
            boost += 0.18
        if "핵심 역량" in target or "지원동기" in target:
            boost += 0.08

    if profile_id == "scenario_script":
        if "시나리오" in target or "선택지" in target:
            boost += 0.12
        if "biz-english" in target or "stage" in target:
            boost += 0.08

    if profile_id == "schedule_timetable":
        if "수강신청" in target or "최종 9과목" in target:
            boost += 0.16
        if any(day in target for day in ["월", "화", "수", "목", "금"]) and any(slot in target for slot in ["1-2", "3-4", "5-6", "7-8"]):
            boost += 0.10

    if profile_id == "todo_task_list":
        if "미구현" in target or "todo" in target:
            boost += 0.15
        if "체크리스트" in target or "보완" in target:
            boost += 0.06

    return boost


def classify_document(text: str, file_name: str = "", threshold: float = 0.38) -> dict:
    cleaned = clean_markdown(text)
    if not cleaned:
        return {**DOCUMENT_PROFILES[-1], "confidence": 0.0}

    sample = add_filename_context(file_name, cleaned[:3500])
    model = get_model()
    query_embedding = model.encode(sample, convert_to_tensor=True, normalize_embeddings=True)
    profile_embeddings = get_profile_embeddings()
    scores = util.cos_sim(query_embedding, profile_embeddings)[0]

    best_index = 0
    best_score = -999.0

    for index, raw_score in enumerate(scores):
        profile = DOCUMENT_PROFILES[index]
        score = float(raw_score) + rule_boost(profile["profile_id"], file_name, cleaned)
        if score > best_score:
            best_score = score
            best_index = index

    best_profile = DOCUMENT_PROFILES[best_index]

    if best_profile["profile_id"] != "general_document" and best_score < threshold:
        return {**DOCUMENT_PROFILES[-1], "confidence": round(best_score, 4)}

    return {**best_profile, "confidence": round(best_score, 4)}
