import logging
import psycopg2
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# [핵심] 우리가 만든 설정 파일 임포트
from src.rag.RAG_config import settings

logger = logging.getLogger("RAG")

class VectorStore:
    def __init__(self):
        # 1. 임베딩 모델 초기화
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 실패: {e}")
            raise e

    def get_connection(self):
        """
        RAG_config.py의 설정을 사용하여 DB 연결 객체 반환
        """
        try:
            conn = psycopg2.connect(**settings.DB_PARAMS)
            return conn
        except Exception as e:
            logger.error(f"DB 연결 실패: {e}")
            raise e

    def add_documents(self, documents: List[Document]):
        """
        문서 리스트를 임베딩하여 DB에 저장
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logger.info(f"Generating embeddings for {len(documents)} documents...")
            
            # 1. 텍스트 임베딩 생성 (Batch)
            texts = [doc.page_content for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)

            # 2. DB Insert Query
            insert_query = """
                INSERT INTO notices (
                    source_type, source_name, source_url, 
                    title, body, 
                    dedupe_hash, embedding, 
                    is_embedded, is_processed,
                    published_at, deadline_at
                ) VALUES (
                    %s, %s, %s, 
                    %s, %s, 
                    %s, %s, 
                    TRUE, TRUE,
                    %s, %s
                )
                ON CONFLICT (dedupe_hash) DO UPDATE 
                SET embedding = EXCLUDED.embedding,
                    body = EXCLUDED.body,
                    updated_at = NOW();
            """

            # 3. 데이터 바인딩 및 실행
            for i, doc in enumerate(documents):
                meta = doc.metadata
                vector = embeddings[i]
                
                # 메타데이터에서 값 추출 (없으면 None)
                params = (
                    meta.get("source_type", "school_notice"),
                    meta.get("source_name", "Unknown"),
                    meta.get("source_url"),
                    meta.get("title"),
                    doc.page_content,
                    meta.get("dedupe_hash"),
                    vector,  # pgvector가 알아서 처리함
                    meta.get("published_at"),
                    meta.get("deadline_at")
                )
                
                cursor.execute(insert_query, params)

            conn.commit()
            logger.info(f"Successfully inserted {len(documents)} documents.")

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to insert documents: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

    def similarity_search(self, query: str, k: int = 3):
        """
        질문(Query)과 유사한 문서 검색
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 질문 임베딩
            query_embedding = self.embeddings.embed_query(query)
            
            # 2. 벡터 검색 쿼리 (L2 Distance or Cosine Similarity)
            # <=> : Cosine distance, <-> : L2 distance, <#> : Inner product
            search_query = """
                SELECT title, body, source_url, 1 - (embedding <=> %s::vector) as similarity
                FROM notices
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            
            cursor.execute(search_query, (query_embedding, query_embedding, k))
            results = cursor.fetchall()
            
            return [
                Document(
                    page_content=row[1], 
                    metadata={"title": row[0], "source_url": row[2], "score": row[3]}
                ) for row in results
            ]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        finally:
            cursor.close()
            conn.close()