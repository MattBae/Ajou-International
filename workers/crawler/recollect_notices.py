import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 설정 및 환경 변수 로드
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from workers.crawler.db import get_session
from workers.crawler import parser, image_uploader
from backend.app.models import Notice

def main():
    session = get_session()
    try:
        # 1. 처리되지 않은(is_processed == False) 공지 목록 가져오기
        unprocessed_notices = (
            session.query(Notice)
            .filter(Notice.is_processed == False)
            .order_by(Notice.published_at.desc())
            .all()
        )
        
        print(f"[*] Found {len(unprocessed_notices)} unprocessed notices in DB.")
        
        for idx, notice in enumerate(unprocessed_notices, 1):
            print(f"[{idx}/{len(unprocessed_notices)}] Re-collecting: {notice.notice_id} | {notice.title[:30]}...")
            
            try:
                # 2. 상세 페이지 URL로 다시 접속하여 수집 및 파싱
                # notice.url은 이미 저장되어 있는 상세 페이지 링크를 사용합니다.
                body, raw_image_urls = parser.fetch_body(notice.url)
                
                if body:
                    # 본문 업데이트
                    notice.body = body
                    
                    # 3. 이미지 업로드 및 R2 URL 리스트 갱신
                    if raw_image_urls:
                        r2_urls = image_uploader.upload_images(notice.notice_id, raw_image_urls)
                        notice.image_urls = r2_urls
                        print(f"    → Success: Body updated and {len(r2_urls)} images uploaded.")
                    else:
                        notice.image_urls = []
                        print(f"    → Success: Body updated (No images found).")
                    
                    # DB 저장
                    session.commit()
                else:
                    print(f"    → Warning: No body content found at {notice.url}")
                
                # 서버 부하 방지를 위한 짧은 휴식
                time.sleep(0.5)
                
            except Exception as e:
                session.rollback()
                print(f"    → Error processing {notice.notice_id}: {e}")

        print("\n[*] Re-collection process completed.")

    finally:
        session.close()

if __name__ == "__main__":
    main()
