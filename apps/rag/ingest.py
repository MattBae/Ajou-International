# apps/rag/ingest.py

import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from langchain_core.documents import Document
from src.rag.vectorstore import VectorStore

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("Ingest")

def generate_dedupe_hash(title: str, url: str) -> str:
    """
    중복 방지를 위한 해시 생성 (Title + URL 조합)
    """
    unique_string = f"{title}_{url}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

# def parse_date(date_str):
#     """
#     날짜 문자열을 파싱하여 DB에 맞는 포맷으로 변환하거나 None 반환
#     """
#     if not date_str:
#         return None
#     try:
#         # 다양한 날짜 포맷 시도 (필요에 따라 추가)
#         for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y.%m.%d"):
#             try:
#                 return datetime.strptime(date_str, fmt)
#             except ValueError:
#                 continue
#         return None # 파싱 실패 시 None
#     except Exception:
#         return None

def run_ingest():
    # 1. 경로 설정 (프로젝트 루트 찾기)
    # apps/rag/ingest.py -> parent(rag) -> parent(apps) -> parent(root)
    base_dir = Path(__file__).resolve().parents[2]
    json_path = base_dir / "source_code" / "Database" / "notice_db.json"

    if not json_path.exists():
        logger.error(f"[Error] JSON 파일을 찾을 수 없습니다: {json_path}")
        return

    # 2. JSON 로드
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)
            logger.info(f"[System] {len(data_list)}개의 공지사항 데이터를 로드했습니다.")
    except Exception as e:
        logger.error(f"[Error] JSON 파일 읽기 실패: {e}")
        return

    # 3. LangChain Document 객체로 변환
    documents = []
    
    for item in data_list:
        try:
            title = item.get("title", "")
            content = item.get("contents", "")
            url = item.get("url", "")
            
            # 필수 데이터 누락 시 건너뛰기
            if not title or not content:
                continue

            # DB 스키마(init_db.py)와 키 이름을 일치시킴
            metadata = {
                "source_type": "school_notice",      # 고정값 또는 로직 추가
                "source_name": item.get("notice_source", "Unknown"),
                "source_url": url,                   # DB 컬럼: source_url
                "title": title,
                "dedupe_hash": generate_dedupe_hash(title, url), # 해시 값
                "published_at": item.get("created"), # DB 컬럼: published_at
                "deadline_at": item.get("deadline"), # DB 컬럼: deadline_at
                "category": item.get("category"),
                "is_embedded": False,
                "is_processed": False
            }
            
            # 본문 구성 (제목 + 내용)
            page_content = f"제목: {title}\n내용: {content}"

            doc = Document(page_content=page_content, metadata=metadata)
            documents.append(doc)
            
        except Exception as ignored_e:
            logger.warning(f"데이터 변환 중 항목 건너뜀: {item.get('title')} - {ignored_e}")
            continue

    # 4. DB 적재
    if documents:
        try:
            # VectorStore 초기화 (RAG_config.py 설정을 자동으로 불러옴)
            store = VectorStore()
            
            logger.info(f"[Start] {len(documents)}개 문서 DB 적재 시작...")
            store.add_documents(documents)
            logger.info("[Success] 데이터 적재가 성공적으로 완료되었습니다.")
            
        except Exception as e:
            logger.error(f"[Critical] DB 적재 중 치명적 오류 발생: {e}")
            # 에러 상세 정보 출력을 위해 traceback 사용 권장
            import traceback
            logger.error(traceback.format_exc())
    else:
        logger.warning("[Warning] 적재할 유효한 데이터가 없습니다.")

if __name__ == "__main__":
    run_ingest()