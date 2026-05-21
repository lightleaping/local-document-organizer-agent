# Architecture

## 전체 구조

```text
Input Folder
    ↓
Document Loader
    ↓
Text Preprocessing
    ↓
Summarizer
    ↓
Keyword Extractor
    ↓
Duplicate Detector
    ↓
Markdown Report Generator
```

## 모듈별 역할

| 모듈 | 역할 |
|---|---|
| main.py | CLI 인자 처리와 전체 파이프라인 실행 |
| document_loader.py | PDF, TXT, Markdown 파일 탐색 및 텍스트 추출 |
| summarizer.py | 문장 분리, 전처리, 핵심 문장 추출 |
| keyword_extractor.py | TF-IDF 기반 키워드 추출 |
| duplicate_detector.py | 문서 간 cosine similarity 계산 및 중복 후보 탐지 |
| report_generator.py | 분석 결과를 Markdown 리포트로 저장 |

## 데이터 흐름

1. 사용자가 입력 폴더와 출력 폴더를 지정합니다.
2. `document_loader.py`가 지원 확장자 파일을 탐색합니다.
3. 각 문서의 텍스트, 파일명, 확장자, 글자 수를 `Document` 객체로 저장합니다.
4. `summarizer.py`가 문서별 요약을 생성합니다.
5. `keyword_extractor.py`가 문서별 주요 키워드를 추출합니다.
6. `duplicate_detector.py`가 문서 간 유사도를 계산합니다.
7. `report_generator.py`가 분석 결과를 Markdown 파일로 저장합니다.

## 설계 특징

- 외부 API 없이 로컬에서 실행 가능
- CLI 기반으로 재사용 가능
- 기능별 모듈 분리
- 실행 결과와 예시 문서 분리
- RAG 전처리 파이프라인으로 확장 가능
