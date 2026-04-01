# AZAN Project — Claude Instructions

## 1. Project Overview

**목적:** 아주대학교 외국인 유학생 대상 공지 푸시알림 + AI 챗봇 앱  
**기간:** 2025.01 ~ 2025.05 (3인 캡스톤 팀)  
**플랫폼:** iOS / Android (React Native + Expo)

### Core Features
- OIA(국제처) 공지 크롤링 및 구조화
- Firebase FCM 기반 푸시 알림
- RAG 기반 챗봇 (공지 Q&A)
- GNN 기반 공지 추천 시스템
- 캘린더 UI (공지 마감일 시각화)

---

## 2. Tech Stack

| 레이어 | 기술 |
|--------|------|
| Frontend | React Native (Expo), Expo Router |
| Backend | FastAPI (Python), Render 배포 |
| Database | Neon PostgreSQL (serverless) |
| ORM | SQLAlchemy 2.0 |
| Vector DB | pgvector (HNSW 인덱스, 1536차원) |
| Full-text Search | pg_trgm (한글/영문) |
| Push Notification | Firebase FCM |
| CI/CD | GitHub Actions |
| Build | EAS (Expo Application Services) |
| Auth | (미정 — 구현 전 반드시 확인) |

---

## 3. Architecture

### 패턴
- **백엔드:** MVC 패턴 (Model / Router / Service 분리)
- **브랜치 전략:** `develop` (개발) → `production` (운영), Neon 브랜치 기능 활용
- **배포:** Render (백엔드 자동 배포), EAS (앱 빌드)

### 디렉토리 구조
```
azan/
├── frontend/              # React Native 앱 (강나연 담당)
│   ├── src/
│   └── App.js
├── workers/
│   ├── alarm/             # 푸시알림 워커 (MattB 담당)
│   └── keyword_match/     # 키워드 매칭 워커 (MattB 담당)
├── rag/                   # RAG 챗봇 (노준상 담당)
├── crawlers/              # OIA 크롤러 (강나연 담당)
├── infra/                 # 인프라 설정
├── legacy_db/             # 레거시 DB (참고용)
├── .github/
│   └── workflows/         # GitHub Actions CI/CD
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## 4. Team Roles

| 이름 | 담당 영역 |
|------|----------|
| **MattB (나)** | 푸시알림 시스템, 공지 처리, AI 추천 시스템 |
| 강나연 | 프론트엔드, OIA 크롤러 |
| 노준상 | RAG 챗봇, 성능 최적화 |

> **Claude는 MattB 담당 영역(workers/, 추천 시스템)을 우선으로 작업한다.**  
> 다른 팀원 담당 코드(frontend/, rag/, crawlers/)를 수정할 때는 반드시 먼저 이유를 설명하고 확인을 받는다.

---

## 5. Database

### Neon PostgreSQL
- **SSL:** 필수 (`sslmode=require`)
- **브랜치:** `develop` 브랜치 → 개발, `main` 브랜치 → 운영
- **드라이버:** `psycopg2-binary`
- **확장:** `pgvector` (1536차원 임베딩), `pg_trgm` (전문검색)

### 마이그레이션 규칙
- DB 스키마 변경 시 반드시 마이그레이션 파일 함께 작성
- 마이그레이션 파일명: `{timestamp}_{description}.py` 형식
- `.github/workflows/dev-migration.yml`로 자동 실행됨

### 공지 데이터 스키마 (핵심 필드)
```
title         — 공지 제목
preview       — 미리보기 텍스트
body          — 본문
published_at  — 게시일
created_at    — 크롤링 시각
deadline      — 마감일 (이미지 OCR 필요한 경우 있음)
```

---

## 6. AI 추천 시스템 설계

### 핵심 인사이트
외국인 유학생은 거의 동일한 라이프사이클을 따른다:  
`TOPIK 준비` → `비자 신청` → `입학` → `수강신청` → `졸업`

→ 개별 user node 불필요. **academic stage node** 사용.

### 그래프 구조 (SR-GNN / LightGCN 기반)
- **Node:** `academic_stage`, `notice`
- **Edge:** collective implicit signal (가중치)
- **가중치 계층:** `click(1)` < `read(2)` < `search(3)` < `schedule(4)`

### MVP 전략
1. **1단계 (현재):** rule-based stage 감지 (키워드 기반)
2. **2단계:** 로그 데이터 충분히 쌓인 후 GNN 도입

---

## 7. OIA 크롤링 주의사항

- **마감일(deadline):** HTML 텍스트가 아닌 **이미지 안에 포함**된 경우가 많음 → OCR 필요 (`pytesseract` 또는 Vision API)
- **이미지 URL 요청 시:** `Referer` 헤더 필수 (없으면 403 반환)
- **이미지 URL 패턴:** 알려진 패턴 존재, 크롤러 코드 참고

---

## 8. Coding Conventions

### Python (백엔드)
- PEP8 준수, **type hint 필수**
- 함수명: `snake_case`, 클래스명: `PascalCase`
- `async/await` 우선 사용 (FastAPI 비동기 패턴)
- 에러는 반드시 **로깅 후 raise** (조용히 무시 금지)
- 환경변수는 **절대 하드코딩 금지** → `.env` 또는 `os.environ` 참조

### React Native (프론트엔드)
- 함수형 컴포넌트 + hooks
- 컴포넌트명: `PascalCase`
- 파일명: 컴포넌트는 `PascalCase.tsx`, 유틸은 `camelCase.ts`

### Git
- 커밋 메시지 접두사: `feat` / `fix` / `docs` / `refactor` / `test` / `chore`
- PR: `develop` → `production`
- 브랜치명: `feat/기능명`, `fix/버그명`

---

## 9. Claude Behavior Rules

### 작업 방식
- **한 번에 하나의 기능 또는 파일만 수정한다** (매 단계마다 사람이 검수함)
- 코드 수정 전에 반드시 **현재 코드 분석 결과를 먼저 보고**한다
- 기능 구현 완료 후 **변경 파일 목록, 변경 이유, 주의사항**을 요약 보고한다
- 불확실한 부분은 구현하지 말고 **질문**한다

### 금지 사항
- 환경변수 하드코딩 금지
- 테스트 없는 DB 스키마 변경 금지
- 다른 팀원 담당 파일 무단 수정 금지
- `legacy_db/` 폴더는 참고용으로만 사용, 직접 수정 금지

### DB 작업 시
- 스키마 변경 → 마이그레이션 파일 동시 생성
- 쿼리 작성 시 `EXPLAIN ANALYZE` 결과 고려
- pgvector 쿼리는 HNSW 인덱스 활용 여부 확인

### CI/CD 작업 시
- workflow 파일명에 **em dash(—) 절대 사용 금지** (GitHub Actions 파싱 오류 발생한 전례 있음)
- 시크릿은 GitHub Actions secrets에서만 참조 (`${{ secrets.NAME }}`)

---

## 10. Environment Variables (참고)

```env
# Database
DATABASE_URL=postgresql://...@...neon.tech/azan?sslmode=require

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Render
RENDER_API_KEY=...

# 기타
ENVIRONMENT=development  # or production
```

> 실제 값은 `.env` 파일 또는 팀 공유 채널 확인
