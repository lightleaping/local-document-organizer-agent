import json
import urllib.error
import urllib.request

from src.keyword_extractor import clean_markdown


OLLAMA_URL = "http://localhost:11434/api/generate"


def build_llm_prompt(text: str, document_type: str, keywords: list[str]) -> str:
    cleaned = clean_markdown(text)
    sample = cleaned[:3500]
    keyword_text = ", ".join(keywords) if keywords else "없음"

    return f"""다음 문서를 한국어로 요약해 주세요.

조건:
- 3문장 이내로 요약합니다.
- 문서의 목적, 핵심 내용, 활용 포인트를 포함합니다.
- 문서에 없는 내용을 만들지 않습니다.
- 코드, 구조도 문법, 깨진 텍스트는 요약하지 않습니다.

문서 유형: {document_type}
핵심 키워드: {keyword_text}

문서 내용:
{sample}
"""


def summarize_with_ollama(
    text: str,
    document_type: str,
    keywords: list[str],
    model: str = "qwen2.5:1.5b",
    timeout: int = 45,
) -> str | None:
    prompt = build_llm_prompt(text, document_type=document_type, keywords=keywords)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 220,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            result = json.loads(body)
            summary = result.get("response", "").strip()
            return summary or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None
