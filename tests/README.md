# AZAN 프로젝트 테스트 가이드 (Tests Guide)

이 디렉토리는 AZAN 프로젝트의 백엔드 API, 크롤러, 알림 워커 등 주요 로직의 안정성을 검증하기 위한 테스트 코드를 포함하고 있습니다. 모든 테스트는 `pytest` 프레임워크를 기반으로 하며, `Allure`를 통해 시각화된 리포트를 제공합니다.

## 1. 테스트 디렉토리 구조
- `backend/`: FastAPI 엔드포인트 및 비즈니스 로직 테스트
- `workers/`: 크롤러 파싱 및 알림 메시지 생성/전송 로직 테스트
- `fixtures/`: 테스트에 사용되는 Mock 데이터 (JSON 파일)
- `conftest.py`: 공통 Fixture 설정 및 SQLite In-memory DB 초기화 로직
- `TEST_SCOPE.md`: 상세 테스트 범위 및 자동화 전략 명세

## 2. 테스트 원칙: Zero-DB Access
본 프로젝트는 테스트의 속도와 독립성을 보장하기 위해 실제 데이터베이스에 접속하지 않는 **File-based Mocking** 전략을 사용합니다.
- `tests/fixtures/`의 JSON 데이터를 SQLite In-memory DB에 로드하여 실제 DB와 유사한 환경을 구현합니다.
- 외부 API(Gemini, Expo Push 등) 호출은 `unittest.mock`을 사용하여 격리된 상태에서 검증합니다.

## 3. 테스트 실행 방법

### 3.1. 환경 준비
프로젝트 루트에서 가상환경이 활성화되어 있어야 하며, 필요한 패키지가 설치되어 있어야 합니다.
```bash
pip install -r backend/requirements.txt  # 또는 프로젝트 설정에 따른 설치
```

### 3.2. 테스트 실행 및 결과 저장
Allure 리포트 생성을 위해 결과 데이터를 `allure-results` 폴더에 저장하며 실행합니다.
```bash
pytest --alluredir=allure-results
```

## 4. Allure 보고서 확인 방법
테스트 실행 후 생성된 데이터를 시각화된 웹 리포트로 확인합니다. 모든 테스트 케이스와 단계(Step)는 **한국어**로 설명되어 있습니다.

```bash
# 로컬 서버를 띄워 리포트 확인
allure serve allure-results
```

### 보고서에서 확인할 수 있는 정보
- **기능(Feature) 및 시나리오(Story)** 별 성공/실패 여부
- **테스트 중요도(Severity)**: Critical, Normal, Minor 등
- **상세 단계(Steps)**: 각 테스트 내에서 수행된 세부 작업과 검증 내용
- **에러 피드백**: 실패 시 실제 값과 기대 값의 차이, API 에러 응답 내용 등

## 5. 테스트 케이스 추가 가이드
새로운 테스트 작성 시 다음 가이드를 준수해 주세요.
- `allure.feature`, `allure.story` 등의 데코레이터를 사용하여 카테고리를 지정하세요.
- `allure.description`과 `allure.step`을 사용하여 **한국어**로 명확한 설명을 작성하세요.
- 엣지 케이스(잘못된 입력, 서버 에러 등)에 대한 검증을 반드시 포함하세요.
