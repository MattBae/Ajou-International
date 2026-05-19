# Test Scope & Automation Strategy

이 문서는 'ajou-international' 프로젝트의 QA 자동화 및 테스트 전략을 설명합니다.

## 1. 데이터 전략: Zero-DB Access (File-based Mocking)

실제 데이터베이스 의존성을 제거하고 테스트 속도를 높이기 위해 다음 전략을 적용했습니다.

- **Fixture 기반 테스트**: `tests/fixtures/` 폴더에 DB 스키마를 반영한 JSON 데이터를 저장하여 테스트 소스로 활용합니다.
- **In-memory DB 활용**: Python 테스트(`pytest`) 실행 시 SQLite In-memory DB를 생성하고 JSON 데이터를 로드하여 로직을 검증합니다.
- **Mocking**: `pgvector`와 같이 SQLite에서 지원하지 않는 특수 타입이나 외부 API 호출은 `unittest.mock`을 통해 격리합니다.

## 2. UI 테스트: React Native Rendering

- **도구 선정**: `Jest` + `@testing-library/react-native`
- **테스트 위치**: `frontend/app/components/**/__tests__/*.test.tsx`
  - 컴포넌트와 동일한 소스 트리 내에 위치시켜 환경 격리 및 경로 참조 에러를 방지합니다.
- **실행 환경**: `jest.config.js`에서 `react-native` 프리셋을 사용하여 Expo 내부 라이브러리와의 호환성을 확보했습니다.
- **가독성 향상**: `jest-spec-reporter`를 도입하여 CLI에서 개별 테스트 케이스의 성공 여부를 시각적으로 확인할 수 있습니다.

## 3. 테스트 범위 및 엣지 케이스

### Notice Crawling (Workers)
- `workers/crawlers/data/`의 샘플 HTML을 로드하여 파싱 로직의 정확성을 검증합니다.
- 날짜 형식 변환 및 제목 누락 등의 예외 상황을 확인합니다.

### Push Alarm (Workers)
- **Expo Token 검증**: 유효한 토큰 형식이 아닐 경우 발송 대상에서 제외되는지 확인합니다.
- **메시지 구성**: 공지 개수에 따라 제목과 본문이 규칙에 맞게 생성되는지 테스트합니다.

### Backend API
- `FastAPI TestClient`를 사용하여 엔드포인트의 HTTP 상태 코드 및 응답 스키마를 검증합니다.
- DB 연결 없이 Mock 데이터를 통해 404, 409 등 예외 응답을 테스트합니다.

### UI Components (Frontend)
- **데이터 바인딩**: Props로 전달된 정보가 정확한 UI 요소에 표시되는지 검증합니다.
- **조건부 렌더링**: '중요' 표시 등 비즈니스 조건에 따른 UI 변화를 확인합니다.

## 4. 커맨드 가이드

### Python 테스트 (Backend & Workers)
```bash
# 전체 테스트 실행
pytest

# Allure 보고서 생성 및 확인
allure serve allure-results
```

### Frontend 테스트
```bash
cd frontend
# 상세 결과(Spec) 포함 실행
npm test
```

## 5. 향후 확장 계획
- **API Mocking (msw)**: 프론트엔드 API 호출부에 대한 Mock 서버 구성.
- **Snapshot Testing**: UI 회귀 테스트를 위한 스냅샷 생성.
- **E2E Testing**: 주요 사용자 시나리오에 대한 통합 테스트 검토.