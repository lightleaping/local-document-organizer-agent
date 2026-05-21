# Local Document Organizer Agent

PDF, TXT, Markdown 문서를 업로드하면 **문서 유형, 제목, 핵심 키워드, 추천 파일명, 요약, 중복 후보, Markdown 리포트**를 생성하는 로컬 문서 정리 자동화 도구입니다.

이 프로젝트는 단순한 파일 목록 출력 도구가 아니라, 문서 기반 AI 서비스에서 필요한 **문서 파싱, 전처리, 요약, 핵심 개념 정리, 중복 탐지, 리포트 생성 흐름**을 하나의 작은 실무형 파이프라인으로 구현한 프로젝트입니다.

CLI와 Streamlit 웹 UI를 모두 제공하며, 웹 UI에서는 문서별 카드 형태로 결과를 확인할 수 있습니다.

---

## 1. 프로젝트 개요

문서 기반 업무에서는 여러 문서를 직접 열어 핵심 내용을 확인하고, 비슷한 문서를 구분하고, 파일명을 정리하는 반복 작업이 자주 발생합니다.

본 프로젝트는 이러한 반복 작업을 자동화하기 위해 개발되었습니다.

사용자는 PDF, TXT, Markdown 문서를 업로드하거나 로컬 폴더를 지정할 수 있고, 시스템은 각 문서를 분석하여 다음 결과를 제공합니다.

- 문서 유형
- 문서 제목
- 핵심 키워드
- 추천 파일명
- 문서 요약
- 중복 의심 문서
- Markdown 분석 리포트

---

## 2. 핵심 개선점

초기 버전은 단순히 키워드를 추출해 이어붙이는 방식이었기 때문에, 추천 파일명과 요약, 핵심 키워드가 서로 따로 노는 문제가 있었습니다.

최종 버전에서는 아래 순서로 분석 흐름을 개선했습니다.

```text
문서 내용
  ↓
문서 유형 판정
  ↓
유형별 제목 생성
  ↓
핵심 개념 선별
  ↓
유형 기반 추천 파일명 생성
  ↓
문장형 요약 생성
  ↓
Markdown 리포트 생성
```

따라서 추천 파일명은 단순히 키워드를 길게 이어 붙인 결과가 아니라, 문서의 목적과 유형을 반영한 이름이 되도록 설계했습니다.

예시:

```text
sample_ai.txt
→ AI 기반 문서 자동화 활용 정리
→ ai_document_automation_overview.txt
```

```text
sample_database.md
→ 데이터베이스 설계와 키 개념 정리
→ database_design_keys_indexes.md
```

---

## 3. 주요 기능

| 기능 | 설명 |
|---|---|
| 문서 로딩 | PDF, TXT, Markdown 문서의 텍스트 추출 |
| 문서 유형 판정 | 문서 내용의 신호어를 바탕으로 문서 성격 분류 |
| 제목 생성 | 문서 유형에 맞는 사람이 읽기 쉬운 제목 생성 |
| 핵심 키워드 추출 | 문서 유형을 설명하는 주요 개념 선별 |
| 추천 파일명 생성 | 문서 유형 기반 파일명 추천 |
| 문서 요약 | 사용자가 빠르게 내용을 이해할 수 있도록 문장형 요약 생성 |
| 중복 탐지 | 유사 문서를 중복 후보로 표시 |
| Markdown 리포트 | 분석 결과를 Markdown 문서로 저장 |
| Streamlit UI | 문서 업로드, 카드형 결과 표시, 리포트 미리보기 및 다운로드 제공 |
| CLI 실행 | 폴더 단위 문서 분석과 리포트 생성 지원 |

---

## 4. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| Web UI | Streamlit |
| PDF Parsing | PyMuPDF |
| Text Processing | re, pathlib |
| Keyword / Profile Logic | Rule-based text profiling |
| Duplicate Detection | scikit-learn TF-IDF, cosine similarity |
| Report | Markdown |
| CLI | argparse |

---

## 5. 프로젝트 구조

```text
local-document-organizer-agent/
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── summarizer.py
│   ├── keyword_extractor.py
│   ├── document_analyzer.py
│   ├── duplicate_detector.py
│   ├── file_renamer.py
│   └── report_generator.py
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
    ├── sample_report.md
    └── portfolio_card.txt
```

