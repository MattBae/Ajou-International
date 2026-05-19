import pytest
import allure
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db

@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@allure.feature("백엔드 API")
@allure.story("헬스체크")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("백엔드 서비스가 정상적으로 실행 중이며 응답 가능한 상태인지 확인합니다.")
def test_health(client):
    with allure.step("/health 엔드포인트 호출"):
        response = client.get("/health")
    with allure.step("상태 코드 및 응답 바디 검증"):
        assert response.status_code == 200, f"기대값 200, 실제값 {response.status_code}"
        assert response.json() == {"status": "ok"}, "헬스체크 응답 메시지 불일치"

@allure.feature("백엔드 API")
@allure.story("공지사항 관리")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("공지사항 목록이 예상된 스키마에 따라 정상적으로 조회되는지 확인합니다.")
def test_list_notices(client):
    with allure.step("/notices 엔드포인트 호출"):
        response = client.get("/notices")
    with allure.step("응답 내용 및 스키마 검증"):
        assert response.status_code == 200, f"기대값 200, 실제값 {response.status_code}"
        data = response.json()
        assert "items" in data, "응답에 'items' 키가 포함되어야 함"
        assert isinstance(data["items"], list), "'items'는 리스트 형태여야 함"
        assert len(data["items"]) > 0, "테스트 환경에서 공지사항 목록이 비어있지 않아야 함"
        
        # 첫 번째 아이템 구조 확인
        item = data["items"][0]
        required_keys = ["id", "title", "keyword", "published_at"]
        for key in required_keys:
            assert key in item, f"공지사항 아이템에 필수 키 누락: {key}"
        assert item["title"] == "2024 Fall Admission Guide", "첫 번째 공지사항 제목 불일치"

@allure.feature("백엔드 API")
@allure.story("공지사항 관리")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("특정 ID를 사용하여 공지사항의 상세 내용을 조회하고 정확성을 검증합니다.")
def test_get_notice_success(client):
    notice_id = "a8b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d"
    with allure.step(f"/notices/{notice_id} 호출"):
        response = client.get(f"/notices/{notice_id}")
    with allure.step("상세 데이터 검증"):
        assert response.status_code == 200, f"기대값 200, 실제값 {response.status_code}"
        data = response.json()
        assert data["id"] == notice_id
        assert data["title"] == "2024 Fall Admission Guide"
        assert "body" in data, "상세 공지사항에는 본문(body) 내용이 포함되어야 함"

@allure.feature("백엔드 API")
@allure.story("공지사항 관리")
@allure.severity(allure.severity_level.MINOR)
@allure.description("존재하지 않는 공지사항 ID로 요청 시 404 에러가 반환되는지 확인합니다.")
def test_get_notice_not_found(client):
    invalid_id = "00000000-0000-0000-0000-000000000000"
    with allure.step(f"존재하지 않는 ID({invalid_id})로 호출"):
        response = client.get(f"/notices/{invalid_id}")
    with allure.step("404 상태 코드 확인"):
        assert response.status_code == 404, f"미존재 ID 요청 시 404를 기대했으나 {response.status_code} 반환됨"
        assert "detail" in response.json(), "에러 응답에 상세 메시지(detail)가 포함되어야 함"
