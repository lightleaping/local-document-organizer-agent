# Trouble Shooting

## 1. Streamlit 명령어를 인식하지 못하는 문제

### 문제

```text
streamlit : The term 'streamlit' is not recognized
```

### 해결

가상환경을 활성화한 뒤 패키지를 다시 설치합니다.

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 2. PyMuPDF import 오류

### 문제

```text
ModuleNotFoundError: No module named 'fitz'
```

### 해결

```bash
pip install pymupdf
```

또는:

```bash
pip install -r requirements.txt
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

## 5. 추천 파일명이 어색한 문제

### 원인

현재는 설치 안정성을 위해 한국어 형태소 분석기 없이 정규식 토큰화와 TF-IDF를 사용합니다.

### 개선 방향

`kiwipiepy` 같은 형태소 분석기를 적용하면 조사와 어미를 줄여 더 자연스러운 추천 파일명을 만들 수 있습니다.
