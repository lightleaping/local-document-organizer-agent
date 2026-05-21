# Project Overview

## 프로젝트명

Local Document Organizer Agent

## 한 줄 설명

로컬 폴더 안의 PDF, TXT, Markdown 문서를 자동으로 읽고 요약, 키워드 추출, 중복 탐지, Markdown 리포트 생성을 수행하는 문서 자동화 Agent입니다.

## 개발 목적

이 프로젝트는 문서 기반 업무에서 반복적으로 발생하는 파일 확인, 요약, 분류, 중복 확인 작업을 자동화하기 위해 개발되었습니다.

특히 RAG 시스템이나 AI 문서 검색 서비스에서는 문서를 수집하고 전처리한 뒤, 검색 가능한 형태로 정리하는 과정이 중요합니다. 본 프로젝트는 이러한 전처리 파이프라인의 기본 구조를 로컬 환경에서 구현한 예시입니다.

## 주요 기능

- 폴더 내 문서 자동 탐색
- PDF, TXT, Markdown 텍스트 추출
- 문서별 요약 생성
- 문서별 키워드 추출
- 중복 의심 문서 탐지
- Markdown 리포트 생성

## 사용 기술

- Python
- PyMuPDF
- scikit-learn
- TF-IDF
- cosine similarity
- argparse
- Markdown

## 기대 효과

- 문서 정리 시간을 줄일 수 있음
- 유사 문서를 빠르게 확인할 수 있음
- 문서 기반 AI 서비스의 전처리 구조를 이해할 수 있음
- RAG 프로젝트와 연결 가능한 문서 처리 경험을 보여줄 수 있음