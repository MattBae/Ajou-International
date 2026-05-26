# 백엔드 notices 테이블(embedding 컬럼)을 읽기 전용으로 조회한다. 적재는 backend/ingest_rag.py에서 수행.

import logging
from typing import List

import psycopg2
from psycopg2 import pool
from langchain_core.documents import Document

from .RAG_config import settings
from .embedder import Embedder

logger = logging.getLogger("RAG")


class VectorStore:
    _pool = None

    def __init__(self):
        try:
            self.embeddings = Embedder().get_embedding_function()
            # 클래스 레벨에서 커넥션 풀 초기화 (싱글톤 패턴과 유사하게 동작)
            if VectorStore._pool is None:
                # SSL 설정 추가: Neon DB 등 클라우드 DB는 필수인 경우가 많음
                db_params = settings.DB_PARAMS.copy()
                if "host" in db_params and "localhost" not in db_params["host"]:
                    db_params["sslmode"] = "require"
                
                VectorStore._pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    **db_params
                )
                logger.info(f"DB Connection Pool initialized (max_conn=20, sslmode={db_params.get('sslmode', 'none')})")
        except Exception as e:
            logger.error("초기화 실패: %s", e)
            raise

    def get_connection(self):
        """풀에서 커넥션 획득"""
        try:
            return VectorStore._pool.getconn()
        except Exception as e:
            logger.error("커넥션 획득 실패: %s", e)
            raise

    def release_connection(self, conn):
        """풀에 커넥션 반납"""
        try:
            VectorStore._pool.putconn(conn)
        except Exception as e:
            logger.error("커넥션 반납 실패: %s", e)

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """질문과 유사한 공지 및 정보 메뉴 검색. 커넥션 풀 사용."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            query_embedding = self.embeddings.embed_query(text=query, output_dimensionality=1536)
            
            # notices 테이블과 information_menu_parts 테이블 통합 검색
            search_query = """
                WITH notice_search AS (
                    SELECT 
                        title, 
                        body AS content, 
                        url AS source_url, 
                        deadline, 
                        'Notice' AS source_type,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM notices
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                ),
                info_search AS (
                    SELECT 
                        menu_title || ' > ' || part_key AS title, 
                        content, 
                        source_url, 
                        NULL::date AS deadline, 
                        'Information' AS source_type,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM information_menu_parts
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                )
                SELECT title, content, source_url, deadline, source_type, similarity
                FROM (
                    SELECT * FROM notice_search
                    UNION ALL
                    SELECT * FROM info_search
                ) AS combined
                ORDER BY similarity DESC
                LIMIT %s;
            """
            cursor.execute(search_query, (
                query_embedding, query_embedding, k,
                query_embedding, query_embedding, k,
                k
            ))
            rows = cursor.fetchall()
            return [
                Document(
                    page_content=row[1] or "",
                    metadata={
                        "title": row[0] or "",
                        "source_url": row[2],
                        "url": row[2],
                        "deadline": row[3],
                        "deadline_at": row[3],
                        "source_type": row[4],
                        "score": row[5],
                    },
                )
                for row in rows
            ]
        except Exception as e:
            logger.error("Search failed: %s", e)
            return []
        finally:
            cursor.close()
            self.release_connection(conn)
