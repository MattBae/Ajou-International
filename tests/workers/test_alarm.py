import pytest
import allure
from unittest.mock import MagicMock, patch
from workers.alarm.keyword_match.send_notifications import build_messages, send_messages

@allure.feature("푸시 알림")
@allure.story("메시지 구성")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("유효한 Expo 토큰과 유효하지 않은 토큰이 섞여 있을 때 메시지 생성 여부를 테스트합니다.")
def test_build_messages_mixed_tokens():
    user_notices = {
        "user-valid": [
            {
                "user_id": "user-valid",
                "expo_push_token": "ExponentPushToken[valid]",
                "notice_id": "notice-1",
                "title": "유효 토큰 공지",
                "keyword": "입학"
            }
        ],
        "user-invalid": [
            {
                "user_id": "user-invalid",
                "expo_push_token": "invalid_token_123",
                "notice_id": "notice-2",
                "title": "무효 토큰 공지",
                "keyword": "일반"
            }
        ]
    }
    with allure.step("혼합 토큰 목록으로부터 메시지 빌드"):
        messages = build_messages(user_notices)
    
    with allure.step("유효한 토큰에 대해서만 메시지가 생성되었는지 확인"):
        assert len(messages) == 1, "유효 토큰에 대해서만 메시지가 생성되어야 함"
        assert messages[0]["to"] == "ExponentPushToken[valid]"
        assert "입학" in messages[0]["title"]

@allure.feature("푸시 알림")
@allure.story("메시지 구성")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("한 사용자에게 여러 공지가 있을 때 메시지가 정상적으로 처리되는지 확인합니다.")
def test_build_messages_aggregation():
    user_notices = {
        "user-1": [
            {"notice_id": "n1", "expo_push_token": "ExponentPushToken[u1]", "title": "공지 1", "keyword": "A"},
            {"notice_id": "n2", "expo_push_token": "ExponentPushToken[u1]", "title": "공지 2", "keyword": "B"}
        ]
    }
    with allure.step("다중 공지 사용자 메시지 빌드"):
        messages = build_messages(user_notices)
    
    with allure.step("메시지 생성 결과 확인"):
        assert len(messages) >= 1, "최소 하나 이상의 메시지가 생성되어야 함"

@allure.feature("푸시 알림")
@allure.story("알림 전송")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("Expo API를 통한 알림 전송 성공 시나리오를 테스트합니다.")
@patch("requests.post")
def test_send_messages_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"data": [{"status": "ok"}]}
    
    messages = [{"to": "ExponentPushToken[valid]", "title": "제목", "body": "본문"}]
    with allure.step("Expo API를 통해 메시지 전송 및 성공 확인"):
        send_messages(messages)
        mock_post.assert_called_once()

@allure.feature("푸시 알림")
@allure.story("알림 전송")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Expo API 서버 에러(500) 발생 시의 예외 처리 및 로깅을 확인합니다.")
@patch("requests.post")
def test_send_messages_api_failure(mock_post):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "Internal Server Error"
    
    messages = [{"to": "ExponentPushToken[valid]", "title": "제목", "body": "본문"}]
    with allure.step("전송 시도 및 에러 핸들링 확인"):
        send_messages(messages)
        mock_post.assert_called_once()
        allure.attach(mock_post.return_value.text, name="Expo API 에러 응답", attachment_type=allure.attachment_type.TEXT)
