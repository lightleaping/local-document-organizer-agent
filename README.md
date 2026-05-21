# Local Document Organizer Agent

로컬 폴더 안의 PDF, TXT, Markdown 문서를 자동으로 읽고, 문서별 요약, 키워드 추출, 중복 문서 탐지, Markdown 리포트 생성을 수행하는 문서 정리 자동화 Agent입니다.

이 프로젝트는 RAG 시스템이나 문서 기반 AI 서비스에서 필요한 문서 수집, 전처리, 요약, 태깅, 중복 탐지 과정을 하나의 로컬 자동화 파이프라인으로 구현하는 것을 목표로 합니다.

---

## 1. 프로젝트 개요

문서 기반 업무에서는 여러 파일을 직접 열어보고 내용을 확인하거나, 비슷한 문서를 수동으로 구분해야 하는 경우가 많습니다.

본 프로젝트는 이러한 반복 작업을 자동화하기 위해 로컬 폴더 내 문서를 분석하고, 문서별 핵심 정보와 중복 의심 문서를 Markdown 리포트로 정리합니다.

주요 목적은 다음과 같습니다.

- 로컬 문서 폴더 자동 탐색
- PDF, TXT, Markdown 문서 텍스트 추출
- 문서별 핵심 문장 요약
- TF-IDF 기반 키워드 추출
- 유사 문서 및 중복 후보 탐지
- Markdown 분석 리포트 자동 생성

---

## 2. 주요 기능

| 기능 | 설명 |
|---|---|
| 문서 로딩 | 지정한 폴더에서 `.pdf`, `.txt`, `.md` 파일을 자동 탐색 |
| 텍스트 추출 | PyMuPDF와 Python 기본 파일 처리를 이용해 문서 텍스트 추출 |
| 문서 요약 | 단어 빈도 기반 문장 점수 계산으로 핵심 문장 추출 |
| 키워드 추출 | TF-IDF 기반으로 문서별 주요 키워드 추출 |
| 중복 탐지 | 문자 n-gram TF-IDF와 cosine similarity로 유사 문서 탐지 |
| 리포트 생성 | 분석 결과를 Markdown 파일로 자동 저장 |

---

## 3. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| PDF Parsing | PyMuPDF |
| Text Processing | re, pathlib |
| Keyword Extraction | scikit-learn TF-IDF |
| Duplicate Detection | scikit-learn cosine similarity |
| Report | Markdown |
| CLI | argparse |

---

## 4. 프로젝트 구조

```text
local-document-organizer-agent/
│
├── main.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── summarizer.py
│   ├── keyword_extractor.py
│   ├── duplicate_detector.py
│   ├── report_generator.py
│   └── file_renamer.py
│
├── sample_docs/
│   ├── sample_ai.txt
│   ├── sample_ai_copy.txt
│   └── sample_database.md
│
├── reports/
│   └── .gitkeep
│
└── docs/
    ├── project_overview.md
    ├── architecture.md
    ├── trouble_shooting.md
    └── sample_report.md
```

---

## 5. 실행 방법

### 5.1 가상환경 생성

```bash
python -m venv .venv
```

### 5.2 가상환경 활성화

Windows PowerShell 기준:

```bash
.\.venv\Scripts\Activate.ps1
```

실행 정책 오류가 발생하면 아래 명령어를 먼저 실행합니다.

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 5.3 패키지 설치

```bash
pip install -r requirements.txt
```

### 5.4 실행

```bash
python main.py --input sample_docs --output reports
```

실행 후 `reports/document_report.md` 파일이 생성됩니다.

---

## 6. 실행 결과 예시

콘솔 출력 예시는 다음과 같습니다.

```text
Local Document Organizer Agent
========================================
Input folder : sample_docs
Output folder: reports

Loaded Documents
----------------------------------------
1. sample_ai.txt
   Extension  : .txt
   Characters : 196
   Summary    : 최근에는 자연어 처리, 이미지 인식, 추천 시스템, 문서 자동화 등 다양한 분야에서 활용되고 있다.
   Keywords   : 문서를, 자동화, 검색하는, 관리하고, 기능은

Duplicate Candidates
----------------------------------------
sample_ai.txt <-> sample_ai_copy.txt
Similarity: 0.8xxx

Total documents loaded: 3
Report generated: reports\document_report.md
```

