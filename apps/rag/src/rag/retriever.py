# apps\rag\src\rag\retriever.py

import psycopg2
from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from .RAG_config import settings
from .embedder import Embedder

class Retriever(BaseRetriever):
    """notices 테이블 직접 조회 Custom Retriever"""
    def __init__(self, **kwargs):
        # BaseRetriever는 Pydantic 기반이라 super().__init__ 호출 방식이 다름
        # 여기서는 간단히 멤버 변수 할당을 위해 이렇게 처리
        super().__init__(**kwargs)
        self.connection_string = settings.DATABASE_URL
        self.embedder = Embedder()
        self.top_k = settings.RETRIEVER_TOP_K
        self.threshold = settings.SIMILARITY_THRESHOLD

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        
        # 질문 임베딩
        query_embedding = self.embedder.get_embedding_function().embed_query(query)
        
        # SQL 실행 (코사인 유사도 기반)
        # title / body / url만 우선 추출
        sql = """
            SELECT 
                title, 
                body, 
                source_url, 
                1 - (embedding <=> %s::vector) as similarity
            FROM notices
            WHERE 1 - (embedding <=> %s::vector) > %s
            ORDER BY similarity DESC
            LIMIT %s;
        """
        
        documents = []
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        query_embedding, 
                        query_embedding, 
                        self.threshold, 
                        self.top_k
                    ))
                    results = cur.fetchall()
                    
                    for row in results:
                        title, body, url, score = row
                        
                        # context 조립
                        page_content = f"제목: {title}\n내용: {body}"
                        metadata = {"source": url, "score": float(score)}
                        
                        documents.append(Document(page_content=page_content, metadata=metadata))
                        
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

        return documents