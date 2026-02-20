# 🤖 Azan Project

Azan은 아주대학교 외국인 유학생들이 언어 장벽과 정보 부족으로 겪는 어려움을 해결하기 위한 AI 기반 학사 정보 챗봇 및 개인화 알림 서비스입니다.

RAG(Retrieval-Augmented Generation) 기술을 활용해 학교 공지사항, 학사 규정, 생활 정보를 정확하게 제공하는 것을 목표로 합니다.

---

## 📚 프로젝트 개요 (Overview)
- **Project Name:** Azan (유학생의 알림과 안내를 책임지는 소리)
- **Goal:** 유학생의 성공적인 학업 수행과 안정적인 한국 생활 적응 지원
- **Target:** 아주대학교 외국인 유학생 (한국어/영어 지원)

### 💡 핵심 기능 (Key Features) - **[Updated]**
**1. AI 챗봇 어시스턴트 (Context-Aware RAG Chatbot)**
- **연속 질의응답 (Memory):** `InMemoryChatMessageHistory`를 도입하여 사용자의 이전 대화 문맥을 기억하고, 목적어가 생략된 질문도 찰떡같이 알아듣습니다.
- **질문 재구성 (Condense Question):** 대화 기록을 분석하여 LLM이 스스로 검색에 최적화된 독립적인 질문(Standalone Question)으로 재구성한 뒤 DB를 탐색합니다.
- **과부하 방지 (Rate Limit 핸들링):** 외부 API 연속 호출 시 발생하는 500 에러를 방지하기 위해 스마트 딜레이(Smart Delay) 로직이 적용되어 있습니다.
- **TOON Format:** 긴 공지사항을 보기 쉬운 표 형태로 요약 제공합니다.
- **Multi-Source RAG:** 교내 공지사항, 법무부 비자 정보, TOPIK 일정 등을 통합 검색합니다. **(구현 예정)**

**2. 개인화 맞춤 알림 (Mom-Style Notification)**
- 사용자의 관심 키워드(Visa, Scholarship 등)에 맞춰 중요 공지 필터링
- 친근한 어조로 마감 기한 및 필수 서류 안내 (다국어 지원)

---

## 🏗️ 프로젝트 구조 (Project Structure)

기능별로 모듈화된 Monorepo 구조입니다.

```text
📦Ajou-International/
│
├── 📂 apps/                    # 애플리케이션 모듈
│   ├── 📂 api/                 # [Backend] FastAPI 메인 서버
│   ├── 📂 mobile/              # [Frontend] React Native 모바일 앱
│   ├── 📂 rag/                 # [AI Core] RAG 파이프라인
│   │   ├── 📂 src/
│   │   │   ├── 📂 chatbot/             # 챗봇 서비스 로직 (Service Layer)
|   |   |   |   ├──📜prompts.py         # 시스템 프롬프트 및 질문 재구성(Condense) 템플릿 관리
|   │   │   │   └──📜service.py         # 메모리 관리 및 LLM 최종 답변 생성을 총괄하는 챗봇 본체
│   │   │   └── 📂 rag/                 # 임베딩/검색/설정 로직 (Core Layer)
|   |   |   |   ├──📜embedder.py        # 사용자의 질문을 모델이 이해할 수 있는 벡터(숫자)로 변환
|   |   |   |   ├──📜RAG_config.py      # 사용 모델명, 검색 갯수 등 RAG 파이프라인의 환경 설정
|   |   |   |   ├──📜retriever.py       # Vector DB에서 관련성이 높은 문서를 꺼내오는 검색기 로직
|   │   │   │   └──📜vectorstore.py     # pgvector DB와 연결하여 코사인 유사도 연산(SQL) 수행
│   │   ├── 📜 ingest.py                # 데이터 적재 스크립트
│   │   ├── 📜 init_db.py               # DB 초기화 스크립트
│   │   └── 📜 test_chatbot.py          # 챗봇 통합 테스트
│   └── 📂 worker/
│
├── 📂 source_code/             # 원본 데이터 소스
│   └── 📂 Database/            # 공지사항 및 사용자 JSON 데이터
│
├── 📂 infra/                   # 인프라 설정
│   └── 📂 docker/              # Docker 관련 파일
│
├── 📂 scripts/                 # 개발 유틸리티 스크립트
│
├── 📜 .env                     # 환경 변수 (API Key, DB 접속 정보)
├── 📜 docker-compose.yml       # 통합 컨테이너 실행 설정
├── 📜 postgresql_init.sql      # PostgreSQL 초기 SQL
└── 📜 requirements.txt         # 전체 프로젝트 의존성 목록
```

---

## 🚀 시작 가이드 (Quick Start)

### 1. 환경 변수 설정 (.env)
프로젝트 최상위 루트(Ajou-International/)에 .env 파일을 생성하고 아래 내용을 입력합니다.

```Ini, TOML
# Database (Docker와 연동됨)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=azan
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# RAG Settings
GENERATION_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=gemini-embedding-001
```

### 2. 인프라 실행 (Docker)
PostgreSQL(pgvector) 데이터베이스를 실행합니다. 프로젝트 루트에서 다음 명령어를 실행하세요.

```Bash
docker-compose up -d
```

### 3. RAG 모듈 설정 및 실행
챗봇 기능을 사용하기 위해 데이터베이스를 초기화하고 데이터를 적재합니다.

### 3-1. 필수 라이브러리 설치
가상환경을 생성하고 루트에 있는 requirements.txt를 설치합니다.
```Bash
# 가상환경 생성 및 활성화 (Windows)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 3-2. DB 초기화 (Table 생성)
apps/rag/init_db.py를 실행하여 PostgreSQL에 테이블을 생성합니다.
```Bash
python apps/rag/init_db.py
```

### 3-3. 데이터 적재 (Ingest)
source_code/Database/notice_db.json 데이터를 읽어 벡터화한 후 DB에 저장합니다.

```Bash
python apps/rag/ingest.py
```

### 3-4. 챗봇 테스트 실행
CLI 환경에서 Azan 챗봇이 정상 동작하는지 테스트합니다.

```Bash
python apps/rag/test_chatbot.py
```