---

## 6. 설치 방법

### 6.1 패키지 설치

가상환경을 사용하지 않는 경우:

```bash
python -m pip install -r requirements.txt
```

가상환경을 사용하는 경우:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

실행 정책 오류가 발생하면:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

패키지 설치:

```bash
pip install -r requirements.txt
```

---
<img width="2492" height="1523" alt="Image" src="https://github.com/user-attachments/assets/bc3a43a5-1bb1-419e-9e58-ba55fc6e0ccc" />
<img width="2492" height="1525" alt="Image" src="https://github.com/user-attachments/assets/3ece6a3d-4057-4f17-a01d-6f61051d5c39" />
<img width="2492" height="1523" alt="Image" src="https://github.com/user-attachments/assets/fae67083-1510-43a5-9e8e-6396386ca1ff" />


## 7. 실행 방법

### 7.1 Streamlit 웹 UI 실행

```bash
python -m streamlit run app.py
```

웹 화면에서 PDF, TXT, Markdown 문서를 업로드하면 문서별 분석 결과가 카드 형태로 표시됩니다.

웹 UI에서 확인할 수 있는 내용은 다음과 같습니다.

- 문서 제목
- 문서 유형
- 핵심 키워드
- 추천 파일명
- 추천 근거
- 요약
- 중복 의심 문서
- Markdown 리포트 미리보기
- Markdown 리포트 다운로드

### 7.2 CLI 실행

```bash
python main.py --input sample_docs --output reports --summary-sentences 3 --keywords 6 --duplicate-threshold 0.65
```

실행 후 `reports/document_report.md` 파일이 생성됩니다.

### 7.3 CLI 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--input` | 분석할 문서 폴더 | 필수 |
| `--output` | 리포트 저장 폴더 | 필수 |
| `--summary-sentences` | 요약 문장 수 | `3` |
| `--keywords` | 핵심 키워드 개수 | `6` |
| `--duplicate-threshold` | 중복 탐지 유사도 임계값 | `0.70` |

---

## 8. 실행 결과 예시

```text
Local Document Organizer Agent
============================================================
Input folder       : C:\Users\kflow\Downloads\local-document-organizer-agent\sample_docs
Output folder      : C:\Users\kflow\Downloads\local-document-organizer-agent\reports
Summary sentences  : 3
Keyword count      : 6
Duplicate threshold: 0.65

Document Analysis
------------------------------------------------------------
[1] sample_ai.txt
    문서 제목     : AI 기반 문서 자동화 활용 정리
    문서 유형     : AI 문서 자동화 개요
    글자 수       : 196
    핵심 키워드   : 인공지능, 문서 자동화, 자연어 처리, 이미지 인식, 추천 시스템, 요약
    추천 파일명   : ai_document_automation_overview.txt
    추천 근거     : 문서 유형 'AI 문서 자동화 개요'을 기준으로 파일명을 생성했습니다.
    요약          : 이 문서는 인공지능의 기본 개념과 문서 자동화 활용 사례를 설명합니다. 자연어 처리, 이미지 인식, 추천 시스템처럼 AI가 활용되는 분야를 제시하고, 문서 요약과 키워드 추출이 대량 문서 관리에 어떤 역할을 하는지 정리합니다.

[3] sample_database.md
    문서 제목     : 데이터베이스 설계와 키 개념 정리
    문서 유형     : 데이터베이스 설계 개념
    글자 수       : 185
    핵심 키워드   : 데이터베이스, 관계형 데이터베이스, 기본 키, 외래 키, 정규화, 무결성
    추천 파일명   : database_design_keys_indexes.md
    추천 근거     : 문서 유형 '데이터베이스 설계 개념'을 기준으로 파일명을 생성했습니다.
    요약          : 이 문서는 데이터베이스의 기본 개념과 관계형 데이터베이스의 구성 요소를 설명합니다. 테이블, 행, 열을 통해 데이터를 표현하는 방식을 다루며, 기본 키, 외래 키, 정규화, 무결성, 인덱스처럼 설계 단계에서 중요한 개념을 정리합니다.

Duplicate Candidates
------------------------------------------------------------
- sample_ai.txt <-> sample_ai_copy.txt / similarity: 0.7323

Result
------------------------------------------------------------
Total documents loaded: 3
Report generated      : reports\document_report.md
```

