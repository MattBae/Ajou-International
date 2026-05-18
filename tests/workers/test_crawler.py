import pytest
import allure
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from workers.crawlers_legacy.parser_list import parse_list

@allure.feature("크롤러")
@allure.story("리스트 파싱")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("크롤러가 표준 TOPIK 일정 HTML 샘플을 정상적으로 파싱하는지 확인합니다.")
def test_parse_list_with_sample():
    with allure.step("샘플 HTML 파일 로드"):
        sample_path = PROJECT_ROOT / "workers" / "crawlers" / "data" / "topik_schedule_sample.html"
        if not sample_path.exists():
            allure.attach(f"경로를 찾을 수 없음: {sample_path}", name="에러", attachment_type=allure.attachment_type.TEXT)
            pytest.skip("샘플 HTML 파일을 찾을 수 없음")
            
        with open(sample_path, "r", encoding="utf-8") as f:
            html = f.read()
    
    with allure.step("HTML 리스트 파싱"):
        list_url = "https://www.topik.go.kr/hm/hp/schedule/list.do"
        items = parse_list(html, list_url)
    
    with allure.step("파싱된 아이템 구조 및 개수 검증"):
        assert isinstance(items, list), "파싱 결과는 리스트여야 함"
        assert len(items) > 0, "샘플에서 최소 하나 이상의 아이템이 추출되어야 함"
        for i, item in enumerate(items[:3]): # 상위 3개 아이템 확인
            with allure.step(f"아이템 {i} 검사"):
                assert "title" in item, "아이템에 'title' 누락"
                assert "url" in item, "아이템에 'url' 누락"
                assert "published_at_raw" in item, "아이템에 'published_at_raw' 누락"
                assert item["url"].startswith("http"), f"잘못된 URL 형식: {item['url']}"

@allure.feature("크롤러")
@allure.story("리스트 파싱")
@allure.severity(allure.severity_level.MINOR)
@allure.description("비어있거나 잘못된 형식의 HTML 입력 시 크롤러가 크래시 없이 정상 처리하는지 확인합니다.")
def test_parse_list_empty_html():
    with allure.step("빈 HTML 문자열 파싱"):
        items = parse_list("", "https://example.com")
    with allure.step("빈 리스트 반환 확인"):
        assert items == [], "빈 HTML에 대해서는 빈 리스트를 반환해야 함"

@allure.feature("크롤러")
@allure.story("리스트 파싱")
@allure.severity(allure.severity_level.MINOR)
@allure.description("잘못된 형식의 HTML 입력 시의 동작을 확인합니다.")
def test_parse_list_malformed_html():
    malformed_html = "<html><body><div>잘못된 콘텐츠</div></body></html>"
    with allure.step("잘못된 형식의 HTML 파싱"):
        items = parse_list(malformed_html, "https://example.com")
    with allure.step("안전한 처리 및 빈 리스트 반환 확인"):
        assert isinstance(items, list)
        # 선택자가 일치하지 않아도 에러가 발생하지 않고 0개의 아이템을 찾아야 함
        assert len(items) == 0
