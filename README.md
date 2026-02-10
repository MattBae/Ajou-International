# 🤖 Azan Project - RAG Chatbot Module

Google Gemini와 ChromaDB를 활용한 **RAG(검색 증강 생성) 기반 공지사항 챗봇** 모듈입니다.

## 📁 프로젝트 구조 (Refactored)

기능별로 로직(`chatbot`)과 데이터 처리(`vectorDB`)를 분리하여 모듈화하였습니다.

```text
AJOU-INTERNATIONAL/
│
├── 📂 chatbot/                 # [Core] 챗봇 핵심 로직
│   ├── __init__.py
│   ├── config.py              # 환경 변수 및 로깅 설정
│   ├── main.py                # 프로그램 실행 진입점 (CLI)
│   └── service.py             # RAG 파이프라인 (검색 -> 프롬프트 -> 생성)
│
├── 📂 vectorDB/                # [Data] 벡터 DB 관리
│   ├── __init__.py
│   ├── client.py              # ChromaDB 연결 클라이언트 (Singleton)
│   └── ingest.py              # 데이터 임베딩 및 DB 적재 스크립트
│
├── 📂 chroma_data/             # (Auto) 벡터 데이터 영구 저장소 (Docker Volume)
├── .env                        # API 키 및 비밀 설정 (Git 제외)
├── .gitignore                  # Git 추적 제외 설정
├── docker-compose.yml          # ChromaDB 컨테이너 설정
└── requirements.txt            # 의존성 패키지 목록
```

## 🛠️ 설치 및 환경 설정
### 1. 필수 요구 사항 (Prerequisites)
Python 3.9 이상

Docker Desktop (Vector DB 실행용)

Google Gemini API Key

---
### 🐳 Docker 설치 및 초기 설정 (Docker 미설치 시)
docker-compose 명령어를 사용하려면 먼저 Docker Desktop이 설치되어 있어야 합니다.

1. Docker Desktop 설치
- Docker 공식 홈페이지에 접속하여 OS(Windows/Mac)에 맞는 설치 파일을 다운로드 후 실행합니다.
- Windows 사용자 주의: 설치 중 'Use WSL 2 instead of Hyper-V' 옵션이 나오면 반드시 체크해 주세요.

2. 시스템 재시작 및 로그인
- 설치 완료 후 컴퓨터를 재시작합니다.
- Docker Desktop을 실행하고 가이드에 따라 초기 설정을 완료합니다.

3. 리소스 설정 (선택 사항)
- Docker Desktop 설정(Settings > Resources)에서 메모리와 CPU 할당량을 확인합니다. 
- ChromaDB의 원활한 작동을 위해 최소 2GB 이상의 메모리 할당을 권장합니다.

4. 설치 확인

- 터미널(PowerShell 또는 CMD)에서 아래 명령어를 입력하여 설치 여부를 확인합니다.

    ```Bash
    docker --version
    docker-compose --version
    ```
---
### 3. 데이터 설정 및 라이브러리 설치
가상환경 사용을 권장합니다.

```Bash
# 1. alarm 브랜치에서 source_code 폴더 가져오기
git checkout feat/alarm -- source_code/

# 2. 가져온 폴더가 Git에 커밋되지 않도록 추적 취소 (이미 커밋된 경우)
git rm -r --cached source_code/

# 3. .gitignore에 source_code/ 추가 확인 후 커밋
git add .gitignore
git commit -m "Ignore fetched source_code folder"
```

### 2. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 아래 내용을 입력하세요.
``` Ini, TOML
# .env
GEMINI_API_KEY=your_api_key_here_xxxxxx
```

### 3. 데이터 설정
chatbot 브랜치에 alarm 브랜치의 source_code 폴더를 가져오고 추적을 제거합니다.
```Bash
# 1. alarm 브랜치에서 source_code 폴더 가져오기
git checkout feat/alarm -- source_code/

# 2. 가져온 폴더가 Git에 커밋되지 않도록 추적 취소 (이미 커밋된 경우)
git rm -r --cached source_code/

# 3. .gitignore에 source_code/ 추가 확인 후 커밋
git add .gitignore
git commit -m "Ignore fetched source_code folder"
```

### 4. 라이브러리 설치
가상환경 사용을 권장합니다.

```Bash
# 1. 가상환경 생성 및 활성화 (Windows)
python -m venv venv
.\venv\Scripts\activate

# 2. 필수 패키지 설치
pip install -r requirements.txt
```

## 🚀 실행 방법 (Step-by-Step)
이 프로젝트는 Vector DB(Docker) 가 실행된 상태에서만 작동합니다.

### 1단계: Vector DB 서버 실행 (Docker)
터미널에서 아래 명령어로 ChromaDB 컨테이너를 실행합니다.

``` Bash
docker-compose up -d
```
확인: docker ps 명령어로 ajou_vector_db 컨테이너가 실행 중인지 확인하세요.

### 2단계: 공지사항 데이터 적재 (Ingest)
최초 실행 시 또는 데이터가 변경되었을 때 한 번 실행합니다. (JSON 데이터를 벡터로 변환하여 DB에 저장합니다.)

```Bash
# 주의: 반드시 프로젝트 루트 경로에서 실행하세요.
python -m vectorDB.ingest
```

### 3단계: 챗봇 실행
챗봇을 CLI 환경에서 실행합니다.

```Bash
python -m chatbot.main
```
종료 방법: 대화창에 q 또는 c 입력

## 📊 개발 현황 (Feature Status)
### ✅ RAG System Implementation
[x] 데이터 처리: 공지사항 JSON 데이터 로딩 및 전처리(Toon)

[x] Vector DB 구축: Docker 기반 ChromaDB 환경 구성 (docker-compose)

[x] 임베딩(Embedding): gemini-embedding-001 모델을 활용한 텍스트 벡터화

[x] 검색 로직: 유사도 기반 문서 검색 (similarity_search) 및 Threshold 필터링

[x] 답변 생성: 검색된 컨텍스트(Context)를 바탕으로 Gemini가 답변 생성

[x] 시스템 관리: 중앙 집중식 로깅(Logging) 및 설정(Config) 관리

### 📝 Todo (Future Works)
[ ] UI 연동: CLI를 넘어선 웹/앱 인터페이스(API) 구축

[ ] 성능 최적화: 프롬프트 엔지니어링 고도화 및 답변 속도 개선