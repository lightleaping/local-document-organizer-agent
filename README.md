# Local Document Organizer Agent

PDF, TXT, Markdown 문서를 자동으로 읽고 **요약, 핵심 키워드 추출, 추천 파일명 생성, 중복 문서 탐지, Markdown 리포트 생성**을 수행하는 로컬 문서 정리 자동화 도구입니다.

이 프로젝트는 단순히 파일 목록을 출력하는 스크립트가 아니라, 문서 기반 AI 서비스에서 필요한 전처리 흐름을 작은 실무형 도구로 구현하는 것을 목표로 합니다.

---

## 핵심 기능

| 기능 | 설명 |
|---|---|
| 문서 로딩 | PDF, TXT, Markdown 문서의 텍스트 추출 |
| 요약 | 문서 내부 핵심 문장을 추출하여 빠르게 내용 파악 |
| 키워드 추출 | 조사 제거와 복합 표현 우선 추출을 적용한 키워드 생성 |
| 파일명 추천 | 문서 유형과 핵심 키워드를 조합한 읽기 쉬운 파일명 추천 |
| 중복 탐지 | 유사한 문서를 찾아 중복 정리 후보로 표시 |
| 리포트 생성 | 정리 결과를 Markdown 리포트로 저장 |
| 웹 UI | Streamlit 기반 업로드, 결과 표, 리포트 다운로드 제공 |

---

## 개선된 출력 예시

```text
[1] sample_ai.txt
    글자 수       : 196
    핵심 키워드   : 인공지능, 자연어 처리, 이미지 인식, 추천 시스템, 문서 자동화
    추천 파일명   : ai__인공지능_자연어_처리.txt
    요약          : 인공지능은 데이터를 기반으로 패턴을 학습하고 예측이나 분류를 수행하는 기술이다. 최근에는 자연어 처리, 이미지 인식, 추천 시스템, 문서 자동화 등 다양한 분야에서 활용되고 있다.

Duplicate Candidates
------------------------------------------------------------
- sample_ai.txt <-> sample_ai_copy.txt / similarity: 0.7323
```

---

## 실행 방법

### 설치

```bash
pip install -r requirements.txt
```

### CLI 실행

```bash
python main.py --input sample_docs --output reports --summary-sentences 3 --keywords 7 --duplicate-threshold 0.65
```

### 웹 UI 실행

```bash
streamlit run app.py
```

---

## 프로젝트 구조

```text
local-document-organizer-agent/
├── app.py
├── main.py
├── README.md
├── requirements.txt
├── src/
│   ├── document_loader.py
│   ├── summarizer.py
│   ├── keyword_extractor.py
│   ├── file_renamer.py
│   ├── duplicate_detector.py
│   └── report_generator.py
├── sample_docs/
├── reports/
└── docs/
```

---

## 포트폴리오 포인트

- 외부 LLM API 없이 동작하는 로컬 문서 자동화 도구
- RAG 전처리에 필요한 문서 파싱, 요약, 키워드 추출, 중복 탐지 흐름 구현
- CLI와 Streamlit UI를 모두 제공하여 개발자/사용자 관점을 함께 고려
- 원본 파일을 직접 변경하지 않는 안전한 dry-run 방식의 파일명 추천
