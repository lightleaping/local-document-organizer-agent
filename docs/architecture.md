# Architecture

## 전체 구조

```text
사용자
  ├─ Streamlit Web UI
  └─ CLI 실행
        ↓
Document Loader
        ↓
Summarizer
        ↓
Keyword Extractor
        ↓
Filename Suggester
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
| `summarizer.py` | 문장 분리와 추출식 요약 |
| `keyword_extractor.py` | TF-IDF 기반 키워드 추출 |
| `file_renamer.py` | 키워드 기반 추천 파일명 생성 |
| `duplicate_detector.py` | 문서 간 cosine similarity 계산 |
| `report_generator.py` | Markdown 리포트 생성 |

## 설계 특징

- CLI와 웹 UI를 분리하여 재사용성 확보
- 핵심 분석 로직은 `src` 모듈에 분리
- 사용자의 원본 파일은 직접 변경하지 않고 추천 결과만 제공
- 실행 결과는 Markdown으로 저장해 포트폴리오와 문서화에 활용 가능
