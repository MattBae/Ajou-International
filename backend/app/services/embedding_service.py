# backend/app/services/embedding_service.py
import sys
from pathlib import Path

# 현재 파일(embedding_service.py)의 부모(services), 그 부모(app), 그 부모(backend), 그 부모(Ajou-International)
# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import logging
from sqlalchemy import text
from backend.app.database import SessionLocal
from backend.app.models import Notice
from workers.rag.src.rag.embedder import Embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmbeddingUpdater")

def update_missing_embeddings():
    db = SessionLocal()
    try:
        # 1. 임베딩이 없는 공지사항 조회
        notices_to_update = db.query(Notice).filter(Notice.embedding.is_(None)).all()
        
        if not notices_to_update:
            logger.info("모든 공지사항에 이미 임베딩이 존재합니다.")
            return

        logger.info(f"총 {len(notices_to_update)}개의 공지사항에 임베딩 생성을 시작합니다.")
        
        # 2. 임베더 초기화
        embedder = Embedder().get_embedding_function()
        
        count = 0
        for notice in notices_to_update:
            content_text = f"제목: {notice.title}\n내용: {notice.body or ''}"
            
            try:
                # 3. 임베딩 생성 (Gemini API 호출)
                vector = embedder.embed_query(text=content_text, output_dimensionality=1536)
                
                # 4. DB 업데이트
                notice.embedding = vector
                count += 1
                
                if count % 10 == 0:
                    db.commit()
                    logger.info(f"{count}개 완료...")
                    
            except Exception as e:
                logger.error(f"Error processing notice {notice.id}: {e}")
                continue
        
        db.commit()
        logger.info(f"성공적으로 총 {count}개의 임베딩을 업데이트했습니다.")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_missing_embeddings()
