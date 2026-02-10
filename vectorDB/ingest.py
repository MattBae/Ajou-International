# ./ingetst_db.py

import json
import os
import logging
from langchain_core.documents import Document
from vectorDB.client import get_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ingest")

def ingest_data():
    # 1. DB 연결 가져오기
    vector_store = get_db()
    if not vector_store:
        logger.error("Database connection failed. Aborting ingestion.")
        return

    logger.info("Starting data ingestion process...")
    
    # 2. JSON 파일 경로 설정
    json_path = os.path.join("source_code", "Database", "notice_db.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded JSON file from: {json_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {json_path}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        return
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from file: {json_path}")
        return

    # 3. Document 객체로 변환
    documents = []
    for item in data:
        content = f"제목: {item.get('title')}\n내용: {item.get('contents')}\n마감일: {item.get('deadline')}"
        
        meta = {
            "notice_id": str(item.get('notice_id')),
            "category": item.get('category', 'General'),
            "deadline": item.get('deadline', 'N/A')
        }
        documents.append(Document(page_content=content, metadata=meta))
    
    logger.debug(f"Prepared {len(documents)} documents for ingestion.")

    # 4. DB에 저장
    if documents:
        try:
            vector_store.add_documents(documents)
            logger.info(f"Successfully saved {len(documents)} notices to ChromaDB.")
        except Exception as e:
            logger.error(f"Error occurred during DB insertion: {str(e)}")
    else:
        logger.warning("No documents found to ingest.")

if __name__ == "__main__":
    ingest_data()