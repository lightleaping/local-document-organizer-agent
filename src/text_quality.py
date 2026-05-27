import re
from dataclasses import dataclass


@dataclass
class TextQualityResult:
    is_valid: bool
    reason: str
    readable_ratio: float
    broken_ratio: float
    text_length: int


BROKEN_CHARS = set("�¬©‹›Ÿﬂ°˝ÕÐÉàÈ")


def check_text_quality(text: str, file_extension: str = "", min_length: int = 30) -> TextQualityResult:
    if not text or not text.strip():
        return TextQualityResult(
            is_valid=False,
            reason="추출된 텍스트가 없습니다.",
            readable_ratio=0.0,
            broken_ratio=1.0,
            text_length=0,
        )

    cleaned = text.strip()
    text_length = len(cleaned)
    ext = file_extension.lower().strip()

    if text_length < min_length:
        return TextQualityResult(
            is_valid=False,
            reason="추출된 텍스트가 너무 짧아 자동 분석하기 어렵습니다.",
            readable_ratio=0.0,
            broken_ratio=0.0,
            text_length=text_length,
        )

    semantic_chars = re.findall(r"[가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z0-9]", cleaned)
    broken_chars = [ch for ch in cleaned if ch in BROKEN_CHARS]
    control_chars = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", cleaned)

    semantic_ratio = len(semantic_chars) / max(text_length, 1)
    broken_ratio = len(broken_chars) / max(text_length, 1)
    control_ratio = len(control_chars) / max(text_length, 1)

    readable_chars = re.findall(
        r"[가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z0-9\s.,!?;:()\[\]{}_\-/\\|@#%&+=~`'\"<>·•–—]",
        cleaned,
    )
    readable_ratio = len(readable_chars) / max(text_length, 1)

    suspicious_patterns = [
        r"[¬©‹›Ÿﬂ°˝]{3,}",
        r"[A-Za-z]\|",
        r"\\\s*[A-Za-z]",
    ]
    suspicious_count = sum(1 for pattern in suspicious_patterns if re.search(pattern, cleaned))

    if ext in {".txt", ".md", ".markdown"}:
        if control_ratio >= 0.08:
            return TextQualityResult(
                is_valid=False,
                reason="제어 문자가 많이 포함되어 텍스트 인코딩 문제가 의심됩니다.",
                readable_ratio=round(readable_ratio, 4),
                broken_ratio=round(broken_ratio, 4),
                text_length=text_length,
            )

        if broken_ratio >= 0.20 and semantic_ratio < 0.20:
            return TextQualityResult(
                is_valid=False,
                reason="깨진 문자 비율이 높고 읽을 수 있는 문자 비율이 낮습니다.",
                readable_ratio=round(readable_ratio, 4),
                broken_ratio=round(broken_ratio, 4),
                text_length=text_length,
            )

        return TextQualityResult(
            is_valid=True,
            reason="TXT/Markdown 문서로 분석 가능한 수준입니다.",
            readable_ratio=round(readable_ratio, 4),
            broken_ratio=round(broken_ratio, 4),
            text_length=text_length,
        )

    if semantic_ratio >= 0.30 and broken_ratio < 0.12 and control_ratio < 0.04:
        return TextQualityResult(
            is_valid=True,
            reason="텍스트 품질이 분석 가능한 수준입니다.",
            readable_ratio=round(readable_ratio, 4),
            broken_ratio=round(broken_ratio, 4),
            text_length=text_length,
        )

    if broken_ratio >= 0.12 and suspicious_count >= 1:
        return TextQualityResult(
            is_valid=False,
            reason="깨진 문자 비율이 높아 자동 분석을 중단했습니다.",
            readable_ratio=round(readable_ratio, 4),
            broken_ratio=round(broken_ratio, 4),
            text_length=text_length,
        )

    if control_ratio >= 0.06:
        return TextQualityResult(
            is_valid=False,
            reason="제어 문자가 많이 포함되어 텍스트 인코딩 문제가 의심됩니다.",
            readable_ratio=round(readable_ratio, 4),
            broken_ratio=round(broken_ratio, 4),
            text_length=text_length,
        )

    if semantic_ratio < 0.15 and suspicious_count >= 2:
        return TextQualityResult(
            is_valid=False,
            reason="읽을 수 있는 문자 비율이 낮고 인코딩 깨짐 패턴이 감지되었습니다.",
            readable_ratio=round(readable_ratio, 4),
            broken_ratio=round(broken_ratio, 4),
            text_length=text_length,
        )

    return TextQualityResult(
        is_valid=True,
        reason="텍스트 품질이 분석 가능한 수준입니다.",
        readable_ratio=round(readable_ratio, 4),
        broken_ratio=round(broken_ratio, 4),
        text_length=text_length,
    )
