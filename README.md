# Local Document Organizer Agent

PDF, TXT, Markdown 문서를 업로드하면 **문서 유형, 제목, 핵심 키워드, 추천 파일명, 요약, 중복 후보, Markdown 리포트**를 생성하는 로컬 문서 정리 자동화 도구입니다.

## 핵심 개선점

기존의 단순 키워드 나열 방식이 아니라, 문서 유형을 먼저 판단한 뒤 결과를 구성합니다.

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
```

따라서 추천 파일명이 단순히 키워드를 길게 이어 붙이는 방식이 아니라, 문서의 목적을 표현하는 이름이 되도록 설계했습니다.

---

## 실행

```bash
python -m streamlit run app.py
```

```bash
python main.py --input sample_docs --output reports --summary-sentences 3 --keywords 6 --duplicate-threshold 0.65
```
