# Trouble Shooting

## 1. PowerShell에서 가상환경 활성화 오류

### 문제

```text
running scripts is disabled on this system
```

### 원인

Windows PowerShell 실행 정책 때문에 `.ps1` 스크립트 실행이 제한된 경우입니다.

### 해결

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

그 다음 다시 실행합니다.

```bash
.\.venv\Scripts\Activate.ps1
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
pip install -r requirements.txt
```

또는 직접 설치합니다.

```bash
pip install pymupdf
```

---

## 3. Markdown 제목이 요약에 포함되는 문제

### 문제

Markdown 파일에서 `# 데이터베이스 개요` 같은 제목이 요약에 포함되었습니다.

### 원인

초기 요약 함수에서 Markdown 문법을 충분히 제거하지 않았기 때문입니다.

### 해결

`summarizer.py`에서 Markdown heading 줄은 요약 대상에서 제외하도록 수정했습니다.

```python
if re.match(r"^#{1,6}\s+", line):
    continue
```

---

## 4. 중복 문서가 탐지되지 않는 문제

### 문제

비슷한 문서인데 중복 후보로 표시되지 않았습니다.

### 원인

유사도 임계값이 너무 높게 설정되었을 수 있습니다.

### 해결

테스트 단계에서는 임계값을 낮춰 확인할 수 있습니다.

```python
detect_duplicates(documents, threshold=0.75)
```

실제 사용 시에는 문서 특성에 따라 `0.80`, `0.85`, `0.90` 등으로 조정할 수 있습니다.

---

## 5. reports/document_report.md가 GitHub에 올라가지 않는 문제

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
