# Trouble Shooting

## 1. Streamlit 명령어를 인식하지 못하는 문제

### 문제

```text
streamlit : The term 'streamlit' is not recognized
```

### 원인

Streamlit이 현재 Python 환경에 설치되어 있지 않거나, 실행 경로에 등록되어 있지 않은 경우입니다.

### 해결

가상환경 없이 진행하는 경우 아래 명령어로 설치합니다.

```bash
python -m pip install -r requirements.txt
```

이후 Streamlit을 모듈 방식으로 실행합니다.

```bash
python -m streamlit run app.py
```

---

## 2. PyMuPDF import 오류

### 문제

```text
ModuleNotFoundError: No module named 'fitz'
```

### 원인

PyMuPDF가 설치되지 않은 상태입니다.

### 해결

```bash
python -m pip install pymupdf
```

또는:

```bash
python -m pip install -r requirements.txt
```

---

## 3. sample_docs 안에 docs 폴더가 같이 분석되는 문제

### 원인

문서 파일을 덮어쓰는 과정에서 `docs` 폴더를 `sample_docs` 안에 잘못 복사한 경우입니다.

### 해결

아래 폴더를 삭제합니다.

```bash
Remove-Item -Recurse -Force sample_docs\docs
```

정상적인 `sample_docs` 구조는 다음과 같습니다.

```text
sample_docs/
  sample_ai.txt
  sample_ai_copy.txt
  sample_database.md
```

---

## 4. 중복 문서가 탐지되지 않는 문제

### 원인

유사도 임계값이 너무 높을 수 있습니다.

### 해결

CLI에서는 임계값을 낮춰 실행합니다.

```bash
python main.py --input sample_docs --output reports --duplicate-threshold 0.65
```

웹 UI에서는 사이드바의 중복 탐지 임계값을 낮춥니다.

---

## 5. 추천 파일명이 단순 키워드 나열처럼 보이는 문제

### 원인

초기 버전에서는 키워드를 단순히 이어 붙여 추천 파일명을 만들었습니다.

### 해결

최종 버전에서는 문서 유형을 먼저 판정하고, 유형별 이름 규칙을 적용합니다.

예:

```text
AI 문서 자동화 개요 → ai_document_automation_overview.txt
데이터베이스 설계 개념 → database_design_keys_indexes.md
```

---

## 6. 핵심 키워드와 요약이 서로 맞지 않는 문제

### 원인

초기 버전에서는 전체 문서에서 키워드를 추출하고, 별도 기준으로 요약을 생성하여 두 결과가 어긋날 수 있었습니다.

### 해결

최종 버전에서는 문서 유형 판정, 제목, 키워드, 추천 파일명, 요약을 `document_analyzer.py`에서 통합 관리하도록 개선했습니다.

---

## 7. reports/document_report.md가 GitHub에 올라가지 않는 문제

### 원인

`.gitignore`에서 실행 결과 리포트를 제외했기 때문입니다.

```gitignore
reports/*.md
!reports/.gitkeep
```

### 해결

실행 결과 예시는 `docs/sample_report.md`로 복사하여 GitHub에 포함합니다.

```bash
Copy-Item reports\document_report.md docs\sample_report.md
```
