# Architecture

## 전체 구조

```text
사용자
  ├─ Streamlit Web UI
  └─ CLI 실행
        ↓
Document Loader
        ↓
Document Analyzer
        ├─ 문서 유형 판정
        ├─ 제목 생성
        ├─ 핵심 키워드 선별
        ├─ 추천 파일명 생성
        └─ 요약 생성
        ↓
Duplicate Detector
        ↓
Markdown Report Generator
```

## 모듈별 역할

| 모듈 | 역할 |
|---|---|
| `app.py` | Streamlit 기반 웹 UI |
| `main.py` | CLI 인자 처리와 전체 파이프라인 실행 |
| `document_loader.py` | PDF, TXT, Markdown 문서 탐색 및 텍스트 추출 |
| `keyword_extractor.py` | Markdown 정리, 토큰 정규화, 키워드 후보 추출 |
| `summarizer.py` | 문장 분리와 추출식 요약 |
| `document_analyzer.py` | 문서 유형 판정, 제목 생성, 키워드 선별, 추천 파일명 생성, 요약 통합 |
| `file_renamer.py` | 추천 파일명 생성 인터페이스 |
| `duplicate_detector.py` | 문서 간 cosine similarity 계산 |
| `report_generator.py` | Markdown 리포트 생성 |

## 데이터 흐름

1. 사용자가 문서를 업로드하거나 입력 폴더를 지정합니다.
2. `document_loader.py`가 지원 확장자 파일을 읽어 텍스트를 추출합니다.
3. `document_analyzer.py`가 문서 유형을 판정합니다.
4. 문서 유형에 맞는 제목, 핵심 키워드, 추천 파일명, 요약을 생성합니다.
5. `duplicate_detector.py`가 문서 간 유사도를 계산합니다.
6. `report_generator.py`가 전체 결과를 Markdown 파일로 저장합니다.
7. `app.py`는 같은 분석 결과를 카드형 UI로 표시하고 리포트 다운로드를 제공합니다.

## 설계 특징

- CLI와 웹 UI를 분리하여 재사용성 확보
- 핵심 분석 로직은 `src` 모듈에 분리
- 추천 파일명은 실제 파일을 변경하지 않는 dry-run 방식
- 결과는 Markdown 리포트로 저장 가능
- 문서 유형 프로필을 추가하여 확장 가능
