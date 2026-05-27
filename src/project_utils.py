import re


PROJECT_NAMES = [
    "Multimodal Intent QA Agent",
    "Course Study RAG Tutor",
    "Local Document Organizer Agent",
    "Manufacturing MCP Agent",
    "Sensor Anomaly Model Pipeline",
    "AI 의결서 RAG",
    "Fair Decision RAG",
    "Biz-English",
]


def detect_project_name(text: str, file_name: str = "") -> str | None:
    target = f"{file_name}\n{text}".lower()

    aliases = {
        "Multimodal Intent QA Agent": [
            "multimodal intent qa agent",
            "multimodal_input_policy",
            "image_input_policy",
            "intent classification",
            "grounded answer",
            "self-check validation",
            "cost estimate",
        ],
        "Course Study RAG Tutor": [
            "course study rag tutor",
            "database_md_chunk",
            "keyword retrieval",
            "embedding retrieval",
            "hybrid retrieval",
            "수업자료 기반 rag",
        ],
        "Local Document Organizer Agent": [
            "local document organizer agent",
            "문서 유형",
            "추천 파일명",
            "중복 후보",
            "markdown 리포트",
        ],
        "Manufacturing MCP Agent": [
            "manufacturing mcp agent",
            "mcp server",
            "제조 데이터",
            "line_performance",
            "sensor anomaly",
        ],
        "Sensor Anomaly Model Pipeline": [
            "sensor anomaly model pipeline",
            "sensorautoencoder",
            "anomaly_score",
            "temperature",
            "vibration",
            "pressure",
        ],
        "AI 의결서 RAG": [
            "ai 의결서 rag",
            "공정거래 의결서",
            "공개본 의결서",
            "chunk_id 5",
            "section-aware",
            "hybrid retrieval",
        ],
        "Fair Decision RAG": [
            "fair decision rag",
            "fair-decision-rag",
        ],
        "Biz-English": [
            "biz-english",
            "biz english",
            "영어 학습 앱",
            "직장인 영어",
        ],
    }

    best_name = None
    best_score = 0

    for project_name, keywords in aliases.items():
        score = 0

        if project_name.lower() in target:
            score += 5

        for keyword in keywords:
            if keyword.lower() in target:
                score += 1

        if score > best_score:
            best_score = score
            best_name = project_name

    if best_score <= 0:
        return None

    return best_name


def slugify_project_name(project_name: str) -> str:
    text = project_name.lower().strip()
    text = text.replace("&", "and")
    text = re.sub(r"[^가-힣a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def project_readme_filename(project_name: str, extension: str = ".md") -> str:
    return f"{slugify_project_name(project_name)}_readme{extension}"


def filter_keywords_by_project(keywords: list[str], project_name: str | None, max_count: int = 6) -> list[str]:
    if not keywords:
        return []

    if not project_name:
        return keywords[:max_count]

    project_related = {
        "Multimodal Intent QA Agent": {
            "Multimodal Intent QA Agent",
            "Intent",
            "Grounded Answer",
            "Self-check",
            "evidence",
            "FastAPI",
            "Streamlit",
            "RAG",
            "AI Agent",
            "Agent Workflow",
        },
        "Course Study RAG Tutor": {
            "Course Study RAG Tutor",
            "RAG",
            "Keyword Retrieval",
            "Embedding Retrieval",
            "Hybrid Retrieval",
            "chunk_id",
            "score",
            "Streamlit",
            "Markdown",
        },
        "Local Document Organizer Agent": {
            "Local Document Organizer Agent",
            "문서 자동화",
            "키워드 추출",
            "추천 파일명",
            "중복 후보",
            "Markdown 리포트",
            "Streamlit",
        },
        "Manufacturing MCP Agent": {
            "Manufacturing MCP Agent",
            "MCP",
            "MCP Server",
            "제조 데이터",
            "FastAPI",
            "LangGraph",
            "PyTorch",
            "Docker",
        },
        "Sensor Anomaly Model Pipeline": {
            "Sensor Anomaly Model Pipeline",
            "SensorAutoEncoder",
            "anomaly_score",
            "PyTorch",
            "FastAPI",
            "temperature",
            "vibration",
        },
        "AI 의결서 RAG": {
            "AI 의결서 RAG",
            "공정거래 의결서",
            "Section-aware Hybrid RAG",
            "BM25",
            "Dense Retrieval",
            "FAISS",
            "chunk_id",
            "Evidence Trace",
        },
        "Fair Decision RAG": {
            "Fair Decision RAG",
            "공정거래 의결서",
            "BM25",
            "FAISS",
            "chunk_id",
            "RAG",
        },
        "Biz-English": {
            "Biz-English",
            "AI 영어 학습",
            "시나리오",
            "선택지",
            "직장인",
            "대화 흐름",
        },
    }

    allowed = project_related.get(project_name, set())
    if not allowed:
        return keywords[:max_count]

    filtered = []
    seen = set()

    for keyword in keywords:
        if keyword in allowed and keyword not in seen:
            filtered.append(keyword)
            seen.add(keyword)

    for keyword in keywords:
        if keyword in seen:
            continue

        # 다른 프로젝트명은 제거
        if any(project in keyword for project in PROJECT_NAMES if project != project_name):
            continue

        filtered.append(keyword)
        seen.add(keyword)

        if len(filtered) >= max_count:
            break

    return filtered[:max_count]