생성되는 Markdown 리포트 예시는 `docs/sample_report.md`에서 확인할 수 있습니다.

---

## 7. 처리 흐름

```text
사용자 입력 폴더
        ↓
지원 파일 탐색
        ↓
PDF / TXT / Markdown 텍스트 추출
        ↓
문서별 요약 생성
        ↓
키워드 추출
        ↓
문서 간 유사도 계산
        ↓
중복 의심 문서 탐지
        ↓
Markdown 리포트 생성
```

---

## 8. 핵심 구현 설명

### 8.1 문서 로딩

`document_loader.py`는 입력 폴더를 재귀적으로 탐색하여 `.pdf`, `.txt`, `.md` 파일만 읽습니다.

PDF는 PyMuPDF를 사용하고, 텍스트 기반 파일은 UTF-8을 우선 적용하되 인코딩 문제가 발생하면 CP949로 다시 읽도록 처리했습니다.

### 8.2 요약

`summarizer.py`는 생성형 AI를 사용하지 않고 추출식 요약 방식을 사용합니다.

문서를 문장 단위로 분리한 뒤, 단어 빈도를 기반으로 문장 점수를 계산하고 핵심 문장을 선택합니다.

Markdown 제목, 목록 기호, 강조 표시 등은 요약 전에 정리하여 불필요한 제목 문장이 요약에 포함되지 않도록 개선했습니다.

### 8.3 키워드 추출

`keyword_extractor.py`는 TF-IDF를 이용해 문서별 주요 키워드를 추출합니다.

현재는 설치 안정성을 위해 형태소 분석기 없이 정규식 기반 토큰화를 사용했습니다.

### 8.4 중복 문서 탐지

`duplicate_detector.py`는 문자 n-gram 기반 TF-IDF 벡터를 생성한 뒤 cosine similarity를 계산합니다.

이 방식은 한국어 형태소 분석기에 의존하지 않고도 유사 문서를 탐지할 수 있다는 장점이 있습니다.

### 8.5 Markdown 리포트 생성

`report_generator.py`는 문서 분석 결과와 중복 탐지 결과를 하나의 Markdown 파일로 정리합니다.

실행 결과는 기본적으로 `reports/document_report.md`에 저장됩니다.

---

## 9. 구현 과정에서 고려한 점

- 외부 LLM API 없이 로컬 환경에서 동작하도록 설계
- 설치 부담을 줄이기 위해 최소 패키지 중심으로 구성
- RAG 전처리 파이프라인과 연결 가능한 구조로 설계
- 문서 자동화 도구로 재사용할 수 있도록 CLI 기반 실행 방식 적용
- 실행 결과와 예시 리포트를 분리하여 GitHub 저장소를 깔끔하게 유지

---

## 10. 한계 및 개선 가능성

현재 버전은 가벼운 로컬 자동화 도구를 목표로 하므로 다음과 같은 한계가 있습니다.

- 요약은 생성형 요약이 아니라 문장 추출식 요약입니다.
- 한국어 형태소 분석기를 사용하지 않아 조사나 어미가 붙은 키워드가 나올 수 있습니다.
- PDF 문서의 표, 이미지, 복잡한 레이아웃은 정교하게 처리하지 않습니다.
- 중복 탐지 임계값은 데이터 특성에 따라 조정이 필요합니다.

향후 개선 방향은 다음과 같습니다.

- kiwipiepy 기반 한국어 키워드 품질 개선
- sentence-transformers 기반 의미 유사도 탐지 추가
- 파일명 자동 정리 기능 강화
- Streamlit 기반 간단한 UI 추가
- RAG 문서 전처리 파이프라인과 연동

---

## 11. 포트폴리오 관점의 의미

이 프로젝트를 통해 다음 역량을 보여줄 수 있습니다.

- Python 기반 파일 처리 자동화
- PDF 및 텍스트 문서 파싱
- NLP 전처리와 키워드 추출
- TF-IDF와 cosine similarity 활용
- 로컬 자동화형 Agent 구조 설계
- CLI 기반 재사용 가능한 도구 제작
- Markdown 기반 분석 리포트 자동 생성

---

## 12. 실행 환경

```text
Python 3.10+
Windows PowerShell
PyMuPDF
scikit-learn
numpy
```