---

## 9. 처리 흐름

```text
문서 업로드 또는 입력 폴더 지정
        ↓
PDF / TXT / Markdown 텍스트 추출
        ↓
문서 유형 판정
        ↓
유형별 제목 생성
        ↓
핵심 키워드 선별
        ↓
추천 파일명 생성
        ↓
문장형 요약 생성
        ↓
중복 의심 문서 탐지
        ↓
Markdown 리포트 생성
        ↓
웹 UI 표시 또는 파일 저장
```

---

## 10. 구현 포인트

### 10.1 문서 로딩

`document_loader.py`는 입력 폴더를 탐색하고 `.pdf`, `.txt`, `.md` 파일의 텍스트를 추출합니다.

PDF는 PyMuPDF를 사용하고, 텍스트 기반 파일은 UTF-8을 우선 적용하되 인코딩 문제가 발생하면 CP949로 다시 읽도록 구성했습니다.

### 10.2 문서 유형 기반 분석

`document_analyzer.py`는 단순 키워드 나열이 아니라 문서 유형을 먼저 판정합니다.

현재는 다음과 같은 프로필 기반 규칙을 사용합니다.

- AI 문서 자동화 개요
- 데이터베이스 설계 개념
- 프로젝트 리포트
- 일반 문서

문서 유형이 결정되면 해당 유형에 맞는 제목, 키워드, 추천 파일명, 요약을 생성합니다.

### 10.3 추천 파일명 생성

추천 파일명은 키워드를 길게 이어 붙이는 방식이 아니라 문서 유형별 이름 규칙을 따릅니다.

예:

```text
AI 문서 자동화 개요 → ai_document_automation_overview.txt
데이터베이스 설계 개념 → database_design_keys_indexes.md
```

원본 파일은 직접 변경하지 않고 추천 결과만 제공합니다.

### 10.4 중복 문서 탐지

`duplicate_detector.py`는 문자 n-gram 기반 TF-IDF 벡터를 생성한 뒤 cosine similarity를 계산합니다.

이 방식은 한국어 형태소 분석기에 의존하지 않고도 유사한 문서를 탐지할 수 있습니다.

### 10.5 Streamlit UI

`app.py`는 문서 업로드, 문서별 카드 결과, 중복 후보 표시, Markdown 리포트 미리보기, 다운로드 기능을 제공합니다.

표 가로 스크롤 없이 각 문서를 카드 형태로 보여주도록 구성했습니다.

---

## 11. 한계 및 개선 가능성

현재 버전은 가벼운 로컬 자동화 도구를 목표로 하므로 다음과 같은 한계가 있습니다.

- 문서 유형 판정은 규칙 기반이므로 새로운 분야의 문서는 일반 문서로 분류될 수 있습니다.
- 생성형 요약이 아니라 규칙 기반 문장형 요약과 추출식 요약을 함께 사용합니다.
- PDF의 표, 이미지, 복잡한 레이아웃 의미 분석은 지원하지 않습니다.
- 문서 유형 프로필을 추가하면 더 다양한 분야로 확장할 수 있습니다.

향후 개선 방향은 다음과 같습니다.

- 문서 유형 프로필 확장
- kiwipiepy 기반 한국어 키워드 품질 개선
- sentence-transformers 기반 의미 유사도 탐지 추가
- 실제 파일명 변경 모드와 dry-run 모드 분리
- RAG 문서 전처리 파이프라인과 연동

---

## 12. 포트폴리오 관점의 의미

이 프로젝트를 통해 다음 역량을 보여줄 수 있습니다.

- Python 기반 파일 처리 자동화
- PDF/TXT/Markdown 문서 파싱
- 문서 전처리 파이프라인 설계
- 규칙 기반 문서 유형 판정
- 키워드/요약/파일명 추천의 결과 일관성 개선
- TF-IDF와 cosine similarity 기반 유사 문서 탐지
- Streamlit 기반 사용자 친화적 UI 구현
- CLI와 웹 UI를 모두 고려한 도구 설계
- Markdown 기반 분석 리포트 자동 생성

---

## 13. 실행 환경

```text
Python 3.10+
Windows PowerShell
PyMuPDF
scikit-learn
numpy
streamlit
pandas
```
